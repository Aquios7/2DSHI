import traceback
from pypylon import pylon  # Import relevant pypylon packages/modules
import cv2
import os, sys
import glob
import natsort
import configparser
import time
from . import App as tk_app
from . import histograms as hgs
from . import s1, s2, s3, s4, s5, s6, s7, s8, s9
from . import store_params as sp
# used for Windows
from image_processing import bit_depth_conversion as bdc
from coregistration import find_gaussian_profile as fgp
from experiment_set_up import find_previous_run as fpr
from constants import STEP_DESCRIPTIONS as sd
from experiment_set_up import user_input_validation as uiv
from gui import runGUI
# used for Linux
# from src.image_processing import bit_depth_conversion as bdc
# from src.coregistration import find_gaussian_profile as fgp
# from src.experiment_set_up import find_previous_run as fpr
# from src.constants import STEP_DESCRIPTIONS as sd
# from src.experiment_set_up import user_input_validation as uiv


twelve_bit_max = (2 ** 12) - 1
eight_bit_max = (2 ** 8) - 1

class Stream:
    def __init__(self, fb=-1, save_imgs=False):
        self.test = False
        self.reason = None
        self.c_folder = None
        self.config = 'config.ini'
        self.args = None
        self.test_dir = '~/test-data/'
        self.stepList = None
        self.prev_direc = None

        self.continuous = True
        self.single_shot = False if self.continuous else True
        self.tkapp = None
        self.max_n_sigma = None

        self.save_imgs = save_imgs
        self.a_frames = list()
        self.b_frames = list()
        self.b_prime_frames = list()
        self.r_frames = list()
        self.r_frames_as_csv_text = list()

        self.cam_a = None
        self.cam_b = None
        self.all_cams = None
        self.latest_grab_results = {"a": None, "b": None}
        self.frame_count = 0
        self.break_key = 'q'
        self.current_frame_a = None
        self.current_frame_b = None
        self.histocam_a = None
        self.histocam_b = None
        self.stacked_streams = None
        self.data_directory = None

        self.mu_x, self.sigma_x_a, self.amp_x = None, None, None
        self.mu_y, self.sigma_y_a, self.amp_y = None, None, None
        self.mu_x, self.sigma_x_b, self.amp_x = None, None, None
        self.mu_y, self.sigma_y_b, self.amp_y = None, None, None

        self.sigma_a_x, self.sigma_b_x = None, None
        self.sigma_a_y, self.sigma_b_y = None, None

        self.static_center_a = None
        self.static_center_b = None

        self.static_sigmas_x = None
        self.static_sigmas_y = None

        self.roi_a = None
        self.roi_b = None

        self.current_run = None

        self.warp_matrix = None
        self.warp_matrix_2 = None

        self.jump_level = 0

        self.R_HIST = None

        self.stats = None
        self.r_frames = None
        self.a_frames = None

        self.a_images = None
        self.b_prime_images = None

        self.start_writing_at = 0
        self.end_writing_at = 0

        self.max_pixel_a = None
        self.max_pixel_b = None

        self.s8_full_a_frames = list()
        self.s8_full_b_frames = list()

        self.s8_full_a_frames_to_save = list()
        self.s8_full_b_frames_to_save = list()

        self.h_offset = None
        self.v_offset = None

        self.n_sigma = None
        self.prv_run_dir = None

    def save_config(self):
        config = configparser.ConfigParser()
        for key, value in self.__dict__.items():
            config.set('DEFAULT', key, str(value))
        c_path = os.path.join(self.c_folder, self.config)
        with open(c_path, 'w') as config_file:
            config.write(config_file)

    def load_config(self):
        config = configparser.ConfigParser()
        c_path = os.path.join(self.c_folder, self.config)
        config.read(c_path)
        for key in self.__dict__:
            if key in config['DEFAULT']:
                setattr(self, key, eval(config['DEFAULT'][key]))

    # switching test depending on the GUI
    def set_test(self, test):
        self.test = test

    def get_12bit_a_frames(self):
        return self.a_frames

    def get_12bit_b_frames(self):
        return self.b_frames

    def get_max_sigmas(self, guas_params_a_x, guas_params_a_y, guas_params_b_x, guas_params_b_y):
        mu_a_x, sigma_a_x, amp_a_x = guas_params_a_x
        mu_a_y, sigma_a_y, amp_a_y = guas_params_a_y

        mu_b_x, sigma_b_x, amp_b__x = guas_params_b_x
        mu_b_y, sigma_b_y, amp_b_y = guas_params_b_y

        max_sigma_x = max(sigma_a_x, sigma_b_x)
        max_sigma_y = max(sigma_a_y, sigma_b_y)

        return max_sigma_x, max_sigma_y

    def get_static_sigmas(self):
        return self.static_sigmas_x, self.static_sigmas_y

    def get_static_centers(self):
        return self.static_center_a, self.static_center_b

    def get_warp_matrix(self):
        return self.warp_matrix

    def get_warp_matrix2(self):
        return self.warp_matrix_2

    def set_current_run(self, datetime_string):
        self.current_run = datetime_string

    def set_static_sigmas(self, x, y):
        self.static_sigmas_x, self.static_sigmas_y = x, y

    def set_static_centers(self, a, b):
        self.static_center_a, self.static_center_b = a, b

    def set_warp_matrix(self, w):
        self.warp_matrix = w

    def set_warp_matrix2(self, w):
        self.warp_matrix_2 = w

    def offer_to_jump(self, highest_possible_jump):
        if self.test:
            offer = 'n'
        else:
            offer = uiv.yes_no_quit(sd.OFFER_TO_JUMP.value)
        level_descriptions = {
            1: sd.S01_DESC.value,
            2: sd.S02_DESC_NO_PREV_WARP_MATRIX.value,
            3: sd.S03_DESC.value,
            4: sd.S04_DESC.value,
            5: sd.S05_DESC.value,
            6: sd.S06_DESC.value
        }

        options = set()

        if offer is True:
            for i in range(1, max(level_descriptions.keys()) + 1):
                if i <= highest_possible_jump:
                    print(level_descriptions[i])
                    options.add(str(i))

            jump_level_input = input(sd.WHICH_LEVEL.value)

            while not uiv.valid_input(jump_level_input, options):
                jump_level_input = input(sd.WHICH_LEVEL.value)

            self.jump_level = int(jump_level_input)

    def get_cameras(self, config_files, test):
        """
        Should be called AFTER and with the return value of find_devices() (as implied by the first parameter: devices)
        Args:
            config_files: An integer
        Raises:
            Exception: Any error/exception other than 'no such file or directory'.
        Returns:
            dict: A dictionary of cameras with ascending lowercase alphabetical letters as keys.
        """

        # updates test
        self.test = test

        # check if this is a test run
        if self.test:
            # default cam
            vid = cv2.VideoCapture(0)
            vid2 = cv2.VideoCapture(0)
            devices = [vid, vid2]
        else:
            tlFactory = pylon.TlFactory.GetInstance()  # Get the transport layer factory.
            devices = tlFactory.EnumerateDevices()  # Get all attached devices and exit application if no device is found.

            cameras = dict()

            # Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
            instant_camera_array = pylon.InstantCameraArray(min(len(devices), 2))
            self.all_cams = instant_camera_array

            for i, cam in enumerate(instant_camera_array):
                cam.Attach(tlFactory.CreateDevice(devices[i]))
                print("Camera ", i, "- Using device ", cam.GetDeviceInfo().GetModelName())  # Print camera model number

                cam.Open()
                # 1st camera will be a (ASCII = 97 + 0 = 97), 2nd will be b (ASCII = 97 + 1 = 98) and so on.
                pylon.FeaturePersistence.Load(config_files[chr(97 + i)], cam.GetNodeMap())
                cameras[chr(97 + i)] = cam

                if i == 0:
                    self.cam_a = cam
                if i == 1:
                    self.cam_b = cam

            self.all_cams = instant_camera_array

    def keep_streaming(self, one_by_one=False):
        if self.continuous:
            if cv2.waitKey(1) & 0xFF == ord(self.break_key):
                return False
            if self.test:
                return False
            if not self.all_cams.IsGrabbing():
                return False
            if (not one_by_one) and not self.all_cams.IsGrabbing():
                return False
            if one_by_one and not self.all_cams.IsGrabbing():
                return True
            return True
        if self.single_shot and (not self.continuous):
            if self.tkapp.stop_streaming_override is True:
                return False
            else:
                if cv2.waitKey(100) & 0xFF == ord(self.break_key):
                    return False
        return True

    def find_centers(self, frame_a_16bit, frame_b_16bit):

        x_a, y_a = fgp.get_coordinates_of_maximum(frame_a_16bit)
        x_b, y_b = fgp.get_coordinates_of_maximum(frame_b_16bit)

        return (x_a, y_a), (x_b, y_b)

    def grab_frames(self, warp_matrix=None, s8=False):
        if self.test:
            # Grab cameras
            a = self.cam_a[self.frame_count]
            b = self.cam_b[self.frame_count]

            # check for warp matrix
            if warp_matrix is None:
                return a, b
            else:
                a = cv2.imread(a)
                b = cv2.imread(b)
                b1_shape = b.shape[1], b.shape[0]
                b_prime = cv2.warpAffine(b, warp_matrix, b1_shape, flags=cv2.WARP_INVERSE_MAP)
                self.b_prime_frames.append(b_prime)
                return a, b_prime
            # return the values from the images
            return a, b

        elif self.continuous:
            try:
                timeout_ms = 3600000
                grab_result_a = self.cam_a.RetrieveResult(timeout_ms, pylon.TimeoutHandling_ThrowException)
                grab_result_b = self.cam_b.RetrieveResult(timeout_ms, pylon.TimeoutHandling_ThrowException)

                if grab_result_a.GrabSucceeded() and grab_result_b.GrabSucceeded():

                    a, b = grab_result_a.GetArray(), grab_result_b.GetArray()
                    grab_result_a.Release()
                    grab_result_b.Release()

                    if s8:
                        self.s8_full_a_frames.append(a)
                        self.s8_full_b_frames.append(b)

                    if warp_matrix is None:
                        return a, b
                    else:
                        b1_shape = b.shape[1], b.shape[0]
                        b_prime = cv2.warpAffine(b, warp_matrix, b1_shape, flags=cv2.WARP_INVERSE_MAP)
                        self.b_prime_frames.append(b_prime)
                        return a, b_prime
            except Exception as e:
                traceback.print_exc()
                raise e
        if self.single_shot and (not self.continuous):
            try:
                if self.test:
                    timeout_ms = 120000
                    grab_result_a = cv2.imread(self.current_frame_a)
                    grab_result_b = cv2.imread(self.current_frame_b)
                else:
                    if not self.all_cams.IsGrabbing():
                        self.all_cams.StartGrabbing()
                    timeout_ms = 120000
                    grab_result_a = self.cam_a.RetrieveResult(timeout_ms, pylon.TimeoutHandling_ThrowException)
                    grab_result_b = self.cam_b.RetrieveResult(timeout_ms, pylon.TimeoutHandling_ThrowException)

                if grab_result_a.GrabSucceeded() and grab_result_b.GrabSucceeded():
                    a, b = grab_result_a.GetArray(), grab_result_b.GetArray()
                    grab_result_a.Release()
                    grab_result_b.Release()

                    if s8:
                        self.s8_full_a_frames.append(a)
                        self.s8_full_b_frames.append(b)

                    if warp_matrix is None:
                        return a, b
                    else:
                        b1_shape = b.shape[1], b.shape[0]
                        b_prime = cv2.warpAffine(b, warp_matrix, b1_shape, flags=cv2.WARP_INVERSE_MAP)
                        self.b_prime_frames.append(b_prime)
                        return a, b_prime
            except Exception as e:
                if self.all_cams.IsGrabbing():
                    self.all_cams.StopGrabbing()
                traceback.print_exc()
                raise e
            finally:
                if self.all_cams.IsGrabbing():
                    self.all_cams.StopGrabbing()

    def grab_frames2(self, roi_a, roi_b, warp_matrix_2):
        if warp_matrix_2 is None:
            return roi_a, roi_b

        roi_shape = roi_b.shape[1], roi_b.shape[0]
        roi_b_double_prime = cv2.warpAffine(roi_b, warp_matrix_2, roi_shape, flags=cv2.WARP_INVERSE_MAP)
        return roi_a, roi_b_double_prime

    def show_16bit_representations(self, a_as_12bit, b_as_12bit, b_prime=False, show_centers=False):
        # convert to 16 bit images
        if self.test:
            a_as_16bit, b_as_16bit = bdc.to_16_bit(a_as_12bit, original_bit_depth=16), bdc.to_16_bit(b_as_12bit, original_bit_depth=16)
        else:
            a_as_16bit, b_as_16bit = bdc.to_16_bit(a_as_12bit), bdc.to_16_bit(b_as_12bit)

        if not show_centers:
            if not b_prime:
                if self.test:
                    for image_a in self.cam_a:
                        # display image
                        im1 = cv2.imread(image_a)
                        cv2.imshow("Image", im1)
                        k = cv2.waitKey(0)

                        # If the 'q' key is pressed, quit the loop
                        if k == ord('q'):
                            break

                        # close window
                        cv2.destroyAllWindows()

                    for image_b in self.cam_b:
                        # display image
                        im2 = cv2.imread(image_b)
                        cv2.imshow("Image", im2)
                        k = cv2.waitKey(0)

                        # If the 'q' key is pressed, quit the loop
                        if k == ord('q'):
                            break

                        # close window
                        cv2.destroyAllWindows()
                else:
                    cv2.imshow("Cam A", a_as_16bit)
                    cv2.imshow("Cam B", b_as_16bit)
            else:
                cv2.imshow("A", a_as_16bit)
                cv2.imshow("B Prime", b_as_16bit)
        else:
            center_a, center_b = self.find_centers(a_as_16bit, b_as_16bit)
            a, b = self.imgs_w_centers(a_as_16bit, center_a, b_as_16bit, center_b)
            if not b_prime:
                cv2.imshow("Cam A", a)
                cv2.imshow("Cam B", b)
            else:
                cv2.imshow("A", a)
                cv2.imshow("B Prime", b)

    def imgs_w_centers(self, a_16bit_color, center_a, b_16bit_color, center_b):
        img_a = cv2.circle(a_16bit_color, center_a, 10, (0, eight_bit_max, 0), 2)
        img_b = cv2.circle(b_16bit_color, center_b, 10, (0, eight_bit_max, 0), 2)
        return img_a, img_b

    def full_img_w_roi_borders(self, img_12bit, center_):

        try:
            mu_x, sigma_x, amp_x = fgp.get_gaus_boundaries_x(img_12bit, center_)
            mu_y, sigma_y, amp_y = fgp.get_gaus_boundaries_y(img_12bit, center_)

            try:

                img_12bit[:, int(center_[0]) + int(sigma_x * 2)] = twelve_bit_max
                img_12bit[:, int(center_[0]) - int(sigma_x * 2)] = twelve_bit_max

                img_12bit[int(center_[1]) + int(sigma_y * 2), :] = twelve_bit_max
                img_12bit[int(center_[1]) - int(sigma_y * 2), :] = twelve_bit_max

            except IndexError:
                print("Warning: 4 sigma > frame height or width.")

        except RuntimeError:
            print("Warning: RuntimeError occurred while trying to calculate gaussian! ")

        return img_12bit

    def show_frame_by_frame(self):
        pass

    def pre_alignment(self, histogram=False, centers=False, roi_borders=False, crop=False):
        a, b = self.current_frame_a, self.current_frame_b

        if roi_borders:
            a_as_16bit = bdc.to_16_bit(a)
            b_as_16bit = bdc.to_16_bit(b)

            if self.static_center_a is None or self.static_center_b is None:
                ca, cb = self.find_centers(a_as_16bit, b_as_16bit)
                self.set_static_centers(ca, cb)
                a = self.full_img_w_roi_borders(a, ca)
                b = self.full_img_w_roi_borders(b, cb)
            else:
                print("Cam A:")
                a = self.full_img_w_roi_borders(a, self.static_center_a)
                print("Cam B:")
                b = self.full_img_w_roi_borders(b, self.static_center_b)

        if histogram:
            self.histocam_a.update(a)
            self.histocam_b.update(b)
            histocams = hgs.add_histogram_representations(self.histocam_a.get_figure(), self.histocam_b.get_figure(), a, b)
            cv2.imshow("Cameras with Histograms", histocams)
        else:
            if roi_borders or crop:
                self.show_16bit_representations(a, b, False, False)
            else:
                self.show_16bit_representations(a, b, False, centers)

    def start(self, config_files, config_folder, test, reason, args, run_directory2, current_direc,
              stepList, prev_direc, histogram=False):
        # update test
        self.test = test

        # update reason
        self.reason = reason

        # copies args into other files for use in steps
        self.args = args

        # sets the test directory being used
        self.test_dir = current_direc + '/test-data'

        # sets stepList for steps 1-5
        self.stepList = stepList

        # sets the previous directory that will be used
        self.prev_direc = prev_direc

        # verbose description
        if self.args.verbose:
            print("This is the stream.\n"
                  "This is used as a wrapper to hold the data as the user goes through the steps of\n"
                  "this program. At the end of each step, the parameter data will be stored here as\n"
                  "well as saved to config.ini inside of the premade data folders.")

        print("self.continuous: ", self.continuous)
        print("self.single_shot: ", self.single_shot)

        if self.test:
            # get a test image
            images1 = glob.glob('/home/andrew/Desktop/2D-folder/test-data/cam_a_frames/*.png')
            images2 = glob.glob('/home/andrew/Desktop/2D-folder/test-data/cam_b_frames/*.png')
            images1 = natsort.natsorted(images1)
            images2 = natsort.natsorted(images2)

            # prep the windows
            cv2.namedWindow('Image1', cv2.WINDOW_NORMAL)
            cv2.namedWindow('Image2', cv2.WINDOW_NORMAL)

            # updates the camera parameters
            self.cam_a, self.cam_b = images1, images2

            # go through the test stream
            for image in images1:
                img1 = cv2.imread(image)
                self.current_frame_a = image

                # Display the frame
                cv2.imshow('Image1', img1)

                # Wait for a key press
                k = cv2.waitKey(0)

                # If the 'q' key is pressed, quit the loop
                if k == ord('q'):
                    break
            for image in images2:
                img2 = cv2.imread(image)
                self.current_frame_b = image

                # Display the frame
                cv2.imshow('Image2', img2)

                # Wait for a key press
                k = cv2.waitKey(0)

                # If the 'q' key is pressed, quit the loop
                if k == ord('q'):
                    break

            devices = [images1, images2]
            self.all_cams = devices

            # Close all windows
            cv2.destroyAllWindows()
        else:
            tlFactory = pylon.TlFactory.GetInstance()
            devices = tlFactory.EnumerateDevices()
            if len(devices) == 0:
                raise Exception("No camera present.")

            self.all_cams = pylon.InstantCameraArray(2)
            self.cam_a, self.cam_b = self.all_cams[0], self.all_cams[1]
            for i, camera in enumerate(self.all_cams):
                camera.Attach(tlFactory.CreateDevice(devices[i]))
                camera.Open()
                pylon.FeaturePersistence.Load(config_files[chr(97 + i)], camera.GetNodeMap())

            # Starts grabbing for all cameras
            if self.continuous:
                self.all_cams.StartGrabbing(pylon.GrabStrategy_LatestImageOnly, pylon.GrabLoop_ProvidedByUser)

        calibration_success = False
        continue_stream = False
        cwd = os.getcwd()
        run_folder = os.path.join(run_directory2)
        self.current_run = run_directory2
        self.prv_run_dir = fpr.get_latest_run_direc(path_override=True, path_to_exclude=self.current_run)

        # save to config
        self.c_folder = config_folder
        self.save_config()

        while calibration_success is not True:
            try:
                app = tk_app.App(self)
                self.tkapp = app
                if self.jump_level <= 1:
                    s1.step_one(self, histogram, continue_stream)

                if self.jump_level <= 2:
                    s2.step_two(self, continue_stream)
                else:
                    s2.step_two(self, continue_stream, autoload_prev_wm1=True)
                sp.store_warp_matrices(self, run_folder)

                if self.jump_level <= 3:
                    s3.step_three(self)
                else:
                    s3.step_three(self, autoload_prev_static_centers=True)
                sp.store_static_centers(self, run_folder)

                if self.warp_matrix is None:
                    self.jump_level = 10

                if self.jump_level <= 4:
                    s4.step_four(self, continue_stream)
                else:
                    s4.step_four(self, continue_stream, autoload_roi=True)
                sp.store_static_sigmas(self, run_folder)
                sp.store_max_n_sigma(self, run_folder)

                if self.jump_level <= 5:
                    s5.step_five(self, continue_stream)

                calibration_success = True

            except Exception as e:
                print("Exception occurred somewhere along the script")
                # self.tkapp.destroy()
                #tk_app.attempt_to_quit(self.tkapp)
                raise e
            finally:
                pass


        figs, histograms, lines = hgs.initialize_histograms_rois()
        figs_alg, histograms_alg, lines_alg = hgs.initialize_histograms_algebra()
        figs_r, histograms_r, lines_r = hgs.initialize_histograms_r()
        time.sleep(1)

        step = 6

        if self.static_center_a is None or self.static_center_b is None:
            print("Regions of Interest not defined: Exiting Program")
            sys.exit(0)

        if self.jump_level <= step:
            s6.step_six(self, app, figs, histograms, lines, histograms_alg, lines_alg, figs_alg,
                   histograms_r, lines_r, figs_r)

            sp.store_n_sigma(self, run_folder)
            sp.store_offsets(self, run_folder)

        self.stats = list()
        self.a_frames = list()
        self.b_prime_frames = list()

        self.a_images = list()
        self.b_prime_images = list()

        # destroy all previous tk windows
        # for window in self.tkapp.root.winfo_children():
        #     window.destroy()
        # time.sleep(1)
        # self.tkapp.root.quit()
        # self.tkapp.root.destroy()
        # tk_app.attempt_to_quit(self.tkapp)
        # time.sleep(1)
        # this is where the runGUI will start
        # runGUI.begin_run(self.data_directory)



        if self.jump_level <= 7:
            s7.step_seven(self, run_folder, app, figs, histograms, lines, histograms_alg, lines_alg, figs_alg,
               histograms_r, lines_r, figs_r)


        if self.jump_level <= 8:
            s8.step_eight(self, self.start_writing_at, self.end_writing_at, run_folder, self.a_images, self.s8_full_a_frames,
                         self.b_prime_images, self.s8_full_b_frames, self.stats)

        if self.test:
            print("test passed")
            tk_app.attempt_to_quit(self.tkapp)
            sys.exit(0)

        elif self.all_cams.IsGrabbing():
            self.all_cams.StopGrabbing()
        s9.step_nine(run_folder)
        tk_app.attempt_to_quit(self.tkapp)
        print("Command line made it here")
        #sys.exit(0)

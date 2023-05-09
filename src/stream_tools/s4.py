from coregistration import find_gaussian_profile as fgp
from image_processing import bit_depth_conversion as bdc
import cv2
import traceback
import os
import pickle
from experiment_set_up import find_previous_run as fpr
from experiment_set_up import user_input_validation as uiv
from exceptions import  coregistration_exceptions as cre
from constants import STEP_DESCRIPTIONS as sd
from gui import popups

cam_frame_height_pixels = 1080
cam_frame_width_pixels = 1920

def step_four(stream, continue_stream, autoload_roi=False):
    if stream.args.verbose:
        print("""
        Step 4
        This step finds the Regions of interest of both images.
        The Regions of Interest are comprised of:
            Sigma_X: Standard deviation of beam's gaussian profile in the horizontal direction
            Sigma_Y: Standard deviation of beam's gaussian profile in the vertical direction
            Static Center A: The coordinates of the Gaussian Peak for Camera A
            Static Center B: The coordinates of the Gaussian Peak for Camera B
    
             _ _ _ _ _ _ _ _ _
            |                 |
            |                 |
            |    (x_a,y_a)    | 2*sigma_y
            |                 |
            |                 |
             _ _ _ _ _ _ _ _ _
                 2*sigma_x
    
        Args:
            stream (Stream): Instance of stream class currently connected to cameras
            continue_stream (bool): Should camera keep streaming. TODO: CHECK IF THIS CAN JUST EXIST IN S5 NAMESPACE

        """)
    if stream.test:
        previous_run_directory = stream.test_dir
    previous_run_directory = fpr.get_latest_run_direc(path_override=True, path_to_exclude=stream.current_run)
    # autoload_roi = True
    autoload_roi = popups.yes_no_popup("Would you like to autoload roi?")
    # print(previous_run_directory)

    prev_sigma_x_path = os.path.join(previous_run_directory, "static_sigma_x.p")
    prev_sigma_x_exist = os.path.exists(prev_sigma_x_path)

    prev_sigma_y_path = os.path.join(previous_run_directory, "static_sigma_y.p")
    prev_sigma_y_exist = os.path.exists(prev_sigma_y_path)

    prev_max_n_sigma_path = os.path.join(previous_run_directory, "max_n_sigma.p")
    prev_max_n_sigma_exists = os.path.exists(prev_max_n_sigma_path)


    if autoload_roi and prev_sigma_x_exist and prev_sigma_y_exist and prev_max_n_sigma_exists:
        with open(prev_sigma_x_path, 'rb') as fp:
            stream.static_sigmas_x = pickle.load(fp)

        with open(prev_sigma_y_path, 'rb') as fp:
            stream.static_sigmas_y = pickle.load(fp)

        with open(prev_max_n_sigma_path, 'rb') as fp:
            stream.max_n_sigma = pickle.load(fp)

        cv2.destroyAllWindows()
        stream.save_config()
        return

    max_n_sigma = 0
    s5_frame_count = 0
    step_description = sd.S04_DESC.value
    # find_rois_ = uiv.yes_no_quit(step_description)
    find_rois_ = popups.yes_no_popup(step_description)
    failed_frame_count = 0
    print("2")
    if find_rois_ is True:
        continue_stream = True
    print("3")
    while continue_stream:
        stream.frame_count += 1
        stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)

        #n_sigma = 1
        # n_sigmas_to_attempt = [1, 1.25, 1.50, 1.75, 2.0, 2.25, 2.5]
        n_sigmas_to_attempt = [1]
        last_successful_index = -1
        try:
            print("4")
            max_n_sigma = 1
            for n_sigma in n_sigmas_to_attempt:  # , , 1.75, 2.00, 2.50]:
                #print("Attempting n_sigma = ", n_sigma)
                attempt_successful = True
                stream.mu_x, stream.sigma_a_x, stream.amp_x = fgp.get_gaus_boundaries_x(stream.current_frame_a,
                                                                                        stream.static_center_a)
                stream.mu_y, stream.sigma_a_y, stream.amp_y = fgp.get_gaus_boundaries_y(stream.current_frame_a,
                                                                                        stream.static_center_a)

                stream.mu_x, stream.sigma_b_x, stream.amp_x = fgp.get_gaus_boundaries_x(stream.current_frame_b,
                                                                                        stream.static_center_b)
                stream.mu_y, stream.sigma_b_y, stream.amp_y = fgp.get_gaus_boundaries_y(stream.current_frame_b,
                                                                                        stream.static_center_b)

                if int(stream.static_center_a[1]) + int(stream.sigma_a_y * n_sigma) > cam_frame_height_pixels:
                    attempt_successful = False
                if int(stream.static_center_b[1]) + int(stream.sigma_b_y * n_sigma) > cam_frame_height_pixels:
                    attempt_successful = False

                if int(stream.static_center_a[0]) + int(stream.sigma_a_x * n_sigma) > cam_frame_width_pixels:
                    attempt_successful = False
                if int(stream.static_center_b[0]) + int(stream.sigma_b_x * n_sigma) > cam_frame_width_pixels:
                    attempt_successful = False

                if attempt_successful:
                    stream.current_frame_a[:, int(stream.static_center_a[0]) + int(stream.sigma_a_x * n_sigma)] = 4095
                    stream.current_frame_a[:, int(stream.static_center_a[0]) - int(stream.sigma_a_x * n_sigma)] = 4095
                    stream.current_frame_a[int(stream.static_center_a[1]) + int(stream.sigma_a_y * n_sigma), :] = 4095
                    stream.current_frame_a[int(stream.static_center_a[1]) - int(stream.sigma_a_y * n_sigma), :] = 4095

                    stream.current_frame_b[:, int(stream.static_center_b[0]) + int(stream.sigma_b_x * n_sigma)] = 4095
                    stream.current_frame_b[:, int(stream.static_center_b[0]) - int(stream.sigma_b_x * n_sigma)] = 4095
                    stream.current_frame_b[int(stream.static_center_b[1]) + int(stream.sigma_b_y * n_sigma), :] = 4095
                    stream.current_frame_b[int(stream.static_center_b[1]) - int(stream.sigma_b_y * n_sigma), :] = 4095

                    last_successful_index += 1
                    print(last_successful_index)


            a_as_16bit = bdc.to_16_bit(stream.current_frame_a)
            b_as_16bit = bdc.to_16_bit(stream.current_frame_b)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)
                cv2.destroyAllWindows()
            cv2.imshow("A", a_as_16bit)
            cv2.imshow("B Prime", b_as_16bit)

            s5_frame_count += 1
            continue_stream = stream.keep_streaming()
            print("5")
        except cre.BeamNotGaussianException:
            a_as_16bit = bdc.to_16_bit(stream.current_frame_a)
            b_as_16bit = bdc.to_16_bit(stream.current_frame_b)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)
                cv2.destroyAllWindows()
            cv2.imshow("A", a_as_16bit)
            cv2.imshow("B Prime", b_as_16bit)
            continue_stream = stream.keep_streaming()

        except Exception as e:
            print("Exception Occurred On n_sigma = ", n_sigma)

            if last_successful_index > -1:
                print("Last Successful n_sigma = ", max_n_sigma)
            elif last_successful_index == -1:
                print("The Script can not display an ROI due to an over sized sigma.\n"
                      "Please either reduce your beam size or overall brightness")
                failed_frame_count += 1
                print("Failed Frame Count: ", failed_frame_count)
                if failed_frame_count >= 50:
                    raise e


        # if stream.frame_count % 15 == 0:
        # print("\tB  - Sigma X, Sigma Y - {}".format((int(stream.sigma_b_x), int(stream.sigma_b_y))))

        if continue_stream is False:
            if int(max(stream.sigma_a_x, stream.sigma_b_x)) < 50 or int(max(stream.sigma_a_y, stream.sigma_b_y)) < 50:
                raise cre.ROITooSmallException()

            # stream.static_sigmas_x = int(max(stream.sigma_a_x, stream.sigma_b_x))
            # stream.static_sigmas_y = int(max(stream.sigma_a_y, stream.sigma_b_y))
            stream.static_sigmas_x = int(input("sigma a: "))
            stream.static_sigmas_y = int(input("sigma b: "))

            print("static sigma x: ", stream.static_sigmas_x)
            print("static sigma y: ", stream.static_sigmas_y)

        #print("max_n_sigma: ", n_sigmas_to_attempt[last_successful_index])
        stream.max_n_sigma = n_sigmas_to_attempt[last_successful_index]
    cv2.destroyAllWindows()
    stream.save_config()

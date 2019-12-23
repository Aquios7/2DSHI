from pypylon import genicam, pylon  # Import relevant pypylon packages/modules
import traceback  # exception handling
import cv2
from image_processing import bit_depth_conversion as bdc
from image_processing import stack_images as stack
from histocam import histocam
import numpy as np




class Stream:
    def __init__(self):
        self.cam_a = None
        self.cam_b = None
        self.all_cams = None
        self.latest_grab_results = {"a": None, "b": None}
        self.frame_count = 0
        self.frame_break = 1000
        self.break_key = 'q'
        self.current_frame_a = None
        self.current_frame_b = None
        self.histocam_a = None
        self.histocam_b = None
        self.stacked_streams = None

    def get_cameras(self, config_files):
        """
        Should be called AFTER and with the return value of find_devices() (as implied by the first parameter: devices)


        Args:
            devices: An instance of tlFactory.EnumerateDevices()
            num_cameras (int): An integer
            config_files: An integer
        Raises:
            Exception: Any error/exception other than 'no such file or directory'.
        Returns:
            dict: A dictionary of cameras with ascending lowercase alphabetical letters as keys.
        """

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

    def keep_streaming(self):
        if not self.all_cams.IsGrabbing():
            return False
        if self.frame_count >= self.frame_break:
            return False
        if cv2.waitKey(1) & 0xFF == ord(self.break_key):
            return False
        return True

    def grab_frames(self):
        try:
            grab_result_a = self.cam_a.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            grab_result_b = self.cam_b.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grab_result_a.GrabSucceeded() and grab_result_b.GrabSucceeded():
                return grab_result_a.GetArray(), grab_result_b.GetArray()
        except Exception as e:
            raise e

    def show_16bit_representations(self, a_as_12bit, b_as_12bit):
        a_as_16bit = bdc.to_16_bit(a_as_12bit)
        b_as_16bit = bdc.to_16_bit(b_as_12bit)
        cv2.imshow("Cam A", a_as_16bit)
        cv2.imshow("Cam B", b_as_16bit)

    def start(self, histogram=False):

        if self.histocam_a is None or self.histocam_b is None:
            self.histocam_a = histocam.Histocam()
            self.histocam_b = histocam.Histocam()

        self.all_cams.StartGrabbing()

        while self.keep_streaming():
            self.frame_count += 1
            self.current_frame_a, self.current_frame_b = self.grab_frames()

            if histogram:
                self.histocam_a.update(self.current_frame_a)
                self.histocam_b.update(self.current_frame_b)
                p = self.histocam_a.get_plot()
                stack_ = stack.horizontal(bdc.to_8_bit(self.current_frame_a), p)
                stack_ = cv2.resize(stack_, (1000, 500))

                print(stack_.shape)
                #hist = self.histocam_a.get_plot()
                cv2.imshow("StackTest", stack_)
            #else:
            #self.show_16bit_representations(self.current_frame_a, self.current_frame_b)
            #self.show_16bit_representations(self.current_frame_a, self.current_frame_b)
            #r = stack.horizontal(bdc.to_16_bit(self.current_frame_a), bdc.to_16_bit(self.current_frame_b))
            #r = cv2.resize(r, (1000, 500))
            #cv2.imshow("stack", r)


        self.all_cams.StopGrabbing()
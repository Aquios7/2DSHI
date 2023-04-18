import cv2
from experiment_set_up import find_previous_run as fpr
import os, sys
import numpy as np
from image_processing import bit_depth_conversion as bdc
from coregistration import img_characterization as ic
from experiment_set_up import user_input_validation as uiv
from constants import STEP_DESCRIPTIONS as sd


def step_two(stream, continue_stream, autoload_prev_wm1=False):
    if stream.args.verbose:
        print("""
        Step 2
        This step finds or imports initial co-registration matrix. For details see links below
            https://mathworld.wolfram.com/AffineTransformation.html
            https://math.stackexchange.com/questions/13150/extracting-rotation-scale-values-from-2d-transformation-matrix
    
        Args:
            stream (Stream): An instance of the Stream class currently connected to cameras.
            continue_stream (bool): TODO: Check if this is needed as a parameter, or can exist within s2
    
        Returns:
            bool: The return value. True for success, False otherwise.
        """)

    # ((translationx, translationy), rotation, (scalex, scaley), shear)

    # point warp matrix at test folder
    if stream.test:
        previous_run_directory = fpr.get_latest_run_direc(path_override=True, path_to_exclude=stream.test_dir)
        prev_wp1_path = os.path.join(previous_run_directory, "wm1.npy")
    else:
        previous_run_directory = fpr.get_latest_run_direc(path_override=True, path_to_exclude=stream.current_run)
        prev_wp1_path = os.path.join(previous_run_directory, "wm1.npy")
    prev_wp1_exist = os.path.exists(prev_wp1_path)

    if prev_wp1_exist and autoload_prev_wm1:
        stream.warp_matrix = np.load(prev_wp1_path)
        cv2.destroyAllWindows()
        stream.save_config()
        return

    coregister_ = False

    if prev_wp1_exist:
        step_description = sd.S02_DESC_PREV_WARP_MATRIX.value
        #step_description = "Step 2 - You created a Warp Matrix 1 last run. Would you like to use it?"
        use_last_wp1 = uiv.yes_no_quit(step_description, app=stream)
        # creating warp matrix
        if use_last_wp1 is True:
            stream.warp_matrix = np.load(prev_wp1_path)
            stream.warp_matrix = stream.warp_matrix.copy()
        else:
            coregister_ = True
    else:
        step_description = sd.S02_DESC_NO_PREV_WARP_MATRIX.value
        #step_description = "Step 2 - New Co-Registration with with Euclidean Transform?"
        coregister_ = uiv.yes_no_quit(step_description)

    if coregister_ is True:
        warp_ = None
        retry = True
        warp_successful = False

        while retry or (not warp_successful):
            try:
                for i in range(2):
                    stream.frame_count += 1
                    stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)

                a_8bit = bdc.to_8_bit(stream.current_frame_a)
                b_8bit = bdc.to_8_bit(stream.current_frame_b)
                warp_ = ic.get_euclidean_transform_matrix(a_8bit, b_8bit)
                retry = False
                warp_successful = True
            except (GeneratorExit, KeyboardInterrupt, SystemExit, Exception):
                #pass
            #except cv2.Error or Exception:
                warp_successful = False
                desc = "Warp Matrix was not successful. Try again?"
                retry = uiv.yes_no_quit(desc)
                if retry is False:
                    print("Script may not continue without Warp Matrix 1")
                    sys.exit(0)


        stream.warp_matrix = warp_

        a, b, tx = warp_[0][0], warp_[0][1], warp_[0][2]
        c, d, ty = warp_[1][0], warp_[1][1], warp_[1][2]

        print("\tTranslation X:{}".format(tx))
        print("\tTranslation Y:{}\n".format(ty))

        scale_x = np.sign(a) * (np.sqrt(a ** 2 + b ** 2))
        scale_y = np.sign(d) * (np.sqrt(c ** 2 + d ** 2))

        print("\tScale X:{}".format(scale_x))
        print("\tScale Y:{}\n".format(scale_y))

        phi = np.arctan2(-1.0 * b, a)
        print("\tPhi Y (rad):{}".format(phi))
        print("\tPhi Y (deg):{}\n".format(np.degrees(phi)))

        temp_a_8bit = np.array(stream.current_frame_a, dtype='uint8')  # bdc.to_8_bit()
        temp_b_prime_8bit = np.array(stream.current_frame_b, dtype='uint8')
        # temp_b_prime_8bit = bdc.to_8_bit(stream.current_frame_b)
        orb = cv2.ORB_create(nfeatures=10000, scoreType=cv2.ORB_FAST_SCORE, nlevels=20)
        keypoints1, descriptors1 = orb.detectAndCompute(temp_a_8bit, None)
        keypoints2, descriptors2 = orb.detectAndCompute(temp_b_prime_8bit, None)

        print("A has {} key points".format(len(keypoints1)))
        print("B has {} key points".format(len(keypoints2)))
        # cv2.drawMatchesKnn expects list of lists as matches.

        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)
        # matches.sort(key=lambda x: x.distance, reverse=False)
        # BFMatcher with default params
        bf = cv2.BFMatcher()
        knn_matches = bf.knnMatch(descriptors1, descriptors2, k=2)
        lowe_ratio = 0.89

        # Apply ratio test_RminRmax
        good_knn = []

        for m, n in knn_matches:
            if m.distance < lowe_ratio * n.distance:
                good_knn.append([m])

        print("Percentage of Matches within Lowe Ratio of 0.89: {0:.4f}".format(
            100 * float(len(good_knn)) / float(len(knn_matches))))

        imMatches = cv2.drawMatches(temp_a_8bit, keypoints1, temp_b_prime_8bit, keypoints2, matches[:25], None)
        cv2.imshow("DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING",
                   cv2.resize(imMatches, (int(imMatches.shape[1] * 0.5), int(imMatches.shape[0] * 0.5))))
        cv2.waitKey(60000)
        cv2.destroyAllWindows()

    continue_stream = True
    while continue_stream:
        stream.frame_count += 1
        stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)
        # setting up the images for test
        if stream.test:
            a_as_16bit = cv2.imread(stream.current_frame_a)
            b_as_16bit = cv2.imread(stream.current_frame_b)
        # actual run
        else:
            a_as_16bit = bdc.to_16_bit(stream.current_frame_a)
            b_as_16bit = bdc.to_16_bit(stream.current_frame_b)

        cv2.imshow("A", a_as_16bit)
        cv2.imshow("B Prime", b_as_16bit)
        continue_stream = stream.keep_streaming()

    cv2.destroyAllWindows()
    stream.save_config()

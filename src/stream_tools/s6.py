from image_processing import bit_depth_conversion as bdc
from coregistration import img_characterization as ic
import numpy as np
import os
import cv2
from experiment_set_up import find_previous_run as fpr
from experiment_set_up import user_input_validation as uiv

y_n_msg = "Proceed? (y/n): "

def load_wm2_if_present(stream):
    previous_run_directory = fpr.get_latest_run_direc(path_override=True, path_to_exclude=stream.current_run)

    prev_wp2_path = os.path.join(previous_run_directory, "wm1.npy")
    prev_wp2_exist = os.path.exists(prev_wp2_path)

    if prev_wp2_exist:
        stream.warp_matrix = np.load(prev_wp2_path)
        cv2.destroyAllWindows()
        return


def step_six_a(stream, continue_stream):
    desc = "Step 6A - Close in on ROI?"
    close_in = uiv.yes_no_quit(desc)
    #close_in = input("Step 6A - Close in on ROI - {}".format(y_n_msg))

    if close_in is True:
        continue_stream = True

    while continue_stream:
        stream.frame_count += 1
        stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)

        x_a, y_a = stream.static_center_a
        x_b, y_b = stream.static_center_b

        n_sigma = 1

        stream.roi_a = stream.current_frame_a[
                     y_a - n_sigma * stream.static_sigmas_y: y_a + n_sigma * stream.static_sigmas_y + 1,
                     x_a - n_sigma * stream.static_sigmas_x: x_a + n_sigma * stream.static_sigmas_x + 1
                     ]

        stream.roi_b = stream.current_frame_b[
                     y_b - n_sigma * stream.static_sigmas_y: y_b + n_sigma * stream.static_sigmas_y + 1,
                     x_b - n_sigma * stream.static_sigmas_x: x_b + n_sigma * stream.static_sigmas_x + 1
                     ]

        cv2.imshow("ROI A", bdc.to_16_bit(stream.roi_a))
        cv2.imshow("ROI B Prime", bdc.to_16_bit(stream.roi_b))
        continue_stream = stream.keep_streaming()

    cv2.destroyAllWindows()


def step_six_b(stream, continue_stream, app):
    desc = "Step 6B - Re-Coregister?"
    find_rois_ = uiv.yes_no_quit(desc)
    #find_rois_ = input("Step 6B - Re-Coregister - {}".format(y_n_msg))

    if find_rois_ is True:
        continue_stream = True

    while continue_stream:
        stream.frame_count += 1
        stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)

        x_a, y_a = stream.static_center_a
        x_b, y_b = stream.static_center_b

        n_sigma = app.foo
        try:
            stream.roi_a = stream.current_frame_a[
                         y_a - n_sigma * stream.static_sigmas_y: y_a + n_sigma * stream.static_sigmas_y + 1,
                         x_a - n_sigma * stream.static_sigmas_x: x_a + n_sigma * stream.static_sigmas_x + 1
                         ]

            stream.roi_b = stream.current_frame_b[
                         y_b - n_sigma * stream.static_sigmas_y: y_b + n_sigma * stream.static_sigmas_y + 1,
                         x_b - n_sigma * stream.static_sigmas_x: x_b + n_sigma * stream.static_sigmas_x + 1
                         ]
        except Exception as e:
            print("Error occurred trying to set warp matrices")
            print("Please verify validity of following variables:")
            potential_error_vars = {
                "x_a": x_a,
                "y_a": y_a,
                "n_sigma": n_sigma,
                "stream.static_sigmas_y": stream.static_sigmas_y,
                "stream.static_sigmas_x": stream.static_sigmas_x,
            }

            for var in potential_error_vars:
                print(var, type(potential_error_vars[var]), var)

            raise e

        roi_a_8bit = bdc.to_8_bit(stream.roi_a)
        roi_b_8bit = bdc.to_8_bit(stream.roi_b)
        warp_2_ = ic.get_euclidean_transform_matrix(roi_a_8bit, roi_b_8bit)
        stream.warp_matrix_2 = warp_2_

        a, b, tx = warp_2_[0][0], warp_2_[0][1], warp_2_[0][2]
        c, d, ty = warp_2_[1][0], warp_2_[1][1], warp_2_[1][2]

        print("\tTranslation X:{}".format(tx))
        print("\tTranslation Y:{}\n".format(ty))

        scale_x = np.sign(a) * (np.sqrt(a ** 2 + b ** 2))
        scale_y = np.sign(d) * (np.sqrt(c ** 2 + d ** 2))

        print("\tScale X:{}".format(scale_x))
        print("\tScale Y:{}\n".format(scale_y))

        phi = np.arctan2(-1.0 * b, a)
        print("\tPhi Y (rad):{}".format(phi))
        print("\tPhi Y (deg):{}\n".format(np.degrees(phi)))
        continue_stream = False

    cv2.destroyAllWindows()

def step_six_c(stream, continue_stream):
    desc = "Step 6C - Display Re-Coregistered Images ?"
    display_new = uiv.yes_no_quit(desc)
    #display_new = input("Step 6C - Display Re-Coregistered Images - {}".format(y_n_msg))

    if display_new is True:
        continue_stream = True

    cv2.destroyAllWindows()

    while continue_stream:
        stream.frame_count += 1
        stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)

        x_a, y_a = stream.static_center_a
        x_b, y_b = stream.static_center_b

        n_sigma = 3.0

        stream.roi_a = stream.current_frame_a[
                     int(y_a - n_sigma * stream.static_sigmas_y): int(y_a + n_sigma * stream.static_sigmas_y) + 1,
                     int(x_a - n_sigma * stream.static_sigmas_x): int(x_a + n_sigma * stream.static_sigmas_x) + 1]

        stream.roi_b = stream.current_frame_b[
                     int(y_b - n_sigma * stream.static_sigmas_y): int(y_b + n_sigma * stream.static_sigmas_y) + 1,
                     int(x_b - n_sigma * stream.static_sigmas_x): int(x_b + n_sigma * stream.static_sigmas_x) + 1]

        cv2.imshow("ROI A", bdc.to_16_bit(stream.roi_a))
        cv2.imshow("ROI B Prime", bdc.to_16_bit(stream.roi_b))

        if stream.warp_matrix_2 is None:
            roi_a = stream.roi_a
            b_double_prime = stream.roi_b
        else:
            roi_a, b_double_prime = stream.grab_frames2(stream.roi_a.copy(), stream.roi_b.copy(), stream.warp_matrix_2.copy())

        cv2.imshow("ROI B DOUBLE PRIME", bdc.to_16_bit(b_double_prime))

        continue_stream = stream.keep_streaming()

    cv2.destroyAllWindows()
from coregistration import find_gaussian_profile as fgp
from image_processing import bit_depth_conversion as bdc
from image_processing import CenterOfMass as com
from experiment_set_up import find_previous_run as fpr
import pickle
import cv2
import os
from stream_tools import crossHairs
from experiment_set_up import user_input_validation as uiv
from constants import STEP_DESCRIPTIONS as sd
from matplotlib import pyplot
import matplotlib.ticker as plticker
from gui import popups

eight_bit_max = (2 ** 8) - 1
twelve_bit_max = (2 ** 12) - 1

# superfluous?
# y_n_msg = "Proceed? (y/n): "


def step_three(stream, autoload_prev_static_centers=False):
    if stream.args.verbose:
        print("""
        Step 3
        This is where you will calculate the static center based on the brightest pixel.
        Without the static center, teh region of interest will not be defined for the next steps, and the program will exit.
        """)
    if stream.test:
        previous_run_directory = stream.test_dir
        autoload_prev_static_centers = True
    else:
        previous_run_directory = fpr.get_latest_run_direc(path_override=True, path_to_exclude=stream.current_run)

    prev_sca_path = os.path.join(previous_run_directory, "static_center_a.p")
    prev_sca_exist = os.path.exists(prev_sca_path)

    prev_scb_path = os.path.join(previous_run_directory, "static_center_b.p")
    prev_scb_exist = os.path.exists(prev_scb_path)

    if autoload_prev_static_centers and prev_sca_exist and prev_scb_exist:
        with open(prev_sca_path, 'rb') as fp:
            stream.static_center_a = pickle.load(fp)

        with open(prev_scb_path, 'rb') as fp:
            stream.static_center_b = pickle.load(fp)

        cv2.destroyAllWindows()
        stream.save_config()
        return


    step_description = "S3 FREESTREAM GRIDLINES"
    if stream.test:
        freestream_ = False
    else:
        # freestream_ = uiv.yes_no_quit(step_description)
        freestream_ = popups.yes_no_popup(step_description)

    if freestream_ is True:
        continue_stream = True

        coords_frame_a, coords_frame_b = crossHairs.run(stream)

        while continue_stream:
            stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)

            y_gridlines = [99, 199, 299, 399,499,599,699,799,899,999,1099,1199,1299,1399,1499,1599,1699,1799,1899]
            x_gridlines = [99, 199, 299, 399,499,599,699,799,899,999,1099,1199]

            for cam_frame in [stream.current_frame_a, stream.current_frame_b]:
                for x_gridlines_index in x_gridlines:
                    cam_frame[x_gridlines_index, :] = twelve_bit_max
                for y_gridlines_index in y_gridlines:
                    cam_frame[:, y_gridlines_index] = twelve_bit_max

            a_as_16bit = bdc.to_16_bit(stream.current_frame_a)
            b_as_16bit = bdc.to_16_bit(stream.current_frame_b)

            cv2.imshow("A-GL", a_as_16bit)
            cv2.imshow("B Prime -GL", b_as_16bit)
            continue_stream = stream.keep_streaming()

        cv2.destroyAllWindows()
    cv2.destroyAllWindows()

        #here is where we find the static centers in a new run by looking for the brightest pixel




    step_description = sd.S03_DESC.value
    if stream.test:
        set_centers_ = False
    else:
        # set_centers_ = uiv.yes_no_quit(step_description)
        set_centers_ = popups.yes_no_popup(step_description)

    if set_centers_ is True:
        continue_stream = True

        if stream.current_frame_a is None or stream.current_frame_b is None:
            stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix)
        #here is where we find the static centers in a new run by looking for the brightest pixel

        a_as_16bit = bdc.to_16_bit(stream.current_frame_a)
        b_as_16bit = bdc.to_16_bit(stream.current_frame_b)

        max_pixel_a, max_pixel_b = stream.find_centers(a_as_16bit, b_as_16bit)
        print(max_pixel_a,max_pixel_b)
        #max_pixel_a, max_pixel_b = input("enter coordinates of the center of the object as '(ax,ay),(bx,by)'")

        stream.mu_a_x, stream.sigma_a_x, stream.amp_a_x = fgp.get_gaus_boundaries_x(stream.current_frame_a, max_pixel_a)
        stream.mu_a_y, stream.sigma_a_y, stream.amp_a_y = fgp.get_gaus_boundaries_y(stream.current_frame_a, max_pixel_a)

        stream.mu_b_x, stream.sigma_b_x, stream.amp_b_x = fgp.get_gaus_boundaries_x(stream.current_frame_b, max_pixel_b)
        stream.mu_b_y, stream.sigma_b_y, stream.amp_b_y = fgp.get_gaus_boundaries_y(stream.current_frame_b, max_pixel_b)

        print("Setting Centers\n")
        print("Calculated Gaussian Centers")
        stream.static_center_a = (int(stream.mu_a_x), int(stream.mu_a_y))
        # stream.static_center_b = (int(mu_b_x), int(mu_b_y))  # Original
        stream.static_center_b = (int(stream.mu_a_x), int(stream.mu_a_y))  # Picking A

        print("\t\tA                         : {}".format(stream.static_center_a))
        print("\t\tB Prime (Calculated)      : {}".format((int(stream.mu_b_x), int(stream.mu_b_y))))
        print("\t\tB Prime (Overwritten to A): {}".format(stream.static_center_a))

        option = input("Would you like to use the \n\tcalculated gaussian center (1) "
                       "\n\tor the overwritten gaussian center (2)  "
                       "\n\tor a user input(3):"
                       "\n\tor Center of Mass(4)")

        if option == "1":
            stream.static_center_b = (int(stream.mu_b_x), int(stream.mu_b_y))  # Picking A
        elif option == "2":
            stream.static_center_b = stream.static_center_a
        elif option =="3":
            stream.static_center_a = int(input("ax: ")), int(input("ay: "))
            stream.static_center_b = int(input("bx: ")), int(input("by: "))
        elif option =="4":
            stream.static_center_a = com.centerofmass(stream.current_frame_a)
            stream.static_center_b = com.centerofmass(stream.current_frame_b)



    else:
        continue_stream = False
        stream.jump_level = 10

    while continue_stream:
        stream.frame_count += 1



        a_as_16bit = bdc.to_16_bit(stream.current_frame_a)
        b_as_16bit = bdc.to_16_bit(stream.current_frame_b)

        """""
        This is all new to try to make grids on a visible cam a and cam b 
        """""
        # continue_stream = stream.keep_streaming()
        # my_dpi = 200
        #
        # fig = pyplot.figure(
        #     figsize=(float(stream.current_frame_a.size[0]) / my_dpi, float(stream.current_frame_a.size[1]) / my_dpi),
        #     dpi=my_dpi)
        # ax = fig.add_subplot(111)
        # # Set the gridding interval: here we use the major tick interval
        # myInterval = 300.
        # loc = plticker.MultipleLocator(base=myInterval)
        # ax.xaxis.set_major_locator(loc)
        # ax.yaxis.set_major_locator(loc)
        #
        # # Add the grid
        # ax.grid(which='major', axis='both', linestyle='-', color='g')
        # #
        # # # Add the image
        # # ax.imshow(image)

        a_as_16bit = cv2.circle(a_as_16bit, stream.static_center_a, 10, (0, eight_bit_max, 0), 2)
        b_as_16bit = cv2.circle(b_as_16bit, stream.static_center_b, 10, (0, eight_bit_max, 0), 2)
        cv2.imshow("A", a_as_16bit)
        cv2.imshow("B Prime", b_as_16bit)
        continue_stream = stream.keep_streaming()

    #print("End of step 4")
    #print("stream.static_center_a", stream.static_center_a)
    #print("stream.static_center_b", stream.static_center_b)
    cv2.destroyAllWindows()

    stream.save_config()

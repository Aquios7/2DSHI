import numpy as np
import os
import matplotlib.pyplot as plt
from image_processing import bit_depth_conversion as bdc
from PIL import Image, ImageDraw, ImageFont
from . import histograms as hgs
from path_management import image_management as im
import cv2
import csv
from experiment_set_up import user_input_validation as uiv
from . import App as tk_app
from constants import STEP_DESCRIPTIONS as sd
from gui import popups

# superfluous?
# y_n_msg = "Proceed? (y/n): "
sixteen_bit_max = (2 ** 16) - 1
twelve_bit_max = (2 ** 12) - 1
eight_bit_max = (2 ** 8) - 1
n_ = 0
prev_R_MATRIX = None


def step_seven(stream, run_folder, figs, histograms, lines, histograms_alg, lines_alg, figs_alg,
               histograms_r, lines_r, figs_r):
    global n_
    # saving paths to frames folders
    a_frames_dir = os.path.join(run_folder, "cam_a_frames")
    b_frames_dir = os.path.join(run_folder, "cam_b_frames")
    # reset frame count
    stream.frame_count = 0

    # app.disable_sigma_slider()
    X_TO_Y_RATIO = stream.static_sigmas_x/stream.static_sigmas_y

    R_VIS_HEIGHT = 500
    R_VIS_WIDTH = int(R_VIS_HEIGHT*X_TO_Y_RATIO*3)

    DASHBOARD_HEIGHT = 600
    DASHBOARD_WIDTH = int(DASHBOARD_HEIGHT*X_TO_Y_RATIO*2)

    last_frame = False

    desc = sd.S07_DESC.value

    if stream.test:
        # record_r_matrices = False
        record_r_matrices = popups.yes_no_popup(desc)
        # test saving
        if stream.test and record_r_matrices:
            # a_frames_new = os.path.join(a_frames_dir, "testSave.txt")
            # with open(a_frames_new, "w") as f:  # open the file in write mode
            #     f.write("Hello world!")  # write the string "Hello world!" to the file
            a_path = os.path.join(a_frames_dir, 'test_frame_a_{}.png'.format(n_))
            b_path = os.path.join(b_frames_dir, 'test_frame_b_{}.png'.format(n_))
            a16 = cv2.imread(stream.current_frame_a)
            b16 = cv2.imread(stream.current_frame_b)
            cv2.imwrite(a_path, a16)
            cv2.imwrite(b_path, b16)
            return

    else:
        # record_r_matrices = uiv.yes_no_quit(desc)
        record_r_matrices = popups.yes_no_popup(desc)
    s8_frame_count = 1
    r_subsection_pixel_vals = None
    satisfied_with_run = False

    while satisfied_with_run is False:

        current_r_frame = 0
        stream.stats = list()
        stream.r_frames = list()
        stream.a_frames = list()
        stream.b_prime_frames = list()

        stream.a_images = list()
        stream.b_prime_images = list()

        stream.s8_full_a_frames = list()
        stream.s8_full_a_frames = list()


        stream.stats.append(["Frame", "Avg_R", "Sigma_R"])

        if record_r_matrices is True:
            continue_stream = True
            while continue_stream:
                r_subsection_pixel_vals = np.array(list())

                stream.frame_count += 1
                stream.current_frame_a, stream.current_frame_b = stream.grab_frames(warp_matrix=stream.warp_matrix, s8=True)

                current_r_frame += 1
                print("Current R Frame: {}".format(current_r_frame))

                x_a, y_a = stream.static_center_a
                x_b, y_b = stream.static_center_b

                # We initially set the LIMITS of the stream to 3 sigma
                # This is done so that if Stream Breaks when trying to show 3 sigma, we know something might be wrong?
                n_sigma = 1
                h_offset = 0
                v_offset = 0
                stream.h_offset = h_offset
                stream.v_offset = v_offset
                stream.n_sigma = n_sigma

                stream.roi_a = stream.current_frame_a[
                               y_a - int(stream.n_sigma * stream.static_sigmas_y) + stream.v_offset:
                               y_a + int(stream.n_sigma * stream.static_sigmas_y + 1) + stream.v_offset,
                               x_a - int(stream.n_sigma * stream.static_sigmas_x) + stream.h_offset:
                               x_a + int(stream.n_sigma * stream.static_sigmas_x + 1) + stream.h_offset
                               ]

                stream.roi_b = stream.current_frame_b[
                               y_b - int(stream.n_sigma * stream.static_sigmas_y) + stream.v_offset:
                               y_b + int(stream.n_sigma * stream.static_sigmas_y + 1) + stream.v_offset:,
                               x_b - int(stream.n_sigma * stream.static_sigmas_x) + stream.h_offset:
                               x_b + int(stream.n_sigma * stream.static_sigmas_x + 1) + stream.h_offset
                               ]

                h = stream.roi_b.shape[0]
                w = stream.roi_b.shape[1]

                hgs.update_histogram(histograms, lines, "a", 4096, stream.roi_a)
                hgs.update_histogram(histograms, lines, "b", 4096, stream.roi_b)
                figs["a"].canvas.draw()  # Draw updates subplots in interactive mode
                figs["b"].canvas.draw()  # Draw updates subplots in interactive mode
                hist_img_a = np.fromstring(figs["a"].canvas.tostring_rgb(), dtype=np.uint8, sep='')
                hist_img_b = np.fromstring(figs["b"].canvas.tostring_rgb(), dtype=np.uint8, sep='')  # convert  to image
                hist_img_a = hist_img_a.reshape(figs["a"].canvas.get_width_height()[::-1] + (3,))
                hist_img_b = hist_img_b.reshape(figs["b"].canvas.get_width_height()[::-1] + (3,))
                hist_img_a = cv2.resize(hist_img_a, (w, h), interpolation=cv2.INTER_AREA)
                hist_img_b = cv2.resize(hist_img_b, (w, h), interpolation=cv2.INTER_AREA)
                hist_img_a = bdc.to_16_bit(cv2.resize(hist_img_a, (w, h), interpolation=cv2.INTER_AREA), 8)
                hist_img_b = bdc.to_16_bit(cv2.resize(hist_img_b, (w, h), interpolation=cv2.INTER_AREA), 8)

                if stream.test:
                    ROI_A_WITH_HISTOGRAM = np.concatenate((hist_img_a, stream.roi_a * 16), axis=1)
                    ROI_B_WITH_HISTOGRAM = np.concatenate((hist_img_b, stream.roi_b * 16), axis=1)
                else:
                    ROI_A_WITH_HISTOGRAM = np.concatenate(
                        (cv2.cvtColor(hist_img_a, cv2.COLOR_RGB2BGR), cv2.cvtColor(stream.roi_a * 16, cv2.COLOR_GRAY2BGR)),
                        axis=1)
                    ROI_B_WITH_HISTOGRAM = np.concatenate(
                        (cv2.cvtColor(hist_img_b, cv2.COLOR_RGB2BGR), cv2.cvtColor(stream.roi_b * 16, cv2.COLOR_GRAY2BGR)),
                        axis=1)

                A_ON_B = np.concatenate((ROI_A_WITH_HISTOGRAM, ROI_B_WITH_HISTOGRAM), axis=0)

                plus_ = cv2.add(stream.roi_a, stream.roi_b)
                minus_ = np.zeros(stream.roi_a.shape, dtype='int16')
                minus_ = np.add(minus_, stream.roi_a)
                minus_ = np.add(minus_, stream.roi_b * (-1))

                hgs.update_histogram(histograms_alg, lines_alg, "plus", 4096, plus_, plus=True)
                hgs.update_histogram(histograms_alg, lines_alg, "minus", 4096, minus_, minus=True)

                displayable_plus = cv2.add(stream.roi_a, stream.roi_b) * 16
                displayable_minus = cv2.subtract(stream.roi_a, stream.roi_b) * 16

                figs_alg["plus"].canvas.draw()  # Draw updates subplots in interactive mode
                hist_img_plus = np.fromstring(figs_alg["plus"].canvas.tostring_rgb(), dtype=np.uint8, sep='')
                hist_img_plus = hist_img_plus.reshape(figs_alg["plus"].canvas.get_width_height()[::-1] + (3,))
                hist_img_plus = cv2.resize(hist_img_plus, (w, h), interpolation=cv2.INTER_AREA)
                hist_img_plus = bdc.to_16_bit(cv2.resize(hist_img_plus, (w, h), interpolation=cv2.INTER_AREA), 8)
                if stream.test:
                    PLUS_WITH_HISTOGRAM = np.concatenate((hist_img_plus, displayable_plus), axis=1)
                else:
                    PLUS_WITH_HISTOGRAM = np.concatenate((cv2.cvtColor(hist_img_plus, cv2.COLOR_RGB2BGR),
                                                          cv2.cvtColor(displayable_plus, cv2.COLOR_GRAY2BGR)), axis=1)

                figs_alg["minus"].canvas.draw()  # Draw updates subplots in interactive mode
                hist_img_minus = np.fromstring(figs_alg["minus"].canvas.tostring_rgb(), dtype=np.uint8,
                                               sep='')  # convert  to image
                hist_img_minus = hist_img_minus.reshape(figs_alg["minus"].canvas.get_width_height()[::-1] + (3,))
                hist_img_minus = cv2.resize(hist_img_minus, (w, h), interpolation=cv2.INTER_AREA)
                hist_img_minus = bdc.to_16_bit(cv2.resize(hist_img_minus, (w, h), interpolation=cv2.INTER_AREA), 8)
                if stream.test:
                    MINUS_WITH_HISTOGRAM = np.concatenate((hist_img_minus, displayable_minus), axis=1)
                else:
                    MINUS_WITH_HISTOGRAM = np.concatenate((cv2.cvtColor(hist_img_minus, cv2.COLOR_RGB2BGR),
                                                           cv2.cvtColor(displayable_minus, cv2.COLOR_GRAY2BGR)), axis=1)

                ALGEBRA = np.concatenate((PLUS_WITH_HISTOGRAM, MINUS_WITH_HISTOGRAM), axis=0)
                DASHBOARD = np.concatenate((A_ON_B, ALGEBRA), axis=1)
                dash_height, dash_width, dash_channels = DASHBOARD.shape

                scale_factor = float(float(2000) / float(dash_width))
                DASHBOARD = cv2.resize(DASHBOARD, (DASHBOARD_WIDTH, DASHBOARD_HEIGHT))
                cv2.imshow("Dashboard", DASHBOARD)

                R_MATRIX = np.divide(minus_, plus_)
                stream.r_frames.append(R_MATRIX)

                h_R_MATRIX = R_MATRIX.shape[0]
                w_R_MATRIX = R_MATRIX.shape[1]
                R_MATRIX_CENTER = int(w_R_MATRIX / 2), int(h_R_MATRIX / 2)

                DISPLAYABLE_R_MATRIX = np.zeros((R_MATRIX.shape[0], R_MATRIX.shape[1], 3), dtype=np.uint8)
                DISPLAYABLE_R_MATRIX[:, :, 1] = np.where(R_MATRIX < 0.00, abs(R_MATRIX * (2 ** 8 - 1)), 0)
                DISPLAYABLE_R_MATRIX[:, :, 2] = np.where(R_MATRIX < 0.00, abs(R_MATRIX * (2 ** 8 - 1)), 0)

                DISPLAYABLE_R_MATRIX[:, :, 2] = np.where(R_MATRIX > 0.00, abs(R_MATRIX * (2 ** 8 - 1)),
                                                         DISPLAYABLE_R_MATRIX[:, :, 2])

                sub_sigma = 0.20
                sigma_x_div = int(stream.static_sigmas_x * sub_sigma)
                sigma_y_div = int(stream.static_sigmas_y * sub_sigma)
                angle = 0
                startAngle = 0
                endAngle = 360
                axesLength = (sigma_x_div, sigma_y_div)
                # Red color in BGR
                color = (255, 255, 255)
                # Line thickness of 5 px
                thickness = -1
                image = cv2.ellipse(DISPLAYABLE_R_MATRIX.copy(), R_MATRIX_CENTER, axesLength,
                                    angle, startAngle, endAngle, color, 1)

                blk_image = np.zeros([h_R_MATRIX, w_R_MATRIX, 3])
                blk_image2 = cv2.ellipse(blk_image.copy(), R_MATRIX_CENTER, axesLength,
                                         angle, startAngle, endAngle, color, thickness)

                combined = blk_image2[:, :, 0] + blk_image2[:, :, 1] + blk_image2[:, :, 2]
                rows, cols = np.where(combined > 0)

                for i, j in zip(rows, cols):
                    r_subsection_pixel_vals = np.append(r_subsection_pixel_vals, R_MATRIX[i, j])

                nan_mean = np.nanmean(r_subsection_pixel_vals)
                nan_st_dev = np.nanstd(r_subsection_pixel_vals)

                stream.stats.append([len(stream.r_frames), nan_mean, nan_st_dev])

                DISPLAYABLE_R_MATRIX = np.zeros((R_MATRIX.shape[0], R_MATRIX.shape[1], 3), dtype=np.uint8)
                DISPLAYABLE_R_MATRIX[:, :, 1] = np.where(R_MATRIX < 0.00, abs(R_MATRIX * (2 ** 8 - 1)), 0)
                DISPLAYABLE_R_MATRIX[:, :, 2] = np.where(R_MATRIX < 0.00, abs(R_MATRIX * (2 ** 8 - 1)), 0)

                DISPLAYABLE_R_MATRIX[:, :, 2] = np.where(R_MATRIX > 0.00, abs(R_MATRIX * (2 ** 8 - 1)),
                                                         DISPLAYABLE_R_MATRIX[:, :, 2])

                image = cv2.ellipse(DISPLAYABLE_R_MATRIX.copy(), R_MATRIX_CENTER, axesLength,
                                    angle, startAngle, endAngle, color, 1)

                dr_height, dr_width, dr_channels = DISPLAYABLE_R_MATRIX.shape

                hgs.update_histogram(histograms_r, lines_r, "r", 4096, R_MATRIX, r=True)
                figs_r["r"].canvas.draw()  # Draw updates subplots in interactive mode
                hist_img_r = np.fromstring(figs_r["r"].canvas.tostring_rgb(), dtype=np.uint8,
                                           sep='')  # convert  to image
                hist_img_r = hist_img_r.reshape(figs_r["r"].canvas.get_width_height()[::-1] + (3,))
                hist_img_r = cv2.resize(hist_img_r, (w, h), interpolation=cv2.INTER_AREA)
                hist_img_r = bdc.to_16_bit(cv2.resize(hist_img_r, (w, h), interpolation=cv2.INTER_AREA), 8)

                if stream.test:
                    stream.R_HIST = hist_img_r
                else:
                    stream.R_HIST = (cv2.cvtColor(hist_img_r, cv2.COLOR_RGB2BGR))

                R_VALUES = Image.new('RGB', (dr_width, dr_height), (eight_bit_max, eight_bit_max, eight_bit_max))

                # initialise the drawing context with
                # the image object as background

                draw = ImageDraw.Draw(R_VALUES)
                font = ImageFont.truetype('arial.ttf', size=int(16.5 * stream.n_sigma))
                (x, y) = (50, 50)
                message = "R Matrix Values\n"
                message = message + "Average: {0:.4f}".format(nan_mean) + "\n"
                message = message + "Sigma: {0:.4f}".format(nan_st_dev)

                px_to_mm = 5.86 * (10 ** (-3))
                message = message + "Shape (px): {0}, {1}".format(h_R_MATRIX, w_R_MATRIX) + "\n"
                message = message + "Shape (mm):  {0:.2f},  {1:.2f}".format(h_R_MATRIX * px_to_mm,
                                                                            w_R_MATRIX * px_to_mm) + "\n"

                # Mean: {0:.4f}\n".format(nan_mean, 2.000*float(stream.frame_count))
                color = 'rgb(0, 0, 0)'  # black color
                draw.text((x, y), message, fill=color, font=font)
                R_VALUES = np.array(R_VALUES)

                VALUES_W_HIST = np.concatenate((R_VALUES * (2 ** 8), np.array(stream.R_HIST)), axis=1)
                R_MATRIX_DISPLAYABLE_FINAL = image
                # R_MATRIX_DISPLAYABLE_FINAL = np.array(DISPLAYABLE_R_MATRIX * (2 ** 8), dtype='uint16')
                R_MATRIX_DISPLAYABLE_FINAL = np.array(R_MATRIX_DISPLAYABLE_FINAL * (2 ** 8), dtype='uint16')
                cv2.imshow("R_MATRIX", cv2.resize(
                    np.concatenate((VALUES_W_HIST, R_MATRIX_DISPLAYABLE_FINAL), axis=1)
                    , (R_VIS_WIDTH, R_VIS_HEIGHT))
                           )

                if current_r_frame > 1:
                    sub_R_MATRIX = np.subtract(R_MATRIX, prev_R_MATRIX)

                    sub_h_R_MATRIX = sub_R_MATRIX.shape[0]
                    sub_w_R_MATRIX = sub_R_MATRIX.shape[1]
                    sub_R_MATRIX_CENTER = int(sub_w_R_MATRIX / 2), int(sub_h_R_MATRIX / 2)

                    sub_DISPLAYABLE_R_MATRIX = np.zeros((sub_R_MATRIX.shape[0], sub_R_MATRIX.shape[1], 3),
                                                        dtype=np.uint8)
                    sub_DISPLAYABLE_R_MATRIX[:, :, 1] = np.where(sub_R_MATRIX < 0.00, abs(sub_R_MATRIX * (2 ** 8 - 1)),
                                                                 0)
                    sub_DISPLAYABLE_R_MATRIX[:, :, 2] = np.where(sub_R_MATRIX < 0.00, abs(sub_R_MATRIX * (2 ** 8 - 1)),
                                                                 0)

                    sub_DISPLAYABLE_R_MATRIX[:, :, 2] = np.where(sub_R_MATRIX > 0.00, abs(sub_R_MATRIX * (2 ** 8 - 1)),
                                                                 sub_DISPLAYABLE_R_MATRIX[:, :, 2])

                    nan_mean = np.nanmean(r_subsection_pixel_vals)
                    nan_st_dev = np.nanstd(r_subsection_pixel_vals)

                    dr_height, dr_width, dr_channels = sub_DISPLAYABLE_R_MATRIX.shape

                    hgs.update_histogram(histograms_r, lines_r, "r", 4096, sub_R_MATRIX, r=True)
                    figs_r["r"].canvas.draw()  # Draw updates subplots in interactive mode
                    hist_img_r = np.fromstring(figs_r["r"].canvas.tostring_rgb(), dtype=np.uint8,
                                               sep='')  # convert  to image
                    hist_img_r = hist_img_r.reshape(figs_r["r"].canvas.get_width_height()[::-1] + (3,))
                    hist_img_r = cv2.resize(hist_img_r, (w, h), interpolation=cv2.INTER_AREA)
                    hist_img_r = bdc.to_16_bit(cv2.resize(hist_img_r, (w, h), interpolation=cv2.INTER_AREA), 8)
                    if stream.test:
                        sub_R_HIST = hist_img_r
                    else:
                        sub_R_HIST = (cv2.cvtColor(hist_img_r, cv2.COLOR_RGB2BGR))

                    sub_R_VALUES = Image.new('RGB', (dr_width, dr_height),
                                             (eight_bit_max, eight_bit_max, eight_bit_max))

                    draw = ImageDraw.Draw(sub_R_VALUES)
                    font = ImageFont.truetype('arial.ttf', size=int(20))
                    (x, y) = (50, 50)
                    message = "R Matrix Values\n"
                    message = message + "Average: {0:.4f}".format(nan_mean) + "\n"
                    message = message + "Sigma: {0:.4f}".format(nan_st_dev)

                    px_to_mm = 5.86 * (10 ** (-3))
                    message = message + "Shape (px): {0}, {1}".format(sub_h_R_MATRIX, sub_w_R_MATRIX) + "\n"
                    message = message + "Shape (mm):  {0:.2f},  {1:.2f}".format(sub_h_R_MATRIX * px_to_mm,
                                                                                sub_w_R_MATRIX * px_to_mm) + "\n"

                    color = 'rgb(0, 0, 0)'  # black color
                    draw.text((x, y), message, fill=color, font=font)
                    sub_R_VALUES = np.array(sub_R_VALUES)

                    sub_R_VALUES_resized = cv2.resize(sub_R_VALUES, (w, h), interpolation=cv2.INTER_AREA)

                    # remake image for d r matrix
                    # image = cv2.ellipse(sub_DISPLAYABLE_R_MATRIX.copy(), R_MATRIX_CENTER, axesLength,
                    #                     angle, startAngle, endAngle, color, 1)

                    sub_VALUES_W_HIST = np.concatenate((sub_R_VALUES_resized * (2 ** 8), np.array(sub_R_HIST)), axis=1)
                    sub_R_MATRIX_DISPLAYABLE_FINAL = sub_DISPLAYABLE_R_MATRIX
                    sub_R_MATRIX_DISPLAYABLE_FINAL = np.array(sub_R_MATRIX_DISPLAYABLE_FINAL * (2 ** 8), dtype='uint16')

                    sub_R_MATRIX_DISPLAYABLE_FINAL_resized = cv2.resize(sub_R_MATRIX_DISPLAYABLE_FINAL, (w * 2, h),
                                                                        interpolation=cv2.INTER_AREA)

                    cv2.imshow("sub_R_MATRIX", cv2.resize(
                        np.concatenate((VALUES_W_HIST, sub_R_MATRIX_DISPLAYABLE_FINAL), axis=1)
                        , (R_VIS_WIDTH, R_VIS_HEIGHT))
                               )

                prev_R_MATRIX = R_MATRIX

                continue_stream = stream.keep_streaming()
                s8_frame_count += 1
                if continue_stream is False:
                    satisfied_with_range = False
                    while satisfied_with_range is False:
                        cv2.destroyAllWindows()
                        fig_ = plt.figure()
                        ax1 = fig_.add_subplot(111)
                        frames = list()
                        averages = list()
                        sigmas = list()

                        starting_frame = 1
                        end_frame = stream.frame_count

                        if (not starting_frame >= 1) or (not starting_frame <= current_r_frame):
                            print("Start frame must be between {0} and {1}".format(1, current_r_frame))
                            val_start = False
                        else:
                            val_start = True

                        if (not end_frame >= starting_frame) or (not end_frame >= 1) \
                                or not (end_frame <= current_r_frame):
                            print("End frame must be between {0} and {1}".format(starting_frame, current_r_frame))
                            val_end = False
                        else:
                            val_end = True

                        while val_start is False or val_end is False:
                            starting_frame = int(input("Start at frame: "))
                            end_frame = int(input("End at frame: "))

                            if (not starting_frame >= 1) or (not starting_frame <= current_r_frame):
                                print("Start frame must be between {0} and {1}".format(1, current_r_frame))
                                val_start = False
                            else:
                                val_start = True

                            if (not end_frame >= starting_frame) or (not end_frame >= 1) \
                                    or not (end_frame <= current_r_frame):
                                print("End frame must be between {0} and {1}".format(max(starting_frame, 1), current_r_frame))
                                val_end = False
                            else:
                                val_end = True


                        # for i in range(1, len(stats)):
                        for i in range(starting_frame, end_frame + 1):
                            frames.append(stream.stats[i][0])
                            averages.append(stream.stats[i][1])
                            sigmas.append(stream.stats[i][2])


                        ax1.errorbar(frames, averages, yerr=sigmas, c='b', capsize=5)
                        ax1.set_xlabel('Frame')
                        ax1.set_ylabel('R (Mean)')
                        ax1.set_title('Mean R by Frame')
                        ax1.axhline(y=-1.0, xmin=starting_frame, xmax=end_frame)
                        ax1.axhline(y=0.0, xmin=starting_frame, xmax=end_frame)
                        ax1.axhline(y=1.0, xmin=starting_frame, xmax=end_frame)

                        save_path = os.path.join(run_folder, 'mean_r_by_frame.png')
                        fig_.savefig(save_path)
                        plot_img = cv2.imread(save_path, cv2.IMREAD_COLOR)
                        cv2.imshow('R Mean Plot', plot_img)
                        cv2.waitKey(30000)
                        cv2.destroyAllWindows()
                        range_satisfaction_input = True
                        if range_satisfaction_input is True:
                            satisfied_with_range = True
                            stream.start_writing_at = starting_frame
                            stream.end_writing_at = end_frame
                    satisfied_with_run = True

                # save r matrix
                n_ += 1
                r_matrix = R_MATRIX
                csv_path = os.path.join(run_folder, "r_matrix_{}.csv".format(n_))
                with open(csv_path, "w+", newline='') as my_csv:
                    csvWriter = csv.writer(my_csv, delimiter=',')
                    csvWriter.writerows(r_matrix.tolist())

                # save a matrix
                a_matrix = stream.current_frame_a
                csv_path = os.path.join(run_folder, "a_matrix_{}.csv".format(n_))
                with open(csv_path, "w+", newline='') as my_csv:
                    csvWriter = csv.writer(my_csv, delimiter=',')
                    csvWriter.writerows(a_matrix.tolist())
                # savee a frames
                a16 = bdc.to_16_bit(a_matrix)
                im.save_img("a_{}.png".format(n_), a_frames_dir, a16)

                # save b matrix
                b_matrix = stream.current_frame_b
                csv_path = os.path.join(run_folder, "b_matrix_{}.csv".format(n_))
                with open(csv_path, "w+", newline='') as my_csv:
                    csvWriter = csv.writer(my_csv, delimiter=',')
                    csvWriter.writerows(b_matrix.tolist())
                # save b frames
                b16 = bdc.to_16_bit(b_matrix)
                im.save_img("b_{}.png".format(n_), b_frames_dir, b16)

                print("\tMatrices and Matrix Stats have finished writing to file. b_{}".format(n_))


        if record_r_matrices is False:
            satisfied_with_run = True
            continue_stream = False

        else:
            continue_stream = stream.keep_streaming(one_by_one=True)

        if not continue_stream:
            if last_frame:
                pass
            else:
                pass

                cv2.destroyAllWindows()

        s8_frame_count += 1

    cv2.destroyAllWindows()
    stream.save_config()

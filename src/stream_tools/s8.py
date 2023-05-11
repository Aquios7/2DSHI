import os
import csv as csv
from path_management import image_management as im
from image_processing import bit_depth_conversion as bdc
from experiment_set_up import user_input_validation as uiv
from constants import STEP_DESCRIPTIONS as sd


def step_eight(stream, start_writing_at, end_writing_at, run_folder, a_images, a_frames, b_prime_images, b_prime_frames,
              stats):

    if stream.test:
        write_to_csv = False
    else:
        desc = sd.S08_DESC.value
        write_to_csv = uiv.yes_no_quit(desc)

    if write_to_csv is True:
    #     r_matrices = stream.r_frames
    #     n_ = 0
    #     print("\tWriting R Matrices")
    #     for i in range(start_writing_at, end_writing_at + 1):
    #         n_ += 1
    #         r_matrix = r_matrices[i - 1]
    #         csv_path = os.path.join(run_folder, "r_matrix_{}.csv".format(n_))
    #         with open(csv_path, "w+", newline='') as my_csv:
    #             csvWriter = csv.writer(my_csv, delimiter=',')
    #             csvWriter.writerows(r_matrix.tolist())
    #
    #     n_ = 0
    #     a_frames_dir = os.path.join(run_folder, "cam_a_frames")
    #     print("\tWriting A Matrices/Images")
    #     for i in range(start_writing_at, end_writing_at + 1):
    #         # for a_matrix in a_frames:
    #         n_ += 1
    #         a_matrix = a_frames[i - 1]
    #         csv_path = os.path.join(run_folder, "a_matrix_{}.csv".format(n_))
    #         with open(csv_path, "w+", newline='') as my_csv:
    #             csvWriter = csv.writer(my_csv, delimiter=',')
    #             csvWriter.writerows(a_matrix.tolist())
    #
    #         a16 = bdc.to_16_bit(a_matrix)
    #         im.save_img("a_{}.png".format(n_), a_frames_dir, a16)
    #
    #
    #     b_frames_dir = os.path.join(run_folder, "cam_b_frames")
    #
    #     n_ = 0
    #     print("\tWriting B Matrices/Images")
    #     for i in range(start_writing_at, end_writing_at + 1):
    #         # for b_matrix in b_prime_frames:
    #         n_ += 1
    #         b_matrix = b_prime_frames[i - 1]
    #         csv_path = os.path.join(run_folder, "b_matrix_{}.csv".format(n_))
    #         with open(csv_path, "w+", newline='') as my_csv:
    #             csvWriter = csv.writer(my_csv, delimiter=',')
    #             csvWriter.writerows(b_matrix.tolist())
    #
    #         b16 = bdc.to_16_bit(b_matrix)
    #         im.save_img("b_{}.png".format(n_), b_frames_dir, b16)

        print("\tWriting R Matrix Stats to file:")
        stats_csv_path = os.path.join(run_folder, "r_matrices_stats.csv")
        with open(stats_csv_path, "w+", newline='') as stats_csv:
            stats_csvWriter = csv.writer(stats_csv, delimiter=',')
            stats_csvWriter.writerow(stats[0])
            count = 0
        print("\tMatrices and Matrix Stats have finished writing to file.")

    else:
        print("run ended with no data saved.")

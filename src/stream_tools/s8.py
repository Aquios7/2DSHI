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
        # desc = sd.S08_DESC.value
        # write_to_csv = uiv.yes_no_quit(desc)
        write_to_csv = True

    if write_to_csv is True:

        print("\tWriting R Matrix Stats to file:")
        stats_csv_path = os.path.join(run_folder, "r_matrices_stats.csv")
        with open(stats_csv_path, "w+", newline='') as stats_csv:
            stats_csvWriter = csv.writer(stats_csv, delimiter=',')
            stats_csvWriter.writerow(stats[0])
            count = 0
        print("\tMatrices and Matrix Stats have finished writing to file.")

    else:
        print("run ended with no data saved.")

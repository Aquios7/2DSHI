"""Driver class - you should be able to run main from the command line along with the some command line arguments of
  your choice, and this script will call all other modules/scripts and feed those args/params as needed."""
import sys
import argparse
import os

from experiment_set_up import update_camera_configuration as ucc
from experiment_set_up import write_experimental_params_to_file as wptf
from experiment_set_up import get_command_line_parameters
from experiment_set_up import find_previous_run
from experiment_set_up import config_file_setup as cam_setup
from experiment_set_up import user_input_validation as uiv

from stream_tools import stream_tools
#from stream_tools import  steam_toosls2 as stream_tools
from image_processing import bit_depth_conversion as bdc
from path_management import image_management as im
from datetime import datetime
from gui import startupGUI


# Create an instance of an ArgumentParser Object
parser = argparse.ArgumentParser()


if __name__ == "__main__":
    args = None
    # run_mode = uiv.determine_run_mode(sys.argv[:])
    current_directory = os.getcwd()

    # run a pre-start GUI asking for specifics before the main run
    current_directory = startupGUI.begin_startup(current_directory)


    # if run_mode == 1:  # Apply the parameters for the previous run, exactly.
    #     prev_run = find_previous_run.get_latest_run()
    #     uiv.display_dict_values(prev_run)
    #     args = prev_run
    #
    # if run_mode == 2:  # Apply the parameters specified in the command line, exactly.
    #     parser = get_command_line_parameters.initialize_arg_parser()
    #     args = vars(parser.parse_args())  # Parse user arguments into a dictionary)
    #     uiv.display_dict_values(args)
    #
    # if run_mode == 3:  # Apply last runs parameters, but with some modifications you'll specify.
    #     prev_run = find_previous_run.get_latest_run()
    #     uiv.display_dict_values(prev_run)
    #     args = uiv.update_previous_params(prev_run)

    current_datetime = datetime.now().strftime("%Y_%m_%d__%H_%M")
    current_direc = current_directory
    run_directory = ''
    run_directory = os.path.join(run_directory, current_direc, current_datetime)

    if not os.path.exists(run_directory):
        os.mkdir(run_directory)
        os.mkdir(os.path.join(run_directory, "cam_a_frames"))
        os.mkdir(os.path.join(run_directory, "cam_b_frames"))

    wptf.document_run(args, current_datetime)

    print("\nAll Experimental Data will be saved in the following directory:\n\tD:\\{}\n".format(current_datetime))
    print("\nStarting Run: {}\n".format(current_datetime))

    config_file_parameters = ["ExposureTime", "AcquisitionFrameRate"]
    parameter_dictionary = ucc.reduce_dictionary(args, config_file_parameters)

    camera_configurations_folder = os.path.join(os.getcwd(), "camera_configuration_files")
    # Prepare Camera Configuration Files
    config_files_by_cam = cam_setup.assign_config_files(parameter_dictionary, args, camera_configurations_folder)

    stream = stream_tools.Stream(fb=args["FrameBreak"], save_imgs=args["SaveImages"])  # Create a Stream() Instance
    stream.set_current_run(current_datetime)
    #stream.get_cameras(config_files_by_cam)  # Get Basler Cameras, and load corresponding camera configuration files

    highest_jump_level = find_previous_run.get_highest_jump_level(stream)
    stream.offer_to_jump(highest_jump_level)

    stream.start(config_files_by_cam, histogram=args["DisplayHistocam"])  # Start steam (Display Histogram if user specified so in input)

    print("Stream has ended.")

    if args["SaveImages"]:
        a_frames_dir = os.path.join(run_directory, "cam_a_frames")
        b_frames_dir = os.path.join(run_directory, "cam_b_frames")

        print("Saving 12 bit frames as 16 bit png files.")
        a_frames = stream.get_12bit_a_frames()
        b_frames = stream.get_12bit_b_frames()

        for i in range(len(a_frames)):
            a16 = bdc.to_16_bit(a_frames[i])
            im.save_img("a_{}.png".format(i + 1), a_frames_dir, a16)

        for j in range(len(b_frames)):
            b16 = bdc.to_16_bit(b_frames[j])
            im.save_img("b_{}.png".format(j + 1), b_frames_dir, b16)

    os.chdir(run_directory)
    if stream.get_warp_matrix() is not None and stream.get_warp_matrix2() is not None:
        try:
            print("Writing Stream Configurations to File")
            wptf.document_configurations(
                warp_matrix=stream.get_warp_matrix(),
                sigmas=stream.get_static_sigmas(),
                static_centers=stream.get_static_centers(),
                warp_matrix_2=stream.get_warp_matrix2())
        except TypeError as e:
            print("TYPE ERROR")
            raise e
    os.chdir(current_directory)
    sys.exit()


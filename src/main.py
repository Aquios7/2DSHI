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

# allow for '-v' and '--verbose'
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Verbose output')

# activate the arguments passed
args = parser.parse_args()

# hyperlink used in the verbose description
hyperlink_format = '<a href="{link}">{text}</a>'
link_text = hyperlink_format.format

# begin the program from here
if __name__ == "__main__":
    # verbose Description
    if args.verbose:
        print("This is a program used in conjunction with the 2D Second Harmonic Dispersion Interferometer\n"
              "Each step will have a description of the process as the program goes through the 7 steps of "
              "calculation\n"
              "For any questions on the program, please contact https://www.l-egantsolutions.com/contact-indigo")

    # args = None
    # run_mode = uiv.determine_run_mode(sys.argv[:])
    current_directory = os.getcwd()

    # run a pre-start GUI asking for specifics before the main run
    current_directory, test, reason = startupGUI.begin_startup(current_directory)
    print(reason)

    # check for current directory
    if test:
        current_datetime = 'test-' + datetime.now().strftime("%Y_%m_%d/")
        current_time = datetime.now().strftime("%H_%M")
    else:
        current_datetime = datetime.now().strftime("%Y_%m_%d/")
        current_time = datetime.now().strftime("%H_%M")
    current_direc = current_directory
    run_directory = ''
    run_directory2 = ''
    run_directory = os.path.join(run_directory, current_direc, current_datetime)
    run_directory2 = os.path.join(run_directory2, run_directory, current_time)

    # create a directory for the current run
    if not os.path.exists(run_directory):
        os.mkdir(run_directory)
    if not os.path.exists(run_directory2):
        os.mkdir(run_directory2)
        os.mkdir(os.path.join(run_directory2, "cam_a_frames"))
        os.mkdir(os.path.join(run_directory2, "cam_b_frames"))
        os.mkdir(os.path.join(run_directory2, "config"))

    # updates for the terminal
    print("\nAll Experimental Data will be saved in the following directory:\n\tD:\\{}\n".format(current_datetime))
    print("\nStarting Run: {}\n".format(current_datetime))

    # configuration parameters created
    config_file_parameters = ["ExposureTime", "AcquisitionFrameRate"]

    # camera config folder path created
    camera_configurations_folder = os.path.join(os.getcwd(), "camera_configuration_files")

    # overall config folder parameter created
    config_folder = os.path.join(run_directory2, "config/")

    # Prepare Camera Configuration Files
    config_files_by_cam = cam_setup.assign_config_files(camera_configurations_folder)

    # Create a Stream() Instance
    stream = stream_tools.Stream()
    stream.set_current_run(current_datetime)

    # find the last point that a previous run ended at
    highest_jump_level = find_previous_run.get_highest_jump_level(stream)
    stream.offer_to_jump(highest_jump_level)

    # Start steam (Display Histogram if user specified so in input)
    stream.start(config_files_by_cam, config_folder, test, reason, args, run_directory2)

    # terminal message for end of stream
    print("Stream has ended.")

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


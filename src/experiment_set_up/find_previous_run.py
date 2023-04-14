import os

def get_latest_run_direc(path_override=False, path_to_exclude=None):
    if not path_override:
        data_directory = os.getcwd()  # Windows PC @ Franks' House

    else:
        # data_directory = os.path.abspath(os.path.join(os.path.join("D:"), os.pardir))
        data_directory = os.getcwd()

    # print(os.listdir(data_directory))
    all_runs = sorted([os.path.join(data_directory, path) for path in os.listdir(data_directory)
                       if os.path.isdir(os.path.join(data_directory, path))

                       and path not in ["$RECYCLE.BIN",
                                        "System Volume Information",
                                        "BaslerCameraData",
                                        ".tmp.drivedownload",
                                        "Recovery"
                                        "WindowsImageBackup",
                                        "venv",
                                        "toolsformatt"]

                      and path not in ['.DS_Store',
                                       'analysis_tools',
                                       'camera_configuration_files',
                                       'Cameron',
                                       'constants',
                                       'coregistration',
                                       'exceptions',
                                       'experiment_set_up',
                                       'gui',
                                       'histocam',
                                       'image_processing',
                                       'last.exe.stackdump',
                                       'Mattt',
                                       'path_management',
                                       'profiling',
                                       'stream_tools',
                                       'test',
                                       'toolsformatt',
                                       'venv']
                      ]
                      )

    if path_to_exclude is not None:
        filtered = [x for x in all_runs if path_to_exclude not in x]
        all_runs = filtered

    return all_runs[-1]


def get_latest_run():
    data_directory = os.getcwd()
    # data_directory = os.path.join("C:", "")  # Windows Laptop

    all_runs = sorted([os.path.join(data_directory, path) for path in os.listdir(data_directory)
                       if os.path.isdir(os.path.join(data_directory, path))
                       and path not in ["$RECYCLE.BIN",
                                        "System Volume Information",
                                        "BaslerCameraData",
                                        ".tmp.drivedownload",
                                        "Recovery"
                                        "WindowsImageBackup"]])
    # print(all_runs)
    all_params_dict = dict()

    if len(all_runs) < 1:
        return all_params_dict

    last_run = get_latest_run_direc()

    last_run_params_file_path = os.path.join(last_run, "run_parameters.txt")
    print("Attempting to retrieve: ", last_run_params_file_path)
    last_run_params_file = open(last_run_params_file_path, 'r')

    string_parameters = ["video_a",
                         "video_b",
                         "camera_configuration_file",
                         "camera_configuration_file_a"
                         "camera_configuration_file_b",
                         "Target"]

    int_parameters = ["SaveImages",
                      "SaveVideos",
                      "FrameBreak",
                      "DisplayHistocam",
                      "SaveHistocam",
                      "Raw",
                      "Grid",
                      "ExposureTime",
                      "AcquisitionFrameRate"]

    float_parameters = ["ResizeFactor",
                        "CrystalTemp1",
                        "CrystalTemp2",
                        "CompensatorAngle"]

    for line in last_run_params_file:
        split_by_tabs = line.split('\t')
        parameter = split_by_tabs[0]
        value = split_by_tabs[1].rstrip()
        if value.endswith("None"):
            all_params_dict[parameter] = None
        elif parameter in int_parameters:
            all_params_dict[parameter] = int(float(value))
        elif parameter in float_parameters:
            all_params_dict[parameter] = float(value)
        elif parameter in string_parameters:
            all_params_dict[parameter] = value
        elif parameter.endswith("RunPreviousParameters"):
            pass
        else:
            print("Warning: Parameter {} with a value of {} has NOT been accounted for.".format(parameter, value))

    last_run_params_file.close()
    return all_params_dict


def get_highest_jump_level(stream):
    highest_jump_level = 2

    previous_run_directory = get_latest_run_direc(path_override=True, path_to_exclude=stream.current_run)
    prev_wp1_path = os.path.join(previous_run_directory, "wm1.npy")
    prev_wp1_exist = os.path.exists(prev_wp1_path)

    if prev_wp1_exist:
        highest_jump_level = 3

    """
    prev_bpa_path = os.path.join(previous_run_directory, "max_pixel_a.p")
    prev_bpa_exist = os.path.exists(prev_bpa_path)

    prev_bpb_path = os.path.join(previous_run_directory, "max_pixel_b.p")
    prev_bpb_exist = os.path.exists(prev_bpb_path)

    if highest_jump_level == 3 and (prev_bpa_exist and prev_bpb_exist):
        highest_jump_level = 4
    else:
        return highest_jump_level
    """

    prev_sca_path = os.path.join(previous_run_directory, "static_center_a.p")
    prev_sca_exist = os.path.exists(prev_sca_path)

    prev_scb_path = os.path.join(previous_run_directory, "static_center_b.p")
    prev_scb_exist = os.path.exists(prev_scb_path)

    if highest_jump_level == 3 and (prev_sca_exist and prev_scb_exist):
        highest_jump_level = 4
    else:
        return highest_jump_level

    prev_sigma_x_path = os.path.join(previous_run_directory, "static_sigma_x.p")
    prev_sigma_x_exist = os.path.exists(prev_sigma_x_path)

    prev_sigma_y_path = os.path.join(previous_run_directory, "static_sigma_y.p")
    prev_sigma_y_exist = os.path.exists(prev_sigma_y_path)

    if highest_jump_level == 4 and (prev_sigma_x_exist and prev_sigma_y_exist):
        highest_jump_level = 5

    prev_wp2_path = os.path.join(previous_run_directory, "wm2.npy")
    prev_wp2_exist = os.path.exists(prev_wp2_path)

    if highest_jump_level == 5 and (prev_wp2_exist or prev_wp1_exist):
        highest_jump_level = 6

    return highest_jump_level


def get_previous_configuration():
    print("Inside Function: get_previous_configuration()")
    data_directory = os.path.join("D:", "")  # Windows PC @ Franks' House

    all_runs = sorted([os.path.join(data_directory, path) for path in os.listdir(data_directory)
                       if os.path.isdir(os.path.join(data_directory, path))
                       and path not in ["$RECYCLE.BIN", "System Volume Information"]])

    all_params_dict = dict()

    if len(all_runs) < 1:
        return all_params_dict

    last_run = all_runs[-1]
    last_run_params_file_path = os.path.join(last_run, "stream_configuration.txt")

    if not os.path.exists(last_run_params_file_path):
        return None

    last_run_params_file = open(last_run_params_file_path, 'r')

    int_parameters = ["static_center_a_x",
                      "static_center_a_y",
                      "static_center_b_x",
                      "static_center_b_y",
                      "sigma_x",
                      "sigma_y"]

    float_parameters = ["a",
                        "b",
                        "tx",
                        "c",
                        "d",
                        "ty"]

    float_parameters += ["a2",
                        "b2",
                        "tx2",
                        "c2",
                        "d2",
                        "ty2"]

    for line in last_run_params_file:
        split_by_tabs = line.split('\t')
        parameter = split_by_tabs[0].strip()
        value = split_by_tabs[1].strip()
        if value.endswith("None"):
            all_params_dict[parameter] = None
        elif parameter in int_parameters:
            all_params_dict[parameter] = int(float(value))
        elif parameter in float_parameters:
            all_params_dict[parameter] = float(value)
        else:
            print("Warning: Parameter {} with a value of {} has NOT been accounted for.".format(parameter, value))

    last_run_params_file.close()
    return all_params_dict
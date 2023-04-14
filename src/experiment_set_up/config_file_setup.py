import os

# Fix ability to update config file later
def assign_config_files(camera_configurations_folder):
    camera_a_configuration = os.path.join(camera_configurations_folder, "cam_a_default.pfs")
    camera_b_configuration = os.path.join(camera_configurations_folder, "cam_b_default.pfs")

    config_files_by_cam = {"a": camera_a_configuration, "b": camera_b_configuration}

    return config_files_by_cam


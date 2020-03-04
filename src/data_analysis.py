from tkinter.filedialog import askopenfilename, askdirectory
import matplotlib.pyplot as plt
import os
import PIL
import sys
import pandas
from path_management import image_management as im
import numpy as np
import csv
from matplotlib import cm
from collections import OrderedDict
from PIL import Image
from image_processing import bit_depth_conversion as bdc
import warnings

import os.path
from os import path

shape_choices = dict()
shape_choices[1] = "Circle"
shape_choices[2] = "Spiral"
shape_choices[3] = "Lines"

circle_options = dict()
circle_options["x_offset"] = 0
circle_options["y_offset"] = 0
circle_options["radii"] = []

old_err_state = np.seterr(divide='raise')
ignored_states = np.seterr(**old_err_state)
warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')

start_dir = os.getcwd()
plot_paths = list()

def does_setup_file_exist(directory_to_check):
    assumed_path = os.path.join(directory_to_check, "data_analysis_parameters.txt")
    return path.exists(assumed_path)

def get_analysis_parameters(csv_files_parent_directory):
    params_as_a_string = ""
    if does_setup_file_exist(csv_files_parent_directory) is True:
        last_run_params_file = open(os.path.join(csv_files_parent_directory, "data_analysis_parameters.txt"), 'r')
        print("Reading in previous parameters:\n")
        for line in last_run_params_file:
            split_by_tabs = line.split('\t')
            parameter = split_by_tabs[0].strip()
            if not parameter.startswith("radii"):
                value = split_by_tabs[1].strip()
                print("Parameter: {}\t\tValue: {}".format(parameter, value))

            else:
                value = split_by_tabs[1:]
                value[-1] = value[-1].strip()
                for radius in value:
                    circle_options["radii"].append(int(radius))
                print("Parameter: {}\t\tValue: {}".format(parameter, circle_options["radii"]))

    else:
        # Now we have to prompt the user
        print("Options: ")
        for key in shape_choices:
            print("\t{}: {}".format(key, shape_choices[key]))



        user_choice = int(input("Enter an integer value that corresponds to the shape you wish to implement "))
        if user_choice == 1:
            print("You picked circle.")
            circle_options["x_offset"] = int(input("Pick an x offset: "))
            circle_options["y_offset"] = int(input("Pick an y offset: "))
            str_ = "Pick as many radii as you'd like.\n "
            str_ += "To add a radius, enter the integer then press enter.\n"
            str_ += "When done, just press Enter without any additional input\n"

            print(str_)

            user_input = "_"
            while user_input != "":
                user_input = input("Add a radius: ")
                if len(user_input) > 0:
                    circle_options["radii"].append(int(user_input))


            # shape
            params_as_a_string += "shape"
            params_as_a_string += "\t"
            params_as_a_string += str(user_choice)
            params_as_a_string += "\n"

            # x offset
            params_as_a_string += "x_offset"
            params_as_a_string += "\t"
            params_as_a_string += str(circle_options["x_offset"])
            params_as_a_string += "\n"

            # y offset
            params_as_a_string += "y_offset"
            params_as_a_string += "\t"
            params_as_a_string += str(circle_options["y_offset"])
            params_as_a_string += "\n"

            # radii
            params_as_a_string += "radii"

            for radius in circle_options["radii"]:
                params_as_a_string += "\t"
                params_as_a_string += str(radius)

            params_as_a_string += "\n"

            params_file = open(os.path.join(csv_files_parent_directory, "data_analysis_parameters.txt"), 'w+')
            params_file.write(params_as_a_string)
            params_file.close()


def get_phi_sample():
    print("Welcome to data_analysis.py using phi.csv")
    quit_string = "\nTo quit, type 'q' or 'quit', then press Enter: "
    user_input = input("To proceed and select phi.csv, press Enter." + quit_string)

    if user_input.lower() in ["quit", "q"]:
        sys.exit()
    # show an "Open" dialog box and return the path to the selected file
    filename_R_sample = askopenfilename(title='Pick a phi.csv sample')
    print("R: {}".format(filename_R_sample))
    return filename_R_sample

def get_data_directory(phi_csv_directory):
    run_directory = os.path.abspath(os.path.join(phi_csv_directory, os.pardir))
    print("Run Directory: {}".format(run_directory))

    return run_directory


def read_in_csv(path_to_phi_csv):
    r_sample_csv_file = pandas.read_csv(path_to_phi_csv, header=None)
    values_r_sample = r_sample_csv_file.values
    R_MATRIX = values_r_sample
    return R_MATRIX

def generate_images_from_R_matrix(R_MATRIX, csv_filename, circle_params):


    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', r'All-NaN (slice|axis) encountered')

        # Initiates an empty array of zeroes, that has the same shape as the CSV file
        DISPLAYABLE_R_MATRIX = np.zeros((R_MATRIX.shape[0], R_MATRIX.shape[1], 3), dtype=np.uint8)

        DISPLAYABLE_R_MATRIX[:, :, 0] = np.where(R_MATRIX < 0.00, abs(R_MATRIX * (2 ** 8 - 1)), 0)
        DISPLAYABLE_R_MATRIX[:, :, 1] = np.where(R_MATRIX < 0.00, abs(R_MATRIX * (2 ** 8 - 1)), 0)

        DISPLAYABLE_R_MATRIX[:, :, 0] = np.where(R_MATRIX > 0.00, abs(R_MATRIX * (2 ** 8 - 1)),
                                                 DISPLAYABLE_R_MATRIX[:, :, 0])


    image = Image.fromarray(DISPLAYABLE_R_MATRIX.astype('uint8'), 'RGB')
    image.save(csv_filename.replace(".csv", ".png"))
    spiral = np.asarray(DISPLAYABLE_R_MATRIX[:, :, :])
    height = spiral.shape[0]
    width = spiral.shape[1]
    center_x = int(width / 2)
    center_y = int(height / 2)
    # This are the deltas of the spiral path from the center of the spiral

    #x_offset, y_offset = [int(x) for x in input("Enter x_offset y_offset (no comma): ").split()]
    x_offset = circle_params["x_offset"]
    y_offset = circle_params["y_offset"]

    for radius in circle_params["radii"]:
        print("Doing analysis on R = {}".format(radius))

        #radius = circle_params["radii"][0]

        y = []
        x = []

        marker_y = []
        marker_x = []


        marker_coords_y = []
        marker_coords_x = []

        points = 500
        num_of_pi = 2

        #print(x_offset, y_offset)

        # for the m= 1 VPP with 100 um
        # vertical_offset = 35 #int(input("Please enter vertical offset: ")) * -1
        # horizontal_offset = -40  #int(input("Please enter horizontal offset: "))
        # for the m= 1 VPP with noPH
        # vertical_offset = 15 #int(input("Please enter vertical offset: ")) * -1
        # horizontal_offset = 50  #int(input("Please enter horizontal offset: "))
        # for the m=2 VPP with noPH
        if y_offset :
            vertical_offset = y_offset
        else:
            vertical_offset = 5 #int(input("Please enter vertical offset: ")) * -1

        if x_offset:
            horizontal_offset = x_offset
        else:
            horizontal_offset = 15  #int(input("Please enter horizontal offset: "))


        count = 0
        for theta in np.linspace(0, num_of_pi*np.pi, num=points):
            count += 1
            r = int(radius)
            # r = -1*((0.25*theta)**2.5)
            x.append(int(r*np.cos(theta)))
            y.append(int(r*np.sin(theta)))

            if count == 1:
                num_marker_points = 3000
                start_ = 0.9 * r
                stop_ = 1.1 * r

                lin = np.linspace(start_, stop_, num_marker_points)
                for r_mod in lin:
                    marker_x.append(int(r_mod * np.cos(theta)))
                    marker_y.append(int(r_mod * np.sin(theta)))




        # Remember, first index is y, where 0 is the top and max is at the bottom
        # Second index is x, goes from left to right
        # Third index is the channel RGB

        spiral_coords_y = []
        spiral_coords_x = []


        for (delta_y, delta_x) in zip(y, x):
            if 0 <= center_y + delta_y + vertical_offset <= (height-1) and 0 <= center_x + delta_x + horizontal_offset <= (width-1):
                spiral_coords_y.append(center_y + delta_y + vertical_offset)
                spiral_coords_x.append(center_x + delta_x + horizontal_offset)

        for (delta_y, delta_x) in zip(marker_y, marker_x):
            if 0 <= center_y + delta_y + vertical_offset <= (
                    height - 1) and 0 <= center_x + delta_x + horizontal_offset <= (width - 1):

                marker_coords_x.append(center_y + delta_y + vertical_offset)
                marker_coords_y.append(center_x + delta_x + horizontal_offset)


        data_point_indices = []
        r_values = []

        count = 0
        for (cord_y, cord_x) in zip(spiral_coords_y, spiral_coords_x):
            count += 1
            spiral[cord_y, cord_x, :] = 255
            data_point_indices.append(count)
            r_values.append(R_MATRIX[cord_y, cord_x])



        for (cord_y, cord_x) in zip(marker_coords_y, marker_coords_x):
            count += 1
            spiral[cord_y, cord_x, :] = 255
            #data_point_indices.append(count)
            #r_values.append(R_MATRIX[cord_y, cord_x])

        fig = plt.figure()
        plt.plot(data_point_indices, r_values)
        plt.title("m=2, no PH, Phi_Values_Over_Circle\nRadius = {}, Delta_x = {}, Delta_y = {}".format(radius, x_offset, y_offset))
        plt.savefig(os.path.join(get_data_directory(csv_filename), "R_Values_Over_Radius={}.png".format(radius)))
        plot_paths.append(path.join(get_data_directory(csv_filename), "R_Values_Over_Radius={}.png".format(radius)))

    spiral_image = Image.fromarray(spiral.astype('uint8'), 'RGB')
    spiral_image.save(csv_filename.replace(".csv", "_circle.png"))


def vertically_stack_all_these_images(parent_folder, paths_to_images):
    # for a vertical stacking it is simple: use vstack

    list_im = paths_to_images #['Test1.jpg', 'Test2.jpg', 'Test3.jpg']
    imgs = [PIL.Image.open(i) for i in list_im]
    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
    list_ = [np.asarray(i.resize(min_shape)) for i in imgs]
    imgs_comb = np.vstack(list_)
    imgs_comb = PIL.Image.fromarray(imgs_comb)
    imgs_comb.save(os.path.join(parent_folder, 'R_Values_Over_Radii.png'))

def delete_all_sub_images(paths_to_images):
    for path in paths_to_images:
        try:
            os.remove(path)
        except OSError:
            pass

phi_csv = get_phi_sample()
run_dir = get_data_directory(phi_csv)
get_analysis_parameters(run_dir)
r_array = read_in_csv(phi_csv)
generate_images_from_R_matrix(r_array, phi_csv, circle_options)
vertically_stack_all_these_images(run_dir, plot_paths)
delete_all_sub_images(plot_paths)


os.chdir(start_dir)

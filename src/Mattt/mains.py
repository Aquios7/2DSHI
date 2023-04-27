#Use Tkinter for python 2, tkinter for python 3
import tkinter as tk
from src.toolsformatt import characterize_calibration_curve as ccc
from src.toolsformatt import create_k_v_a_phi_matrices as genphi
from src.toolsformatt import replace_nans as rn
from src.toolsformatt import gen_phi_from_csv as phi2png
from src.toolsformatt import gen_line_outs as glo
from tkinter.filedialog import askdirectory, askopenfilename
import os
import csv
import sys
import numpy as np
import PIL
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from os import path
from scipy import ndimage



class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.r_stats_full_path = None
        self.r_min_full_path = None
        self.r_max_full_path = None
        self.pre_calibration_path = None
        self.calibration_directory = None
        self.analytics_directory = None
        self.alpha = None
        self.v = None
        self.r_sample_full_path = None
        self.r_background_full_path = None

        self.r_min_full_path_nonans = None
        self.r_max_full_path_nonans = None
        self.r_sample_full_path_nonans = None
        self.r_background_full_path_nonans = None
        self.min_f = None
        self.max_f = None

        self.phi_bg_lineout = None
        self.phi_lineout = None
        self.phi_minus_bg_lineout = None

        self.phi_csv_path = None
        self.phi_minus_bg_csv_path = None
        self.phi_background_csv_path = None
        self.checkvar1 = 0
        self.line_out_phi_path = None
        self.line_out_bg_path = None
        self.integrated_sample_path = None
        self.integrated_bg_path = None

        self.phi_image_array = None
        self.phi_bg_image_array = None

        self.parent = parent

        """Column 1: Calibration Parameters"""

        self.analytics_directory_and_calib_curve_inputs = tk.Label(self.parent,
                                                                   text="Add Calibration Curve and Analytics Directory")
        self.analytics_directory_and_calib_curve_inputs.grid(column=1, row=0, padx=5, pady=10, sticky="W")

        self.pre_calibration_button = tk.Button(self.parent, text="Use A Previous Calibration", anchor="w",
                                              command=self.select_pre_calibration_file)
        self.pre_calibration_button.grid(column=1, row=1, padx=10, pady=1, sticky="W")

        self.pre_calibration_label = tk.Label(self.parent, text="")
        self.pre_calibration_label.grid(column=1, row=2, padx=10, pady=5, sticky="W")

        self.analytics_dir_button = tk.Button(self.parent, text="Select An Analytics Directory", anchor="w",
                                              command=self.select_analytics_directory)
        self.analytics_dir_button.grid(column=1, row=3, padx=10, pady=1, sticky="W")

        self.analytics_dir_label = tk.Label(self.parent, text="")
        self.analytics_dir_label.grid(column=1, row=4, padx=10, pady=5, sticky="W")

        self.cal_curve_button = tk.Button(self.parent, text="Select Calibration Curve", anchor="w",
                                          command=self.select_calibration_directory)
        self.cal_curve_button.grid(column=1, row=5, padx=10, pady=10, sticky="W")

        self.calibration_directory_label = tk.Label(self.parent, text="")
        self.calibration_directory_label.grid(column=1, row=6, padx=5, pady=5, sticky="W")

        self.r_min_label = tk.Label(self.parent, text="")
        self.r_min_label.grid(column=1, row=7, padx=10, pady=5, sticky="W")

        self.r_max_label = tk.Label(self.parent, text="")
        self.r_max_label.grid(column=1, row=8, padx=10, pady=5, sticky="W")

        self.alpha_label = tk.Label(self.parent, text="")
        self.alpha_label.grid(column=1, row=9, padx=10, pady=5, sticky="W")

        self.v_label = tk.Label(self.parent, text="")
        self.v_label.grid(column=1, row=10, padx=10, pady=5, sticky="W")

        self.alpha_overwrite = tk.Entry(self.parent)
        #if self.alpha_overwrite.get() != '':
            #self.alpha_overwrite = float(self.alpha_overwrite.get())
        self.alpha_overwrite.grid(column=1, row=12, padx=10, pady=5, sticky="W")
        self.alpha_overwrite_label = tk.Label(self.parent, text="Alpha overwrite")
        self.alpha_overwrite_label.grid(column=1, row=11, padx=10, pady=5, sticky="W")


        """Column 2: R Sample and R Background"""

        self.sample_and_bg_files = tk.Label(self.parent, text="Add Sample and Background Matrices")
        self.sample_and_bg_files.grid(column=2, row=0, padx=5, pady=10, sticky="W")

        self.select_sample_button = tk.Button(self.parent, text="Select Sample", anchor="w",
                                          command=self.pick_r_sample)
        self.select_sample_button.grid(column=2, row=1, padx=10, pady=1, sticky="W")

        self.select_background_button = tk.Button(self.parent, text="Select Background", anchor="w",
                                          command=self.pick_r_background)

        self.select_background_button.grid(column=2, row=3, padx=10, pady=1, sticky="W")

        self.r_sample_label = tk.Label(self.parent, text="")
        self.r_sample_label.grid(column=2, row=2, padx=10, pady=5, sticky="W")

        self.r_background_label = tk.Label(self.parent, text="")
        self.r_background_label.grid(column=2, row=4, padx=10, pady=5, sticky="W")


        """Column 3: Create Phi Matrices and PNGs"""

        self.png_and_csv_text = tk.Label(self.parent, text="Generate first CSV and PNG")
        self.png_and_csv_text.grid(column=3, row=0, padx=5, pady=10, sticky="W")

        # self.gen_phi_csv_button = tk.Button(self.parent, text="Generate phi CSVs", anchor="w",
        #                                           command=self.gen_kvaphi_matrices)
        # self.gen_phi_csv_button.grid(column=3, row=1, padx=10, pady=1, sticky="W")
        #
        # self.gen_phi_img_button = tk.Button(self.parent, text="Generate Phi IMGs", anchor="w",
        #                                           command=self.gen_imgs)
        # self.gen_phi_img_button.grid(column=3, row=2, padx=10, pady=5, sticky="W")
        self.moving_average_label = tk.Label(self.parent, text="Moving average pixels")
        self.moving_average_label.grid(column=3, row=1, padx=5, pady=3, sticky='W')
        self.moving_average_entry = tk.Entry(self.parent)
        self.moving_average_entry.grid(column=3, row=2, padx=5, pady=3, sticky='W')
        self.run = tk.Button(self.parent, text='Run', anchor='w', command=self.moving_average)
        self.run.grid(column=3, row=3, padx=5, pady=3, sticky='W')

        """Column 4: Line outs"""

        # self.pick_line_out_label = tk.Label(self.parent, text="Pick a line out type")
        # self.pick_line_out_label.grid(column=4, row=0, padx=5, pady=2, sticky="W")
        #
        # self.line_out_option_var = tk.StringVar(self.parent)
        # self.line_out_option_var.set("Radial")  # default value
        # line_out_options = ["Radial", "Spiral", "Vertical/Horizontal"]
        # self.option_menu = tk.OptionMenu(self.parent, self.line_out_option_var, *line_out_options)
        # self.option_menu.grid(column=4, row=1, padx=5, pady=2, sticky="W")
        #
        # self.chose_line_out_button = tk.Button(self.parent, text="Specify Line Out Parameters", anchor="w",
        #                                        command=self.create_line_out_options)
        # self.chose_line_out_button.grid(column=4, row=2, padx=5, pady=2, sticky="W")
        #
        # self.radial_entry_instructions = tk.Label(self.parent, text="Enter number of lines.")
        # self.radial_entry_instructions.grid(column=4, row=3, padx=5, pady=2, sticky="W")
        # self.radial_entry = tk.Entry(self.parent)
        # self.radial_entry.grid(column=4, row=4, padx=5, pady=2, sticky="W")
        #
        # self.vertical_offset_label = tk.Label(self.parent, text="Set vertical offset")
        # self.vertical_offset_label.grid(column=4, row=5, padx=5, pady=3, sticky='W')
        # self.set_vertical_offset = tk.Entry(self.parent)
        # self.set_vertical_offset.grid(column=4, row=6, padx=5, pady=3, sticky='W')
        #
        # self.horizontal_offset_label = tk.Label(self.parent, text="Set horizontal offset")
        # self.horizontal_offset_label.grid(column=4, row=7, padx=5, pady=3, sticky='W')
        # self.set_horizontal_offset = tk.Entry(self.parent)
        # self.set_horizontal_offset.grid(column=4, row=8, padx=5, pady=3, sticky='W')
        #
        # self.run = tk.Button(self.parent, text='Run', anchor='w', command=self.process_radian_values)
        # self.run.grid(column=4, row=9, padx=5, pady=3, sticky='W')

        """Column 5: Create Line out PNGs"""

        # self.integrate_label = tk.Label(self.parent, text="Integrate phase")
        # self.integrate_label.grid(column=5, row=0, padx=5, pady=3, sticky='W')
        # self.run = tk.Button(self.parent, text='Run', anchor='w', command=self.integrate_phi)
        # self.run.grid(column=5, row=1, padx=5, pady=3, sticky='W')

        # self.integrate_10_label = tk.Label(self.parent, text="Integrate phase 10")
        # self.integrate_10_label.grid(column=5, row=2, padx=5, pady=3, sticky='W')
        # self.run = tk.Button(self.parent, text='Run', anchor='w', command=self.integrate_phi_by_10)
        # self.run.grid(column=5, row=3, padx=5, pady=3, sticky='W')

        # self.subtract = tk.Label(self.parent, text="Subtract")
        # self.subtract.grid(column=5, row=4, padx=5, pady=3, sticky='W')
        # self.run = tk.Button(self.parent, text='Run', anchor='w', command=self.subtractz)
        # self.run.grid(column=5, row=5, padx=5, pady=3, sticky='W')


    """""
    popout window prompts a user to select a directory/folder to save all new data    
    """""
    def select_analytics_directory(self):
        self.analytics_directory = askdirectory(title="Pick an analytics directory")
        self.analytics_dir_label.config(text=self.analytics_directory)

        self.no_nan_button = tk.Button(self.parent, text="Generate No NaN Files", anchor="w",
                                          command=self.gen_no_nan_files)
        self.no_nan_button.grid(column=2, row=5, padx=10, pady=1, sticky="W")

        self.no_nan_label = tk.Label(self.parent, text="")
        self.no_nan_label.grid(column=2, row=6, padx=10, pady=1, sticky="W")

        #self.no_nan_label =  tk.Label(self.parent, text="")
        #self.no_nan_label.grid(column=3, row=2, padx=10, pady=5, sticky="W")

    """""
    popout window lets you search directories for an r.csv  
    """""
    def pick_r_sample(self):
        self.r_sample_full_path = genphi.get_r_sample()
        self.r_sample_label.config(text=self.r_sample_full_path)

    """""
    dropdown menue lets users select a bg R.csv
    """""
    def pick_r_background(self):
        self.r_background_full_path = genphi.get_r_background()
        self.r_background_label.config(text=self.r_background_full_path)

    """""
    replaces NANs with 0 for r_sample, r_bg,r_min from calibration curve, r_max from calibration curve 
    """""
    def gen_no_nan_files(self):
        _files_ = {
            "r_sample": self.r_sample_full_path,
            "r_background": self.r_background_full_path,
            "r_min": self.r_min_full_path,
            "r_max": self.r_max_full_path,
            "pre_calibration": self.pre_calibration_path
        }

        for _file_ in _files_:
            new_shorthand_path = _file_ + "_noNANs.csv"
            new_full_path = os.path.join(self.analytics_directory, new_shorthand_path)

            if _file_ == "r_sample":
                self.r_sample_full_path_nonans = new_full_path
            elif _file_ == "r_background":
                self.r_background_full_path_nonans = new_full_path
            elif _file_ == "r_min":
                self.r_min_full_path_nonans = new_full_path
            elif _file_ == "r_max":
                self.r_max_full_path_nonans = new_full_path

            if _file_ != "pre_calibration":
                print("Generating NoNans Version of {0}".format(_file_))
                print("Source File: {0}".format(_files_[_file_]))
                print("NoNan Version: {0}\n\n".format(new_full_path))
                rn.replace_nans_in_file(_files_[_file_], save_to=new_full_path)
                self.no_nan_label.config(text="completed")

        # Saving data sources
        _files_["r_matrices_stats"] = self.r_stats_full_path

        with open(os.path.join(self.analytics_directory, 'data_sources.csv'), 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in _files_.items():
                writer.writerow([key, value])

        if _file_ == "pre_calibration":
            print("Generating Pre-calibration Version of this run")
            print("Source File: {0}".format(_files_[_file_]))
            calib_list = [("analytics_directory", self.analytics_directory),
                          ("calibration_curve", self.calibration_directory),
                          ("r_sample", self.r_sample_full_path),
                          ("r_background", self.r_background_full_path),
                          ("r_sample_noNaNs", self.r_sample_full_path_nonans),
                          ("r_background_noNaNs", self.r_background_full_path_nonans),
                          ("r_min_path", self.r_min_full_path),
                          ("r_max_path", self.r_max_full_path),
                          ("r_min_path_noNaNs", self.r_min_full_path_nonans),
                          ("r_max_path_noNaNs", self.r_max_full_path_nonans),
                          ("r_stats_full_path", self.r_stats_full_path),
                          ("alpha", self.alpha),
                          ("alpha_overwrite", float(self.alpha_overwrite.get())),
                          ("v", self.v),
                          ("min_f", self.min_f),
                          ("max_f", self.max_f)]
            with open(os.path.join(os.getcwd(), 'last_calibration.csv'), 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                for key, value in calib_list:
                    writer.writerow([key, value])

            #place the phi and img generation here to remove the buttons
            # csv matrices
            self.gen_kvaphi_matrices()
            # iamges
            self.gen_imgs()



    def readKeyValues(self):
        # input file reader
        infile = open(self.pre_calibration_path, "r")
        read = csv.reader(infile)

        returnDict = {}

        # for each row
        for row in read:
            key = row[0]
            value = row[1]
            # Add to list
            returnDict[key] = value
        return returnDict


    """""
    popout window prompts a user to select a previous calibration csv file
    """""
    def select_pre_calibration_file(self):
        self.pre_calibration_path = genphi.get_pre_calibration()
        self.pre_calibration_label.config(text=self.pre_calibration_path)
        calibration_list = self.readKeyValues()
        # input analytics directory
        self.analytics_directory = calibration_list["analytics_directory"]
        self.analytics_dir_label.config(text=self.analytics_directory)
        # input calibration curve
        self.r_stats_full_path = calibration_list["r_stats_full_path"]
        self.calibration_directory = calibration_list["calibration_curve"]
        self.r_min_full_path = calibration_list["r_min_path"]
        self.r_max_full_path = calibration_list["r_max_path"]
        self.alpha = float(calibration_list["alpha"])
        self.v = float(calibration_list["v"])
        self.min_f = calibration_list["min_f"]
        self.max_f = calibration_list["max_f"]
        self.r_min_label.config(text="Min: Frame " + str(self.min_f))
        self.r_max_label.config(text="Max: Frame " + str(self.max_f))
        self.calibration_directory_label.config(text="" + self.calibration_directory)
        self.alpha_label.config(text="alpha: " + str(calibration_list["alpha"]))
        self.v_label.config(text="v: " + str(calibration_list["v"]))
        # input alpha overwrite (if any)
        self.alpha_overwrite.setvar(calibration_list["alpha_overwrite"])
        if self.alpha_overwrite != '':
            self.alpha_overwrite.insert(0, calibration_list["alpha_overwrite"])
        # input sample
        self.r_sample_full_path = calibration_list["r_sample"]
        self.r_sample_label.config(text=self.r_sample_full_path)
        # input background
        self.r_background_full_path = calibration_list["r_background"]
        self.r_background_label.config(text=self.r_background_full_path)
        # input noNaNs
        self.r_max_full_path_nonans = calibration_list["r_max_path_noNaNs"]
        self.r_min_full_path_nonans = calibration_list["r_min_path_noNaNs"]
        self.r_sample_full_path_nonans = calibration_list["r_sample_noNaNs"]
        self.r_background_full_path_nonans = calibration_list["r_background_noNaNs"]
        # create noNaNs button
        self.no_nan_button = tk.Button(self.parent, text="Generate No NaN, CSV & IMG Files", anchor="w",
                                          command=self.gen_no_nan_files)
        self.no_nan_button.grid(column=2, row=5, padx=10, pady=1, sticky="W")

        self.no_nan_label = tk.Label(self.parent, text="Complete")
        self.no_nan_label.grid(column=2, row=6, padx=10, pady=1, sticky="W")


    """""
    uses calibration curve or alpha overwrite to create K,V,alpha matrices and applies a transform to take R csvs
    and turns them to phi csvs
    """""
    def gen_kvaphi_matrices(self):

        if self.alpha_overwrite.get() == "":
            self.phi_csv_path, self.phi_minus_bg_csv_path, self.phi_background_csv_path = genphi.generate_kvaphi_matrices(
                self.r_min_full_path_nonans,
                self.r_max_full_path_nonans,
                self.r_sample_full_path_nonans,
                self.r_background_full_path_nonans,
                self.analytics_directory,
                self.v,
                self.alpha)
            self.gen_kvaphi_label = tk.Label(self.parent, text="")
            self.gen_kvaphi_label.config(text="Phi matrices generated")
        else:
            self.phi_csv_path, self.phi_minus_bg_csv_path, self.phi_background_csv_path = genphi.generate_kvaphi_matrices(
                self.r_min_full_path_nonans,
                self.r_max_full_path_nonans,
                self.r_sample_full_path_nonans,
                self.r_background_full_path_nonans,
                self.analytics_directory,
                self.v,
                float(self.alpha_overwrite.get()))
            self.gen_kvaphi_label = tk.Label(self.parent, text="")
            self.gen_kvaphi_label.config(text="Phi matrices generated")

    """""
    dropdown menu allows users to pick lineout options radial, spiral, linear. each option has parameters the user needs
    to specify.  
    """""
    def create_line_out_options(self):
        """Column 4: Entry field for angles"""

        if self.line_out_option_var.get() == "Radial":
            self.radial_entry_instructions = tk.Label(self.parent, text="Enter number of lines.")
            self.radial_entry_instructions.grid(column=4, row=3, padx=5, pady=2, sticky="W")

            self.radial_entry = tk.Entry(self.parent)
            self.radial_entry.grid(column=4, row=4, padx=5, pady=2, sticky="W")

        if self.line_out_option_var.get() == "Spiral":
            self.spiral_entry_instructions = tk.Label(self.parent,text='Enter radius of circles.')
            self.spiral_entry_instructions.grid(column=4, row=3, padx=5, pady=2, sticky="W")

            self.spiral_entry = tk.Entry(self.parent)
            self.spiral_entry.grid(column=4, row=4, padx=5, pady=2, sticky="W")

        if self.line_out_option_var.get() == "Vertical/Horizontal":
            self.horivert_entry_instructions = tk.Label(self.parent,text='Enter number of lines.')
            self.horivert_entry_instructions.grid(column=4, row=3, padx=5, pady=2, sticky="W")

            self.horivert_entry = tk.Entry(self.parent)
            self.horivert_entry.grid(column=4, row=4, padx=5, pady=2, sticky="W")

    """""
    creates images for lineouts on both gb and sample
    """""
    def gen_imgs2(self):
        self.phi_lineout = pd.read_csv('data_out/phi_lineouts_by_angle.csv')
        self.phi_bg_lineout = pd.read_csv('data_out/phi_bg_lineouts_by_angle.csv')

        phi2png.gen_phi_imgs2(self.phi_lineout, self.phi_bg_lineout)
        load = Image.open('data_out\phi_lineouts_by_angle.csv')
        resize_img = load.resize(120, 120)
        render = PIL.ImageTk.PhotoImage(resize_img)

        img2 = tk.Label(self.parent, image=render)
        img2.grid(column=5, row=5, padx=5, pady=5, sticky="W")
        img2.image = render

    """""
    creates phase images for bg, sample and sample-bg
    """""
    def gen_imgs(self):
        paths = phi2png.gen_phi_imgs(self.phi_csv_path, self.phi_minus_bg_csv_path, self.phi_background_csv_path)
        self.phi_image_array = paths[0]
        self.phi_bg_image_array = paths[0]
        self.gen_imgs_label = tk.Label(self.parent, text="")
        self.gen_imgs_label.config(text="Phi imgs generated")

    """""
    uses characterize function from tools to generate K,V,alpha values from a popout window
    """""
    def select_calibration_directory(self):
        try:
            d, a, v, min_f, max_f = ccc.characterize()
            # characterize() spits out
            # directory, alpha, v, min_frame, max_frame
            self.r_stats_full_path = d
            self.calibration_directory = d.split("/")[-2]
            self.r_min_full_path = d.replace("r_matrices_stats", "r_matrix_{0}".format(min_f))
            self.r_max_full_path = d.replace("r_matrices_stats", "r_matrix_{0}".format(max_f))
            self.alpha = float(a)
            self.v = float(v)
            self.min_f = min_f
            self.max_f = max_f

            self.r_min_label .config(text="Min: Frame " + str(min_f))
            self.r_max_label .config(text="Max: Frame " + str(max_f))
            self.calibration_directory_label.config(text="" + self.calibration_directory)
            self.alpha_label.config(text="alpha: " + str(a))
            self.v_label.config(text="v: " + str(v))
        except (FileNotFoundError, FileExistsError):
            self.calibration_directory_label.config(text="Pick a calibration run")

    """""
    takes the user specified parameters (type of lineouts, nuber of lines
    """""
    def process_radian_values(self):
        if self.line_out_option_var.get() == "Radial":
            if self.radial_entry.get() == "":
                num_lines = 4
            else:
                num_lines = int(self.radial_entry.get())
        if self.line_out_option_var.get() == "Vertical/Horizontal":
            num_lines = int(self.horivert_entry.get())
        num_lines_list = list()
        for i in range(num_lines): num_lines_list.append(i)
        angles = list()
        vertical_offset = self.set_vertical_offset.get()

        horizontal_offset = self.set_horizontal_offset.get()
        files = (self.phi_csv_path, self.phi_background_csv_path)

        # print("Starting for loop: for file in files")
        for file in files:
            if vertical_offset == "": vertical_offset = 0
            if horizontal_offset == "": horizontal_offset = 0
            plot_paths = list()
            height_phi = int(glo.get_phi_csv_shape(file)[0])
            R_MATRIX = np.asarray(glo.gen_radial_line_outs(file))
            # spiral = np.zeros(shape=(height_phi, height_phi))
            data_dictionary = dict()
            data_dict = dict()
            center_phi = int(height_phi/2)
            arrays = self.phi_image_array, self.phi_bg_image_array

            for i in range(num_lines):
                angles.append((i/num_lines)*2*np.pi+(np.pi/num_lines))
                num_lines_list.append(i)
                data_dict["line={}".format(i)] = list()

            # print(angles)
            for i in range(int(num_lines)):
                num = num_lines_list[i]
                y = []
                x = []
                points = int(center_phi)
                angle = angles[i]

                for rad in np.linspace(0, int(np.sqrt(2)*(center_phi-1)), num=points):
                    r = int(rad)
                    x.append(int(r * np.cos(angle)))
                    y.append(int(r * np.sin(angle)))
                spiral_coords_y = []
                spiral_coords_x = []

                # Below checks if the points will be on the phi image or not, if they are they are added to spiral_coords
                for (delta_y, delta_x) in zip(y, x):
                    if 0 <= center_phi + delta_y + int(vertical_offset) <= (
                            height_phi - 1) and 0 <= center_phi + delta_x + int(horizontal_offset) <= (height_phi - 1):
                        spiral_coords_y.append(center_phi + delta_y + int(vertical_offset))
                        spiral_coords_x.append(center_phi + delta_x + int(horizontal_offset))

                data_point_indices = []
                r_values = []
                # below gets the phi image data points that correspond to the radial line outs and writes it to an arbitrary
                # number
                count1 = 0
                for (cord_y, cord_x) in zip(spiral_coords_y, spiral_coords_x):
                    # print(cord_x,cord_y)
                    for array in arrays:
                        array[cord_y,cord_x] = 255
                    count1 += 1
                    # print("Count1 = {0}, len(r_values) = {1}".format(count1, len(r_values)))
                    # spiral[int(cord_y), int(cord_x)] = 255
                    data_point_indices.append(count1)
                    r_values.append(R_MATRIX[int(cord_y), int(cord_x)])
                data_dictionary["line={}".format(num)] = r_values
                markedimage1 = Image.fromarray(self.phi_image_array.astype('uint8'), 'RGB')
                markedimage1.save(file.replace(".csv","_marked.png"))
                markedimage2 = Image.fromarray(self.phi_bg_image_array.astype('uint8'), 'RGB')
                markedimage2.save(file.replace(".csv","_marked.png"))
                fig = plt.figure()
                plt.plot(data_point_indices, r_values)
                current_file_distinguisher_test = os.path.basename(os.path.normpath(file))
                _test, file_extension_test = os.path.splitext(file)
                current_file_distinguisher_test = current_file_distinguisher_test.replace(file_extension_test, "")

                plt.title("{0}: Phi_Values_Over_Lineout\ny = {1}".format(current_file_distinguisher_test, i))
                plt.savefig(
                    os.path.join(glo.get_data_directory(file), "{}={}.png".format(file,i)))
                plot_paths.append(
                    path.join(glo.get_data_directory(file), "{}={}.png".format(file,i)))

            run_dir = self.analytics_directory
            dataset = pd.DataFrame(data_dictionary)
            pathvar = os.path.join(glo.get_data_directory(file), file.replace(".csv", "_lineouts_by_angle.csv"))
            if file == self.phi_csv_path:
                self.line_out_phi_path = pathvar
            else:
                self.line_out_bg_path = pathvar
            dataset.to_csv(pathvar)
            current_file_distinguisher = os.path.basename(os.path.normpath(file))
            _, file_extension = os.path.splitext(file)
            current_file_distinguisher = current_file_distinguisher.replace(file_extension, "")
            glo.vertically_stack_all_these_images(run_dir, plot_paths, current_file_distinguisher)
            glo.delete_all_sub_images(plot_paths)

    """""
     moving average of sample and bg phi csvs. default value is 3 pixels if prompt left empty
     """""
    def moving_average(self):
        if self. moving_average_entry.get() == "":
            newvar = 3
        else:
            newvar =  int(self.moving_average_entry.get())

        for file in self.phi_csv_path,self.phi_background_csv_path:
            csv_file = pd.read_csv(file, header=None)
            values = csv_file.values
            result = ndimage.uniform_filter(values,newvar, mode="nearest")
            pathvar = file.replace(".csv","")
            csv_path = os.path.join(pathvar, "{}_avg_{}.csv".format(pathvar, str(newvar)))


            with open(csv_path, "w+", newline='') as my_csv:
                csvWriter = csv.writer(my_csv, delimiter=',')
                csvWriter.writerows(result.tolist())
                if file == self.phi_csv_path:
                    self.phi_csv_path = csv_path
                elif file == self.phi_background_csv_path:
                    self.phi_background_csv_path = csv_path
    """""
    Integrates phi values of sample and bg from center outwards.
    Two functions, one for 1 pixel at a time and another for ten pixels at a time. 
    """""
    def integrate_phi(self):
        files = (self.line_out_phi_path,self.line_out_bg_path)
        linedict = dict()
        for file in files:
            df = pd.read_csv(file)
            nparray = df.to_numpy()
            for i in range(len(nparray[0,:])):
                index = i
                yintegrated = list()
                y = nparray[:,int(index)]
                # print(y)
                tmp = y
                for i2 in range(len(y)):
                    var = int(i2)
                    if i2 == 0:
                        yintegrated.append(0)
                    else:
                        yintegrated.append(abs(tmp[var] - tmp[var - 1]) + yintegrated[var - 1])
                linedict["line={}".format(i)] = yintegrated
            pathvar2 = os.path.join(glo.get_data_directory(file), file.replace(".csv", "integrated.csv"))
            dataframe = pd.DataFrame(linedict)
            dataframe.to_csv(pathvar2, index = False)
            if file == self.line_out_phi_path:
                self.integrated_sample_path = pathvar2
            else:
                self.integrated_bg_path = pathvar2

    def integrate_phi_by_10(self):
        files = (self.line_out_phi_path, self.line_out_bg_path)
        linedict = dict()
        for file in files:
            df = pd.read_csv(file)
            nparray = df.to_numpy()
            for i in range(len(nparray[0,:])):
                index = i
                yintegrated = list()
                y = nparray[:, int(index)]
                tmp = y
                step = int(len(y)/10)
                for i2 in range(step):
                    var = int(i2)*10
                    if i2 == 0:
                        yintegrated.append(0)
                    elif 0<i2<int(len(y)):
                        yintegrated.append(abs(tmp[var] - tmp[var - 10]) + yintegrated[i2 - 1])
                    else:
                        break

                linedict["line={}".format(i)] = yintegrated
            pathvar2 = os.path.join(glo.get_data_directory(file), file.replace(".csv", "integrated_by_10.csv"))
            dataframe = pd.DataFrame(linedict)
            dataframe.to_csv(pathvar2)
            if file == self.line_out_phi_path:
                self.integrated_sample_path = pathvar2
            else:
                self.integrated_bg_path = pathvar2

    """""
    subtracts integrated values to give (sample+bg) - bg = sample delta phi
    """""
    def subtractz(self):
        files = (self.integrated_sample_path, self.integrated_bg_path)
        sample = pd.read_csv(files[0]).values
        bg = pd.read_csv(files[1]).values
        subtracted = np.subtract(sample,bg)
        subtracted = np.delete(subtracted,0,1)
        subtracted = np.delete(subtracted,1,0)
        sub_path = os.path.join(self.analytics_directory, "SUBTRACTED.csv")
        print(sub_path)

        with open(sub_path, "w+", newline='') as f:
            csvWriter = csv.writer(f, delimiter=',')
            csvWriter.writerows(subtracted.tolist())

    def kill_app(self):
        self.parent.quit()


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()
    sys.exit(0)



"""
from gui import app

if __name__ == '__main__':
    app = app.App()
    app.run()
"""

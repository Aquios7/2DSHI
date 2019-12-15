import matplotlib.pyplot as plt
import numpy as np

import cv2
import os


run = "2019_12_14__13_08"

img_a_path = os.path.join("D:", "2DSHI_Runs")
img_a_path = os.path.join(img_a_path, run)
algebra_directory = os.path.join(img_a_path, "Image_Algebra")
img_a_path = os.path.join(img_a_path, "cam_a_frames")
img_a_path = os.path.join(img_a_path, "cam_a_frame_1.png")
img_a = np.asarray(cv2.imread(img_a_path, cv2.IMREAD_ANYDEPTH))
img_a_12_bit = img_a/16

img_b_prime_path = os.path.join(algebra_directory, "B_Prime.png")
img_b_prime = np.asarray(cv2.imread(img_b_prime_path, cv2.IMREAD_ANYDEPTH))
img_b_prime_12_bit = img_b_prime/16


subtracted = np.subtract(img_a_12_bit, img_b_prime_12_bit)
added = np.add(img_a_12_bit, img_b_prime_12_bit)


def create_colormap(file_name, save_directory, array, algebra_type):
    save_path = os.path.join(save_directory, file_name)
    fig = plt.figure()
    imgplot = plt.imshow(array)
    imgplot.set_cmap('bwr')
    for im in plt.gca().get_images():
        if "subtraction" in algebra_type:
            im.set_clim(-4095*2, 4095*2)
        if "addition" in algebra_type:
            im.set_clim(-4095*2, 4095*2)
    plt.colorbar()
    plt.show()
    fig.savefig(save_path)



create_colormap("A_Minus_B_Prime_Colormap.png", algebra_directory, subtracted, "subtraction")
create_colormap("A_Plus_B_Prime_Colormap.png", algebra_directory, added, "addition")

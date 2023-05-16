import os
from PIL import Image
import cv2
import numpy as np

def read_img(img_path):
    return cv2.imread(img_path, cv2.IMREAD_ANYDEPTH)

def reduce_bit_depth(image_array, original_bit_depth=12, intended_bit_depth=8):
    """
    Lossy.
    TODO: Check if we are using this function anywhere, and if so, add documentation. Else, delete.

    """
    if intended_bit_depth not in (8, 12):
        raise RuntimeError(
            "\nLooks like you want to convert your image to a bit depth of {}.\n"
            "Unfortunately, this program currently only supports reduction of images to 8 or 12 bit."
            .format(intended_bit_depth))
    if intended_bit_depth == 8:
        return np.array(image_array/(2**(original_bit_depth-intended_bit_depth)), dtype=np.uint8)
    if intended_bit_depth == 12:
        return image_array/(2**(original_bit_depth-intended_bit_depth))



def save_img(filename, directory, image, bit_depth=16):
    """
    Saves an image to the specified directory at a specified bit depth.
    (For our purposes, all images are grayscale).

    Args:
        filename (str): The filename you with to use (i.e. img_23.png)
        directory (str): The directory you with to save the img to (i.e. C:/username/images).
        image (numpy.array): TODO: Verify this is a numpy array and add description.
        bit_depth (int): The intended bit depth. Must be a power of 2 >= 8 (i.e. 8, 16, 32).
    """
    cwd = os.getcwd()
    os.chdir(directory)
    if bit_depth == 16:
        image = Image.fromarray(image)
        image.save(filename, compress_level=0)
    else:
        cv2.imwrite(filename, image.astype(np.uint16))
    os.chdir(cwd)

import numpy as np


def to_16_bit(image_array, original_bit_depth=12):
    """
    Takes an image array and represents it as 16 bit by multiplying all the values by the corresponding integer and
    specifying the bit depth in the creation of a new 2D Numpy Array.

    Args:
        image_array (numpy.ndarray): The original image array.
    Returns:
        numpy.ndarray: The same image represented
    """
    if original_bit_depth == 16:
        return image_array
    if original_bit_depth < 16:
        return np.array(image_array * 2**(16-original_bit_depth), dtype=np.uint16).astype(np.uint16)
    else:
        raise Exception('Original Bit Depth was greater than or equal to 16')


def to_8_bit(image_array, original_bit_depth=12):
    """
    Takes an image array and represents it as 8 bit array TODO: Describe how

    Args:
        image_array (numpy.ndarray): The original image array.
    Returns:
        numpy.ndarray: The same image represented as a 8 bit array (TODO: Verify if Conversion is indeed lossy )
    """
    if original_bit_depth == 12:
        return np.array(image_array/16, dtype=np.uint8).astype(np.uint8)
    return None

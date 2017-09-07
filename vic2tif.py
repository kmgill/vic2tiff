
import os
import sys
import re
import numpy as np
from struct import *
from libtiff import TIFFimage
import math
import argparse


# This is Cassini-specific!
def build_output_filename(value_pairs):
    PRODUCT_ID = value_pairs["PRODUCT_ID"]
    PRODUCT_ID = PRODUCT_ID[PRODUCT_ID.find("_")+1:PRODUCT_ID.find(".")]
    FILTERS = value_pairs["FILTER_NAME"][1:-1].split(",")

    output_filename = "%s_%s_%s.tif"%(PRODUCT_ID, FILTERS[0], FILTERS[1])

    return output_filename

def load_vic(input_file):
    if not os.path.exists(input_file):
        print "Input file '%s' not found!"%input_file
        return None, None

    f = open(input_file, "rb")
    data = f.read()
    f.close()

    # First, we need to extract the label size
    lblsize_tag = re.search('LBLSIZE=[0-9]+', data).group(0)
    LBLSIZE = int(re.search("[0-9]+", lblsize_tag).group(0))

    # Extract whole label
    label = data[0:LBLSIZE]

    # Convert raw label in to a key/value dictionary
    e = re.compile('(?:\w+)=[^ \t]+')
    value_pairs_str = e.findall(label)
    value_pairs_lst = [vp.replace("'", "").split("=") for vp in value_pairs_str]

    value_pairs = {}
    for pair in value_pairs_lst:
        value_pairs[pair[0]] = pair[1]

    pixel_format = value_pairs["FORMAT"]
    int_format = value_pairs["INTFMT"]
    real_format = value_pairs["REALFMT"]

    unpack_format = "<f" # Will need to determine this based off of pixel_format and real_format/int_format

    NBB = int(value_pairs["NBB"])         # Number of bytes in binary prefix before each record
    NLB = int(value_pairs["NLB"])         # Number of lines (records) of binary header at the top of the file
    NL = int(value_pairs["NL"])           # Number of lines
    N1 = int(value_pairs["N1"])           # The size (in pixels) of the first dimension
    N2 = int(value_pairs["N2"])           # The size of the second dimension
    N3 = int(value_pairs["N3"])           # Size of third dimension
    NS = int(value_pairs["NS"])           # Number of samples in the image
    NB = int(value_pairs["NB"])           # Number of bands in the image
    RECSIZE = int(value_pairs["RECSIZE"]) # RECSIZE & (NBB + N1 * Pixel Size) should match
    NUMLINES = N2 * N3                    # NL & NUMLINES should match

    binary_header_size = (NLB * RECSIZE)
    binary_header_size_start = LBLSIZE
    binary_header_stop = binary_header_size + binary_header_size_start
    binary_header = data[binary_header_size_start:binary_header_stop] # Not actually doing anything with this

    pixel_matrix = np.zeros((NL, NS))

    for line_index in range(0, NUMLINES):
        line_start = binary_header_stop + (line_index * RECSIZE)
        binary_prefix_end = line_start + NBB
        line_pixels_start = binary_prefix_end
        line_end = line_start + RECSIZE

        line_binary_prefix = data[line_start:binary_prefix_end] # Not actually doing anything with this
        line_pixels_data = data[line_pixels_start:line_end]

        for s in range(0, NS):
            sample_start = s * 4 # Assuming 4 byte REAL for now...
            sample_end = sample_start + 4
            sample = line_pixels_data[sample_start:sample_end]
            sample_value = unpack(unpack_format, sample)[0]
            if math.isnan(sample_value) or sample_value == -1000.0:
                sample_value = np.nan
            pixel_matrix[line_index][s] = sample_value

    return pixel_matrix, value_pairs

"""
Detect rows of null values that are a result of Cassini non-lossy compression
"""
def detect_null_stripes(pixel_matrix):

    stripes = []

    height = pixel_matrix.shape[0]
    width = pixel_matrix.shape[1]

    for y in range(501, height-1, 2):
        for x in range(width - 2, -1, -1):

            pixel_value_prev_row = pixel_matrix[y-1][x]
            pixel_value = pixel_matrix[y][x]
            pixel_value_next_row = pixel_matrix[y+1][x]
            #if pixel_value == 0.0 and pixel_value_prev_row != 0.0 and pixel_value_next_row != 0.0:
            #    print pixel_value_prev_row, pixel_value, pixel_value_next_row
            if pixel_value != 0.0 and pixel_value_prev_row != 0.0 and pixel_value_next_row != 0.0:
                if x < width - 2:
                    stripes.append((y, x+1))
                break

    return stripes

def fill_stripe(pixel_matrix, row, start_x):
    for x in range(start_x, pixel_matrix.shape[1]):
        prev_row_value = pixel_matrix[row-1][x]
        next_row_value = pixel_matrix[row+1][x]
        fill_value = np.mean([prev_row_value, next_row_value])
        pixel_matrix[row][x] = fill_value


def fill_stripes(pixel_matrix, stripes):
    for stripe in stripes:
        fill_stripe(pixel_matrix, stripe[0], stripe[1])




def get_vic_min_max(input_file):
    pixel_matrix, value_pairs = load_vic(input_file)

    pixel_min = np.nanmin(pixel_matrix)
    pixel_max = np.nanmax(pixel_matrix)

    return pixel_min, pixel_max


def vic2tif(input_file, force_input_min=None, force_input_max=None, fill_null_stripes=False):

    pixel_matrix, value_pairs = load_vic(input_file)
    if pixel_matrix is None or value_pairs is None:
        return False

    # Scale to 0-65535 and convert to UInt16
    if force_input_min is not None:
        pixel_min = force_input_min
    else:
        pixel_min = np.nanmin(pixel_matrix)

    if force_input_max is not None:
        pixel_max = force_input_max
    else:
        pixel_max = np.nanmax(pixel_matrix)

    print "Minimum Native:", pixel_min, "Maximum Native:", pixel_max

    if fill_null_stripes is True:
        stripes = detect_null_stripes(pixel_matrix)
        fill_stripes(pixel_matrix, stripes)

    inds = np.where(np.isnan(pixel_matrix))
    pixel_matrix[inds] = pixel_max

    pixel_matrix += abs(pixel_min)
    pixel_matrix *= 65534.0/pixel_max
    pixel_matrix = pixel_matrix.astype(np.uint16)

    output_filename = build_output_filename(value_pairs)
    print "Writing", output_filename

    # Create output tiff
    tiff = TIFFimage(pixel_matrix, description='')
    tiff.write_file(output_filename, compression='none')
    return True


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Input VICAR files", required=True, type=str, nargs='+')
    parser.add_argument("-i", "--intensity", help="Match intensities when stretching", required=False, action="store_true")
    parser.add_argument("-f", "--fill", help="Fill null stripes", required=False, action="store_true")

    args = parser.parse_args()

    input_files = args.data
    match_intensities = args.intensity
    fill = args.fill

    if len(input_files) < 1:
        print "Please specify vicar file to convert"
        sys.exit(1)

    input_min = None
    input_max = None

    if match_intensities is True:
        values = []
        for input_file in input_files:
            vic_min, vic_max = get_vic_min_max(input_file)
            values += [vic_min, vic_max]

        input_min = np.array(values).min()
        input_max = np.array(values).max()

    for input_file in input_files:
        vic2tif(input_file, force_input_min=input_min, force_input_max=input_max, fill_null_stripes=fill)

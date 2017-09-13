
import os
import sys
import numpy as np
from libtiff import TIFFimage
import argparse
import vicar

# This is Cassini-specific!
def build_output_filename(value_pairs):
    PRODUCT_ID = value_pairs["PRODUCT_ID"]
    PRODUCT_ID = PRODUCT_ID[PRODUCT_ID.find("_")+1:PRODUCT_ID.find(".")]
    FILTERS = value_pairs["FILTER_NAME"][1:-1].split(",")

    output_filename = "%s_%s_%s.tif"%(PRODUCT_ID, FILTERS[0], FILTERS[1])

    return output_filename



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
    pixel_matrix, value_pairs = vicar.load_vic(input_file)

    pixel_min = np.nanmin(pixel_matrix)
    pixel_max = np.nanmax(pixel_matrix)

    return pixel_min, pixel_max


def histeq(pixel_matrix, nbr_bins=65536):
    im = pixel_matrix
    imhist, bins = np.histogram(im.flatten(), nbr_bins, normed=True)
    cdf = imhist.cumsum()  # cumulative distribution function
    cdf = 65535 * cdf / cdf[-1]  # normalize

    # use linear interpolation of cdf to find new pixel values
    im2 = np.interp(im.flatten(), bins[:-1], cdf)
    im2 = im2.reshape(im.shape)

    return np.array(im2, np.uint16)

def vic2tif(input_file, force_input_min=None, force_input_max=None, fill_null_stripes=False, fillsat=False, dohisteq=False, minpercent=None, maxpercent=None):

    pixel_matrix, value_pairs = vicar.load_vic(input_file)
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

    if fillsat is True:
        inds = np.where(np.isnan(pixel_matrix))
        pixel_matrix[inds] = pixel_max

    # The min/max percent stuff isn't correct. TODO: Make it correct.
    if minpercent is not None:
        diff = pixel_min + ((pixel_max - pixel_min) * (minpercent / 100.0))
        print "Min:", diff
        pixel_matrix[pixel_matrix < diff] = diff
        pixel_min = diff

    if maxpercent is not None:
        diff = pixel_min + ((pixel_max - pixel_min) * (maxpercent / 100.0))
        print "Max:", diff
        pixel_matrix[pixel_matrix > diff] = diff
        pixel_max = diff

    pixel_matrix = pixel_matrix - pixel_min
    pixel_matrix = pixel_matrix / (pixel_max - pixel_min)
    pixel_matrix[pixel_matrix < 0] = 0

    # Format for UInt16
    pixel_matrix = pixel_matrix * 65535.0
    pixel_matrix = pixel_matrix.astype(np.uint16)
    #print pixel_matrix.min(), pixel_matrix.max()

    if dohisteq is True:
        pixel_matrix = histeq(pixel_matrix)

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
    parser.add_argument("-s", "--fillsat", help="Fill saturated pixels to match max value", required=False, action="store_true")
    parser.add_argument("-e", "--histeq", help="Apply histogram equalization", required=False,action="store_true")
    parser.add_argument("-x", "--maxpercent", help="Clamp values to maximum percent (0-100)", type=float, default=None)
    parser.add_argument("-n", "--minpercent", help="Clamp values to minimum percent (0-100)", type=float, default=None)


    args = parser.parse_args()

    input_files = args.data
    match_intensities = args.intensity
    fill = args.fill
    fillsat = args.fillsat
    dohisteq = args.histeq
    maxpercent = args.maxpercent
    minpercent = args.minpercent

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
        vic2tif(input_file,
                force_input_min=input_min,
                force_input_max=input_max,
                fill_null_stripes=fill,
                fillsat=fillsat,
                dohisteq=dohisteq,
                minpercent=minpercent,
                maxpercent=maxpercent
                )


import argparse
import vicar
import datetime

"""
Pretty basic for now. In the future, allow user to specify desired fields via CLI.
"""
def print_vicar_info(input_file):
    value_pairs = vicar.load_vic(input_file, label_only=True)

    filters = value_pairs["FILTER_NAME"][1:-1].split(",")
    image_time = datetime.datetime.strptime(value_pairs["IMAGE_TIME"], '%Y-%jT%H:%M:%S.%fZ')

    print value_pairs["PRODUCT_ID"], value_pairs["TARGET_NAME"], value_pairs["INSTRUMENT_ID"], image_time, value_pairs["NL"], value_pairs["NS"], filters[0], filters[1]

    #TARGET_NAME
    #INSTRUMENT_ID
    #IMAGE_TIME
    #FILTER_NAME
    #NL
    #NS
    #OBSERVATION_ID
    #PRODUCT_ID




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", help="Input VICAR files", required=True, type=str, nargs='+')

    args = parser.parse_args()

    input_files = args.data

    for input_file in input_files:
        print_vicar_info(input_file)

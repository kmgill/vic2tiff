# vic2tiff
Conversion of calibrated Cassini VICAR files to TIFF format

## How to use

```
usage: vic2tif.py [-h] -d DATA [DATA ...] [-i] [-f] [-s] [-e] [-x MAXPERCENT]
                  [-n MINPERCENT] [-r RESIZE]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA [DATA ...], --data DATA [DATA ...]
                        Input VICAR files
  -i, --intensity       Match intensities when stretching
  -f, --fill            Fill null stripes
  -s, --fillsat         Fill saturated pixels to match max value
  -e, --histeq          Apply histogram equalization
  -x MAXPERCENT, --maxpercent MAXPERCENT
                        Clamp values to maximum percent (0-100)
  -n MINPERCENT, --minpercent MINPERCENT
                        Clamp values to minimum percent (0-100)
  -r RESIZE, --resize RESIZE
                        Resize image to WidthxHeight
```

## Options

`-d <file.cal>` - List of one or more input VICAR files

`-i / --intensity` - Normalizes intensity value stretching across input files

`-f / --fill` - Fills horizontal null stripes using linear interpolation

`-s / --fillsat` - Fills null/nan saturated pixels with a file's maximum valid value

`-e / --histeq` - Performs a histogram equalization on a file

`-x n / --maxpercent n` - Clamps values to the maximum percentage of input values (0 - 100). Values exceeding the limit will be set equal to the value matching that value limit. The new maximum value will be considered when computing the output stretch values.

`-n n / --minpercent n` - Clamps values to the minimum percentage of input values (0 - 100). Values exceeding the limit will be set equal to the value matching that value limit. The new maximum value will be considered when computing the output stretch values.

`-r NNNNxNNNN / --resize NNNNxNNNN` - Scales a file to the specified dimensions (example: 1024x1024). Used bicubic interpolation.


# vicident.py
Prints out basic information about an calibrated Cassini VICAR file. Currently it prints out the image ID, target, instrument, width, height, filter 1, & filter 2. A future revision plans user-selectable fields. 

## How to use
```
usage: vicident.py [-h] -d DATA [DATA ...]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA [DATA ...], --data DATA [DATA ...]
                        Input VICAR files
```

## Example
```
$ python ~/repos/vic2tiff/vicident.py -d *cal

1_N1884017087.122 TITAN ISSNA 1024 1024 CL1 CB3
1_N1884017197.122 TITAN ISSNA 1024 1024 CL1 CB3
1_N1884017307.122 TITAN ISSNA 1024 1024 CL1 CB3
1_N1884017401.123 TITAN ISSNA 1024 1024 CL1 MT1
1_N1884017543.125 TITAN ISSNA 1024 1024 CL1 MT3
1_N1884017605.126 TITAN ISSNA 512 512 CL1 CB1
1_N1884017637.127 TITAN ISSNA 1024 1024 CL1 CB2
1_N1884017731.128 TITAN ISSNA 1024 1024 CL1 MT2
1_N1884017786.130 TITAN ISSNA 1024 1024 RED CL2
1_N1884017841.130 TITAN ISSNA 1024 1024 CL1 GRN
1_N1884017911.130 TITAN ISSNA 1024 1024 BL1 CL2
1_N1884018021.131 TITAN ISSNA 1024 1024 CL1 UV3
1_N1884018579.132 TITAN ISSNA 512 512 UV2 CL2
```

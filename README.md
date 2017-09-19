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

*-d <file.cal>* - List of one or more input VICAR files

*-i / --intensity* - Normalizes intensity value stretching across input files

*-f / --fill* - Fills horizontal null stripes using linear interpolation

*-s / --fillsat* - Fills null/nan saturated pixels with a file's maximum valid value

*-e / --histeq* - Performs a histogram equalization on a file

*-x n / --maxpercent n* - Clamps values to the maximum percentage of input values. (0 - 100)

*-n n / --minpercent n* - Clamps values to the minimum percentage of input values. (0 - 100)

*-r NNNNxNNNN / --resize NNNNxNNNN* - Scales a file to the specified dimensions (example: 1024x1024). Used bicubic interpolation.

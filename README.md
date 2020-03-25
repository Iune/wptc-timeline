# `wptc-timeline`

This is a simple Python program to parse the National Hurricane Center (NHC) historical tropical cyclone tracking data, which is stored in the `hurdat2` format, and identify the closest NHC warning breakpoint to each record in the tracking data.

## Usage

```
usage: timeline.py [-h] [-i INPUT] [-o OUTPUT] -y YEAR

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input hurdat2 file location
  -o OUTPUT, --output OUTPUT
                        Output tsv file location
  -y YEAR, --year YEAR  Year to process
```
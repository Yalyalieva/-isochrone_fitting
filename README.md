Package for astronomical practicum.

# Dependencies

You need the following pthon packages:

- `PyQt5`:
```bash
pip install PyQt5
```

- `matplotlib`:
```bash
pip install matplotlib
```

- `numpy`:
```bash
pip install numpy
```

- `pandas`:
```bash
pip install pandas
```
- `scipy`:
```bash
pip install SciPy
```

# Run

```bash
python isochron_fitting.py
```

# Hotkeys:

A Z - shift the isochrone along the ordinate axis
, . - shift the isochrone along the abscissa axis
N P - change the age of the isochrone

[ ] - change the step along the ordinate axis
; ' - change the step along the abscissa axis

( ) - change the number of points on the density plot

The data file must contain three columns: the distance of the star from the center of the cluster, stellar magnitude, and color.
The file should not have a header with column names (or they should be commented out with '#', like in the example file 'ngc225_jjh.csv').

# Loading new isochrones.

Click the "Load new theoretical isochrones" button.

In the dialog box that appears, select a file using the "Upload" button.
File structure: 3 columns, the first - logt, the second - stellar magnitude, the third - color.

There should be no column names in the file, or they should be commented out with '#'.

Fill in the data about the isochrones.

Example: To load isochrones (J,J-H) with a metallicity of 0.02,
corresponding to the filters of the 2MASS survey. Fill in the fields as follows:

J Filter

Color J-H

2mass filter system

Metallicity 0.02
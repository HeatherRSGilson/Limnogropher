# Limnogropher v0.1
Provided with a greyscale heightmap, Limnogropher will generate an image overlayed with paths representing rivers procedurally generated based on elevation.

# Dependencies
Python 3.12.4

pillow 10.4.0

numpy 2.1.0

# Usage
This project currently only provides the class and functions without an interface. An example of the usage is provided in the ./src/test folder. 

# TODO
- Improve in-file documentation (doc-strings, inline, type hints...)
- Implement user interface
- Add additional parameters to functions for increased customizability (filters & further preprocessing, color space reduction)
- Finish aridity functionality (currently a map may be provided, but it is not used in calculation of source generation)
- Add output options (rivers only, etc.)

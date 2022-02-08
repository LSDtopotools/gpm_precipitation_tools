=======================
gpm_precipitation_tools
=======================


.. image:: https://img.shields.io/pypi/v/gpm_precipitation_tools.svg
        :target: https://pypi.python.org/pypi/gpm_precipitation_tools

.. image:: https://img.shields.io/travis/LSDtopotools/gpm_precipitation_tools.svg
        :target: https://travis-ci.com/LSDtopotools/gpm_precipitation_tools

.. image:: https://readthedocs.org/projects/gpm-precipitation-tools/badge/?version=latest
        :target: https://gpm-precipitation-tools.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status



Package for downloading and analysing NASA Global Precipitation Measurement mission data.

This tool is an adapted version of the PPTs_ tool developed by Vinicius Mesquita. It was modified from the original code by Marina Ruiz Sánchez-Oro (University of Edinburgh - School of GeoSciences) and Guillaume Goodwin (University of Edinburgh - School of GeoSciences, now in University of Padova). It offers less flexibility than the original PPTs tool and focuses on downloading rainfall data from GPM instead of offering various data sources. It contains an additional module to generate time-series of rainfall intensity in over a specified area of interest.


* Free software: MIT license
* Documentation (in progress): https://gpm-precipitation-tools.readthedocs.io.

Accessing data
-----------------


Before you try to download any data, ensure that you have created an account at the NASA Earth Data website_.

Make a login and password, click in Applications>Authorized Apps> Approve More Applications and select NASA GESDISC DATA ARCHIVE.

You will be prompted for the username and the password every time you download the data using this package.


Usage
--------

Install the ``gpm_precipitation_tools`` package:

``pip install gpm_precipitation_tools``

Using the package:

Open ``python`` or type in a python script:

``import gpm_precipitation_tools``

To download and pre-process the precipitation data:

``gpm_precipitation_tools.PPT_CMD_RUN.main() --ProdTP XXX --StartDate %Y-%m-%d --EndDate %Y-%m-%d --ProcessDir XXX --SptSlc XXX``

To process the precipitation data and convert into timeseries or raster:

``gpm_precipitation_tools.process_timeseries_files_pipeline.main() --file_folder XXX --crs EPSG:XXXX --x_lon XX --y_lat YY --time %Y-%m-%d:%H%M%S``

Where,

**--ProdTP** = 'GPM_30min' (default)

GPM_30min: GPM half-hourly (IMERGM v6)
GPM_D: GPM daily (IMERGM v6)
GPM_M: GPM monthly (IMERGM v6)

**--StartDate** = Insert the start date (format %Y-%M-%D)

**--EndDate** = Insert the end date (format %Y-%M-%D)

**--ProcessDir** = Insert the processing directory path

**--SptSlc** = Insert the cutline feature path (if not used, it assumes a global product)

**--OP** = Call this argument if you already have the data and want to process it. Make sure you have a directory with a raw files subfolder!!!!

**--file_folder** = Folder where the data to analyse lives.

**--crs** = Coordinate system in format EPSG:XXXX.

**--x_lon** = Longitude coordinate of the point of interest.

**--y_lat** = Latitude coordinate of the point of interest.

**--time** = Time of interest (format: %Y-%m-%d:%H%M%S)

Credits
-------
This package is based on the code_ from Vinicius Mesquita, and has been adapted by Guillaume Goodwin (University of Edinburgh/ Universita di Padova) and Marina Ruiz Sánchez-Oro (University of Edinburgh).

.. _code: https://github.com/lapig-ufg/PPTs
.. _PPTs: https://github.com/lapig-ufg/PPTs

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

.. _website: https://urs.earthdata.nasa.gov

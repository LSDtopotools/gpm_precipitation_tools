#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['numpy','pandas','rasterio','scipy','fiona','geopandas','pyproj','gdal','utm','matplotlib', 'shapely','rioxarray','xarray', 'PyQt5']

test_requirements = [ ]

setup(
    author="Marina Ruiz Sanchez-Oro",
    author_email='marina.ruiz.so@ed.ac.uk',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Package for downloading and analysing NASA Global Precipitation Measurement mission data.",
    entry_points={
        'console_scripts': [
            'PPT_CMD_RUN=gpm_precipitation_tools.PPT_CMD_RUN:main',
            'process_timeseries_files_pipeline=gpm_precipitation_tools.process_timeseries_files_pipeline:main'
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='gpm_precipitation_tools',
    name='gpm_precipitation_tools',
    packages=find_packages(include=['gpm_precipitation_tools']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/LSDtopotools/gpm_precipitation_tools',
    version='0.4.1',
    zip_safe=False,
)

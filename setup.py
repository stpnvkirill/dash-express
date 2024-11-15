# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dash_express",
    version="1.2.0",                     
    author="Kirill Stepanov",
    author_email="stpnv.kirill.o@gmail.com",
    description="A tool for faster application development Plotly Dash",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[                      
        "dash>=2.11.1",
        "pandas>=2.0.3",
        "orjson>=3.9.2",
        "dash_iconify==0.1.2",
        "dash_leaflet==0.1.28",
        "flask_caching>=2.0.2",
        "dash_mantine_components==0.12.1"                                        
    ],                                             
    url="https://github.com/stpnvkirill/dash-express",
    packages=setuptools.find_packages(),
    classifiers=(                                 
        "Programming Language :: Python :: 3",    
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",   
    ),
)
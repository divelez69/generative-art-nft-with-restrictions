#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import time
import os
from progressbar import progressbar
import json
from copy import deepcopy

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Please: Check in config.py general settings and parameters
from config import JSON_DIR, ZEROS_PAD

# Base metadata. MUST BE EDITED.
# ----------------------------------------------
# The base metadata will depend on the blockchain and plattform you use to deploy your NFTs
# The original script from Rounak Banik complies with OpenSea metadata requirements.
# Therefore, I leave it here in comment mode for your refference:


# BASE_IMAGE_URL = "ipfs://<-- Your CID Code-->"
# BASE_NAME = ""

# BASE_JSON = {
#     "name": BASE_NAME,
#     "description": "",
#     "image": BASE_IMAGE_URL,
#     "attributes": [],
# }

# ----------------------------------------------
# On the other hand, I had to adapt the code to comply with Lighthouse tool and WeBump whose NFTs are deployed on the SEI network.
# These plus other adjustments I had to do. I invite you to read the README.md about them, specially about important imporovements I made to the original script.
# 
# Base metadata for Lighthouse. It must be edited too:

BASE_NAME = "Scrappy Squirrel #"

BASE_JSON = {
    "name": BASE_NAME,
    "symbol": "SSQ",
    "description": "The most fun and bizarre squirrels of misty forest",
    "image": "",
    "edition": None,
    "attributes": [],
}

# ----------------------------------------------

# Get metadata and JSON files path based on edition
def generate_paths(edition_name):
    edition_path = os.path.join('output', 'edition ' + str(edition_name))
    metadata_path = os.path.join(edition_path, 'metadata.csv')
    json_path = os.path.join(edition_path, JSON_DIR)

    return edition_path, metadata_path, json_path

# Function to convert snake case to sentence case
def clean_attributes(attr_name):
    
    clean_name = attr_name.replace('_', ' ')
    clean_name = list(clean_name)
    
    for idx, ltr in enumerate(clean_name):
        if (idx == 0) or (idx > 0 and clean_name[idx - 1] == ' '):
            clean_name[idx] = clean_name[idx].upper()
    
    clean_name = ''.join(clean_name)
    return clean_name


# Function to get attribure metadata
def get_attribute_metadata(metadata_path):

    # Read attribute data from metadata file 
    df = pd.read_csv(metadata_path)
    df = df.drop('Unnamed: 0', axis = 1)
    df.columns = [clean_attributes(col) for col in df.columns]

    # If zeros padd set to True...
    # Get zfill count based on number of images generated
    # -1 according to nft.py. Otherwise not working for 100 NFTs, 1000 NTFs, 10000 NFTs and so on
    zfill_count = len(str(df.shape[0]-1)) if ZEROS_PAD else None

    # Note: The zeros filling is part of the original code by rounakbanik
    # I found out that Lighthouse tool required not to have those zeros filled.
    # Therefore, I made this as a parameter 'ZEROS_PAD' to set in config.py
    #

    return df, zfill_count

# Main function that generates the JSON metadata
def main():

    # Get edition name
    print("Enter edition you want to generate metadata for: ")
    while True:
        edition_name = input()
        edition_path, metadata_path, json_path = generate_paths(edition_name)

        if os.path.exists(edition_path):
            print("Edition exists! Generating JSON metadata...")
            break

        else:
            print("Oops! Looks like this edition doesn't exist! Check your output folder to see what editions exist.")
            print("Enter edition you want to generate metadata for: ")
            continue
    
    # Make json folder
    if not os.path.exists(json_path):
        os.makedirs(json_path)

    # Get attribute data and zfill count (if it's the case)
    df, zfill_count = get_attribute_metadata(metadata_path)
    
    for idx, row in progressbar(df.iterrows()):    
    
        # Get a copy of the base JSON (python dict)
        item_json = deepcopy(BASE_JSON)
        
        # Append number to base name 
        item_json['name'] = item_json['name'] + str(idx)

        # Append image PNG file name to base image path
        item_json['image'] = \
            item_json['image'] + '/' + \
            (str(idx).zfill(zfill_count) if ZEROS_PAD else str(idx)) + \
            '.png'

        # Insert number to edition: Is added for the Base Metadata for Lighthouse
        item_json['edition'] = idx
        
        # Convert pandas series to dictionary
        attr_dict = dict(row)
        
        # Add all existing traits to attributes dictionary
        for attr in attr_dict:
            
            if attr_dict[attr] != 'none':
                item_json['attributes'].append({ 'trait_type': attr, 'value': attr_dict[attr] })
        
        # Write file to JSON_DIR folder
        # The original code lacks the adition of the '.json' extension
        item_assets_path = os.path.join(
            json_path, 
            (str(idx).zfill(zfill_count) if ZEROS_PAD else str(idx)) + ".json"
            )
        
        with open(item_assets_path, 'w') as f:
            json.dump(item_json, f)

# Run the main function
main()

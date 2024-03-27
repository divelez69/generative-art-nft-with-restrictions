"""
This file MUST be configured in order for the code to run properly.
PLEASE READ CAREFULLY

Make sure you put all your input images into an 'assets' folder. You can change the folder's name in the global ASSETS_DIR if you wish.
Each layer (or category) of images must be put in a folder of its own.

CONFIG is an array of objects where each object represents a layer
THESE LAYERS MUST BE ORDERED.

Each layer needs to specify the following:

    1.  id: A number representing a particular layer

    2.  name: The name of the layer. Does not necessarily have to be the same as the directory name containing the layer images.

    3.  directory: The folder inside assets that contain traits for the particular layer.

    4.  required: If the particular layer is required (True) or optional (False). The first layer must always be set to true.

    5.  rarity_weights: Denotes the rarity distribution of traits. It can take on four types of values:

        - None: This makes all the traits defined in the layer equally rare (or common)

        - "random": Assigns rarity weights at random.

        - array: An array of numbers where each number represents a weight.

            => If required is True, this array must be equal to the number of images in the layer directory. The first number is  the weight of the first image (in alphabetical order) and so on...

            => If required is False, this array must be equal to one plus the number of images in the layer directory. The first number is the weight of having no image at all for this layer. The second number is the weight of the first image and so on...

        - "file": extracts rarity weights from a CSV file located within the “rarity weights” folder. Here's how it works:

            The CSV filename must match the layer's name. For instance, if the layer is named “Body”, the corresponding CSV file should be named “Body.csv”. If the script cannot find the specified CSV file, it will create one automatically. In this case, it assigns a weight value of one (1) to all traits, including 'None' if applicable. This convenient feature allows users to generate all necessary CSV files during the initial script run. Later, they can edit these files according to their preferences. On subsequent runs, once the CSV files are correctly set up, they can devote entirely to the avatars creation.
            
            Take notice of:

                => The number of traits within the CSV depends on how the 'required' flag is set. If it's set to True, then the number of traits must match the count of traits in the layer's category. However, if it's set to False, the CSV should include one additional 'none' trait.

                => The trait names within the CSV file should match the corresponding trait filenames in the 'assets' folder, but re-styled to 'Title Style'. Don't worry, the script does the re-styling for you. However, once CSVs are created don't modify the 'Traits', otherwise it won't be able to read the data. You should focus only on the rarity weigths.

Be sure to check out the tutorial in the README for more details.                
"""

#==============================================================================================
# ABOUT PUBLIC AND GLOBAL VARIABLES USED ACROSS THE WHOLE SET OF SCRIPTS:
#----------------------------------------------------------------------------------------------
# Input image traits must be placed in the assets folder whose name is stored in ASSETS_DIR.
ASSETS_DIR = 'assets'

# This tool deploys the production of images and its metadata in the 'output' folder.
# The nft.py script deploys the PNGs in the IMGS_DIR while metadata.py script deploys the json files in JSON_DIR.
# You can change the output folders in the globlas IMGS_DIR and JSON_DIR if you need.
# Both directories can have the same name if you wish.
IMGS_DIR = 'images'
JSON_DIR = 'json'

# By default, when ZEROS_PAD is set to True, images and json files are named 000, 001, 002...
# If set to False, they will be named: 0, 1, 2, ...
ZEROS_PAD = True

# Note: The original code written by rounakbanik fills the zeros: 0000, 0001, 0002... etc.
# However, when using this tool to create NFTs to deploy with Lighthouse tool on the SEI network I had to remove the zeros.
# WeBump requires to upload images and metadata to Arweave, and the smart contract is referenced to images once located there. 
# The zeros filled couldn't be referenced, but they were once the zeros were removed.
# 
# When launching your own project you'll encounter your own challenges impossible to detect in advance. 
# I heartly hope this remarkable code (thanks to rounakbanik) and the improvements I made will be of good help on your projects.
# ----------------------------------------

CONFIG = [
    {
        'id': 1,
        'name': 'Background',
        'directory': 'Background',
        'required': True,
        'rarity_weights': None
    },
    {
        'id': 2,
        'name': 'Accessory Behind',
        'directory': 'Accessory Behind',
        'required': False,
        'rarity_weights': 'file'
    },
    {
        'id': 3,
        'name': 'Body',
        'directory': 'Body',
        'required': True,
        'rarity_weights': [2, 1]
    },
    {
        'id': 4,
        'name': 'Head',
        'directory': 'Head',
        'required': False,
        'rarity_weights': 'random'
    },
    {
        'id': 5,
        'name': 'Clothing',
        'directory': 'Clothing',
        'required': False,
        'rarity_weights': None
    },
    {
        'id': 6,
        'name': 'Mouth',
        'directory': 'Mouth',
        'required': True,
        'rarity_weights': 'file'
    },
    {
        'id': 7,
        'name': 'Eyes',
        'directory': 'Eyes',
        'required': True,
        'rarity_weights': 'random'
    },
    {
        'id': 8,
        'name': 'Front Accessory',
        'directory': 'Front Accessory',
        'required': False,
        'rarity_weights': [5, 1]
    },
]
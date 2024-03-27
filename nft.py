#!/usr/bin/env python
# coding: utf-8

# Import required libraries
import sys
import math
from PIL import Image
import pandas as pd
import numpy as np
import time
import os
import random
from progressbar import progressbar

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from restriction_code import parse_restrictions, setup_restrictions, fix_trait, is_valid_trait, title_style

# These are general settings imports. Please review them in config.py
from config import CONFIG, ASSETS_DIR, IMGS_DIR, ZEROS_PAD

# GLOBALS:
RESTRICTIONS = {} # It will be updated with final restrictions' workable dictionary

# To minimize missmatches, trait name references within RESTRICTIONS and
# PNG trait filenames are re-styled to 'Title Style'
# The following map will relate the real PNG filename with its re-styled trait name
# Its structure:
#   {
#       'name_1': {'Trait Name 1': 'trait name 1.png, 'Trait Name 2': 'trait name 2.png'... }
#       'name_2': {'Trait Name 1': 'trait name 1.png, 'Trait Name 2': 'trait name 2.png'... }
#       ...
#   }
trait_file = {}


# Parse the configuration file and make sure it's valid
def parse_config():

    # Collect new CSVs if recently created
    new_CSVs = []

    # Loop through all layers defined in CONFIG
    for layer in CONFIG:

        # Improve the aesthetic as it is going to be shown in the metadata
        layer['name'] = title_style(layer['name'])

        # Go into assets/ to look for layer folders
        layer_path = os.path.join(ASSETS_DIR, layer['directory'])
        
        # Make a reference of fixed and re-styled trait names to PNG trait filenames
        trait_name = {
            title_style(fix_trait(tr_file)): tr_file \
                for tr_file in os.listdir(layer_path) if is_valid_trait(tr_file, layer_path)
        }

        # Update map: re-styled trait names to corresponding PNG trait filenames
        trait_file[layer['name']] = trait_name

        # Get trait (in 'Title Style') array in sorted order
        traits = sorted(trait_name.keys())

        # If layer is not required, add a None to the start of the traits array
        if not layer['required']:
            traits = [None] + traits
        
        # Generate final rarity weights
        if layer['rarity_weights'] is None:
            rarities = [1 for x in traits]
        elif layer['rarity_weights'] == 'random':
            rarities = [random.random() for x in traits]
        elif layer['rarity_weights'] == 'file':

            # Get rarities from a CSV file
            rarities, new_csv = get_rarities_from_csv(layer, traits)
            
            # Collect CSV filename only if newly created
            if new_csv:
                new_CSVs.append(new_csv)

        elif type(layer['rarity_weights'] == 'list'):
            assert len(traits) == len(layer['rarity_weights']), "Make sure you have the current number of rarity weights"
            rarities = layer['rarity_weights']
        else:
            raise ValueError("Rarity weights is invalid")
        
        rarities = get_weighted_rarities(rarities)
        
        # Re-assign final values to main CONFIG
        layer['rarity_weights'] = rarities
        layer['cum_rarity_weights'] = np.cumsum(rarities)
        layer['traits'] = traits

    return new_CSVs


# "get_rarities_from_csv" helper function:
# Look for all possible 'none', 'nonE', 'noNe', ...'NONE' as keys and extract the first value found
def get_value_from_none_key(wd):

    # Transform input binary number into its equivalent: 0000 => none, 0001 => nonE, 0010 => noNe, etc
    get_non_str = lambda b: ''.join([c if b[j] == '0' else c.upper() for j, c in enumerate('none')])

    # Parse the 16 in binaries: 0000, 0001, 0010, ...1111
    for i in range(16):

        # Get a form of 'none' given a binary number from 0 to 15 
        none_str = get_non_str('{0:04b}'.format(i))

        # Extract and return the first 'none' key found's value
        try:
            return wd[none_str]
        except Exception:
            continue

    else:
        raise KeyError("Not any 'none' found")


# Get rarity weights from CSV file
def get_rarities_from_csv(layer, traits):

    # Rarities CSVs folder
    rar_dir = 'rarity weights'

    # Create the rarities folder if it doesn't exist. If it does, make sure is a folder
    if not os.path.exists(rar_dir):
        os.mkdir(rar_dir)
    elif not os.path.isdir(rar_dir):
        raise NotADirectoryError("'%s' exists and isn't a directory. Please delete or rename it." % rar_dir)
    
    # CSV filepath:
    csv_filename = layer['name'] + '.csv' 
    csv_file_path = os.path.join(rar_dir, csv_filename)

    # Make a new CSV file if it doesn't exist
    if not os.path.exists(csv_file_path):

        # Export to a CSV
        df = pd.DataFrame(['none'] + traits[1:] if traits[0] is None else traits, columns = ['Trait'])
        df['Weight'] = 1
        df.to_csv(csv_file_path, index=False)

        # Return all traits with a preloaded default value of 1 + the new CSV filename
        return [1] * len(traits), csv_filename

    # A CSV is found. Read the file and extract the weights
    try:
        df = pd.read_csv(csv_file_path, na_filter=False)
        wd = dict(zip(df['Trait'], df['Weight']))

    except Exception as e:
        err_msg = "%s: Failed to extract rarity weights from '%s'. The file may be corrupted. Consider erasing the CSV and run this script again to create a new one from scratch."  % (str(e), csv_filename)
        raise type(e)(err_msg)
    
    err_msg =  "The number of rarity weights extracted from '%s.csv' doesn't match current project.\nEdit the csv file or consider erasing it and run the script again to create a new one from scratch." % csv_filename
    assert len(traits) == len(wd), err_msg

    # Initialize a weights list with the weight value corresponding to a 'None' if exists
    try:
        weights = [ get_value_from_none_key(wd) ]
    except KeyError:
        weights = []
        init = 0
    else:
        init = 1
    
    # Extract the rest of the weights in sorted order
    missmatch = [] # <-- collect here the missmatches
    for trait in sorted(traits[init:]):
        try:
            # Traits must match the CSVs Trait
            weights.append( wd[trait] )
        except KeyError:
            # Collect the missmatch
            missmatch.append(trait)

    err_msg = "Some of the trait names in the '%s' didn't match with the traits in the '%s' folder. These are '%s'. Seems the CSV has been corrupted. Consider to delete it and run the script again to build a new one from scratch. Save previous weight's data before proceeding." \
        % (csv_filename, ASSETS_DIR, "', '".join(missmatch))
    assert len(missmatch) == 0, err_msg

    # Return the extracted weights and None, because it's not a new CSV file
    return weights, None


# Weight rarities and return a numpy array that sums up to 1
def get_weighted_rarities(arr):
    return np.array(arr)/ sum(arr)


# Generate a single image given an array of filepaths representing layers
def generate_single_image(filepaths, output_filename=None):
    
    # Treat the first layer as the background
    bg = Image.open(os.path.join(ASSETS_DIR, filepaths[0]))
    
    # Loop through layers 1 to n and stack them on top of another
    for filepath in filepaths[1:]:
        if filepath.endswith('.png'):
            img = Image.open(os.path.join(ASSETS_DIR, filepath))
            bg.paste(img, (0,0), img)
    
    # Save the final image into desired location
    if output_filename is not None:
        bg.save(output_filename)
    else:
        # If output filename is not specified, use timestamp to name the image and save it in output/single_images
        if not os.path.exists(os.path.join('output', 'single_images')):
            os.makedirs(os.path.join('output', 'single_images'))
        bg.save(os.path.join('output', 'single_images', str(int(time.time())) + '.png'))


# Get total number of distinct possible combinations
def get_total_combinations():
    
    total = 1
    for layer in CONFIG:
        total = total * len(layer['traits'])
    return total


# Select an index based on rarity weights
def select_index(cum_rarities, rand):
    
    cum_rarities = [0] + list(cum_rarities)
    for i in range(len(cum_rarities) - 1):
        if rand >= cum_rarities[i] and rand <= cum_rarities[i+1]:
            return i
    
    # Should not reach here if everything works okay
    return None


# Generate a set of traits given rarities
def generate_trait_set_from_config():
    
    trait_set = []
    
    for layer in CONFIG:
        # Extract list of traits and cumulative rarity weights
        traits, cum_rarities = layer['traits'], layer['cum_rarity_weights']

        # Generate a random number
        rand_num = random.random()

        # Select an element index based on random number and cumulative rarity weights
        idx = select_index(cum_rarities, rand_num)

        # Add selected trait to trait set
        trait_set.append(traits[idx])

    return trait_set


# Get the corresponding traits paths set from given traits set
def generate_paths_set_from_traits(traits_set):
    traits_path = []
    for idx, trait in enumerate(traits_set):

        # skip the none trait. There's no PNG equivalent
        if (trait.lower() != 'none') and (trait is not None):
            trait_path = os.path.join(CONFIG[idx]['directory'], trait_file[CONFIG[idx]['name']][trait])
            traits_path.append(trait_path)

    return traits_path


# Validate image's trait set: Image should not break a rule. Return True if it does!
def is_image_invalid(row):
    
    # Get the names and traits from pandas series row arg
    traits_set = dict(zip(row.index, row))
    names = set(traits_set.keys())

    # Loop all given traits one by one
    for name, trait in traits_set.items():

        # Check if current trait imposed restrictions on others
        if name in RESTRICTIONS and trait in RESTRICTIONS[name]:

            # Get affected name/trait pairs by current trait
            restricted_names = RESTRICTIONS[name][trait]

            # Loop other traits from current image and check if they're affected 
            for other_name in names - {name}:

                if other_name in restricted_names:

                    # A red flag raised. Look further
                    restr_traits = restricted_names[other_name]
                    other_trait = traits_set[other_name]

                    if restr_traits['Restrict All'] and other_trait != "none":
                        return True
                    
                    if other_trait in restr_traits['Restricted']:
                        return True

    # No rule violated!                
    return False


# Generate a table of raw data images based on random traits
def generate_imgs_table(count, prog_bar=False):

    # The table size won't be equal to 'count' since it'll be purged
    # 'prog_bar' is to inform the advanced of the operation...
    # ...however, since first samples are small, no need to inform, hence 'prog_bar' is False

    # Initialize an empty rarity table
    rarity_table = {}
    for layer in CONFIG:
        rarity_table[layer['name']] = []

    # Wrap iterator range object with other iterator if prog_bar given
    iter_obj = lambda rng_obj: progressbar(rng_obj,) if prog_bar else rng_obj
      
    # Generate traits rows data. Images not yet
    for _ in iter_obj(range(count)):

        # Get a random set of valid traits based on rarity weights
        trait_sets = generate_trait_set_from_config()

        # Populate the rarity table with metadata of newly created image
        for idx, trait in enumerate(trait_sets):
            if trait is not None:
                rarity_table[CONFIG[idx]['name']].append(trait)
            else:
                rarity_table[CONFIG[idx]['name']].append('none')

    # Inform user of task advance if prog_bar given
    if prog_bar:
        init_time = time.time()
        print("Depurating table from duplicates and non-valid avatars. This may take a while. Please be patient...")

    # Create a Data Frame
    rarity_table = pd.DataFrame(rarity_table)

    # Check and remove invalid images (the ones that violate any rule)
    invalid_imgs = rarity_table.apply(is_image_invalid, axis=1)
    invalid_imgs = invalid_imgs[invalid_imgs]
    rarity_table.drop(invalid_imgs.index, inplace=True)

    # Drop duplicates
    rarity_table.drop_duplicates(inplace=True)

    # Inform user the end of task if prog_bar given
    if prog_bar:
        end_time = time.time()
        print("...depuration completed in %s seconds!" % ("{:2.2f}".format(end_time - init_time)))

    return rarity_table


# Generate table with exact number of request data images, all distinct and depurated
def generate_exact_imgs_table(count):
    """
    To create a table with an exact number of requested data images (all distinct and purified), we must gather preliminary statistics. This step is crucial, especially when handling requests for hundreds of thousands or even millions of avatar images.

    In the previous script version, the entire image set was generated first, followed by the purification process. However, image production is significantly more computationally expensive than creating a trait-based dataset. Moreover, images are unnecessary for purging repetitions and bad images that do not comply with the RESTRICTIONS_CONFIG settings. All we need to accomplish the task is the raw data's table of trait sets.

    The assertion rate of valid images varies unpredictably based on the complexity of the restrictions settings. Therefore, before embarking on the production of a traits dataset on a large scale, it is advisable to assess the complexity using small samples. This function achieves precisely that. It tests ten samples, each containing one thousand data images, to measure the assertion rate before generating the entire set. Armed with these firsthand statistics, we can confidently request the necessary oversized image data table, ensuring that after depuration, we achieve the requested size with an accuracy of 97.5%.
    """

    # For statistics:
    n = 10     # --> Number of samples
    m = 1000   # --> Number of traits dataset per sample (table)
    results = [] # --> Collect n assertion rates per sample

    # Initialize an empty table: It'll append each new table as it's been produced
    master_rt = pd.DataFrame()

    # Generate n tables to collect their assertion rates
    for _ in range(n):

        # Generate a table of m images (rows)
        # The resulting table will have only the valid traits datasets after depuration
        rt = generate_imgs_table(m)

        # Concatenate current table with master one... thus not wasting previous job
        master_rt = pd.concat([master_rt, rt])

        # master table may be the final if it has more traits set than requested
        if master_rt.shape[0] >= count:

            # If after dropping duplicates, still have more than requested. Just use it!
            master_rt.drop_duplicates(inplace=True)
            if master_rt.shape[0] >= count:
                break

        # Collect the statistic: The percentage rate of assertion
        results.append(rt.shape[0] / m)

    else:

        # Get the stats
        results = np.array(results)
        mean = np.mean(results)
        stDev = np.std(results)

        if mean == 0.0:
            print()
            print("Failed to generate images!")
            print("Restrictions settings (in RESTRICTIONS_CONFIG) are impossible to comply:")
            print("From %i attempts, no single image was able to generate." % (n * m))
            print("Take a deeper look to RESTRICTIONS_CONFIG settings and loose them up.")
            print("Execution aborted!")
            quit()

        elif mean < 0.05:

            # Less than 5% of assertion rate!
            print()
            print("WARNING:")
            print("From %i attempts it was only able to generate %s%% images." % (n * m, "{:2.2f}".format(mean * 100.0)))
            print("The total generation of %s images may fail or consume a lot of time and resources." % count)
            print("There might be not enough traits to make distinct combinations, or restrictions settings (in RESTRICTIONS_CONFIG) are very tough. It'll be recommended to make a deep review of them.")
            print()
            
            while True:
                resp = input("Despite warnings, do you want to continue Y/N?")
                
                if resp.lower() == 'y':
                    print("Ok, let's try!...")
                    break

                elif resp.lower() == 'n':
                    print("Execution aborted!")
                    quit()

        # Try up to 10 times to get the missing traits dataset to fill the 'count' requested
        for i in range(10):

            # Get the size for next table.
            next_table_size = math.ceil((count - master_rt.shape[0]) / (mean - 2 * stDev))

            print("We have already %i distintict and aproved avatars." % (master_rt.shape[0]))
            print("Due to an assertion rate of {:.2f}%, we have to generate {} aditional image data to fulfill the {} requested."\
                  .format(mean * 100, next_table_size, count))
            print("Remember that not all data images generated are incorpotated, because some are duplicates or fail to pass the restriction rules.")
            print("We have a 97.50% probability to acomplish the goal in the next atempt.")
            print()
            print("Attempt %i of 10: Generating %i new images data..." % (i + 1, next_table_size))

            # Generate the next table and concatenate to the master one
            # With given stats, we expect 97.5% chances to get enough depurated traits dataset in the first attempt
            rt = generate_imgs_table(next_table_size, True)
            master_rt = pd.concat([master_rt, rt])
            master_rt.drop_duplicates(inplace=True)

            # Check if we reach the goal
            if master_rt.shape[0] >= count:
                print()
                break

            else:

                # Didn't reach the goal.
                # This is a rare 2.5% case of failing in previous attempt 
                # However, the newly traits dataset have been integrated
                # Try again only for the remaing. 
                # There's a 97.5% chance that next iteration will fullfill
                print("Last generated table wasn't enough to produce the avatar images requested.")
                print()

        else:

            # It fails to get the missing data. Is virtually impossible.
            print("After 10 attempts it wasn't possible to generate a table for all images required.")
            print("Only %i distinct and valid images will be be produced." % master_rt.shape[0])
            print()

    # Modify final rarity table to reflect removals
    master_rt.reset_index(inplace=True)
    master_rt.drop('index', axis=1, inplace=True)

    # Chop the excess of rows so to match to requested 'count'
    master_rt.drop(master_rt[master_rt.index>= count].index, inplace=True)

    return master_rt


# Generate the image set
def generate_images(edition, count):

    # Define output path to output/edition {edition_num}
    op_path = os.path.join('output', 'edition ' + str(edition), IMGS_DIR)

    # Create output directory if it doesn't exist
    if not os.path.exists(op_path):
        os.makedirs(op_path)

    # Generate a table with exact 'count' rows, distinct and valid avatar imgs.
    # No further depuration is required
    rarity_table = generate_exact_imgs_table(count)

    # Adjust the number of expected images if complete required table generation fails 
    if rarity_table.shape[0] < count:
            count = rarity_table.shape[0]

    # Will require this to name final images as 000, 001,...
    # later on, these zeros will be removed if Zeroes Padding is set to False
    zfill_count = len(str(count - 1))

    print("Generating %s images..." % count)

    # Loop the table (dataframe)
    iter_rows = rarity_table.iterrows()
    for _ in progressbar(range(rarity_table.shape[0])):

        # Get next row with data and extract the depurated traits
        row = next(iter_rows)
        trait_set = list(row[1])

        # Get the corresponding PNG paths of traits
        trait_paths = generate_paths_set_from_traits(trait_set)

        # Generate next image filename
        img_name = str(row[0]).zfill(zfill_count) + '.png'
        
        # Generate the actual image
        generate_single_image(trait_paths, os.path.join(op_path, img_name))

    if not ZEROS_PAD:
        # Remove the zeros at the left of the PNG new avatar filename
        # Some tools like Lighthouse require to remove the zeros padding

        for filename in os.listdir(op_path):
            if filename.startswith('0'):

                # Remove the '0's padding of all PNG avatars...
                new_filename = filename.lstrip('0')

                # ...except the '0.png' filename
                if new_filename == '.png':
                    new_filename = '0' + new_filename

                # Rename the filenames
                os.rename(os.path.join(op_path, filename), os.path.join(op_path, new_filename))

    return rarity_table


# New CSVs require user to be alerted
def manage_new_CSVs(new_csvs):

    if not new_csvs:

        # No new CSVs created. So rarity weights must be fine
        print("Assets look great! Let's continue!")
        print()
        return

    print("Assets are fine, but new rarity-weights' CSV files has been created.")
    print()
    print("These are: '%s'" % "', '".join(new_csvs))
    print()
    print("By default, weights in all CSV traits have been assign with the value of 1.")
    print("You may wish to edit them before continue with the avatars creation.")
    print()

    # Get a response from user
    while True:
        resp = input("Despite the advice, do you want to continue? (Y/N)")
        if resp.lower() == 'y':
            break # user decided to keep with the task

        elif resp.lower() == 'n':
            print("Execution aborted!")
            quit()
        

# Main function. Point of entry
def main():

    # Prepare traits information and rarities weights
    print("Checking assets...")
    new_CSVs = parse_config()

    # Manage properly if new CSVs have been created
    manage_new_CSVs(new_CSVs)

    print("Checking the restriction file...")
    parse_restrictions()
    print("Restrictions configuration is all good! We are now good to go!")
    print()

    print("Setting up RESTRICTIONS_CONFIG and looking for warnings and issues...")
    RESTRICTIONS.update(setup_restrictions())

    tot_comb = get_total_combinations()
    print("A total of %i of distinct trait combinations has been calculated.\nNot all of them can be transformed into avatars."  % (tot_comb))
    print("The output number will be less, and it will depend on the severity of the 'RESTRICTIONS_CONFIG' settings.")
    print()

    print("How many avatars would you like to create? We will try to acomplish exactly your request.")
    print("Enter a number greater than 0: ")
    while True:
        num_avatars = int(input())
        if num_avatars > 0:
            break
    
    print("What would you like to call this edition?: ")
    edition_name = input()

    print("Starting task...")
    print()
    rt = generate_images(edition_name, num_avatars)

    print("Saving metadata...")
    rt.to_csv(os.path.join('output', 'edition ' + str(edition_name), 'metadata.csv'))

    print("Task complete!")


# Run the main function
main()
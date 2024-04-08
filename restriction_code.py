import os
from  itertools import chain

from restrictions import RESTRICTIONS_CONFIG
from config import CONFIG, ASSETS_DIR

####################################################################################

# GLOBALS

# This will update with  map of current names and traits once uploaded
NAMES = {}

####################################################################################
#
# HELPER FUNCTIONS
#
#------------------------------------------------------------------------------------
# Public Helper Funcions:
#

# Check if given filename is a valid trait
def is_valid_trait(trait_filename, layer_path):

    # traits should be a file, not a folder
    if os.path.isdir(os.path.join(layer_path, trait_filename)):
        return False

    # not whatever file, but a PNG
    if not trait_filename.endswith('.png'):
        return False

    # only visible ones
    if trait_filename[0] == '.':
        return False
    
    return True


# Remove the '.png' extension from trait filenames if they have
def fix_trait(trait):

    if trait.endswith('.png'):
        trait = trait[:-4]

    # No traits should be named as "none.png" since 'none' is reserved for trait's absence
    if trait.lower() == 'none':
        raise ValueError("Not allowed 'none.png', 'None.png', 'NONE.png', etc. filenames for traits.")
    
    return trait


# Re-style name to "A Title Style", but keep the upparcase words intact
def title_style(name):
    words = name.split()
    idxs = [i for i, tr in  enumerate(words) if tr.isupper()]
    name = name.title()
    words = name.split()
    for i in idxs:
        words[i] = words[i].upper()
    name = ' '.join(words)
    return name


#------------------------------------------------------------------------------------
# Private Helper Funcions:
#
# Make trait name compatible with PNG filename
def fix_trait_name(name, tr_name):
    """
    Trait names should coincide with their PNG equivalents. To minimize missmatches, the script reshapes both of them to "The Title Style". The only exception is when a whole word is in uppercase, for example: 'LED" in "LED Glasses".

    This function re-styles to "Title Style" but preserving the uppercase words.
    """

    # None is a valid trait and means the absence of a trait...
    if tr_name is None or tr_name.lower() == 'none':

        # ...but its layer must not be required
        if NAMES[name]['required']:
            raise ValueError("The '%s' layer can't have a None as a trait: %s" % (name,
                            "In the config.py is set that this layer is required."))
        
        # From now and on, 'none' is used instead of None
        return 'none'

    # Re-style the trait name
    tr_name = title_style(tr_name)

    # Its '.png' trait filename equivalent must exist
    if tr_name not in NAMES[name]['traits']:

        err_msg = "\nFailed to find '%s' trait in '%s' layer:\n\nEither trait doesn't exist or is misspelled. Please check the trait where its PNG should be and the RESTRICTIONS_CONFIG.\n" % (tr_name, name)
        err_msg_cont = "\nTo minimize missmatches, the script internally renames traits to 'Title Stile', except if a word is all uppercase, for example 'LED' in 'LED Sunglasses'.\n"
        e = ValueError(err_msg + err_msg_cont)

        # Pass fixed name trait and err msg through exception object before raising it
        e.trait_name = tr_name
        e.err_msg_cont = err_msg_cont
        raise e
    
    return tr_name


# Make a map of all names with their traits based on CONFIG
def map_assets():
    names_map = {}

    # Loop through all layers defined in CONFIG
    for layer in CONFIG:

        # Go into assets/ to look for layer folders
        layer_path =os.path.join(ASSETS_DIR, layer['directory'])

        # Get trait filenames array found in 'directory' folder
        traits = [filename for filename in os.listdir(layer_path) if is_valid_trait(filename, layer_path)]

        # Remove '.png' extensions and reject 'none.png', 'None.png', 'NONE.png', etc
        try:
            traits = [fix_trait(filename) for filename in traits]
        except ValueError as e:
            raise ValueError("%s One found in folder '%s'" % (str(e), layer_path))
        
        # Make traits "Title Style"
        traits = [title_style(trait) for trait in traits]

        # map in a dictionary the traits, quantity + other relevant data from CONFIG
        names_map[layer['name']] = {
            'traits': set(traits),
            'n': len(traits),
            'directory': layer['directory'],
            'required': layer['required']
        }

    return names_map


####################################################################################
#  Private:
#------------------------------------------------------------------------------------
# "parse_restrictions" -->  Helper Funcions:
#

# All traits must exist in NAMES map or be a None
def check_traits_sequence(name, traits):

    # traits argument should be list, tuple or set
    if not ( (type(traits) is list) or (type(traits) is tuple) or (list(traits) is set) ):
        raise ValueError("'%s' isn't valid: list, tuple or set expected." % traits)

    # Collect fixed name traits that match to their PNG equivalents
    new_traits = []

    # Collect traits not found in NAMES map
    no_traits = []

    # Loop through traits
    for trait in traits:

        # Get a compatible name with their corresponding '.png' files
        try:
            new_tr = fix_trait_name(name, trait)

        except ValueError as e:

            # Failed to find its PNG equivalent
            if hasattr(e, 'trait_name'):

                # Collect the failures to later re-raise a ValueError exception
                no_traits.append(e.trait_name)
                if not 'err_msg_cont' in locals():
                    err_msg_cont = e.err_msg_cont

            else:
                # Re-raise the exception if it was from a different cause
                raise e
        
        except Exception as e:
            # Re-raise the exception if it was from a different type cause
            raise e

        else:
            # Collect valid and existent trait names
            new_traits.append(new_tr)

    # Inform the user through an error if no PNG traits equivalents have been found
    if no_traits:
        err_msg = "\nIn layer '%s', the following traits don't exist: '%s'\n" % (name, "', '".join(no_traits))
        raise ValueError(err_msg + err_msg_cont)
    
    # Return a list of existing valid trait names
    return new_traits
    

# Extract a list of restricted items, according to one-item dict specs
def get_traits_from_one_item_dict(name, traits_dict):
    """
    The one-item dictionary is in fact a dictionary that can have only one item and its allowed key is one of the following strings: 'all', 'R' or 'A'.

    The 'all' key can only have a boolean as value, and 'A' and 'R' can only have a comma-separated string of traits.
    Anything else raise a ValueError exception.
    """

    # Given traits dict must be a one-item dictionary
    if len(traits_dict) != 1:
        raise ValueError("%s isn't valid. It must be a one-item dictionary whose valid keys are 'A', 'R' or 'all'." % str(traits_dict))
    
    # This is one of the valid keys and must be a boolean
    if 'all' in traits_dict:

        if type(traits_dict['all']) is not bool:
             raise ValueError("%s The only valid value for 'all' key is True or False" % str(traits_dict))

        if traits_dict['all']:

            # Doesn't change anything. {'all': True} is process later
            return traits_dict

        # {'all': False} is redundant and innecessary, but doesn't raise an error
        return None
    
    # 'R' and 'A' which stand for "Restricted" and "Allowed" are the only other valid keys
    if 'R' not in traits_dict and 'A' not in traits_dict:
        raise ValueError("%s must be a one-item dictionary whose valid keys are: 'R', 'A' or 'all'." % str(traits_dict))
    
    # Get the comma-separated string of items attached to keys
    flag = True if 'R' in traits_dict else False
    traits_str = traits_dict['R'] if flag else traits_dict['A']

    try:

        # From the string, extract a list of fixed traits that match with corresponding PNG files 
        traits_seq = list(map(str.strip, traits_str.split(',')))
        traits_seq = check_traits_sequence(name, traits_seq)

    except ValueError as e:

        # Inform the user through an error if some traits don't exist or failed to match with PNG files
        raise ValueError("%s\nOriginal string: %s" % (e, str(traits_dict)))
    
    except Exception as e:
        raise e
    
    else:

        # The one-time dictionary is replaced by the list of validated restricted traits
        # with 'A' the list is streightforward, but with 'R' return the other traits from layer
        return traits_seq if flag else list(NAMES[name]['traits'] - set(traits_seq))


# Return a std error message with a list of names not found
def no_names_error_message(no_names):

    # no_names -->  Is a list of names not found
    n = len(no_names)

    # Transform list into an aesthetic comma separated string
    if n ==1 :
        no_names_str = "'%s'" % no_names[0]
    else:
        no_names_str = "'%s'" % "', '".join(no_names[:-1])
        no_names_str += " and '%s'" % no_names[-1]

    # Build the message to return
    err_msg = "The following %s not exist: %s." % ("name does" if n == 1 else "names do", no_names_str)
    err_msg += "\n"
    err_msg += "The name(s) of the provided name/trait pairs within RESTRICTIONS_CONFIG must match the layer names defined in CONFIG (config.py)"
    err_msg += "\n"
    err_msg += "It’s possible that they don’t actually exist or that there is a simple misspelling bug."

    return err_msg


# Layer's name categories and its traits are organized in a key/value pair structure
def check_subrestrictions_dict(sub_restr):

    # To collect name/traits equal to {'all': False}
    garbage_items = [] 

    # To collect names not found in NAMES map
    no_names = [] 

    # Loop through sub restriction and make sure name/trait pairs are valid
    for name, traits in sub_restr.items():

        if name not in NAMES:

            # Collect invalid name category and check the next one
            no_names.append(name)
            continue

        if type(traits) is dict:

            # Get the restricted traits
            traits = get_traits_from_one_item_dict(name, traits)

            if traits is None:

                # None is for {'all': False}. This is redundant and will be disposed
                garbage_items.append(name)

            else:

                # Replace one-item dict with specific restricted traits list
                sub_restr[name] = traits

        else:
            sub_restr[name] = check_traits_sequence(name, traits)

    # Inform the user through an Exception if non-existent names were given
    if no_names:
        raise ValueError(no_names_error_message(no_names))

    # Delete all collected names that contain {'all': False}
    while garbage_items:
        sub_restr.pop(garbage_items.pop(), None)


# Parse, check and modify subrestriction whenever is a list of name/trait pairs
def check_subrestriction_list(sub_restr):

    # To collect names that don't exist
    no_names = []

    # To build a better sub restriction and to replace later the original
    new_subr = []

    # Loop through the name/traits pairs of the sub restriction until exhaust
    while sub_restr:
        trait_pair = sub_restr.pop()

        # Raise exception if string or dictionary is giving. It must be a tuple or similar
        if type(trait_pair) is str:
            raise ValueError("'%s': Expected a (name, trait) tuple or similar. String alone isn't valid." % trait_pair)
        
        if type(trait_pair) is dict:
            raise ValueError("'%s': Expected a (name, trait) tuple or similar. In this case, when the trait-pairs set are given in a list (or equivalent), the trait-pair inner items must be in the form of a tuple. Dictionaries aren't allowed." % trait_pair)

        try:
            # Destruct trait_pair. 'traits' can be single trait as a string or a list of traits
            name, traits = trait_pair

        except Exception as e:
            raise ValueError("<<%s>>: %s" % (trait_pair, str(e)))

        # Collect names not found to raise Exception later
        if name not in NAMES:
            no_names.append(name)

            # No need to do anything else if name doesn't exist
            continue

        if type(traits) is dict:

            # If dict, it must be one-item. Extract restricted traits according to dict specs
            new_trs = get_traits_from_one_item_dict(name, traits)

            # {'all': False} is redundant. Just ignore it!
            if new_trs is None:
                continue

        elif type(traits) is str or traits is None:

            # traits is a singular trait (it's not plural)
            # None is valid: Means the absence of a trait
            new_trs = fix_trait_name(name, traits)

        else:
            new_trs = check_traits_sequence(name, traits)
            
        # Collect the already checked and valid name/traits
        new_subr.append((name, new_trs))

    # Raise exception to inform the user about names that don't exist
    if no_names:
        raise ValueError(no_names_error_message(no_names))
    
    # Replenish subrestriction with valid and check name/trait pairs
    sub_restr.extend(new_subr)
    

# parse, check and fix each restriction
def parse_single_restriction(restriction):

    # General Error intro in case of exceptions
    err_msg = lambda jdx, subr: "The %s set of trait pairs: '%s'\n" % ('left' if jdx == 0 else 'right', str(subr))
    
    # Call different processes wether sub_restr is a dict or a list
    process = lambda typ: check_subrestrictions_dict if typ is dict else check_subrestriction_list

    # Loop through the inner items of a restriction
    for jdx, sub_restr in enumerate(restriction):

        # Make sure subrestriction is a list or dictionary and not empty
        if not (type(sub_restr) is list or type(sub_restr) is dict):
            raise ValueError("%sExpected a list or dictionary." % err_msg(jdx, sub_restr))
        if len(sub_restr) == 0:
            raise ValueError("%sIs empty." % err_msg(jdx, sub_restr))

        # Make a copy to inform user in case of Exceptions. Original sub_restr will be modified
        subr_copy = sub_restr.copy()

        # Call the appropiate process depending the subr type
        try:
            process(type(sub_restr))(sub_restr)
        except ValueError as e:
            raise ValueError("%s%s" % (err_msg(jdx, subr_copy), e))


####################################################################################
#  Private
#------------------------------------------------------------------------------------
# "setup_restrictions" -->  Helper Funcions:
#
            
# Retrieve all trait pairs, transform them into a tuple (name, trait) and return them pack into a set
def get_trait_pairs_set(subrestriction, is_setters = True):

    # subrestriction ==> is one of the two components of a restriction: 'Restr. Setters' or 'Restr. Getters'
    # is_setters  ==> If true is 'Restr. Setters' otherwise is 'Restr. Getters'

    # Fix trait function: None is a valid trait and is stored as 'none'.
    fix = lambda tr: 'none' if tr is None else tr

    # The set that will collect all name-trait pairs.
    trait_pairs_set = set()

    # Each subrestriction can be either a dictionary or a list
    if type(subrestriction) is dict:

        # Filter out key/value pair items whose values are dictionaries and place in different lists
        subr_dicts_2nd_item = [(name, tr) for name, tr in subrestriction.items() if type(tr) is dict]
        subr_others = [(name, tr) for name, tr in subrestriction.items() if type(tr) is not dict]

        # Process all items whose values are dictionaries. The only value they can have is {'all': True}
        # The {'R': <<string>>} and {'A': <<string>>} has been already transformed into traits lists
        if is_setters:

            # Loop all traits in names' folders and transform into tuples (name, trait)
            #                             [
            # {name_1: {'all': True}} ==> [(name_1, trait_1,), (name_1, trait_2), (name_1, trait_3), ...(name_1, trait_n)],
            # {name_2: {'all': True}} ==> [(name_2, trait_1,), (name_2, trait_2), (name_2, trait_3), ...(name_2, trait_n)],
            # {name_3: {'all': True}} ==> [(name_3, trait_1,), (name_3, trait_2), (name_3, trait_3), ...(name_3, trait_n)],
            # ...
            # {name_n: {'all': True}} ==> [(name_n, trait_1,), (name_n, trait_2), (name_n, trait_3), ...(name_n, trait_n)],
            #                                                                                                             ]
            # Unpack the nested lists and place the tuples in the set and repleace all {name: {'all': True}}s
            trait_pairs_set.update(list(chain(
                *[ [ (name, fix(tr)) for tr in NAMES[name]['traits'] ] for name, d in subr_dicts_2nd_item if d['all'] ]
            )))

        else:

            # Transform all {name: {'All': True}} into a tuple (name, True) and place them in the set
            trait_pairs_set.update([(name, True) for name, d in subr_dicts_2nd_item if d['all']])

        # Update the trait's set with the rest of value items (which are lists of traits)
        trait_pairs_set.update(list(chain(
            *[ [ (name, fix(tr)) for tr in trs] for name, trs in subr_others]
        )))
        
    else: # 'subrestriction' is a list

        # Filter out the dictionary as a 2nd item items from the other iterables
        dict_list = [s for s in subrestriction if type(s[1]) is dict]
        else_list = [s for s in subrestriction if type(s[1]) is not dict]

        # Dictionaries can only be {'all': True} or {'all': False}. Process only the True ones
        # The {'R': <<string>>} and {'A': <<string>>} has been already transformed into traits lists
        if is_setters:

            # Loop all traits in names' folders and transform into tuples (name, trait)
            #                             [
            # (name_1, {'all': True}) ==> [(name_1, trait_1,), (name_1, trait_2), (name_1, trait_3), ...(name_1, trait_m)],
            # (name_2, {'all': True}) ==> [(name_2, trait_1,), (name_2, trait_2), (name_2, trait_3), ...(name_2, trait_m)],
            # (name_3, {'all': True}) ==> [(name_3, trait_1,), (name_3, trait_2), (name_3, trait_3), ...(name_3, trait_m)],
            # ...
            # (name_n, {'all': True}) ==> [(name_n, trait_1,), (name_n, trait_2), (name_n, trait_3), ...(name_n, trait_m)],
            #                                                                                                             ]
            # Unpack the nested lists and place the tuples in the set and repleace all (name, {'all': True})s
            trait_pairs_set.update(list(chain(
                *[ [ (name, fix(tr)) for tr in NAMES[name]['traits']] for name, d in dict_list if d['all']]
            )))
            
        else:

            # Transform all (name, {'all': True}) into (name, True) and place in the set
            trait_pairs_set.update([(name, True) for name, d in dict_list if d['all']])
        
        # Filter out second item s[1] str types from the ramaining iterables
        other_str_list = [s for s in else_list if (type(s[1]) is str) or (s[1] is None)]
        else_list = [s for s in else_list if s not in other_str_list]

        # Fix the trait's name and update the set
        trait_pairs_set.update([ (name, fix(tr)) for name, tr in other_str_list])

        # Finally: update the set with the ramining iterables, whose 2nd item are traits' lists
        trait_pairs_set.update(list(chain(*[[(name, fix(t)) for t in trs] for name, trs in else_list])))

    return trait_pairs_set


# Get a list of workable dictionaries from list of restrictions
def get_wble_dictionaries():
    # This is the STEP 1) of compiling a full workable integrated dictionary 
    # Compile all single workable dictionaries per Restriction

    # Collect all workable dictionaries from restrictions in the following list
    restrictions_list = []

    # Collect collisions:
    # A collision: when the same layer name are found in both sides of the restriction: R. Setters and R. Getters
    common_names = []

    # Loop all restrictions
    for idx, restriction in enumerate(RESTRICTIONS_CONFIG):

        # De-structure the restriction in its parts: R. Setters and R. Getters 
        subr_setter, subr_getter = restriction

        # Get the corresponding SETs of (name, trait) tuples from R. Setters and R. Getters
        setters = get_trait_pairs_set(subr_setter)
        getters = get_trait_pairs_set(subr_getter, False)

        # Build the 3rd and 4th depht levels of workable dictionary corresponding to current restriction 
        # These levels correspond to the name/trait pairs that are restricted.
        wd_getters = {}

        # Process all (name, trait) from getters set until exhaust
        while getters:
            name, trait = getters.pop()

            # Create the basic format for this name if absent 
            if name not in wd_getters:
                wd_getters.update( { name: {'Restrict All': False, 'Restricted': set() } } )

            if type(trait) is bool:

                if trait:
                    # If pair is (name, True) all traits from name are restricted
                    # if 'Restrict All' was already True, no want to change. Do nothing if trait is False
                    wd_getters[name]['Restrict All'] = True

            else:
                # Add the restricted trait to the set
                wd_getters[name]['Restricted'].add(trait)


        # Build the 1st and 2nd depth levels of workable dictionary corresponding to current restriction
        # These levels correspond to the name/trait pairs that impose restrictions.
        wd_setters = {}

        # Process all (name, trait) from setters set until exhaust
        while setters:
            name, trait = setters.pop()

            if name not in wd_setters:
                wd_setters.update({name: {}})

            # Connect the 3rd and 4th levels to current trait
            wd_setters[name].update({trait: wd_getters.copy()})
        

        # Look for collisions: Check if the same name are in both sides 
        comm_names = set(wd_getters.keys()) & set(wd_setters.keys())

        # Add to the list if one is found
        if comm_names:

            # A record of Restriction index, collision names and restriction is to inform to user
            common_names.append((idx, list(comm_names), str(restriction)))

        # Store current single workable dictionary in list
        restrictions_list.append(wd_setters)


    # Inform the user about collisions if found one or more
    if common_names:

        print("========================================================")
        print('...Ooops!  We have WARNINGS:')
        print("The following restrictions have the same layer names in both sides of the restriction:")
        print()

        # Inform as detailed as possible: Restriction index, collision names and restriction
        for idx, comm_names, restriction in common_names:
            print("Restriction with index %i. Repeated layer's names: '%s'" % (idx, "', '".join(comm_names)))
            print("==> %s" % str(restriction))
            print()

        print("""Restriction settings still work, but they may output undesired results. Consider to split given restriction lines in order to avoid these collisions and ensure appropiate results.""")

        while True:
            r = input("Do you want to continue anyway? Y/N:")
            if r == "Y" or r == "y":
                break

            if r == "N" or r == "n":
                print("Execution aborted!")
                quit()

        # Continue despite the warnings!
        print()

    else:

        # No Warnings
        print("...everything is fine. We have an operable RESTRICTIONS settings.")
        print()

    return restrictions_list


# Get the final Workable Dictionary that will perform in nft.py    
def get_final_wd_dictionary(restrictions_list):
    # This is the STEP 2) of compiling a full workable integrated dictionary
    # Integrates all restrictions dictionaries list into a single one 

    # Initialize the final workable dictionary
    restr_WD = {}

    # Loop the list of restriction dictionaries
    for restriction_dict in restrictions_list:

        # Parse the 1st level: restrictor names
        for name_pair in restriction_dict.items():
            name, restr = name_pair

            # Add all restriction settings from restrictor name if absent
            if name not in restr_WD:
                restr_WD.update(dict([name_pair]))

                # Go for the next restriction dictionary. Current is integrated
                continue

            # Parse the 2nd level: restrictor traits from layer
            for trait_restr in restr.items():
                trait_setter, restricted_pairs = trait_restr

                # Add all restriction settings from restrictor trait if absent
                if trait_setter not in restr_WD[name]:
                    restr_WD[name].update(dict([trait_restr]))

                    # Go for the next restrictor trait. Current one is integrated
                    continue

                # Parse the 3rd level: restricted names from restrictor trait
                for name_restricted, traits_restricted in restricted_pairs.items():

                    # Add the final level (restricted traits) if absent
                    if name_restricted not in restr_WD[name][trait_setter]:
                        restr_WD[name][trait_setter][name_restricted] = traits_restricted.copy()

                        # Go for next restricted pairs. Current one is integrated
                        continue

                    # If already exists, change to True if it's the case...
                    if traits_restricted['Restrict All']:
                        restr_WD[name][trait_setter][name_restricted]['Restrict All'] = True

                    # ...and update with new restricted traits if there any
                    restr_WD[name][trait_setter][name_restricted]['Restricted'].update(traits_restricted['Restricted'])
    
    return restr_WD


# Check final Workable dictionary for if it has the ALL/None issues
def check_for_all_none_issues(restr_WD):
    # The All/None issue is described in the structure of the Workable Dictionary (WD) structure
    #
    # This issue shows up when a particular name/trait restricts all traits from other layer including the None...
    # ...or when all traits of a layer (including None) restrict a particular name/trait
    # 
    # in both cases, there's no way such name/trait could be present in collection.

    print("Looking for ALL/None issues...")

    # This list collect all name/trait pairs affected and layer name provoker
    all_none_issues = []


    # 1) Search for the ALl/None issues within the Getters side

    # Loop through all restrictor name/pairs to search for the ALL/None issue
    for rstor_name in restr_WD.keys():

        # Loop deeper into each restrictor name and its traits
        for restrictor_trait in restr_WD[rstor_name].keys():

            # Loop one deeper level: each restrictor traits and their restricted names
            for restricted_name, restricted_traits in restr_WD[rstor_name][restrictor_trait].items():

                # Not a None/All issue detected yet
                issue_found = False

                # It's a red flag if 'Restrict All' is set to True
                red_flag = restricted_traits['Restrict All']

                # It's also a red flag if the total traits of a layer category are within the restricted set
                red_flag = red_flag or len(restricted_traits['Restricted']) >= NAMES[restricted_name]['n']

                # if the red flag is raised and 'none' is also among the restricted items. We have an issue!
                issue_found  = red_flag and 'none' in restricted_traits['Restricted']

                # However, the red flag is raised and issue not found yet, but...
                if red_flag and not issue_found:

                    # ...if trait of that layer is required (None not accepted), we have an issue too!
                    issue_found = NAMES[restricted_name]['required']
                        
                # Collect the All/None issue found
                if issue_found:

                    # The pair: "Restrictor Name / restrictor trait" (rstor_name, restrictor_trait)...
                    # ...won't show up in collection, because all traits of the restricted name are banned,
                    # ...including 'none'
                    all_none_issues.append(
                        {
                            'pair': (rstor_name, restrictor_trait),
                            'provoker': restricted_name,
                            'side': 'getter'
                        })


    # 2) Search for All/None issues within the Setters side:
                    
    # Inner helper function: merges all given sets and return the resulting set                
    def merge_sets(*ls):
        total_pairs_set = set()
        total_pairs_set.update(*ls)
        return total_pairs_set
                    
    # Loop through Workable Dictionary
    for rstor_nm, trs_setter in restr_WD.items():

        # Get all Restrictor traits from current restrictor name
        rstor_trs = trs_setter.keys()

        if len(rstor_trs) == (NAMES[rstor_nm]['n'] + (0 if NAMES[rstor_nm]['required'] else 1)):

            # A red flag is raised: restrictor name's all traits restrict something

            # Get a list of lists of restricted pairs set: 
            # [ [ { <<restr. pairs of name1...>> }, { <<restr. pairs name2... },...], [ {}, {}...],... ]
            restr_pairs = [ [ 
                merge_sets(
                    set( [ (rn, tr) for tr in dat['Restricted'] ] ),
                    set( [ (rn, tr) for tr in NAMES[rn]['traits'] ] if dat['Restrict All'] else set() )
                ) for rn, dat in rrn.items() ] for rrn in trs_setter.values() ]
            
            # los: List of Sets of pairs per restrictor trait:
            # Merge the inner list of restricted pairs set
            los = [ merge_sets(*ppt) for ppt in restr_pairs]

            # Extract only the common restricted pairs in all traits
            # These common pairs won't show up in collection
            all_none_issues.extend(
                [ 
                    {
                        'pair': (rsd_nm, rsd_tr),
                        'provoker': rstor_nm,
                        'side': 'setter'
                     } for rsd_nm, rsd_tr in set.intersection(*los) ]
                )

    # Inform user if All/None issues were found
    if all_none_issues:

        print("===============================")
        print("Issues have been found...!:")
        print("The following traits are compromised to never exist, because they fully restrict or are fully restricted by an entire layer's category... including 'None':")
        print()

        for idx, issue in enumerate(all_none_issues):
            print("%s ==> '%s / %s'  ...%s  ==>  %s's all traits%s" % \
                (
                    str(idx + 1), 
                    *issue['pair'], 
                    "fully restricts" if issue['side'] == 'getter' else "is fully restricted by", 
                    issue["provoker"], 
                    '.' if NAMES[issue['provoker']]['required'] else ', including None.'
                ))
        
        print()
        print("===============================")
        print("We encourage you to carefully review the RESTRICTION_CONFIG settings in restrictions.py")
        
        while True:
            r = input("Do you want to continue anyway? Y/N:")
            if r == "Y" or r == "y":
                break

            if r == "N" or r == "n":
                print("Execution aborted!")
                quit()

        # Continue despite the warnings!
        print()

    else:

        # No ALL/None issues found
        print("...Perfect!  No All/None issues found.")
        print()    



# ======================================================================================
#       PUBLIC
# ======================================================================================

# Parse RESTRICTIONS_CONFIG from restrictions.py and make sure is valid
def parse_restrictions():

    # The whole set of restrictions must be a list (or tuple) of individual restrictions
    if not (type(RESTRICTIONS_CONFIG) is list or type(RESTRICTIONS_CONFIG) is tuple):
        raise ValueError("'RESTRICTIONS_CONFIG': expected list or tuple")
    
    # Error messages templates:

    restr_form_err_msg = \
        "\n" + \
        "Error in the restriction of index %i:\n" + \
        "%s\n" + \
        "Given restriction %s.\n" + \
        "The restriction MUST be a list of TWO components: The left and right sets of trait pairs. They can be either a list or a dictionary." + \
        "\n"
    
    generic_err_msg = \
        "\n" + \
        "Error in the restriction of index %i.\n" + \
        "%s" + \
        "\n"
        

    # Loop through all restrictions in RESTRICTIONS_CONFIG list
    for idx, restriction in enumerate(RESTRICTIONS_CONFIG):

        # Restriction must be a list
        if type(restriction) is not list:
            raise ValueError(restr_form_err_msg % (idx, "-----", "is '%s'" % str(restriction)))

        # Restriction must be a list of two components
        r_len = len(restriction)
        if r_len != 2:
            raise ValueError(restr_form_err_msg % (idx, str(restriction), \
                                         'is empty' if r_len == 0 else "has %i items" % r_len))
        
        try:
            parse_single_restriction(restriction)

        except ValueError as e:
            raise ValueError(generic_err_msg % (idx, e))

    # If code reach this line, is wonderful!
    return None


# Get a workable dictionary made from already verified RESTRICTION_CONFIG
def setup_restrictions():

    # The workable dictionary has the following structure:
    #
    # { 
    #   name_restrictor_1: {
    #      trait_restrictor_1: {
    #          name_restricted_1: {
    #              'All Restricted': False,
    #              'Restricted': {trait_restricted_1, trait_restricted_2, ...trait_restricted_n}
    #             },
    #
    #          name_restricted_2: {
    #               'All Restricted': True,
    #               'Restricted': {}  # It doesn't matter if have traits
    #             },
    #          ...
    #          name_restricted_n: {...},
    #      },
    #
    #      trait_restrictor_2: {...},
    #      ...
    #      trait_restrictor_n: {...}
    #       },
    #
    #   name_restrictor_2: {...},
    #   ...
    #   name_restrictor_n: {...}
    # }
    #
    # The workable dictionary is a 4th level depht nested dictionary of dictionaries.
    # The first two layers are made from layer names and traits respectively. The later ones belongs to the layer.
    # Thus, in the example above: trait_restrictor_1, trait_restrictor_2, etc. belong to name_restrictor_1,
    # These name and trait restrictors are the name-trait pairs that impose restrictions to the deeper levels following
    # the path of the nested dictionaries.
    # Thus, in the example above: trait_restricted_1, trait_restricted_2 and so on (which all belong to name_restricted_1) 
    # are restricted to exist if name_restrictor_1 / trait_restrictor_1 pair is present.
    #
    # When some name_restricted has the "All Restricted" key with a False value, means that specifically the traits
    # found in 'Restricted' value are the ones restricted to exist.
    # 
    # Otherwise, when 'All Restricted' value is True, means that all traits from its corresponding name_restricted, are
    # restricted, despite whatever traits found in 'Restricted'
    #
    # However, if 'All Restricted' value is True and 'none' is present in 'Restricted' we have an issue:
    # The corresponding name_restrictor / trait_restrictor pair (following up the path) can't exist. It will always be banned.
    # When detected, this particular issue is reported when running the code.

    # ===================================================================
    # There's a two step process to Build the dictionary as explained above:
    # 1) Compile a single workable dictionary per 'restriction' from the RESTRICTION_CONFIG list of restrictions
    # 2) Merge all previous workable dictionaries into a single one 

    # ===================================================================

    # Execute step 1: Get a list of workable dictionaries
    restrictions_list = get_wble_dictionaries()

    # Execute step 2: Get the final workable dictionary from the list of WDs.
    restr_WD = get_final_wd_dictionary(restrictions_list)

    # Before delivering the final Workable Dictionary, check for the all/none issues and inform the user
    check_for_all_none_issues(restr_WD)
    
    return restr_WD


#------------------------------------------------------------------------------------
# End of Public Functions
# ======================================================================================

# Main function. 
def main():
    # Need to map PNGs traits and filenames per categories based on CONFIG
    # Update map into global and public NAMES
    NAMES.update(map_assets())


# Run when module is imported
main()
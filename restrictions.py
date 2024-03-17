# This is the file where you setup your restrictions.
#
# Restrictions are necessary to avoid unwanted trait combinations.
# Please, read the tutorial on how to setup restrictions in RESTRICTIONS_TUTORIAL.md 

# Here I provide you with an example of a restriction configuration to work with given assets sample.
# Take your time to understand the whole restriction setup structure.
# Take notice of the following:
    # > The RESTRICTIONS_CONFIG is a list of three inner lists
    # > Each inner list is a restriction. Thus, this whole restrictions setup is composed by 3 individual restrictions.
    # > Each inner restrictions is composed by two items: that can be a list or a dictionary:
        # >> Each of these items are in fact a reference to a group of trait pairs.
        # >> All trait pairs referenced in the first group restricts the trait pairs referenced in the second, and viceviersa.
#
# Please, read the RESTRICTIONS_TUTORIAL.md


RESTRICTIONS_CONFIG = [
    [ [('Background', 'Brown')], [('Head', 'Punk')] ],
    [ {'Accessory Behind': {'all': True}}, [('Body', 'majin buu'), ('Clothing', {'A': 'Light white suit'})] ],
    [ [('Front Accessory', 'scar')], [('Clothing', {'all': True})]]
]


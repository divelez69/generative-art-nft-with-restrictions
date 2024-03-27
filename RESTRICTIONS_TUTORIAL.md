# VERY IMPORTANT NOTE

Please, read!

The RESTRICTIONS_CONFIG is the cherry on the cake of this entire set of scripts. This was made to generate clean and beautiful NFT avatars. I encourage you to read the concise but complete tutorial I provide you.

# TUTORIAL

INTRODUCTION:

The process of crafting NFT collections encompasses thousands of trait combinations across various layers. However, not all traits harmonize seamlessly. Allowing incompatible combinations would result in chaotic and unappealing avatar images. For instance, while our frog characters within the collection might sport helmets, those adorned with unique hairstyles would undoubtedly reject them (yes, we do have delightfully hairy amphibians!). To address this challenge, we require a mechanism to precisely define and manage these undesired pairings. The `RESTRICTIONS_CONFIG` within `restrictions.py` serves this purpose admirably.

To address scenarios like the one described, we need to configure restrictions for our NFT collections. Here's how you can set it up:

```python
    RESTRICTIONS_CONFIG = [
        [ [('hair', 'Punk')], { 'helmet': { 'all': True } } ],
    ]
```

In plain English, this means that frog images with the `'Punk'` trait for `'hair'` explicitly exclude any possibility of having `'helmet'` traits. These specific combinations will be rejected.

If we wish to incorporate an 80s-style hair trait into the existing restrictions that also prevent helmets, the setup may look like this:

```python
    RESTRICTIONS_CONFIG = [
        [
            [ ('hair', 'Punk'), ('hair', '80style') ],
            { 'helmet': { 'all': True } }
        ],
    ]
```

Given that both `'Punk'` and `'80s style'` traits belong to the same layer category, namely `'hair'`, we can bundle them in a list:

```python
    RESTRICTIONS_CONFIG = [
        [
            [ ('hair', ['Punk', '80style']) ],
            { 'helmet': { 'all': True } }
        ],
    ]
```

### Key Considerations:

1.  Layer Names: The layer names (e.g., `'hair'` and `'helmet'`) must match the layer names specified in the `CONFIG` from `config.py`.

1.  Trait Names: Trait names should correspond to the PNG filenames of the traits in their respective directories. For instance, if we have traits like `'Punk'` and `'80style'`, there should be equivalent files named `'Punk.png'` and `'80style.png'`. More about that in a final note at the end of this tutorial.

1.  Trait Pairs:

    1. Traits are implicitly represented as name/trait pairs. In Python code, this is a tuple: `(name, trait)`.

    1. If it references to more than one trait per layer category they can be bundled in a list: `(name, [trait1, trait2, ...])`.

    1. To reference all traits within a layer's category (excluding `None`), use: `(name, {'all': True})`.

# THE RESTRICTION (It's structure):

A restriction is a list containing two items, each representing a set of trait pairs:

```
[ << Left set of trait pairs >>,  << Right set of trait pairs >> ]
```

These sets of trait pairs (left and right) are mutually exclusive. For instance, all trait pairs referenced within the left set restrict those referenced in the right set, and vice versa.

### Key Points to Consider:

1. Unlimited Trait Pairs: There's no limit to the number of trait pairs that can be referenced within the same set. These pairs can even belong to different categories. For example:

   ```python
   [ ('hair', ['Punk', '80style']), ('eyes', 'mad'), ('mouth', {'all': True}) ]
   ```

1. Trait pairs within the same set don't exclude each other. Instead, they restrict the ones referenced in the other set. For instance, in given example, `'Punk'` hair and `'mad'` eyes can coexist.

1. The term “set” here doesn't refer to the Python data structure. It simply means grouping trait pairs, either in a list or a dictionary.

1. Using Dictionaries as set of Trait Pairs:

   1. In a dictionary, keys represents the layer's names (e.g., `'hair'`), and their values are references to specific traits. The same example above, but in dictionary form is:

      ```python
      { 'hair': ['Punk', '80style'], 'eyes': ['mad'], 'mouth': {'all': True} }
      ```

      Note that when using a dictionary, the traits must be within a list or a one-item dictionary. More about one-item dictionaries later.

## Now, let's take a look to some restrictions examples:

1.  Example, ties of flowers, birds and rainbows restrict the cowboy's hat, and vice-versa:

    ```python
    [
        [ ('tie', ['flowers', 'birds', 'rainbows']) ],
        [ ('hat', 'cowboy') ]
    ]
    ```

1.  Example, the high and hippie skirts and the absence of skirt restrict ties of spirits and ghosts.

    ```python
    [
        [ ('skirt', {'high', 'hippie', None}) ],
        { 'tie': {'spirits', 'ghosts'} }
    ]
    ```

1.  Example, the brown leather, blue jean and crocks shoes restrict the cowboy hat and the abscence of hat.

    ```python
    [
        { 'shoe': ['brown leather', 'blue jean', 'crocks'] },
        [ ('hat', ['cowboy', None]) ]
    ]
    ```

1.  Example, try to interpret this restriction yourself...

    ```python
    [
        {
            'skirt': [ 'squares', 'rainbow', None ],
            'tie': ('red', ),
        },
        {
            'helmet': {'fireworker', 'police'},
            'hat': {'cowboy', 'baibol'},
            'socks': {'all': True}
            'skirts': {'A': 'squares, circles, triangles'}
        }
    ]
    ```

    Did you notice new things in previous examples?

    1. Using Python `None`:
       The Python `None` can be assigned as a trait. It signifies the absence of a trait. In the `CONFIG` (from `config.py`), certain categories are not required to have a trait. These categories support `None` as a valid trait value. In the `RESTRICTIONS_CONFIG`, `None` is treated as any other regular trait. It restricts other traits just as it is restricted by them.

    1. Multiple Traits per Category:
       When referencing more than one trait within the same category, you can bundle them using various data structures such as lists, tuples, and sets. This time we explicitly reference the actual Python `set` data structure.

    1. The 'One-Item Dictionary':
       The item: `'skirts': {'A': 'squares, circles, triangles'}` from the previous example demonstrates the use of a one-item dictionary. Let's delve deeper into this:

       1. The key `'skirts'` represents the layer's name.
       1. The value `{'A': 'squares, circles, triangles'}` specifies the allowed traits for that layer.

## The One-Item Dictionary:

The one-item dictionary provides an efficient way to reference trait pairs, especially when managing multiple traits within the same layer's category. By definition, it contains only one item. If more than one is provided, the script will reject it. Here's how it works:

1. `{'all': True}`:
   Refers to all traits within a given layer's name, excluding the `None` (if applicable). Examples:

   ```python
   ( 'hair', {'all': True} ) # or its equivalent
   { 'hair': {'all': True}}
   ```

   Refers to all traits from the `'hair'` category.

1. `{'all': False}`:
   When using the one-item dictionary with the key-value `'all': False`, it refers to no trait within the specified layer's name, including the `None`. By default, all layer names are implicitly given this one-item dictionary, so explicitly providing it is redundant. The script simply ignores it.

1. `{'R': <<comma-separated list of traits>> }`:
   The `'R'` stands for 'Restrict', and the 'comma-separated list of traits' is a string (not a list) containing specific traits. If any other type of value besides a string is provided, the script will raise a `ValueError` exception. The traits specified within this string will either restrict or be restricted by the trait pairs in the other set within the same restriction.

1. `{'A': <<comma-separated list of traits>> }`:
   The `'A'` stands for 'Allows' or 'Allowed'. It indicates that the listed traits are the solely permitted ones. In contrast to `'R'` (which restricts certain traits), the `'A'` specifically means that those traits not mentioned are the ones that are restricted.

# The `RESTRICTIONS_CONFIG` whole set:

The `RESTRICTIONS_CONFIG` is a list of restrictions, each containing two sets of trait pairs (as previously described):

```
RESTRICTIONS_CONFIG = [
    [ << Left set of trait pairs >>,  << Right set of trait pairs >> ]
    [ << Left set of trait pairs >>,  << Right set of trait pairs >> ]
    [ << Left set of trait pairs >>,  << Right set of trait pairs >> ]
    ...
    [ << Left set of trait pairs >>,  << Right set of trait pairs >> ]
]
```

There's no limit to the number of restrictions within the whole set. Each restriction acts independently, therefore whatever is defined in a restriction does not interfere with the rest of restrictions.

# Final Note on Trait Names and Filenames:

When working with the `RESTRICTIONS_CONFIG`, it is crucial to ensure that references to traits align with their corresponding file names within the `‘assets’` subdirectories. For instance, if a restriction mentions the `“LED Sunglasses”` trait, there must be a corresponding `“LED Sunglasses.png”` file in the appropriate `‘assets’` subdirectory. Failing to do so will result in a `ValueError` exception being raised during script execution.

Unfortunately, these mismatches between trait names and filenames are common and can pose a challenge when running the script for the first time. You will likely need to manually address this issue by debugging and cleaning up the data beforehand. However, this trade-off is well worth it because it ultimately leads to the creation of beautiful and pristine NFTs.

To minimize these hurdles, the script internally re-styles trait filenames and their references (within `RESTRICTIONS_CONFIG`) to a “Title Style” form. For example, if a trait named `“brown leather.png”` is referenced as `“Brown leather”`, both will be re-styled to `“Brown Leather”`, thus ensuring a match. The only exception is that, while re-styling, if a whole word in uppercase is found, it remains unchanged. For instance, `“LED sunglasses.png”` will be re-styled as `“LED Sunglasses”`.

This feature also corrects the excess of blank spaces, a common typo. For example, `“blue       Mujin .png”` (with a space before the `'.png'` extension) will be re-styled as `“Blue Mujin”`. However, other typos, such as attempting to reference `“cigarr”` (with two `'r'`) to `“cigar.png”`, must be manually addressed.

Although this feature isn’t flawless in addressing all typos and mismatches, it significantly simplifies the overall process by relieving the need to reference the PNG filenames exactly as they are written. Importantly, the re-styling feature doesn’t alter PNG filenames; however, you will see the improvements reflected in the JSON files’ metadata, enhancing their aesthetic.

---

Now, unleash your creativity and dive into your NFT projects! Feel free to share your feedback and project links. I'd love to see what you build.

Best regards,

Diego E Velez
divelez69@gmail.com
Feb, 2024

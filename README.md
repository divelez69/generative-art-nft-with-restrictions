# Generative NFT Art With Rarities and Programmable Restrictions

by Diego E. Velez (Feb, 2024)

## Introduction

The `generative-art-nft-with-restrictions` repository is a library for creating generative art with a programmable restrictions feature that prevents mixing incompatible traits within the same artwork.

This enhanced version is based on a previous iteration coded by Rounak Banik, originally developed to generate NFT avatars and collectible projects. The improved version was specifically used to create the artwork for the [Pepiyans (also known as TheCarlos)](https://x.com/pepeiyans?s=20) project in SEI Network.

This tool is designed to be blockchain-agnostic. By making the necessary adjustments in `metadata.py`, you can theoretically create NFTs that are compatible with any network out there, including Ethereum, Solana, Avalanche, Cosmos, Radix, and more. Remember to conduct your own research.

## Features (Original version legacy)

### Generate over a million distinct images with less than 60 traits

The library allows you to generate images every distinct possible combination of your traits. For context, if you had trait art for a project like [Bored Apes](https://boredapeyachtclub.com/#/home), the library could generate upwards of 1.2 billion distinct apes.

### Add rarity weights

The library also allows you to configure the image generation process in such a way that you have complete control over how rare each and every trait is.

### Generate compliant JSON metadata for your NFTs

This repository includes a functionality for generating JSON metadata for your NFTs, which is essential for most marketplaces. The original version implemented this feature in compliance with OpenSea requirements (and, by extension, the general NFT metadata standard). However, this newly enhanced version was specifically tailored to create a collection for the [WeBump](https://webump.xyz/) community using its `Lighthouse` client tool. In this updated version, both base code types of metadata are retained. Users may need to make minor adjustments to select or adapt the base metadata code according to their specific requirements.

### Fuzzy friendly

Even if you’re not familiar with programming (whether in Python or any other language), you can still utilize this library. A tutorial for this updated and enhanced version is currently in progress.

Indeed, there exists a tutorial for the original version of this code, which does not include the `RESTRICTIONS_CONFIG` feature. While that tutorial retains some relevance for this new and improved version, I strongly recommend directing your attention to the dedicated sections that highlight the new features. Take the time to explore the specific tutorials provided here to fully leverage the enhancements. Since there isn’t yet a dedicated tutorial on Medium for this enhanced version, paying close attention to the specific instructions below, in this file, is especially important.

## ENHANCED VERSION by Diego E. Velez: Feb, 29th 2024:

### Background:

While exploring resources, I stumbled upon an impressive Python codebase authored by Rounak Banik (rounakbanik). This codebase was used to generate over 3000 collection NFTs known as the [Pepeiyans (AKA TheCarlos)](https://x.com/pepeiyans?s=20). The NFT images in this collection were crafted from 219 base traits spread across 8 categories, resulting in an astonishing number of possible avatars—over a billion!

However, I discovered that manipulating rarity weights using data arrays wasn’t enjoyable or efficient. Moreover, the original version lacked a crucial feature: preventing unwanted trait combinations. As a consequence, the resulting avatar images were chaotic, disorganized, and frankly unappealing. Driven by this realization, I set out to enhance the original code, and here’s what I came up with:

### RESTRICTIONS configuration (Enhanced version)

Combination rules can be established to ensure that not all traits are mixed indiscriminately. For example, we might want to avoid pairing hats with certain types of heads. To address this, I introduced the `RESTRICTIONS_CONFIG` within `restrictions.py`. Using straightforward and user-friendly Python data structures so combination rules can be easily set up.

To provide maximum assistance to users, I offer a detailed `RESTRICTIOINS_TUTORIAL.md` on how to setup `RESTRICTION_CONFIG` effectively.

### Rarity Weights in CSV files (Enhanced version)

Now it is possible to feed the rarity weights using CSV files. This feature is more convenient than using simple data arrays, especially when dealing with large numbers of traits and for users who want to experiment with different rarity weights. CSV files are more user-friendly since they can be edited with regular spreadsheets.

### Other improvements (Enhanced version)

Users can effortlessly customize the deployment folder for assets, as well as the output folder for images and metadata. All these global settings are conveniently located within the `config.py` file.

Based on a personal experience where I needed to remove zero-padding from the output images and metadata filenames, I’ve introduced a global boolean variable in `config.py` called `ZERO_PAD`. This variable acts as a switch to enable or disable zero-padding.

In this version, we’ve improved efficiency by separating trait set generation from image creation. Data cleaning now occurs within a lightweight trait dataset table, eliminating the need for computationally expensive images that would later be discarded. This change was particularly noticeable after introducing the `RESTRICTIONS_CONFIG` feature, which significantly increases the rejection rate of image trait sets that don’t comply with the specified restriction rules.

## Installation

**Clone this repository**

```
git clone https://github.com/divelez69/generative-art-nft-with-restrictions.git
```

**Install required packages**

```
pip install Pillow pandas progressbar2
```

## Configuration

**Setup initial configuration**

Begin by uploading your input assets to the `assets` folder. Next, complete the `config.py` file by carefully following the instructions provided within it.

**Setup Rarities**

Setup the `rarity weights`. You can simply fill up arrays for each category, but I encourage you to use CSV files. Set the value for `'rarity_weights'` to `'file'` within `config.py`, and then run `python nft.py` for the first time. This will automatically create the CSVs for you. Stop the execution, so you can edit the CSVs using your preferred spreadsheet software. If needed, you can delete a CSV file and run the script again to create a new one with preloaded values.

**Setup restriction rules**

Setup the `RESTRICTIONS_CONFIG` in `restrictions.py`. This is a crucial step for defining unwanted trait combinations and ensure the production of clean and beautiful avatars. I encourage you to read the tutorial in `RESTRICTIONS_TUTORIAL.md` for further guidance.

## Production

**Generate the avatar images**

If all previous setups are done correctly, execute:

```
python nft.py
```

...and you'll be guided to smoothly produce the avatar images you need...

However it’s unlikely that you’ll achieve immediate success in your initial attempts, because setting up restriction rules can be quite a complex endeavor. The script may encounter mismatches, typos, or code errors within the `RESTRICTIONS_CONFIG` located in `restrictions.py` file. These issues require debugging.

To mitigate these challenges, the script internally re-styles trait PNG filenames and their references within `RESTRICTIONS_CONFIG` to a “Title Style” format. This automatic re-styling resolves the majority of mismatches. However, some typos may still need manual attention during various iterations. It's important to note that this re-styling feature only works for traits, not for layer names. Be sure that layer names match those defined within `CONFIG` in `config.py`.

I understand that this process may appear daunting and challenging, but I encourage you to persevere. By clearly defining the necessary trait combination restrictions, you will ultimately create beautiful and clean avatar images.

**JSON metadata generation**

In order to generate JSON metadata, define BASE_NAME, BASE_IMAGE_URL, and BASE_JSON in `metadata.py`. Make the necessary adjustments according to the specifications of the platform and network you chose to launch your NFTs. Then, run:

```
python metadata.py
```

## About Pepeiyans, also known as TheCarlos

<img src='TheCarlos.gif' height="250" width="250" />

This library was created as part of the Pepeiyans (AKA TheCarlos) Project.

These funny guys are TheCarlos, and is a collection of 3.333 randomly generated NFTs on the SEI Network Blockchain. TheCarlos are meant for buyers. Last time they were seen in [Pallet](https://pallet.exchange/collection/pepeiyans) marketplace.

The community is built around learning about the NFT revolution, exploring its current use cases, discovering new applications, and finding members to collaborate on exciting projects with.

## Reference to old version:

For your reference, here are the links of the original code written by Rounak Banik

Original code repository: https://github.com/rounakbanik/generative-art-nft.git

Detailed tutorial of the original tool: [here](https://medium.com/scrappy-squirrels/tutorial-create-generative-nft-art-with-rarities-8ee6ce843133)

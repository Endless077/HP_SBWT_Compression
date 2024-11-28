#   __                _            _____   
#  [  |              (_)          / ___ `. 
#   | |.--.   ____   __  _ .--.  |_/___) | 
#   | '/'`\ \[_   ] [  |[ '/'`\ \ .'____.' 
#   |  \__/ | .' /_  | | | \__/ |/ /_____  
#  [__;.__.' [_____][___]| ;.__/ |_______| 
#                       [__|               

import logging
import bz2

###################################################################################################

def bzip2_encode(data):
    """
    Compress data using bzip2.

    Args:
        data (bytes): Input data to compress.

    Returns:
        bytes: Compressed data.
    """
    logging.debug("Starting bzip2 compression.")
    try:
        compressed_data = bz2.compress(data)
    except OSError as e:
        logging.error(f"Error during bzip2 compression: {e}")
        raise ValueError(f"Error during bzip2 compression: {e}")

    logging.debug("bzip2 compression completed.")
    return compressed_data

def bzip2_decode(compressed_data):
    """
    Decompress data using bzip2.

    Args:
        compressed_data (bytes): The compressed data to decompress.

    Returns:
        bytes: Decompressed data.
    """
    logging.debug("Starting bzip2 decompression.")
    try:
        decompressed_data = bz2.decompress(compressed_data)
        logging.debug("bzip2 decompression completed.")
        return decompressed_data
    except OSError as e:
        logging.error(f"Error during bzip2 decompression: {e}")
        raise ValueError(f"Error during bzip2 decompression: {e}")

###################################################################################################

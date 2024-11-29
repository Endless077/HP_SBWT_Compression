# ____    ____                          _            ________                          _    
#|_   \  /   _|                        / |_         |_   __  |                        / |_  
#  |   \/   |   .--.   _   __  .---.  `| |-' .--.     | |_ \_|_ .--.   .--.   _ .--. `| |-' 
#  | |\  /| | / .'`\ \[ \ [  ]/ /__\\  | | / .'`\ \   |  _|  [ `/'`\]/ .'`\ \[ `.-. | | |   
# _| |_\/_| |_| \__. | \ \/ / | \__.,  | |,| \__. |  _| |_    | |    | \__. | | | | | | |,  
#|_____||_____|'.__.'   \__/   '.__.'  \__/ '.__.'  |_____|  [___]    '.__.' [___||__]\__/  
                                                                                           
import logging
from collections import deque

###################################################################################################

# Move-to-Front Encoding
def mft_encode(data):
    """
    Encodes the input data using the Move-to-Front (MTF) algorithm.

    Args:
        data (bytes): Input data to encode.

    Returns:
        tuple: A tuple containing the encoded list of indices and the list of unique symbols.
    """
    logging.debug("Starting Move-to-Front (MTF) encoding.")

    # Unique symbols collection from data in the order they appear
    symbols = []
    index_map = {}
    for byte in data:
        if byte not in index_map:
            index_map[byte] = len(symbols)
            symbols.append(byte)

    # Move-To-Front list init with the unique symbols
    mtf_list = deque(symbols)
    encoded = []

    # Encode the data using the MTF algorithm
    for byte in data:
        # Get the index of the byte using the dictionary
        index = index_map[byte]
        encoded.append(index)

        # Update the MTF list and index_map
        mtf_list.remove(byte)
        mtf_list.appendleft(byte)
        index_map = {value: i for i, value in enumerate(mtf_list)}

    logging.debug("MTF encoding completed.")
    return encoded, symbols

# Move-to-Front Decoding
def mft_decode(encoded, symbols):
    """
    Decodes a list of indices into data using the Move-to-Front (MTF) algorithm.

    Args:
        encoded (list): List of indices to decode.
        symbols (list): Original list of unique symbols.

    Returns:
        bytes: Decoded data.
    """
    logging.debug("Starting Move-to-Front (MTF) decoding.")

    # Initialize the Move-To-Front list
    mtf_list = deque(symbols)
    decoded = []

    # Iterate over each index in the encoded data
    for index in encoded:
        # Validate the index to ensure it's within the valid range
        if index < 0 or index >= len(mtf_list):
            logging.error(f"Invalid MTF index: {index}")
            raise ValueError(f"Invalid index {index} in MTF decoding.")

        # Retrieve the byte corresponding to the current index
        byte = mtf_list[index]
        decoded.append(byte)

        # Update the MTF list
        mtf_list.remove(byte)
        mtf_list.appendleft(byte)

    logging.debug("MTF decoding completed.")
    return bytes(decoded)

###################################################################################################

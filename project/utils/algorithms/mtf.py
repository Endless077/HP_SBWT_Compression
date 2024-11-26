# ____    ____                          _            ________                          _    
#|_   \  /   _|                        / |_         |_   __  |                        / |_  
#  |   \/   |   .--.   _   __  .---.  `| |-' .--.     | |_ \_|_ .--.   .--.   _ .--. `| |-' 
#  | |\  /| | / .'`\ \[ \ [  ]/ /__\\  | | / .'`\ \   |  _|  [ `/'`\]/ .'`\ \[ `.-. | | |   
# _| |_\/_| |_| \__. | \ \/ / | \__.,  | |,| \__. |  _| |_    | |    | \__. | | | | | | |,  
#|_____||_____|'.__.'   \__/   '.__.'  \__/ '.__.'  |_____|  [___]    '.__.' [___||__]\__/  
                                                                                           
import logging

###################################################################################################

# Move-to-Front Encoding
def mft_encode(data):
    """
    Encodes the input data using the Move-to-Front (MTF) algorithm.
    
    Args:
        data (str): Input string to encode.
        
    Returns:
        tuple: A tuple containing the encoded list of indices and the list of unique symbols.
    """
    logging.debug("Starting Move-to-Front (MTF) encoding.")

    # Get unique symbols in sorted order
    symbols = sorted(set(data))

    # Setup the mtf symbols list
    mtf_list = symbols[:]

    # Map for fast index lookup
    mtf_dict = {char: idx for idx, char in enumerate(mtf_list)}
    encoded = []

    for char in data:
        if char not in mtf_dict:
            logging.error(f"Character '{char}' not found in MTF list.")
            raise ValueError(f"Character '{char}' not in the initial symbol list.")
        
        # Retrieve index
        index = mtf_dict[char]
        encoded.append(index)
        
        # Move the character to the front
        mtf_list.pop(index)       # Remove character from current position
        mtf_list.insert(0, char)  # Insert character at the front
        
        # Update MTF dictionary with new positions
        mtf_dict = {char: idx for idx, char in enumerate(mtf_list)}

    logging.debug("MTF encoding completed.")
    return encoded, symbols

# Move-to-Front Decoding
def mft_decode(encoded, symbols):
    """
    Decodes a list of indices into a string using the Move-to-Front (MTF) algorithm.
    
    Args:
        encoded (list): List of indices to decode.
        symbols (list): Original list of unique symbols.
        
    Returns:
        str: Decoded string.
    """
    logging.debug("Starting Move-to-Front (MTF) decoding.")

    # Setup the mtf symbols list
    mtf_list = symbols[:]
    decoded = []

    for index in encoded:
        if index < 0 or index >= len(mtf_list):
            logging.error(f"Invalid MTF index: {index}")
            raise ValueError(f"Invalid index {index} in MTF decoding.")
        
        # Retrieve the character at the given index
        char = mtf_list[index]
        decoded.append(char)
        
        # Move the character to the front
        mtf_list.pop(index)       # Remove character from current position
        mtf_list.insert(0, char)  # Insert character at the front

    logging.debug("MTF decoding completed.")
    return ''.join(decoded)

###################################################################################################

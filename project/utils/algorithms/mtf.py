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
        data (bytes): Input data to encode.

    Returns:
        tuple: A tuple containing the encoded list of indices and the list of unique symbols.
    """
    logging.debug("Starting Move-to-Front (MTF) encoding.")

    # Collect unique symbols from data in the order they appear
    symbols = []
    seen = set()
    for byte in data:
        if byte not in seen:
            seen.add(byte)
            symbols.append(byte)

    # Initialize the Move-To-Front list with the unique symbols
    mtf_list = symbols[:]
    encoded = []

    # Encode the data using the MTF algorithm
    for byte in data:
        # Find the index of the current byte in the MTF list
        index = mtf_list.index(byte)
        
        # Append the index to the encoded output
        encoded.append(index)

        # If the byte is not at the front, move it to the front
        if index != 0:
            # Remove the byte from its current position and insert it at the front
            mtf_list.insert(0, mtf_list.pop(index))

    # Log the completion of the encoding process
    logging.debug("MTF encoding completed.")

    # Return the encoded data and the list of unique symbols
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
    mtf_list = symbols[:]
    decoded = []

    # Iterate over each index in the encoded data
    for index in encoded:
        # Validate the index to ensure it's within the valid range
        if index < 0 or index >= len(mtf_list):
            logging.error(f"Invalid MTF index: {index}")
            raise ValueError(f"Invalid index {index} in MTF decoding.")

        # Retrieve the byte corresponding to the current index
        byte = mtf_list[index]

        # Append the byte to the decoded output
        decoded.append(byte)

        # If the byte is not at the front of the MTF list, move it to the front
        if index != 0:
            # Remove the byte from its current position and insert it at the front
            mtf_list.insert(0, mtf_list.pop(index))

    logging.debug("MTF decoding completed.")
    return bytes(decoded)


###################################################################################################

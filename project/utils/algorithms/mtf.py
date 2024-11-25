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

# Save MTF symbols
def save_symbols(f, symbols):
    """
    Saves the MTF symbols to a binary file.
    
    Args:
        f (file object): File object opened in binary write mode.
        symbols (list): List of unique symbols to save.
    """
    logging.debug("Saving Move-to-Front (MTF) symbols.")

    f.write(len(symbols).to_bytes(2, byteorder='big'))              # Write the number of symbols
    for symbol in symbols:
        symbol_bytes = symbol.encode('utf-8')
        f.write(len(symbol_bytes).to_bytes(1, byteorder='big'))     # Write symbol length
        f.write(symbol_bytes)                                       # Write symbol itself

    logging.debug("MTF symbols saved successfully.")

# Load MTF symbols
def load_symbols(f):
    """
    Loads MTF symbols from a binary file.
    
    Args:
        f (file object): File object opened in binary read mode.
        
    Returns:
        list: List of unique symbols loaded from the file.
    """
    logging.debug("Loading Move-to-Front (MTF) symbols.")

    symbols_length = int.from_bytes(f.read(2), byteorder='big')     # Read number of symbols
    symbols = []
    for _ in range(symbols_length):
        symbol_length = int.from_bytes(f.read(1), byteorder='big')  # Read symbol length
        symbol_bytes = f.read(symbol_length)                        # Read symbol bytes
        symbol = symbol_bytes.decode('utf-8')                       # Decode symbol
        symbols.append(symbol)

    logging.debug("MTF symbols loaded successfully.")
    return symbols

###################################################################################################

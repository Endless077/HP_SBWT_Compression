#    _____     ________  ____      ____ 
#   |_   _|   |  __   _||_  _|    |_  _|
#     | |     |_/  / /    \ \  /\  / /  
#     | |   _    .'.' _    \ \/  \/ /   
#    _| |__/ | _/ /__/ |    \  /\  /    
#   |________||________|     \/  \/         
#                                       

import logging

###################################################################################################

def lzw_encode(data):
    """
    Encodes the input data using the LZW algorithm.

    Args:
        data (list): List of symbols (integers) to encode.

    Returns:
        list: List of LZW codes.
    """
    logging.debug("Starting LZW encoding.")
    
    # Initialize the dictionary with all single symbols
    dictionary_size = 256
    dictionary = {bytes([i]): i for i in range(dictionary_size)}
    
    current_sequence = bytes()
    encoded_output = []
    
    # Create the dictionary
    for symbol in data:
        current_byte = bytes([symbol])
        combined_sequence = current_sequence + current_byte
        if combined_sequence in dictionary:
            current_sequence = combined_sequence
        else:
            encoded_output.append(dictionary[current_sequence])
            # Add combined_sequence to the dictionary
            dictionary[combined_sequence] = dictionary_size
            dictionary_size += 1
            current_sequence = current_byte
    
    # Add the last current_sequence to the output
    if current_sequence:
        encoded_output.append(dictionary[current_sequence])
    
    logging.debug("LZW encoding completed.")
    return encoded_output

def lzw_decode(encoded):
    """
    Decodes data encoded with LZW.

    Args:
        encoded (list): List of LZW codes to decode.

    Returns:
        list: List of decoded symbols (integers).
    """
    logging.debug("Starting LZW decoding.")
    
    if not encoded:
        return []
    
    # Initialize the dictionary with all single symbols
    dictionary_size = 256
    dictionary = {i: bytes([i]) for i in range(dictionary_size)}
    
    # Decode the bsequence
    decoded_bytes = bytearray()
    previous_sequence = dictionary[encoded[0]]
    decoded_bytes.extend(previous_sequence)
    
    # Decode the dictionary
    for code in encoded[1:]:
        if code in dictionary:
            current_sequence = dictionary[code]
        elif code == dictionary_size:
            current_sequence = previous_sequence + previous_sequence[:1]
        else:
            logging.error("Invalid LZW encoding.")
            raise ValueError("Invalid LZW encoding.")
        
        decoded_bytes.extend(current_sequence)
        
        # Add previous_sequence + current_sequence[0] to the dictionary
        dictionary[dictionary_size] = previous_sequence + current_sequence[:1]
        dictionary_size += 1
        
        previous_sequence = current_sequence
    
    # Convert bytes to symbols (integers)
    decoded_output = list(decoded_bytes)
    
    logging.debug("LZW decoding completed.")
    return decoded_output

###################################################################################################
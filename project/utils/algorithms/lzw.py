#    _____     ________  ____      ____ 
#   |_   _|   |  __   _||_  _|    |_  _|
#     | |     |_/  / /    \ \  /\  / /  
#     | |   _    .'.' _    \ \/  \/ /   
#    _| |__/ | _/ /__/ |    \  /\  /    
#   |________||________|     \/  \/         (Lempel-Ziv-Welch)  

import logging

###################################################################################################

def lzw_encode(data, initial_code_size=9, max_code_size=16):
    """
    Encodes the input data using an improved LZW algorithm with dynamic code size.

    Args:
        data (list): List of symbols (integers) to encode.
        initial_code_size (int): Initial bit size for codes.
        max_code_size (int): Maximum bit size for codes.

    Returns:
        list: Encoded LZW codes.
    """
    logging.debug("Starting improved LZW encoding.")
    
    # Initialize the dictionary with all single symbols
    dictionary_size = 256
    dictionary = {bytes([i]): i for i in range(dictionary_size)}
    
    current_sequence = bytes()
    encoded_output = []
    current_code_size = initial_code_size
    max_dictionary_size = 1 << current_code_size
    
    for symbol in data:
        current_byte = bytes([symbol])
        combined_sequence = current_sequence + current_byte
        if combined_sequence in dictionary:
            current_sequence = combined_sequence
        else:
            encoded_output.append(dictionary[current_sequence])
            
            # Add combined_sequence to the dictionary
            if dictionary_size < (1 << max_code_size):
                dictionary[combined_sequence] = dictionary_size
                dictionary_size += 1
                # Adjust code size if needed
                if dictionary_size == max_dictionary_size and current_code_size < max_code_size:
                    current_code_size += 1
                    max_dictionary_size = 1 << current_code_size
            else:
                # Reset dictionary if max size reached
                logging.debug("Dictionary size limit reached. Resetting dictionary.")
                dictionary = {bytes([i]): i for i in range(256)}
                dictionary_size = 256
                current_code_size = initial_code_size
                max_dictionary_size = 1 << current_code_size

            current_sequence = current_byte

    # Add the last current_sequence to the output
    if current_sequence:
        encoded_output.append(dictionary[current_sequence])
    
    logging.debug("Improved LZW encoding completed.")
    return encoded_output

def lzw_decode(encoded, initial_code_size=9, max_code_size=16):
    """
    Decodes data encoded with an improved LZW algorithm with dynamic code size.

    Args:
        encoded (list): List of LZW codes to decode.
        initial_code_size (int): Initial bit size for codes.
        max_code_size (int): Maximum bit size for codes.

    Returns:
        list: Decoded symbols (integers).
    """
    logging.debug("Starting improved LZW decoding.")
    
    if not encoded:
        return []
    
    # Initialize the dictionary with all single symbols
    dictionary_size = 256
    dictionary = {i: bytes([i]) for i in range(dictionary_size)}
    decoded_bytes = bytearray()
    current_code_size = initial_code_size
    max_dictionary_size = 1 << current_code_size
    
    previous_sequence = dictionary[encoded[0]]
    decoded_bytes.extend(previous_sequence)
    
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
        if dictionary_size < (1 << max_code_size):
            dictionary[dictionary_size] = previous_sequence + current_sequence[:1]
            dictionary_size += 1
            # Adjust code size if needed
            if dictionary_size == max_dictionary_size and current_code_size < max_code_size:
                current_code_size += 1
                max_dictionary_size = 1 << current_code_size
        else:
            # Reset dictionary if max size reached
            logging.debug("Dictionary size limit reached. Resetting dictionary.")
            dictionary = {i: bytes([i]) for i in range(256)}
            dictionary_size = 256
            current_code_size = initial_code_size
            max_dictionary_size = 1 << current_code_size
        
        previous_sequence = current_sequence
    
    # Convert bytes to symbols (integers)
    decoded_output = list(decoded_bytes)
    
    logging.debug("Improved LZW decoding completed.")
    return decoded_output

###################################################################################################

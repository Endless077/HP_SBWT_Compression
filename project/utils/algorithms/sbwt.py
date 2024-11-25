#    ______   ______  ____      ____  _________  
#  .' ____ \ |_   _ \|_  _|    |_  _||  _   _  | 
#  | (___ \_|  | |_) | \ \  /\  / /  |_/ | | \_| 
#   _.____`.   |  __'.  \ \/  \/ /       | |     
#  | \____) | _| |__) |  \  /\  /       _| |_    
#   \______.'|_______/    \/  \/       |_____|   
#                                                

import logging
import hashlib
import numpy as np
from collections import defaultdict

###################################################################################################

# Generate a custom order based on the provided key
def generate_order_from_key(input_string, key):
    """
    Generates a custom character order based on a key.
    
    Args:
        input_string (str): The input string to generate the order for.
        key (str): The key used to generate the custom order.
        
    Returns:
        dict: A mapping of characters to their custom order indices.
    """
    logging.debug("Generating custom order based on the key.")

    # Extract all unique characters from the input and sort them
    unique_chars = sorted(set(input_string))
    key_bytes = key.encode('utf-8')  # Convert the key into bytes

    # Compute hashes for each unique character
    char_hashes = []
    for c in unique_chars:
        # Combine the key and character, then compute its SHA-256 hash
        combined = key_bytes + c.encode('utf-8')
        hash_value = hashlib.sha256(combined).hexdigest()
        char_hashes.append((c, hash_value))

    # Sort characters by their hash values
    sorted_chars = sorted(char_hashes, key=lambda x: x[1])

    # Map characters to their custom order indices
    order = {char: idx for idx, (char, _) in enumerate(sorted_chars)}
    logging.debug(f"Custom order generated based on the key: {order}")
    return order

# Build a suffix array using a custom character order
def build_suffix_array_with_custom_order(s, custom_order):
    """
    Builds a suffix array using a custom character order.
    
    Args:
        s (str): The input string.
        custom_order (dict): A mapping of characters to their custom order indices.
        
    Returns:
        numpy.ndarray: The suffix array for the input string.
    """
    logging.debug("Building the suffix array with custom order.")

    # Length of the input string
    n = len(s)

    # Initial suffix indices
    suffix_array = np.arange(n, dtype=np.int32)

    # Ranks based on custom order
    rank = np.array([custom_order[c] for c in s], dtype=np.int32)

    k = 1
    while k < n:
        # Create tuple keys for sorting suffixes
        # (handle edge cases with -1)
        key = np.array([(rank[i], rank[i + k] if i + k < n else -1) for i in suffix_array ],
                       dtype=[('rank1', int), ('rank2', int)])

        # Sort suffix indices by their tuple keys
        sorted_indices = np.argsort(key, order=['rank1', 'rank2'])
        suffix_array = suffix_array[sorted_indices]

        # Update ranks for the sorted suffixes
        new_rank = np.zeros(n, dtype=np.int32)
        new_rank[suffix_array[0]] = 0
        for i in range(1, n):
            new_rank[suffix_array[i]] = new_rank[suffix_array[i - 1]] + (
                key[sorted_indices[i]] != key[sorted_indices[i - 1]])
        rank = new_rank

        # Double the step size
        k *= 2  

    logging.debug("Suffix array successfully built.")
    return suffix_array

###################################################################################################

# SBWT Transform
def sbwt_encode(input_string, key):
    """
    Encode the input string using SBWT and a custom order based on the key.
    
    Args:
        input_string (str): The string to compress.
        key (str): The key used to generate the custom order.
        
    Returns:
        tuple: The compressed string (last column) and the original pointer.
    """
    logging.debug("Starting SBWT transform.")

    # Append the null terminator
    if '\0' not in input_string:
        input_string += '\0'
        logging.debug("Null terminator '\\0' added to the input.")

    # Generate custom order and suffix array
    custom_order = generate_order_from_key(input_string, key)
    suffix_array = build_suffix_array_with_custom_order(input_string, custom_order)

    # Construct the last column from the suffix array
    last_column = ''.join(input_string[i - 1] for i in suffix_array)

    # Find the original pointer
    try:
        orig_ptr = int(np.where(suffix_array == 0)[0][0])
    except IndexError as e:
        logging.error("Original pointer not found in the suffix array.")
        raise ValueError(f"Original pointer not found in the suffix array: {e}")

    logging.debug("SBWT transform completed.")
    return last_column, orig_ptr

# SBWT Inverse Transform
def sbwt_decode(last_column, orig_ptr, key):
    """
    Decode the SBWT-compressed string using the custom order based on the key.
    
    Args:
        last_column (str): The compressed string (last column of the matrix).
        orig_ptr (int): The original pointer to reconstruct the string.
        key (str): The key used to generate the custom order.
        
    Returns:
        str: The decompressed original string.
    """
    logging.debug("Starting SBWT inverse transform.")

    # Length of the compressed string
    n = len(last_column)

    # Generate custom order for the last column
    custom_order = generate_order_from_key(last_column, key)

    # Create the first column by sorting the last column using custom order
    first_col = ''.join(sorted(last_column, key=lambda c: (custom_order[c], c)))

    # Build mappings between the last and first columns
    count_last = defaultdict(int)
    first_indices = defaultdict(list)
    for idx, char in enumerate(first_col):
        first_indices[char].append(idx)

    # Map each index in the last column to the first column
    last_to_first = np.zeros(n, dtype=np.int32)
    for idx, char in enumerate(last_column):
        last_to_first[idx] = first_indices[char][count_last[char]]
        count_last[char] += 1

    # Reconstruct the original string
    original = []
    idx = orig_ptr
    for _ in range(n):
        original.append(last_column[idx])
        idx = last_to_first[idx]

    # Remove the null terminator and return the decompressed string
    decompressed = ''.join(reversed(original)).rstrip('\0')
    logging.debug("SBWT inverse transform completed.")
    return decompressed

###################################################################################################

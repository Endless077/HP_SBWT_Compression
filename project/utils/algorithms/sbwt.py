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

###################################################################################################

def generate_order_from_key(s, key):
    """
    Generates a custom order for characters based on the provided key.
    
    Args:
        s (str or bytes): Input string or data.
        key (str): Key to generate the custom order.

    Returns:
        dict: A dictionary mapping each character to its custom order index.
    """
    logging.debug("Generating custom order based on the key.")
    unique_chars = sorted(set(s))  # Extract unique characters from input
    key_bytes = key.encode('utf-8')

    # Create hashes for each character combined with the key
    char_hashes = []
    for c in unique_chars:
        c_bytes = bytes([c]) if isinstance(c, int) else c.encode('latin1')
        combined = key_bytes + c_bytes
        hash_value = hashlib.sha256(combined).hexdigest()
        char_hashes.append((c, hash_value))

    # Sort characters by their hash values
    sorted_chars = sorted(char_hashes, key=lambda x: x[1])
    order = {char: idx for idx, (char, _) in enumerate(sorted_chars)}

    logging.debug(f"Custom order generated: {order}")
    return order

def build_suffix_array_with_custom_order(s, custom_order):
    """
    Builds the suffix array of a string using a custom character order.
    
    Args:
        s (str or bytes): Input string or data.
        custom_order (dict): Mapping of characters to custom order indices.

    Returns:
        list: Suffix array of the string.
    """
    logging.debug("Building the suffix array with custom order.")
    n = len(s)  # Length of the input
    step_size = 1  # Initial comparison is based on the first character

    # Convert input to a list of integers if necessary (bytes or ord values)
    s_int = list(s) if isinstance(s, bytes) else [ord(c) for c in s]

    # Initialize ranks using the custom order of characters
    suffix_ranks = [custom_order[char] for char in s_int]
    temp_ranks = [0] * n  # Temporary storage for updated ranks
    suffix_array = list(range(n))  # Initial suffix array (0 to n-1)

    # Iteratively refine the suffix array
    while step_size < n:
        # Create sorting keys: (current rank, next rank) for each suffix
        sorting_keys = [
            (
                (suffix_ranks[i], suffix_ranks[i + step_size] if i + step_size < n else -1),
                i
            )
            for i in suffix_array
        ]
        
        # Sort the suffix indices based on the sorting keys
        sorting_keys.sort()
        suffix_array = [index for _, index in sorting_keys]

        # Update ranks based on sorted suffix indices
        new_rank = 0
        temp_ranks[suffix_array[0]] = new_rank  # First suffix gets rank 0
        for i in range(1, n):
            # If the current key is different from the previous, increment the rank
            if sorting_keys[i][0] != sorting_keys[i - 1][0]:
                new_rank += 1
            temp_ranks[suffix_array[i]] = new_rank

        # Prepare for the next iteration
        suffix_ranks = temp_ranks[:]
        step_size <<= 1  # Double the step size for the next iteration

    logging.debug("Suffix array built successfully.")
    return suffix_array

###################################################################################################

def sbwt_encode(data, key):
    """
    Encodes input data using SBWT and a custom key.
    
    Args:
        data (bytes): Input data to encode.
        key (str): Key used for transformation.

    Returns:
        tuple: The last column (bytes) and the original pointer (int).
    """
    logging.debug("Starting SBWT encoding.")
    
    # Ensure a terminator is present
    if data[-1] != 0:
        data += bytes([0])

    custom_order = generate_order_from_key(data, key)
    sa = build_suffix_array_with_custom_order(data, custom_order)
    n = len(sa)

    # Create the last column from the suffix array
    last_column = bytes([data[(idx - 1) % n] for idx in sa])
    orig_ptr = sa.index(0)

    logging.debug("SBWT encoding completed.")
    return last_column, orig_ptr

def sbwt_decode(last_column, orig_ptr, key):
    """
    Decodes data using the inverse SBWT and a custom key.
    
    Args:
        last_column (bytes): The last column from the SBWT encoding.
        orig_ptr (int): Original pointer used for reconstruction.
        key (str): Key used for transformation.

    Returns:
        bytes: The decoded original data.
    """
    logging.debug("Starting SBWT decoding.")
    
    n = len(last_column)
    custom_order = generate_order_from_key(last_column, key)

    # Count occurrences of each character
    count = np.zeros(256, dtype=int)
    for byte in last_column:
        count[byte] += 1

    # Calculate cumulative positions for each character
    cumulative_count = np.zeros(256, dtype=int)
    total = 0
    for i in range(256):
        cumulative_count[i] = total
        total += count[i]

    # Sort last_column using the custom order to form the first column
    first_column = sorted(
        [(byte, idx) for idx, byte in enumerate(last_column)],
        key=lambda x: (custom_order[x[0]], x[0])
    )

    # Map last_column positions to first_column positions
    t = np.zeros(n, dtype=int)
    char_positions = {i: [] for i in range(256)}
    for idx, byte in enumerate(last_column):
        char_positions[byte].append(idx)

    pos_in_char = {i: 0 for i in range(256)}
    for sorted_idx, (byte, _) in enumerate(first_column):
        orig_idx = char_positions[byte][pos_in_char[byte]]
        t[sorted_idx] = orig_idx
        pos_in_char[byte] += 1

    # Reconstruct the original data
    idx = orig_ptr
    decoded = bytearray()
    for _ in range(n - 1):  # Skip the terminator
        idx = t[idx]
        decoded.append(last_column[idx])

    logging.debug("SBWT decoding completed.")
    return bytes(decoded)

###################################################################################################
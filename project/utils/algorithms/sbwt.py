#    ______   ______  ____      ____  _________  
#  .' ____ \ |_   _ \|_  _|    |_  _||  _   _  | 
#  | (___ \_|  | |_) | \ \  /\  / /  |_/ | | \_| 
#   _.____`.   |  __'.  \ \/  \/ /       | |     
#  | \____) | _| |__) |  \  /\  /       _| |_    
#   \______.'|_______/    \/  \/       |_____|      (Scrambled Burrows-Wheeler Transform (SBWT))

import base64
import hashlib
import logging
from collections import Counter, defaultdict

###################################################################################################

EOF = b'\xFF'

###################################################################################################

def build_suffix_array(custom_order, data):
    """
    Builds the suffix array of a string using a custom character order.

    Args:
        custom_order (dict): Mapping of characters to custom order indices.
        data (str or bytes): Input string or data.

    Returns:
        list: Suffix array of the string.
    """
    logging.debug("Building the suffix array with custom order.")
    length = len(data)
    step_size = 1

    # Convert input to integers using custom order
    s_int = list(data) if isinstance(data, bytes) else [ord(c) for c in data]
    suffix_ranks = [custom_order[char] for char in s_int]
    suffix_array = list(range(length))

    # Iteratively refine the suffix array
    while step_size < length:
        # Use tuple of (current rank, next rank) as sorting key
        suffix_array.sort(key=lambda i: (
            suffix_ranks[i],
            suffix_ranks[i + step_size] if i + step_size < length else -1
        ))

        # Update ranks based on sorted suffix indices
        temp_ranks = [0] * length
        new_rank = 0
        temp_ranks[suffix_array[0]] = new_rank
        for i in range(1, length):
            prev, curr = suffix_array[i - 1], suffix_array[i]
            if (suffix_ranks[prev], suffix_ranks[prev + step_size] if prev + step_size < length else -1) != \
               (suffix_ranks[curr], suffix_ranks[curr + step_size] if curr + step_size < length else -1):
                new_rank += 1
            temp_ranks[curr] = new_rank

        # Update suffix ranks and double the step size
        suffix_ranks = temp_ranks
        step_size <<= 1

    logging.debug("Suffix array built successfully.")
    return suffix_array

###################################################################################################

def generate_order_from_key(data, key):
    """
    Generates a custom order for characters based on the provided key.
    
    Args:
        data (str or bytes): Input string or data.
        key (str): Key to generate the custom order.

    Returns:
        dict: A dictionary mapping each character to its custom order index.
    """
    logging.debug("Generating custom order based on the key.")

    # Extract unique characters from input
    unique_chars = set(data)
    key_bytes = key.encode('utf-8')

    # Create hashes for each character combined with the key
    char_hashes = []
    for c in unique_chars:
        c_bytes = bytes([c]) if isinstance(c, int) else c.encode('latin1')
        combined = key_bytes + c_bytes
        hash_value = hashlib.sha256(combined).digest()
        char_hashes.append((c, hash_value))

    # Sort characters by their hash values
    sorted_chars = sorted(char_hashes, key=lambda x: x[1])
    order = {char: idx for idx, (char, _) in enumerate(sorted_chars)}

    logging.debug(f"Custom order generated: {order}")
    return order

###################################################################################################

def key_derivation(key, block_number):
    """
    Derives a sub-key from a master key.

    Args:
        key (str): The master key, a string of alphanumeric characters.
        block_number (int): A block number used as an increment in the derivation process.

    Returns:
        str: A derived sub-key in base64 representation.
    """
    logging.debug("Derivation of sub-key by master key.")

    # Concatenating the key with the block number
    combined_key = f"{key}-{block_number}".encode('UTF-8')

    # Using a hash function (SHA-256) to derive the key
    derived_key = hashlib.sha256(combined_key).digest()

    # Convert the derived key to base64 for safe string representation
    encoded_key = base64.b64encode(derived_key).decode('ascii')

    logging.debug("Derivation of sub-key by master key complete.")
    return encoded_key

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
    if not data.endswith(EOF):
        data += EOF

    # Generate custom order from key
    custom_order = generate_order_from_key(data, key)

    # Build the suffix array
    suffix_array = build_suffix_array(custom_order, data)
    suffix_array_length = len(suffix_array)

    # Create the last column from the suffix array
    last_column = bytes([data[(idx - 1) % suffix_array_length] for idx in suffix_array])
    orig_ptr = suffix_array.index(0)

    logging.debug("SBWT encoding completed.")
    return last_column, orig_ptr

###################################################################################################

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
    count = Counter(last_column)

    # Calculate cumulative positions
    cumulative_count = {}
    total = 0
    for char in sorted(count.keys(), key=lambda x: custom_order[x]):
        cumulative_count[char] = total
        total += count[char]

    # Map last_column to first_column using cumulative positions
    next_pos = defaultdict(int)
    t = [0] * n
    for idx, char in enumerate(last_column):
        t_idx = cumulative_count[char] + next_pos[char]
        t[t_idx] = idx
        next_pos[char] += 1

    # Reconstruct the original data
    idx = orig_ptr
    decoded = bytearray()
    for _ in range(n - len(EOF)):  # Exclude the terminator
        idx = t[idx]
        decoded.append(last_column[idx])

    # Remove the terminator before returning
    if decoded[-len(EOF):] == EOF:
        decoded = decoded[:-len(EOF)]

    logging.debug("SBWT decoding completed.")
    return bytes(decoded)

###################################################################################################

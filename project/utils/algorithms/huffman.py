# ____  ____            ___    ___                              
#|_   ||   _|         .' ..] .' ..]                             
#  | |__| |  __   _  _| |_  _| |_  _ .--..--.   ,--.   _ .--.   
#  |  __  | [  | | |'-| |-''-| |-'[ `.-. .-. | `'_\ : [ `.-. |  
# _| |  | |_ | \_/ |, | |    | |   | | | | | | // | |, | | | |  
#|____||____|'.__.'_/[___]  [___] [___||__||__]\'-;__/[___||__]                                                              

import heapq
import logging
import numpy as np
from collections import Counter

# Node class for Huffman Tree
class HuffmanNode:
    """
    Represents a node in the Huffman tree.
    """
    def __init__(selfile, symbol=None, freq=0):
        selfile.symbol = symbol    # The symbol (character) stored in the node
        selfile.freq = freq        # Frequency of the symbol
        selfile.left = None        # Left child (subtree)
        selfile.right = None       # Right child (subtree)

    # Comparison operator for heap ordering
    def __lt__(selfile, other):
        return selfile.freq < other.freq

###################################################################################################

# Build Huffman Tree
def build_huffman_tree(data):
    """
    Constructs a Huffman tree from the input data.
    
    Args:
        data (str): The input data to be encoded.
        
    Returns:
        HuffmanNode: The root of the Huffman tree.
    """
    logging.debug("Starting Huffman tree construction.")

    # Count frequency of each symbol
    frequency = Counter(data)
    heap = [HuffmanNode(symbol, freq) for symbol, freq in frequency.items()]

    # Transform the list into a heap
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    
    logging.debug("Huffman tree successfully built.")
    return heap[0]

# Generate Huffman codes
def build_huffman_codes(root):
    """
    Generates Huffman codes for each symbol in the input data.
    
    Args:
        root (HuffmanNode): The root of the Huffman tree.
        
    Returns:
        dict: A dictionary mapping symbols to their Huffman codes.
    """
    logging.debug("Starting Huffman code generation.")

    # Init the stack trace and the codes
    stack = [(root, "")]
    codes = {}

    # Start the iterative codes generation
    while stack:
        node, current_code = stack.pop()
        if node is not None:
            if node.symbol is not None:
                codes[node.symbol] = current_code
            else:
                stack.append((node.right, current_code + "1"))
                stack.append((node.left, current_code + "0"))

    logging.debug("Huffman codes successfully generated.")
    return codes

# Helper function for padding operations
def apply_padding(bits, padding_length=None, mode='add'):
    """
    Adds or removes padding to ensure the bitstring is a multiple of 8.
    
    Args:
        bits (str): The bitstring to pad or unpad.
        padding_length (int): Number of padding bits to add or remove.
        mode (str): 'add' to apply padding, 'remove' to remove padding.
    
    Returns:
        tuple or str: Padded bitstring and padding length (if 'add'),
                      or bitstring without padding (if 'remove').
    """
    if mode == 'add':
        if padding_length is None:
            padding_length = (8 - len(bits) % 8) % 8
        padded_bits = bits + '0' * padding_length
        return padded_bits, padding_length
    elif mode == 'remove':
        if padding_length is None:
            raise ValueError("Padding length must be provided for removal.")
        unpadded_bits = bits[:-padding_length] if padding_length else bits
        return unpadded_bits
    else:
        raise ValueError("Invalid mode. Use 'add' or 'remove'.")

###################################################################################################

# Huffman encoding
def huffman_encode(data):
    """
    Encodes the input data using Huffman coding.
    
    Args:
        data (str): The input data to be encoded.
        
    Returns:
        tuple: Encoded bytes, Huffman codes, and padding length.
    """
    logging.debug("Starting Huffman encoding.")

    ## Build the Huffman Tree
    root = build_huffman_tree(data)
    huffman_codes = build_huffman_codes(root)
    encoded_bits = ''.join(huffman_codes[symbol] for symbol in data)

    # Add padding to make the length a multiple of 8
    encoded_bits, padding_length = apply_padding(encoded_bits, mode='add')

    # Convert the bit string into bytes
    byte_array = np.fromiter(
        (int(encoded_bits[i:i+8], 2) for i in range(0, len(encoded_bits), 8)),
        dtype=np.uint8
    )

    logging.debug("Huffman encoding completed.")
    return byte_array, huffman_codes, padding_length

# Huffman decoding
def huffman_decode(encoded_bytes, huffman_codes, padding_length):
    """
    Decodes the input encoded bytes using Huffman coding.
    
    Args:
        encoded_bytes (numpy.ndarray): Encoded data in bytes.
        huffman_codes (dict): Mapping of symbols to Huffman codes.
        padding_length (int): The length of padding added during encoding.
        
    Returns:
        list: The decoded data as a list of symbols.
    """
    logging.debug("Starting Huffman decoding.")

    # Convert bytes back into a bit string
    encoded_bits = ''.join(f'{byte:08b}' for byte in encoded_bytes)

    # Remove padding
    encoded_bits = apply_padding(encoded_bits, padding_length, mode='remove')

    # Reverse the Huffman code map for decoding
    reverse_codes = {v: k for k, v in huffman_codes.items()}
    decoded = []
    current_code = ""
    for bit in encoded_bits:
        current_code += bit
        if current_code in reverse_codes:
            decoded.append(reverse_codes[current_code])
            current_code = ""
    
    logging.debug("Huffman decoding completed.")
    return decoded

###################################################################################################

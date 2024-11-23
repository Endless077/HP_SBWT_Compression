# Huffman Encoding/Decodning

import heapq
import math
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

    # Init the codes dict
    codes = {}

    # Recursive function to generate codes
    def generate_codes(node, current_code):
        if node is None:
            return
        if node.symbol is not None:
            codes[node.symbol] = current_code
        generate_codes(node.left, current_code + "0")   # Traverse left subtree
        generate_codes(node.right, current_code + "1")  # Traverse right subtree

    generate_codes(root, "")
    logging.debug("Huffman codes successfully generated.")
    return codes

# Helper function for padding operations
def apply_padding(bits, padding_length=0, mode='add'):
    """
    Applies or removes padding to ensure the bitstring is a multiple of 8.
    
    Args:
        bits (str): The bitstring to pad or unpad.
        padding_length (int): The amount of padding to apply or remove.
        mode (str): 'add' to apply padding, 'remove' to remove padding.
        
    Returns:
        str: The modified bitstring.
    """
    if mode == 'add':
        padding_length = 8 - (len(bits) % 8) if len(bits) % 8 != 0 else 0
        return bits + '0' * padding_length, padding_length
    elif mode == 'remove' and padding_length > 0:
        return bits[:-padding_length]
    return bits

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

# Save Huffman codes
def save_huffman_codes(file, huffman_codes):
    """
    Saves Huffman codes to a file in an efficient format.
    
    Args:
        f (file object): The file to write to.
        huffman_codes (dict): Mapping of symbols to Huffman codes.
    """
    logging.debug("Saving Huffman codes.")

    # Write the number of codes
    file.write(len(huffman_codes).to_bytes(2, byteorder='big'))
    for symbol, code in huffman_codes.items():
        # Write the symbol (4 bytes)
        file.write(symbol.to_bytes(4, byteorder='big'))
        code_length = len(code)

        # Write code length
        file.write(code_length.to_bytes(1, byteorder='big'))
        code_bytes_length = math.ceil(code_length / 8)
        code_int = int(code, 2)
        code_bytes = code_int.to_bytes(code_bytes_length, byteorder='big')

        # Write the code bytes
        file.write(code_bytes)
    
    logging.debug("Huffman codes saved successfully.")

# Load Huffman codes
def load_huffman_codes(file):
    """
    Loads Huffman codes from a file.
    
    Args:
        f (file object): The file to read from.
        
    Returns:
        dict: Mapping of symbols to Huffman codes.
    """
    logging.debug("Loading Huffman codes.")

    huffman_codes = {}
    huffman_codes_length = int.from_bytes(file.read(2), byteorder='big')

    for _ in range(huffman_codes_length):
        # Read the symbol (4 bytes)
        symbol = int.from_bytes(file.read(4), byteorder='big')

        # Read code length
        code_length = int.from_bytes(file.read(1), byteorder='big')
        code_bytes_length = math.ceil(code_length / 8)

        # Read the code
        code_bytes = file.read(code_bytes_length)
        code_int = int.from_bytes(code_bytes, byteorder='big')
        code = bin(code_int)[2:].zfill(code_length)
        huffman_codes[symbol] = code
    
    logging.debug("Huffman codes loaded successfully.")
    return huffman_codes

###################################################################################################

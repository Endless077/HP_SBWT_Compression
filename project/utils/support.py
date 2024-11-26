#  ______                                            _    
#.' ____ \                                          / |_  
#| (___ \_|__   _  _ .--.   _ .--.    .--.   _ .--.`| |-' 
# _.____`.[  | | |[ '/'`\ \[ '/'`\ \/ .'`\ \[ `/'`\]| |   
#| \____) || \_/ |,| \__/ | | \__/ || \__. | | |    | |,  
# \______.''.__.'_/| ;.__/  | ;.__/  '.__.' [___]   \__/  
#                 [__|     [__|                           

from utils.algorithms.mtf import *
from utils.algorithms.sbwt import *
from utils.algorithms.huffman import *
from utils.algorithms.arithmetic import *

###################################################################################################

# Data Compression
def compress_data(input_data, key):
    """
    Compresses a block of data using SBWT, MTF, and Huffman encoding.

    Args:
        input_data (str): Input data to compress.
        key (str): Key used for SBWT encoding.

    Returns:
        dict: Contains compressed data and related metadata.
    """
    logging.debug("Start of data compression process.")

    # Encode Process
    last_column, orig_ptr = sbwt_encode(input_data, key)
    mtf_encoded, symbols = mft_encode(last_column)
    huffman_encoded, huffman_codes, padding_length = huffman_encode(mtf_encoded)
    
    logging.debug("Data compression process completed.")
    
    return {
        'data': huffman_encoded,
        'padding_length': padding_length,
        'orig_ptr': orig_ptr,
        'symbols': symbols,
        'huffman_codes': huffman_codes
    }

# Data Decompression
def decompress_data(compressed_data, key):
    """
    Decompresses a block of data encoded with SBWT, MTF, and Huffman encoding.

    Args:
        compressed_data (dict): Compressed data and metadata.
        key (str): Key used for SBWT decoding.

    Returns:
        str: Decompressed data.
    """
    logging.debug("Start of data decompression process.")
    
    # Retrive Metadata
    huffman_encoded = compressed_data['data']
    padding_length = compressed_data['padding_length']
    orig_ptr = compressed_data['orig_ptr']
    symbols = compressed_data['symbols']
    huffman_codes = compressed_data['huffman_codes']

    # Decode Process
    huffman_decoded = huffman_decode(huffman_encoded, huffman_codes, padding_length)
    mtf_decoded = mft_decode(huffman_decoded, symbols)
    decompressed = sbwt_decode(mtf_decoded, orig_ptr, key)
    
    logging.debug("Data decompression process completed.")
    
    return decompressed

###################################################################################################

# Single Block Compression (parallel task)
def compress_block(block_data, key):
    """
    Compresses a single block of data using the compression pipeline.

    Args:
        block_data (str): Input data for the block to compress.
        key (str): Key used for SBWT encoding.

    Returns:
        dict: A dictionary containing the compressed data and metadata.
    """
    logging.debug("Starting compression of a single block.")
    try:
        compressed_data = compress_data(block_data, key)
        logging.debug("Block compression completed successfully.")
        return compressed_data
    except Exception as e:
        logging.error(f"Error during block compression: {e}", exc_info=True)
        raise RuntimeError("Block compression failed.") from e

# Single Block Decompression (parallel task)
def decompress_block(compressed_data, key):
    """
    Decompresses a single block of compressed data using the decompression pipeline.

    Args:
        compressed_data (dict): A dictionary containing compressed data and metadata.
        key (str): Key used for SBWT decoding.

    Returns:
        str: The decompressed data as a string.
    """
    logging.debug("Starting decompression of a single block.")
    try:
        decompressed_data = decompress_data(compressed_data, key)
        logging.debug("Block decompression completed successfully.")
        return decompressed_data
    except Exception as e:
        logging.error(f"Error during block decompression: {e}", exc_info=True)
        raise RuntimeError("Block decompression failed.") from e

###################################################################################################

# Retreaving Symbols
def load_symbols(f):
    """
    Loads symbols from a binary file.
    
    Args:
        f (file object): File object opened in binary read mode.
        
    Returns:
        list: List of unique symbols loaded from the file.
    """
    logging.debug("Loading symbols.")

    symbols_length = int.from_bytes(f.read(2), byteorder='big')     # Read number of symbols
    symbols = []
    for _ in range(symbols_length):
        symbol_length = int.from_bytes(f.read(1), byteorder='big')  # Read symbol length
        symbol_bytes = f.read(symbol_length)                        # Read symbol bytes
        symbol = symbol_bytes.decode('utf-8')                       # Decode symbol
        symbols.append(symbol)

    logging.debug("symbols loaded successfully.")
    return symbols

# Storing Symbols
def save_symbols(f, symbols):
    """
    Saves the symbols to a binary file.
    
    Args:
        f (file object): File object opened in binary write mode.
        symbols (list): List of unique symbols to save.
    """
    logging.debug("Saving symbols.")

    f.write(len(symbols).to_bytes(2, byteorder='big'))              # Write the number of symbols
    for symbol in symbols:
        symbol_bytes = symbol.encode('utf-8')
        f.write(len(symbol_bytes).to_bytes(1, byteorder='big'))     # Write symbol length
        f.write(symbol_bytes)                                       # Write symbol itself

    logging.debug("Symbols saved successfully.")

###################################################################################################

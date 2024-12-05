#  ______                                            _
#.' ____ \                                          / |_
#| (___ \_|__   _  _ .--.   _ .--.    .--.   _ .--.`| |-'
# _.____`.[  | | |[ '/'`\ \[ '/'`\ \/ .'`\ \[ `/'`\]| |
#| \____) || \_/ |,| \__/ | | \__/ || \__. | | |    | |,
# \______.''.__.'_/| ;.__/  | ;.__/  '.__.' [___]   \__/
#                 [__|     [__|

# Compression Algorithms
from utils.algorithms.lzw import *
from utils.algorithms.bzip2 import *
from utils.algorithms.huffman import *
from utils.algorithms.arithmetic import *

# Transformation Algorithms
from utils.algorithms.mtf import *
from utils.algorithms.sbwt import *

###################################################################################################

# Data Compression
def compress_data(block_number, data, mode, key):
    """
    Compresses a block of data using SBWT, MTF, and specified encoding.

    Args:
        block_number (int): The block id number.
        data (bytes): The input data to be compressed.
        mode (str): The compression algorithm.
        key (str): Key used for SBWT encoding.

    Returns:
        dict: Contains compressed data and related metadata.
    """
    logging.debug(f"Compressing block {block_number} using mode '{mode}'.")

    if mode == 'bzip2':
        # bzip2 compression algorithm
        compressed_data = {
            'mode': mode,
            'block_number': block_number,
            'data': bzip2_encode(data)
        }
    else:
        # Transform with SBWT (Scrambled Burrows–Wheeler Transform)
        last_column, orig_ptr = sbwt_encode(data, key)
        logging.debug(f"SBWT Encoded Last Column: {last_column}")
        logging.debug(f"SBWT Original Pointer: {orig_ptr}")

        # Transform with MTF (Move To Front Transform)
        mtf_encoded, symbols = mft_encode(last_column)
        logging.debug(f"MTF Encoded: {mtf_encoded}")
        logging.debug(f"Symbols: {symbols}")

        if mode == 'lzw':
            # LZW (Lempel–Ziv–Welch) Encoding
            lzw_encoded = lzw_encode(mtf_encoded)
            compressed_data = {
                'mode': mode,
                'symbols': symbols,
                'data': lzw_encoded,
                'orig_ptr': orig_ptr,
                'block_number': block_number
            }
        elif mode == 'huffman':
            # Huffman Encoding
            huffman_encoded, huffman_codes, padding_length = huffman_encode(mtf_encoded)
            compressed_data = {
                'mode': mode,
                'symbols': symbols,
                'orig_ptr': orig_ptr,
                'data': huffman_encoded,
                'block_number': block_number,
                'huffman_codes': huffman_codes,
                'padding_length': padding_length
            }
        elif mode == 'arithmetic':
            # Arithmetic Encoding
            encoded_data_bytes = arithmetic_encode(mtf_encoded)
            compressed_data = {
                'mode': mode,
                'symbols': symbols,
                'orig_ptr': orig_ptr,
                'data': encoded_data_bytes,
                'block_number': block_number
            }
        else:
            logging.error(f"Unknown compression mode: {mode}")
            return None

    logging.debug(f"Block {block_number} compressed using mode '{mode}'.")
    return compressed_data

# Data Decompression
def decompress_data(block_number, compressed_data, key):
    """
    Decompresses a block of data encoded with specified encoding.

    Args:
        block_number (int): The block id number.
        compressed_data (dict): Compressed data and metadata.
        key (str): Key used for SBWT decoding.

    Returns:
        tuple: Block number and decompressed data.
    """
    # Retrieving the compression mode
    mode = compressed_data['mode']
    logging.debug(f"Decompressing block {block_number} using mode '{mode}'.")

    if mode == 'bzip2':
        # bzip2 decompression algorithm
        decompressed_data = bzip2_decode(compressed_data['data'])
    else:
        if mode == 'lzw':
            # LZW (Lempel–Ziv–Welch) Metadata
            symbols = compressed_data['symbols']
            lzw_encoded = compressed_data['data']
            orig_ptr = compressed_data['orig_ptr']

            # LZW (Lempel–Ziv–Welch) Decoding
            mtf_encoded = lzw_decode(lzw_encoded)
        elif mode == 'huffman':
            # Huffman Metadata
            symbols = compressed_data['symbols']
            orig_ptr = compressed_data['orig_ptr']
            huffman_encoded = compressed_data['data']
            huffman_codes = compressed_data['huffman_codes']
            padding_length = compressed_data['padding_length']

            # Huffman Decoding
            mtf_encoded = huffman_decode(huffman_encoded, huffman_codes, padding_length)
        elif mode == 'arithmetic':
            # Arithmetic Metadata
            symbols = compressed_data['symbols']
            orig_ptr = compressed_data['orig_ptr']
            encoded_data_bytes = compressed_data['data']

            # Arithmetic Decoding
            mtf_encoded = arithmetic_decode(encoded_data_bytes)
        else:
            logging.error(f"Unknown decompression mode: {mode}")
            return None

        if mode in ['huffman', 'arithmetic', 'lzw']:
            # Inverse Transform with MTF (Move To Front Transform)
            mtf_decoded = mft_decode(mtf_encoded, symbols)
            logging.debug(f"MTF Decoded: {mtf_decoded}")

            # Inverse Transform with SBWT (Scrambled Burrows–Wheeler Transform)
            decompressed_data = sbwt_decode(mtf_decoded, orig_ptr, key)
            logging.debug(f"SBWT Decoded Data: {decompressed_data}")
        else:
            logging.error(f"Unknown compression mode: {mode}")
            return None

    logging.debug(f"Block {block_number} decompressed using mode '{mode}'.")
    return (block_number, decompressed_data)

###################################################################################################

# Single Block Compression (parallel task)
def compress_block(args):
    """
    Compresses a single block of data using the compression pipeline.

    Args:
        args (tuple): Block information struct (block_number, input_data, mode, key).

    Returns:
        dict: A dictionary containing the compressed data and metadata.
    """
    logging.debug("Starting compression of a single block.")
    try:
        block_number, data, mode, key = args
        compressed_data = compress_data(block_number, data, mode, key)
        logging.debug("Block compression completed successfully.")
        return compressed_data
    except Exception as e:
        logging.error(f"Error during block compression: {e}", exc_info=True)
        raise RuntimeError("Block compression failed.") from e

# Single Block Decompression (parallel task)
def decompress_block(args):
    """
    Decompresses a single block of compressed data using the decompression pipeline.

    Args:
        args (tuple): Block information struct (block_number, compressed_data, key).

    Returns:
        tuple: Block number and the decompressed data.
    """
    logging.debug("Starting decompression of a single block.")
    try:
        block_number, compressed_data, key = args
        decompressed_data = decompress_data(block_number, compressed_data, key)
        logging.debug("Block decompression completed successfully.")
        return decompressed_data
    except Exception as e:
        logging.error(f"Error during block decompression: {e}", exc_info=True)
        raise RuntimeError("Block decompression failed.") from e

###################################################################################################

#   _____  _____  _    _   __          
#  |_   _||_   _|/ |_ (_) [  |         
#    | |    | | `| |-'__   | |  .--.   
#    | '    ' |  | | [  |  | | ( (`\]  
#     \ \__/ /   | |, | |  | |  `'.'.  
#      `.__.'    \__/[___][___][\__) ) 

# Logging
import logging

# Chars detector
import string
import chardet
from charset_normalizer import from_bytes

###################################################################################################

# Chunk Dimension (64 KB)
CHUNK_SIZE = 64 * 1024

###################################################################################################

# Char Detector
def char_detector(file_path, block_size=CHUNK_SIZE):
    """
    Detect the character encoding of a file using a specified block size.
    
    Args:
        file_path (str): Path to the file to be analyzed.
        block_siz_e (int): Number of bytes to read from the file for analysis.
        
    Returns:
        dict: A dictionary containing the detected encoding, confidence level, and language (if applicable).
    """
    # Open the file in binary mode
    with open(file_path, 'rb') as f:
        # Read the specified number of bytes from the file
        raw_data = f.read(block_size)
        
    # Use chardet to detect the encoding of the read data
    return chardet.detect(raw_data)

# Charset Detector
def charset_detector(file_path, block_size=CHUNK_SIZE):
    """
    Detect the encoding of a file using charset-normalizer.

    Args:
        file_path (str): Path to the file to analyze.
        block_size (int): Number of bytes to read for analysis (default: 256 KiB).

    Returns:
        dict: A dictionary containing:
            - 'encoding': The detected encoding (or None if not detected).
            - 'confidence': The confidence level of the detection.
            - 'is_text': True if the file is likely a text file, False otherwise.
    """
    try:
        with open(file_path, 'rb') as file:
            # Read a portion of the file
            raw_data = file.read(block_size)

        # Use charset-normalizer to detect encoding
        result = from_bytes(raw_data).best()

        if result:
            return {
                'encoding': result.encoding,
                'confidence': result.mean_mess_ratio,
                'is_text': True
            }
        else:
            return {
                'encoding': None,
                'confidence': 0.0,
                'is_text': False
            }

    except Exception as e:
        return {
            'error': str(e),
            'encoding': None,
            'confidence': 0.0,
            'is_text': False
        }

# Binary File Detector
def binary_detector(file_path, block_size=CHUNK_SIZE):
    # Text Characters set (Unicode + ASCII)
    text_characters = get_text_characters()

    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(block_size)
            
        # Identify non-printable characters in the chunk
        non_text_chars = [chr(c) for c in chunk if c not in text_characters]
        
        # Debug logs for non-printable characters
        logging.debug(f"Non-printable characters: {non_text_chars}")
        logging.debug(f"Number of non-printable characters: {len(non_text_chars)} out of {len(chunk)}")

        # Calculate the ratio of non-printable to total characters
        non_text_ratio = len(non_text_chars) / len(chunk) if len(chunk) > 0 else 0
        logging.debug(f"Non-printable character ratio: {non_text_ratio:.2f}")

        # Consider the file binary if the ratio exceeds 30%
        return non_text_ratio > 0.3
    except Exception as e:
        print(f"Error while reading the file: {e}")
        return False

###################################################################################################

# Get a Text Characters Set
def get_text_characters():
    # Unicode printable ranges (e.g., Latin-1, Greek, Cyrillic, etc.)
    unicode_ranges = (
        range(0x20, 0x7F),   # Basic Latin
        range(0xA0, 0x100),  # Latin-1 Supplement
        range(0x370, 0x400), # Greek and Coptic
        range(0x400, 0x500), # Cyrillic
        range(0x590, 0x600), # Hebrew
        range(0x600, 0x700), # Arabic
        range(0x4E00, 0x9FFF), # CJK Unified Ideographs
    )

    # Basic ASCII printable + newlines
    ascii_characters = bytes(string.printable, 'ascii') + b'\n\r\t'

    # Combine ranges into a single set of bytes
    unicode_characters = b''.join(bytes([c]) for r in unicode_ranges for c in r)

    return ascii_characters + unicode_characters

###################################################################################################

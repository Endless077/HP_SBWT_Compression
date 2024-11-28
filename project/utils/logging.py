#  _____                             _                   
# |_   _|                           (_)                  
#   | |       .--.   .--./)  .--./) __   _ .--.   .--./) 
#   | |   _ / .'`\ \/ /'`\; / /'`\;[  | [ `.-. | / /'`\; 
#  _| |__/ || \__. |\ \._// \ \._// | |  | | | | \ \._// 
# |________| '.__.' .',__`  .',__` [___][___||__].',__`  
#                  ( ( __))( ( __))             ( ( __)) 

import os
import logging

###################################################################################################

# Usage messages
USAGE_COMPRESSION = "Usage for compression:\npython3 script.py compress <lzw | bzip2 | huffman | arithmetic> <input_file> <output_file> <key | file.key>"
USAGE_DECOMPRESSION = "Usage for compression:\npython3 script.py decompress <input_file> <output_file> <key | file.key>"

###################################################################################################

# Logging compression/decompression metrics
def log_metrics(file_path, reference_size, operation):
    """
    Logs file size and size change percentage relative to a reference size.

    Args:
        file_path (str): Path to the file to measure.
        reference_size (int): Reference size in bytes.
        operation (str): Either 'compress' or 'decompress'.

    Returns:
        None
    """
    try:
        size = os.path.getsize(file_path)
        logging.info(f"{operation.capitalize()} file size: {size} bytes.")
        
        if reference_size > 0:
            change = ((size - reference_size) / reference_size) * 100
            if operation == "compress" and size < reference_size:
                logging.info(f"Size reduction: {abs(change):.2f}%")
            elif operation == "decompress" and change >= 0:
                logging.info(f"Size growth: {change:.2f}%")
            else:
                logging.warning(f"{operation.capitalize()} succeeded, but the resulting file size is unexpected: {change:.2f}% change.")
        else:
            logging.warning(f"The reference file is empty or invalid.")
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found. {operation.capitalize()} might have failed.")
    except Exception as e:
        logging.error(f"Error while calculating file size for {operation}: {e}", exc_info=True)

# Basic Log Configuration
logging.basicConfig(
    level=logging.INFO,
    format='[LOG] %(levelname)s - %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

###################################################################################################

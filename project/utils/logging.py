#  _____                             _                   
# |_   _|                           (_)                  
#   | |       .--.   .--./)  .--./) __   _ .--.   .--./) 
#   | |   _ / .'`\ \/ /'`\; / /'`\;[  | [ `.-. | / /'`\; 
#  _| |__/ || \__. |\ \._// \ \._// | |  | | | | \ \._// 
# |________| '.__.' .',__`  .',__` [___][___||__].',__`  
#                  ( ( __))( ( __))             ( ( __)) 

# Logging
import logging

# System libraries
import os
import sys
from datetime import datetime

###################################################################################################

# Usage messages
USAGE_COMPRESSION = "Usage for compression:\npython3 hpsbwt.py compress -m <lzw | bzip2 | huffman | arithmetic> -i <input_file> -o <output_file> -k <key | file.key> [-l <log_file>]"
USAGE_DECOMPRESSION = "Usage for decompression:\npython3 hpsbwt.py decompress -i <input_file> -o <output_file> -k <key | file.key> [-l <log_file>]"

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

# Setup Logging
def setup_logging(args, file=None):
    # Ensure the "logs" directory exists
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    log_filename = file
    
    if not file:
        # Generate the dynamic log file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.operation == "compress":
            log_suffix = f"{args.operation}_{args.mode}_{os.path.basename(args.input)}"
        else:
            log_suffix = f"{args.operation}_{os.path.basename(args.input)}"
            
        log_filename = os.path.join(logs_dir, f"log_{log_suffix}_{timestamp}.log")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[LOG] %(levelname)s - %(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.info(f"Logging configured with file: {log_filename}")
    return log_filename

###################################################################################################

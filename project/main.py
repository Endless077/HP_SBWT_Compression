# ____    ____          _            
#|_   \  /   _|        (_)           
#  |   \/   |   ,--.   __   _ .--.   
#  | |\  /| |  `'_\ : [  | [ `.-. |  
# _| |_\/_| |_ // | |, | |  | | | |  
#|_____||_____|\'-;__/[___][___||__] 
                                                                                                                             
# Multi-processing
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

# System libraries
import os
import sys
import time

# Support libraries
from utils.logging import *
from utils.support import *

###################################################################################################

# Block Dimension (64 KB)
BLOCK_SIZE = 64 * 1024

###################################################################################################

# Compress an input file in parallel blocks
def compress_file(input_file, output_file, key):
    """
    Compresses a file by dividing it into blocks and processing them in parallel.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to save the compressed file.
        key (str): Key for SBWT encoding.
    """
    logging.info(f"Starting compression: {input_file} -> {output_file}")
    
    # Check the input file
    if not os.path.isfile(input_file):
        logging.error(f"Input file '{input_file}' does not exist.")
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

    # Start the counter
    start_time = time.perf_counter()
    
    # Read the input file and split it into blocks
    blocks = []
    input_size = 0
    with open(input_file, 'r', encoding='utf-8') as fin:
        block_number = 0
        while True:
            input_data = fin.read(BLOCK_SIZE)
            if not input_data:
                break
            block_number += 1
            blocks.append((block_number, input_data))
            input_size += len(input_data)
    logging.info(f"Input file size: {input_size} bytes.")
    
    compressed_blocks = {}
    
    # Configure parallel processing with up to 60% of available CPU cores
    total_cores = multiprocessing.cpu_count()
    num_workers = max(1, int(total_cores * 0.6))
    logging.info(f"Using {num_workers} processes for parallel compression.")
    
    # Using ProcessPoolExecutor to compress blocks in parallel
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Start the process pool executor mapping
        futures = {executor.submit(compress_block, block_data, key): idx for idx, block_data in blocks}

        for future in as_completed(futures):
            idx = futures[future]
            try:
                compressed_data = future.result()
                compressed_blocks[idx] = compressed_data
            except Exception as e:
                logging.error(f"Error compressing block {idx}: {e}")
    
    # Count failed blocks after parallel compression
    failed_blocks = sum(1 for idx in range(1, block_number + 1) if compressed_blocks.get(idx) is None)
    if failed_blocks > 0:
        logging.error(f"{failed_blocks} blocks failed during compression. Process incomplete.")
        raise ValueError(f"{failed_blocks} blocks failed during compression. Process incomplete.")

    # Write compressed blocks to the output file
    with open(output_file, 'wb') as fout:
        for idx in range(1, block_number + 1):
            compressed_data = compressed_blocks.get(idx)
            if compressed_data is None:
                logging.error(f"Block {idx} missing. Incomplete compression.")
                continue
            
            logging.debug(f"Start writing compressed {idx} block.")

            # Write the block metadata
            fout.write(compressed_data['padding_length'].to_bytes(1, byteorder='big'))
            fout.write(compressed_data['orig_ptr'].to_bytes(4, byteorder='big'))

            save_symbols(fout, compressed_data['symbols'])
            save_huffman_codes(fout, compressed_data['huffman_codes'])

            fout.write(len(compressed_data['data']).to_bytes(4, byteorder='big'))
            fout.write(compressed_data['data'])

            logging.debug(f"Writing block {idx} completed.")
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    logging.info(f"Compression completed in {duration:.4f} seconds.")
    
    # Dimension of the compressed file
    log_metrics(output_file, input_size, "compress")

# Decompress an input file in parallel blocks
def decompress_file(input_file, output_file, key):
    """
    Decompresses a file by dividing it into blocks and processing them in parallel.

    Args:
        input_file (str): Path to the compressed input file.
        output_file (str): Path to save the decompressed file.
        key (str): Key for SBWT decoding.
    """
    logging.info(f"Starting decompression: {input_file} -> {output_file}")
    
    # Check the input file
    if not os.path.isfile(input_file):
        logging.error(f"Input file '{input_file}' does not exist.")
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")

    # Get the input file size
    compressed_size = os.path.getsize(input_file)
    logging.info(f"Compressed file size: {compressed_size} bytes.")

    # Start the counter
    start_time = time.perf_counter()

    # Read compressed file and parse it into blocks
    blocks = []
    with open(input_file, 'rb') as fin:
        while fin.tell() < compressed_size:
            block_number = len(blocks) + 1
            logging.debug(f"Beginning block reading: {block_number}.")

            # Read the block metadata
            padding_length = int.from_bytes(fin.read(1), byteorder='big')
            orig_ptr = int.from_bytes(fin.read(4), byteorder='big')

            symbols = load_symbols(fin)
            huffman_codes = load_huffman_codes(fin)

            data_length = int.from_bytes(fin.read(4), byteorder='big')
            huffman_encoded = bytearray(fin.read(data_length))

            # Build the block metadata struct
            compressed_data = {
                'data': huffman_encoded,
                'padding_length': padding_length,
                'orig_ptr': orig_ptr,
                'symbols': symbols,
                'huffman_codes': huffman_codes
            }
            blocks.append((block_number, compressed_data))

    # Only data block filter
    blocks = [block for block in blocks if block[1]['data']]
    logging.info(f"Total blocks to decompress: {len(blocks)}.")

    # Calculation of the maximum number of processes to use a maximum of 60% of the cores
    total_cores = multiprocessing.cpu_count()
    num_workers = max(1, int(total_cores * 0.6))
    logging.info(f"Using {num_workers} processes for parallel decompression.")

    # Using ProcessPoolExecutor to decompress blocks in parallel
    decompressed_blocks = {}
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Start the process pool executor mapping
        futures = {executor.submit(decompress_block, block_data, key): idx for idx, block_data in blocks}

        for future in as_completed(futures):
            idx = futures[future]
            try:
                decompressed_data = future.result()
                decompressed_blocks[idx] = decompressed_data
            except Exception as e:
                logging.error(f"Error decompressing block {idx}: {e}")

    # Count failed blocks after parallel decompression
    failed_blocks = sum(1 for idx in range(1, len(blocks) + 1) if decompressed_blocks.get(idx) is None)
    if failed_blocks > 0:
        logging.error(f"{failed_blocks} blocks failed during decompression. Process incomplete.")
        raise ValueError(f"{failed_blocks} blocks failed during decompression. Process incomplete.")

    with open(output_file, 'w', encoding='utf-8') as fout:
        for idx in range(1, len(blocks) + 1):
            decompressed_data = decompressed_blocks.get(idx)
            if decompressed_data is None:
                logging.error(f"Block {idx} missing. Incomplete decompression.")
                continue
            
            logging.debug(f"Start writing the decompressed {idx} block.")
            fout.write(decompressed_data)
            logging.debug(f"Writing block {idx} completed.")
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    logging.info(f"Decompression completed in {duration:.4f} seconds.")
    
    # Dimension of the decompressed file
    log_metrics(output_file, compressed_size, "decompress")

###################################################################################################

# Main Function
def main():
    # Ensure at least the operation is specified
    if len(sys.argv) < 5:
        print(f"{USAGE}")
        sys.exit(1)

    # Retrieve operation
    operation = sys.argv[1].lower()

    input_file = sys.argv[2]
    output_file = sys.argv[3]
    key = sys.argv[4]

    # Key validation
    if os.path.isfile(key):
        try:
            with open(key, 'r') as key_file:
                key = key_file.read().strip()
                logging.info(f"Key loaded from file: {key}")
        except Exception as e:
            logging.error(f"Failed to load key from file: {e}")
            sys.exit(1)

    if not key or len(key) < 16 or not key.isalnum():
        logging.error("Invalid key provided. The key must be at least 16 alphanumeric characters.")
        sys.exit(1)

    # Welcome Message
    print(r" ____  ____  _______     ______   ______  ____      ____  _________  ")
    print(r"|_   ||   _||_   __ \  .' ____ \ |_   _ \|_  _|    |_  _||  _   _  | ")
    print(r"  | |__| |    | |__) | | (___ \_|  | |_) | \ \  /\  / /  |_/ | | \_| ")
    print(r"  |  __  |    |  ___/   _.____`.   |  __'.  \ \/  \/ /       | |     ")
    print(r" _| |  | |_  _| |_     | \____) | _| |__) |  \  /\  /       _| |_    ")
    print(r"|____||____||_____|     \______.'|_______/    \/  \/       |_____|   (a High Performance SBWT Compression)")
    print(r"                                                                     ")

    # Operation execution
    if operation == "compress":
        compress_file(input_file, output_file, key)
    elif operation == "decompress":
        decompress_file(input_file, output_file, key)
    else:
        print(f"Operation not recognized. Use 'compress' or 'decompress'.")
        sys.exit(1)

if __name__ == "__main__":
    main()

###################################################################################################

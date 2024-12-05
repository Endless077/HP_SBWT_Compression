# ____    ____          _            
#|_   \  /   _|        (_)           
#  |   \/   |   ,--.   __   _ .--.   
#  | |\  /| |  `'_\ : [  | [ `.-. |  
# _| |_\/_| |_ // | |, | |  | | | |  
#|_____||_____|\'-;__/[___][___||__] 
                                                           
# Multi-processing
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

# Serialization
import msgpack as msg_classic
import msgpack_numpy as msg_np

# System libraries
import os
import sys
import time
import struct

# Support libraries
from utils.logging import *
from utils.support import *

###################################################################################################

# Block Dimension (64 KB)
BLOCK_SIZE = 64 * 1024

###################################################################################################

# Compress an input file in parallel blocks
def compress_file(input_file, output_file, extension, mode, key):
    """
    Compresses a file by dividing it into blocks and processing them in parallel.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to save the compressed file.
        mode (str): Compression mode.
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
    with open(input_file, 'rb') as fin:
        block_number = 0
        while True:
            input_data = fin.read(BLOCK_SIZE)
            if not input_data:
                break

            # Block subdivision
            blocks.append((block_number, input_data, extension, mode, key_derivation(key, block_number)))
            block_number += 1

            # Input file size calculation
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
        futures = {executor.submit(compress_block, args): args[0] for args in blocks}

        for future in as_completed(futures):
            idx = futures[future]
            try:
                compressed_data = future.result()
                if compressed_data:
                    compressed_blocks[idx] = compressed_data
                else:
                    logging.error(f"Compression failed for block {idx}.")
                    raise RuntimeError(f"Compression failed for block {idx}.")
            except Exception as e:
                logging.error(f"Error compressing block {idx}: {e}")
                raise RuntimeError(f"Error compressing block {idx}: {e}")

    # Count failed blocks after parallel compression
    failed_blocks = sum(1 for idx in range(block_number) if compressed_blocks.get(idx) is None)
    if failed_blocks > 0:
        logging.error(f"Failure of {failed_blocks} blocks failed during compression. Process incomplete.")
        raise RuntimeError(f"Failure of {failed_blocks} blocks failed during compression. Process incomplete.")
    
    # Write compressed blocks to the output file
    with open(output_file, 'wb') as fout:
        for idx in range(block_number):
            compressed_data = compressed_blocks.get(idx)
            if compressed_data is None:
                logging.error(f"Block {idx} missing. Incomplete compression.")
                raise RuntimeError(f"Block {idx} missing. Incomplete compression.")
            
            logging.debug(f"Start writing compressed {idx} block.")

            # Pack the data with msgpack serialization
            packed_data = msg_np.packb(compressed_data, use_bin_type=True)

            # Write data (unsigned int (I))
            fout.write(struct.pack('I', len(packed_data)))
            fout.write(packed_data)

            logging.debug(f"Writing block {idx} completed.")
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    logging.info(f"Compression completed in {duration:.4f} seconds.")
    
    # Dimension of the compressed file
    log_metrics(output_file, input_size, "compress")

###################################################################################################

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
        while True:
            try:
                # Get the data length
                data_length = fin.read(4)
                if not data_length:
                    break
                
                # Read the block length
                block_length = struct.unpack('I', data_length)[0]

                # Read the block data
                packed_data = fin.read(block_length)

                # Deserialize the block data
                compressed_data = msg_np.unpackb(packed_data, strict_map_key=False, raw=False)
                block_number = compressed_data['metadata'].get('block_number')

                # Append the compressed data block to the blocks list
                blocks.append((block_number, compressed_data, key_derivation(key, block_number)))
            except Exception as e:
                logging.error(f"Error reading block: {e}")
                raise RuntimeError(f"Error reading block: {e}")
    
    logging.info(f"Total blocks to decompress: {len(blocks)}.")

    # Calculation of the maximum number of processes to use a maximum of 60% of the cores
    total_cores = multiprocessing.cpu_count()
    num_workers = max(1, int(total_cores * 0.6))
    logging.info(f"Using {num_workers} processes for parallel decompression.")

    # Using ProcessPoolExecutor to decompress blocks in parallel
    decompressed_blocks = {}
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Start the process pool executor mapping
        futures = {executor.submit(decompress_block, args): args[0] for args in blocks}

        for future in as_completed(futures):
            idx = futures[future]
            try:
                block_number, extension, decompressed_data = future.result()
                if decompressed_data:
                    decompressed_blocks[idx] = decompressed_data
                else:
                    logging.error(f"Decompression failed for block {idx}.")
                    raise RuntimeError(f"Compression failed for block {idx}.")
            except Exception as e:
                logging.error(f"Error decompressing block {idx}: {e}")
                raise RuntimeError(f"Error decompressing block {idx}: {e}")

    # Count failed blocks after parallel decompression
    failed_blocks = sum(1 for idx in range(len(blocks)) if decompressed_blocks.get(idx) is None)
    if failed_blocks > 0:
        logging.error(f"Failure of {failed_blocks} blocks failed during decompression. Process incomplete.")
        raise RuntimeError(f"Failure of {failed_blocks} blocks failed during decompression. Process incomplete.")

    # Decompressed order block with the correct order
    sorted_blocks = [decompressed_blocks[idx] for idx in sorted(decompressed_blocks.keys())]
    
    # Write the blocks int the output file
    output_file = output_file + extension
    with open(output_file, 'wb') as fout:
        for decompressed_data in sorted_blocks:
            fout.write(decompressed_data)
    
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
        print(f"{USAGE_COMPRESSION}\n{USAGE_DECOMPRESSION}")
        sys.exit(1)

    # Retrieve operation
    operation = sys.argv[1].lower()

    # Operation type checking
    if operation == "compress":

        valid_modes = ['lzw', 'bzip2', 'huffman', 'arithmetic']
        mode = sys.argv[2].lower()
        if mode not in valid_modes:
            print(f"Invalid compression mode '{mode}'. Use one of {valid_modes}.")
            sys.exit(1)

        input_file = sys.argv[3]
        key = sys.argv[4]

        root, extension = os.path.splitext(input_file)
        output_file = root + ".bin"

    elif operation == "decompress":
        
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        key = sys.argv[4]

    else:
        print(f"Operation not recognized. Use 'compress' or 'decompress'.")
        sys.exit(1)

    # Key validation
    if os.path.isfile(key):
        try:
            with open(key, 'r') as key_file:
                key = key_file.read().strip()
                logging.info(f"Key loaded from file: {key}")
        except Exception as e:
            logging.error(f"Failed to load key from file: {e}")
            sys.exit(1)

    if not key or not (16 <= len(key) <= 32) or not key.isalnum():
        print("Invalid key provided. The key must be at least 16 to 32 alphanumeric characters.")
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
        compress_file(input_file, output_file, extension, mode, key)
    elif operation == "decompress":
        decompress_file(input_file, output_file, key)

if __name__ == "__main__":
    main()

###################################################################################################

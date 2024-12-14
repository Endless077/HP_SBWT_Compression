#     ______                                                            
#   .' ___  |                                                           
#  / .'   \_|  .--.   _ .--..--.  _ .--.   _ .--.  .---.  .--.   .--.   
#  | |       / .'`\ \[ `.-. .-. |[ '/'`\ \[ `/'`\]/ /__\\( (`\] ( (`\]  
#  \ `.___.'\| \__. | | | | | | | | \__/ | | |    | \__., `'.'.  `'.'.  
#   `.____ .' '.__.' [___||__||__]| ;.__/ [___]    '.__.'[\__) )[\__) ) 
#                                [__|                                   

# Multi-processing
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

# Serialization
import msgpack as msg_classic
import msgpack_numpy as msg_np

# System libraries
import os
import time
import struct
import logging

# Support library
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
    logging.info(f"Starting compression: {input_file} -> {output_file} with mode {mode}.")
    
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
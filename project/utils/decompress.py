#   ______                                                                            
#  |_   _ `.                                                                          
#    | | `. \ .---.  .---.   .--.   _ .--..--.  _ .--.   _ .--.  .---.  .--.   .--.   
#    | |  | |/ /__\\/ /'`\]/ .'`\ \[ `.-. .-. |[ '/'`\ \[ `/'`\]/ /__\\( (`\] ( (`\]  
#   _| |_.' /| \__.,| \__. | \__. | | | | | | | | \__/ | | |    | \__., `'.'.  `'.'.  
#  |______.'  '.__.''.___.' '.__.' [___||__||__]| ;.__/ [___]    '.__.'[\__) )[\__) ) 
#                                              [__|                                   

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

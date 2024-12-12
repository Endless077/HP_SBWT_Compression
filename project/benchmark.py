#   ______                           __                                  __       
#  |_   _ \                         [  |                                [  |  _   
#    | |_) |  .---.  _ .--.   .---.  | |--.   _ .--..--.   ,--.   _ .--. | | / ]  
#    |  __'. / /__\\[ `.-. | / /'`\] | .-. | [ `.-. .-. | `'\_ : [ `/'`\]| '' <   
#   _| |__) || \__., | | | | | \__.  | | | |  | | | | | | // | |, | |    | |`\ \  
#  |_______/  '.__.'[___||__]'.___.'[___]|__][___||__||__]\\'-;__/[___]  [__|  \_] 
#                                                                                 

# Logging
import logging

# Subprocess
import subprocess

# System
import os
import sys
import time
import argparse
from datetime import datetime

###################################################################################################

def setup_logging(path):
    log_folder = os.path.join(path, "results", "logs")
    os.makedirs(log_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_folder, f"log_{os.path.basename(path)}_{timestamp}.log")

    logging.basicConfig(
        format='[LOG] %(levelname)s - %(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    return log_file

###################################################################################################

def process_files(path, key):
    # Check the key
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
    print(" ______                           __                                  __       ")
    print("|_   _ \                         [  |                                [  |  _   ")
    print("  | |_) |  .---.  _ .--.   .---.  | |--.   _ .--..--.   ,--.   _ .--. | | / ]  ")
    print("  |  __'. / /__\\[ `.-. | / /'`\] | .-. | [ `.-. .-. | `'\_ : [ `/'`\]| '' <   ")
    print(" _| |__) || \__., | | | | | \__.  | | | |  | | | | | | // | |, | |    | |`\ \  ")
    print("|_______/  '.__.'[___||__]'.___.'[___]|__][___||__||__]\\'-;__/[___]  [__|  \_]") 
    print("                                                                               ")

    # Startup logging
    log_file = setup_logging(path)
    logging.info(f"Benchmark started on dataset {path}.")

    # Stats struct
    stats = {
        "total_tests": 0,
        "successful_tests": 0,
        "failed_tests": 0,
        "failed_files": [],
        "total_time": 0,
        "compression_ratios": {},
        "mode_times": {"bzip2": 0, "huffman": 0, "lzw": 0, "arithmetic": 0},
        "file_counts": {"bzip2": 0, "huffman": 0, "lzw": 0, "arithmetic": 0}
    }

    modes = ["bzip2", "huffman", "lzw", "arithmetic"]
    start_time = time.time()

    # Getting all files in the dataset
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    # Perform benchmark for all files
    for file_name in files:
        file_path = os.path.join(path, file_name)
        
        for mode in modes:
            compressed_path = os.path.join(path, "results", mode, f"{file_name}_compress")
            decompressed_path = os.path.join(path, "results", f"{file_name}_decompress")
            
            current_compress_file = f"{compressed_path}_{file_name}_{mode}"
            current_decompress_file = f"{decompressed_path}_{file_name}_{mode}"

            os.makedirs(os.path.dirname(compressed_path), exist_ok=True)
            os.makedirs(os.path.dirname(decompressed_path), exist_ok=True)

            try:
                stats["total_tests"] += 1
                start_mode_time = time.time()

                # Compression
                subprocess.run([
                    "python", "hpsbwt.py", "compress", "-m", mode, "-i", file_path, "-o", current_compress_file, "-k", key, "-l", log_file
                ], check=True)

                # Decompression
                subprocess.run([
                    "python", "hpsbwt.py", "decompress", "-i", current_compress_file, "-o", current_decompress_file, "-k", key, "-l", log_file
                ], check=True)

                # Diff Check
                with open(file_path, 'r') as original, open(current_decompress_file, 'r') as decompressed:
                    if original.read() != decompressed.read():
                        raise RuntimeError(f"Diff check failed for file {file_name} in mode {mode}")

                # Compute compression ratio
                original_size = os.path.getsize(file_path)
                compressed_size = os.path.getsize(current_compress_file)
                compression_ratio = compressed_size / original_size
                stats["compression_ratios"].setdefault(mode, []).append(compression_ratio)

                stats["successful_tests"] += 1
                logging.info(f"Test succeeded for file {file_name} in mode {mode}")

                # Update mode time
                elapsed_mode_time = time.time() - start_mode_time
                stats["mode_times"][mode] += elapsed_mode_time
                stats["file_counts"][mode] += 1

            except Exception as e:
                stats["failed_tests"] += 1
                stats["failed_files"].append(f"{file_name} (mode: {mode})")
                logging.error(f"Test failed for file {file_name} in mode {mode}: {str(e)}")

    stats["total_time"] = time.time() - start_time

    # Compute additional statistics
    average_mode_times = {
        mode: stats["mode_times"][mode] / stats["file_counts"].get(mode, 1)
        for mode in modes if stats["file_counts"].get(mode, 0) > 0
    }

    best_mode = min(average_mode_times, key=average_mode_times.get) if average_mode_times else None

    logging.info(f"Benchmark on dataset {path} completed.")

    # Stats logging
    logging.info(f"Total tests: {stats['total_tests']}")
    logging.info(f"Successful tests: {stats['successful_tests']}")
    logging.info(f"Failed tests: {stats['failed_tests']}")

    if stats["failed_tests"] > 0:
        logging.info("Failed files:")
        for failed_file in stats["failed_files"]:
            logging.info(f"- {failed_file}")

    logging.info(f"Total time: {stats['total_time']:.2f} s")

    for mode, ratios in stats["compression_ratios"].items():
        average_ratio = sum(ratios) / len(ratios)
        logging.info(f"Average compression ratio for {mode}: {average_ratio:.2f}")

    for mode, avg_time in average_mode_times.items():
        logging.info(f"Average time per file for {mode}: {avg_time:.2f} s")

    if best_mode:
        logging.info(f"Most efficient mode: {best_mode}")

    return stats

###################################################################################################

if __name__ == "__main__":
    # Input paser
    parser = argparse.ArgumentParser(description="Run compression and decompression tests on files in a folder.")
    parser.add_argument("dataset", help="Path to the dataset containing files to test.")
    parser.add_argument("key", help="Path to the file containing the encryption key.")

    args = parser.parse_args()

    # Process the dataset tests
    stats = process_files(args.dataset, args.key)

    sys.exit(0)

###################################################################################################

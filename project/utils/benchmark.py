#   ______                           __                                  __       
#  |_   _ \                         [  |                                [  |  _   
#    | |_) |  .---.  _ .--.   .---.  | |--.   _ .--..--.   ,--.   _ .--. | | / ]  
#    |  __'. / /__\\[ `.-. | / /'`\] | .-. | [ `.-. .-. | `'_\ : [ `/'`\]| '' <   
#   _| |__) || \__., | | | | | \__.  | | | |  | | | | | | // | |, | |    | |`\ \  
#  |_______/  '.__.'[___||__]'.___.'[___]|__][___||__||__]\'-;__/[___]  [__|  \_] 
#                                                                                 

import os
import sys
import time
import logging
import subprocess
from datetime import datetime

SUPPORTED_MODES = ["bzip2", "huffman", "lzw", "arithmetic"]

###################################################################################################

def initialize_stats():
    """
    Initializes and returns a dictionary structure to track statistics for the benchmark process.

    This structure is used to store and calculate various metrics related to the 
    performance and efficiency of compression and decompression tests across multiple modes.

    Returns:
        dict: A dictionary with the following keys:
            - total_tests (int): Total number of tests performed across all modes.
            - successful_tests (int): Number of successful compression/decompression tests.
            - failed_tests (int): Number of failed tests.
            - failed_files (list): List of tuples (file, mode) for failed tests.
            - inefficient_compressions (int): Number of compressions where the size increased.
            - inefficient_files (list): List of tuples (file, mode) for inefficient compressions.
            - total_time (float): Total time taken for all tests in seconds.
            - compression_ratios (dict): Dictionary with modes as keys and lists of compression ratios as values.
            - compression_percentages (dict): Dictionary with modes as keys and average compression percentages as values.
            - inefficiency_rates (dict): Dictionary with modes as keys and percentages of inefficient compressions as values.
            - average_mode_times (dict): Dictionary with modes as keys and average processing times per file in seconds as values.
            - average_compression_ratios (dict): Dictionary with modes as keys and average compression ratios (efficient only) as values.
            - best_time_mode (str): Mode with the fastest average processing time.
            - best_compression_mode (str): Mode with the best average compression ratio.
            - best_combined_mode (str): Mode with the best combined time and compression efficiency.
            - mode_times (dict): Dictionary with modes as keys and total processing times in seconds as values.
            - file_counts (dict): Dictionary with modes as keys and the number of files processed as values.
    """
    return {
        "total_tests": 0,                                                       # Total number of tests performed across all modes
        "successful_tests": 0,                                                  # Number of successful compression/decompression tests
        "failed_tests": 0,                                                      # Number of failed tests
        "failed_files": [],                                                     # List of tuples (file, mode) for failed tests
        "inefficient_compressions": 0,                                          # Number of compressions where the size increased
        "inefficient_files": [],                                                # List of tuples (file, mode) for inefficient compressions
        "total_time": 0,                                                        # Total time taken for all tests in seconds
        "compression_ratios": {mode: [] for mode in SUPPORTED_MODES},           # List of compression ratios for each mode
        "compression_percentages": {mode: None for mode in SUPPORTED_MODES},    # Average compression percentage per mode
        "inefficiency_rates": {mode: 0 for mode in SUPPORTED_MODES},            # Percentage of inefficient compressions per mode
        "average_mode_times": {mode: None for mode in SUPPORTED_MODES},         # Average processing time per file in seconds for each mode
        "average_compression_ratios": {mode: None for mode in SUPPORTED_MODES}, # Average compression ratio (efficient only) per mode
        "best_time_mode": None,                                                 # Mode with the fastest average processing time
        "best_compression_mode": None,                                          # Mode with the best average compression ratio
        "best_combined_mode": None,                                             # Mode with the best combined time and compression efficiency
        "mode_times": {mode: 0 for mode in SUPPORTED_MODES},                    # Total processing time in seconds per mode
        "file_counts": {mode: 0 for mode in SUPPORTED_MODES},                   # Number of files processed per mode
    }

def setup_logging(path):
    """
    Sets up logging for the benchmark process. Creates necessary folders for logs
    and initializes the logging configuration. Returns the log folder path, log file path,
    and a timestamp for consistent file naming.

    Args:
        path (str): The base path where the results/logs folders will be created.

    Returns:
        tuple: A tuple containing:
            - log_folder (str): The path to the folder where logs are stored.
            - log_file (str): The full path to the log file.
            - timestamp (str): The timestamp used for consistent file naming.
    """
    log_folder = os.path.join(path, "results", "logs")
    os.makedirs(log_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_folder, f"log_{os.path.basename(path)}_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='[LOG] %(levelname)s - %(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.info("Let's Start Benchmark.")
    logging.info("Logging setup complete.")
    return log_folder, log_file, timestamp

###################################################################################################

def compress_file(file_path, compressed_path, mode, key, log_file):
    """
    Compresses a file using the specified mode and key.

    Args:
        file_path (str): Path to the input file.
        compressed_path (str): Path to store the compressed file.
        mode (str): Compression mode (bzip2, huffman, etc.).
        key (str): Encryption key.
        log_file (str): Path to the log file.

    Raises:
        RuntimeError: If the subprocess fails.
    """
    result = subprocess.call([
        "python", "hpsbwt.py", "compress", "-m", mode, "-i", file_path, "-o", compressed_path,
        "-k", key, "-l", log_file
    ])
    if result != 0:
        raise RuntimeError(f"Compression failed for file {file_path} in mode {mode}.")

def decompress_file(compressed_path, decompressed_path, mode, key, log_file):
    """
    Decompresses a file using the specified mode and key.

    Args:
        compressed_path (str): Path to the compressed file.
        decompressed_path (str): Path to store the decompressed file.
        mode (str): Decompression mode.
        key (str): Encryption key.
        log_file (str): Path to the log file.

    Raises:
        RuntimeError: If the subprocess fails.
    """
    result = subprocess.call([
        "python", "hpsbwt.py", "decompress", "-i", f"{compressed_path}.bin",
        "-o", decompressed_path, "-k", key, "-l", log_file
    ])
    if result != 0:
        raise RuntimeError(f"Decompression failed for file {compressed_path} in mode {mode}.")

def diff_check(original_file, decompressed_file):
    """
    Verifies that the decompressed file matches the original.

    Args:
        original_file (str): Path to the original file.
        decompressed_file (str): Path to the decompressed file.

    Returns:
        bool: True if the files match, False otherwise.
    """
    with open(original_file, 'rb') as original, open(decompressed_file, 'rb') as decompressed:
        return original.read() == decompressed.read()
    
def key_validation(key):
    """
    Validates the encryption key provided as input.

    If the key is a file path, it reads and validates the key from the file. 
    Otherwise, it directly validates the key string.

    Validation Criteria:
    - Key must be a string of length between 16 and 32 characters.
    - Key must contain only alphanumeric characters.

    Args:
        key (str): The encryption key or the path to a file containing the key.

    Returns:
        str: The validated key as a string.

    Raises:
        ValueError: If the key is invalid or if there is an error reading the key from a file.
    """
    if os.path.exists(key) and os.path.isfile(key):
        try:
            with open(key, 'r') as key_file:
                key = key_file.read().strip()
        except Exception as e:
            raise ValueError(f"Failed to load key from file: {e}")

    if not (16 <= len(key) <= 32 and key.isalnum()):
        raise ValueError("Invalid key provided. Must be a string of 16 to 32 alphanumeric characters.")

    return key


###################################################################################################

def process_files(path, log_file, key):
    """
    Runs compression and decompression benchmarks on all files in the dataset.

    Args:
        path (str): Path to the dataset.
        log_file (str): Path to the log file.
        key (str): Encryption key or path to a key file.

    Returns:
        dict: Fully calculated statistics collected during benchmarking.
    """
    if os.path.isfile(key):
        try:
            with open(key, 'r') as key_file:
                key = key_file.read().strip()
        except Exception as e:
            raise ValueError(f"Failed to load key from file: {e}")

    if not key or not (16 <= len(key) <= 32) or not key.isalnum():
        raise ValueError("Invalid key provided. Must be 16-32 alphanumeric characters.")

    # Initialize statistics structure
    stats = initialize_stats()

    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    start_time = time.time()

    for file_name in files:
        file_path = os.path.join(path, file_name)
        for mode in stats["mode_times"].keys():
            compressed_path = os.path.join(path, "results", mode, f"{file_name}_compress_{mode}")
            decompressed_path = os.path.join(path, "results", f"{file_name}_decompress_{mode}")
            os.makedirs(os.path.dirname(compressed_path), exist_ok=True)
            os.makedirs(os.path.dirname(decompressed_path), exist_ok=True)

            stats["total_tests"] += 1
            start_mode_time = time.time()

            try:
                # Compression
                compress_file(file_path, compressed_path, mode, key, log_file)

                # Compression efficiency
                original_size = os.path.getsize(file_path)
                compressed_size = os.path.getsize(f"{compressed_path}.bin")
                if compressed_size >= original_size:
                    stats["inefficient_compressions"] += 1
                    stats["inefficient_files"].append((file_name, mode))

                # Decompression
                decompress_file(compressed_path, decompressed_path, mode, key, log_file)

                # Diff check
                decompressed_file_path = decompressed_path + os.path.splitext(file_name)[1]
                if not diff_check(file_path, decompressed_file_path):
                    raise RuntimeError(f"Diff check failed for file {file_name} in mode {mode}.")

                # Calculate compression ratio
                compression_ratio = compressed_size / original_size
                stats["compression_ratios"].setdefault(mode, []).append(compression_ratio)

                # Update time and success count
                elapsed_time = time.time() - start_mode_time
                stats["mode_times"][mode] += elapsed_time
                stats["file_counts"][mode] += 1
                stats["successful_tests"] += 1

            except Exception:
                stats["failed_tests"] += 1
                stats["failed_files"].append((file_name, mode))

    stats["total_time"] = time.time() - start_time

    # Compute inefficiency rates, average compression ratios, and compression percentages
    for mode, ratios in stats["compression_ratios"].items():
        # Inefficiency rate
        inefficient_count = sum(1 for r in ratios if r > 1)
        total_cases = len(ratios)
        stats["inefficiency_rates"][mode] = (inefficient_count / total_cases * 100) if total_cases > 0 else 0

        # Average compression ratio (efficient compressions only)
        efficient_ratios = [r for r in ratios if r <= 1]
        stats["average_compression_ratios"][mode] = (
            sum(efficient_ratios) / len(efficient_ratios) if efficient_ratios else None
        )

        # Average compression percentage (efficient compressions only)
        if efficient_ratios:
            stats["compression_percentages"][mode] = (
                (1 - sum(efficient_ratios) / len(efficient_ratios)) * 100
            )
        else:
            stats["compression_percentages"][mode] = None  # No efficient compressions

    # Compute average times per mode
    stats["average_mode_times"] = {
        mode: stats["mode_times"][mode] / stats["file_counts"].get(mode, 1)
        for mode in stats["mode_times"]
        if stats["file_counts"][mode] > 0
    }

    # Compute best mode by time
    if stats["average_mode_times"]:
        stats["best_time_mode"] = min(stats["average_mode_times"], key=stats["average_mode_times"].get)

    # Compute best mode by compression
    compression_efficiency = {
        mode: sum(ratios) / len(ratios)
        for mode, ratios in stats["compression_ratios"].items()
        if ratios
    }
    if compression_efficiency:
        stats["best_compression_mode"] = min(compression_efficiency, key=compression_efficiency.get)

    # Compute Best mode by combined metric
    time_weight = 0.5
    compression_weight = 0.5
    efficiency_scores = {
        mode: (time_weight * stats["average_mode_times"].get(mode, float('inf')))
               + (compression_weight * compression_efficiency.get(mode, float('inf')))
        for mode in stats["mode_times"]
        if stats["file_counts"][mode] > 0
    }
    if efficiency_scores:
        stats["best_combined_mode"] = min(efficiency_scores, key=efficiency_scores.get)

    return stats

###################################################################################################
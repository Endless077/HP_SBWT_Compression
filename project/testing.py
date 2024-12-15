#   _________               _    _                   
#  |  _   _  |             / |_ (_)                  
#  |_/ | | \_|.---.  .--. `| |-'__   _ .--.   .--./) 
#      | |   / /__\\( (`\] | | [  | [ `.-. | / /'`\; 
#     _| |_  | \__., `'.'. | |, | |  | | | | \ \._// 
#    |_____|  '.__.'[\__) )\__/[___][___||__].',__`  
#                                           ( ( __)) 

# Logging
import logging

# Json
import json

# System
import os
import sys
import argparse

# Own modules
from utils.benchmark import *

###################################################################################################

if __name__ == "__main__":
    # Input parser
    parser = argparse.ArgumentParser(description="Run compression and decompression tests on files in a folder.")
    parser.add_argument("dataset", help="Path to the dataset containing files to test.")
    parser.add_argument("key", help="Path to the file containing the encryption key.")

    args = parser.parse_args()

    # Dataset path validation
    if not os.path.exists(args.dataset) or not os.path.isdir(args.dataset):
        logging.error("Dataset path is invalid or does not exist.")
        sys.exit(1)

    # Key validation
    try:
        key = key_validation(args.key)
    except ValueError as e:
        logging.error(e)
        sys.exit(1)

    # Welcome Message
    print(r" _____            _    _          ______    _                  _    ")    
    print(r"|_   _|          / |_ | |       .' ____ \  / |_               / |_  ")
    print(r"  | |      .---.`| |-'\_|.--.   | (___ \_|`| |-',--.   _ .--.`| |-' ")
    print(r"  | |   _ / /__\\| |    ( (`\]   _.____`.  | | `'_\ : [ `/'`\]| |   ")
    print(r" _| |__/ || \__.,| |,    `'.'.  | \____) | | |,// | |, | |    | |,  ")
    print(r"|________| '.__.'\__/   [\__) )  \______.' \__/\'-;__/[___]   \__/      (Benchmark on High Performance SBWT Compression")
    print(r"                                                                    ")

    # Setup logging
    log_folder, log_file, timestamp = setup_logging(args.dataset.rstrip(os.sep))
    json_folder = os.path.join(log_folder, "json")
    os.makedirs(json_folder, exist_ok=True)

    # Process the dataset tests
    stats = process_files(args.dataset, log_file, key)

    # Save benchmark results to JSON file
    report_file = os.path.join(json_folder, f"benchmark_results_{timestamp}.json")
    with open(report_file, "w") as json_file:
        json.dump(stats, json_file, indent=4)
    logging.info(f"Benchmark results saved to {report_file}.")

    # Print statistics
    logging.info("#" * 100)
    logging.info("--- Final Stats ---")
    logging.info("#" * 100)
    logging.info(f"Total tests: {stats['total_tests']}")
    logging.info(f"Total time: {stats['total_time']:.2f} s")
    logging.info(f"Successful tests: {stats['successful_tests']}")
    logging.info(f"Failed tests: {stats['failed_tests']}")

    # Failed tests and inefficient compressions
    if stats["failed_tests"] > 0:
        logging.info("--- Failed Files ---")
        for file, mode in stats["failed_files"]:
            logging.info(f"- {file} ({mode})")
    if stats["inefficient_compressions"] > 0:
        logging.info("--- Inefficient Files ---")
        for file, mode in stats["inefficient_files"]:
            logging.info(f"- {file} ({mode})")

    # Single mode statistics
    logging.info("--- Single mode Statistics ---")
    for mode in stats["compression_ratios"].keys():
        inefficiency_rate = stats["inefficiency_rates"].get(mode, 0)
        failed_rate = stats["failed_rates"].get(mode, 0)
        average_ratio = stats["average_compression_ratios"].get(mode)
        avg_time = stats["average_mode_times"].get(mode, None)

        if average_ratio is not None:
            average_compression_percent = (1 - average_ratio) * 100
        else:
            average_compression_percent = None

        logging.info(f"Mode: {mode}")
        logging.info(f"- Inefficiency rate: {inefficiency_rate:.2f}%")
        logging.info(f"- Failed rate: {failed_rate:.2f}%")
        if avg_time is not None:
            logging.info(f"- Average time per file: {avg_time:.2f} s")
        else:
            logging.info("- No time data available.")

        if average_ratio is not None:
            logging.info(f"- Average compression percent: {average_compression_percent:.2f}%")
            logging.info(f"- Average compression ratio (efficient only): {average_ratio:.2f}")
        else:
            logging.info("- No efficient compressions available.")

    # Best modes
    logging.info("--- Best Modes ---")
    if stats.get("best_time_mode"):
        logging.info(f"Best mode by time: {stats['best_time_mode']}")
    if stats.get("best_compression_mode"):
        logging.info(f"Best mode by compression: {stats['best_compression_mode']}")
    if stats.get("best_combined_mode"):
        logging.info(f"Best mode by combined metric: {stats['best_combined_mode']}")

    logging.info("#" * 100)
    sys.exit(0)

###################################################################################################

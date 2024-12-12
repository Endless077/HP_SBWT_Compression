# ____    ____          _            
#|_   \  /   _|        (_)           
#  |   \/   |   ,--.   __   _ .--.   
#  | |\  /| |  `'_\ : [  | [ `.-. |  
# _| |_\/_| |_ // | |, | |  | | | |  
#|_____||_____|\'-;__/[___][___||__] 
                                                           
# System libraries
import os
import sys
import argparse

# Support libraries
from utils.logging import *
from utils.support import *
from utils.compress import compress_file
from utils.decompress import decompress_file

###################################################################################################

# Main Function
def main():
    # Ensure at least the operation is specified
    if len(sys.argv) < 2:
        print(f"{USAGE_COMPRESSION}\n{USAGE_DECOMPRESSION}")
        sys.exit(1)

     # Argument parser setup
    parser = argparse.ArgumentParser(
        description="High Performance SBWT Compression/Decompression Tool"
    )

    # Common arguments
    parser.add_argument(
        "operation",
        choices=["compress", "decompress"],
        help="Operation to perform: 'compress' or 'decompress'"
    )
    parser.add_argument("-i", "--input", required=True, help="Input file")
    parser.add_argument("-o", "--output", required=True, help="Output file")
    parser.add_argument("-k", "--key", required=True, help="Private Key")
    parser.add_argument("-l", "--log", help="Optional log file")
    
    # Compression-specific arguments
    parser.add_argument("-m", "--mode", choices=["lzw", "bzip2", "huffman", "arithmetic"], required=False)

    args = parser.parse_args()

    # Welcome Message
    print(r" ____  ____  _______     ______   ______  ____      ____  _________  ")
    print(r"|_   ||   _||_   __ \  .' ____ \ |_   _ \|_  _|    |_  _||  _   _  | ")
    print(r"  | |__| |    | |__) | | (___ \_|  | |_) | \ \  /\  / /  |_/ | | \_| ")
    print(r"  |  __  |    |  ___/   _.____`.   |  __'.  \ \/  \/ /       | |     ")
    print(r" _| |  | |_  _| |_     | \____) | _| |__) |  \  /\  /       _| |_    ")
    print(r"|____||____||_____|     \______.'|_______/    \/  \/       |_____|   (a High Performance SBWT Compression)")
    print(r"                                                                     ")
    
    # Configure logging
    log_file = args.log if args.log else None
    setup_logging(args, file=log_file)
    
    # Retrieve and validate arguments
    operation = args.operation
    input_file = args.input
    output_file = args.output
    key = args.key
    mode = args.mode

 # Check operation-specific arguments
    if operation == "compress":
        if not mode:
            print(f"Compression mode is required.\n{USAGE_COMPRESSION}")
            sys.exit(1)

        # Add .bin extension to output for compression
        output_file += ".bin"
        _, extension = os.path.splitext(input_file)

    elif operation == "decompress":
        if mode:
            print(f"Mode is not for decompression.\n{USAGE_DECOMPRESSION}")
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

    # Execute operation
    if operation == "compress":
        compress_file(input_file, output_file, extension, mode, key)
    elif operation == "decompress":
        decompress_file(input_file, output_file, key)

if __name__ == "__main__":
    main()

###################################################################################################

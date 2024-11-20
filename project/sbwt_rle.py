# sbwt_rle.py
import os
import sys
import numpy as np
from tqdm import tqdm

# Function to build a suffix array with a progress bar
def build_suffix_array_with_progress(s):
    """
    Efficient construction of the suffix array with numpy arrays and progress bar.
    """
    n = len(s)                                              # Length of the input string
    suffix_array = np.arange(n, dtype=np.int32)             # Initial suffix array
    rank = np.array(list(map(ord, s)), dtype=np.int32)      # Ranks based on character ASCII values
    k = 1                                                   # Step size for comparison

    # Continue doubling the comparison step until the full string is processed
    while k < n:
        print(f"[LOG] Sorting with k={k}...")

        # Key for sorting using current rank and next rank
        key = np.array([(rank[i], rank[i + k] if i + k < n else -1) for i in suffix_array], 
                       dtype=[('rank1', int), ('rank2', int)])
        
        # Sort suffixes
        suffix_array = suffix_array[np.argsort(key, order=['rank1', 'rank2'])]

        # Update ranks based on the sorted order
        new_rank = np.zeros(n, dtype=np.int32)
        for i in range(1, n):
            new_rank[suffix_array[i]] = new_rank[suffix_array[i - 1]]
            if key[suffix_array[i]] != key[suffix_array[i - 1]]:
                new_rank[suffix_array[i]] += 1

        rank = new_rank     # Update rank array
        k *= 2              # Double the step size

    return suffix_array


# Function to compress a string using SBWT
def sbwt_compress(input_string):
    """
    Compress a string using the SBWT algorithm efficiently, with numpy.
    """
    # Convert the input string to an array of ASCII values
    ascii_string = np.array(list(map(ord, input_string)), dtype=np.uint16)

    # Length of the input string
    n = len(ascii_string)
    print(f"[LOG] Input string length: {n}")
    print(f"[LOG] Generating suffix array...")

    # Generate the suffix array
    suffix_array = build_suffix_array_with_progress(input_string)
    print(f"[LOG] Suffix array generated.")

    # Create the last column of the BWT matrix
    last_column = ''.join(chr(ascii_string[(i - 1) % n]) for i in suffix_array)
    
    # Identify the original string pointer
    orig_ptr = int(np.where(suffix_array == 0)[0][0])

    print(f"[DEBUG] Last column generated. Length: {len(last_column)}")
    print(f"[DEBUG] Original string pointer: {orig_ptr}")

    return last_column, orig_ptr


# Function to apply Run-Length Encoding (RLE) compression
def run_length_encode(data):
    """
    Apply Run-Length Encoding (RLE) to a string, escaping all non-alphanumeric characters.
    """
    print(f"[LOG] Applying RLE compression...")
    encoding = []           # List to store encoded segments
    prev_char = data[0]     # Initialize with the first character
    count = 1               # Initialize the count of the first character

    # Escaping function for non-alphanumeric characters
    def escape_char(c):
        return f"\\{ord(c)}" if not c.isalnum() else c

    # Iterate over the input data for RLE compression
    for char in data[1:]:
        # Increment count if the character is the same as the previous one
        if char == prev_char:
            count += 1
        else:
            # Append encoded format for the previous character
            encoding.append(f"{count}:{escape_char(prev_char)}")
            prev_char = char    # Update the current character
            count = 1           # Reset the count

    # Handle the last character
    encoding.append(f"{count}:{escape_char(prev_char)}")

    # Join all encoded segments into a string
    compressed = ','.join(encoding)
    print(f"[DEBUG] RLE compression complete. Original: {len(data)} bytes, Compressed: {len(compressed)} bytes.")
    return compressed


# Function to decode an RLE-compressed string
def run_length_decode(data):
    """
    Decode a Run-Length Encoded string, handling all escaped non-alphanumeric characters.
    """
    print(f"[LOG] Decoding with RLE...")
    decoded = []

    # Function to unescape characters (convert escaped ASCII code to character)
    def unescape_char(c):
        if c.startswith('\\'):
            return chr(int(c[1:]))
        return c

    # Split the encoded string and decode each block
    for block in data.split(','):
        if ':' in block:
            count, char = block.split(':', 1)                   # Separate count and character
            decoded.append(unescape_char(char) * int(count))    # Append decoded characters

    # Join all decoded segments
    decompressed = ''.join(decoded)
    print(f"[DEBUG] RLE decompression complete.")
    return decompressed


# Function to decompress a string using SBWT
def sbwt_decompress(last_column, orig_ptr):
    """
    Decompress a string using the SBWT algorithm, decoding ASCII values back to characters.
    """
    n = len(last_column)
    print(f"[LOG] Input string length (last column): {n}")

    # Generate the first column by sorting the last column
    first_col = ''.join(sorted(last_column))
    print(f"[DEBUG] First column generated with length: {len(first_col)}.")

    # Build a map to reconstruct the original string
    print(f"[LOG] Building next map...")
    next_map = np.zeros(n, dtype=np.int32)
    char_positions = {c: np.where(np.array(list(last_column)) == c)[0] for c in set(last_column)}

    # Track current positions for each character
    current_positions = {c: 0 for c in char_positions}
    for i, char in enumerate(first_col):
        next_map[i] = char_positions[char][current_positions[char]]
        current_positions[char] += 1

    print(f"[LOG] next_map constructed successfully.")

    # Reconstruct the original string using the map
    print(f"[LOG] Reconstructing the original string...")
    original = np.zeros(n, dtype='U1')                  # Initialize an array for the original string
    idx = orig_ptr                                      # Start from the original pointer
    for i in tqdm(range(n), desc="Reconstructing"):
        original[i] = first_col[idx]                    # Append the current character
        idx = next_map[idx]                             # Move to the next index

    return ''.join(original)


# Function to compress a file
def process_compression(input_file, compressed_file):
    """
    Compress a string from the input file and save the result to compressed file.
    """
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file '{input_file}' does not exist.")
        return

    # Read the input file
    with open(input_file, "r", encoding="utf-8") as f:
        input_string = f.read().strip()
    print(f"[LOG] Read input string of size: {len(input_string)} characters.")
    print(f"[LOG] Input file size: {os.path.getsize(input_file)} bytes")

    # Compress the string using SBWT
    last_column, orig_ptr = sbwt_compress(input_string)

    # Apply RLE compression
    rle_compressed = run_length_encode(last_column)

    # Save the compressed data to the output file
    with open(compressed_file, "w", encoding="utf-8") as f:
        f.write(f"{orig_ptr}\n{rle_compressed}")
    print(f"[LOG] Compressed data written to '{compressed_file}'.")
    print(f"[LOG] Compressed file size: {os.path.getsize(compressed_file)} bytes")


# Function to decompress a file
def process_decompression(compressed_file, decompressed_file):
    """
    Decompress a string from the compressed file and save the result to decompressed file.
    """
    # Check if the compressed file exists
    if not os.path.exists(compressed_file):
        print(f"[ERROR] Compressed file '{compressed_file}' does not exist.")
        return

    # Read the compressed file
    with open(compressed_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    orig_ptr = int(lines[0].strip())    # Extract the original pointer
    rle_compressed = lines[1].strip()   # Extract the RLE compressed data

    # Decode the RLE-compressed data
    last_column = run_length_decode(rle_compressed)

    # Decompress the string using SBWT
    decompressed_string = sbwt_decompress(last_column, orig_ptr)

    # Save the decompressed string to the output file
    with open(decompressed_file, "w", encoding="utf-8") as f:
        f.write(decompressed_string)
    print(f"[LOG] Decompressed output written to '{decompressed_file}'.")
    print(f"[LOG] Decompressed file size: {os.path.getsize(decompressed_file)} bytes")


# Main entry point for the script
if __name__ == "__main__":
    
    # Ensure sufficient arguments are provided
    if len(sys.argv) < 4:
        print("Usage: python sbwt4.py <compress|decompress> <input_file> <output_file>")
        sys.exit(1)

    operation = sys.argv[1]     # Operation type (compress or decompress)
    input_file = sys.argv[2]    # Input file path
    output_file = sys.argv[3]   # Output file path

    # Perform the specified operation
    if operation == "compress":
        process_compression(input_file, output_file)
    elif operation == "decompress":
        process_decompression(input_file, output_file)
    else:
        print(f"[ERROR] Unknown operation: {operation}")
        sys.exit(1)

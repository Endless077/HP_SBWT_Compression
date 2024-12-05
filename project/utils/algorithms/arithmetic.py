#        _                _   _   __                          _    _             ______                __   _                   
#       / \              (_) / |_[  |                        / |_ (_)          .' ___  |              |  ] (_)                  
#      / _ \     _ .--.  __ `| |-'| |--.   _ .--..--.  .---.`| |-'__   .---.  / .'   \_|  .--.    .--.| |  __   _ .--.   .--./) 
#     / ___ \   [ `/'`\][  | | |  | .-. | [ `.-. .-. |/ /__\\| | [  | / /'`\] | |       / .'`\ \/ /'`\' | [  | [ `.-. | / /'`\; 
#   _/ /   \ \_  | |     | | | |, | | | |  | | | | | || \__.,| |, | | | \__.  \ `.___.'\| \__. || \__/  |  | |  | | | | \ \._// 
#  |____| |____|[___]   [___]\__/[___]|__][___||__||__]'.__.'\__/[___]'.___.'  `.____ .' '.__.'  '.__.;__][___][___||__].',__`  
#                                                                                                                      ( ( __)) 

import logging
import struct

# Arithmetic Coder
from utils.algorithms.coders.arithmethic_coder import *

###################################################################################################

# Input BitStream
class InputStream:
    def __init__(self, data):
        # 'data' must be a bytes-like object. Bits are read sequentially.
        self.input = data
        self.byte_index = 0
        self.currentbyte = 0
        self.numbitsremaining = 0

    def read(self):
        # Returns the next bit (0 or 1), or -1 if end of data is reached.
        if self.numbitsremaining == 0:
            if self.byte_index >= len(self.input):
                return -1
            self.currentbyte = self.input[self.byte_index]
            self.byte_index += 1
            self.numbitsremaining = 8
        self.numbitsremaining -= 1
        return (self.currentbyte >> self.numbitsremaining) & 1

    def read_no_eof(self):
        # Return the next bit (0 or 1), or raises EOFError.
        result = self.read()
        if result == -1:
            raise EOFError("No more bits available.")
        return result

# Output BitStream
class OutputStream:
    def __init__(self):
        # Accumulates bits until a full byte is formed.
        self.buffer = bytearray()
        self.currentbyte = 0
        self.numbitsfilled = 0

    def write(self, b):
        # Writes a single bit (0 or 1).
        if b not in (0, 1):
            raise ValueError("Bit must be 0 or 1.")
        self.currentbyte = (self.currentbyte << 1) | b
        self.numbitsfilled += 1
        if self.numbitsfilled == 8:
            self.buffer.append(self.currentbyte)
            self.currentbyte = 0
            self.numbitsfilled = 0

    def getbytes(self):
        # Flushes any remaining bits (padded with zeros) and returns all data.
        if self.numbitsfilled > 0:
            self.currentbyte <<= (8 - self.numbitsfilled)
            self.buffer.append(self.currentbyte)
            self.currentbyte = 0
            self.numbitsfilled = 0
        return bytes(self.buffer)

###################################################################################################

def arithmetic_encode(data):
    """
    Encodes the given data using arithmetic coding in a minimal-overhead binary format.

    Args:
        data (list of int): A list of integers representing the data to encode.

    Returns:
        bytes: Encoded data as a bytes object.
    """
    logging.debug("Starting arithmetic encoding.")

    # Determine the maximum symbol to figure out the total number of symbols.
    max_symbol = max(data)
    num_symbols = max_symbol + 2  # Add 1 for the EOF symbol

    # Create an initial frequency table.
    initfreqs = FlatFrequencyTable(num_symbols)
    freqs = SimpleFrequencyTable(initfreqs)

    # Create an in-memory bit output stream.
    bitout = OutputStream()

    # Create the arithmetic encoder.
    enc = ArithmeticEncoder(32, bitout)

    # Encode the data.
    for symbol in data:
        enc.write(freqs, symbol)
        freqs.increment(symbol)

    # Write the EOF symbol.
    eof_symbol = num_symbols - 1
    enc.write(freqs, eof_symbol)
    enc.finish()

    # Get the compressed bytes.
    compressed_data = bitout.getbytes()

    # Pack num_symbols (unsigned int, big-endian) + compressed_data
    # '!I' = network order (big-endian) unsigned int (4 bytes)
    encoded_data_bytes = struct.pack("!I", num_symbols) + compressed_data

    logging.debug("Arithmetic encoding completed.")

    return encoded_data_bytes


def arithmetic_decode(encoded_data_bytes):
    """
    Decodes the given arithmetic-coded data from the custom binary format.

    Args:
        encoded_data_bytes (bytes): Encoded data as a bytes object.

    Returns:
        list of int: A list of integers representing the decoded data.
    """
    logging.debug("Starting arithmetic decoding.")

    # Read the first 4 bytes to get num_symbols
    if len(encoded_data_bytes) < 4:
        raise ValueError("Encoded data too short to contain header")

    num_symbols = struct.unpack("!I", encoded_data_bytes[:4])[0]
    compressed_data = encoded_data_bytes[4:]

    # Recreate the frequency table.
    initfreqs = FlatFrequencyTable(num_symbols)
    freqs = SimpleFrequencyTable(initfreqs)

    # Create an in-memory bit input stream.
    bitin = InputStream(compressed_data)

    # Create the arithmetic decoder.
    dec = ArithmeticDecoder(32, bitin)

    # Decode the data until the EOF symbol is reached.
    decoded_data = []
    while True:
        symbol = dec.read(freqs)
        if symbol == num_symbols - 1:  # EOF symbol
            break
        decoded_data.append(symbol)
        freqs.increment(symbol)

    logging.debug("Arithmetic decoding completed.")

    return decoded_data

###################################################################################################

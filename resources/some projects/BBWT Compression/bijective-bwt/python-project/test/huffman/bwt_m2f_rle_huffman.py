from test.huffman import COMPRESSED_HUFFMAN_DIR_PATH
from test.huffman import DECOMPRESSED_HUFFMAN_DIR_PATH
from test.huffman import generate_file_name

from pre_processing.bwt.encode import encode as bwt_encode
from pre_processing.bwt.decode import decode as bwt_decode

from pre_processing.rle import rle_e
from pre_processing.rle import rle_d

from pre_processing.mtf import m2f_e
from pre_processing.mtf import m2f_d

from compression.huffman import huffman_encoding
from compression.huffman import huffman_decoding

from util.file import read_in_chunks
from util.file import write_compressed_file
from util.file import read_compressed_file
from util.file import write_decompressed_file
from util.file_compare import compression_ratio_from_file

import os
import io

PRE_PROCESSING: str = "bwt_m2f_rle"
CHUNK_SIZE = io.DEFAULT_BUFFER_SIZE


def bwt_m2f_rle_huffman(file_path: str, file_name: str, alphabet: list[str], chunk_size=CHUNK_SIZE) -> dict:
    # open file
    _file = open(os.path.join(file_path, file_name))
    # generate file name of compressed file
    _file_name: str = os.path.splitext(file_name)[0]
    compressed_file_name: str = generate_file_name(_file_name, PRE_PROCESSING, chunk_size)

    # clone alphabet
    _alphabet = alphabet[:] + ['§']

    # apply bwt for each chunk
    bwt_encoded = ""
    for chunk in read_in_chunks(_file, chunk_size=chunk_size):
        # use bwt encoding
        bwt_encoded_chunk = bwt_encode(chunk)
        bwt_encoded += bwt_encoded_chunk
    # use m2f encoding
    m2f_encoded = m2f_e(bwt_encoded, _alphabet)
    # use rle encoding
    rle_encoded = rle_e(m2f_encoded)
    # use huffman encoding
    compressed_data, tree = huffman_encoding(rle_encoded)

    # write compressed file
    compressed_file_path = write_compressed_file(COMPRESSED_HUFFMAN_DIR_PATH, compressed_file_name, compressed_data)
    # read compressed file
    compressed_data = read_compressed_file(COMPRESSED_HUFFMAN_DIR_PATH, compressed_file_name)

    # use huffman decoding
    decompressed_data: str = huffman_decoding(compressed_data, tree)
    # use rle decoding
    rle_decoded = rle_d(decompressed_data)
    # init _alphabet
    _alphabet = alphabet[:] + ['§']
    # use m2f decoding
    m2f_decoded = m2f_d(rle_decoded, _alphabet)
    # use bwt decoding for each chunk
    for chunk in [m2f_decoded[i:i + chunk_size + 1]
                  for i in range(0, len(m2f_decoded), chunk_size + 1)]:
        bwt_decoded_chunk = bwt_decode(chunk)
        write_decompressed_file(DECOMPRESSED_HUFFMAN_DIR_PATH, compressed_file_name, bwt_decoded_chunk)

    compression_ratio = compression_ratio_from_file(os.path.join(file_path, file_name),
                                                    compressed_file_path)
    result = dict()
    result["PIPELINE"] = PRE_PROCESSING + '_huffman'
    result["RATIO"] = compression_ratio
    result["PATH"] = compressed_file_path
    return result

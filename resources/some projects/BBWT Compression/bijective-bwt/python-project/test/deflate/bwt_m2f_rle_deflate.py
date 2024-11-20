from test.deflate import COMPRESSED_DEFLATE_DIR_PATH
from test.deflate import DECOMPRESSED_DEFLATE_DIR_PATH
from test.deflate import generate_file_name

from pre_processing.bwt.encode import encode as bwt_encode
from pre_processing.bwt.decode import decode as bwt_decode

from pre_processing.rle import rle_e
from pre_processing.rle import rle_d

from pre_processing.mtf import m2f_e
from pre_processing.mtf import m2f_d

from compression.deflate import deflate as deflate_encoding
from compression.deflate import inflate as deflate_decoding

from util.file import read_in_chunks
from util.file import write_decompressed_file
from util.file import write_pickle
from util.file import read_pickle

import os
import io

PRE_PROCESSING: str = "bwt_m2f_rle"
CHUNK_SIZE = io.DEFAULT_BUFFER_SIZE


def bwt_m2f_rle_deflate(file_path: str, file_name: str, alphabet: list[str]) -> str:
    # open file
    _file = open(os.path.join(file_path, file_name))
    # generate file name of compressed file
    _file_name: str = os.path.splitext(file_name)[0]
    compressed_file_name: str = generate_file_name(_file_name, PRE_PROCESSING)

    # clone alphabet
    _alphabet = alphabet[:] + ['§']

    # apply bwt for each chunk
    bwt_encoded = ""
    for chunk in read_in_chunks(_file, chunk_size=CHUNK_SIZE):
        # use bwt encoding
        bwt_encoded_chunk = bwt_encode(chunk)
        bwt_encoded += bwt_encoded_chunk
    # use m2f encoding
    m2f_encoded = m2f_e(bwt_encoded, _alphabet)
    # use rle encoding
    rle_encoded = rle_e(m2f_encoded)
    # use deflate encoding
    compressed_data = deflate_encoding(rle_encoded)

    # write compressed file
    write_pickle(COMPRESSED_DEFLATE_DIR_PATH, compressed_file_name, compressed_data)
    # read compressed file
    compressed_data = read_pickle(COMPRESSED_DEFLATE_DIR_PATH, compressed_file_name)

    # use deflate decoding
    decompressed_data: str = deflate_decoding(compressed_data)
    # use rle decoding
    rle_decoded = rle_d(decompressed_data)
    # init _alphabet
    _alphabet = alphabet[:] + ['§']
    # use m2f decoding
    m2f_decoded = m2f_d(rle_decoded, _alphabet)
    # use bwt decoding for each chunk
    for chunk in [m2f_decoded[i:i + CHUNK_SIZE + 1]
                  for i in range(0, len(m2f_decoded), CHUNK_SIZE + 1)]:
        bwt_decoded_chunk = bwt_decode(chunk)
        write_decompressed_file(DECOMPRESSED_DEFLATE_DIR_PATH, compressed_file_name, bwt_decoded_chunk)

    return os.path.join(DECOMPRESSED_DEFLATE_DIR_PATH, compressed_file_name)

from test.deflate import COMPRESSED_DEFLATE_DIR_PATH
from test.deflate import DECOMPRESSED_DEFLATE_DIR_PATH
from test.deflate import generate_file_name

from pre_processing.bwt.encode import encode as bwt_encode
from pre_processing.bwt.decode import decode as bwt_decode

from pre_processing.mtf import m2f_e
from pre_processing.mtf import m2f_d

from compression.deflate import deflate as deflate_encoding
from compression.deflate import inflate as deflate_decoding

from util.file import read_in_chunks
from util.file import write_compressed_file_bytes
from util.file import read_compressed_file_bytes
from util.file import write_decompressed_file

import os
import io

PRE_PROCESSING: str = "bwt_m2f"
CHUNK_SIZE = io.DEFAULT_BUFFER_SIZE


def bwt_m2f_deflate(file_path: str, file_name: str, alphabet: list[str]) -> str:
    # open file
    _file = open(os.path.join(file_path, file_name))
    # generate file name of compressed file
    _file_name: str = os.path.splitext(file_name)[0]
    compressed_file_name: str = generate_file_name(_file_name, PRE_PROCESSING)

    # clone alphabet
    _alphabet = alphabet[:] + ['§']

    # apply bwt and m2f for each chunk
    m2f_encoded_chunks = []
    for chunk in read_in_chunks(_file, chunk_size=CHUNK_SIZE):
        # use bwt encoding
        bwt_encoded_chunk = bwt_encode(chunk)
        # use m2f encoding
        m2f_encoded_chunk = m2f_e(bwt_encoded_chunk, _alphabet)
        # append chunk
        m2f_encoded_chunks += m2f_encoded_chunk
    # use deflate encoding
    m2f_encoded_chunks = bytes(m2f_encoded_chunks)
    compressed_data = deflate_encoding(m2f_encoded_chunks)

    # write compressed file
    write_compressed_file_bytes(COMPRESSED_DEFLATE_DIR_PATH, compressed_file_name, compressed_data)
    # read compressed file
    compressed_data: str = read_compressed_file_bytes(COMPRESSED_DEFLATE_DIR_PATH, compressed_file_name)

    # use deflate decoding
    decompressed_data: str = deflate_decoding(compressed_data)
    # init _alphabet
    _alphabet = alphabet[:] + ['§']
    # for each chunk use m2f decoding and bwt decoding
    for chunk in [decompressed_data[i:i + CHUNK_SIZE + 1]
                  for i in range(0, len(decompressed_data), CHUNK_SIZE + 1)]:
        # use m2f decoding
        m2f_decoded_chunk = m2f_d(chunk, _alphabet)
        # use bwt decoding
        bwt_decoded_chunk = bwt_decode(m2f_decoded_chunk)
        write_decompressed_file(DECOMPRESSED_DEFLATE_DIR_PATH, compressed_file_name, bwt_decoded_chunk)

    return os.path.join(DECOMPRESSED_DEFLATE_DIR_PATH, compressed_file_name)

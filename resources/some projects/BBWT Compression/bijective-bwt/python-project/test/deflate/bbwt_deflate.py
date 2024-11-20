from test.deflate import COMPRESSED_DEFLATE_DIR_PATH
from test.deflate import DECOMPRESSED_DEFLATE_DIR_PATH
from test.deflate import generate_file_name

from pre_processing.bbwt_cfl.encode import encode as bbwt_encode
from pre_processing.bbwt_cfl.decode import decode as bbwt_decode

from compression.deflate import deflate as deflate_encoding
from compression.deflate import inflate as deflate_decoding

from util.file import read_in_chunks
from util.file import write_decompressed_file
from util.file import write_pickle
from util.file import read_pickle

import os
import io

PRE_PROCESSING: str = "bbwt"
CHUNK_SIZE = io.DEFAULT_BUFFER_SIZE


def bbwt_deflate(file_path: str, file_name: str) -> str:
    # open file
    _file = open(os.path.join(file_path, file_name))
    # generate file name of compressed file
    _file_name: str = os.path.splitext(file_name)[0]
    compressed_file_name: str = generate_file_name(_file_name, PRE_PROCESSING)

    # apply bbwt for each chunk
    bbwt_encoded = ""
    for chunk in read_in_chunks(_file, chunk_size=CHUNK_SIZE):
        # use bbwt encoding
        bbwt_encoded_chunk = bbwt_encode(chunk)
        bbwt_encoded += bbwt_encoded_chunk
    # use deflate encoding
    bbwt_encoded = bbwt_encoded.encode()
    compressed_data = deflate_encoding(bbwt_encoded)

    # write compressed file
    write_pickle(COMPRESSED_DEFLATE_DIR_PATH, compressed_file_name, compressed_data)
    # read compressed file
    compressed_data = read_pickle(COMPRESSED_DEFLATE_DIR_PATH, compressed_file_name)

    # use deflate decoding
    decompressed_data: str = deflate_decoding(compressed_data)
    # use bbwt decoding for each chunk
    for chunk in [decompressed_data[i:i + CHUNK_SIZE]
                  for i in range(0, len(decompressed_data), CHUNK_SIZE)]:
        bbwt_decoded_chunk = bbwt_decode(chunk)
        write_decompressed_file(DECOMPRESSED_DEFLATE_DIR_PATH, compressed_file_name, bbwt_decoded_chunk)

    return os.path.join(DECOMPRESSED_DEFLATE_DIR_PATH, compressed_file_name)

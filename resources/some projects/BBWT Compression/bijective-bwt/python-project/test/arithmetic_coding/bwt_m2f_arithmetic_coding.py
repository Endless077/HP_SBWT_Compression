from test.arithmetic_coding import COMPRESSED_ARITHMETIC_CODING_DIR_PATH
from test.arithmetic_coding import DECOMPRESSED_ARITHMETIC_CODING_DIR_PATH
from test.arithmetic_coding import generate_file_name

from pre_processing.bwt.encode import encode as bwt_encode
from pre_processing.bwt.decode import decode as bwt_decode

from pre_processing.mtf import m2f_e
from pre_processing.mtf import m2f_d

from compression.arithmetic_coding import arithmetic_encoding
from compression.arithmetic_coding import arithmetic_decoding

from util.file import read_in_chunks
from util.file import write_decompressed_file
from util.file import write_compressed_file_path_folder
from util.file_compare import compression_ratio_from_file

import os
import io

PRE_PROCESSING: str = "bwt_m2f"
CHUNK_SIZE = io.DEFAULT_BUFFER_SIZE


def bwt_m2f_arithmetic_coding(file_path: str, file_name: str, alphabet: list[str], chunk_size=CHUNK_SIZE) -> dict:
    # open and read file
    _file = open(os.path.join(file_path, file_name))
    # generate file name and file path of compressed file
    _file_name: str = os.path.splitext(file_name)[0]
    compressed_file_name: str = generate_file_name(_file_name, PRE_PROCESSING, chunk_size)
    compressed_file_path: str = write_compressed_file_path_folder(COMPRESSED_ARITHMETIC_CODING_DIR_PATH,
                                                                  compressed_file_name)
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
    # convert m2f encoding into a string
    m2f_encoded_string = ""
    for m2f_item in m2f_encoded:
        m2f_encoded_string += str(m2f_item) + ' '
    m2f_encoded_string = m2f_encoded_string[:-1].encode()
    with open('/tmp/temp', 'wb') as file:
        file.write(m2f_encoded_string)

    # use arithmetic encoding and write compressed file
    os.system(f'./ac/arithm-coding e /tmp/temp {compressed_file_path}')

    # use arithmetic decoding and write compressed file
    os.system(f'./ac/arithm-coding d {compressed_file_path} /tmp/temp-2')

    # read file
    with open('/tmp/temp-2', 'r') as file:
        decompressed_data = file.read()
    # convert decompressed_data into a integer list
    decompressed_data = list(map(int, decompressed_data.split(" ")))
    # init _alphabet
    _alphabet = alphabet[:] + ['§']
    # use m2f decoding
    m2f_decoded = m2f_d(decompressed_data, _alphabet)
    # use bbwt decoding for each chunk
    for chunk in [m2f_decoded[i:i + chunk_size + 1]
                  for i in range(0, len(m2f_decoded), chunk_size + 1)]:
        bwt_decoded_chunk = bwt_decode(chunk)
        write_decompressed_file(DECOMPRESSED_ARITHMETIC_CODING_DIR_PATH, compressed_file_name, bwt_decoded_chunk)

    compression_ratio = compression_ratio_from_file(os.path.join(file_path, file_name),
                                                    compressed_file_path)
    result = dict()
    result["PIPELINE"] = PRE_PROCESSING + '_arithmetic_coding'
    result["RATIO"] = compression_ratio
    result["PATH"] = compressed_file_path
    return result

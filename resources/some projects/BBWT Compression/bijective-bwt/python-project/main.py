from test.huffman.huffman import huffman
from test.huffman.bwt_m2f_huffman import bwt_m2f_huffman
from test.huffman.bbwt_m2f_huffman import bbwt_m2f_huffman
from test.huffman.bwt_m2f_rle_huffman import bwt_m2f_rle_huffman
from test.huffman.bbwt_m2f_rle_huffman import bbwt_m2f_rle_huffman

from test.arithmetic_coding.arithmetic_coding import arithmetic_coding
from test.arithmetic_coding.bwt_m2f_arithmetic_coding import bwt_m2f_arithmetic_coding
from test.arithmetic_coding.bbwt_m2f_arithmetic_coding import bbwt_m2f_arithmetic_coding
from test.arithmetic_coding.bwt_m2f_rle_arithmetic_coding import bwt_m2f_rle_arithmetic_coding
from test.arithmetic_coding.bbwt_m2f_rle_arithmetic_coding import bbwt_m2f_rle_arithmetic_coding

from test.lzw.lzw import lzw
from test.lzw.bwt_m2f_lzw import bwt_m2f_lzw
from test.lzw.bbwt_m2f_lzw import bbwt_m2f_lzw
from test.lzw.bwt_m2f_rle_lzw import bwt_m2f_rle_lzw
from test.lzw.bbwt_m2f_rle_lzw import bbwt_m2f_rle_lzw

from test.deflate.deflate import deflate
from test.deflate.bwt_m2f_deflate import bwt_m2f_deflate

from util.plot import plot_different_chunk_size
from util.plot import plot_different_pipeline

import os

# declare path of test files
PATH_DIR_TEST_FILES = os.path.join(os.getcwd(), "files")
# declare alphabet
ALPHABET: list[chr] = [chr(i) for i in range(128)]
# declare chunk size test
# CHUNK_SIZE_R = [0.0001, 0.000075, 0.00005, 0.000025, 0.00001]
CHUNK_SIZE_R = [0.001, 0.0025, 0.005, 0.0075, 0.01]


def test_different_pipeline(test: bool):
    for file_name in os.listdir(PATH_DIR_TEST_FILES):

        if test:
            if file_name != 'test.txt':
                continue
        else:
            if file_name == 'test.txt':
                continue

        # HUFFMAN TEST
        huffman(PATH_DIR_TEST_FILES, file_name)
        bwt_m2f_huffman(PATH_DIR_TEST_FILES, file_name, ALPHABET)
        bbwt_m2f_huffman(PATH_DIR_TEST_FILES, file_name, ALPHABET)
        bwt_m2f_rle_huffman(PATH_DIR_TEST_FILES, file_name, ALPHABET)
        bbwt_m2f_rle_huffman(PATH_DIR_TEST_FILES, file_name, ALPHABET)

        # ARITHMETIC-CODING TEST
        arithmetic_coding(PATH_DIR_TEST_FILES, file_name)
        bwt_m2f_arithmetic_coding(PATH_DIR_TEST_FILES, file_name, ALPHABET)
        bbwt_m2f_arithmetic_coding(PATH_DIR_TEST_FILES, file_name, ALPHABET)
        bwt_m2f_rle_arithmetic_coding(PATH_DIR_TEST_FILES, file_name, ALPHABET)
        bbwt_m2f_rle_arithmetic_coding(PATH_DIR_TEST_FILES, file_name, ALPHABET)

        # LZW TEST
        lzw(PATH_DIR_TEST_FILES, file_name)
        bwt_m2f_lzw(PATH_DIR_TEST_FILES, file_name, ALPHABET)
        bbwt_m2f_lzw(PATH_DIR_TEST_FILES, file_name, ALPHABET)
        bwt_m2f_rle_lzw(PATH_DIR_TEST_FILES, file_name, ALPHABET)
        bbwt_m2f_rle_lzw(PATH_DIR_TEST_FILES, file_name, ALPHABET)

        # DEFLATE TEST
        deflate(PATH_DIR_TEST_FILES, file_name)
        bwt_m2f_deflate(PATH_DIR_TEST_FILES, file_name, ALPHABET)


def test_different_chunk(test: bool):
    for file_name in os.listdir(PATH_DIR_TEST_FILES):

        if test:
            if file_name != 'test.txt':
                continue
        else:
            if file_name == 'test.txt':
                continue

        file_stat = os.stat(os.path.join(PATH_DIR_TEST_FILES, file_name))
        """
        results = []
        print(f"HUFFMAN TEST\n")
        for i in range(5):
            chunk_size = int(file_stat.st_size * CHUNK_SIZE_R[i]) + (file_stat.st_size % CHUNK_SIZE_R[i] > 0)
            print(f"Test with chunk size: {chunk_size}")
            # TEST HUFFMAN WITH DIFFERENT CHUNK SIZE
            _results = [huffman(PATH_DIR_TEST_FILES, file_name),
                        bwt_m2f_huffman(PATH_DIR_TEST_FILES, file_name, ALPHABET, chunk_size=chunk_size),
                        bbwt_m2f_huffman(PATH_DIR_TEST_FILES, file_name, ALPHABET, chunk_size=chunk_size),
                        bwt_m2f_rle_huffman(PATH_DIR_TEST_FILES, file_name, ALPHABET, chunk_size=chunk_size),
                        bbwt_m2f_rle_huffman(PATH_DIR_TEST_FILES, file_name, ALPHABET, chunk_size=chunk_size)]

            # append results
            results.append(_results)

        print(f"\nStart plotting results...")
        chunks_size = 5 * [0]
        for i in range(5):
            chunk_size = int(file_stat.st_size * CHUNK_SIZE_R[i]) + (file_stat.st_size % CHUNK_SIZE_R[i] > 0)
            chunks_size[i] = chunk_size
            print(f"Plot result with chunk size: {chunk_size}")
            plot_different_chunk_size(file_name, "huffman", chunk_size, results[i])

        for i in range(5):
            _results = [r[i] for r in results]
            pipeline = _results[0]["PIPELINE"]
            print(f"Plot result with pipeline: {pipeline}")
            plot_different_pipeline(file_name, pipeline, _results, chunks_size)

        """
        results = []
        print(f"\nARITHMETIC CODE TEST\n")
        for i in range(5):
            chunk_size = int(file_stat.st_size * CHUNK_SIZE_R[i]) + (file_stat.st_size % CHUNK_SIZE_R[i] > 0)
            print(f"Test with chunk size: {chunk_size}")

            # TEST HUFFMAN WITH DIFFERENT CHUNK SIZE
            _results = [arithmetic_coding(PATH_DIR_TEST_FILES, file_name),
                        bwt_m2f_arithmetic_coding(PATH_DIR_TEST_FILES, file_name, ALPHABET, chunk_size=chunk_size),
                        bbwt_m2f_arithmetic_coding(PATH_DIR_TEST_FILES, file_name, ALPHABET, chunk_size=chunk_size),
                        bwt_m2f_rle_arithmetic_coding(PATH_DIR_TEST_FILES, file_name, ALPHABET, chunk_size=chunk_size),
                        bbwt_m2f_rle_arithmetic_coding(PATH_DIR_TEST_FILES, file_name, ALPHABET, chunk_size=chunk_size)]

            # append results
            results.append(_results)

        print(f"\nStart plotting results...")
        chunks_size = 5 * [0]
        for i in range(5):
            chunk_size = int(file_stat.st_size * CHUNK_SIZE_R[i]) + (file_stat.st_size % CHUNK_SIZE_R[i] > 0)
            chunks_size[i] = chunk_size
            print(f"Plot result with chunk size: {chunk_size}")
            plot_different_chunk_size(file_name, "arithmetic_code", chunk_size, results[i])

        for i in range(5):
            _results = [r[i] for r in results]
            pipeline = _results[0]["PIPELINE"]
            print(f"Plot result with pipeline: {pipeline}")
            plot_different_pipeline(file_name, pipeline, _results, chunks_size)


if __name__ == '__main__':
    test_different_chunk(False)

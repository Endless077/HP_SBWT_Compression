import os.path as path
import os

COMPRESSED_HUFFMAN_DIR_PATH: str = path.join(os.getcwd(), 'compressed', 'huffman')
DECOMPRESSED_HUFFMAN_DIR_PATH: str = path.join(os.getcwd(), 'decompressed', 'huffman')
COMPRESSED_HUFFMAN_FILE_NAME: str = "{name}_{pre_processing}_huffman_{chunk_size}"


def generate_file_name(name: str, pre_processing: str, chunk_size: int) -> str:
    return COMPRESSED_HUFFMAN_FILE_NAME.format(name=name, pre_processing=pre_processing, chunk_size=chunk_size)

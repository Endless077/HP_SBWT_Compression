import os


def compression_ratio_from_file(uncompressed_path: str, compressed_path: str, decimal_digits=2) -> float:
    """ returns compression ratio for the input files. """
    uncompressed_size = os.path.getsize(uncompressed_path)
    compressed_size = os.path.getsize(compressed_path)

    if compressed_size == 0:
        return 0

    return round(uncompressed_size / compressed_size, decimal_digits)


# compare from two str
def compression_ratio(uncompressed_text: str, compressed_text: str, decimal_digits=2) -> float:
    """ returns compression ratio for the input texts. """
    uncompressed_size = len(uncompressed_text)
    compressed_size = len(compressed_text)

    if compressed_size == 0: return 0

    return round(uncompressed_size / compressed_size, decimal_digits)

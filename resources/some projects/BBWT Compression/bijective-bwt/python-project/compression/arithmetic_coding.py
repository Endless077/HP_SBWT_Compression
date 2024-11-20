import compression._arithmetic_utils as ae

import contextlib


def arithmetic_encoding(data: str, output_path: str) -> None:
    with contextlib.closing(ae.BitOutputStream(open(output_path, "wb"))) as bit_out:
        init_frequencies = ae.FlatFrequencyTable(257)
        frequencies = ae.SimpleFrequencyTable(init_frequencies)
        enc = ae.ArithmeticEncoder(32, bit_out)
        while True:
            # Read and encode one byte
            if len(data) > 0:
                symbol = chr(data[0]).encode()
                data = data[1:]
            else:
                break
            enc.write(frequencies, symbol[0])
            frequencies.increment(symbol[0])
        enc.write(frequencies, 256)  # EOF
        enc.finish()  # Flush remaining code bits


def arithmetic_decoding(input_path: str) -> str:
    with open(input_path, "rb") as inp:
        out = ""
        bit_in = ae.BitInputStream(inp)
        init_frequencies = ae.FlatFrequencyTable(257)
        frequencies = ae.SimpleFrequencyTable(init_frequencies)
        dec = ae.ArithmeticDecoder(32, bit_in)
        while True:
            # Decode and write one byte
            symbol = dec.read(frequencies)
            if symbol == 256:  # EOF symbol
                break
            out += chr(symbol)
            frequencies.increment(symbol)

    return out

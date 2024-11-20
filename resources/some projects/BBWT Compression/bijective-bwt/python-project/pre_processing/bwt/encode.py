from pre_processing.suffix_array import suffix_array_manber_myers


def encode(string: str) -> str:
    _string = string + '§'
    sa = suffix_array_manber_myers(_string)
    return "".join(_string[idx - 1] for idx in sa)


if __name__ == '__main__':
    print(encode('banana'))
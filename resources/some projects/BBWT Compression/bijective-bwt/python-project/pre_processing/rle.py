def rle_e(sequence):
    """Encode a sequence of characters and return the result as a list of tuples (data value and number of observed instances of value).
    Keyword arguments:
    sequence -- a sequence of characters to encode represented as a string.
    """
    count = 1
    result = []

    for x, item in enumerate(sequence):
        if x == 0:
            continue
        elif item == sequence[x - 1]:
            count += 1
        else:
            result.append((sequence[x - 1], count))
            count = 1

    result.append((sequence[len(sequence) - 1], count))

    return result


def rle_d(sequence):
    """Decodes the sequence and returns the result as a string.
    Keyword arguments:
    sequence -- a list of tuples (data value and number of observed instances of value).
    """
    result = []

    for item in sequence:
        for _ in range(item[1]):
            result.append(item[0])

    return result

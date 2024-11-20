def decode(data: str):
    t = _construct_t(data)  # return array the index of character
    out: [str] = [None] * len(data)
    i: int = len(data) - 1
    # for each j-th position of data
    for j in range(len(data)):
        if t[j] == -1:
            continue
        # set j-th position in k
        k = j
        while t[k] != -1:
            # return character of k position in i position
            out[i] = data[k]
            # decrement i
            i -= 1
            # set value of t[k] in temporary variable
            k_temp = t[k]
            # set value of t[k] equals to -1 because character has been used
            t[k] = -1
            k = k_temp
    return ''.join(out)


def _construct_t(data: str):
    t = [0] * len(data)
    counts = [0] * 65536  # Unicode code points
    # for each _-th character b
    for _, b in enumerate(data):
        # count occurrences of character b unicode code points
        counts[ord(b)] += 1
    cum_counts = [0] * 65536
    for i in range(1, 65536):
        # array that return position of first occurrences for each character.
        cum_counts[i] = cum_counts[i - 1] + counts[i - 1]

    # return position of all character.
    for i, b in enumerate(data):
        t[i] = cum_counts[ord(b)]
        cum_counts[ord(b)] += 1
    return t


if __name__ == "__main__":
    print(decode("annbaa"))

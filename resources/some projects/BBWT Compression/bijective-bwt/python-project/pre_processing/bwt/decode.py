def fm_index(bwt):
    fm = [{c: 0 for c in bwt}]
    for c in bwt:
        row = {symbol: count + 1 if (symbol == c) else count for symbol, count in fm[-1].items()}
        fm.append(row)
    offset = {}
    n = 0
    for symbol in sorted(row.keys()):
        offset[symbol] = n
        n += row[symbol]

    return fm, offset


def recover_suffix(i, bwt, fm_index, offset):
    suffix = ''
    c = bwt[i]
    predecessor = offset[c] + fm_index[i][c]
    suffix = c + suffix
    while predecessor != i:
        c = bwt[predecessor]
        predecessor = offset[c] + fm_index[predecessor][c]
        suffix = c + suffix
    return suffix


def decode(string: str) -> str:
    fm, offset = fm_index(string)
    i = string.index("§")
    s = recover_suffix(i, string, fm, offset)
    return s[:-1]


if __name__ == '__main__':
    print(decode('bnn§aaa'))

def cfl(string: str) -> [str]:
    """Returns Lyndon factorization of string"""
    words: [str] = []
    while len(string) > 0:
        i: int = 0
        j: int = 1
        while j < len(string) and string[i] <= string[j]:
            if string[i] == string[j]:
                i += 1
            else:
                i = 0
            j += 1
        l: int = j - i
        while i >= 0:
            words.append(string[:l])
            string = string[l:]
            i -= l
    return words


if __name__ == '__main__':
    print(cfl("banana"))

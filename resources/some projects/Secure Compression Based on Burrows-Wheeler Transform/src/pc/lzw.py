from math import floor, ceil
import pickle

#ASCII_TO_INT: dict = {i.to_bytes(1, 'big'): i for i in range(256)}
#INT_TO_ASCII: dict = {i
# : b for b, i in ASCII_TO_INT.items()}
max_dict_size_to_add = 600
max_dim_binary = 10

def compress(data: str) -> bytes:
    alpha_list = sorted(set(data))
    if type(data) is str:
        data = data.encode()
    
    alphabeth = {}
    i_char = 0
    for char in alpha_list:
        alphabeth[char.encode()] = i_char
        i_char += 1
    keys: dict = alphabeth.copy()
    n_keys: int = len(alpha_list)
    compressed: list = []
    start: int = 0
    n_data: int = len(data)+1
    while True:
        if n_keys >= len(alpha_list) * 2 + max_dict_size_to_add: # Max dimensione che sono disposto a fornire al dizionario
            keys = alphabeth.copy()
            n_keys = len(alpha_list)
        for i in range(1, n_data-start):
            w: bytes = data[start:start+i]
            #print("alfabeto:", keys)
            #print("---W:", w)
            if w not in keys:
                #print("Da aggiungere:", keys[w[:-1]])
                compressed.append(keys[w[:-1]])
                keys[w] = n_keys
                start += i-1
                n_keys += 1
                break
        else:
            compressed.append(keys[w])
            break
    #print("RISULTATO COMPRESSIONE:", compressed)
    bits = ""
    for i in compressed:
        bits += bin(i)[2:].zfill(max_dim_binary) # Faccio in modo che l'output di bin() abbia sempre lunghezza definita e non contenga 0b iniziale
    compressed_to_bits = int(bits,2).to_bytes(ceil(len(bits)/8), 'big') # Separo i bit in gruppi da 8 per codificare l'output in byte
    #print("Byte:", compressed_to_bits)
    '''bits: str = ''.join([bin(i)[2:].zfill(9) for i in compressed])
    print("BITS:", bits)
    return int(bits, 2).to_bytes(ceil(len(bits) / 8), 'big'), alphabeth'''
    return compressed_to_bits, alphabeth


def decompress(data: str, compression_alphabeth: dict) -> bytes:
    #print("data:", data[:500])
    alpha_list = compression_alphabeth.keys()
    i_key = 0
    alphabeth = {}
    for key in alpha_list:
        alphabeth[i_key] = key
        i_key += 1
    
    if type(data) is str:
        data = data.encode()
    keys: dict = alphabeth.copy()
    bits: str = bin(int.from_bytes(data, 'big'))[2:].zfill(len(data) * 8)
    n_extended_bytes: int = floor(len(bits) / max_dim_binary)
    bits: str = bits[-n_extended_bytes * max_dim_binary:]
    data_list: list = [int(bits[i*max_dim_binary:(i+1)*max_dim_binary], 2)
                       for i in range(n_extended_bytes)]
    #print("KEY:", keys, "\nDATA:", data_list[:500])
    previous: bytes = keys[data_list[0]]
    uncompressed: list = [previous]
    n_keys: int = len(alpha_list)
    for i in data_list[1:]:
        if n_keys >= len(alpha_list) * 2 + max_dict_size_to_add:
            keys = alphabeth.copy()
            n_keys = len(alpha_list)
        try:
            current: bytes = keys[i]
        except KeyError:
            current = previous + previous[:1]
        uncompressed.append(current)
        keys[n_keys] = previous + current[:1]
        previous = current
        n_keys += 1
    return b''.join(uncompressed)

if __name__ == "__main__":
    #inputFile = open("../TestFiles/Input/test2.txt", "r")
    inputFile = open("../TestFiles/Output/outputRLE.txt", "r")
    listInput = inputFile.readlines()
    stringInput = ""
    for val in listInput:
        stringInput += val
    #stringInput = "Ciaonelmao"
    compression, dictionary = compress(stringInput)
    #print("Compressione:", compression)
    fileout = open("out.txt", "wb")
    fileout.write(compression)
    fileoutDict = open("outDict.txt", "wb")
    pickle.dump(dictionary, fileoutDict)

    decompression = decompress(compression, dictionary).decode()
    filein = open("in.txt", "w")
    filein.write(decompression)
    #print("Decompressione:", decompression)
    print("Vero?", decompression == stringInput)

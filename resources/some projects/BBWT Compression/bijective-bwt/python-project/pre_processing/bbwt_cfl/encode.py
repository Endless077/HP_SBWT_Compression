from pre_processing.bbwt_cfl.cfl import cfl
from pre_processing.suffix_array import suffix_array_manber_myers


class Rotation:
    def __init__(self, w: int, r: int):
        # index of factor
        self.w = w
        # index of the first character generating the rotation
        self.r = r

    def __str__(self):
        return f"w: {self.w}\n" \
               f"r: {self.r}"


def less_rotation(factors: [str], i: Rotation, j: Rotation) -> bool:
    # get index of factor i
    i_w: int = i.w
    # get the index of the first character of the rotation
    i_r: int = i.r
    # length of i-th factor
    i_length: int = len(factors[i_w])

    # get index of factor j
    j_w: int = j.w
    # get the index of the first character of the rotation
    j_r: int = j.r
    # length of j-th factor
    j_length: int = len(factors[j_w])

    for _ in range(i_length * j_length):
        # check if the factor to merge is less than factor already merged
        if factors[i_w][i_r] < factors[j_w][j_r]:
            return True
        # if is greater than return false
        elif factors[i_w][i_r] > factors[j_w][j_r]:
            return False

        # else all the factors are equals then this have to increment value
        # if ri or rj are equal to length of one of two factor then will set to 0 the value
        # simply as modular increment
        i_r += 1
        j_r += 1
        if i_r == i_length:
            i_r = 0
        if j_r == j_length:
            j_r = 0
    # if 2 factors are equals, return false
    return False


def merge_rotation(factors: [str], a: [[Rotation]], b: [[Rotation]]) -> [Rotation]:
    # a will be a list of the factor merged since this execution
    # b will be the list of factors of a factor to merge
    a_length: int = len(a)
    b_length: int = len(b)
    length: int = a_length + b_length
    out: [[Rotation]] = [None] * length

    # index for list a
    i: int = 0
    # index for list b
    j: int = 0
    # index for list out
    k: int = 0

    # check if the index is less than length of the two factor
    while i < a_length and j < b_length:
        # less rotation check if rotation b[j] is less than rotation a[i]
        if less_rotation(factors, b[j], a[i]):
            # append at k-th position b[j]
            out[k] = b[j]
            # increment index of list b
            j += 1
        # if rotation a[i] is less or equal than b[j]
        else:
            # append at k-th position a[i]
            out[k] = a[i]
            # increment index of list a
            i += 1
        # increment index of list out
        k += 1
    # this mean that we added to out all the element of list b or of list a
    # then we add to out all the remaining elements
    if i < a_length:
        out[k:] = a[i:]
    elif j < b_length:
        out[k:] = b[j:]
    return out


def merge_rotations(factors: [str], rotations_of_all_factors: [[Rotation]]) -> [Rotation]:
    merged: [[Rotation]] = []
    while len(rotations_of_all_factors) > 0:
        # call merge_rot on every element of rots
        # (Rotation object can contain multiple rotation based on the factor and conjugate numbers)
        merged = merge_rotation(factors, merged, rotations_of_all_factors[0])
        # discard the first element of rotations_of_all_factors because it's already merged
        rotations_of_all_factors = rotations_of_all_factors[1:]
    return merged


def sort_rotations(factors: [str], rotations_of_all_factors: [[Rotation]]) -> [Rotation]:
    # for all rotations of i-th factor
    for i, rotations in enumerate(rotations_of_all_factors):
        # get the suffix array on the factor
        suffix_array = suffix_array_manber_myers(factors[i])
        # use suffix_array for update order of the factor's rotations
        for j, r in enumerate(suffix_array):
            rotations[j].r = r
    # Return merge of all rotations of all factors
    return merge_rotations(factors, rotations_of_all_factors)


def encode(string: str) -> str:
    # get all lyndon factors of string
    factors: [str] = cfl(string)
    out = [None] * len(string)

    rotations_of_factors: [[Rotation]] = []
    # for each i-th factor w
    for i, w in enumerate(factors):
        # declare array which contains all rotation of string w
        rotations_of_w: [Rotation] = [None] * len(w)
        # for each j-th character of w
        for j in range(len(w)):
            # j-th rotation of w is equal to (i, j)
            rotations_of_w[j] = Rotation(i, j)
        # append all rotation of w
        rotations_of_factors.append(rotations_of_w)
    # merge and order by ascending all factors and conjugates
    sorted_rotations_of_factors = sort_rotations(factors, rotations_of_factors)
    # selects the last column of the matrix consisting of all ordered rotations
    for i, rotation in enumerate(sorted_rotations_of_factors):
        i_r: int = rotation.r - 1
        if i_r < 0:
            i_r += len(factors[rotation.w])
        out[i] = factors[rotation.w][i_r]
    return ''.join(out)


if __name__ == "__main__":
    print(encode("banana"))

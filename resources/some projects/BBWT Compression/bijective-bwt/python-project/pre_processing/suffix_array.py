from collections import defaultdict


def sort_bucket(s, bucket, order):
    d = defaultdict(list)
    for i in bucket:
        # in key there is value from (i+order//2) to (i+order)
        # if we have i = 0 and order that is a constant with value 1 we will have
        # i + order // 2 = 0 and i+order = 1 so key will be the value from 0 to 1 ,excluded, of s
        key = s[i + order // 2:i + order]
        # add to dictionary key that will be the letters and i for value, like a hashmap
        d[key].append(i)
    result = []
    # sorted function sorts the elements of a given iterable in ascending order and returns it as a list. 
    # call foreach on sorted dict
    for k, v in sorted(d.items()):
        if len(v) > 1:
            # if v have more than one single element call recusively sort_buckets with s that have the current factor
            # v that have the current element of dict and multiply order number
            result += sort_bucket(s, v, 2 * order)
        else:
            # populate result to return all
            result.append(v[0])
    return result


def suffix_array_manber_myers(s):
    """http://algorithmicalley.com/archive/2013/06/30/suffix-arrays.aspx"""
    return sort_bucket(s, range(len(s)), 1)

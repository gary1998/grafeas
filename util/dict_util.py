import copy


def dict_merge(n, o):
    # merge two lists
    if isinstance(o, list) and isinstance(n, list):
        return [dict_merge(i, j) for i, j in zip(n, o)]

    if not isinstance(o, dict) or not isinstance(n, dict):
        return o

    # get deep copy of n
    result = copy.deepcopy(n)

    # overlay o items over n items
    for k, v in o.items():
        if k in result:
            result[k] = dict_merge(result[k], v)
        else:
            result[k] = copy.deepcopy(v)

    return result

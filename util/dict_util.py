import copy


def override(n, o):
    # merge two lists
    if isinstance(o, list) and isinstance(n, list):
        return [override(i, j) for i, j in zip(n, o)]

    if not isinstance(o, dict) or not isinstance(n, dict):
        return o

    # get deep copy of n
    result = copy.deepcopy(n)

    # overlay o items over n items
    for k, v in o.items():
        if k in result:
            result[k] = override(result[k], v)
        else:
            result[k] = copy.deepcopy(v)

    return result

import copy

def fill_until_length(list_dest, item, length):
    while len(list_dest) < length:
        list_dest.append(copy.deepcopy(item))

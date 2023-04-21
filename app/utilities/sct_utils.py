"""
    sct_utils.py
    -------
    This module consists of utility functions used by other module
"""


def tuple_to_dict(key_list: list, tuple_list: list) -> list:
    """
    Converts a tuple list and a list of dictionary keys returning dictionary

    :param key_list: Dictionary keys
    :param tuple_list: List of tuples
    :return: List of Dictionary
    """
    result_dict = []
    for e in tuple_list:
        se = dict()
        for i, k in enumerate(key_list):
            se[k] = e[i]
        result_dict.append(se)
    return result_dict


def tuple_to_list(tuple_list: list) -> list:
    """
    Converts a list of single item tuple to a simple python list

    :param tuple_list: Single element tuple
    :return: List of elements
    """
    return [t[0] for t in tuple_list]

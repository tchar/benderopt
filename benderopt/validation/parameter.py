import numpy as np


def validate_categorical(search_space):
    # error = "Expected a dict with mandatory key 'values' (list) and optional key 'weights' (list)"
    search_space = search_space.copy()

    if type(search_space) != dict:
        raise ValueError
    elif "values" not in search_space.keys() or type(search_space['values']) != list:
        raise ValueError
    elif "weights" in search_space.keys() and (
        type(search_space['weights']) != list or
        len(search_space['weights']) != len(search_space['values']) or
            sum(search_space['weights']) != 1):
        raise ValueError

    if "weights" not in search_space.keys():
        number_of_values = len(search_space["values"])
        search_space["weights"] = list(np.ones(number_of_values) / number_of_values)

    return search_space


def validate_normal(search_space):
    # error = "Expected a type dict with mandatory keys : [mu, sigma] and optional key log  or step"
    search_space = search_space.copy()

    if type(search_space) != dict:
        raise ValueError

    elif "mu" not in search_space.keys() or type(search_space["mu"]) not in (int, float):
        raise ValueError

    elif "sigma" not in search_space.keys() or type(search_space["sigma"]) not in (int, float):
        raise ValueError

    elif "log" in search_space.keys():
        if type(search_space["log"]) not in (bool,):
            raise ValueError

    elif "step" in search_space.keys():
        if type(search_space["step"]) not in (int, float):
            raise ValueError

    elif "low" in search_space.keys():
        if type(search_space["low"]) not in (int, float):
            raise ValueError

    elif "high" in search_space.keys():
        if type(search_space["high"]) not in (int, float):
            raise ValueError

    elif "high" in search_space.keys() and "low" in search_space.keys():
        if search_space["high"] >= search_space["low"]:
            raise ValueError("low <= high")

    if "high" not in search_space.keys():
        search_space["high"] = np.inf

    if "low" not in search_space.keys():
        search_space["low"] = -np.inf

    return search_space


def validate_uniform(search_space):
    # error = "Expected a type dict with mandatory keys : [low, high] and optional key [log]"
    search_space = search_space.copy()

    if type(search_space) != dict:
        raise ValueError

    elif "low" not in search_space.keys() or type(search_space["low"]) not in (int, float):
        raise ValueError

    elif "high" not in search_space.keys() or type(search_space["high"]) not in (int, float):
        raise ValueError

    elif "log" in search_space.keys():
        if type(search_space["log"]) not in (bool,):
            raise ValueError

    elif "step" in search_space.keys():
        if type(search_space["step"]) not in (int, float):
            raise ValueError

    return search_space


def validate_gaussian_mixture(search_space):
    # error = "Expected a type dict with mandatory keys : [low, high] and optional key [log]"
    search_space = search_space.copy()

    if type(search_space) != dict:
        raise ValueError

    elif "mus" not in search_space.keys() or type(search_space["mus"]) != list:
        raise ValueError

    elif "sigmas" not in search_space.keys() or type(search_space["sigmas"]) != list:
        raise ValueError

    elif "log" in search_space.keys():
        if type(search_space["log"]) not in (bool,):
            raise ValueError

    elif "step" in search_space.keys():
        if type(search_space["step"]) not in (int, float):
            raise ValueError

    elif "low" in search_space.keys():
        if type(search_space["low"]) not in (int, float):
            raise ValueError

    elif "high" in search_space.keys():
        if type(search_space["high"]) not in (int, float):
            raise ValueError

    elif "high" in search_space.keys() and "low" in search_space.keys():
        if search_space["high"] >= search_space["low"]:
            raise ValueError("low >= high")

    if "high" not in search_space.keys():
        search_space["high"] = np.inf

    if "low" not in search_space.keys():
        search_space["low"] = -np.inf

    return search_space


validate_search_space = {
    "categorical": validate_categorical,
    "normal": validate_normal,
    "uniform": validate_uniform,
    "gaussian_mixture": validate_gaussian_mixture,
}
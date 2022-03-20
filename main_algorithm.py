"""
主算法框架类
考虑时空距离和vns
"""

from genetic_algorithm import *
from read_data import *
from time import time


class MainAlgorithm:
    def __init__(self):
        pass

    def run(self):
        d = ReadData()
        data = d.run()
        ga = GeneticAlgorithm(data)
        ga.run()


def Timecounter(func):
    """

    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        print(f'算法总耗时{time() - start}秒', func.__name__)
        return result
    return wrapper

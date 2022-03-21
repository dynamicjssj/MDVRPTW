import pandas as pd

# 用于存储每15分钟的拥堵系数
class Coefficient:
    def __init__(self, coe1, coe2):
        self.quarter_1 = coe1
        self.quarter_2 = (coe2 - coe1) * 0.25 + coe1
        self.quarter_3 = (coe2 - coe1) * 0.5 + coe1
        self.quarter_4 = (coe2 - coe1) * 0.75 + coe1


def get_coefficient_list():
    crowd_list = []  # 存储从excel中获取的拥堵系数
    df = pd.read_excel('时变路网.xlsx')
    for i in range(24):
        crowd_list.append(df['拥堵指数'][i])
    coe_list = []
    for i in range(24):
        if i == 23:
            coe = Coefficient(crowd_list[i], crowd_list[0])
            coe_list.append(coe)
        else:
            coe = Coefficient(crowd_list[i], crowd_list[i + 1])
            coe_list.append(coe)
    return coe_list

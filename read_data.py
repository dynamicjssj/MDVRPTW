"""
读取数据并处理数据类

"""
import numpy.random
import pandas as pd
from collections import defaultdict
from Coefficient import get_coefficient_list


class ReadData:
    def __init__(self):
        self.coe_list = None
        self.m = 36  # 客户数量
        self.n = 3  # 仓库数量
        self.v1 = 32.64  # 车辆k行驶的平均速km/h
        self.v2 = 1500  # 装卸料速度	t/h
        self.p_0 = 0.165  # 车辆k空载时的单位距离油耗	L/km
        self.p_star = 0.377  # 车辆k满载时的单位距离油耗	L/km
        self.alpha_1 = 2  # 制冷设备在运输过程中单位时间的燃料消耗量	L/h
        self.alpha_2 = 2.5  # 制冷设备卸货时单位时间燃料消耗量	L/h
        self.Q = 1100  # 配送车辆ｋ的最大载重量

        self.c1 = 200  # 每辆车的派遣成本	RMB/car
        self.c2 = 5   # 单位距离运输成本	RMB/km
        self.c3 = 16.68  # 单位燃油价格	RMB/L
        self.c4 = 30  # 提前到达的车辆的单位时间等待成本	RMB/h
        self.c5 = 30  # 迟到的车辆每单位时间的惩罚成本	RMB/h
        self.c6 = 0.25  # 碳价	RMB/kg
        self.c7 = 1

        self.T_q = 100  # 碳排放配额	kg
        self.NVC = 43.3  # 燃料的平均低位发热量	GJ/t
        self.CC = 0.0202  # 燃料的单位热值含碳量	tC/GJ
        self.OF = 0.98  # 燃料的碳氧化率	%
        self.M = 1000000  # 任意大的常数

        self.dis_mat = defaultdict(dict)
        self.data = defaultdict(dict)
        # self.cong_mat = defaultdict(dict)
        self.time_space_dis = defaultdict(dict)
        self.warehouse_list = ['A', 'B', 'C']
        self.warehouse_A = (7.1, 25.6)
        self.warehouse_B = (15.12, 9.06)
        self.warehouse_C = (28.28, 30.4)
        self.w_list = [self.warehouse_A, self.warehouse_B, self.warehouse_C]
        self.warehouse_time = (3.5, 20.50)

    def distance_matrix(self):
        df = pd.read_excel('数据.xlsx')
        for i in range(len(df)):
            i_x, i_y = df['横坐标/km'][i], df['纵坐标/km'][i]
            for j in range(len(df)):
                j_x, j_y = df['横坐标/km'][j], df['纵坐标/km'][j]
                dis_i_j = pow(pow(i_x - j_x, 2) + pow(i_y - j_y, 2), 1 / 2)
                self.dis_mat[i][j] = dis_i_j

        for idx, ware in enumerate(self.w_list):
            for i in range(len(df)):
                i_x, i_y = df['横坐标/km'][i], df['纵坐标/km'][i]
                dis_i_ware = pow(pow(i_x - ware[0], 2) + pow(i_y - ware[1], 2), 1 / 2)
                if idx == 0:
                    self.dis_mat[i]['A'] = dis_i_ware
                    self.dis_mat['A'][i] = dis_i_ware
                elif idx == 1:
                    self.dis_mat[i]['B'] = dis_i_ware
                    self.dis_mat['B'][i] = dis_i_ware
                else:
                    self.dis_mat[i]['C'] = dis_i_ware
                    self.dis_mat['C'][i] = dis_i_ware

    #  这里加入随机拥堵 系数矩阵
    # def congestion_matrix(self):
    #     for i in range(self.m):
    #         for j in range(self.m):
    #             if i == j:
    #                 continue
    #             if i < j:
    #                 random_cong = numpy.random.random()
    #                 self.cong_mat[i][j] = random_cong
    #                 self.cong_mat[j][i] = random_cong
    #     for idx, ware in enumerate(self.w_list):
    #         for i in range(self.m):
    #             random_cong = numpy.random.random()
    #             if idx == 0:
    #                 self.cong_mat[i]['A'] = random_cong
    #                 self.cong_mat['A'][i] = random_cong
    #             elif idx == 1:
    #                 self.cong_mat[i]['B'] = random_cong
    #                 self.cong_mat['B'][i] = random_cong
    #             else:
    #                 self.cong_mat[i]['C'] = random_cong
    #                 self.cong_mat['C'][i] = random_cong

    def time_matrix(self):
        time_mat = defaultdict(dict)
        df = pd.read_excel('数据.xlsx')
        for i in range(len(df)):
            i_x, i_y = df['ET浮点数'][i], df['LT浮点数'][i]
            for j in range(len(df)):
                if i == j:
                    continue
                j_x, j_y = df['ET浮点数'][j], df['LT浮点数'][j]
                travel_time = self.dis_mat[i][j] / self.v1
                service_time = (df['交付需求/t'][i] + df['取件需求/t'][i]) / self.v2
                a = i_x + travel_time + service_time
                b = i_y + travel_time + service_time
                dijt = None
                if b < j_x:
                    dijt = self.c4 * (j_x - b)
                elif a > j_y:
                    dijt = self.c5 * (a - j_y)
                elif a < j_x < b or a < j_y < b:
                    dijt = self.c7 * (travel_time + service_time)
                elif j_x < a < b < j_y:
                    dijt = travel_time + service_time
                time_mat[i][j] = dijt

        return time_mat

    def space_time_matrix(self):
        theta1, theta2 = 0.6, 0.4
        self.distance_matrix()
        time_mat = self.time_matrix()
        min_dt, min_ds = float('inf'), float('inf')
        max_dt, max_ds = -float('inf'), -float('inf')
        for key, val in self.dis_mat.items():
            for _, dis in val.items():
                min_ds = min(min_ds, dis)
                max_ds = max(max_ds, dis)
        for _, val in time_mat.items():
            for _, time_dis in val.items():
                min_dt = min(min_dt, time_dis)
                max_dt = max(max_dt, time_dis)

        for i in range(self.m):
            for j in range(self.m):
                if i == j:
                    continue

                self.time_space_dis[i][j] = theta1 * ((self.dis_mat[i][j] - min_ds) / (max_ds - min_ds)) + \
                                            theta2 * ((time_mat[i][j] - min_dt) / (max_dt - min_dt))

    def get_data(self):
        df = pd.read_excel('数据.xlsx')
        for i in range(len(df)):
            self.data['交付需求/t'][i] = df['交付需求/t'][i]
            self.data['取件需求/t'][i] = df['取件需求/t'][i]
            self.data['x'][i] = df['横坐标/km'][i]
            self.data['y'][i] = df['纵坐标/km'][i]
            self.data['ET浮点数'][i] = df['ET浮点数'][i]
            self.data['LT浮点数'][i] = df['LT浮点数'][i]
            self.data['EET浮点数'][i] = df['EET浮点数'][i]
            self.data['LLT浮点数'][i] = df['LLT浮点数'][i]
            self.data['用户等级'][i] = df['用户等级'][i]

        self.data['交付需求/t']['A'] = 0
        self.data['取件需求/t']['A'] = 0
        self.data['x']['A'] = 7.1
        self.data['y']['A'] = 25.6
        self.data['ET浮点数']['A'] = 3.50
        self.data['LT浮点数']['A'] = 20.50
        self.data['EET浮点数']['A'] = 3.5
        self.data['LLT浮点数']['A'] = 20.50

        self.data['交付需求/t']['B'] = 0
        self.data['取件需求/t']['B'] = 0
        self.data['x']['B'] = 15.12
        self.data['y']['B'] = 9.06
        self.data['ET浮点数']['B'] = 3.5
        self.data['LT浮点数']['B'] = 20.50
        self.data['EET浮点数']['B'] = 3.5
        self.data['LLT浮点数']['B'] = 20.50

        self.data['交付需求/t']['C'] = 0
        self.data['取件需求/t']['C'] = 0
        self.data['x']['C'] = 28.28
        self.data['y']['C'] = 30.4
        self.data['ET浮点数']['C'] = 3.5
        self.data['LT浮点数']['C'] = 20.50
        self.data['EET浮点数']['C'] = 3.5
        self.data['LLT浮点数']['C'] = 20.50
        self.coe_list = get_coefficient_list()  # 根据预测的拥堵 系数获得拥堵 系数列表

    def run(self):
        self.space_time_matrix()
        self.get_data()
        # self.congestion_matrix()

        return self

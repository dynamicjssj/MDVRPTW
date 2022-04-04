from genetic_algorithm import *
from read_data import *
from plot_func import *
import numpy as np
from tqdm import tqdm  # 实现进度条
import sys
from prettytable import PrettyTable
from matplotlib.font_manager import FontProperties

plt.rcParams["font.family"] = 'Arial Unicode MS'
plt.rcParams['font.sans-serif'] = ['Arial Black']


def analysisCarbonPrice(data):
    # 碳价对总成本对影响
    carbon_price = np.arange(0, 20.25, 0.25)
    carbon_emission = []
    carbon_cost = []
    total_cost = []
    carbon_percent = []
    table = PrettyTable(['碳价', '碳排放', '碳排放成本', '总成本'])
    with tqdm(total=len(carbon_price)) as pbar:
        pbar.set_description('Processing:')
        for i in carbon_price:
            data.c6 = i
            ga = GeneticAlgorithm(data)
            grouped_chromosome, in_1, y, y_best, y1, y_best1 = ga.run(False)
            f1, f2, f3, f4, f5, m, ce = ga.cal_fitness(grouped_chromosome, True)  # f4是碳价
            total_price = f1 + f2 + f3 + f4 + f5  # 总共花费的价格
            fc1, fc2 = 0, f3 / data.c3
            for route in grouped_chromosome:
                cur_weight = 0
                for k in range(1, len(route)):
                    cur_weight += data.data['交付需求/t'][route[k]]  # 路上总需求
                for k in range(1, len(route)):
                    dij = data.dis_mat[route[k]][route[k - 1]]
                    qij = cur_weight - data.data['交付需求/t'][route[k - 1]] + data.data['取件需求/t'][
                        route[k - 1]]
                    fc1 += dij * (
                            data.p_0 + qij * (data.p_star - data.p_0) / data.Q)
            carbon_no = data.NVC * data.CC * data.OF * 44 / 12 * (fc1 + fc2)
            carbon_emission.append(carbon_no)
            carbon_cost.append(f4)
            total_cost.append(total_price)
            carbon_percent.append(f4 / total_price)
            table.add_row([i, carbon_no, f4, total_price])
            pbar.update(1)
    print(table)
    plt.plot(carbon_price, carbon_cost, marker='o', label=u'碳排放成本')
    plt.plot(carbon_price, total_cost, marker='*', label=u'总成本')
    plt.xlabel(u"碳价(RMB/kg)")  # X轴标签
    plt.ylabel(u"总成本(RMB)")  # Y轴标签
    plt.legend()
    plt.show()
    return carbon_price,carbon_cost,total_cost

def analysisQuotas(data):
    # 碳价对总成本对影响
    carbon_quotas = np.arange(50, 325, 25)
    carbon_emission = []
    carbon_cost = []
    total_cost = []
    carbon_percent = []
    table = PrettyTable(['碳配额', '碳排放', '碳排放成本', '总成本'])
    with tqdm(total=len(carbon_quotas) * 10) as pbar:
        pbar.set_description('Processing:')
        for i in carbon_quotas:
            total_price = 0
            carbon_no = 0
            car_cost = 0
            for j in range(10):
                data.c6 = 0.25
                data.T_q = i
                ga = GeneticAlgorithm(data)
                grouped_chromosome, in_1, y, y_best, y1, y_best1 = ga.run(False)
                f1, f2, f3, f4, f5, m, ce = ga.cal_fitness(grouped_chromosome, True)  # f4是碳价
                total_price += (f1 + f2 + f3 + f4 + f5)  # 总共花费的价格
                fc1, fc2 = 0, f3 / data.c3
                for route in grouped_chromosome:
                    cur_weight = 0
                    for k in range(1, len(route)):
                        cur_weight += data.data['交付需求/t'][route[k]]  # 路上总需求
                    for k in range(1, len(route)):
                        dij = data.dis_mat[route[k]][route[k - 1]]
                        qij = cur_weight - data.data['交付需求/t'][route[k - 1]] + data.data['取件需求/t'][
                            route[k - 1]]
                        fc1 += dij * (
                                data.p_0 + qij * (data.p_star - data.p_0) / data.Q)
                pbar.update(1)
                carbon_no += (data.NVC * data.CC * data.OF * 44 / 12 * (fc1 + fc2))
                car_cost += f4
            car_cost /= 10
            carbon_no /= 10
            total_price /= 10
            carbon_emission.append(carbon_no)
            carbon_cost.append(car_cost)
            total_cost.append(total_price)
            carbon_percent.append(car_cost / total_price)
            table.add_row([i, carbon_no, car_cost, total_price])

    print(table)
    plt.plot(carbon_quotas, carbon_cost, marker='o', label=u'碳排放成本')
    plt.xlabel(u"碳配额(RMB/kg)")  # X轴标签
    plt.ylabel(u"碳排放成本(RMB)")  # Y轴标签
    plt.legend(loc="right")
    plt.show()
    plt.figure()
    plt.plot(carbon_quotas, carbon_emission, marker='*', label=u'碳排放量')
    plt.xlabel(u"碳配额(RMB/kg)")  # X轴标签
    plt.ylabel(u"碳排放量(kg)")  # Y轴标签
    plt.legend(loc="right")
    plt.show()
    return carbon_quotas,car_cost,carbon_emission


def analysisAll(data):
    # 绘制3D柱状图
    # 生成图表对象。
    fig = plt.figure()
    # 生成子图对象，类型为3d
    ax = fig.gca(projection='3d')
    car_price = [0.5,0.75,1]
    car_quotas = [0, 100, 200,300,400,500,600]
    color_ = ['r', 'g', 'b']
    table = PrettyTable(['碳价','碳配额', '碳排放', '碳排放成本', '总成本'])
    with tqdm(total=len(car_price) * len(car_quotas)*5 ) as pbar:
        pbar.set_description('Processing:')
        for i in car_price:

            for j in car_quotas:
                car_cost = 0
                total_price = 0
                car_emission =0
                for k in range(5):
                    data.c6 = i
                    data.T_q = j
                    ga = GeneticAlgorithm(data)
                    grouped_chromosome, in_1, y, y_best, y1, y_best1 = ga.run(False)
                    f1, f2, f3, f4, f5, m, ce = ga.cal_fitness(grouped_chromosome, True)  # f4是碳价
                    total_price += (f1 + f2 + f3 + f4 + f5)  # 总共花费的价格
                    car_emission += ce # 碳排放量
                    car_cost += f4
                    pbar.update(1)
                car_cost/=5
                car_emission/=5
                total_price/=5
                table.add_row([i, j, car_emission, car_cost,total_price])

                # 设置坐标轴标签
            print(table)

    plt.show()

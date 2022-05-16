from prettytable import PrettyTable
import numpy as np

from tools import cal_duration, cal_varying_time

f1_list = []
f2_list = []
f3_list = []
f4_list = []
f5_list = []
carbon_emission_list = []
total_cost_list = []


# 上面这些list用来存储每辆车产出的数据
def get_ship_order(route):
    ship_order = ''
    for index in route:
        ship_order += str(index)
        ship_order += '-'
    return ship_order[:-1]


def get_time(route, time_variable, ga):  # 时间需要分情况讨论，时变速度和恒定速度
    # 三个返回值 start_time ，time_route, end_time
    start_time = ga.data_bag.data['ET浮点数'][route[1]]  # 不管是时变速度还是恒定速度，到达第一个客户的时间是固定的
    time_route = ''
    end_time = 0
    if time_variable:
        duration, _ = cal_duration(start_time, ga.data_bag.dis_mat[route[1]][
            route[0]], ga.data_bag.coe_list)
        start_time -= duration  # 减去从仓库到达第一个节点的时间
        current_time = start_time
        for i in range(1, len(route)-1):
            current_time, fuel_cost = cal_varying_time(current_time,
                                                       ga.data_bag.dis_mat[route[i]][route[i - 1]],
                                                       ga.data_bag.coe_list)
            # 这里加入服务时间
            sij = (ga.data_bag.data['交付需求/t'][route[i]] + ga.data_bag.data['取件需求/t'][
                route[i]]) / ga.data_bag.v2
            current_time += sij
            time_route += transform_time(current_time)
            time_route += '-'

        end_time,_ = cal_varying_time(current_time,
                                                       ga.data_bag.dis_mat[route[len(route)-2]][route[len(route)-1]],
                                                       ga.data_bag.coe_list)
    else:
        start_time -= (ga.data_bag.dis_mat[route[1]][
                           route[0]] / ga.data_bag.v1)
        current_time = start_time
        for i in range(1, len(route)-1):  # 从第一个客户点开始计时
            current_time += (ga.data_bag.dis_mat[route[i]][
                                 route[i - 1]] / ga.data_bag.v1)
            # 这里加入服务时间
            sij = (ga.data_bag.data['交付需求/t'][route[i - 1]] + ga.data_bag.data['取件需求/t'][
                route[i - 1]]) / ga.data_bag.v2
            current_time += sij
            temp = transform_time(current_time)
            time_route += temp
            time_route += '-'
        end_time = current_time + (ga.data_bag.dis_mat[route[len(route)-2]][
                                 route[len(route)-1]] / ga.data_bag.v1)

    start_time = transform_time(start_time)
    end_time = transform_time(end_time)
    return start_time, time_route[:-1],end_time


def transform_time(t):  # 将小数时间转化为现实生活中的时间
    hour = int(t)  # 获取小时
    minute = int((t - hour) * 60)  # 获取分钟
    time = ''
    time += str(hour)
    time += ':'
    if minute < 10:
        time += '0'
    time += str(minute)
    return time


def get_loaded(route, ga):  # 获取载重量
    loaded = ''
    weight = 0
    for index in route:
        weight += ga.data_bag.data['交付需求/t'][index]
    loaded += str(weight)
    loaded += '-'
    for index in route[1:-1]:  # 从第一个客户点
        weight += ga.data_bag.data['取件需求/t'][index]
        weight -= ga.data_bag.data['交付需求/t'][index]
        loaded += str(weight)
        loaded += '-'
    return loaded[:-1]


def print_message(individual, label, time_variable, ga):  # label是打印的标号，比如考虑时空聚类
    print('=' * 50)
    print("=" * 20 + f'{label}:' + "=" * 20)
    print('共需要{}辆车'.format(len(individual)))
    f1_list.clear()
    f2_list.clear()
    f3_list.clear()
    f4_list.clear()
    f5_list.clear()
    carbon_emission_list.clear()
    total_cost_list.clear()
    # 因为上面的list为全局变量，在打印新的内容时需要清空
    table = PrettyTable(
        ['车辆编号', '配送顺序', '派遣成本', '运输成本', '制冷成本', '时间窗惩罚成本', '总成本(不包括碳排放成本)', '碳排放量', '路程', '载重量', '到达各个配送点时间',
         '从配送中心出发时间', '回到配送中心时间'])
    for i in range(len(individual)):
        ship_order = get_ship_order(individual[i])
        temp = []
        temp.append(individual[i])
        loaded = get_loaded(individual[i], ga)
        f1, f2, f3, f4, f5, _, carbon_emission = ga.cal_fitness(temp, time_variable)
        deal_list(f1, f2, f3, f5, carbon_emission)
        distance = f2 / ga.data_bag.c2;
        start_time, time_route,end_time = get_time(individual[i], time_variable, ga)
        table.add_row(
            [i + 1, ship_order, f1, f2, f3, f5, (f1 + f2 + f3 + f5), carbon_emission, distance, loaded, time_route,
             start_time,end_time])
    print(table)

    print(individual)
    print('总成本为:', np.sum(total_cost_list)+(np.sum(carbon_emission_list) - ga.data_bag.T_q)*ga.data_bag.c6)
    print('车辆派遣成本为:', np.sum(f1_list))
    print('车辆运输成本为:', np.sum(f2_list))
    print('制冷成本为:', np.sum(f3_list))
    print('碳排放量为:', np.sum(carbon_emission_list))
    print('碳排放成本:', (np.sum(carbon_emission_list) - ga.data_bag.T_q)*ga.data_bag.c6)
    print('时间窗惩罚成本为:', np.sum(f5_list))
    print('总运输距离为:', np.sum(f2_list) / ga.data_bag.c2)


def deal_list(f1, f2, f3, f5, carbon_emission):
    f1_list.append(f1)
    f2_list.append(f2)
    f3_list.append(f3)
    f5_list.append(f5)
    carbon_emission_list.append(carbon_emission)
    total_cost_list.append((f1 + f2 + f3 + f5))

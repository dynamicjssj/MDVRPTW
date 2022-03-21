max_v = 50  # 拥堵时的最大速度
min_v = 20  # 拥堵时的最小速度
from Coefficient import get_coefficient_list


# 基于分段函数
def get_speed(t):  # 根据传入的时间获取速度
    # 最早出发时间为7点，所以第一个点速度按7点时取值
    if 7 <= t < 8 or 9 <= t < 10 or 17 <= t < 18:
        return 40
    elif 8 <= t < 9:
        return 20
    else:
        return 50  # 单位km/h


# 基于随机拥堵 系数获得速度
def get_random_speed(coefficient):
    return min_v + (max_v - min_v) * coefficient  # 当最大最小速度改变时，需要改这里


# 获取时变速度、基于拥堵 系数,相比于上面的分段函数，这部分的取值更小（间隔为15分钟）
def get_time_varying_speed(t, coe_list):
    quarter_1, quarter_2, quarter_3, quarter_4 = divide_time(t)
    coefficient = coe_list[quarter_1]  # 获取Coefficient对象
    if quarter_1 <= t < quarter_2:  # 这里左闭右开
        return max_v / coefficient.quarter_1
    elif quarter_2 <= t < quarter_3:
        return max_v / coefficient.quarter_2
    elif quarter_3 <= t < quarter_4:
        return max_v / coefficient.quarter_3
    else:
        return max_v / coefficient.quarter_4


# 划分时间 将时间按0.25 划分成四部分 8.3 划分成 8 8.25 8.5 8.75
def divide_time(t):
    quarter_1 = int(t)  # 前15分钟的时间
    quarter_2 = quarter_1 + 0.25  # 15 ~ 30 分钟
    quarter_3 = quarter_2 + 0.25  # 30 ~ 45 分钟
    quarter_4 = quarter_3 + 0.25  # 45 ~ 60 分钟
    return quarter_1, quarter_2, quarter_3, quarter_4


# 自己实现的取整 方法 每间隔0.25取整 例如 8.3  取整 是 8.5 这个时间段的剩余时间是 0.2
def my_round(t):
    quarter_1, quarter_2, quarter_3, quarter_4 = divide_time(t)
    if quarter_1 <= t < quarter_2:  # 这里左闭右开
        return quarter_2
    elif quarter_2 <= t < quarter_3:
        return quarter_3
    elif quarter_3 <= t < quarter_4:
        return quarter_4
    else:
        return int(t + 1)


# 自己实现的向下取整 方法 每间隔0.25取整 例如 10.1 取整 是 10 10取整 是 9.75
def down_round(t):
    quarter_1, quarter_2, quarter_3, quarter_4 = divide_time(t)
    if quarter_1 == t:
        return t - 0.25
    elif quarter_1 < t <= quarter_2:  # 这里左闭右开
        return quarter_1
    elif quarter_2 < t <= quarter_3:
        return quarter_2
    elif quarter_3 < t <= quarter_4:
        return quarter_3
    else:
        return quarter_4


# 获取时变速度下需要的时间
def cal_varying_time(t, dis, coe_list):
    driving_distance = 0
    left_dis = dis  # 标注剩余的距离
    while driving_distance < dis:
        left_time = my_round(t) - t  # 获取该时段的剩余时间
        speed = get_time_varying_speed(t, coe_list)  # 获取速度
        driving_distance += left_time * speed  # 已经行驶的距离
        if driving_distance >= dis:
            t += left_dis / speed
        else:
            t = my_round(t)  # 时间到达下一个时间段
            left_dis -= speed * left_time
    return t


def cal_time(t, dis):  # t表示开始的时间,dis表示两个点之间点距离 返回值是到达的时间
    left_time = None
    speed = None
    driving_distance = 0
    left_dis = dis  # 标注剩余的距离
    while driving_distance < dis:
        left_time = int(t + 1) - t  # 获取该时段的剩余时间
        speed = get_speed(t)  # 获取速度
        driving_distance += left_time * speed  # 已经行驶的距离
        if driving_distance >= dis:
            t += left_dis / speed
        else:
            t = int(t + 1)  # 时间到达下一个时间段
            left_dis -= speed * left_time
    return t


# 获取仓库到第一个节点需要到时间 ,（已知结束时间和距离算从仓库到第一个节点到时间）
def cal_duration(end_time, dis, coe_list):
    left_time = None
    speed = None
    driving_distance = 0
    left_dis = dis  # 标注剩余的距离
    start_time = end_time
    while driving_distance < dis:
        left_time = start_time - down_round(start_time)  # 获取该时段的剩余时间
        speed = get_time_varying_speed(down_round(start_time), coe_list)  # 获取速度
        driving_distance += left_time * speed  # 已经行驶的距离
        if driving_distance >= dis:
            start_time -= left_dis / speed
        else:
            start_time = down_round(start_time)  # 时间到达下一个时间段
            left_dis -= speed * left_time
    return end_time - start_time


# 根据用户等级获取惩罚系数
def get_punish_coefficient(level):
    c4 = 0  # 提前到的惩罚成本
    c5 = 0  # 迟到的惩罚成本
    if level == 'A':
        c4 = 30
        c5 = 40
    elif level == 'B':
        c4 = 20
        c5 = 30
    else:
        c4 = 10
        c5 = 20
    return c4, c5


# if __name__ == '__main__':
#     coe_list = get_coefficient_list()
#     t = cal_duration(10,20,coe_list)
#     print(t)


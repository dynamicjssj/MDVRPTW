def get_speed(t):  # 根据传入的时间获取速度
    # 最早出发时间为7点，所以第一个点速度按7点时取值
    if 7 <= t < 8 or 9 <= t < 10 or 17 <= t < 18:
        return 40
    elif 8 <= t < 9:
        return 20
    else:
        return 50  # 单位km/h


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


# 获取用户的等级、暂时先通过index来查看
def get_user_level(index):
    if index <= 11:  # 1~12为A,计算机中计数从0开始，所以是0-11
        return 'A'
    elif 12 <= index <= 23:  # 13 ~ 24
        return 'B'
    else:
        return 'C'


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

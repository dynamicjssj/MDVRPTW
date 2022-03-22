"""

VNS邻域搜索类

"""
from copy import deepcopy
from random import sample

from CEME import CEME
from tools import cal_time, get_punish_coefficient, cal_varying_time, cal_duration


class VariableNeighborSearch:

    def __init__(self, grouped_chromosome, data):
        self.chromosome = grouped_chromosome
        # for route in grouped_chromosome:
        #     start = route[0]
        #     end = route[-1]
        #     route = route[1:-1]
        #     route.sort(key=lambda x: data.data['EET浮点数'][x])
        #     route = [start] + route + [end]
        #     self.chromosome.append(route)
        self.data_bag = data
        self.remove_number = data.m // 6
        self.MAX_ = 1000
        self.y = []
        self.y_best = []

    def cal_fitness_all(self, grouped_chromosome, time_variable):

        """

        :param grouped_chromosome:
        :return:
        """

        f1, f2, f3, f4, f5 = 0, 0, 0, 0, 0
        # 1 车辆派遣成本
        f1 += len(grouped_chromosome) * self.data_bag.c1
        # 2 运输成本
        for route in grouped_chromosome:
            for i in range(1, len(route)):
                f2 += self.data_bag.dis_mat[route[i]][route[i - 1]] * self.data_bag.c2
        # 3 制冷成本
        for route in grouped_chromosome:
            # self.data_bag.v1 需要替换。需要先获取第一个点的时间
            current_time = self.data_bag.data['ET浮点数'][route[1]]
            f3 += self.data_bag.dis_mat[route[1]][
                      route[0]] / self.data_bag.v1 * self.data_bag.alpha_1 * self.data_bag.c3
            # 上面的公式用于计算仓库到第一个客户，这个时间速度是恒定的50
            for i in range(2, len(route)):
                dynamic_time = cal_time(current_time, self.data_bag.dis_mat[route[i]][route[i - 1]])
                f3 += (dynamic_time - current_time) * self.data_bag.alpha_1 * self.data_bag.c3
                current_time = dynamic_time
                f3 += self.data_bag.alpha_2 * self.data_bag.c3 * (
                        self.data_bag.data['交付需求/t'][route[i]] + self.data_bag.data['取件需求/t'][
                    route[i]]) / self.data_bag.v2
        # 4 碳排放成本
        fc1, fc2 = 0, f3 / self.data_bag.c3
        for route in grouped_chromosome:
            cur_weight = 0
            for i in range(1, len(route)):
                cur_weight += self.data_bag.data['交付需求/t'][route[i]]  # 路上总需求
            for i in range(1, len(route)):
                dij = self.data_bag.dis_mat[route[i]][route[i - 1]]
                qij = cur_weight - self.data_bag.data['交付需求/t'][route[i - 1]] + self.data_bag.data['取件需求/t'][
                    route[i - 1]]
                fc1 += dij * (self.data_bag.p_0 + qij * (self.data_bag.p_star - self.data_bag.p_0) / self.data_bag.Q)

        f4 += self.data_bag.c6 * (
                self.data_bag.NVC * self.data_bag.CC * self.data_bag.OF * 44 / 12 * (fc1 + fc2) - self.data_bag.T_q)

        # 5 时间窗惩罚成本
        for route in grouped_chromosome:
            # 出发时间
            to_time = None
            for i in range(1, len(route)):
                if i == 1:  # 第一个客户到达时间
                    to_time = self.data_bag.data['ET浮点数'][route[1]]
                else:
                    # tij = self.data_bag.dis_mat[route[i]][route[i - 1]] / self.data_bag.v1   # 行驶时间
                    # to_time = cal_time(to_time, self.data_bag.dis_mat[route[i]][route[i - 1]])
                    if time_variable:
                        to_time,_ = cal_varying_time(to_time, self.data_bag.dis_mat[route[i]][route[i - 1]],
                                                   self.data_bag.coe_list)
                    else:
                        tij = self.data_bag.dis_mat[route[i]][route[i - 1]] / self.data_bag.v1  # 行驶时间
                        to_time += tij

                if to_time > self.data_bag.data['LLT浮点数'][route[i]]:
                    f5 += self.data_bag.M
                else:
                    self.data_bag.c4, self.data_bag.c5 = get_punish_coefficient(self.data_bag.data["用户等级"][i])
                    f5 += self.data_bag.c4 * max(self.data_bag.data['ET浮点数'][route[i]] - to_time,
                                                 0) + self.data_bag.c5 * max(
                        to_time - self.data_bag.data['LT浮点数'][route[i]], 0)
                sij = (self.data_bag.data['交付需求/t'][route[i - 1]] + self.data_bag.data['取件需求/t'][
                    route[i - 1]]) / self.data_bag.v2
                to_time += sij  # 出发时间更新为到达时间+服务时间

        return f1, f2, f3, f4, f5, self.data_bag.M / (f1 + f2 + f3 + f4 + f5)

    def cal_fitness_single(self, route, time_variable):

        """

        :param route:
        :return:
        """

        f1, f2, f3, f4, f5 = 0, 0, 0, 0, 0
        # 1 车辆派遣成本
        f1 += 1 * self.data_bag.c1
        # 2 运输成本
        for i in range(1, len(route)):
            f2 += self.data_bag.dis_mat[route[i]][route[i - 1]] * self.data_bag.c2

        # 3 制冷成本
        current_time = self.data_bag.data['ET浮点数'][route[1]]
        ceme = CEME()
        if time_variable:
            duration, fuel_cost = cal_duration(current_time, self.data_bag.dis_mat[route[1]][
                route[0]], self.data_bag.coe_list)
            f3 += fuel_cost
        else:
            # f3 += self.data_bag.dis_mat[route[1]][
            #           route[0]] / self.data_bag.v1 * self.data_bag.alpha_1 * self.data_bag.c3
            f3 += ceme.get_fuel_cost(self.data_bag.v1, self.data_bag.dis_mat[route[1]][
                route[0]])
        # 上面的公式用于计算仓库到第一个客户，这个时间速度是恒定的50
        for i in range(2, len(route)):
            if time_variable:
                dynamic_time, fuel_cost = cal_varying_time(current_time,
                                                           self.data_bag.dis_mat[route[i]][route[i - 1]],
                                                           self.data_bag.coe_list)
                f3 += fuel_cost
                current_time = dynamic_time
            else:
                f3 += ceme.get_fuel_cost(self.data_bag.v1, self.data_bag.dis_mat[route[i]][
                    route[i - 1]])
                current_time += self.data_bag.dis_mat[route[i]][route[i - 1]] / self.data_bag.v1

            f3 += self.data_bag.alpha_2 * self.data_bag.c3 * (
                    self.data_bag.data['交付需求/t'][route[i]] + self.data_bag.data['取件需求/t'][
                route[i]]) / self.data_bag.v2

        # 4 碳排放成本
        fc1, fc2 = 0, f3 / self.data_bag.c3
        cur_weight = 0
        for i in range(1, len(route)):
            cur_weight += self.data_bag.data['交付需求/t'][route[i]]  # 路上总需求
        for i in range(1, len(route)):
            dij = self.data_bag.dis_mat[route[i]][route[i - 1]]
            qij = cur_weight - self.data_bag.data['交付需求/t'][route[i - 1]] + self.data_bag.data['取件需求/t'][
                route[i - 1]]
            fc1 += dij * (self.data_bag.p_0 + qij * (self.data_bag.p_star - self.data_bag.p_0) / self.data_bag.Q)

        f4 += self.data_bag.c6 * (
                    self.data_bag.NVC * self.data_bag.CC * self.data_bag.OF * 44 / 12 * (fc1 + fc2) - self.data_bag.T_q)

        # 5 时间窗惩罚成本
        # 出发时间
        to_time = None
        for i in range(1, len(route)):
            if i == 1:  # 第一个客户到达时间
                to_time = self.data_bag.data['ET浮点数'][route[1]]
            else:
                # tij = self.data_bag.dis_mat[route[i]][route[i - 1]] / self.data_bag.v1   # 行驶时间
                # to_time = cal_time(to_time, self.data_bag.dis_mat[route[i]][route[i - 1]])
                if time_variable:
                    to_time,_ = cal_varying_time(to_time, self.data_bag.dis_mat[route[i]][route[i - 1]],
                                               self.data_bag.coe_list)
                else:
                    tij = self.data_bag.dis_mat[route[i]][route[i - 1]] / self.data_bag.v1  # 行驶时间
                    to_time += tij

            if to_time > self.data_bag.data['LLT浮点数'][route[i]]:
                f5 += self.data_bag.M
            else:
                self.data_bag.c4, self.data_bag.c5 = get_punish_coefficient(self.data_bag.data["用户等级"][i])
                f5 += self.data_bag.c4 * max(self.data_bag.data['ET浮点数'][route[i]] - to_time,
                                             0) + self.data_bag.c5 * max(
                    to_time - self.data_bag.data['LT浮点数'][route[i]], 0)
            sij = (self.data_bag.data['交付需求/t'][route[i - 1]] + self.data_bag.data['取件需求/t'][
                route[i - 1]]) / self.data_bag.v2
            to_time += sij  # 出发时间更新为到达时间+服务时间

        total_cost = f1 + f2 + f3 + f4 + f5

        return total_cost

    def insert_operator(self, r_c, g_c, time_variable):
        """

        :param r_c:
        :param g_c:
        :return:
        """
        for c in r_c:
            g_c = self.swap_operator(c, g_c, time_variable)

        return g_c

    def swap_operator(self, c, g_c, time_variable):
        """

        :param c:
        :param g_c:
        :return:
        """
        res = []  # (i, route, delta)
        for route in g_c:
            before_fit = self.cal_fitness_single(route, time_variable)
            for i in range(1, len(route)):
                route.insert(i, c)
                load_flag, time_flag = self.check_load_and_time(route, time_variable)
                if load_flag and time_flag:
                    after_fit = self.cal_fitness_single(route, time_variable)
                    route.remove(c)
                    res.append((i, route, after_fit - before_fit))
                else:
                    route.remove(c)

        if not res:  # 未insert
            g_c.append(self.add_ware([c]))
            return g_c

        res.sort(key=lambda x: x[2])
        i, route, delta = res[0]
        g_c.remove(route)
        route.insert(i, c)
        g_c.append(route)
        g_c_new = []
        for route in g_c:
            g_c_new.append(self.add_ware(route[1:-1]))

        return g_c_new

    def two_opt_operator(self, grouped_chromosome):
        """

        :return:
        """
        g_c = deepcopy(grouped_chromosome)
        r_c = sample(list(range(self.data_bag.m)), self.remove_number)

        for c in r_c:
            for route in g_c:
                if c in route:
                    route.remove(c)
                    break

        g_c = [route for route in g_c if len(route) > 2]  # 去掉只有ware的

        return r_c, g_c

    def add_ware(self, route):
        """

        :param route:
        :return:

        """
        first_node = route[0]
        f_v, f_w = float('inf'), None
        last_node = route[-1]
        l_v, l_w = float('inf'), None
        for w in self.data_bag.warehouse_list:
            if self.data_bag.dis_mat[first_node][w] < f_v:
                f_v = self.data_bag.dis_mat[first_node][w]
                f_w = w

            if self.data_bag.dis_mat[last_node][w] < l_v:
                l_v = self.data_bag.dis_mat[last_node][w]
                l_w = w

        route = [f_w] + route + [l_w]
        return route

    def check_load_and_time(self, route, time_variable):
        """

        :param route:
        :return:
        """
        send = 0
        put = []
        left = []
        receive = 0
        to_time = 0
        flag1, flag2 = True, True
        for i in range(1, len(route)):
            send += self.data_bag.data['交付需求/t'][route[i]]
            put.append(self.data_bag.data['交付需求/t'][route[i]])
            left.append(0)
            receive += self.data_bag.data['取件需求/t'][route[i]]

            tmp = 0
            for j in range(len(put)):
                tmp += put[j]
                left[j] = send - tmp

            check = [True for i in left if i + receive <= self.data_bag.Q]
            if send > self.data_bag.Q or len(check) != len(left):
                flag1 = False
                return flag1, flag2

            sij = (self.data_bag.data['交付需求/t'][route[i - 1]] + self.data_bag.data['取件需求/t'][
                route[i - 1]]) / self.data_bag.v2
            # tij = self.data_bag.dis_mat[route[i - 1]][route[i]] / self.data_bag.v1
            if i == 1:
                to_time = (self.data_bag.data['EET浮点数'][route[i]])
            else:
                # to_time = cal_time(to_time, self.data_bag.dis_mat[route[i]][route[i - 1]])
                if time_variable:
                    to_time,_ = cal_varying_time(to_time, self.data_bag.dis_mat[route[i]][route[i - 1]],
                                               self.data_bag.coe_list)
                else:
                    tij = self.data_bag.dis_mat[route[i]][route[i - 1]] / self.data_bag.v1  # 行驶时间
                    to_time += tij
                to_time += sij

            # to_time < self.data_bag.data['EET浮点数'][route[i]] or
            if to_time > self.data_bag.data['LLT浮点数'][route[i]]:
                flag2 = False
                return flag1, flag2

        return flag1, flag2

    def run_vns(self, time_variable):

        """

        :return:
        """
        fit_cur = float('inf')
        g_c_cur = self.chromosome

        fit_best = float('inf')
        g_c_best = None

        for it in range(self.MAX_):
            r_c, g_c = self.two_opt_operator(g_c_cur)
            g_c_new = self.insert_operator(r_c, g_c, time_variable)
            fit_new = 0
            for route in g_c_new:
                fit_new += self.cal_fitness_single(route, time_variable)
            self.y.append(fit_new)
            if fit_new < fit_cur:
                fit_cur = fit_new
                self.y_best.append(fit_new)
                # print(fit_new)
                g_c_cur = g_c_new

                if fit_new < fit_best:
                    fit_best = fit_new
                    g_c_best = g_c_new

        return g_c_best, self.y, self.y_best

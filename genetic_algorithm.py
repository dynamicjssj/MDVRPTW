"""

遗传类

"""
import heapq

from CEME import CEME
from main_algorithm import *
from copy import deepcopy
from random import randint, random, shuffle, sample
from collections import deque
from variable_neighbor_search import *
from tools import get_punish_coefficient, cal_varying_time, cal_duration
import numpy as np
from print_func import print_message


class GeneticAlgorithm:
    def __init__(self, data):
        self.data_bag = data  # 数据
        self.mutation_pro = 0.1
        self.cross_pro = 0.8
        self.popsize = 100
        self.max_iterations = 100
        self.pop = []  # 种群
        self.n = data.m  # 染色体长度
        self.fit_max = 1  # 全局最优值
        self.individual = None
        self.individual1 = None
        self.y = []
        self.y_best = []
        self.reasonable_sol = []
        self.reasonable_fit = []
        self.in_no_st = None
        self.in_st = None
        self.PC1 = 0.9
        self.PC2 = 0.6
        self.PM1 = 0.1
        self.PM2 = 0.001

    def init_chrom_by_time_and_space(self):
        customers = list(range(self.data_bag.m))
        theta1, theta2 = 0.6, 0.4
        self.data_bag.distance_matrix()
        time_mat = self.data_bag.time_matrix()
        min_dt, min_ds = float('inf'), float('inf')
        max_dt, max_ds = -float('inf'), -float('inf')
        for key, val in self.data_bag.dis_mat.items():
            for _, dis in val.items():
                min_ds = min(min_ds, dis)
                max_ds = max(max_ds, dis)
        for _, val in time_mat.items():
            for _, time_dis in val.items():
                min_dt = min(min_dt, time_dis)
                max_dt = max(max_dt, time_dis)

        for i in range(self.n):
            for j in range(self.n):
                if i == j:
                    continue

                self.data_bag.time_space_dis[i][j] = theta1 * (
                        (self.data_bag.dis_mat[i][j] - min_ds) / (max_ds - min_ds)) + \
                                                     theta2 * ((time_mat[i][j] - min_dt) / (max_dt - min_dt))

    def init_chrom_by_random(self, time_variable):
        customers = list(range(self.data_bag.m))
        pop = []
        for i in range(self.popsize):
            pop.append(sample(customers, self.data_bag.m))
        self.in_no_st = self.divide_into_group(pop[0], time_variable)
        return pop

    def cal_fitness(self, grouped_chromosome, time_variable):
        """
        grouped_chromosome: 集群染色体

        目标函数为：

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
            ceme = CEME()
            if time_variable:
                duration, fuel_cost = cal_duration(current_time, self.data_bag.dis_mat[route[1]][
                    route[0]], self.data_bag.coe_list)
                f3 += fuel_cost
            else:
                # f3 += self.data_bag.dis_mat[route[1]][
                #       route[0]] / self.data_bag.v1 * self.data_bag.alpha_1 * self.data_bag.c3
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
        carbon_emission = self.data_bag.NVC * self.data_bag.CC * self.data_bag.OF * 44 / 12 * (fc1 + fc2)
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
                        to_time, _ = cal_varying_time(to_time, self.data_bag.dis_mat[route[i]][route[i - 1]],
                                                      self.data_bag.coe_list)
                    else:
                        tij = self.data_bag.dis_mat[route[i]][route[i - 1]] / self.data_bag.v1  # 行驶时间
                        to_time += tij
                if to_time > self.data_bag.data['LLT浮点数'][route[i]]:
                    f5 += self.data_bag.M
                else:
                    self.data_bag.c4, self.data_bag.c5 = get_punish_coefficient(self.data_bag.data["用户等级"][i-1])
                    f5 += self.data_bag.c4 * max(self.data_bag.data['ET浮点数'][route[i]] - to_time,
                                                 0) + self.data_bag.c5 * max(
                        to_time - self.data_bag.data['LT浮点数'][route[i]], 0)
                sij = (self.data_bag.data['交付需求/t'][route[i]] + self.data_bag.data['取件需求/t'][
                    route[i]]) / self.data_bag.v2
                to_time += sij  # 出发时间更新为到达时间+服务时间

        e1 = 1
        e2 = 1
        e3 = 1

        return f1, f2, f3, f4, f5, self.data_bag.M / (e1*(f1 + f3) + f2 + e2*f4 + e3*f5), carbon_emission

    def divide_into_group(self, chromosome, time_variable):
        """

        :param chromosome:
        :return:
        """
        grouped_chromosome = []
        q = deque()
        for i in chromosome:
            q.append(i)
        send = 0
        receive = 0
        to_time = 0  # to_time 记录当前route last_node 的离开时间
        put = []
        left = []
        route = []
        while q:
            cur_node = q.popleft()
            # print(cur_node)
            send += self.data_bag.data['交付需求/t'][cur_node]

            put.append(self.data_bag.data['交付需求/t'][cur_node])
            left.append(0)
            # print(send)
            receive += self.data_bag.data['取件需求/t'][cur_node]
            # 更新当前每个节点剩余
            tmp = 0
            for i in range(len(put)):
                tmp += put[i]
                left[i] = send - tmp
            check = [True for i in left if i + receive <= self.data_bag.Q]
            if send <= self.data_bag.Q and len(check) == len(left):  # 容量约束满足
                if route:  # route 非空
                    last_node = route[-1]
                    # tij = self.data_bag.dis_mat[last_node][cur_node] / self.data_bag.v1
                    # to_time += tij  # cur_node 到达时间 or to_time < self.data_bag.data['EET浮点数'][cur_node]
                    # to_time = cal_time(to_time, self.data_bag.dis_mat[last_node][cur_node])
                    if time_variable:
                        to_time, _ = cal_varying_time(to_time, self.data_bag.dis_mat[last_node][cur_node],
                                                      self.data_bag.coe_list)
                    else:
                        tij = self.data_bag.dis_mat[last_node][cur_node] / self.data_bag.v1
                        to_time += tij  # cur_node 到达时间 or to_time < self.data_bag.data['EET浮点数'][cur_node]
                    if to_time > self.data_bag.data['LLT浮点数'][cur_node]:  # 时间窗违反
                        send = 0
                        receive = 0
                        to_time = 0
                        put = []
                        left = []
                        q.appendleft(cur_node)  # 重新放回
                        grouped_chromosome.append(route)
                        route = []
                    else:
                        route.append(cur_node)
                        sij = (self.data_bag.data['交付需求/t'][cur_node] + self.data_bag.data['取件需求/t'][
                            cur_node]) / self.data_bag.v2
                        to_time += sij  # 更新下一节点离开时间

                else:
                    route.append(cur_node)
                    sij = (self.data_bag.data['交付需求/t'][cur_node] + self.data_bag.data['取件需求/t'][
                        cur_node]) / self.data_bag.v2
                    to_time = self.data_bag.data['ET浮点数'][cur_node] + sij  # 离开第一个客户时间

            else:  # 更新
                # print('=======================================================')
                send = 0
                receive = 0
                to_time = 0
                put = []
                left = []
                q.appendleft(cur_node)  # 重新放回
                grouped_chromosome.append(route)
                route = []

        if route:  # last check
            grouped_chromosome.append(route)

        grouped_chromosome_with_ware = []
        while grouped_chromosome:
            route = grouped_chromosome.pop()
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

            grouped_chromosome_with_ware.append(route)
        # print(grouped_chromosome_with_ware)
        return grouped_chromosome_with_ware

    def divide_group_by_stack(self, chromosome):

        pass

    def get_pop_fitness(self, pop, time_variable):
        """
        种群适应度
        """

        fitness = []
        for chromosome in pop:
            grouped_chromosome = self.divide_into_group(chromosome, time_variable)
            a, b, c, d, e, fitness_cur, carbon_emission = self.cal_fitness(grouped_chromosome, time_variable)
            if fitness_cur > self.fit_max:
                self.fit_max = fitness_cur
                self.individual = grouped_chromosome

                if e < self.data_bag.M:
                    self.reasonable_sol.append(grouped_chromosome)
                    self.reasonable_fit.append((a + b + c + d + e, a, b, c, d, e))
            # print(a, b, c, d, e)
            fitness.append(fitness_cur)
        self.y_best.append(self.data_bag.M / self.fit_max)
        return fitness

    def select(self, pop, fit_value):
        """
        轮盘赌选择个体
        """

        def cumsum(fit_value):

            t = 0
            for i in range(len(fit_value)):
                t += fit_value[i]
                fit_value[i] = t
            return fit_value

        newfit_value = []  # 存储累计概率
        total_fit = sum(fit_value)
        for i in range(self.popsize):
            #  计算每个适应度占适应度综合的比例
            newfit_value.append(fit_value[i] / total_fit)
        newfit_value = cumsum(newfit_value)

        ms = [random() for _ in range(self.popsize)]  # 随机数序列
        ms.sort()

        # 轮盘赌选择
        heap = [(-1, 0)]
        heapq.heapify(heap)  # 建立小根堆
        fitin = 0
        newin = 0
        newpop = [0] * self.popsize
        newfit = [0] * self.popsize
        while newin < self.popsize:
            #  选择--累计概率大于随机概率
            if ms[newin] < newfit_value[fitin]:
                newpop[newin] = pop[fitin]
                newfit[newin] = fit_value[fitin]
                newin += 1
                if heap and heap[0][0] < fit_value[fitin]:
                    heapq.heappush(heap, (fit_value[fitin], pop[fitin]))
                if len(heap) > self.popsize // 10:
                    heapq.heappop(heap)
            else:
                fitin += 1

        while heap:
            fit_tmp, chromosome = heapq.heappop(heap)
            newpop.append(chromosome)
            newfit.append(fit_tmp)

        newpop = pop[self.popsize // 10:] + newpop[-self.popsize // 10:]
        newfit = fit_value[self.popsize // 10:] + newfit[-self.popsize // 10:]

        return newpop, newfit

    def inner_cross(self, single1, single2):
        city_num = len(single1)
        # 交叉点
        cp1 = randint(0, city_num - 2)
        cp2 = randint(cp1 + 1, city_num - 1)
        # 交叉片段
        gene1 = single1[cp1:cp2]
        gene2 = single2[cp1:cp2]
        # 得到原序列通过改变序列的染色体，并复制出来备用
        child1_c = single1[cp2:] + single1[:cp2]
        child2_c = single2[cp2:] + single2[:cp2]

        # 去掉交叉后的序列
        for i in gene1:
            child2_c.remove(i)
        for i in gene2:
            child1_c.remove(i)
        child1_c = child1_c + gene2
        child2_c = child2_c + gene1

        single1 = child1_c[city_num - cp2:] + child1_c[:city_num - cp2]
        single2 = child2_c[city_num - cp2:] + child2_c[:city_num - cp2]
        return single1, single2

    def cross(self, pop, fitness, adaptive):
        """
        交叉
        """
        mean_fit = np.mean(fitness)
        max_fit = np.max(fitness)
        for i in range(0, self.popsize, 2):
            f_per = max(fitness[i], fitness[i + 1])
            if f_per >= mean_fit:
                cxpb = self.PC1 - (self.PC1 - self.PC2) * (f_per - mean_fit) / (max_fit - mean_fit)
            else:
                cxpb = self.PC1
            if fitness == False:
                cxpb = self.cross_pro
            if random() < cxpb:
                pop[i], pop[i + 1] = self.inner_cross(pop[i], pop[i + 1])
            else:
                pass

        return pop

    def mutation(self, pop, fitness, adaptive):
        """
        依表现型进行概率变异
        """
        mean_fit = np.mean(fitness)
        max_fit = np.max(fitness)
        for i in range(self.popsize):
            f_m = fitness[i]
            if f_m >= mean_fit:
                mutpb = self.PM1 - (self.PM1 - self.PM2) * (max_fit - f_m) / (max_fit - mean_fit)
            else:
                mutpb = self.PM1
            if fitness == False:
                mutpb = self.mutation_pro
            if random() < mutpb:
                # 变异
                u = randint(0, self.n - 1)
                v = randint(0, self.n - 1)

                idx1 = pop[i].index(u)
                idx2 = pop[i].index(v)
                pop[i][idx1], pop[i][idx2] = pop[i][idx2], pop[i][idx1]

        return pop

    def neighbor_search(self, grouped_chromosome, time_variable):
        vns = VariableNeighborSearch(grouped_chromosome, self.data_bag)
        return vns.run_vns(time_variable)

    @Timecounter
    def run(self, flag, adaptive=True, time_variable=True):  # time_variable 为True表示使用时变速度
        begin = time()
        pop = self.init_chrom_by_random(time_variable)
        print("计算中......")
        for _ in range(self.max_iterations):
            fitness = self.get_pop_fitness(pop, time_variable)
            self.y.append(self.data_bag.M / (sum(fitness) / self.popsize))
            pop, fitness = self.select(pop, fitness)
            pop = self.mutation(pop, fitness, adaptive)
            pop = self.cross(pop, fitness, adaptive)
            shuffle(pop)
            # print(self.data_bag.M / self.fit_max)
        self.in_st = self.reasonable_sol[-5]
        self.individual1 = self.individual
        self.individual, y, y_best = self.neighbor_search(self.individual, time_variable)
        print('算法结束')
        if flag:
            # label = "普通遗传算法联合取送一体化情境下"
            # print_message(self.individual1, label, time_variable, self)
            label = "改进遗传算法联合取送一体化情境下"
            print_message(self.individual, label, time_variable, self)
            # label = "不考虑时空聚类初始解如下"
            # print_message(self.in_no_st, label, time_variable, self)
            # label = "考虑时空聚类的解如下"
            # print_message(self.in_st, label, time_variable, self)
            # print(f'联合取送一体化情境下,算法总耗时:{time() - begin}秒')

            print('=======================================================================================')
            print('画图中，请稍等...')
        y_best1 = self.y_best + y_best
        y1 = self.y + y
        self.y = self.y * 2 * 5
        self.y_best = self.y_best * 2 * 5
        self.y.sort(reverse=True)
        self.y_best.sort(reverse=True)
        return self.individual, self.individual1, y1, y_best1, self.y, self.y_best

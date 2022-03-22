import numpy as np


# 综合燃油排放模型 直接调用该类中的方法来计算燃料的消耗
class CEME:
    def __init__(self) -> None:
        super().__init__()
        self.epsilon = 1  # 燃料空气质量比
        self.G = 0.2  # 发动机的摩擦系数
        self.N = 33  # 发动机转速
        self.Vs = 2.78  # 发动机排量
        self.neta = 0.9  # 发动机转换效率
        self.mu = 44  # 燃料充分燃烧的热量值(KJ/g)
        self.P = 115  # 发动机功率
        self.neta_tf = 0.4  # 汽车的传统动力效率
        self.P_acc = 0  # 车辆附件运行损失功率需求
        self.M = 4.3  # 车辆总重量
        self.a = 0  # 车辆加速度
        self.g = 9.81  # 重力加速度
        self.seta = 0  # 道路坡度
        self.C_d = 0.7  # 空气阻力系数
        self.roll = 1.2041  # 空气密度
        self.S = 7.2  # 迎风面积
        self.C_r = 0.01  # 车轮滚动阻力系数
        self.transform = 737  # 燃料转换系数

    def get_lambda(self):
        return self.epsilon / (self.transform * self.mu)

    def get_t(self):
        return self.G * self.N * self.Vs

    def get_fie(self):
        return self.a + self.g * np.sin(self.seta) + self.g * self.C_r * np.cos(
            self.seta)

    def get_beta(self):
        return 0.5 * self.C_d * self.roll * self.S

    def get_alpha(self):
        return 1 / (1000 * self.transform * self.neta_tf * self.neta)

    def get_fuel_cost(self, speed, distance):
        lam = self.get_lambda()
        t = self.get_t()
        fie = self.get_fie()
        beta = self.get_beta()
        alpha = self.get_alpha()
        f = lam * (t + (self.M * fie * speed + beta * np.power(speed, 3)) * alpha) * distance / speed
        return f

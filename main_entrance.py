"""
算法入口


"""
from genetic_algorithm import *
from read_data import *
from plot_func import *
import tkinter
from visual import center_window, test
from analysis import analysisAll, analysisQuotas, analysisCarbonPrice
from tools import clip

win = None
d = ReadData()
data = d.run()


# 菜单最小化
def exit_home():
    win.iconify()


def basic_function(event):
    print("*******正在运行基础方法(恒定速度)**********")
    exit_home()
    ga = GeneticAlgorithm(data)
    grouped_chromosome, in_1, y, y_best, y1, y_best1 = ga.run(True, False, False)
    clip(y)
    clip(y_best)
    scatter_func(data, grouped_chromosome)
    plot_func(y, y_best)
    scatter_func(data, in_1)
    plot_func(y1, y_best1)


def basic_function_v(event):
    print("*******正在运行基础方法(时变速度)**********")
    exit_home()
    ga = GeneticAlgorithm(data)
    grouped_chromosome, in_1, y, y_best, y1, y_best1 = ga.run(True, False, True)
    clip(y)
    clip(y_best)
    scatter_func(data, grouped_chromosome)
    plot_func(y, y_best)
    #scatter_func(data, in_1)
    #plot_func(y1, y_best1)


def adaptive_function(event):
    print("*******正在运行自适应方法(恒定速度)**********")
    exit_home()
    ga = GeneticAlgorithm(data)
    grouped_chromosome, in_1, y, y_best, y1, y_best1 = ga.run(True, True, False)  # 把这里的第一个参数换成True就能打印输出
    clip(y)
    clip(y_best)
    scatter_func(data, grouped_chromosome)
    plot_func(y, y_best)
    # scatter_func(data, in_1)
    # plot_func(y1, y_best1)


def adaptive_function_v(event):
    print("*******正在运行自适应方法(时变速度)**********")
    exit_home()
    ga = GeneticAlgorithm(data)
    grouped_chromosome, in_1, y, y_best, y1, y_best1 = ga.run(True, True, True)
    clip(y)
    clip(y_best)
    scatter_func(data, grouped_chromosome)
    plot_func(y, y_best)
    # scatter_func(data, in_1)
    # plot_func(y1, y_best1)


def analysis_carbon_price(event):
    exit_home()
    carbon_price, carbon_cost, total_cost = analysisCarbonPrice(data=data)


def analysis_carbon_quotas(event):
    exit_home()
    carbon_quotas, car_cost, carbon_emission = analysisQuotas(data=data)


def analysis_all(event):
    exit_home()
    analysisAll(data=data)


if __name__ == '__main__':
    win = tkinter.Tk()
    win.title('给姐姐写的简单可视化窗口')
    center_window(win, width=600, height=450)

    btn = tkinter.Button(win, text='基本运行（恒定速度）', font=(None, 24), width=30, height=1)  # 设置高度
    btn_v = tkinter.Button(win, text='基本运行（时变速度）', font=(None, 24), width=30, height=1)  # 设置高度
    btn1 = tkinter.Button(win, text='自适应（恒定速度）', font=(None, 24), width=30, height=1)  # 设置高度
    btn1_v = tkinter.Button(win, text='自适应（时变速度）', font=(None, 24), width=30, height=1)  # 设置高度
    btn2 = tkinter.Button(win, text='分析碳价', font=(None, 24), width=30, height=1)  # 设置高度
    btn3 = tkinter.Button(win, text='分析碳配额', font=(None, 24), width=30, height=1)  # 设置高度
    btn4 = tkinter.Button(win, text='分析碳价+碳配额', font=(None, 24), width=30, height=1)  # 设置高度
    btn.bind("<Button-1>", basic_function)
    btn_v.bind("<Button-1>", basic_function_v)
    btn1.bind("<Button-1>", adaptive_function)
    btn1_v.bind("<Button-1>", adaptive_function_v)
    btn2.bind("<Button-1>", analysis_carbon_price)
    btn3.bind("<Button-1>", analysis_carbon_quotas)
    btn4.bind("<Button-1>", analysis_all)
    btn.grid(row=1, column=1, padx=60, pady=10)
    btn_v.grid(row=2, column=1, padx=60, pady=10)
    btn1.grid(row=3, column=1, padx=60, pady=10)
    btn1_v.grid(row=4, column=1, padx=60, pady=10)
    btn2.grid(row=5, column=1, padx=60, pady=10)
    btn3.grid(row=6, column=1, padx=60, pady=10)
    btn4.grid(row=7, column=1, padx=60, pady=10)

    win.mainloop()

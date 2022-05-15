"""

"""

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx

from matplotlib.font_manager import FontProperties

def scatter_func(data, grouped_chromosome):
    """

    :param data:
    :param grouped_chromosome:
    :return:
    """
    plt.figure(figsize=(80, 32), dpi=80)

    x_receive = []
    y_receive = []
    x_send = []
    y_send = []
    x_ware = []
    y_ware = []

    for i in range(data.m):
        if data.data['取件需求/t'][i]:  # 取
            x_receive.append(data.data['x'][i])
            y_receive.append(data.data['y'][i])

        if not data.data['取件需求/t'][i]:  # 送
            x_send.append(data.data['x'][i])
            y_send.append(data.data['y'][i])

    for i in data.warehouse_list:    # 仓
        x_ware.append(data.data['x'][i])
        y_ware.append(data.data['y'][i])


    fig, ax = plt.subplots()
    # ax = plt.axes()
    ax.scatter(x_receive + x_send, y_receive + y_send, color='black', marker='o', s=18, label=u'客户点')
    ax.scatter(x_ware, y_ware, color='red', marker='s', s=30, label=u'配送中心')

    ax.set_xlim([0, 40])
    ax.set_ylim([0, 40])
    ax.set_xlabel('X/KM')
    ax.set_ylabel('Y/KM')

    for i in data.warehouse_list:
        # plt.text((data.data['x'][i], data.data['y'][i]),i,size=5)
        ax.annotate(i, (data.data['x'][i] + 0.6, data.data['y'][i] + 0.7), fontsize=10, ha='center')

    for i in range(data.m):
        ax.annotate(i+1, (data.data['x'][i]+0.6, data.data['y'][i]+0.6), fontsize=9, ha='center')  # ,

    font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=10)
    plt.legend(prop=font, fontsize=8, loc='upper right', markerscale=0.6)

    #plt.legend(['customers', 'warehouse'], fontsize=7, loc='upper right', markerscale=0.5)

    cmap = plt.cm.jet
    cNorm = colors.Normalize(vmin=0, vmax=len(grouped_chromosome))
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

    for k, path in enumerate(grouped_chromosome):
        x_list = []
        y_list = []
        for node in path:
            x_list.append(data.data['x'][node])
            y_list.append(data.data['y'][node])

        colorVal = scalarMap.to_rgba(k)
        for i in range(1, len(x_list)):

            plt.arrow(x_list[i - 1], y_list[i - 1], x_list[i] - x_list[i - 1], y_list[i] - y_list[i - 1],
                      length_includes_head=True, head_width=0.5, lw=0.8,
                      color=colorVal)
        # plt.plot(
        #             x_list,
        #             y_list,
        #             color='black',
        #             lw=2,  # 线宽
        #             ls='-',  # 线条类型
        #         )
    # for path in real_path:
    #     x_list, y_list = [], []
    #     for node in path:
    #         x, y = info[node]['x_y']
    #         x_list.append(x)
    #         y_list.append(y)
    #     plt.plot(
    #         x_list,
    #         y_list,
    #         color='black',
    #         lw=2,  # 线宽
    #         ls='-',  # 线条类型
    #     )
    #
    # for path in drone_path:
    #     x_list, y_list = [], []
    #     for node in path:
    #         x, y = info[node]['x_y']
    #         x_list.append(x)
    #         y_list.append(y)
    #     plt.plot(
    #         x_list,
    #         y_list,
    #         color='red',
    #         lw=2,  # 线宽
    #         ls='--',  # 线条类型
    #     )
    plt.xticks(size=10)
    plt.yticks(size=10)
    plt.show()


def plot_func(y, y_best):
    """

    :param y:
    :param y_best:
    :return:
    """
    plt.figure(figsize=(40, 16), dpi=80)
    n = len(y)
    m = len(y_best)
    y_best += [y_best[-1]] * (n - m)
    # y = y[: n // 2]
    # y_best = y_best[: n // 2]
    x = list(range(n))
    plt.plot(
        x,
        y,
        color='black',
        lw=2,  # 线宽
        ls='-',  # 线条类型
        label=u'平均值',
    )

    plt.plot(
        x,
        y_best,
        color='red',
        lw=2,  # 线宽
        ls='-',  # 线条类型
        label=u'最优值',
    )

    plt.xticks(size=25)
    plt.yticks(size=25)
    # plt.rcParams['font_set.sans-serif'] = ['Microsoft YaHei']
    font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=30)
    plt.xlabel(u'迭代次数', fontproperties=font_set, fontsize=30)
    plt.ylabel(u'目标函数值', fontproperties=font_set, fontsize=30)
    plt.legend(prop=font_set, fontsize=20, loc='upper right', markerscale=0.6, numpoints=5)


   # plt.legend(['pop average value', 'pop best value'], fontsize=40, loc='upper right', markerscale=1.0)

    #plt.xticks(size=40)
    #plt.yticks(size=40)

    plt.show()

    pass


# _locations = [
#     (4, 4),   # depot
#     (4, 4),   # unload depot_prime
#     (4, 4),   # unload depot_second
#     (4, 4),   # unload depot_fourth
#     (4, 4),   # unload depot_fourth
#     (4, 4),   # unload depot_fifth
#     (2, 0),
#     (8, 0),   # locations to visit
#     (0, 1),
#     (1, 1),
#     (5, 2),
#     (7, 2),
#     (3, 3),
#     (6, 3),
#     (5, 5),
#     (8, 5),
#     (1, 6),
#     (2, 6),
#     (3, 7),
#     (6, 7),
#     (0, 8),
#     (7, 8)]
#
#
# plt.figure(figsize=(10, 10))
# p1 = [l[0] for l in _locations]
# p2 = [l[1] for l in _locations]
# plt.plot(p1[:6], p2[:6], 'g*', ms=20, label='depot')
# plt.plot(p1[6:], p2[6:], 'ro', ms=15, label='customer')
# plt.grid(True)
# plt.legend(loc='lower left')
#
# way = [[0, 12, 18, 17, 16, 4, 14, 10, 11, 13, 5], [0, 6, 9, 8, 20, 3], [0, 19, 21, 15, 7, 2]]  #
#
# cmap = plt.cm.jet
# cNorm = colors.Normalize(vmin=0, vmax=len(way))
# scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)
#
# for k in range(0, len(way)):
#   way0 = way[k]
#   colorVal = scalarMap.to_rgba(k)
#   for i in range(0, len(way0)-1):
#     start = _locations[way0[i]]
#     end = _locations[way0[i+1]]
# #     plt.arrow(start[0], start[1], end[0]-start[0], end[1]-start[1], length_includes_head=True,
# #         head_width=0.2, head_length=0.3, fc='k', ec='k', lw=2, ls=lineStyle[k], color='red')
#     plt.arrow(start[0], start[1], end[0]-start[0], end[1]-start[1],
#          length_includes_head=True, head_width=0.2, lw=2,
#          color=colorVal)
# plt.show()
if __name__ == '__main__':
    # import pandas as pd
    #
    # df1 = pd.read_excel('自适应1.xls')
    # df1.head()
    # x = [i for i in range(0, 501)]
    # avgFit = []
    # minFit = []
    # for i in range(0, 501):
    #     avgFit.append(df1['平均值'][i])
    #     minFit.append(df1["最优值"][i])
    #
    # plot_func(avgFit , minFit)

    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import numpy as np
    import pylab

    plt.figure(figsize=(40, 16), dpi=80)
    font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=30)
    carbon_price = []
    carbon_emission = []
    df1 = pd.read_excel('碳价.xls')
    print(df1.columns)
    print(df1)
    for i in range(0, 81):
        carbon_price.append(df1['碳价'][i])
        carbon_emission.append(df1['碳排放'][i])

    plt.xticks(size=25)
    plt.yticks(size=25)
    plt.xlabel(u"碳价(元/kg)",fontproperties=font_set,fontsize=30)  # X轴标签
    plt.ylabel(u"碳排放量(Kg)",fontproperties=font_set,fontsize=30)  # Y轴标签
    plt.plot(carbon_price, carbon_emission, marker='o', ms=10, label=u'碳排放量',lw=3)
    plt.legend(prop=font_set, fontsize=20, loc='best', markerscale=1, numpoints=1)
    parameter = np.polyfit(carbon_price, carbon_emission, 4)  # n=1为一次函数，返回函数参数
    f = np.poly1d(parameter)  # 拼接方程
    pylab.plot(carbon_price, f(carbon_price), "r.", ms=5)
    plt.show()



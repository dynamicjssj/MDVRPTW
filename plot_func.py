"""

"""

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx


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
    ax.scatter(x_receive + x_send, y_receive + y_send, color='red', marker='o', s=50)
    ax.scatter(x_ware, y_ware, color='blue', marker='s', s=50)

    for i in range(data.m):
        ax.annotate(i, (data.data['x'][i], data.data['y'][i]))    # ,

    plt.legend(['customers', 'warehouse'], fontsize=7, loc='upper right', markerscale=0.5)

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
                      length_includes_head=True, head_width=0.2, lw=0.6,
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
    y = y[: n // 2]
    y_best = y_best[: n // 2]
    x = list(range(n // 2))
    plt.plot(
        x,
        y,
        color='black',
        lw=2,  # 线宽
        ls='-',  # 线条类型
    )

    plt.plot(
        x,
        y_best,
        color='red',
        lw=2,  # 线宽
        ls='-',  # 线条类型
    )

    plt.legend(['pop average value', 'pop best value'], fontsize=40, loc='upper right', markerscale=1.0)
    plt.xticks(size=40)
    plt.yticks(size=40)
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



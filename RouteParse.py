# 用于将输入的路径转化为载重和时间
import tkinter as tk
from main_entrance import center_window
from read_data import *
from genetic_algorithm import GeneticAlgorithm
from print_func import get_time

windows = tk.Tk()
windows.title("根据路径获取时间、载重序列")
# 设置输入框，对象是在windows上，show参数--->显示文本框输入时显示方式None:文字不加密，show="*"加密
center_window(windows, 500, 300)
d = ReadData()
data = d.run()
ga = GeneticAlgorithm(data)


def generate_series():
    route = edit_text.get(1.0, 'end')
    route = route.replace(" ", '')
    route = route.replace('\n', '')
    routes = route.split('-')
    print(type(routes))
    for i in range(len(routes)):
        if routes[i] == 'A' or routes[i] == 'B' or routes[i] == 'C':
            pass
        else:
           routes[i] =  int(routes[i])
    start_time, time_route, end_time = get_time(routes, time_variable=True, ga=ga)
    time_route = start_time+'-'+time_route+'-'+end_time
    show_label.configure(text=time_route)


def clear_input():
    edit_text.delete(0.0, 'end')


# 设置提示标签
hint_label = tk.Label(windows, height=2, text="请输入路径，如A-1-2-3-15-B")
hint_label.grid(row=1, column=1)

# 设置文本框
edit_text = tk.Text(windows, height=2, width=72)
edit_text.grid(row=2, column=1, pady=10)

# 设置显示标签
show_label = tk.Label(windows, height=2, text="结果展示处")
show_label.grid(row=3, column=1)
# 清空文本框按钮
clear_button = tk.Button(windows, text='清空按钮', command=clear_input)
clear_button.grid(row=4, column=1)
# 设置 运行按钮
run_button = tk.Button(windows, text='生成序列', command=generate_series)
run_button.grid(row=5, column=1)

if __name__ == '__main__':
    windows.mainloop()

# coding:utf-8
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# 轴名称
plt.xlabel("Experiment ID")
plt.ylabel("# exactly learned model ")

# X轴数据
x_title = ['manual-1', 'manual-2', 'manual-3', '4_2_10-1', '4_2_10-2', '4_2_10-3', '6_2_10-1', '6_2_10-2', '6_2_10-3', '6_2_20-1', '6_2_20-2', '6_2_20-3', '6_2_50-1', '6_2_50-2', '6_2_50-3',
           '6_4_10-1', '6_4_10-2', '6_4_10-3', '6_6_10-1', '6_6_10-2', '6_6_10-3', '8_2_10-1', '8_2_10-2', '8_2_10-3', '10_2_10-1', '10_2_10-2', '10_2_10-3']
x = range(len(x_title))
plt.xticks(x, x_title, rotation=90)

# Y轴数据
Y_1 = [15, 15, 15, 15, 15, 15, 15, 15, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 14, 15, 15, 15, 15, 15]
Y_2 = [15, 15, 1, 15, 15, 15, 15, 15, 14, 15, 2, 15, 15, 2, 15, 15, 14, 15, 11, 14, 15, 2, 15, 7, 15, 11, 15]
Y_3 = [15, 15, 5, 15, 15, 15, 15, 15, 15, 15, 3, 15, 15, 3, 15, 15, 15, 14, 15, 15, 15, 3, 15, 9, 14, 12, 15]

plt.plot(x_title, Y_1, linestyle='-', color="red", label="With heuristic test case generation", marker='o')
plt.plot(x_title, Y_2, linestyle='-', color="dodgerblue", label="With purely random testing ", marker='^')
plt.plot(x_title, Y_3, linestyle='-', color="midnightblue", label="With A&T's method", marker='+')

plt.legend(loc="lower left", prop={"size": 8})

plt.tight_layout()

plt.savefig('tc_generation_correct.pdf', dpi=1200, format='pdf')
plt.show()




# # 轴名称
# plt.xlabel("Experiment ID")
# plt.ylabel("Mean passing rate")
#
# # X轴数据
# x_title = ['manual-1', 'manual-2', 'manual-3', '4_2_10-1', '4_2_10-2', '4_2_10-3', '6_2_10-1', '6_2_10-2', '6_2_10-3', '6_2_20-1', '6_2_20-2', '6_2_20-3', '6_2_50-1', '6_2_50-2', '6_2_50-3',
#            '6_4_10-1', '6_4_10-2', '6_4_10-3', '6_6_10-1', '6_6_10-2', '6_6_10-3', '8_2_10-1', '8_2_10-2', '8_2_10-3', '10_2_10-1', '10_2_10-2', '10_2_10-3']
# x = range(len(x_title))
# plt.xticks(x, x_title, rotation=70)
#
# # Y轴数据
# Y_1 = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9995426666666667, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9999826666666666, 1.0, 1.0, 1.0, 1.0, 1.0]
# Y_2 = [1.0, 1.0, 0.9998466666666666, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9998946666666666, 1.0, 0.9997493333333333, 1.0, 1.0, 0.9999426666666665, 1.0, 1.0, 1.0, 1.0, 0.9999626666666667, 0.9999786666666667,
#        1.0, 0.9996240000000001, 1.0, 0.9996933333333333, 1.0, 0.999576, 1.0]
# Y_3 = [1.0, 1.0, 0.9999226666666666, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9999133333333334, 1.0, 1.0, 0.999916, 1.0, 1.0, 1.0, 0.9999586666666667, 1.0, 1.0, 1.0, 0.9998039999999999, 1.0,
#        0.9997440000000001, 0.999964, 0.9998640000000001, 1.0]
#
# plt.plot(x_title, Y_1, linestyle='-', color="red", label="With heuristic test case generation", marker='o')
# plt.plot(x_title, Y_2, linestyle='-', color="dodgerblue", label="With purely random testing ", marker='^')
# plt.plot(x_title, Y_3, linestyle='-', color="midnightblue", label="With A&T's method", marker='+')
#
#
# def to_percent(temp, position):
#     a = ["100%", "99.99%", "99.98%", "99.97%", "99.96%", "99.95%"]
#     b = [1.0000, 0.9999, 0.9998, 0.9997, 0.99960, 0.9995]
#     for i in range(len(b)):
#         if b[i] <= temp:
#             return a[i]
#
#
# plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
#
# plt.legend(loc="lower left", prop={"size": 8})
#
# plt.tight_layout()
#
# plt.savefig('tc_generation_passing.png', dpi=1200, format='png')
# plt.show()




# # 轴名称
# plt.xlabel("Experiment ID")
# plt.ylabel("# exactly learned model ")
#
# # X轴数据
# x_title = ['manual-1', 'manual-2', 'manual-3',  '4_2_10-1', '4_2_10-2', '4_2_10-3', '6_2_10-1', '6_2_10-2', '6_2_10-3', '6_2_20-1', '6_2_20-2', '6_2_20-3', '6_2_50-1', '6_2_50-2', '6_2_50-3',
#            '6_4_10-1', '6_4_10-2', '6_4_10-3', '6_6_10-1', '6_6_10-2', '6_6_10-3', '8_2_10-1', '8_2_10-2', '8_2_10-3', '10_2_10-1', '10_2_10-2', '10_2_10-3']
# x = range(len(x_title))
# plt.xticks(x, x_title, rotation=70)
#
# # Y轴数据
# Y_1 = [ 15, 15, 15, 15, 15, 15, 15, 15, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 14, 15, 15, 15, 15, 15]
# Y_2 = [15, 15, 15, 15, 15, 15, 15, 0, 0, 0, 0, 15, 15, 0, 15, 15, 15, 15, 15, 15, 15, 0, 14, 15, 15, 0, 15]
# Y_3 = [14, 15, 0, 10, 0, 5, 8, 13, 3, 12, 4, 9, 15, 4, 15, 13, 15, 15, 15, 14, 15, 7, 9, 2, 14, 10, 12]
#
# plt.plot(x_title, Y_1, linestyle='-', color="red", label="With two mutation operators", marker='o')
# plt.plot(x_title, Y_2, linestyle='-', color="dodgerblue", label="With timed mutation operator", marker='^')
# plt.plot(x_title, Y_3, linestyle='-', color="midnightblue", label="With split-state mutation operator", marker='+')
#
# plt.legend(loc="lower left", prop={"size": 8})
#
# plt.tight_layout()
#
# plt.savefig('tc_ops_correct.pdf', dpi=1200, format='pdf')
# plt.show()




# # 轴名称
# plt.xlabel("Experiment ID")
# plt.ylabel("Mean passing rate")
#
# # X轴数据
# x_title = ['manual-1', 'manual-2', 'manual-3', '4_2_10-1', '4_2_10-2', '4_2_10-3', '6_2_10-1', '6_2_10-2', '6_2_10-3', '6_2_20-1', '6_2_20-2', '6_2_20-3', '6_2_50-1', '6_2_50-2', '6_2_50-3',
#            '6_4_10-1', '6_4_10-2', '6_4_10-3', '6_6_10-1', '6_6_10-2', '6_6_10-3', '8_2_10-1', '8_2_10-2', '8_2_10-3', '10_2_10-1', '10_2_10-2', '10_2_10-3']
# x = range(len(x_title))
# plt.xticks(x, x_title, rotation=70)
#
# # Y轴数据
# Y_1 = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9995426666666667, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9999826666666666, 1.0, 1.0, 1.0, 1.0, 1.0]
# Y_2 = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.4784013333333333, 0.8448306666666666, 0.5301800000000001, 0.47225866666666677, 1.0, 1.0, 0.7492866666666668, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
#        0.8121786666666666, 0.9811133333333333, 1.0, 1.0, 0.8747893333333335, 1.0]
# Y_3 = [0.9989319999999999, 1.0, 0.9835026666666667, 0.8339866666666665, 0.5320760000000001, 0.7829773333333332, 0.8610546666666666, 0.960632, 0.9941933333333334, 0.9952173333333334,
#        0.9906626666666667, 0.9901306666666666, 1.0, 0.9997973333333333, 1.0, 0.9995746666666666, 1.0, 1.0, 1.0, 0.998464, 1.0, 0.9998, 0.7602666666666666, 0.7640666666666667, 0.999808,
#        0.9961413333333334, 0.9501373333333334]
#
# plt.plot(x_title, Y_1, linestyle='-', color="red", label="With two mutation operators", marker='o')
# plt.plot(x_title, Y_2, linestyle='-', color="dodgerblue", label="With timed mutation operator", marker='^')
# plt.plot(x_title, Y_3, linestyle='-', color="midnightblue", label="With split-state mutation operator", marker='+')
#
#
# def to_percent(temp, position):
#     a = ["100%", "90%", "80%", "70%", "60%", "50%"]
#     b = [1.0000, 0.9, 0.8, 0.7, 0.60, 0.5]
#     for i in range(len(b)):
#         if b[i] <= temp:
#             return a[i]
#
#
# plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
#
# plt.legend(loc="lower left", prop={"size": 8})
#
# plt.tight_layout()
#
# plt.savefig('tc_ops_passing.pdf', dpi=1200, format='pdf')
# plt.show()
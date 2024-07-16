import matplotlib.pyplot as plt
import time
import numpy as np

from RiskFuncManage import *

class getFig:
    def __init__(self, labels, sizes, file_path_=None, fig_name=None, file_name_=None, get_path=False):
        i = len(sizes) - 1
        while i >= 0:
            if sizes[i] == 0:
                sizes.pop(i)
                labels.pop(i)
            i -= 1
        if file_path_ is None:
            file_path_ = ""
        else:
            file_path_ = file_path_ + "\\"
        self.file_path_ = file_path_
        self.fig_name = fig_name
        self.labels = labels
        self.sizes = sizes
        self.file_name_ = file_name_
        self.get_path = get_path

    def get_fig(self):
        # 绘制饼状图
        plt.figure(figsize=(8, 6))
        patches, texts, autotexts = plt.pie(self.sizes, labels=self.labels, autopct='%1.1f%%', shadow=True,
                                            startangle=140)

        # 创建标题
        if self.fig_name is not None:
            plt.title(self.fig_name)

        # 保证饼状图是圆形
        plt.axis('equal')

        # 计算文本框的位置
        left, bottom, width, height = 0.05, 0.1, 0.1, 0.9
        ax2 = plt.axes([left, bottom, width, height])

        # 在右侧添加描述性文本框
        ax2.axis('off')  # 隐藏坐标轴
        ax2.set_xlim([0, 1])  # 设置x轴范围
        ax2.set_ylim([0, 1])  # 设置y轴范围

        # 添加文本
        for i, label in enumerate(self.labels):
            ax2.text(0.05, 0.95 - i * 0.05, f"{label}: {self.sizes[i]}", transform=ax2.transAxes)

        # 图片保存
        if self.file_name_ is None:
            local_time = time.localtime()
            self.file_name_ = time.strftime("%Y_%m_%d_%H_%M_%S", local_time)
            self.file_name_ = self.file_name_ + '.jpg'
        path = self.file_path_ + self.file_name_
        plt.savefig(path)

        # 是否返回
        if self.get_path:
            return path


if __name__ == "__main__":
    file_path = r"C:\Users\86177\Desktop\test\test.c"
    manager = FunctionManager(file_path)
    results = manager.riskFunction()
    print(results)

    labels = manager.get_fig_labels_high()
    sizes = manager.get_fig_sizes_high()
    path_name = getFig(labels, sizes, r"C:\Users\86177\Desktop\test", "total",None,True).get_fig()
    print(path_name)
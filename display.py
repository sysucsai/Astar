import sys
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import string
import random
import Astar
import math

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#   保存了0-9的阶乘
fac = tuple([math.factorial(i) for i in range(10)])

# 画布，用来让networkx画图，并用matplotlib的pyplot输出图像
class MyCanvas(QWidget):
    def __init__(self, canvas_no, parent=None):
        super(MyCanvas, self).__init__(parent)
        self.canvas_no = canvas_no  # 这是pyplot的显示区编号
        self.figure1 = plt.figure(canvas_no)  # 指定到哪个pyplot显示区，并返回显示区，初始化时使用返回值绑定到画布
        self.canvas1 = FigureCanvas(self.figure1) # 添加画布并绑定显示区
        self.layout = QHBoxLayout(self) # 建立这个Widget中的框架
        self.layout.addWidget(self.canvas1)     # 画布添加到框架

        #   networkx的画图属性
        self.options = {
            'node_color': 'black',
            'node_size': 1,
            'width':0.5,
        #    'node_shape' : 's',
            'alpha' : 0.5,
            'font_size':7,
            'with_labels':True,
        }

    # 刷新（重绘）画布
    def update_figure(self, G, root):
        self.figure1 = plt.figure(self.canvas_no)  # 回到自己的显示区
        plt.clf()   # 清空显示区

        # 一系列步骤创造networkx图的点的排列方式
        shellLay = [[root]]
        tmp = [root]
        close = tmp
        while len(tmp) != 0:
            thisLay = [[j for j in nx.all_neighbors(G, i)] for i in tmp]
            shellLay.append([])
            for i in thisLay:
                shellLay[-1] += i
            for i in close:
                while i in shellLay[-1]:
                    shellLay[-1].remove(i)
            tmp = shellLay[-1]
            if len(shellLay[-1]) <= 1:
                shellLay[-2] += shellLay[-1]
                shellLay.remove(shellLay[-1])
            close += tmp

        #   画图，指定点排列，指定画图属性
        nx.draw_shell(G, nlist=shellLay, **self.options)
        self.canvas1.draw()

class ApplicationWindow(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        self.on = 0     # 看似是说明是否开始了，实际是用来保存当前步数 :)
        self.LayoutInit()   # 调用布局设置
        self.initList = [1,2,3,8,0,4,7,6,5] # 初始状态表
        self.goal = [1,2,3,8,0,4,7,6,5]     # 目标状态表
        #1 2 3
        #8 0 4
        #7 6 5
        self.Astar_h1 = Astar.Astar(self.initList, self.goal, 1)    # 生成h1的Astart类
        self.Astar_h2 = Astar.Astar(self.initList, self.goal, 2)    # 生成h2的Astart类
        self.G1 = nx.Graph()    #   创建h1的图
        self.G2 = nx.Graph()    #   创建h2的图
                                                            #list_2_grid是一个将列表转换成矩阵自负串的函数
        self.G1.add_node(self.list_2_grid(self.initList))  # 将初始状态列表换成结点放入图中
        self.G2.add_node(self.list_2_grid(self.initList))  # 同上
        self.show_h1()      # 文字初始化
        self.show_h2()      # 文字初始化

        #   计时器，一段时间执行一步循环
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(100)

    # 布局设置
    def LayoutInit(self):
        # h1的标题、画布、标签、步骤
        self.label_h1 = QLabel("h1:",self)
        self.canvas_h1 = MyCanvas(1, self)
        self.attrib_h1 = QLabel(" 结点\t  步数\t  总拓展数  OPEN表结点数\th(n)\t  f(n)",self)
        self.text_h1 = QTextEdit(self)
        self.text_h1.setReadOnly(True)

        # h2的标题、画布、标签、步骤
        self.label_h2 = QLabel("h2:",self)
        self.canvas_h2 = MyCanvas(2, self)
        self.attrib_h2 = QLabel(" 结点\t  步数\t  总拓展数  OPEN表结点数\th(n)\t  f(n)\t",self)
        self.text_h2 = QTextEdit(self)
        self.text_h2.setReadOnly(True)

        # 九宫格
        self.gridEntry = [[QLabel(self) for i in range(3)] for j in range(3)]
        self.gridRow = [QHBoxLayout() for i in range(3)]
        self.grid = QVBoxLayout()
        pe = QPalette() #   背景样式
        pe.setColor(QPalette.Background,Qt.white)
        for j in range(3):
            for i in range(3):
                self.gridEntry[j][i].setAutoFillBackground(True)
                self.gridEntry[j][i].setPalette(pe)
                self.gridEntry[j][i].setText(str(j*3 + i))
                self.gridEntry[j][i].setFixedWidth(40)
                self.gridEntry[j][i].setFixedHeight(40)
                self.gridEntry[j][i].setFont(QFont("Roman times",20,QFont.Bold))# 字体、大小、加粗
                self.gridRow[j].addWidget(self.gridEntry[j][i])
            self.grid.addLayout(self.gridRow[j])

        # 随机生成按钮
        self.randomButton = QPushButton("随机生成")
        self.randomButton.clicked.connect(self.randomGenerate)

        # 开始按钮
        self.startButton = QPushButton("开始")
        self.startButton.clicked.connect(self.start)

        # 右下结果显示表
        self.resultEntry =[[QLabel(self) for i in range(3)] for j in range(4)]
        self.resultRow = [QHBoxLayout() for i in range(4)]
        self.resultTable = QVBoxLayout()
        for j in range(4):
            for i in range(3):
                self.resultEntry[j][i].setFixedWidth(100)
                self.resultEntry[j][i].setFixedHeight(40)
                self.resultEntry[j][i].setText("0")
                self.resultRow[j].addWidget(self.resultEntry[j][i])
            self.resultTable.addLayout(self.resultRow[j])
        self.resultEntry[0][0].setText("结果")
        self.resultEntry[0][1].setText("h1")
        self.resultEntry[0][2].setText("h2")
        self.resultEntry[1][0].setText("步数")
        self.resultEntry[2][0].setText("节点数")
        self.resultEntry[3][0].setText("f*（S0）")

        # 加入框架###################################################################
        # 第一大列
        self.column1 = QVBoxLayout()
        self.column1.addWidget(self.label_h1)
        self.column1.addWidget(self.canvas_h1)
        self.column1.addWidget(self.attrib_h1)
        self.column1.addWidget(self.text_h1)

        # 第二大列
        self.column2 = QVBoxLayout()
        self.column2.addWidget(self.label_h2)
        self.column2.addWidget(self.canvas_h2)
        self.column2.addWidget(self.attrib_h2)
        self.column2.addWidget(self.text_h2)

        # 第三大列
        self.column3 = QVBoxLayout()
        self.column3.addStretch(1)
        self.column3.addLayout(self.grid)
        self.column3.addStretch(1)
        self.column3.addWidget(self.randomButton)
        self.column3.addWidget(self.startButton)
        self.column3.addStretch(1)
        self.column3.addLayout(self.resultTable)
        self.column3.addStretch(1)

        # 主框架
        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.column1)
        self.mainLayout.addLayout(self.column2)
        self.mainLayout.addLayout(self.column3)

        #   框架生效
        self.setLayout(self.mainLayout)

    # 随机生成按钮事件
    def randomGenerate(self):
        self.on = 0
        self.text_h1.setText("")
        self.text_h2.setText("")
        indexi = 1
        indexj = 1
        tempList = [1,2,3,8,0,4,7,6,5]
        for k in range(5):
            go = [1,2,3,4]
            if indexi == 0:
                go.remove(1)
            if indexi == 2:
                go.remove(2)
            if indexj == 0:
                go.remove(3)
            if indexj == 2:
                go.remove(4)
            k = random.sample(go,1)[0]
            if k == 1:
                old_index = indexi * 3 + indexj
                indexi -= 1
                new_index = indexi * 3 + indexj
                temp = tempList[old_index]
                tempList[old_index] = tempList[new_index]
                tempList[new_index] = temp
            elif k == 2:
                old_index = indexi * 3 + indexj
                indexi += 1
                new_index = indexi * 3 + indexj
                temp = tempList[old_index]
                tempList[old_index] = tempList[new_index]
                tempList[new_index] = temp
            elif k == 3:
                old_index = indexi * 3 + indexj
                indexj -= 1
                new_index = indexi * 3 + indexj
                temp = tempList[old_index]
                tempList[old_index] = tempList[new_index]
                tempList[new_index] = temp
            else:
                old_index = indexi * 3 + indexj
                indexj += 1
                new_index = indexi * 3 + indexj
                temp = tempList[old_index]
                tempList[old_index] = tempList[new_index]
                tempList[new_index] = temp
        self.initList = tempList[:]
        for j in range(3):
            for i in range(3):
                self.gridEntry[j][i].setText(str(tempList[j*3 + i]))
        self.Astar_h1 = Astar.Astar(self.initList, self.goal, 1)
        self.Astar_h2 = Astar.Astar(self.initList, self.goal, 2)
        self.G1 = nx.Graph()
        self.G2 = nx.Graph()
        self.G1.add_node(self.list_2_grid(self.initList))  # 从v中添加结点，相当于顶点编号为1到8
        self.G2.add_node(self.list_2_grid(self.initList))  # 从v中添加结点，相当于顶点编号为1到8
        self.show_h1()
        self.show_h2()

    # 开始按钮事件
    def start(self):
        self.on = 1

    # 总更新步骤，调用h1、h2更新步骤
    def update(self):
        # 没开始就返回
        if self.on == 0:
            return

        # 调用两个各自的刷新
        if(self.Astar_h1.fail != True and self.Astar_h1.success!= True):
            self.update_h1()
            self.show_h1()
        if(self.Astar_h2.fail != True and self.Astar_h2.success!= True):
            self.update_h2()
            self.show_h2()

        # 终止结果输出
        if (self.Astar_h1.fail == True):
            self.text_h1.append("This puzzle is unsolvable!")
        if (self.Astar_h2.fail == True):
            self.text_h2.append("This puzzle is unsolvable!")
        if (self.Astar_h1.success == True):
            self.text_h1.append("Success!")
            path,n = self.Astar_h1.get_best_path()
            for i in path:
                nodestr = self.list_2_grid(i)
                self.text_h1.append(nodestr + "\n")
            self.text_h1.append("最短路径长："+str(n))
        if (self.Astar_h2.success == True):
            self.text_h2.append("Success!")
            path,n = self.Astar_h2.get_best_path()
            for i in path:
                nodestr = self.list_2_grid(i)
                self.text_h2.append(nodestr + "\n")
            self.text_h2.append("最短路径长："+str(n))

        # 终止停止
        if((self.Astar_h1.fail == True or self.Astar_h1.success == True) and (self.Astar_h2.fail == True or self.Astar_h2.success== True)):
            self.on = 0
        else:
            # 否则步数加一
            self.on+=1

    # h1更新步骤
    def update_h1(self):
        # 调用类的刷新函数，返回新增结点列表和边列表
        add_nodes, add_edges = self.Astar_h1.update()

        # 加入新点
        for i in add_nodes:
            tmp_list = self.cantor_decode(i)
            self.G1.add_node(self.list_2_grid(tmp_list))

        # 加入新边
        for (i, j) in add_edges:
            self.G1.add_edge(self.list_2_grid(self.cantor_decode(i)), self.list_2_grid(self.cantor_decode(j)))

        # 更新画布
        self.canvas_h1.update_figure(self.G1,self.list_2_grid(self.initList))

    # h2更新步骤
    def update_h2(self):
        # 同h1
        add_nodes, add_edges = self.Astar_h2.update()
        for i in add_nodes:
            tmp_list = self.cantor_decode(i)
            self.G2.add_node(self.list_2_grid(tmp_list))
        for (i, j) in add_edges:
            self.G2.add_edge(self.list_2_grid(self.cantor_decode(i)), self.list_2_grid(self.cantor_decode(j)))
        self.canvas_h2.update_figure(self.G2,self.list_2_grid(self.initList))

    #   显示h1的文字信息
    def show_h1(self):
        self.canvas_h1.update_figure(self.G1,self.list_2_grid(self.initList))
        index = self.Astar_h1.open[0]
        for i in self.Astar_h1.open:
            if i.f < index.f:
                index = i
        nodestr = self.list_2_grid(self.cantor_decode(index.cantor))
        expandstr = str(self.Astar_h1.close_count + len(self.Astar_h1.open))
        self.text_h1.append(nodestr + "\t" + str(self.on) + "\t" + expandstr+ "\t" + str(len(self.Astar_h1.open)) + "\t" + str(index.h) + "\t" + str(index.f) + "\n")
        self.resultEntry[1][1].setText(str(self.on))
        self.resultEntry[2][1].setText(expandstr)

    #   显示h2的文字信息
    def show_h2(self):
        self.canvas_h2.update_figure(self.G2,self.list_2_grid(self.initList))
        index = self.Astar_h2.open[0]
        for i in self.Astar_h2.open:
            if i.f < index.f:
                index = i
        nodestr = self.list_2_grid(self.cantor_decode(index.cantor))
        expandstr = str(self.Astar_h2.close_count + len(self.Astar_h2.open))
        self.text_h2.append(nodestr + "\t" + str(self.on) + "\t" + expandstr + "\t" + str(len(self.Astar_h2.open)) + "\t" + str(index.h) + "\t" + str(index.f) + "\n")
        self.resultEntry[1][2].setText(str(self.on))
        self.resultEntry[2][2].setText(expandstr)

    # 列表转换成图结点的矩阵字符串
    def list_2_grid(self,_list):
        tmp_list = _list[:]
        sl = [str(i) for i in tmp_list]
        sl = ''.join(sl)
        sl = sl[:3] + '\n' + sl[3:]
        sl = sl[:7] + '\n' + sl[7:]
        return sl

    # 康拓解码
    def cantor_decode(self,cantor):
        tmp_list = []
        take_list = [i for i in range(9)]
        remain = cantor
        for i in range(9):
            _fac = fac[8 - i]
            n = remain // _fac
            remain = remain % _fac
            tmp_list.append(take_list[n])
            take_list.remove(take_list[n])
        return tmp_list

if __name__ == '__main__':
    app = QApplication(sys.argv)
    astart = ApplicationWindow()
    astart.setWindowTitle("A* Algorithm")
    astart.show()
    app.exec_()

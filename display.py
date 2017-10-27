import sys
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx                   #导入NetworkX包，为了少打几个字母，将其重命名为nx
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

#matplotlib.use("Qt5Agg") # 声明使用QT5

fac = tuple([math.factorial(i) for i in range(10)])

class MyCanvas(QWidget):
    def __init__(self, canvas_no, parent=None):
        super(MyCanvas, self).__init__(parent)
        self.canvas_no = canvas_no
        # 绘制网络图G，带标签，           用指定颜色给结点上色

        self.figure1 = plt.figure(canvas_no)  # 返回当前的figure
        self.canvas1 = FigureCanvas(self.figure1)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.canvas1)

    def update_figure(self, G):
        self.figure1 = plt.figure(self.canvas_no)  # 返回当前的figure
        plt.clf()
        pos = nx.spring_layout(G)
        nx.draw(G,pos,with_labels =True,font_size=5,node_size=100,width=0.5,alpha = 0.5,node_shape='s')
        self.canvas1.draw()

class ApplicationWindow(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
       # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)while
        self.on = 0
        self.LayoutInit()
        self.initList = [0,1,2,3,4,5,6,7,8]
        self.goal = [0,1,2,3,4,5,6,7,8]
        self.Astar_h1 = Astar.Astar(self.initList, self.goal, 1)
        self.Astar_h2 = Astar.Astar(self.initList, self.goal, 2)
        self.G1 = nx.Graph()
        self.G2 = nx.Graph()
        self.G1.add_node(self.list_2_grid(self.initList))  # 从v中添加结点，相当于顶点编号为1到8
        self.G2.add_node(self.list_2_grid(self.initList))  # 从v中添加结点，相当于顶点编号为1到8
        self.showState()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(100)

    # 布局设置
    def LayoutInit(self):
        # h1的标题、图、步骤
        self.label_h1 = QLabel("h1:",self)
        self.canvas_h1 = MyCanvas(1, self)
        self.attrib_h1 = QLabel("\t步数\t总拓展数\tOPEN表结点数\th（n）\tf（n）",self)
        self.text_h1 = QTextEdit(self)

        # h2的标题、图、步骤
        self.label_h2 = QLabel("h2:",self)
        self.canvas_h2 = MyCanvas(2, self)
        self.attrib_h2 = QLabel("\t步数\t总拓展数\tOPEN表结点数\th（n）\tf（n）",self)
        self.text_h2= QTextEdit(self)

        # 九宫格
        self.gridEntry = [[QLabel(self) for i in range(3)] for j in range(3)]
        self.gridRow = [QHBoxLayout() for i in range(3)]
        self.grid = QVBoxLayout()
        pe = QPalette()
        pe.setColor(QPalette.Background,Qt.white)       # 设置背景颜色，和上面一行的效果一样
        for j in range(3):
            for i in range(3):
                self.gridEntry[j][i].setAutoFillBackground(True)
                self.gridEntry[j][i].setPalette(pe)
                self.gridEntry[j][i].setText(str(j*3 + i))
                self.gridEntry[j][i].setFixedWidth(40)
                self.gridEntry[j][i].setFixedHeight(40)
                self.gridEntry[j][i].setFont(QFont("Roman times",20,QFont.Bold))
                self.gridRow[j].addWidget(self.gridEntry[j][i])
            self.grid.addLayout(self.gridRow[j])

        # 随机生成按钮
        self.randomButton = QPushButton("随机生成")
        self.randomButton.clicked.connect(self.randomGenerate)

        # 开始
        self.startButton = QPushButton("开始")
        self.startButton.clicked.connect(self.start)

        #结果显示
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

        # 加入框架
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

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.column1)
        self.mainLayout.addLayout(self.column2)
        self.mainLayout.addLayout(self.column3)

        self.setLayout(self.mainLayout)

    # 随机生成按钮
    def randomGenerate(self):
        indexi = 0
        indexj = 0
        tempList = [i for i in range(9)]
        for k in range(15):
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
        self.showState()

    # 开始按钮
    def start(self):
        self.on = 1

    def update(self):
        if(self.Astar_h1.fail != True and self.Astar_h1.success!= True):
            self.update_h1()
        if(self.Astar_h2.fail != True and self.Astar_h2.success!= True):
            self.update_h2()
        if((self.Astar_h1.fail != True and self.Astar_h1.success!= True) == False and (self.Astar_h2.fail != True and self.Astar_h2.success!= True) == False):
            self.on = 0

    def update_h1(self):
        if self.on == 0:
            return
        add_nodes, add_edges = self.Astar_h1.update()
        for i in add_nodes:
            tmp_list = self.cantor_decode(i)
            self.G1.add_node(self.list_2_grid(tmp_list))
        for (i, j) in add_edges:
            self.G1.add_edge(self.list_2_grid(self.cantor_decode(i)), self.list_2_grid(self.cantor_decode(j)))
        self.canvas_h1.update_figure(self.G1)

    def update_h2(self):
        if self.on == 0:
            return
        add_nodes, add_edges = self.Astar_h2.update()
        for i in add_nodes:
            tmp_list = self.cantor_decode(i)
            self.G2.add_node(self.list_2_grid(tmp_list))
        for (i, j) in add_edges:
            self.G2.add_edge(self.list_2_grid(self.cantor_decode(i)), self.list_2_grid(self.cantor_decode(j)))
        self.canvas_h2.update_figure(self.G2)

    # 显示状态
    def showState(self):
        self.canvas_h1.update_figure(self.G1)
        self.canvas_h2.update_figure(self.G2)
     #   self.text_h1.append()

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

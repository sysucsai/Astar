import math
import heapq

fac = tuple([math.factorial(i) for i in range(10)])


class State:
	def __init__(self, initial, g, h_mode, goal, dis_map):
		#使用当前搜索深度作为g(n)
		self.g = g
		self.child = []
		self.father = self

		#使用放错位置的数字的个数作为h1*
		#使用每个数字距离目标位置的距离作为h2*
		if h_mode == 1:
			self.h = sum([(1 if initial[i]!=goal[i] and initial[i]!=0 else 0) for i in range(9)])
		else :
			self.h = sum([dis_map[i][initial[i]] if initial[i] != 0 else 0 for i in range(9)])

		#计算f
		self.f = self.g + self.h

		#使用康托展开进行状态压缩
		self.cantor = 0
		for i in range(9):
			bigger_than = 0
			for j in range(i+1,9):
				if initial[i] > initial[j]:
					bigger_than += 1
			self.cantor += bigger_than * fac[8-i]

	def get_graph(self):
		valid = [i for i in range(9)]
		graph = []
		for i in range(8, -1, -1):
			p = int(self.cantor%fac[i+1]/fac[i])
			graph.append(valid[p])
			del valid[p]
		return graph

	def relax(self, father, astar):
		if self.father == father:
			self.g = father.g+1
			self.f = self.g + self.h
			astar.open_count += 1
			heapq.heappush(astar.open, (self.f * 100 + self.g + astar.open_count * 0.000001, self))
			for i in self.child:
				i.relax(self)
		else:
			if self.father != self:
				self.father.child.remove(self)
			self.father = father
			self.g = father.g + 1
			self.f = self.g + self.h
			father.child.append(self)
			for i in self.child:
				i.relax(self)


class flag:
	def __init__(self):
		self.flag = False

	def set_true(self, state):
		self.flag = True
		self.pointer = state

	def is_true(self):
		return self.flag


class Astar:
	def __init__(self, initial, goal, h_mode):
		'''构造函数
		参数1：初始状态list(int)
		参数2：目标状态list(int)
		参数3：估价函数，h_mode = 1 或 2'''
		self.goal = goal
		self.h_mode = h_mode
		self.fail = True
		if self.if_possible(initial, goal):
			self.fail = False
		self.success = False
		self.close_count = 0
		self.open_count = 1

		#dis_map[i][j]表示第i个位置上，如果是数字j数字，则距离initial[i]的距离，用于计算h2
		self.dis_map = []
		if h_mode == 2:
			self.dis_map_init(goal)

		self.initial = State(initial, 0, h_mode, goal, self.dis_map)
		self.open = [(self.initial.f*100+self.initial.g+self.open_count*0.000001, self.initial)]
		self.close = []
		self.hash = tuple([flag() for i in range(fac[9])])
		self.hash[self.initial.cantor].set_true(self.initial)
		self.goal_cantor = State(goal, 0, 1, goal, self.dis_map).cantor

	def if_possible(self, initial, goal):
		tmp_sum_a = 0
		tmp_sum_b = 0
		tmp_a = initial
		tmp_b = goal
		tmp_possible = 0
		tmp_count = 0
		'''print(tmp_a)
		print(tmp_b)'''
		for i in range(9):
			for j in range(i+1,9):
				tmp_count += 1
				'''print("step %d:"%(tmp_count))
				print("a[i] = %d, a[j] = %d"%(tmp_a[i], tmp_a[j]))
				print("b[i] = %d, b[j] = %d"%(tmp_b[i], tmp_b[j]))'''
				if tmp_a[i] > tmp_a[j] and tmp_a[j] != 0:
					tmp_sum_a += 1
				if tmp_b[i] > tmp_b[j] and tmp_b[j] != 0:
					tmp_sum_b += 1
				'''print("step %d: m = %d, n = %d"%(tmp_count, tmp_sum_a, tmp_sum_b))'''
		if (tmp_sum_a % 2) == (tmp_sum_b % 2):
			tmp_possible = True
		return tmp_possible

	def dis_map_init(self, goal):
		for i in range(9):
			self.dis_map.append([])
			for j in range(9):
				for k in range(9):
					if goal[k] == j:
						self.dis_map[i].append(abs(int(i/3)-int(k/3)) + abs(i%3-k%3))
						break
			self.dis_map[i] = tuple(self.dis_map[i])
		self.dis_map = tuple(self.dis_map)

	def update(self):
		'''执行一次迭代，返回新增的点和边'''
		self.close_count += 1
		#now = self.open.pop(0)
		while True:
			record_fg, now = heapq.heappop(self.open)
			if math.floor(record_fg) == now.f*100+now.g:
				break
		now_graph = now.get_graph()
		for i in range(9):
			if now_graph[i] == 0:
				p = i
				break
		move = (-3, -1, 1, 3)
		add_nodes = []
		add_edges = []
		for i in range(4):
			if 0<=p+move[i] and p+move[i] <=8:
				if p%3 == 2 and move[i] == 1:
					continue
				if p%3 == 0 and move[i] == -1:
					continue
				now_graph[p] = now_graph[p+move[i]]
				now_graph[p + move[i]] = 0
				new = State(now_graph, now.g+1, self.h_mode, self.goal, self.dis_map)
				if self.hash[new.cantor].is_true():
					#如果要添加的点已经拓展过
					pre = self.hash[new.cantor].pointer
					if pre.g > new.g:
						pre.relax(now, self)
						self.open_count += 1
						heapq.heappush(self.open, (new.f * 100 + new.g + self.open_count * 0.000001, new))
						add_edges.append((now.cantor, new.cantor))
				else:
					#如果要添加的点未拓展过
					self.hash[new.cantor].set_true(new)
					new.relax(now, self)
					add_nodes.append(new.cantor)
					add_edges.append((now.cantor, new.cantor))
					#self.open.append(new)
					self.open_count += 1
					heapq.heappush(self.open, (new.f*100+new.g+self.open_count*0.000001, new))
				if new.cantor == self.goal_cantor:
					self.success = True
					return add_nodes, add_edges
				now_graph[p + move[i]] = now_graph[p]
				now_graph[p] = 0
		#如果Open表为空则搜索结束，标记fail为True
		if len(self.open) == 0:
			self.fail = True
		return add_nodes, add_edges

	def get_best_path(self):
		'''获取最优路径和长度
		返回值1：list[list[9]]最优路径
		返回值2：最优路径长度
		注意返回值1的list的元素数量=返回值2 + 1'''
		best_path = []
		now = self.hash[self.goal_cantor].pointer
		while now != self.initial:
			#print(now.get_graph())
			best_path.insert(0, now.get_graph())
			now = now.father
		best_path.insert(0, now.get_graph())
		return best_path, len(best_path)-1


if __name__ == "__main__":
	goal = [0,5,2,
			1,4,3,
			8,7,6]
	initial = [3,6,8,
			   0,1,2,
			   4,5,7]
	h1 = Astar(initial, goal, 2)
	while h1.fail == False and h1.success == False:
		add_nodes, add_edges = h1.update()
		'''print(add_nodes)
		print(add_edges)'''
	if h1.success == True:
		print("Find!")
		best_path , best_path_step= h1.get_best_path()
		for i in best_path:
			print(i[0:3])
			print(i[3:6])
			print(i[6:9])
			print()
		print("Best path step :", best_path_step)
	else:
		print("Not find")
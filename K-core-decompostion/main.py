import math
import random
import numpy
import queue
import time

epsilon = 0.5   # 控制环的厚度
delta = 50       # 同一个壳不同组件之间的距离
gamma = 50     # 控制组件的直径
belta = 50       # 控制核的直径

kk = 0          # 最大的k-core值

graph = []
class node:
    def __init__(self, _degree=-1, _core=0, _cluster=-1):
        self.degree = _degree
        self.k = -1
        self.core = _core
        self.cluster = _cluster
        self.x = 0
        self.y = 0
class shell:
    def __init__(self):
        self.shellNode = []
        self.clusterList = []
        self.size = 0

    def deal(self):
        self.size = len(self.shellNode)
        def dfs(u):
            data[u].cluster = len(self.clusterList) - 1
            self.clusterList[-1] += 1
            for v in graph[u]:
                if v in self.shellNode and data[v].cluster == -1:
                    dfs(v)
        def bfs(i):
            q = queue.Queue()
            q.put(i)
            data[i].cluster = len(self.clusterList) - 1
            self.clusterList[-1] += 1
            while not q.empty():
                u = q.get()
                for v in graph[u]:
                    if v in self.shellNode and data[v].cluster == -1:
                        q.put(v)
                        data[v].cluster = len(self.clusterList) - 1
                        self.clusterList[-1] += 1

        for i in self.shellNode:
            if data[i].cluster == -1:  # 未访问该节点
                self.clusterList.append(0)
                bfs(i)
class core:
    def __init__(self, _parent, _k = 0):
        self.parent = _parent
        self.coreNode = []
        self.shell = shell()
        self.size = 0
        self.sonSize = 0
        self.X = 0
        self.Y = 0
        self.unit = 1
        self.phi = random.uniform(0, 2 * math.pi)
        self.k = _k
        self.son = []
cores = []
curCores = []
def core_decomposition():
    bin = [[] for i in range(maxDegree + 1)]
    n = len(data)
    for i in range(1, n):
        bin[data[i].degree].append(i)
    vis = [False] * n
    for k in range(maxDegree + 1):
        curShell = []
        for u in bin[k]:
            if vis[u]:
                continue
            vis[u] = True
            data[u].k = data[u].degree
            global kk
            if data[u].k > kk:
                kk = data[u].k
            curShell.append(u)
            for v in graph[u]:
                if vis[v]:
                    continue
                if data[v].degree > k:
                    data[v].degree = data[v].degree - 1
                    bin[data[v].degree].append(v)
        global curCores
        tmpCores = curCores[:]
        for i in range(len(curCores)):
            idx = curCores[i]
            cores[idx].shell.shellNode = list(set(cores[idx].coreNode) & set(curShell))
            cores[idx].shell.deal();
            # cores.append(core(len(cores), list( set(cores[idx].coreNode) - set(cores[idx].shell.shellNode) ) ))
            # curCores[i] = len(cores) - 1
            tmpNode = list(set(cores[idx].coreNode) - set(cores[idx].shell.shellNode))
            cores[idx].sonSize = len(tmpNode)
            if len(tmpNode) == 0:  # 没有剩下节点
                tmpCores[i] = -1  # 删除这个核
                continue
            # 将剩下的节点分成不同的核
            tail = len(cores)  # 从尾部开始

            def dfs(u):
                data[u].core = len(cores) - 1
                cores[-1].coreNode.append(u)
                for v in graph[u]:
                    if v in tmpNode and data[v].core == idx:
                        dfs(v)
            def bfs(i):
                q = queue.Queue()
                q.put(i)
                data[i].core = len(cores) - 1
                cores[-1].coreNode.append(i)
                while not q.empty():
                    u = q.get()
                    for v in graph[u]:
                        if v in tmpNode and data[v].core == idx:
                            q.put(v)
                            data[v].core = len(cores) - 1
                            cores[-1].coreNode.append(v)


            for u in tmpNode:
                if (data[u].core == idx):
                    cores.append(core(idx, k))
                    bfs(u)
                    cores[-1].size = len(cores[-1].coreNode)
            tmpCores[i] = list(range(tail, len(cores)))  # 从tail到cores末尾都是新加入的核，用来替换原来的核
            cores[idx].son = tmpCores[i]
        # 此时的tmpCores保存了最新的核，把tmpCores展开
        curCores = []
        for item in tmpCores:
            if item == -1:
                continue
            for i in item:
                curCores.append(i)
            continue

def extend(x):
    if x >= len(graph):
        while len(graph) <= x :
            graph.append([])

def deal_data():
    # 处理每个核core的坐标
    for i in range(1, len(cores)):
        C = cores[i]
        parent = cores[C.parent]
        C.unit = parent.unit * C.size / parent.sonSize
        sonList = parent.son
        sumSize = 0
        for j in sonList:
            if j > i:
                break
            sumSize += cores[j].size
        phi = parent.phi + 2 * math.pi * sumSize / parent.sonSize
        rho = 1 - C.size / parent.sonSize
        C.X = parent.X + delta * (kk - C.k) * parent.unit * rho * math.cos(phi)
        C.Y = parent.Y + delta * (kk - C.k) * parent.unit * rho * math.sin(phi)
    for i in range(1, len(data)):
        u = data[i]
        if u.k == kk:
            u.x = random.uniform(-belta, belta)
            u.y = random.uniform(-belta, belta)
            continue
        a = 0
        b = 0
        for j in graph[i]:
            v = data[j]
            if v.k >= u.k:
                a += kk - v.k
                b += 1
        rho = (1 - epsilon)*(kk - u.k)
        if b > 0:
            rho += epsilon * a / b
        curShell = cores[u.core].shell
        clusterList = curShell.clusterList
        c = 0
        for ii in range(u.cluster):
            # print(i, u.core, u.cluster,  ii, clusterList, sep=' ')
            c += clusterList[ii]
        d = clusterList[u.cluster] / curShell.size
        alpha = 2 * math.pi * c / curShell.size + numpy.random.normal(d/2, math.sqrt(math.pi * d))
        u.x = cores[u.core].X + gamma * cores[u.core].unit * rho * math.cos(alpha)
        u.y = cores[u.core].Y + gamma * cores[u.core].unit * rho * math.sin(alpha)
        # if u.k == 2 and math.fabs(u.x) < 10 and math.fabs(u.y) < 10:
        #     print(rho,gamma, cores[u.core].unit,sep=' ')


# 程序入口
# 读入文件
time_start = time.time()
with open('bio-CE-GT.edges', 'r') as fp, open('input.csv', 'w') as wp:
    wp.write('source,target,\n')
    for line in fp:
        tmp = list(line.split())
        u = int(tmp[0]) + 1
        v = int(tmp[1]) + 1
        extend(max(u, v))
        if u == v:
            print(u,v,sep=' ')
            continue;
        graph[u].append(v)
        graph[v].append(u)
        wp.write('%d,%d,\n'%(u,v))

# 处理数据
data = [node(len(graph[i])) for i in range(len(graph))]
def getValue(d):
    return d.degree
maxDegree = max(data,key = getValue).degree
# print(maxDegree)
cores.append(core(-1, -1, ))
cores[0].coreNode = [i for i in range(1, len(data))]
cores[0].size = len(cores[0].coreNode)
curCores.append(0)
core_decomposition()
deal_data()
for i in range(1, len(data)):
    n = data[i]
    # print("%d : k=%d core=%d cluster=%d degree=%d x=%f y=%f"%(i, n.k, n.core, n.cluster, n.degree, n.x, n.y))

print("输出文件")
with open('ouput.csv', 'w') as fp:
    print("打开output")
    fp.write("id,x,y,k,\n")
    for i in range(1, len(data)):
        n = data[i]
        if n.k == 0:
            print('%d: x=%f\ty=%f' % (i,n.x,n.y))
        fp.write("%d,%f,%f,%d,\n"%(i,n.x,n.y,n.k))

time_end = time.time()
print('time cost s',time_end-time_start,'s')

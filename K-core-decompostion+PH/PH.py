from time import time
from numba import jit
import numpy as np

def PH():
    # 数据定义
    MAXN = 924
    INF = 1e6
    d = [[INF]*MAXN for i in range(MAXN)]
    d = np.array(d)
    for i in range(MAXN):
        d[i][i] = 0.0
    class edge:
        def __init__(self, u, v, w):
            self.u = u
            self.v = v
            self.w = w
            self.ratio = 0
    edges = []
    maxNode = 0
    # 打开文件
    with open('test_data.edges', 'r') as fp:
        for line in fp:
            tmp = list(line.split())
            u = int(tmp[0])
            v = int(tmp[1])
            if u > maxNode:
                maxNode = u
            if v > maxNode:
                maxNode = v
            w = float(tmp[2])
            if u == v:
                continue
            d[u][v] = 100.0/w
            d[v][u] = 100.0/w

    # 初始化graph
    maxNode += 1
    graph = [[] for i in range(maxNode)]

    @jit(nopython=True)
    def calute(d, MAXN):
        for k in range(MAXN):
            for i in range(MAXN):
                for j in range(MAXN):
                    d[i][j] = min(d[i][j], d[i][k] + d[k][j])

    # Floyd处理出最短路径
    start = time()
    calute(d, MAXN)
    end = time()
    print(end-start)

    # 将邻接矩阵转的边记录
    for i in range(MAXN):
        for j in range(i):
            if(d[i][j] != INF):     # 是有效边
                edges.append(edge(i, j, d[i][j]))

    # Kruskal算法
    ph = []
    # 排序
    edges.sort(key=lambda e:e.w)
    n = len(edges)
    father = [i for i in range(MAXN)]     # 并查集
    def find(x):
        y = x
        while(father[y] != y):
            y = father[y]
        while(father[x] != y):
            t = father[x]
            father[x] = y
            x = t
        return y

    def merge(u, v):
        rootU = find(u)
        rootV = find(v)
        father[rootU] = rootV

    for e in edges:
        if find(e.u) != find(e.v):
            merge(e.u, e.v)
            ph.append(edge(e.u, e.v, 100/e.w))

    # calculate subset ratio
    for i in range(len(ph)):
        e = ph[i]
        u = e.u
        v = e.v
        graph[u].append((v, i))
        graph[v].append((u, i))
    sz = [0] * maxNode
    def dfs(u, father):
        sz[u] = 1
        for item in graph[u]:
            v = item[0]
            if v == father:
                continue
            dfs(v, u)
            sz[u] += sz[v]
    def dfs2(u, father):
        for item in graph[u]:
            v = item[0]
            if v == father:
                continue
            idx = item[1]
            # 转移根节点
            sz[u] -= sz[v]
            ph[idx].ratio = sz[u]/sz[v]
            if ph[idx].ratio > 1:
                ph[idx].u, ph[idx].v = ph[idx].v, ph[idx].u
                ph[idx].ratio = 1/ph[idx].ratio
            sz[v] += sz[u]

            dfs2(v, u)

            sz[v] -= sz[u]
            sz[u] += sz[v]
    # 第一遍dfs
    dfs(0, -1)
    # dp
    dfs2(0, -1)

    print(ph)
    ph.sort(key=lambda e: e.w + e.ratio ,reverse=False)

    # 输出到ph.csv
    with open("ph.csv", "w") as fp:
        fp.write('id,source,target,ph,ratio,\n')
        for i in range(len(ph)):
            e = ph[i]
            fp.write('%d,%d,%d,%f,%f,\n'%(i,e.u+1, e.v+1, e.w, e.ratio))
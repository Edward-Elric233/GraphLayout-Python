# 数据定义
MAXN = 924
INF = 1e6
d = [[INF]*MAXN for i in range(MAXN)]
for i in range(MAXN):
    d[i][i] = 0.0
class edge:
    def __init__(self, u, v, w):
        self.u = u
        self.v = v
        self.w = w
edges = []
# 打开文件
with open('bio-CE-GT.edges', 'r') as fp:
    for line in fp:
        tmp = list(line.split())
        u = int(tmp[0])
        v = int(tmp[1])
        w = 100.0 / float(tmp[2])
        if u == v:
            continue
        d[u][v] = w
        d[v][u] = w

# Floyd处理出最短路径
for k in range(MAXN):
    for i in range(MAXN):
        for j in range(MAXN):
            d[i][j] = min(d[i][j], d[i][k] + d[k][j])

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
        ph.append(e)

# 输出到ph.csv
with open("ph.csv", "w") as fp:
    fp.write('source,target,\n')
    for e in ph:
        fp.write('%d,%d,%f,\n'%(e.u+1, e.v+1, e.w))
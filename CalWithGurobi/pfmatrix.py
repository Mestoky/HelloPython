from numpy import *


class PfMatrix:
    '''输入网络导纳列表bs，以4节点为例，格式为[b12,b13,b14,b23,b24,b34]. n为节点个数'''
    def __init__(self, bs, n):
        self.bs = bs
        self.n = n
        self.bnmat = None
        self.bmat = None
        self.invbmatn = None
        self.amat = None
        self.blmat = None
        self.mats = None

    # 全节点导纳矩阵
    def get_bnmat(self):
        bn = mat(zeros([self.n, self.n]))
        tempbs = self.bs
        for row in range(self.n):
            for column in range(self.n):
                if column < row:
                    bn[row, column] = bn[column, row]
                elif column > row:
                    bn[row, column] = tempbs.pop(0)
            else:
                bn[row, row] = -sum(bn.tolist()[row])
        return mat(bn)

    # 导纳矩阵（最后一个节点选为平衡节点，theta=0）
    def get_bmat(self):
        bn = self.get_bnmat()
        b = bn[arange(self.n - 1)][:, arange(self.n - 1)]
        return b

    # 导纳矩阵逆矩阵，添加最后一行0
    def get_invbmatn(self):
        b = self.get_bmat()
        return vstack((b.I, zeros([1, self.n - 1])))

    # 节点关联矩阵（只和节点个数有关）
    def get_amat(self):
        a = list()
        for i in range(self.n - 1):
            a.append([0] * self.n)
            for j in range(i + 1, self.n - 1):
                a[-1][i] = 1
                a[-1][j] = -1
                a.append([0] * self.n)
            else:
                a[-1][i] = 1
                a[-1][self.n - 1] = -1
        return mat(a)

    # 线路导纳矩阵
    def get_blmat(self):
        return mat(diag(self.bs))

    # 三个矩阵乘积
    def get_mats(self):
        return self.get_blmat() * self.get_amat() * self.get_invbmatn()


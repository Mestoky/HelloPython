import cvxpy as cvx
import numpy as np
import matplotlib.pyplot as plt


class ProSimu:
    def __init__(self, name=None):
        self.name = name
        self.prob = None
        self.sense = 'minimize'
        self.constraints = list()
        self.totalcost = 0
        self.units = list()  # Units
        self.pload = list()  # Power Load
        self.hload = list()  # Heat Load
        self.pfmat = None  # Power Flow Matrix
        self.pfbound = list()  # Power Flow Upbound
        self.plot = None  # Plot Or Not
        self.wpunits = list()  # Wind Power Units
        self.pcunits = list()  # Pure Condensing Units
        self.chpunits = list()  # CHP Units
        self.T = 0  # Time Scale
        self.TEG = 0  # Total Electric Generation
        self.TTG = 0  # Total Thermal Generation

    # Build the Model
    def build(self):
        self.T = len(self.pload)
        for unit in self.units:
            if unit.ptype == 0:
                self.wind_unit(unit)
            elif unit.ptype == 1:
                self.pc_unit(unit)
            else:
                if unit.rtype == 0:  # 不改造，五段抽汽供热
                    self.chp_unit0(unit)
                elif unit.rtype == 1:  # 切低压缸运行
                    self.chp_unit1(unit)
                elif unit.rtype == 2:  # 低压旁路
                    self.chp_unit2(unit)
                elif unit.rtype == 3:  # 高、低压旁路
                    self.chp_unit3(unit)
                elif unit.rtype == 4:  # 储热
                    self.chp_unit4(unit)
        self.constraints += [self.TEG == self.pload]
        self.constraints += [self.TTG == self.hload]

    # Solve the Model
    def solve(self, flag=1):
        self.build()
        try:
            if self.sense == 'minimize':
                self.prob = cvx.Problem(cvx.Minimize(self.totalcost), self.constraints)
            else:
                self.prob = cvx.Problem(cvx.Maximize(self.totalcost), self.constraints)
            self.prob.solve()  # Returns the optimal value.
            if flag:
                print("Status:", self.prob.status)
                print("Optimal value:", self.prob.value)
            if self.plot:
                self.plot_result()
        except ValueError as error:
            print(error)

    def getoptvalue(self):
        self.solve(flag=0)
        return self.prob.value if self.prob.status == 'optimal' else 10.0**4*sum(self.hload+self.pload)

    # Wind Power Unit
    def wind_unit(self, unit):
        self.wpunits.append(unit)
        unit.pschedule = cvx.Variable(self.T)
        self.TEG += unit.pschedule
        self.constraints += [unit.pschedule >= 0,
                             unit.pschedule <= np.array([unit.maxwp]).T]

    # Pure Condensing Unit
    def pc_unit(self, unit):
        self.pcunits.append(unit)
        unit.isopen = cvx.Bool()
        unit.mmain = cvx.Variable(self.T)
        unit.pschedule = cvx.Variable(self.T)
        unit.cost = sum(map(unit.costfun, unit.mmain))
        self.TEG += unit.pschedule
        self.totalcost += unit.cost
        self.constraints += [unit.mmain == unit.pschedule / 2.8]
        self.constraints += [unit.pschedule >= unit.pbound[0] * unit.isopen,
                             unit.pschedule <= unit.pbound[1] * unit.isopen]

    # CHP Unit 不改造，五段抽汽供热
    def chp_unit0(self, unit):
        self.chpunits.append(unit)
        unit.isopen = cvx.Bool()
        unit.mmain = cvx.Variable(self.T)
        unit.p1 = cvx.Variable(self.T)
        unit.p2 = cvx.Variable(self.T)
        unit.p3 = cvx.Variable(self.T)
        unit.h1 = cvx.Variable(self.T)
        unit.pschedule = unit.p1 + unit.p2 + unit.p3
        unit.hschedule = unit.h1
        unit.cost = sum(map(unit.costfun, unit.mmain))
        self.TEG += unit.pschedule
        self.TTG += unit.hschedule
        self.totalcost += unit.cost
        self.constraints += [unit.mmain == unit.p1]
        self.constraints += [unit.p1 == unit.p2]
        self.constraints += [unit.p2 == unit.p3 / 0.8 + unit.h1 / 4.66]
        self.constraints += [unit.p3 / 0.8 >= unit.p2 * 0.15]
        self.constraints += [unit.p1 >= 0]
        self.constraints += [unit.p2 >= 0]
        self.constraints += [unit.p3 >= 0]
        self.constraints += [unit.h1 >= 0]
        self.constraints += [unit.pschedule >= unit.pbound[0] * unit.isopen,
                             unit.pschedule <= unit.pbound[1] * unit.isopen]

    # CHP Unit 切低压缸运行
    def chp_unit1(self, unit):
        self.chpunits.append(unit)
        unit.isopen = cvx.Bool()
        unit.mmain = cvx.Variable(self.T)
        unit.p1 = cvx.Variable(self.T)
        unit.p2 = cvx.Variable(self.T)
        unit.h1 = cvx.Variable(self.T)
        unit.pschedule = unit.p1 + unit.p2
        unit.hschedule = unit.h1
        unit.cost = sum(map(unit.costfun, unit.mmain))
        self.TEG += unit.pschedule
        self.TTG += unit.hschedule
        self.totalcost += unit.cost
        self.constraints += [unit.mmain == unit.p1]
        self.constraints += [unit.p1 == unit.p2]
        self.constraints += [unit.p2 == unit.h1 / 4.66]
        self.constraints += [unit.p1 >= 0]
        self.constraints += [unit.p2 >= 0]
        self.constraints += [unit.h1 >= 0]
        self.constraints += [unit.pschedule >= unit.pbound[0] * unit.isopen,
                             unit.pschedule <= unit.pbound[1] * unit.isopen]

    # CHP Unit 低压旁路
    def chp_unit2(self, unit):
        self.chpunits.append(unit)
        unit.isopen = cvx.Bool()
        unit.mmain = cvx.Variable(self.T)
        unit.p1 = cvx.Variable(self.T)
        unit.p2 = cvx.Variable(self.T)
        unit.p3 = cvx.Variable(self.T)
        unit.h1 = cvx.Variable(self.T)
        unit.h2 = cvx.Variable(self.T)
        unit.pschedule = unit.p1 + unit.p2 + unit.p3
        unit.hschedule = unit.h1 + unit.h2
        unit.cost = sum(map(unit.costfun, unit.mmain))
        self.TEG += unit.pschedule
        self.TTG += unit.hschedule
        self.totalcost += unit.cost
        self.constraints += [unit.mmain == unit.p1]
        self.constraints += [unit.p1 == unit.p2 + unit.h2 / 6]
        self.constraints += [unit.p2 >= unit.p1 * 0.8]
        self.constraints += [unit.p2 == unit.p3 / 0.8 + unit.h1 / 4.66]
        self.constraints += [unit.p3 / 0.8 >= unit.mmain * 0.15]
        self.constraints += [unit.p1 >= 0]
        self.constraints += [unit.p2 >= 0]
        self.constraints += [unit.p3 >= 0]
        self.constraints += [unit.h1 >= 0]
        self.constraints += [unit.h2 >= 0]
        self.constraints += [unit.pschedule >= unit.pbound[0] * unit.isopen,
                             unit.pschedule <= unit.pbound[1] * unit.isopen]

    # CHP Unit 高、低压旁路
    def chp_unit3(self, unit):
        self.chpunits.append(unit)
        unit.isopen = cvx.Bool()
        unit.mmain = cvx.Variable(self.T)
        unit.p1 = cvx.Variable(self.T)
        unit.p2 = cvx.Variable(self.T)
        unit.p3 = cvx.Variable(self.T)
        unit.h1 = cvx.Variable(self.T)
        unit.h2 = cvx.Variable(self.T)
        unit.pschedule = unit.p1 + unit.p2 + unit.p3
        unit.hschedule = unit.h1 + unit.h2
        unit.cost = sum(map(unit.costfun, unit.mmain))
        self.TEG += unit.pschedule
        self.TTG += unit.hschedule
        self.totalcost += unit.cost
        self.constraints += [unit.p1 >= unit.mmain * 0.8, unit.p1 <= unit.mmain]
        self.constraints += [unit.mmain*1.15 - unit.p1*0.15 == unit.p2 + unit.h2 / 6]
        self.constraints += [unit.p2 >= unit.p1 * 0.8]
        self.constraints += [unit.p2 == unit.p3 / 0.8 + unit.h1 / 4.66]
        self.constraints += [unit.p3 / 0.8 >= unit.mmain * 0.15]
        self.constraints += [unit.p1 >= 0]
        self.constraints += [unit.p2 >= 0]
        self.constraints += [unit.p3 >= 0]
        self.constraints += [unit.h1 >= 0]
        self.constraints += [unit.h2 >= 0]
        self.constraints += [unit.pschedule >= unit.pbound[0] * unit.isopen,
                             unit.pschedule <= unit.pbound[1] * unit.isopen]

    # CHP Unit 储热
    def chp_unit4(self, unit):
        self.chpunits.append(unit)
        unit.isopen = cvx.Bool()
        unit.mmain = cvx.Variable(self.T)
        unit.p1 = cvx.Variable(self.T)
        unit.p2 = cvx.Variable(self.T)
        unit.p3 = cvx.Variable(self.T)
        unit.h1 = cvx.Variable(self.T)
        unit.hr = cvx.Variable(self.T)
        unit.hs = cvx.Variable(self.T)
        unit.H = cvx.Variable(self.T + 1)
        unit.h0 = unit.hr - unit.hs
        unit.pschedule = unit.p1 + unit.p2 + unit.p3
        unit.hschedule = unit.h1 + unit.hr
        unit.cost = sum(map(unit.costfun, unit.mmain))
        self.TEG += unit.pschedule
        self.TTG += unit.hschedule
        self.totalcost += unit.cost
        self.constraints += [unit.mmain == unit.p1]
        self.constraints += [unit.p1 == unit.p2]
        self.constraints += [unit.p2 == unit.p3 / 0.8 + (unit.h1 + unit.hs) / 4.66]
        self.constraints += [unit.p3 / 0.8 >= unit.p2 * 0.15]
        self.constraints += [unit.p1 >= 0]
        self.constraints += [unit.p2 >= 0]
        self.constraints += [unit.p3 >= 0]
        self.constraints += [unit.h1 >= 0]
        self.constraints += [unit.hr >= 0, unit.hr <= unit.hrmax]
        self.constraints += [unit.hs >= 0, unit.hs <= unit.hsmax]
        self.constraints += [unit.H[0] == unit.Hmax / 2, unit.H >= 0, unit.H <= unit.Hmax]
        for i in range(self.T):
            self.constraints += [unit.H[i + 1] == unit.H[i] * (1 - unit.Hloss) + (unit.hs[i] - unit.hr[i])]
        self.constraints += [unit.pschedule >= unit.pbound[0] * unit.isopen,
                             unit.pschedule <= unit.pbound[1] * unit.isopen]

    # Plot the Results
    def plot_result(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        # 负荷
        plt.figure()
        plt.plot(list(range(1, self.T + 1)), self.pload, 'cx-', label=u"电负荷曲线")
        plt.plot(list(range(1, self.T + 1)), self.hload, 'mo-', label=u"热负荷曲线")
        plt.ylabel(u"负荷曲线(MW)")
        plt.legend()
        plt.title(u"负荷曲线(MW)")
        plt.show()
        # 机组
        wp_abandon = 0
        for unit in self.wpunits:
            plt.figure()
            plt.plot(list(range(1, self.T + 1)), unit.pschedule.value, 'cx-', label=u"出力曲线")
            plt.plot(list(range(1, self.T + 1)), unit.maxwp, 'r--', label=u"最大出力曲线")
            plt.ylabel(u"出力曲线(MW)")
            plt.legend()
            plt.title(u"%s出力曲线(MW)" % unit.name)
            plt.show()
            wp_abandon += sum(np.array([unit.maxwp]).T-np.array(unit.pschedule.value))
        print('弃风量(MWh): %d' % wp_abandon)
        for unit in self.pcunits:
            plt.figure()
            plt.plot(list(range(1, self.T + 1)), unit.pschedule.value, 'cx-', label=u"电出力曲线")
            plt.plot(list(range(1, self.T + 1)), [unit.pbound[0]] * self.T, 'r--',
                     label=u"电出力下限")
            plt.ylabel(u"出力曲线(MW)")
            plt.legend()
            plt.title(u"%s出力曲线(MW)" % unit.name)
            plt.show()
        for unit in self.chpunits:
            plt.figure()
            plt.plot(list(range(1, self.T + 1)), unit.pschedule.value, 'cx-', label=u"电出力曲线")
            plt.plot(list(range(1, self.T + 1)), [unit.pbound[0]] * self.T, 'r--',
                     label=u"电出力下限")
            plt.plot(list(range(1, self.T + 1)), unit.hschedule.value, 'mo-', label=u"热出力曲线")
            plt.ylabel(u"出力曲线(MW)")
            plt.legend()
            plt.title(u"%s出力曲线(MW)" % unit.name)
            plt.show()
            if unit.rtype == 4:
                plt.figure()
                plt.plot(list(range(1, self.T + 2)), unit.H.value, 'mo-', label=u"储热量曲线")
                plt.ylabel(u"储热量曲线(MWh)")
                plt.title(u"%s储热装置运行曲线(MWh)" % unit.name)
                plt.show()


class Unit:
    def __init__(self, *, ptype, rtype=0, pbound=None, hbound=None, costfun=lambda x: 0, maxwp=None, name=None):
        # 输入参数
        self.name = name
        self.ptype = ptype  # 机组类型
        self.rtype = rtype  # 改造类型
        self.pbound = pbound  # 电出力范围
        self.hbound = hbound  # 热出力范围
        self.costfun = costfun  # 煤耗函数
        self.maxwp = maxwp  # 最大风电出力曲线
        self.hrmax = 15  # 储热装置放热速率极限
        self.hsmax = 15  # 储热装置储热速率极限
        self.Hmax = 30  # 储热装置容量
        self.Hloss = 0.003  # 储热装置热损失率（平均每小时）
        # 优化参数
        self.isopen = 1  # 是否开机
        self.cost = 0  # 机组煤耗
        self.pschedule = 0  # 发电曲线
        self.hschedule = 0  # 供热曲线
        self.mmain = 0  # 主蒸汽量
        self.p1 = 0  # 高压缸发电功率
        self.p2 = 0  # 中压缸发电功率
        self.p3 = 0  # 低压缸发电功率
        self.h1 = 0  # 五段抽汽供热功率
        self.h2 = 0  # 低压旁路供热功率
        self.hr = 0  # 储热装置供热功率
        self.hs = 0  # 储热装置储热速率
        self.h0 = 0  # 储热装置净储放热速率（放热为正，储热为负）
        self.H = 0  # 储热装置储热量







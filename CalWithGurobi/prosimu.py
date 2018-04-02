from gurobipy import *
import numpy as np
import matplotlib.pyplot as plt


def prod_simulation(plants, pload, hload, mats, pfctr, plot_result=None):
    try:
        # Create a new model
        m = Model("prod_simulation")
        # 决策变量
        wplants = list()  # 风电场列表
        chpplants = list()  # CHP电厂列表
        wpschedules = list()  # 风电出力计划列表
        pchpschedules = list()  # CHP电厂电出力计划列表
        hchpschedules = list()  # CHP电厂热出力计划列表
        isopens = list()  # CHP电厂开机计划列表
        for plant in plants:
            if plant.ptype == 0:
                wplants.append(plant)
                wpschedules.append(list(m.addVars(list(range(len(pload))), vtype=GRB.CONTINUOUS,
                                                  name='%s:wp-schedule' % plant.name).values()))
            elif plant.ptype == 1:
                chpplants.append(plant)
                pchpschedules.append(list(m.addVars(list(range(len(pload))), vtype=GRB.CONTINUOUS,
                                                    name='%s:e-schedule' % plant.name).values()))
                hchpschedules.append(list(m.addVars(list(range(len(hload))), vtype=GRB.CONTINUOUS,
                                                    name='%s:h-schedule' % plant.name).values()))
                isopens.append(m.addVar(vtype=GRB.BINARY, name='%s:isopen' % plant.name))
        m.update()
        # 约束
        # 风电出力约束
        bigm = 10**4
        for plant, wpschedule in zip(wplants, wpschedules):
            m.addConstrs((wpschedule[i] <= plant.maxwp[i] for i in range(len(pload))),
                         name='%s:wp-u-cstr' % plant.name)
            m.addConstrs((wpschedule[i] >= 0 for i in range(len(pload))),
                         name='%s:wp-d-cstr' % plant.name)
        # CHP出力约束
        for plant, pchpschedule, hchpschedule, isopen in zip(chpplants, pchpschedules, hchpschedules, isopens):
            m.addConstrs((pchpschedule[i] <= isopen * bigm for i in range(len(pload))),
                         name='%s:e-chp-u-cstr1' % plant.name)
            m.addConstrs((pchpschedule[i] >= 0 for i in range(len(pload))),
                         name='%s:e-chp-d-cstr1' % plant.name)
            m.addConstrs((hchpschedule[i] <= isopen * bigm for i in range(len(pload))),
                         name='%s:h-chp-u-cstr1' % plant.name)
            m.addConstrs((hchpschedule[i] >= 0 for i in range(len(pload))),
                         name='%s:h-chp-d-cstr1' % plant.name)
            m.addConstrs((pchpschedule[i] <= plant.pbound[1] + (1-isopen) * bigm
                          for i in range(len(pload))), name='%s:e-chp-u-cstr2' % plant.name)
            m.addConstrs((pchpschedule[i] >= plant.pbound[0] - (1-isopen) * bigm
                          for i in range(len(pload))), name='%s:e-chp-d-cstr2' % plant.name)
            m.addConstrs((hchpschedule[i] <= plant.hbound[1] + (1-isopen) * bigm
                          for i in range(len(pload))), name='%s:h-chp-u-cstr2' % plant.name)
            m.addConstrs((hchpschedule[i] >= plant.hbound[0] - (1-isopen) * bigm
                          for i in range(len(pload))), name='%s:h-chp-d-cstr2' % plant.name)
            m.addConstrs((hchpschedule[i] <= pchpschedule[i] * 1.7 for i in range(len(pload))),
                         name='%s:eh-chp-cstr' % plant.name)
        # 电热供需约束
        m.update()
        p_intime = list(zip(*(pchpschedules + wpschedules)))
        h_intime = list(zip(*hchpschedules))
        m.addConstrs((sum(p_intime[i]) == pload[i] for i in range(len(pload))), name='pload-cstr')
        m.addConstrs((sum(h_intime[i]) == hload[i] for i in range(len(hload))), name='hload-cstr')
        # 潮流约束
        m.addConstrs((quicksum(mats[j][k]*p_intime[i][k] for k in range(len(p_intime[i]))) <= pfctr[j]
                      for j in range(len(pfctr)) for i in range(len(pload))), name='pf-u-cstr')
        m.addConstrs((quicksum(mats[j][k]*p_intime[i][k] for k in range(len(p_intime[i]))) >= -pfctr[j]
                      for j in range(len(pfctr)) for i in range(len(pload))), name='pf-d-cstr')
        m.update()
        # Set objective
        m.setObjective(cal_cost(chpplants, pchpschedules, hchpschedules, isopens, wplants, wpschedules), GRB.MINIMIZE)
        m.optimize()
        # 输出结果
        print('决策变量：\n' + '-' * 100)
        for v in m.getVars():
            print('%30s %0.2f' % (v.varName, v.x))
        print('松弛变量：\n' + '-' * 100)
        for c in m.getConstrs():
            print('%30s %0.2f' % (c.ConstrName, c.Slack))
        print('最优结果：\n' + '-' * 100)
        print('%30s %0.2f' % ('Optimal Obj:', m.objVal))
        # 画图
        if plot_result:
            plt.rcParams['font.sans-serif'] = ['SimHei']
            # 负荷
            plt.figure()
            plt.plot(list(range(1, len(pload) + 1)), pload, 'cx-', label=u"电负荷曲线")
            plt.plot(list(range(1, len(hload) + 1)), hload, 'mo-', label=u"热负荷曲线")
            plt.ylabel(u"负荷曲线(MW)")
            plt.legend()
            plt.title(u"负荷曲线(MW)")
            plt.show()
            # 机组
            for plant, wpschedule in zip(wplants, wpschedules):
                plt.figure()
                wp = list(wpschedule[i].x for i in range(len(wpschedule)))
                plt.plot(list(range(1, len(wp) + 1)), wp, 'cx-', label=u"出力曲线")
                plt.plot(list(range(1, len(wp) + 1)), plant.maxwp, 'r--', label=u"最大出力曲线")
                plt.ylabel(u"出力曲线(MW)")
                plt.legend()
                plt.title(u"%s出力曲线(MW)" % plant.name)
                plt.show()
            for plant, pchpschedule, hchpschedule in zip(chpplants, pchpschedules, hchpschedules):
                plt.figure()
                pchp = list(pchpschedule[i].x for i in range(len(pchpschedule)))
                hchp = list(hchpschedule[i].x for i in range(len(hchpschedule)))
                plt.plot(list(range(1, len(pchp) + 1)), pchp, 'cx-', label=u"电出力曲线")
                plt.plot(list(range(1, len(pchp) + 1)), [plant.pbound[0]] * len(pchpschedule), 'r--', label=u"电出力下限")
                plt.plot(list(range(1, len(pchp) + 1)), hchp, 'mo-', label=u"热出力曲线")
                plt.ylabel(u"出力曲线(MW)")
                plt.legend()
                plt.title(u"%s出力曲线(MW)" % plant.name)
                plt.show()
    except GurobiError:
        print('Error reported')


class Plant:
    def __init__(self, *, ptype, pbound=None, hbound=None, costfun=lambda x: 0, maxwp=None, reformtype=None, name=None):
        self.name = name
        self.ptype = ptype
        self.pbound = pbound
        self.hbound = hbound
        self.costfun = costfun
        self.maxwp = maxwp
        self.reformtype = reformtype


def cal_cost(chpplants, pchpschedules, hchpschedules, isopens, wplants, wpschedules):
    result = 0
    # CHP
    p = list()
    h = list()
    for plant, pchpschedule, hchpschedule, isopen in zip(chpplants, pchpschedules, hchpschedules, isopens):
        result += quicksum((pchpschedule[i] + hchpschedule[i]*0.17) * plant.costfun(pchpschedule[i], hchpschedule[i])
                           for i in range(len(pchpschedule)))
        result += isopen * plant.costfun(plant.pbound[1], plant.hbound[1]) * len(pchpschedule) * 0.1
        p.append(np.mat(pchpschedule) / plant.pbound[1])
        h.append(np.mat(hchpschedule) / plant.hbound[1])
    p_intime = list(zip(*p))
    h_intime = list(zip(*h))
    for pt, ht in zip(p_intime, h_intime):
        result += np.var(pt) * 0.001
        result += np.var(ht) * 0.001
    # 风电
    wp = list()
    for wplant, wpschedule in zip(wplants, wpschedules):
        wp.append(list(wpschedule[i] / wplant.maxwp[i] for i in range(len(wplant.maxwp))))
    wp_intime = list(zip(*wp))
    for wpt in wp_intime:
        result += np.var(wpt) * 0.001
    return result




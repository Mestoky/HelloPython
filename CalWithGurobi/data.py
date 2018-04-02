from prosimu import *
from pfmatrix import *

pload = [500, 500, 800, 810, 500]
hload = [200, 200, 200, 200, 200]
wp1 = [40, 40, 30, 40, 50]
wp2 = [30, 50, 30, 50, 30]
s = [0.25, 0.25, 0, 0, 0.25, 0.25, 0, 0, 0.25, 0, 0, 0.25, 0.25, 0, 0.25]
n = 6
x = PfMatrix(s, n)
x[x < 0.00001] = 0
xx = x.tolist()
print(x)
pfcstr = [300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 75]

plants = list()
plants.append(Plant(ptype=1, pbound=(180, 280), hbound=(0, 200),
                    costfun=(lambda p, h: 200), name='CHP_HS1'))
plants.append(Plant(ptype=1, pbound=(120, 280), hbound=(0, 200),
                    costfun=(lambda p, h: 200), name='CHP_SF1'))
plants.append(Plant(ptype=1, pbound=(120, 280), hbound=(0, 200),
                    costfun=(lambda p, h: 200), name='CHP_SF2'))
plants.append(Plant(ptype=0, pbound=(0, 50), maxwp=wp1, name='WP1'))
plants.append(Plant(ptype=0, pbound=(0, 50), maxwp=wp2, name='WP2'))


prod_simulation(plants, pload, hload, xx, pfcstr, plot_result=1)



from prosimu import *

pload = [500, 500, 700, 710, 500]
hload = [300, 300, 300, 300, 300]
wp1 = [40, 50, 30, 40, 50]
wp2 = [50, 40, 30, 50, 30]

plants = list()
plants.append(Unit(ptype=1, pbound=(180, 280), hbound=(0, 200),
                   costfun=(lambda p: (0.001*p**2+200*p+200)), name='PC1'))
plants.append(Unit(ptype=2, pbound=(120, 280), hbound=(0, 200),
                   costfun=(lambda p: (0.001*p**2+200*p+200)), name='CHP_SF1', rtype=1))
plants.append(Unit(ptype=1, pbound=(120, 280), hbound=(0, 200),
                   costfun=(lambda p: (0.001*p**2+200*p+200)), name='PC2'))
# plants.append(Unit(ptype=1, pbound=(140, 280), hbound=(0, 200),
#                    costfun=(lambda p: (0.001*p**2+200*p+200)), name='PC3'))
plants.append(Unit(ptype=0, pbound=(0, 50), maxwp=wp1, name='WP1'))
plants.append(Unit(ptype=0, pbound=(0, 50), maxwp=wp2, name='WP2'))


a = ProSimu()
a.plot = 1
a.units = plants
a.pload = pload
a.hload = hload
a.solve()

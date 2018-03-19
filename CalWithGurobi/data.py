from prosimu import *

pload = [500, 700, 800, 810, 500]
hload = [200, 200, 200, 200, 200]
wp1 = [20, 40, 30, 30, 50]
wp2 = [30, 50, 30, 20, 30]


plants = list()
plants.append(Plant(ptype=1, pbound=(180, 280), hbound=(0, 200),
                    costfun=(lambda p, h: 0.004 * (p + 0.1 * h - 230) * (p + 0.1 * h - 230) + 190), name='CHP_HS1'))
plants.append(Plant(ptype=1, pbound=(120, 280), hbound=(0, 200),
                    costfun=(lambda p, h: 0.004 * (p + 0.1 * h - 230) * (p + 0.1 * h - 230) + 190), name='CHP_SF1'))
plants.append(Plant(ptype=1, pbound=(120, 280), hbound=(0, 200),
                    costfun=(lambda p, h: 0.004 * (p + 0.1 * h - 230) * (p + 0.1 * h - 230) + 190), name='CHP_SF2'))
plants.append(Plant(ptype=0, pbound=(0, 50), maxwp=wp1, name='WP1'))
plants.append(Plant(ptype=0, pbound=(0, 50), maxwp=wp2, name='WP2'))


prod_simulation(plants, pload, hload)


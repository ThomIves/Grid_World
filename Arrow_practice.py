import vpython as vp
import numpy as np
import time

axis_list = [vp.vector(-1, 0, 0), vp.vector(1, 0, 0),
             vp.vector(0, -1, 0), vp.vector(0, 1, 0)]

num = 0

arrow = vp.arrow(
    pos=vp.vector(0, 0, 0),
    axis=vp.vector(0.0, 0.0, 1),
    shaftwidth=0.1,
    color=vp.color.red)

arrow.rotate(
    angle=np.pi/2, axis=axis_list[num],
    origin=vp.vector(0, 0, 0.1))

for i in [0.2, 0.1, 0.0, 0.1]:
    time.sleep(2)
    arrow.shaftwidth = i + 0.001
    print(arrow.shaftwidth)

print('Done')

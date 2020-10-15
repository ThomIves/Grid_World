import vpython as vp
import numpy as np

grid_width = 1.0
grid_height = 1.0
grid_thick = 0.05
arrow_width = grid_thick
arrow_length = grid_width / 3.0 - 2.0 * grid_thick

rows = 3
cols = 4

ctr_x = float(cols * grid_width) / 2.0 - grid_width / 2.0
ctr_y = float(rows * grid_height) / 2.0 - grid_height / 2.0

vp.sphere(pos=vp.vector(0, 0, 0), radius=0.1, color=vp.color.red)

axis_list = [vp.vector(-1, 0, 0),
             vp.vector(1, 0, 0),
             vp.vector(0, -1, 0),
             vp.vector(0, 1, 0)]

squares = []
arrows = []
for col in range(cols):
    squares.append([])
    arrows.append([])
    for row in range(rows):
        squares[col].append(vp.box(
            pos=vp.vector(
                col * grid_width - ctr_x,
                row * grid_height - ctr_y, 0),
            axis=vp.vector(0, 0, grid_thick),
            width=grid_width - grid_thick,
            height=grid_height - grid_thick))

        arrows[col].append([])
        for arrow in range(4):
            # Need arrow tips next
            arrows[col][row].append(vp.box(
                pos=vp.vector(col * grid_width - ctr_x,
                              row * grid_height - ctr_y,
                              arrow_length / 2.0 +
                              grid_thick +
                              arrow_length / 2.0),
                axis=vp.vector(0.0,
                               0.0,
                               arrow_length),
                width=arrow_width,
                height=arrow_width,
                color=vp.color.red))

            arrows[col][row][-1].rotate(
                angle=np.pi/2,
                axis=axis_list[arrow],
                origin=vp.vector(
                    col * grid_width - ctr_x,
                    row * grid_height - ctr_y,
                    grid_thick))

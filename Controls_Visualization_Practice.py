import vpython as vp
import numpy as np
import sys


vp.box()


def B(b):
    print("The button said this: ", b.text)


vp.button(bind=B, text='Click me!')
# vp.scene.append_to_caption('\n\n')


def T(s):
    print(s, type(s.number), s.number)


vp.winput(bind=T)


# def R(r):
#     print(r.checked)  # alternates
#
#
# vp.radio(bind=R, text='Run')  # text to right of button
# vp.scene.append_to_caption('\n\n')
#
#
# def C(r):
#     print(r.checked)  # alternates
#
#
# vp.checkbox(bind=C, text='Run')  # text to right of checkbox
# vp.scene.append_to_caption('\n\n')
#
#
# def S(s):
#     print(s.value)
#
#
# vp.slider(bind=S)
# vp.scene.append_to_caption('\n\n')
#
#
# def M(m):
#     print(m.selected, m.index)
#
#
# vp.menu(choices=['cat', 'dog', 'horse'], bind=M)
# vp.scene.append_to_caption('\n\n')
#
#
# def T(s):
#     print(s.text, s.number)
#
#
# vp.winput(bind=T)
# s = input('What is your name?')

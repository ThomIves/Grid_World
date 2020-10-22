import vpython as vp
import numpy as np
import time
import sys
import pprint

pp = pprint.PrettyPrinter(indent=2)


class Grid_Visualization:
    def __init__(self, grid_instance, grid_dict,
                 grid_width=1.0, grid_height=1.0, grid_thick=0.05,
                 arrow_base_width=0.05, show_ctr=False):

        self.GI = grid_instance
        self.grid_dict = grid_dict
        self.cols = grid_dict['cols']
        self.rows = grid_dict['rows']
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid_thick = grid_thick

        scale = 2.0
        self.agent_radius = grid_width / (5.0 / scale)
        self.bounce_scale = 1.0 / (self.agent_radius - grid_width / 2.0)
        # 4.0 / scale

        self.arrow_length = grid_width / 3.0 - 2.0 * grid_thick
        self.arrow_base_width = arrow_base_width

        self.ctr_x = float(self.cols * grid_width) / 2.0 - grid_width / 2.0
        self.ctr_y = float(self.rows * grid_height) / 2.0 - grid_height / 2.0

        if show_ctr:
            vp.sphere(pos=vp.vector(0, 0, 0), radius=0.1, color=vp.color.red)

        self.axis_list = [vp.vector(-1, 0, 0), vp.vector(1, 0, 0),
                          vp.vector(0, -1, 0), vp.vector(0, 1, 0)]

        agent_x = +self.grid_dict['start'][1] * self.grid_width - self.ctr_x
        agent_y = -self.grid_dict['start'][0] * self.grid_height + self.ctr_y

        self.agent = vp.cylinder(
            pos=vp.vector(agent_x, agent_y, grid_thick / 2.0),
            radius=self.agent_radius, axis=vp.vector(0, 0, grid_thick),
            color=vp.color.white, texture='Kate_Agent.jpg')

        self.squares = []
        self.arrows = []
        self.rewards = []
        self.returns = []
        self.grid_dict['returns'] = {}
        for col in range(self.cols):
            self.squares.append([])
            self.arrows.append([])
            self.rewards.append([])
            self.returns.append([])
            for row in range(self.rows):
                loc = (row, col)
                self.squares[col].append('')
                self.arrows[col].append([])
                self.rewards[col].append('')
                self.returns[col].append('')
                for i in range(4):
                    self.arrows[col][row].append('')

        T = vp.text(text="Gauntlet Grid World", align='center',
                    color=vp.color.white,
                    height=self.grid_height * 0.5,
                    pos=vp.vector(0, self.ctr_y + self.grid_height / 1.5, 0))

        self.__draw_grid__()
        self.draw_weighted_arrows()
        self.display_current_rewards_returns()
        self.__step_button__()
        self.__start_over_button__()
        self.__auto_stepping_button__()
        vp.scene.append_to_caption("  Set Pause Time: ")
        self.__pause_time_input__()
        self.__clear_records_button__()

    def __draw_grid__(self):
        reward_height = self.grid_height * 0.2
        for col in range(self.cols):
            for row in range(self.rows):
                loc = (row, col)
                if self.grid_dict['rewards'][loc] is None:
                    color = vp.color.black
                elif self.grid_dict['start'] == loc:
                    color = vp.color.green
                elif self.grid_dict['actions'][loc] == 'win':
                    color = vp.color.white
                    win_loc = loc
                elif self.grid_dict['actions'][loc] == 'lose':
                    color = vp.color.white
                    lose_loc = loc
                else:
                    color = vp.color.white

                x = col * self.grid_width - self.ctr_x
                y = -row * self.grid_height + self.ctr_y

                self.squares[col][row] = vp.box(
                    pos=vp.vector(x, y, 0),
                    axis=vp.vector(0, 0, self.grid_thick),
                    width=self.grid_width - self.grid_thick,
                    height=self.grid_height - self.grid_thick,
                    color=color)

        self.squares[win_loc[1]][win_loc[0]].texture = 'DATAcated.jpg'
        self.squares[lose_loc[1]][lose_loc[0]].texture = 'NotReg.jpg'

    def draw_weighted_arrows(self):
        for col in range(self.cols):
            for row in range(self.rows):
                state = (row, col)

                if self.GI.max_acts.get(state, None):
                    num_arrows = len(self.GI.max_acts[state])
                    arrow_width = self.arrow_base_width / num_arrows

                x = col * self.grid_width - self.ctr_x
                y = -row * self.grid_height + self.ctr_y
                al = self.arrow_length
                z = al / 2.0 + self.grid_thick + al / 2.0

                for arrow in range(4):
                    the_act = self.GI.actions[arrow]
                    max_acts = self.GI.max_acts.get(state, [])
                    if the_act not in max_acts:
                        self.arrows[col][row][arrow] = ''
                        continue

                    self.arrows[col][row][arrow] = vp.arrow(
                        pos=vp.vector(x, y, z),
                        axis=vp.vector(0.0, 0.0, al),
                        shaftwidth=arrow_width,
                        color=vp.color.red)

                    self.arrows[col][row][arrow].rotate(
                        angle=np.pi/2, axis=self.axis_list[arrow],
                        origin=vp.vector(x, y, self.grid_thick))

    def change_width_of_arrows(self):
        for col in range(self.cols):
            for row in range(self.rows):
                state = (row, col)

                max_acts_list = self.GI.max_acts.get(state, [])
                if max_acts_list:
                    num_arrows = len(max_acts_list)
                    arrow_width = 0.1 / num_arrows

                for arrow_num in range(4):
                    if self.arrows[col][row][arrow_num] == '':
                        continue

                    the_act = self.GI.actions[arrow_num]
                    max_acts = self.GI.max_acts.get(state, [])
                    if the_act not in max_acts:
                        self.arrows[col][row][arrow_num].shaftwidth = 0.001
                    else:
                        self.arrows[col][row][arrow_num].shaftwidth \
                            = arrow_width

    def display_current_rewards_returns(self):
        # self.GI.V_of_s[loc]
        # self.grid_dict['returns'][loc] = \
        #     self.grid_dict['rewards'][loc]
        text_ht_1 = self.grid_height * 0.1
        text_ht_2 = self.grid_height * 0.1

        for col in range(self.cols):
            for row in range(self.rows):
                loc = (row, col)
                x1 = col * self.grid_width - self.ctr_x - \
                    self.grid_width / 4.0
                y1 = -row * self.grid_height + self.ctr_y - \
                    self.grid_width / 4.0
                the_text_1 = self.grid_dict['rewards'][loc]
                if str(the_text_1) in ('10', '-10'):
                    the_text_1 = None

                if the_text_1 is not None:
                    self.rewards[col][row] = vp.text(
                        text=str(the_text_1), height=text_ht_1,
                        align='center', color=vp.color.black,
                        pos=vp.vector(x1, y1 - text_ht_1 / 2,
                                      self.grid_thick * 2))

                # y2 = -row * self.grid_height + self.ctr_y + \
                #     self.grid_width / 4.0
                # the_text_2 = self.GI.V_of_s.get(loc, None)
                #
                # if the_text_2 is not None:
                #     self.returns[col][row] = vp.text(
                #         text=str(round(the_text_2, 2)), height=text_ht_2,
                #         align='center', color=vp.color.black,
                #         pos=vp.vector(x1, y2 - text_ht_2 / 2,
                #                       self.grid_thick * 2))

    def __step_button__(self):
        vp.button(bind=self.GI.determine_agent_step,
                  text='Step')

    def __auto_stepping_button__(self):
        vp.button(bind=self.GI.auto_stepping,
                  text='Automate Episode')

    def __start_over_button__(self):
        vp.button(bind=self.GI.restart_agent,
                  text='Restart')

    def __clear_records_button__(self):
        vp.button(bind=self.GI.clear_records,
                  text='Clear Records')

    def __pause_time_input__(self):
        vp.winput(bind=self.__set_pause_time__,
                  text=f'{self.GI.pause_time}')

    def __set_pause_time__(self, capture):
        self.GI.pause_time = capture.number

    def move_agent(self, loc):
        if type(loc) is tuple:
            agent_x = +loc[1] * self.grid_width - self.ctr_x
            agent_y = -loc[0] * self.grid_height + self.ctr_y

            self.agent.pos = vp.vector(
                agent_x, agent_y, self.grid_thick / 2.0)

        if type(loc) is list:
            temp_loc = (loc[0][0] - loc[1][0],
                        loc[0][1] - loc[1][1])

            agent_x = self.agent.pos.x + temp_loc[1] / self.bounce_scale
            agent_y = self.agent.pos.y - temp_loc[0] / self.bounce_scale

            self.agent.pos = vp.vector(
                agent_x, agent_y, self.grid_thick / 2.0)

            time.sleep(self.GI.pause_time)

            agent_x = self.agent.pos.x - temp_loc[1] / self.bounce_scale
            agent_y = self.agent.pos.y + temp_loc[0] / self.bounce_scale

            self.agent.pos = vp.vector(
                agent_x, agent_y, self.grid_thick / 2.0)

    def __start_over__(self):
        agent_x = +self.grid_dict['start'][1] * self.grid_width - self.ctr_x
        agent_y = -self.grid_dict['start'][0] * self.grid_height + self.ctr_y

        self.agent.pos = vp.vector(
            agent_x, agent_y, self.grid_thick / 2.0)

from Grid_Visualization import Grid_Visualization as GV

import sys
import random
import math
import time
import json
import os
import copy
import pprint

pp = pprint.PrettyPrinter(indent=2)


class Grid_Data:
    def __init__(self, grid_dict={}, rows=0, cols=0, percent_walls=0,
                 values=-1, terms=10, trim_impossibles=False,
                 gamma=0.9, epsilon=0.7, max_steps=500,
                 pause_time=0.05):
        self.grid_dict = grid_dict
        self.rows = 3 if rows == 0 else rows
        self.cols = 4 if cols == 0 else cols
        self.max_dist = (self.rows**2 + self.cols**2)**0.5
        self.pc_walls = 0.1 if percent_walls == 0 else percent_walls//100
        self.values = values
        self.terms = terms
        self.actions_D = {0: 'up', 1: 'dn', 2: 'lt', 3: 'rt'}
        self.actions = list(self.actions_D.values())

        self.gamma = gamma
        self.epsilon = epsilon
        self.max_steps = max_steps
        self.pause_time = pause_time

        # self.records_file_name = 'action_state_rewards.data'
        # self.records = self.__load_records_object_from_file__()
        self.records = {}
        self.episode = "0"
        self.num_steps = 0
        self.episode = self.__get_next_episode_value__()
        self.records[self.episode] = []

        # self.grid_dict['returns'] = self.grid_dict['rewards']

        if not self.grid_dict:
            self.grid_dict = {'rows': self.rows, 'cols': self.cols}
            self.grid_dict['poss_actions'] = self.actions_D
            self.__auto_generate_grid__()
        if trim_impossibles:
            self.__trim_impossible_policies__()

        self.state = self.grid_dict['start']
        self.all_states = [
            l for l in list(self.grid_dict['rewards'].keys())
            if self.grid_dict['rewards'][l] is not None]
        self.all_action_states = [
            l for l in list(self.grid_dict['actions'].keys())
            if type(self.grid_dict['actions'][l]) is list]
        self.terminal_states = [
            l for l in self.all_states
            if abs(self.grid_dict['rewards'][l]) == self.terms]

        self.__initialize_V_of_s__()

        self.rewards_D = {}
        self.trans_probs_D = {}
        self.policy = {}
        self.actions_probs = {}
        self.max_acts = {}

        for state in self.all_action_states:
            self.policy[state] = [[0.0, 'up'], [0.0, 'dn'],
                                  [0.0, 'lt'], [0.0, 'rt']]
            self.max_acts[state] = self.actions
            for act in self.actions:
                self.actions_probs[(state, act)] = 0.25

        self.old_policy = copy.deepcopy(self.policy)
        self.gv = GV(self, self.grid_dict)

    def __initialize_V_of_s__(self):
        self.V_of_s = {}

        for state in self.all_states:
            self.V_of_s[state] = 0

    def __trim_impossible_policies__(self):
        aD = self.grid_dict['actions']
        rD = self.grid_dict['rewards']

        locs = list(aD.keys())

        for loc in locs:
            up = (loc[0] - 1, loc[1])
            dn = (loc[0] + 1, loc[1])
            lt = (loc[0], loc[1] - 1)
            rt = (loc[0], loc[1] + 1)

            actD = {up: 'up', dn: 'dn', lt: 'lt', rt: 'rt'}

            for act in actD.keys():
                ast = actD[act]
                if type(aD[loc]) is list:
                    if ((ast in aD[loc])
                       and (act not in locs)
                       or (act in locs and aD[act] is None)):
                        aD[loc].remove(ast)

    def __auto_generate_grid__(self):
        num_posts = math.ceil((self.rows * self.cols - 2) * 0.1)
        locations_buffer = []
        posts_buf = []
        aD = {}
        rD = {}

        ''' Pick start point '''
        row = random.randint(0, self.rows - 1)
        col = 0
        locations_buffer.append((row, col))

        ''' Pick Fail and Win '''
        while len(locations_buffer) < 4:
            row = random.randint(0, self.rows - 1)
            col = self.cols - 1
            if (row, col) not in locations_buffer:
                locations_buffer.append((row, col))

        ''' Need routine to distribute posts well '''
        while len(posts_buf) < num_posts:
            row = random.randint(1, self.rows - 2)
            col = random.randint(1, self.cols - 2)
            if (row, col) not in posts_buf:
                posts_buf.append((row, col))  # NEED MORE ...

        ''' Start Data '''
        self.grid_dict['start'] = locations_buffer[0]
        rD[locations_buffer[0]] = -1
        aD[locations_buffer[0]] = list(self.actions_D.values())

        ''' Terminations Data '''
        rD[locations_buffer[1]] = 10
        aD[locations_buffer[1]] = 'win'
        rD[locations_buffer[2]] = -10
        aD[locations_buffer[2]] = 'lose'

        ''' Columns Data '''
        for loc in posts_buf:
            rD[loc] = None
            aD[loc] = None

        ''' Fill in remaining data '''
        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) not in rD:
                    rD[(row, col)] = -1
                if (row, col) not in aD:
                    aD[(row, col)] = list(self.actions_D.values())

        self.grid_dict['actions'] = aD
        self.grid_dict['rewards'] = rD

        self.__trim_impossible_policies__()

    def __get_loc_for_move__(self, current_loc, move_str):
        if move_str == 'up':
            new_loc = (current_loc[0] - 1, current_loc[1])
        elif move_str == 'dn':
            new_loc = (current_loc[0] + 1, current_loc[1])
        elif move_str == 'lt':
            new_loc = (current_loc[0], current_loc[1] - 1)
        elif move_str == 'rt':
            new_loc = (current_loc[0], current_loc[1] + 1)

        if new_loc not in self.grid_dict['rewards'].keys():
            return [new_loc, current_loc]
        elif self.grid_dict['rewards'][new_loc] is None:
            return [new_loc, current_loc]
        else:
            return new_loc

    def report_actions(self):
        print('Actions:')
        pp.pprint(self.grid_dict['actions'])
        print()

    def report_rewards(self):
        print('Rewards:')
        pp.pprint(self.grid_dict['rewards'])
        print()

    def determine_agent_step(self):
        terminals = ('win', 'lose')
        result = self.grid_dict['actions'][self.state]
        done = result in terminals or self.num_steps >= self.max_steps

        if done:
            self.__episode_wrap_up__()
            return False

        the_action = self.__get_next_action__()

        previous_state = self.state
        self.state = self.__get_loc_for_move__(previous_state, the_action)

        if type(self.state) is tuple:
            state = self.state
        elif type(self.state) is list:
            state = self.state[1]

        reward = self.grid_dict["rewards"][state]

        self.records[self.episode].append([
            self.num_steps, previous_state, the_action, state, reward])
        self.num_steps += 1

        self.__move_agent__(self.state)

        return True

    def __get_next_action__(self):
        coin = random.uniform(0, 1)

        if coin < self.epsilon:
            return random.choice(self.actions)

        # print(self.state)
        this_max = self.policy[self.state][0][0]
        max_actions = [
            a[1] for a in self.policy[self.state] if a[0] == this_max]
        # print(this_max, max_actions)
        # print()

        return random.choice(max_actions)

    def restart_agent(self):
        self.state = self.grid_dict['start']
        self.gv.__start_over__()
        self.episode = self.__get_next_episode_value__()
        self.records[self.episode] = []

        # self.__store_records_object_to_file__()

        self.num_steps = 0

    def clear_records(self):
        self.records = {}
        # self.__store_records_object_to_file__()
        self.episode = "0"
        self.records[self.episode] = []

    def __move_agent__(self, loc):
        self.gv.move_agent(loc)
        if type(loc) is list:
            self.state = loc[1]

    def auto_stepping(self):
        while self.determine_agent_step():
            time.sleep(self.pause_time)
            # result = self.grid_dict['actions'][self.state]

    def __episode_wrap_up__(self):
        # self.__store_records_object_to_file__()

        self.__evaluate_policy__()
        self.__find_policy_rankings__()

        print(f'\nPercent Exploration = {round(self.epsilon*100, 2)}')
        print('Current State: Value: Policies')
        for state in self.max_acts:
            val = round(self.V_of_s[state], 3)
            acts = self.max_acts[state]
            print(f'{state}: {val}: {acts}')
        print()

        self.epsilon *= self.gamma
        self.gv.change_width_of_arrows()

        time.sleep(1.0)
        self.restart_agent()

    # def __load_records_object_from_file__(self):
    #     file_exists = os.path.exists(self.records_file_name)
    #     if not file_exists:
    #         self.records = {}
    #         self.episode = "0"
    #
    #         return self.records
    #
    #     with open(self.records_file_name, 'r', encoding="utf-8") as f:
    #         self.records = json.load(f)
    #         record_keys = list(self.records.keys())
    #         self.episode = str(max([int(e) for e in record_keys]))
    #
    #         return self.records

    # def __store_records_object_to_file__(self):
    #     with open(self.records_file_name, 'w', encoding="utf-8") as f:
    #         json.dump(self.records, f, ensure_ascii=False, indent=4)

    def __get_next_episode_value__(self):
        record_keys = list(self.records.keys())

        if record_keys:
            record_keys = [int(k) for k in record_keys]
            next_episode = str(max(record_keys) + 1)
        else:
            next_episode = str(0)

        return next_episode

    def __evaluate_policy__(self):
        self.__initialize_V_of_s__()
        iteration = 0

        episode_list = self.records[self.episode]

        for event in episode_list:
            state = tuple(event[1])
            action = event[2]
            state_next = tuple(event[3])
            reward = event[4]
            trans = (state, action, state_next)
            if trans not in self.rewards_D.keys():
                self.rewards_D[trans] = reward
            if trans not in self.trans_probs_D.keys():
                self.trans_probs_D[(state, action, state_next)] = 1

        while True:
            max_Delta = 0
            for state in self.all_states:
                if state not in self.terminal_states:
                    old_V_of_s = self.V_of_s[state]
                    new_V_of_s = 0
                    for action in self.actions:
                        for state_next in self.all_states:
                            trans = (state, action, state_next)
                            action_prob = self.actions_probs.get(
                                (state, action), 0)
                            trans_prob = self.trans_probs_D.get(trans, 0)
                            reward = self.rewards_D.get(trans, 0)
                            Vs_next = self.V_of_s[state_next]

                            new_V_of_s += action_prob * trans_prob * \
                                (reward + self.gamma * Vs_next)

                    self.V_of_s[state] = new_V_of_s
                    max_Delta = max(max_Delta,
                                    abs(old_V_of_s - self.V_of_s[state]))

            iteration += 1

            if max_Delta < 0.001:
                break

        self.gv.display_current_rewards_returns()

    def __find_policy_rankings__(self):
        episode_list = self.records[self.episode]

        self.actions_probs = {}

        for state in self.all_action_states:
            self.policy[state] = []
            for action in self.actions:
                value = 0
                for state_next in self.all_states:
                    trans = (state, action, state_next)
                    trans_prob = self.trans_probs_D.get(trans, 0)
                    reward = self.rewards_D.get(trans, 0)

                    value += trans_prob \
                        * (reward + self.gamma * self.V_of_s[state_next])

                self.policy[state].append([value, action])

            self.policy[state].sort(reverse=True)

            this_max = self.policy[state][0][0]
            max_actions = [
                a[1] for a in self.policy[state] if a[0] == this_max]
            num_max_actions = len(max_actions)

            self.max_acts[state] = max_actions

            for action in self.actions:
                self.actions_probs[(state, action)] = 0.0

            for action in max_actions:
                self.actions_probs[(state, action)] = 1.0 / num_max_actions


grid_dict = {
    'start': (2, 0), 'rows': 3, 'cols': 4,
    'poss_actions': {0: 'up', 1: 'dn', 2: 'lt', 3: 'rt'},
    'rewards': {
        (0, 0): -1,
        (0, 1): -1,
        (0, 2): -1,
        (0, 3): 10,
        (1, 0): -1,
        (1, 1): None,
        (1, 2): -1,
        (1, 3): -10,
        (2, 0): -1,
        (2, 1): -1,
        (2, 2): -1,
        (2, 3): -1
        },
    'actions': {
        (0, 0): ['up', 'dn', 'lt', 'rt'],
        (0, 1): ['up', 'dn', 'lt', 'rt'],
        (0, 2): ['up', 'dn', 'lt', 'rt'],
        (0, 3): 'win',
        (1, 0): ['up', 'dn', 'lt', 'rt'],
        (1, 1): None,
        (1, 2): ['up', 'dn', 'lt', 'rt'],
        (1, 3): 'lose',
        (2, 0): ['up', 'dn', 'lt', 'rt'],
        (2, 1): ['up', 'dn', 'lt', 'rt'],
        (2, 2): ['up', 'dn', 'lt', 'rt'],
        (2, 3): ['up', 'dn', 'lt', 'rt']
        }
}

gd = Grid_Data(rows=4, cols=6, max_steps=800)  # grid_dict=grid_dict)  #

# gd.report_actions()
# gd.report_rewards()
# gd.determine_agent_step()
# gd.move_agent((1, 0))

import pprint
import sys
import random
import math
import time
import json
import os

from Grid_Visualization import Grid_Visualization as GV

pp = pprint.PrettyPrinter(indent=2)


class Grid_Data:
    def __init__(self, grid_dict={}, rows=0, cols=0, percent_walls=0,
                 values=-1, terms=10, trim_impossibles=False,
                 gamma=0.9):
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

        self.records_file_name = 'action_state_rewards.data'
        self.records = self.__load_records_object_from_file__()
        self.step_num = 0

        self.grid_dict['returns'] = self.grid_dict['rewards']

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

        self.V_of_s = {}
        self.Q_of_s = {}
        self.max_P = {}
        self.ratio_P = {}

        for state in self.all_states:
            self.V_of_s[state] = 0
            for action in self.actions:
                self.Q_of_s[(state, action)] = 0

        self.pause_time = 0.1

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
        num_columns = math.ceil((self.rows * self.cols - 2) * 0.1)
        locations_buffer = []
        cols_buf = []
        aD = {}
        rD = {}

        while len(locations_buffer) < 4:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if 0 < len(locations_buffer) < 3:
                x_dist = locations_buffer[0][1] - col
                y_dist = locations_buffer[0][0] - row
                h_dist = (x_dist**2 + y_dist**2)**0.5
                if ((h_dist < 0.5*self.max_dist) or (
                  (row, col) in locations_buffer)):
                    continue
            locations_buffer.append((row, col))

        ''' Need routine to distribute columns well '''
        while 4 <= len(locations_buffer) < (num_columns + 3):
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if ((h_dist < 0.5*self.max_dist) or (
              (row, col) in locations_buffer)):
                pass  # NEED MORE ...
            if cols_buf > 0:  # NEED MORE ...
                cols_buf.append((row, col))  # NEED MORE ...

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
        for loc in locations_buffer[3:]:
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

    def __policy_distribution__(self):
        # print()
        for loc in self.grid_dict['actions'].keys():
            if self.grid_dict['actions'][loc]:
                count = len(self.grid_dict['actions'][loc])
            else:
                count = 0
            # print(loc, self.grid_dict['actions'][loc], count)

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

    def visualize_grid(self):
        self.gv = GV(self, self.grid_dict)
        self.__policy_distribution__()

    def determine_agent_step(self):
        actions = self.grid_dict['actions'][self.state]
        temp_actions = [a for a in actions]
        if 'win' == actions or 'lose' == actions:
            return

        coin = random.uniform(0, 1)
        print(f'Coin is {coin}')

        best_move = self.max_P.get(self.state)
        print(f'Best move is {best_move}')

        ratio = self.ratio_P.get(self.state)
        print(f'Ratio is {ratio}')

        if best_move:
            temp_actions.remove(best_move)
            print(f'Actions are {actions}')
            print(f'Temp Actions are {temp_actions}')

        if best_move and ratio <= coin:
            the_action = best_move
            print('Used best move')
        elif best_move:  # and self.ratio_P.get(self.state) > coin
            zones = []
            num_actions = len(temp_actions)
            step = 1.0 / num_actions
            for i in range(num_actions):
                logic = i * step <= coin < step * (i + 1)
                zones.append(logic)
            the_action = temp_actions[zones.index(True)]
            print('Exploring')
        else:
            zones = []
            num_actions = len(actions)
            step = 1.0 / num_actions
            for i in range(num_actions):
                logic = i * step <= coin < step * (i + 1)
                zones.append(logic)
            the_action = actions[zones.index(True)]
            print('No policy set yet')

        print()

        previous_state = self.state
        self.state = self.__get_loc_for_move__(previous_state, the_action)

        if type(self.state) is tuple:
            state = self.state
        elif type(self.state) is list:
            state = self.state[1]

        reward = self.grid_dict["rewards"][state]

        self.records[self.episode].append([
            self.step_num, previous_state, the_action, state, reward])
        self.step_num += 1

        self.__move_agent__(self.state)

    def restart_agent(self):
        self.state = self.grid_dict['start']
        self.gv.__start_over__()

        # print(f'\nResults for episode {self.episode}')
        # pp.pprint(self.records[self.episode])

        self.__store_records_object_to_file__()

        self.markov_predictions()

        self.step_num = 0

    def clear_records(self):
        self.records = {}
        self.__store_records_object_to_file__()
        self.episode = "0"
        self.records[self.episode] = []

    def __move_agent__(self, loc):
        self.gv.move_agent(loc)
        if type(loc) is list:
            self.state = loc[1]

    def auto_stepping(self):
        self.episode = self.__get_next_episode_value__()
        self.records[self.episode] = []

        reward = self.grid_dict['actions'][self.state]
        while reward not in ('win', 'lose'):
            self.determine_agent_step()
            time.sleep(self.pause_time)
            reward = self.grid_dict['actions'][self.state]

        self.__store_records_object_to_file__()

        time.sleep(2.0)
        self.restart_agent()

    def __load_records_object_from_file__(self):
        file_exists = os.path.exists(self.records_file_name)
        if not file_exists:
            self.records = {}
            self.episode = "0"

            return self.records

        with open(self.records_file_name, 'r', encoding="utf-8") as f:
            self.records = json.load(f)
            record_keys = list(self.records.keys())
            self.episode = str(max([int(e) for e in record_keys]))

            return self.records

    def __store_records_object_to_file__(self):
        with open(self.records_file_name, 'w', encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)

    def __get_next_episode_value__(self):
        record_keys = list(self.records.keys())

        if record_keys:
            record_keys = [int(k) for k in record_keys]
            next_episode = str(max(record_keys) + 1)
        else:
            next_episode = str(0)

        return next_episode

    def __evaluate_policy__(self):
        iteration = 0

        episode_list = self.records[self.episode]
        rewards_D = {}
        trans_probs_D = {}
        for event in episode_list:
            state = tuple(event[1])
            action = event[2]
            state_next = tuple(event[3])
            reward = event[4]
            rewards_D[(state, action, state_next)] = reward
            trans_probs_D[(state, action, state_next)] = 1

        while True:
            max_Delta = 0
            for state in self.all_states:
                if state not in self.terminal_states:
                    old_V_of_s = self.V_of_s[state]
                    new_V_of_s = 0
                    for action in self.actions:
                        for state_next in self.all_states:
                            trans = (state, action, state_next)
                            action_prob = 0.25
                            reward = rewards_D.get(trans, 0)

                            new_V_of_s += action_prob \
                                * trans_probs_D.get(trans, 0) \
                                * (reward + self.gamma *
                                   self.V_of_s[state_next])

                    self.V_of_s[state] = new_V_of_s
                    max_Delta = max(max_Delta,
                                    abs(old_V_of_s - self.V_of_s[state]))

            # print(f'Interation: {iteration}, Max Delta: {max_Delta}')
            # pp.pprint(self.V_of_s)
            # print()
            iteration += 1

            if max_Delta < 0.001:
                break

    def __find_best_policy__(self):
        episode_list = self.records[self.episode]

        policy = {}
        rewards_D = {}
        trans_probs_D = {}

        for event in episode_list:
            state = tuple(event[1])
            action = event[2]
            state_next = tuple(event[3])
            reward = event[4]

            rewards_D[(state, action, state_next)] = reward
            trans_probs_D[(state, action, state_next)] = 1

        policy_is_converged = True

        for state in self.all_action_states:
            policy[state] = []
            for action in self.actions:
                value = 0
                for state_next in self.all_states:
                    trans = (state, action, state_next)
                    trans_prob = trans_probs_D.get(trans, 0)
                    reward = rewards_D.get(trans, 0)

                    value += trans_prob \
                        * (reward + self.gamma * self.V_of_s[state_next])

                policy[state].append([value, action])

            policy[state].sort(reverse=True)

            print(f'For state {state}:')
            pp.pprint(policy[state])
            print()


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

# grid_dict=grid_dict
gd = Grid_Data(grid_dict=grid_dict)  # rows=6, cols=8)
# gd.visualize_grid()
gd.__evaluate_policy__()
gd.__find_best_policy__()


# gd.report_actions()
# gd.report_rewards()
# gd.determine_agent_step()
# gd.move_agent((1, 0))

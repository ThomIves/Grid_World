for i in range(num_acts_in_episode):
    event = episode_list[i]
    ploc = tuple(event[1])
    move = event[2]
    lloc = tuple(event[3])
    reward = event[4]
    # print('\t', ploc, move, lloc, reward)

    if ploc not in self.V_of_s.keys():
        self.V_of_s[ploc] = 0
    if lloc not in self.V_of_s.keys():
        self.V_of_s[lloc] = 0
    self.V_of_s[ploc] += \
        0.25 * (reward + gamma * self.V_of_s[lloc])

    if (ploc, move) not in self.Q_of_s.keys():
        self.Q_of_s[(ploc, move)] = 0
    self.Q_of_s[(ploc, move)] += \
        0.25 * (reward + gamma * self.V_of_s[lloc])

# V(s) = sum_a pi(a|s) * sum_s' sum_r p(s', r | s, a) {r + g V(s')}
# V*(s) = max_a * sum_s' sum_r p(s', r | s, a) {r + g V*(s')}
# pi*(s) = arg max_a * sum_s' sum_r p(s', r | s, a) {r + g V*(s')}

# Q(s, a) = sum_s' sum_r p(s', r | s, a) {r + g V(s')}
# Q*(s, a) = sum_s' sum_r p(s', r | s, a) {r + g max_a Q*(s', a')}
# Q*(s, a) = max_a sum_s' sum_r p(s', r | s, a) {r + g V*(s')}
# pi*(s) = arg max_a * Q*(s, a)

# print('\nValues:')
# pp.pprint(self.V_of_s)
#
# print('\nPolicies:')
# pp.pprint(self.Q_of_s)

# print()
#
# total_Q = {}
# max_Q = {}
#
# for loc in self.grid_dict['rewards'].keys():
#     total_Q[loc] = 0
#     max_Q[loc] = self.V_of_s.get(loc)
#     if max_Q[loc] is None:
#         max_Q[loc] = self.grid_dict['rewards'][loc]
#     for move in ('up', 'dn', 'lt', 'rt'):
#         if self.Q_of_s.get((loc, move)):
#             total_Q[loc] += self.Q_of_s[(loc, move)]
#         else:
#             continue
#         if self.Q_of_s[(loc, move)] >= max_Q[loc]:
#             self.max_P[loc] = move
#             max_Q[loc] = self.Q_of_s[(loc, move)]
#
# exploration_factor = 1.0  # - 0.25 * math.exp(-int(rec) * 0.2)
# for loc in self.max_P.keys():
#     if total_Q[loc] == 0:
#         self.ratio_P[loc] = 1.0
#     else:
#         self.ratio_P[loc] = exploration_factor * \
#             (total_Q[loc] - max_Q[loc]) / total_Q[loc]

# print()
# print('total_Q')
# pp.pprint(total_Q)
#
# print()
# print('Max_Q')
# pp.pprint(max_Q)
#
# print()
# print('Max_P')
# pp.pprint(self.max_P)
#
# print()
# print('Ratio_P')
# pp.pprint(self.ratio_P)
#
# print('\n')

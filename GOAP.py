from copy import deepcopy

class Goal(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get_discontentment(self):
        return self.value * self.value

class Action(object):
    def __init__(self, name, goals=None, costs=None):
        self.name = name
        self.goals = goals
        self.costs = costs

class WorldState(object):
    def __init__(self, goals, actions, costs):
        self.goals = goals
        self.actions = actions
        self.costs = costs
        self.alive = True
        self.win = False
        self.current_action = None

    def apply_action(self, action_name):
        for action in self.actions:
            if action.name == action_name:
                for action_goal in action.goals:
                    for self_goal in self.goals:
                        if action_goal.name == self_goal.name:
                            self_goal.value += action_goal.value
                            self.costs['mana'] += action.costs['mana']
                            if self.goals[0].value >= 10:
                                self.alive = False
                            if self.goals[1].value <= 0:
                                self.win = True

# https://gamedev.stackexchange.com/questions/62355/choosing-a-heuristic-function-for-rpg-characters-ai

    def discontentment(self):
        discontent = 0
        for goal in self.goals:
            discontent += goal.get_discontentment()
        return discontent

    def next_action(self):
        if not self.current_action:
            self.current_action = {'action': self.actions[0], 'index': 0}
            return self.actions[0]
        else:
            index = self.current_action['index'] + 1
            if index + 1 > len(self.actions):
                return None
            if self.costs['mana'] + self.actions[index].costs['mana'] <= 0:
                return None
            self.current_action['action'] = self.actions[index]
            self.current_action['index'] += 1
            return self.actions[index]

class App(object):
    def __init__(self):
        goals = [Goal('life', 0), Goal('damage', 10)]
        actions = [
            Action('attack', [Goal('life', 2), Goal('damage', -2)], {'mana': 0}),
            Action('defend', [Goal('life', 1), Goal('damage', 0)], {'mana': 0}),
            Action('fireball', [Goal('life', 2), Goal('damage', -4)], {'mana': -4}),
            Action('heal', [Goal('life', -4), Goal('damage', 0)], {'mana': -2})
        ]
        costs = {'mana': 10}
        self.world = WorldState(goals, actions, costs)

    def choose_action_group(self,max_depth):
        states = [[WorldState(self.world.goals, self.world.actions, self.world.costs), Action('base')]]

        best_action = None
        best_value = 10000  # infinite
        best_plan = []
        changed = True

        while states:
            current_value = states[-1][0].discontentment()
            if len(states) >= max_depth or states[-1][0].win or not states[-1][0].alive:
                if current_value < best_value:
                    best_action = states[1][1]
                    best_value = current_value
                    best_plan = [state[1].name for state in states if state[1]] + [best_value]
                states.pop()
                continue

            next_action = states[-1][0].next_action()
            if next_action:
                new_state = deepcopy(states[-1][0])
                new_state.current_action = None
                states.append([new_state, None])
                states[-1][1] = next_action
                new_state.apply_action(next_action.name)
            else:
                states.pop()

        return best_action, best_plan

    def run(self):
        limit = 0
        while self.world.alive and not self.world.win and limit < 20:
            action, plan = self.choose_action_group(8)
            self.world.apply_action(action.name)
            print('plan: ' + str(plan))
            print('action: ' + action.name)
            limit += 1
        if not self.world.alive:
            print('Dead')
        if self.world.win:
            print('Win')

if __name__ == '__main__':
    app = App()
    app.run()

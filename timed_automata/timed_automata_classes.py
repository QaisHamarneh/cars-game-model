from typing import Callable

from game_model.astar_cars_game import AstarCarsGame


class State:
    def __init__(self,
                 name: str,
                 player: int,
                 time_invariants: list[Callable[[list[int]], bool]] = None,
                 game_invariants: list[Callable[[AstarCarsGame, int], bool]] = None,
                 transitions: list = None):
        self.name = name
        self.player = player
        self.time_invariants = []
        if time_invariants is not None:
            self.time_invariants = time_invariants
        self.game_invariants = []
        if game_invariants is not None:
            self.game_invariants = game_invariants
        self.transitions = []
        if transitions is not None:
            self.transitions = transitions

    def valid(self, game: AstarCarsGame, clocks: list[int]):
        valid_time = all([invariant(clocks) for invariant in self.time_invariants])
        valid_game = all([invariant(game, self.player) for invariant in self.game_invariants])
        return valid_time and valid_game


class Transition:
    def __init__(self,
                 player: int,
                 start: State,
                 end: State,
                 reset: list[int],
                 time_guards: list[Callable[[list[int]], bool]] = None,
                 game_guards: list[Callable[[AstarCarsGame, int], bool]] = None):
        self.player = player
        self.start = start
        self.end = end
        self.reset = reset
        self.time_guards = []
        if time_guards is not None:
            self.time_guards = time_guards
        self.game_guards = []
        if game_guards is not None:
            self.game_guards = game_guards

    def enabled(self, game: AstarCarsGame, clocks: list[int]):
        time_guards_enabled = all([guard(clocks) for guard in self.time_guards])
        game_guards_enabled = all([guard(game, self.player) for guard in self.game_guards])
        new_clocks = clocks.copy()
        for clock in self.reset:
            new_clocks[clock] = 0
        end_state_valid = self.end.valid(game, new_clocks)
        return time_guards_enabled and game_guards_enabled and end_state_valid


class TimedAutomata:
    def __init__(self,
                 game: AstarCarsGame,
                 player: int,
                 states: list[State],
                 start_state: State,
                 transitions: list[Transition],
                 num_clocks: int):
        self.player = player
        self.game = game
        self.states = states
        self.start_state = start_state
        self.transitions = transitions
        self.clocks = [0.0] * num_clocks

        self.current_state = start_state

    def valid(self):
        return self.current_state.valid(self.game, self.clocks)

    def delay(self, delay):
        return [clock + delay for clock in self.clocks]

    def move(self, delay: float = None, transition:Transition = None):
        if delay is None:
            if self.current_state != transition.start:
                return False
            if not transition.enabled(self.game, self.clocks):
                return False
            for clock in transition.reset:
                self.clocks[clock] = 0
            self.current_state = transition.end
        else:
            self.clocks = self.delay(delay)
        return self.valid()


if __name__ == '__main__':
    s0 = State(0, 's0', time_invariants=[lambda l:l[0] < 5])
    s1 = State(0, 's1', time_invariants=[lambda l:l[0] > 4])

    t1 = Transition(0, s0, s1, [], time_guards=[lambda l: l[0] >= 4])
    t2 = Transition(0, s1, s0, [0])

    a = TimedAutomata(None, 0, [s0, s1], s0, [t1, t2], 1)

    print(a.current_state.name)
    print(a.clocks)
    a.move(delay=2)
    print(a.current_state.name)
    print(a.clocks)
    a.move(transition=t1)
    print(a.current_state.name)
    print(a.clocks)
    a.move(transition=t2)
    print(a.current_state.name)
    print(a.clocks)
    a.move(delay=2)
    print(a.current_state.name)
    print(a.clocks)
    a.move(transition=t1)
    print(a.current_state.name)
    print(a.clocks)
    a.move(delay=0.1)
    a.move(transition=t1)
    print(a.current_state.name)
    print(a.clocks)
    a.move(transition=t2)
    print(a.current_state.name)
    print(a.clocks)

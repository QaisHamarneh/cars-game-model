from typing import Callable


class State:
    def __init__(self,
                 name: str,
                 invariants: list = None,
                 transitions: list[Callable[[list[int]], bool]] = None):
        self.name = name
        self.invariants = []
        if invariants is not None:
            self.invariants = invariants
        self.transitions = []
        if transitions is not None:
            self.transitions = transitions

    def valid(self, clocks: list[int]):
        return all([invariant(clocks) for invariant in self.invariants])


class Transition:
    def __init__(self,
                 start: State,
                 end: State,
                 reset: list[int],
                 guards: list[Callable[[list[int]], bool]] = None):
        self.start = start
        self.end = end
        self.reset = reset
        self.guards = []
        if guards is not None:
            self.guards = guards

    def enabled(self, clocks:list[int]):
        guards_enabled = all([guard(clocks) for guard in self.guards])
        new_clocks = clocks.copy()
        for clock in self.reset:
            new_clocks[clock] = 0
        end_state_valid = self.end.valid(new_clocks)
        return guards_enabled and end_state_valid


class TimedAutomata:
    def __init__(self,
                 states: list[State],
                 start_state: State,
                 transitions: list[Transition],
                 num_clocks: int):

        self.states = states
        self.start_state = start_state
        self.transitions = transitions
        self.clocks = [0.0] * num_clocks

        self.current_state = start_state

    def valid(self):
        return self.current_state.valid(self.clocks)

    def delay(self, delay):
        return [clock + delay for clock in self.clocks]

    def move(self, delay: float = None, transition:Transition = None):
        if delay is None:
            if self.current_state != transition.start:
                return False
            if not transition.enabled(self.clocks):
                return False
            for clock in transition.reset:
                self.clocks[clock] = 0
            self.current_state = transition.end
        else:
            self.clocks = self.delay(delay)
        return self.valid()


if __name__ == '__main__':
    s0 = State('s0', invariants=[lambda l:l[0] < 5])
    s1 = State('s1', invariants=[lambda l:l[0] > 4])

    t1 = Transition(s0, s1, [], guards=[lambda l: l[0] >= 4])
    t2 = Transition(s1, s0, [0])

    a = TimedAutomata([s0, s1], s0, [t1, t2], 1)

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

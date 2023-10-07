from timed_automata.timed_automata_classes import TimedAutomata, State, Transition

from game_model.game_model import AstarCarsGame


def collision_check(player: int, game: AstarCarsGame):
    return True


def potential_collision_check(player: int, game: AstarCarsGame):
    return True


class LaneChangeController:
    def __init__(self,
                 game: AstarCarsGame,
                 player: int):
        self.game = game
        self.player = player

        self.clocks = [0]

        self.max_claim_time = 5
        self.lane_change_time = 5

        # def set_automata(self):
        self.q0 = State(self.player, "q0", game_invariants=[collision_check])
        self.q1 = State(self.player, "q1")
        self.q2 = State(self.player, "q2",
                        game_invariants=[potential_collision_check],
                        time_invariants=[lambda l: l[0] <= self.max_claim_time])
        self.q3 = State(self.player, "q3",
                        time_invariants=[lambda l: l[0] <= self.lane_change_time])

        self.t1 = Transition()


        # automata = TimedAutomata()



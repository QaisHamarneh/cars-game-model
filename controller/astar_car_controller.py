from controller.helper_functions import astar_heuristic, reconstruct_path
from game_model.astar_cars_game import AstarCarsGame
from game_model.road_network import LaneSegment, CrossingSegment, Segment


class AstarCarController:
    def __init__(self, game: AstarCarsGame, player: int):
        self.game = game
        self.player = player

        self.car = self.game.cars[player]
        self.goal = self.game.goals[player]

    def get_action(self) -> int:
        actions = {"turn": 0, "accelerate": 1}
        if isinstance(self.car.res[-1]["seg"], CrossingSegment):
            next_segment = self.astar()
            next_direction = self.car.direction
            for direction, segment in self.car.res[-1]["seg"].connected_segments.items():
                if next_segment == segment:
                    next_direction = direction
            dir_diff = (next_direction.value - self.car.res[-1]["dir"].value) % 4
            if dir_diff == 3:
                dir_diff = 2
            actions["turn"] = dir_diff

        return actions

    def astar(self) -> Segment:
        start_seg = self.car.res[-1]["seg"]
        goal_seg = self.goal.lane_segment
        # Initialize the open list with the start node and a cost of 0
        open_list = [(0, start_seg)]
        # Initialize the came_from dictionary to track the path
        came_from: dict[Segment, Segment] = {}
        # Initialize the g_score dictionary to store the cost from start to each node
        g_score = {node: float('inf') for node in self.game.segments}
        g_score[start_seg] = 0
        # Initialize the f_score dictionary to store the total estimated cost from start to goal
        f_score = {node: float('inf') for node in self.game.segments}
        f_score[start_seg] = astar_heuristic(start_seg, goal_seg)  # Replace with your heuristic function

        while open_list:
            _, current_seg = open_list.pop(0)

            if current_seg == goal_seg:
                return reconstruct_path(came_from, current_seg)[1]

            neighbors = []
            match current_seg:
                case LaneSegment():
                    neighbors = [current_seg.end_crossing] if current_seg.end_crossing is not None else []
                case CrossingSegment():
                    neighbors = [seg for seg in
                                 current_seg.connected_segments.values()
                                 if seg is not None]

            for neighbor in neighbors:
                tentative_g_score = g_score[current_seg] + current_seg.length

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current_seg
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + astar_heuristic(neighbor, goal_seg)
                    open_list.append((f_score[neighbor], neighbor))

        return None  # No path found

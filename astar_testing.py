import heapq

from constants import BLOCK_SIZE
from game_model.helper_functions import dist
from game_model.road_network import Road, LaneSegment, CrossingSegment, Point, Segment


def astar_heuristic(current_seg: Segment, goal_seg: LaneSegment):
    midlane = BLOCK_SIZE // 2
    match current_seg:
        case LaneSegment():
            if goal_seg.lane.road.horizontal:
                if current_seg.lane.road.horizontal:
                    return dist(Point(current_seg.end, current_seg.lane.top),
                                Point(goal_seg.begin, goal_seg.lane.top))
                else:
                    return dist(Point(current_seg.lane.top, current_seg.end),
                                Point(goal_seg.begin, goal_seg.lane.top))
            else:
                if current_seg.lane.road.horizontal:
                    return dist(Point(current_seg.end, current_seg.lane.top),
                                Point(goal_seg.lane.top, goal_seg.begin))
                else:
                    return dist(Point(current_seg.lane.top, current_seg.end),
                                Point(goal_seg.lane.top, goal_seg.begin))
        case CrossingSegment():
            if goal_seg.lane.road.horizontal:
                return dist(Point(current_seg.horiz_lane.top + midlane, current_seg.vert_lane.top + midlane),
                            Point(goal_seg.begin, goal_seg.lane.top))
            else:
                return dist(Point(current_seg.horiz_lane.top + midlane, current_seg.vert_lane.top + midlane),
                            Point(goal_seg.lane.top, goal_seg.begin))


def astar(segments: list[Road], start_seg: Segment, goal_seg: LaneSegment):
    # Initialize the open list with the start node and a cost of 0
    open_list = [(0, start_seg)]
    # Initialize the came_from dictionary to track the path
    came_from = {}
    # Initialize the g_score dictionary to store the cost from start to each node
    g_score = {node: float('inf') for node in segments}
    g_score[start_seg] = 0
    # Initialize the f_score dictionary to store the total estimated cost from start to goal
    f_score = {node: float('inf') for node in segments}
    f_score[start_seg] = astar_heuristic(start_seg, goal_seg)  # Replace with your heuristic function

    while open_list:
        _, current_seg = open_list.pop(0)

        if current_seg == goal_seg:
            return reconstruct_path(came_from, current_seg)

        neighbors = []
        match current_seg:
            case LaneSegment():
                neighbors = [current_seg.end_crossing] if current_seg.end_crossing is not None else []
            case CrossingSegment():
                neighbors = [seg for seg in [current_seg.right, current_seg.left, current_seg.up, current_seg.down]
                             if seg is not None]

        for neighbor in neighbors:
            tentative_g_score = g_score[current_seg] + current_seg.length

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current_seg
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + astar_heuristic(neighbor, goal_seg)
                open_list.append((f_score[neighbor], neighbor))

    return None  # No path found


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.insert(0, current)
    return path


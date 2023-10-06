import pyglet
from pyglet import shapes

from constants import *
from game_model.road_network import Direction, Point, direction_axis, LaneSegment, horiz_direction


def _draw_dash_line(start, end, width=LANE_DISPLACEMENT, color=WHITE, dash=20):
    lines = []
    # Vertical
    if start.x == end.x:
        length = end.y - start.y
        steps = length // dash
        step_length = length / steps
        for i in range(steps):
            if i % 2 == 0:
                lines.append(shapes.Line(start.x, start.y + i * step_length,
                                         start.x, start.y + (i + 1) * step_length,
                                         width, color=color))

    # Horizontal
    elif start.y == end.y:
        length = end.x - start.x
        steps = length // dash
        step_length = length / steps
        for i in range(steps):
            if i % 2 == 0:
                lines.append(shapes.Line(start.x + i * step_length, start.y,
                                         start.x + (i + 1) * step_length, start.y,
                                         width, color=color))
    return lines


def _draw_arrow(begin, end, horizontal, direction, tip=BLOCK_SIZE / 4, width=LANE_DISPLACEMENT, color=WHITE):
    lines = []
    if horizontal:
        lines.append(shapes.Line(begin.x, begin.y,
                                 end.x, end.y,
                                 width, color=color))
        if direction == Direction.RIGHT:
            lines.append(shapes.Line(end.x, end.y,
                                     end.x - tip, end.y - tip,
                                     width, color=color))
            lines.append(shapes.Line(end.x, end.y,
                                     end.x - tip, end.y + tip,
                                     width, color=color))
        if direction == Direction.LEFT:
            lines.append(shapes.Line(begin.x, begin.y,
                                     begin.x + tip, begin.y - tip,
                                     width, color=color))
            lines.append(shapes.Line(begin.x, begin.y,
                                     begin.x + tip, begin.y + tip,
                                     width, color=color))
    else:
        lines.append(shapes.Line(begin.x, begin.y,
                                 end.x, end.y,
                                 width, color=color))
        if direction == Direction.UP:
            lines.append(shapes.Line(end.x, end.y,
                                     end.x - tip, end.y - tip,
                                     width, color=color))
            lines.append(shapes.Line(end.x, end.y,
                                     end.x + tip, end.y - tip,
                                     width, color=color))
        if direction == Direction.DOWN:
            lines.append(shapes.Line(begin.x, begin.y,
                                     begin.x - tip, begin.y + tip,
                                     width, color=color))
            lines.append(shapes.Line(begin.x, begin.y,
                                     begin.x + tip, begin.y + tip,
                                     width, color=color))
    return lines


class AstarCarsWindow(pyglet.window.Window):
    def __init__(self, game, controllers, eval_games, manual=False):
        super().__init__()
        self.set_size(WINDOW_SIZE, WINDOW_SIZE)
        self.set_minimum_size(WINDOW_SIZE, WINDOW_SIZE)
        self.game = game
        self.controllers = controllers
        self.eval_games = eval_games
        self.frames_count = 0
        self.manual = manual

        self.gameover = [False] * self.game.players
        self.pause = False
        self.scores = [0] * self.game.players
        self.n_games_eval = 0
        self.n_games = 0
        # self.old_positions: list[Point] = [car.pos for car in self.game.cars]

        self.road_shapes = []
        self.goal_shapes = []
        self.car_shapes = []

        for road in self.game.roads:
            self._draw_road(road)
        for road in self.game.roads:
            self._draw_lane_lines(road)

        self.event_loop = pyglet.app.EventLoop()
        pyglet.app.run(1 / FRAME_RATE)

    def on_draw(self):
        self.clear()
        if self.n_games < self.eval_games:
            if not self.pause:
                if self.frames_count == FRAME_RATE:
                    if not self.manual:
                        self._update_game()
                    else:
                        self._manual_update_game(0)
                    self.frames_count = 0
            self._update_cars()
            self._update_goals()
            background = shapes.Rectangle(x=0, y=0, width=WINDOW_SIZE, height=WINDOW_SIZE, color=PALE_GREEN)
            background.draw()
            for shape in self.road_shapes:
                shape.draw()
            for shape in self.goal_shapes:
                shape.draw()
            for shape in self.car_shapes:
                shape.draw()
        elif self.n_games < + self.eval_games:
            self.close()
            quit()
        self.frames_count += FRAME_RATE

    def _update_game(self):
        for player in range(self.game.players):
            if not self.gameover[player]:
                # self.old_positions[player] = self.game.cars[player].pos
                self.gameover[player], self.scores[player] = self.game.play_step(player,
                                                                                 self.controllers[player].get_action())

        if all(self.gameover):
            print(f"Game {self.n_games}:")
            for player in range(self.game.players):
                print(f"player {player} score {self.scores[player]}")
            self.gameover = [False] * self.game.players
            self.game.reset()
            self.n_games += 1

    def _manual_update_game(self, action_ind):
        action = [0] * self.game.n_actions
        action[action_ind] = 1
        reward, self.gameover[0], self.scores[0] = self.game.play_step(0, action)
        if self.gameover[0]:
            print(f"Game {self.n_games}:")
            for player in range(self.game.players):
                print(f"player {player} score {self.scores[player]}")

    def on_key_press(self, symbol, modifiers):
        if self.manual:
            if symbol == pyglet.window.key.RIGHT:
                self._manual_update_game(1)
            if symbol == pyglet.window.key.LEFT:
                self._manual_update_game(2)
            elif symbol == pyglet.window.key.DOWN:
                self._manual_update_game(3)
            elif symbol == pyglet.window.key.UP:
                self._manual_update_game(4)
            elif symbol == pyglet.window.key.SPACE:
                self.pause = not self.pause

    def _update_cars(self):
        self.car_shapes = []
        for player, car in enumerate(self.game.cars):
            # direction = direction_axis[car.direction]
            # pos = self.old_positions[player]
            self.car_shapes.append(shapes.Rectangle(
                x=car.pos.x, y=car.pos.y,
                # x=int(pos.x + direction[0] * (self.frames_count * car.speed) / FRAME_RATE),
                # y=int(pos.y + direction[1] * (self.frames_count * car.speed) / FRAME_RATE),
                width=car.w, height=car.h,
                color=car.color if not car.dead else DEAD_GREY))
            # self.car_shapes.append(*self._draw_dash_line(car.color,
            #                         Point(lane.top + BLOCK_SIZE, 0),
            #                         Point(lane.top + BLOCK_SIZE, WINDOW_SIZE),
            #                         width=LANE_DISPLACEMENT))

    def _update_goals(self):
        self.goal_shapes = []
        for goal in self.game.goals:
            self.goal_shapes.append(shapes.Rectangle(x=goal.pos.x, y=goal.pos.y, width=BLOCK_SIZE, height=BLOCK_SIZE,
                                                     color=goal.color))

    def _draw_road(self, road):
        if road.horizontal:
            self.road_shapes.append(shapes.Rectangle(0, road.top, WINDOW_SIZE, road.bottom - road.top,
                                                     color=ROAD_BLUE
                                                     ))
        else:
            self.road_shapes.append(shapes.Rectangle(road.top, 0, road.bottom - road.top, WINDOW_SIZE,
                                                     color=ROAD_BLUE
                                                     ))

    def _draw_lane_lines(self, road):
        for i, lane in enumerate(road.right_lanes + road.left_lanes):
            if road.horizontal:
                if i == len(road.right_lanes) - 1 and len(road.left_lanes) > 0:
                    self.road_shapes.append(shapes.Line(0, lane.top + BLOCK_SIZE,
                                                        WINDOW_SIZE, lane.top + BLOCK_SIZE,
                                                        LANE_DISPLACEMENT, color=WHITE))
                elif i < len(road.right_lanes + road.left_lanes) - 1:
                    dashed_lines = _draw_dash_line(Point(0, lane.top + BLOCK_SIZE),
                                                   Point(WINDOW_SIZE, lane.top + BLOCK_SIZE))
                    for line in dashed_lines:
                        self.road_shapes.append(line)
                arrow = _draw_arrow(Point(2 * BLOCK_SIZE, lane.top + BLOCK_SIZE / 2),
                                    Point(5 * BLOCK_SIZE, lane.top + BLOCK_SIZE / 2), True, lane.direction)
                for line in arrow:
                    self.road_shapes.append(line)
            else:
                if i == len(road.right_lanes) - 1 and len(road.left_lanes) > 0:
                    self.road_shapes.append(shapes.Line(lane.top + BLOCK_SIZE, 0,
                                                        lane.top + BLOCK_SIZE, WINDOW_SIZE,
                                                        color=WHITE))
                elif i < len(road.right_lanes + road.left_lanes) - 1:
                    dashed_lines = _draw_dash_line(Point(lane.top + BLOCK_SIZE, 0),
                                                   Point(lane.top + BLOCK_SIZE, WINDOW_SIZE))
                    for line in dashed_lines:
                        self.road_shapes.append(line)
                arrow = _draw_arrow(Point(lane.top + BLOCK_SIZE / 2, 2 * BLOCK_SIZE),
                                    Point(lane.top + BLOCK_SIZE / 2, 5 * BLOCK_SIZE), False, lane.direction)
                for line in arrow:
                    self.road_shapes.append(line)

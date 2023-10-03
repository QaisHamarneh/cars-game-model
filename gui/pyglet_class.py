import pyglet
from pyglet import shapes

from constants import *
from game_model.road_network import Direction, Point, direction_axis, LaneSegment


class CarsWindow(pyglet.window.Window):
    def __init__(self, game, agents, total_games, manual=False):
        super().__init__()
        self.set_size(WINDOW_SIZE, WINDOW_SIZE)
        self.set_minimum_size(WINDOW_SIZE, WINDOW_SIZE)
        self.game = game
        self.agents = agents
        self.total_games = total_games
        self.frames_count = 0
        self.manual = manual

        self.gameover = [False] * self.game.players
        self.pause = False
        self.scores = [0] * self.game.players
        self.n_games = 0
        self.old_positions: list[Point] = [car.pos for car in self.game.cars]

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
        if not all(self.gameover) and self.n_games < self.total_games:
            if self.frames_count == FRAME_RATE:
                if not self.manual:
                    self._update_game()
                self.frames_count = 0
            self._update_cars()
            self._update_goals()
            background = shapes.Rectangle(x=0, y=0, width=WINDOW_SIZE, height=WINDOW_SIZE, color=PALE_GREEN)
            background.draw()
            for shape in self.road_shapes:
                shape.draw()
            # for shape in self.goal_shapes:
            #     shape.draw()
            # for shape in self.car_shapes:
            #     shape.draw()
        else:
            self.game.reset()
            self.n_games += 1
        self.frames_count += 1

    def _update_game(self):
        for player in range(self.game.players):
            if not self.gameover[player]:
                self.old_positions[player] = self.game.cars[player].pos
                self.gameover[player], self.scores[player] = self.agents[player].eval()
                print(self.game.cars[player].get_segment(self.game.roads))

        if all(self.gameover):
            print(f"Game {self.n_games}:")
            for player in range(self.game.players):
                print(f"player {player} score {self.scores[player]}")

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

    def _update_cars(self):
        self.car_shapes = []
        for player, car in enumerate(self.game.cars):
            direction = direction_axis[car.direction]
            pos = self.old_positions[player]
            self.car_shapes.append(shapes.Rectangle(
                x=car.pos.x, y=car.pos.y,
                # x=int(pos.x + direction[0] * (self.frames_count * car.speed) / FRAME_RATE),
                # y=int(pos.y + direction[1] * (self.frames_count * car.speed) / FRAME_RATE),
                width=car.w, height=car.h,
                color=car.color if not car.dead else DEAD_GREY))

    def _update_goals(self):
        self.goal_shapes = []
        for goal in self.game.goals:
            self.goal_shapes.append(shapes.Rectangle(x=goal.pos.x, y=goal.pos.y, width=BLOCK_SIZE, height=BLOCK_SIZE,
                                                     color=goal.color))

    # def tick(self):
    #     self.clock.tick(SPEED)

    def _draw_road(self, road):
        if road.horizontal:
            for _, lane in enumerate(road.left_lanes + road.right_lanes):
                self.road_shapes.append(shapes.Rectangle(0, lane.top, WINDOW_SIZE, BLOCK_SIZE,
                                                         color=ROAD_BLUE
                                                         ))
                # for seg in lane.segments:
                # self.road_shapes.append(pyglet.text.Label(f"{seg}",
                #                                           font_name='Times New Roman',
                #                                           font_size=6,
                #                                           x=(seg.begin if isinstance(seg, LaneSegment) else seg.vert_lane.top) + 15,
                #                                           y=lane.top + 10,
                #                                           anchor_x='center', anchor_y='center'))
        else:
            for _, lane in enumerate(road.left_lanes + road.right_lanes):
                self.road_shapes.append(shapes.Rectangle(lane.top, 0, BLOCK_SIZE, WINDOW_SIZE,
                                                         color=ROAD_BLUE
                                                         ))
                # for seg in lane.segments:
                # self.road_shapes.append(pyglet.text.Label(f"{road.name}:{lane.num}",
                #                                           font_name='Times New Roman',
                #                                           font_size=6,
                #                                           x=lane.top + 2,
                #                                           y=(seg.begin if isinstance(seg, LaneSegment) else seg.horiz_lane.top) + 15,
                #                                           anchor_x='center', anchor_y='center'))

    def _draw_lane_lines(self, road):
        if road.horizontal:
            for i, lane in enumerate(road.left_lanes + road.right_lanes):
                if i == len(road.left_lanes) - 1 and len(road.right_lanes) > 0:
                    self.road_shapes.append(shapes.Line(0, lane.top + BLOCK_SIZE,
                                                        WINDOW_SIZE, lane.top + BLOCK_SIZE,
                                                        LANE_DISPLACEMENT, color=WHITE))
                elif i < len(road.left_lanes) + len(road.right_lanes) - 1:
                    self._draw_dash_line(WHITE, ROAD_BLUE,
                                         Point(0, lane.top + BLOCK_SIZE),
                                         Point(WINDOW_SIZE, lane.top + BLOCK_SIZE),
                                         width=LANE_DISPLACEMENT)
        else:
            for i, lane in enumerate(road.left_lanes + road.right_lanes):
                if i == len(road.left_lanes) - 1 and len(road.right_lanes) > 0:
                    self.road_shapes.append(shapes.Line(lane.top + BLOCK_SIZE, 0,
                                                        lane.top + BLOCK_SIZE,
                                                        WINDOW_SIZE, LANE_DISPLACEMENT,
                                                        color=WHITE))
                elif i < len(road.left_lanes) + len(road.right_lanes) - 1:
                    self._draw_dash_line(WHITE, ROAD_BLUE,
                                         Point(lane.top + BLOCK_SIZE, 0),
                                         Point(lane.top + BLOCK_SIZE, WINDOW_SIZE),
                                         width=LANE_DISPLACEMENT)

    def _draw_dash_line(self, color1, color2, start, end, width, dash=20):
        # Vertical
        if start.x == end.x:
            length = end.y - start.y
            steps = length // dash
            step_length = length // steps
            for i in range(steps):
                self.road_shapes.append(shapes.Line(start.x, start.y + i * step_length,
                                                    start.x, start.y + (i + 1) * step_length,
                                                    width, color=color1 if i % 2 == 0 else color2))

        # Horizontal
        elif start.y == end.y:
            length = end.x - start.x
            steps = length // dash
            step_length = length // steps
            for i in range(steps):
                self.road_shapes.append(shapes.Line(start.x + i * step_length, start.y,
                                                    start.x + (i + 1) * step_length, start.y,
                                                    width, color=color1 if i % 2 == 0 else color2))

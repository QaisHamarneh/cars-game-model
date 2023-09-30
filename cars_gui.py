import pygame
from constants import *
from helper_classes import Car, Direction, Point, Road


class CarGui:
    def __init__(self, roads:list[Road]=[]) -> None:
        pygame.init()
        self.font = pygame.font.SysFont('arial', 25)
        self.roads = roads

        self.display = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('Multi Player Snake')
        self.clock = pygame.time.Clock()

    
    def _update_ui(self, cars, foods, scores):
        self.display.fill(PALE_GREEN)
        for road in self.roads:
            self._draw_road(road)

        for road in self.roads:
            self.draw_lane_lines(road)

        for car in cars:
            self._draw_car(car)
        for i, food in enumerate(foods):
            pygame.draw.rect(self.display, food.car.color, pygame.Rect(
                food.pos.x, food.pos.y, BLOCK_SIZE, BLOCK_SIZE))
        

        text = self.font.render(
            f"High Score: {max(scores)}", True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def tick(self):
        self.clock.tick(SPEED)

    def _draw_car(self, car):
        if car.dir == Direction.RIGHT:
            pygame.draw.rect(self.display, 
                             car.color if not car.dead else DEAD_GREY, 
                             (car.pos.x , car.pos.y, car.w, car.h),
                             width=BLOCK_SIZE // 5,
                             border_bottom_right_radius=BLOCK_SIZE // 3,
                             border_top_right_radius=BLOCK_SIZE // 3
                             )
        if car.dir == Direction.DOWN:
            pygame.draw.rect(self.display, 
                             car.color if not car.dead else DEAD_GREY, 
                             (car.pos.x, car.pos.y, car.w, car.h),
                             width=BLOCK_SIZE // 5,
                             border_bottom_right_radius=BLOCK_SIZE // 3,
                             border_bottom_left_radius=BLOCK_SIZE // 3
                             )
        if car.dir == Direction.LEFT:
            pygame.draw.rect(self.display, 
                             car.color if not car.dead else DEAD_GREY, 
                             (car.pos.x, car.pos.y, car.w, car.h),
                             width=BLOCK_SIZE // 5,
                             border_bottom_left_radius=BLOCK_SIZE // 3,
                             border_top_left_radius=BLOCK_SIZE // 3
                             )
        if car.dir == Direction.UP:
            pygame.draw.rect(self.display, 
                             car.color if not car.dead else DEAD_GREY, 
                             (car.pos.x, car.pos.y, car.w, car.h),
                             width=BLOCK_SIZE // 5,
                             border_top_left_radius=BLOCK_SIZE // 3,
                             border_top_right_radius=BLOCK_SIZE // 3
                             )
        
    def _draw_road(self, road):
        if road.horizontal:
            for _, lane in enumerate(road.left_lanes + road.right_lanes):
                pygame.draw.rect(self.display, 
                                ROAD_BLUE, 
                                (0, lane.top, WINDOW_SIZE, BLOCK_SIZE)
                                )
        else:
            for _, lane in enumerate(road.left_lanes + road.right_lanes):
                pygame.draw.rect(self.display, 
                                ROAD_BLUE, 
                                (lane.top, 0, BLOCK_SIZE, WINDOW_SIZE)
                                )
    
    def draw_lane_lines(self, road):
        if road.horizontal:
            for i, lane in enumerate(road.left_lanes + road.right_lanes):
                if i == road.left - 1 and road.right > 0:
                    pygame.draw.line(self.display, WHITE, 
                                     (0, lane.top + BLOCK_SIZE), 
                                     (WINDOW_SIZE, lane.top + BLOCK_SIZE), 
                                     width=LANE_DISPLACEMENT)
                elif i < road.left + road.right - 1:
                    self._draw_dash_line(WHITE, ROAD_BLUE,
                                     Point(0, lane.top + BLOCK_SIZE), 
                                     Point(WINDOW_SIZE, lane.top + BLOCK_SIZE), 
                                     width=LANE_DISPLACEMENT)
        else:
            for i, lane in enumerate(road.left_lanes + road.right_lanes):
                if i == road.left - 1 and road.right > 0:
                    pygame.draw.line(self.display, WHITE, 
                                     (lane.top + BLOCK_SIZE, 0), 
                                     (lane.top + BLOCK_SIZE, WINDOW_SIZE), 
                                     width=LANE_DISPLACEMENT)
                elif i < road.left + road.right - 1:
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
                pygame.draw.line(self.display, color1 if i % 2 == 0 else color2, 
                                (start.x, start.y + i * step_length), 
                                (start.x, start.y + (i+1) * step_length), 
                                width=width)

        # Horizental
        elif start.y == end.y:
            length = end.x - start.x
            steps = length // dash
            step_length = length // steps
            for i in range(steps):
                pygame.draw.line(self.display, color1 if i % 2 == 0 else color2, 
                                (start.x + i * step_length, start.y), 
                                (start.x + (i+1) * step_length, start.y), 
                                width=width)
    
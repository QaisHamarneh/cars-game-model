import pygame

from direction import Direction


# rgb colors
WHITE = (255, 255, 255)
BGREEN = (0, 200, 200)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLUE3 = (0, 100, 150)

RED1 = (255, 0, 0)
RED2 = (255, 100, 0)
RED3 = (150, 100, 0)
YELLOW = (255, 170, 51)

COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
          (255, 255, 0), (255, 255, 255), (128, 0, 128)]

BLACK = (0, 0, 0)




class CarGui:
    def __init__(self, players, speed = 10, size=10, block_size=60) -> None:
        pygame.init()
        self.font = pygame.font.SysFont('arial', 25)

        self.players = players

        self.speed = speed

        self.size = size
        self.block_size = min(block_size, 800 // self.size)

        self.display = pygame.display.set_mode((self.size *self. block_size, self.size * self.block_size))
        pygame.display.set_caption('Multi Player Snake')
        self.clock = pygame.time.Clock()

    
    def _update_ui(self, cars, directions, foods, scores):
        self.display.fill(BLACK)

        for player in range(len(cars)):
            self._draw_car(cars[player], directions[player], COLORS[player])
            pygame.draw.rect(self.display, COLORS[player], pygame.Rect(
                foods[player].x * self.block_size, foods[player].y * self.block_size, self.block_size, self.block_size))

        text = self.font.render(
            f"High Score: {max(scores)}", True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def tick(self):
        self.clock.tick(self.speed)

    def _draw_car(self, car, direction, color):
        if direction == Direction.RIGHT:
            pygame.draw.rect(self.display, 
                             color, 
                             (car.x * self.block_size, car.y * self.block_size, self.block_size, self.block_size),
                             width=self.block_size // 5,
                             border_bottom_right_radius=self.block_size // 3,
                             border_top_right_radius=self.block_size // 3
                             )
        if direction == Direction.DOWN:
            pygame.draw.rect(self.display, 
                             color, 
                             (car.x * self.block_size, car.y * self.block_size, self.block_size, self.block_size),
                             width=self.block_size // 5,
                             border_bottom_right_radius=self.block_size // 3,
                             border_bottom_left_radius=self.block_size // 3
                             )
        if direction == Direction.LEFT:
            pygame.draw.rect(self.display, 
                             color, 
                             (car.x * self.block_size, car.y * self.block_size, self.block_size, self.block_size),
                             width=self.block_size // 5,
                             border_bottom_left_radius=self.block_size // 3,
                             border_top_left_radius=self.block_size // 3
                             )
        if direction == Direction.UP:
            pygame.draw.rect(self.display, 
                             color, 
                             (car.x * self.block_size, car.y * self.block_size, self.block_size, self.block_size),
                             width=self.block_size // 5,
                             border_top_left_radius=self.block_size // 3,
                             border_top_right_radius=self.block_size // 3
                             )
        
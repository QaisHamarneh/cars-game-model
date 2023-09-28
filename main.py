import pygame
from cars_agent import CarAgent
from cars_game import CarsGame


def main(players, file_name, train=0, eval=5):

    game = CarsGame(players=players)

    agents = [CarAgent(game=game, player=i, file_name=file_name) for i in range(players)]
    
    if train > 0:
        print("\n\nTraining\n\n")
        for i in range(train):
            gameover = [False] * players
            while not all(gameover):
                for player in range(players):
                    if not gameover[player]:
                        gameover[player] = agents[player].train()
            
            game.reset()

    if eval > 0:
        if train == 0:
            for player in range(players):
                agents[player].load_model()
        game.activate_gui()
        # 1. collect user input
        print("\n\nEvaluating\n\n")
        pause = False
        scores = [0] * players
        for i in range(eval):
            gameover = False
            while not gameover:
                for player in range(players):
                    if not pause:
                        done, scores[player] = agents[player].eval()

                        gameover = gameover or done

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                pause = not pause
                    
                if gameover:
                    print(f"Game {i}:")
                    for player in range(players):
                        print(f"player {player} score {scores[player]}")
            game.reset()


if __name__ == '__main__':
    players = 3
    fn = "cars_model_1"
    main(players, fn, train=0, eval=2)
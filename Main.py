from Game import Game

def main():
    game = Game()
    game.__init__()
    while game.running:
        game.update()
    game.shutdown()

if __name__ == '__main__':
    main()

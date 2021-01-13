import pygame
import numpy as np
import random
import sys
import copy


list_of_tetrominoes = [
    [[0, 0, 0, 0],
     [1, 1, 1, 1],
     [0, 0, 0, 0],
     [0, 0, 0, 0]],

    [[1, 1],
     [1, 1]],

    [[0, 1, 0],
     [1, 1, 1],
     [0, 0, 0]],

    [[0, 1, 1],
     [1, 1, 0],
     [0, 0, 0]],

    [[1, 1, 0],
     [0, 1, 1],
     [0, 0, 0]],

    [[1, 0, 0],
     [1, 1, 1],
     [0, 0, 0]],

    [[0, 0, 1],
     [1, 1, 1],
     [0, 0, 0]]
]
for i in range(len(list_of_tetrominoes)):
    list_of_tetrominoes[i] = np.array(list_of_tetrominoes[i])

width = 10
height = 12
size = 16
speed = 2

class Tetris:
    def __init__(self, offset):
        self.height = height
        self.width = width
        self.offset = offset
        self.score = 0
        self.cleared = 0
        self.canstore = True
        self.state = 'play'
        self.board = np.full((height, width), 0)
        self.matrix = self.board
        self.next_tetromino1 = random.choice(list_of_tetrominoes)
        self.next_tetromino2 = random.choice(list_of_tetrominoes)
        self.next_tetromino3 = random.choice(list_of_tetrominoes)
        self.current_tetromino = []
        self.stored_tetromino = []
        self.get_next_tetromino()

    def get_next_tetromino(self):
        self.current_tetromino = self.next_tetromino1
        self.next_tetromino1 = self.next_tetromino2
        self.next_tetromino2 = self.next_tetromino3
        self.next_tetromino3 = random.choice(list_of_tetrominoes)
        self.x = width // 2 - len(self.current_tetromino) // 2
        self.y = 0
        self.draw_matrix()


    def store_piece(self):
        if self.canstore:
            self.canstore = False
            if len(self.stored_tetromino) == 0:
                self.stored_tetromino = self.current_tetromino
                self.current_tetromino = self.next_tetromino1
                self.next_tetromino1 = self.next_tetromino2
                self.next_tetromino2 = self.next_tetromino3
                self.next_tetromino3 = random.choice(list_of_tetrominoes)
            else:
                (self.stored_tetromino, self.current_tetromino) = self.current_tetromino, self.stored_tetromino
            if not self.valid_space():
                (self.stored_tetromino, self.current_tetromino) = self.current_tetromino, self.stored_tetromino
                self.canstore = True

    def move(self, direction):
        self.x += direction
        if not self.valid_space():
            self.x -= direction

    def normal_drop(self):
        self.y += 1
        if not self.valid_space():
            self.y -= 1
            self.lock_pos()

    def force_drop(self):
        while self.valid_space():
            self.y += 1
        self.y -= 1

    def rotate(self, rotation):
        self.current_tetromino = np.rot90(self.current_tetromino, rotation)
        if not self.valid_space():
            self.current_tetromino = np.rot90(self.current_tetromino, -rotation)

    def valid_space(self):
        for i in range(len(self.current_tetromino)):
            for j in range(len(self.current_tetromino[i])):
                if self.current_tetromino[i][j] == 1:
                    if i + self.y > self.height - 1 or \
                            j + self.x < 0 or \
                            j + self.x > self.width - 1 or \
                            self.board[i + self.y][j + self.x] == 1:
                        return False
        self.draw_matrix()
        return True

    def lock_pos(self):
        for i in range(len(self.current_tetromino)):
            for j in range(len(self.current_tetromino[i])):
                if self.current_tetromino[i][j] == 1:
                    self.board[i + self.y][j + self.x] = self.current_tetromino[i][j]
        self.clear_line()
        self.get_next_tetromino()
        self.draw_matrix()
        if not self.valid_space():
            print(1)
            self.state = 'gameover'
        self.canstore = True

    def clear_line(self):
        cleared_lines = 0
        for i in range(height):
            if sum(self.board[i]) == width:
                cleared_lines += 1
                for l in range(i, 1, -1):
                    for j in range(width):
                        self.board[l][j] = self.board[l - 1][j]
        self.cleared = cleared_lines
        self.score += cleared_lines ** 2

    def draw_matrix(self):
        self.matrix = self.board.copy()
        for i in range(len(self.current_tetromino)):
            for j in range(len(self.current_tetromino[i])):
                if self.current_tetromino[i][j] == 1:
                    self.matrix[i + self.y][j + self.x] = self.current_tetromino[i][j]

    def add_junk(self, junk):
        for i in range(junk):
            if 1 in self.board[i]:
                self.state = 'gameover'
                return
        for i in range(height - junk):
            self.board[i] = self.board[i + junk]
        junk_line = np.full(self.width, 1)
        junk_line[random.randint(0, self.width-1)] = 0
        for i in range(junk):
            self.board[self.height - 1 - i] = junk_line


pygame.init()
Field = pygame.display.set_mode(((width + 4) * size * 2, height * size))
Field.fill((255, 255, 255))

# Game Variables
done = False
game1 = Tetris(0)
game2 = Tetris((width + 4) * size)
pressing_down1 = False
pressing_down2 = False
clock = pygame.time.Clock()
fps = 20
counter = 0

while not done:
    counter += 1
    if counter > 10000:
        counter = 0

    # Game Keys
    if counter % (fps) == 0 or pressing_down1:
        if game1.state == 'play':
            game1.normal_drop()

    if counter % (fps) == 0 or pressing_down2:
        if game2.state == 'play':
            game2.normal_drop()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                game1.rotate(1)
            if event.key == pygame.K_e:
                game1.rotate(-1)
            if event.key == pygame.K_s:
                pressing_down1 = True
            if event.key == pygame.K_a:
                game1.move(-1)
            if event.key == pygame.K_d:
                game1.move(1)
            if event.key == pygame.K_w:
                game1.store_piece()
            if event.key == pygame.K_SPACE:
                game1.force_drop()

            if event.key == pygame.K_u:
                game2.rotate(1)
            if event.key == pygame.K_o:
                game2.rotate(-1)
            if event.key == pygame.K_k:
                pressing_down2 = True
            if event.key == pygame.K_j:
                game2.move(-1)
            if event.key == pygame.K_l:
                game2.move(1)
            if event.key == pygame.K_i:
                game2.store_piece()
            if event.key == pygame.K_SPACE:
                game2.force_drop()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                pressing_down1 = False
            if event.key == pygame.K_k:
                pressing_down2 = False

    # Draw Game Board
    Field.fill((255, 255, 255))
    for i in range(height):
        for j in range(width):
            pygame.draw.rect(Field, (255, 255, 255), (j * size, i * size, size, size))
            pygame.draw.rect(Field, (255, 255, 255), (j * size + game2.offset, i * size, size, size))
            if game1.board[i][j] == 1:
                pygame.draw.rect(Field, (0, 0, 0), (j * size, i * size, size, size))
            if game2.board[i][j] == 1:
                pygame.draw.rect(Field, (0, 0, 0), (j * size + game2.offset, i * size, size, size))

    # Draw Current, Next and Stored Pieces
    if game1.current_tetromino is not None:
        if game1.valid_space():
            for i in range(len(game1.current_tetromino)):
                for j in range(len(game1.current_tetromino[0])):
                    if game1.current_tetromino[i][j] == 1:
                        pygame.draw.rect(Field, (128, 128, 128,), ((game1.x + j) * size,
                                                                   (game1.y + i) * size, size, size))

    if game2.current_tetromino is not None:
        if game2.valid_space():
            for i in range(len(game2.current_tetromino)):
                for j in range(len(game2.current_tetromino[0])):
                    if game2.current_tetromino[i][j] == 1:
                        pygame.draw.rect(Field, (128, 128, 128,), ((game2.x + j) * size + game2.offset,
                                                                   (game2.y + i) * size, size, size))

    if game1.next_tetromino1 is not None:
        for i in range(len(game1.next_tetromino1)):
            for j in range(len(game1.next_tetromino1[0])):
                if game1.next_tetromino1[i][j] == 1:
                    pygame.draw.rect(Field, (0, 0, 0), (((width + j) * size),
                                                        ((4 + i) * size), size, size))

    if game2.next_tetromino1 is not None:
        for i in range(len(game2.next_tetromino1)):
            for j in range(len(game2.next_tetromino1[0])):
                if game2.next_tetromino1[i][j] == 1:
                    pygame.draw.rect(Field, (0, 0, 0), (((width + j) * size + game2.offset),
                                                        ((4 + i) * size), size, size))

    if game1.next_tetromino2 is not None:
        for i in range(len(game1.next_tetromino2)):
            for j in range(len(game1.next_tetromino2[0])):
                if game1.next_tetromino2[i][j] == 1:
                    pygame.draw.rect(Field, (0, 0, 0), (((width + j) * size),
                                                        ((8 + i) * size), size, size))

    if game2.next_tetromino2 is not None:
        for i in range(len(game2.next_tetromino2)):
            for j in range(len(game2.next_tetromino2[0])):
                if game2.next_tetromino2[i][j] == 1:
                    pygame.draw.rect(Field, (0, 0, 0), (((width + j) * size + game2.offset),
                                                        ((8 + i) * size), size, size))

    if game1.next_tetromino3 is not None:
        for i in range(len(game1.next_tetromino3)):
            for j in range(len(game1.next_tetromino3[0])):
                if game1.next_tetromino3[i][j] == 1:
                    pygame.draw.rect(Field, (0, 0, 0), (((width + j) * size),
                                                        ((12 + i) * size), size, size))

    if game2.next_tetromino3 is not None:
        for i in range(len(game2.next_tetromino3)):
            for j in range(len(game2.next_tetromino3[0])):
                if game2.next_tetromino3[i][j] == 1:
                    pygame.draw.rect(Field, (0, 0, 0), (((width + j) * size + game2.offset),
                                                        ((12 + i) * size), size, size))

    if game1.stored_tetromino is not None:
        for i in range(len(game1.stored_tetromino)):
            for j in range(len(game1.stored_tetromino[0])):
                if game1.stored_tetromino[i][j] == 1:
                    pygame.draw.rect(Field, (0, 0, 0), (((width + j) * size),
                                                        (size * i), size, size))

    if game2.stored_tetromino is not None:
        for i in range(len(game2.stored_tetromino)):
            for j in range(len(game2.stored_tetromino[0])):
                if game2.stored_tetromino[i][j] == 1:
                    pygame.draw.rect(Field, (0, 0, 0), (((width + j) * size + game2.offset),
                                                        (size * i), size, size))

    if game1.cleared > 1:
        game2.add_junk(game1.cleared - 1)
        game1.cleared = 0

    if game2.cleared > 1:
        game1.add_junk(game2.cleared - 1)
        game2.cleared = 0

    if game1.state == 'gameover':
        print('2 won')
        done = False
        game1 = Tetris(0)
        game2 = Tetris((width + 4) * size)
        pressing_down1 = False
        pressing_down2 = False

    if game2.state == 'gameover':
        print('1 won')
        done = False
        game1 = Tetris(0)
        game2 = Tetris((width + 4) * size)
        pressing_down1 = False
        pressing_down2 = False

    pygame.display.flip()
    clock.tick(fps)

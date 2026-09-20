# Implement game logic, game setting.
# Vẽ tile, vẽ bàn chơi.
import random
import pygame
from collections import deque
from game_settings import *

# Các loại tile type
# "." = unknown
# "X" -> mìn
# "C" -> số
# "/" -> rỗng

class Tile:
    def __init__(self, x, y, image, type, revealed = False, flagged = False):
        self.x, self.y = x * TILESIZE, y * TILESIZE
        self.image = image
        self.type = type
        self.revealed = revealed
        self.flagged = flagged

    # Từng tile có hàm tự vẽ bản thân lên bàn chơi
    def draw(self, board_surface):
        if not self.flagged and self.revealed:
            board_surface.blit(self.image, (self.x, self.y))
        elif self.flagged and not self.revealed:
            board_surface.blit(tile_flag, (self.x, self.y))
        elif not self.revealed:
            board_surface.blit(tile_unknown, (self.x, self.y))

    def __repr__(self):
        return self.type

class Board:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.width = self.rows * TILESIZE
        self.height = self.cols * TILESIZE
        
        self.board_surface = pygame.Surface((self.width, self.height))                                                         # Bàn chơi chính là một surface của pygame, sẽ được vẽ lên screen.
        self.board_list = [[Tile(row, col, tile_empty, ".") for col in range(self.cols)] for row in range(self.rows)]          # List để quản lý data của từng tile
        self.place_mines()
        self.place_clues()
        self.dug = []

    # Dựa trên setting số mìn để loop chọn ra tọa độ random để đặt mìn.
    def place_mines(self):
        max_mines = (self.rows * self.cols) - 1
        actual_mines = min(self.mines, max_mines)
        count = 0
        while count < actual_mines:
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.cols - 1)
            if self.board_list[x][y].type == ".":
                self.board_list[x][y].type = "X"
                self.board_list[x][y].image = tile_mine
                count += 1

    # Tile nào không phải mìn sẽ được đặt số.
    def place_clues(self):
        for x in range(self.rows):
            for y in range(self.cols):
                if self.board_list[x][y].type != "X":
                    # check_neighbours(x, y) để check số mìn xung quanh tile đó
                    total_mines = self.check_neighbours(x, y)
                    if total_mines > 0:
                        self.board_list[x][y].image = tile_numbers[total_mines-1]
                        self.board_list[x][y].type = "C"


    # Check out of bounds
    def is_inside(self, x, y):
        return 0 <= x < self.rows and 0 <= y < self.cols

    # Dùng offset để duyệt qua 8 tile xung quanh tile đang xét để đếm số mìn lân cận
    def check_neighbours(self, x, y):
        total_mines = 0
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                neighbour_x = x + x_offset
                neighbour_y = y + y_offset
                if self.is_inside(neighbour_x, neighbour_y) and self.board_list[neighbour_x][neighbour_y].type == "X":
                    total_mines += 1
        return total_mines


    def draw(self, screen):
        for row in self.board_list:
            for tile in row:
                # Duyệt qua từng tile trên bàn chơi, tile chạy hàm draw() để vẽ bản thân lên vị trí tọa độ đó
                tile.draw(self.board_surface)
        # Sau khi vẽ xong toàn bộ tile lên board, dán board lên màn hình game
        screen.blit(self.board_surface, (0, 0))

    # Logic để thực hiện tính năng loang khi click vào một ô empty.
    def dig(self, x, y):
        # List để lưu lại những ô đã đào được.
        self.dug.append((x, y))

        if self.board_list[x][y].type == "X":
            self.board_list[x][y].revealed = True
            self.board_list[x][y].image = tile_exploded
            return False
        elif self.board_list[x][y].type == "C":
            self.board_list[x][y].revealed = True
            return True

        self.board_list[x][y].revealed = True

        # Duyệt qua những ô xung quanh ô đã đào, thực hiện đệ quy để tiếp tục đào.
        for row in range(max(0, x-1), min(self.rows-1, x+1) + 1):
            for col in range(max(0, y-1), min(self.cols-1, y+1) + 1):
                if (row, col) not in self.dug:
                    self.dig(row, col)
        return True

    def display_board(self):
        for row in self.board_list:
            print(row)
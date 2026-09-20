# Quản lý game state và event handler.
import pygame
import sys
from game_settings import *
from sprites import *

class Button:
    def __init__(self, x, y, width, height, text, bg_color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color

    # Hàm vẽ nút lên screen
    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
        text_surf = FONT_MEDIUM.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.rows = DEFAULT_ROW_NUM
        self.cols = DEFAULT_COL_NUM
        self.mines = DEFAULT_MINE_NUM

        # Vẽ main menu
        self.screen = pygame.display.set_mode((450, 400))

    def settings_menu(self):
        self.screen = pygame.display.set_mode((450, 400))
        
        # Tạo điều chỉnh rows
        btn_row_sub = Button(250, 80, 40, 40, "-", LIGHTGREY, WHITE)
        btn_row_add = Button(370, 80, 40, 40, "+", LIGHTGREY, WHITE)
        
        # Tạo điều chỉnh cols
        btn_col_sub = Button(250, 140, 40, 40, "-", LIGHTGREY, WHITE)
        btn_col_add = Button(370, 140, 40, 40, "+", LIGHTGREY, WHITE)

        # Tạo điều chỉnh mines
        btn_mine_sub = Button(250, 200, 40, 40, "-", LIGHTGREY, WHITE)
        btn_mine_add = Button(370, 200, 40, 40, "+", LIGHTGREY, WHITE)

        # Nút start
        btn_start = Button(125, 300, 200, 50, "PLAY GAME", GREEN, WHITE)

        in_menu = True
        while in_menu:
            self.clock.tick(FPS)
            self.screen.fill(BGCOLOUR)

            # Vẽ các chữ và dán lên screen
            title_surf = FONT_LARGE.render("GAME SETTINGS", True, WHITE)
            self.screen.blit(title_surf, title_surf.get_rect(center=(225, 35)))

            row_txt = FONT_MEDIUM.render(f"Rows: {self.rows}", True, WHITE)
            col_txt = FONT_MEDIUM.render(f"Cols: {self.cols}", True, WHITE)
            mine_txt = FONT_MEDIUM.render(f"Mines: {self.mines}", True, WHITE)

            self.screen.blit(row_txt, (40, 85))
            self.screen.blit(col_txt, (40, 145))
            self.screen.blit(mine_txt, (40, 205))

            # Vẽ các nút
            btn_row_sub.draw(self.screen)
            btn_row_add.draw(self.screen)
            btn_col_sub.draw(self.screen)
            btn_col_add.draw(self.screen)
            btn_mine_sub.draw(self.screen)
            btn_mine_add.draw(self.screen)
            btn_start.draw(self.screen)

            pygame.display.flip()

            # Event handler cho main menu screen.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Xử lý tín hiệu khi player click vào button
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos

                    if btn_row_sub.is_clicked(pos):
                        self.rows = max(5, self.rows - 1)
                    elif btn_row_add.is_clicked(pos):
                        self.rows = min(30, self.rows + 1)

                    if btn_col_sub.is_clicked(pos):
                        self.cols = max(5, self.cols - 1)
                    elif btn_col_add.is_clicked(pos):
                        self.cols = min(30, self.cols + 1)

                    max_allowed_mines = (self.rows * self.cols) - 1
                    self.mines = min(self.mines, max_allowed_mines)

                    if btn_mine_sub.is_clicked(pos):
                        self.mines = max(1, self.mines - 1)
                    elif btn_mine_add.is_clicked(pos):
                        self.mines = min(max_allowed_mines, self.mines + 1)

                    if btn_start.is_clicked(pos):
                        in_menu = False

    # Khi bắt đầu màn chơi, căn chỉnh màn hình lại tỉ lệ phù hợp với board size đã chọn.
    def new(self):
        width = self.rows * TILESIZE
        height = self.cols * TILESIZE
        self.screen = pygame.display.set_mode((width, height))
        self.board = Board(self.rows, self.cols, self.mines)

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.draw()
        self.end_screen()

    def draw(self):
        self.screen.fill(BGCOLOUR)
        self.board.draw(self.screen)
        pygame.display.flip()

    def check_win(self):
        for row in self.board.board_list:
            for tile in row:
                if tile.type != "X" and not tile.revealed:
                    return False
        return True

    # Event handler cho phần gameplay chính
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Chia để lấy phần nguyên cho phần tọa độ chuột đã click vào để game register
            # Giúp game register chính xác tile mà player đã click.
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                mx //= TILESIZE
                my //= TILESIZE

                if 0 <= mx < self.rows and 0 <= my < self.cols:
                    if event.button == 1:  # Nút chuột trái, hành động đào tile.
                        # Nếu ô đã flagged, ko cho đào
                        if not self.board.board_list[mx][my].flagged:
                            # Nếu dig trả về False (game over), thực hiện reveal kết quả toàn bộ bàn chơi
                            if not self.board.dig(mx, my):
                                for row in self.board.board_list:
                                    for tile in row:
                                        if tile.flagged and tile.type != "X":
                                            tile.flagged = False
                                            tile.revealed = True
                                            tile.image = tile_not_mine
                                        elif tile.type == "X":
                                            tile.revealed = True
                                self.playing = False

                    elif event.button == 3:  # Nút chuột phải
                        if not self.board.board_list[mx][my].revealed:
                            # flagged = not flagged để mỗi lần click để toggle đặt cờ.
                            self.board.board_list[mx][my].flagged = not self.board.board_list[mx][my].flagged

                    
                    if self.check_win():
                        self.playing = False
                        for row in self.board.board_list:
                            for tile in row:
                                if not tile.revealed:
                                    tile.flagged = True

    def end_screen(self):
        """Màn hình kết thúc ván chơi - click chuột để về menu cài đặt"""
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False


game = Game()
while True:
    game.settings_menu()
    game.new()
    game.run()
import tkinter as tk
import random
import os

WIDTH, HEIGHT = 400, 600
PLAYER_SIZE = 25
PLATFORM_WIDTH, PLATFORM_HEIGHT = 60, 10
GRAVITY = 0.4
JUMP_VELOCITY = -10
SCROLL_THRESHOLD = HEIGHT // 2
STAR_SIZE = 20
OBSTACLE_SIZE = 20
FIELD_HEIGHT = HEIGHT * 50
PLATFORM_STEP_Y = 80
PLAYER_IMAGE = "doctor.png"

class Game:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#00004d")
        self.canvas.pack()

        self.root.title("Доктор Прыгун")

        self.use_image = os.path.exists(PLAYER_IMAGE)
        if self.use_image:
            self.doctor_img = tk.PhotoImage(file=PLAYER_IMAGE)

        self.platforms = []
        self.stars = []
        self.obstacles = []

        self.player = {'x': WIDTH // 2, 'y': HEIGHT - 100, 'vy': JUMP_VELOCITY, 'vx': 0, 'id': None}
        self.score = 0
        self.running = True

        self.canvas.bind_all("<KeyPress-Left>", self.move_left)
        self.canvas.bind_all("<KeyPress-Right>", self.move_right)
        self.canvas.bind_all("<KeyRelease-Left>", self.stop_move)
        self.canvas.bind_all("<KeyRelease-Right>", self.stop_move)

        self.init_game()

    def move_left(self, e):
        self.player['vx'] = -5

    def move_right(self, e):
        self.player['vx'] = 5

    def stop_move(self, e):
        self.player['vx'] = 0

    def init_game(self):
        self.canvas.delete("all")
        self.platforms.clear()
        self.stars.clear()
        self.obstacles.clear()
        self.score = 0
        self.running = True

        x0 = WIDTH // 2
        y0 = HEIGHT - 100
        if self.use_image:
            self.player['id'] = self.canvas.create_image(x0, y0, image=self.doctor_img, anchor="nw")
        else:
            self.player['id'] = self.canvas.create_oval(x0, y0, x0 + PLAYER_SIZE, y0 + PLAYER_SIZE, fill="white")
        self.player['x'], self.player['y'], self.player['vy'] = x0, y0, JUMP_VELOCITY

        start_plat = self.canvas.create_rectangle(
            x0 - PLATFORM_WIDTH // 2, y0 + 10,
            x0 + PLATFORM_WIDTH // 2, y0 + 10 + PLATFORM_HEIGHT,
            fill='brown'
        )
        self.platforms.append(start_plat)

        start_y = y0 + 50
        for i in range(1, FIELD_HEIGHT // PLATFORM_STEP_Y):
            y = start_y - i * PLATFORM_STEP_Y
            x = random.randint(0, WIDTH - PLATFORM_WIDTH)
            plat = self.canvas.create_rectangle(x, y, x + PLATFORM_WIDTH, y + PLATFORM_HEIGHT, fill='brown')
            self.platforms.append(plat)

            obj_x = x + 20
            obj_y = y - 25
            r = random.random()
            if r < 0.4:
                self.spawn_star(obj_x, obj_y)
            elif r < 0.7:
                self.spawn_obstacle(obj_x, obj_y)

        self.update_game()

    def spawn_star(self, x, y):
        star = self.canvas.create_oval(x, y, x + STAR_SIZE, y + STAR_SIZE, fill='yellow')
        self.stars.append(star)

    def spawn_obstacle(self, x, y):
        l1 = self.canvas.create_line(x, y, x + OBSTACLE_SIZE, y + OBSTACLE_SIZE, fill='red', width=2)
        l2 = self.canvas.create_line(x + OBSTACLE_SIZE, y, x, y + OBSTACLE_SIZE, fill='red', width=2)
        self.obstacles.append((l1, l2))

    def update_game(self):
        if not self.running:
            return

        p = self.player
        old_y = p['y']
        p['x'] += p['vx']
        p['vy'] += GRAVITY
        p['y'] += p['vy']

        if p['x'] < -PLAYER_SIZE:
            p['x'] = WIDTH
        elif p['x'] > WIDTH:
            p['x'] = -PLAYER_SIZE

        if self.use_image:
            self.canvas.coords(p['id'], p['x'], p['y'])
        else:
            self.canvas.coords(p['id'], p['x'], p['y'], p['x'] + PLAYER_SIZE, p['y'] + PLAYER_SIZE)

        for plat in self.platforms:
            x1, y1, x2, y2 = self.canvas.coords(plat)
            if (p['vy'] > 0 and
                p['x'] + PLAYER_SIZE > x1 and p['x'] < x2 and
                old_y + PLAYER_SIZE <= y1 and p['y'] + PLAYER_SIZE > y1):
                p['y'] = y1 - PLAYER_SIZE
                p['vy'] = JUMP_VELOCITY

        if p['y'] < SCROLL_THRESHOLD:
            dy = SCROLL_THRESHOLD - p['y']
            p['y'] = SCROLL_THRESHOLD
            for plat in self.platforms:
                self.canvas.move(plat, 0, dy)
            for star in self.stars:
                self.canvas.move(star, 0, dy)
            for obs in self.obstacles:
                self.canvas.move(obs[0], 0, dy)
                self.canvas.move(obs[1], 0, dy)

        for star in list(self.stars):
            x1, y1, x2, y2 = self.canvas.coords(star)
            if not (p['x'] + PLAYER_SIZE < x1 or p['x'] > x2 or
                    p['y'] + PLAYER_SIZE < y1 or p['y'] > y2):
                self.canvas.delete(star)
                self.stars.remove(star)
                self.score += 1

        for l1, l2 in self.obstacles:
            coords = self.canvas.coords(l1)
            if len(coords) == 4:
                obs_left = min(coords[0], coords[2])
                obs_right = max(coords[0], coords[2])
                obs_top = min(coords[1], coords[3])
                obs_bottom = max(coords[1], coords[3])
                if (obs_right > p['x'] and obs_left < p['x'] + PLAYER_SIZE and
                    obs_bottom > p['y'] and obs_top < p['y'] + PLAYER_SIZE):
                    self.game_over()
                    return

        if p['y'] > HEIGHT:
            self.game_over()
            return

        self.canvas.delete("score")
        self.canvas.create_text(60, 20, text=f"Лекарства: {self.score}",
                                font=('Arial', 14), tag="score", fill="white")

        self.root.after(20, self.update_game)

    def game_over(self):
        self.running = False
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text="GAME OVER",
                                font=('Arial', 24), fill="red")
        self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 40, text="Нажмите R для рестарта",
                                font=('Arial', 14), fill="white")
        self.root.bind("<KeyPress-r>", self.restart_game)
        self.root.bind("<KeyPress-R>", self.restart_game)

    def restart_game(self, event=None):
        self.root.unbind("<KeyPress-r>")
        self.root.unbind("<KeyPress-R>")
        self.init_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()

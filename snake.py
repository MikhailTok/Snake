from tkinter import *
import time
import random


class Game(Tk):
    play = False

    def __init__(self):
        super().__init__()
        self.title('Snake')

        self.frames = [Main(self), Play(self)]
        self.frames[0].grid(row=1, column=0, columnspan=2)

        main = Button(self, text='Main', command=self.open_main)
        main.grid(row=0, column=0)

        game = Button(self, text='Game', command=self.open_game)
        game.grid(row=0, column=1)

    def open_main(self):
        self.hide_all()
        self.frames[0].grid(row=1, column=0, columnspan=2)

    def open_game(self):
        self.hide_all()
        self.frames[1].grid(row=1, column=0, columnspan=2)

    def hide_all(self):
        for frame in self.frames:
            frame.grid_forget()


class Main(Frame):
    def __init__(self, master):
        super().__init__(master)

        dev = Label(self, text='In development, press Game')
        dev.pack()
        self.config(bg='red')


class Play(Frame):
    score = 0
    collision_happened = False
    difficulties_option = (0.1, 0.04, 0.02)

    def __init__(self, master):
        super().__init__(master)
        self.canvas_width = 300
        self.canvas_height = 300

        self.score_label = Label(self, width=15, height=1, text='Score - 0')
        self.score_label.grid(row=1, column=1)

        self.canvas = Canvas(self, width=self.canvas_width, height=self.canvas_height)
        self.canvas.grid(row=2, column=0, columnspan=3)

        self.button_start = Button(self, text='Start', command=self.play)
        self.button_start.grid(row=0, column=0)

        button_pause = Button(self, text='Pause', command=self.pause)
        button_pause.grid(row=0, column=1)

        button_restart = Button(self, text='Restart', command=self.restart)
        button_restart.grid(row=0, column=2)

        difficulties = [('Beginner', 0), ('Middle', 1), ('Expert', 2)]

        self.dif = IntVar()
        pos = 0
        for text, dc in difficulties:
            d = Radiobutton(self, text=text, variable=self.dif, value=dc)
            d.grid(row=3, column=pos)
            pos += 1

        self.snake = Snake(self.canvas, self.canvas_width, self.canvas_height)
        self.food = Food(self.canvas, self.canvas_width, self.canvas_height)
        self.create_grid()

    def create_grid(self):
        for i in range(10, self.canvas_height, 10):
            self.canvas.create_line(0, i, self.canvas_width, i)

        for j in range(10, self.canvas_width, 10):
            self.canvas.create_line(j, 0, j, self.canvas_height)

    def play(self):
        Game.play = True

    def pause(self):
        Game.play = False

    def restart(self):
        Game.play = False
        del self.snake
        del self.food
        self.canvas.delete("all")
        self.create_grid()
        self.score = 0
        self.score_label['text'] = 'Score - 0'
        self.button_start.config(state='normal')

        self.snake = Snake(self.canvas, self.canvas_width, self.canvas_height)
        self.food = Food(self.canvas, self.canvas_width, self.canvas_height)


class Box:
    size = 5

    def __init__(self, canvas, xc, yc, color='green'):
        self.xc = xc
        self.yc = yc
        self.canvas = canvas
        self.id = self.canvas.create_rectangle(self.xc - Box.size, self.yc - Box.size,
                                               self.xc + Box.size, self.yc + Box.size,
                                               fill=color)

    def get_xc_yc(self):
        pos = self.canvas.coords(self.id)
        pos_x = (pos[0] + pos[2]) / 2
        pos_y = (pos[1] + pos[3]) / 2
        return pos_x, pos_y


class Snake(Box):
    def __init__(self, canvas, width, height):
        super().__init__(canvas=canvas, xc=5, yc=5, color='blue')

        self.width = width
        self.height = height

        self.canvas.bind_all('<Up>', self.up)
        self.canvas.bind_all('<Down>', self.down)
        self.canvas.bind_all('<Right>', self.right)
        self.canvas.bind_all('<Left>', self.left)
        self.direction = [-10, 0]

        self.tail = [Box(self.canvas, 5, 5, color='green') for _ in range(3)]
        self.move()

        self.coord = None

    def move(self):
        self.canvas.move(self.id, 50, 50)
        span = 60
        for i in self.tail:
            self.canvas.move(i.id, span, 50)
            span += 10

    def run(self):
        self.coord = [tuple(self.canvas.coords(self.id))]
        self.canvas.move(self.id, *self.direction)

        pos_x, pos_y = self.get_xc_yc()

        if pos_x < 0:
            self.canvas.move(self.id, self.width, 0)
        if pos_x > self.width:
            self.canvas.move(self.id, -self.width, 0)
        if pos_y < 0:
            self.canvas.move(self.id, 0, self.height)
        if pos_y > self.height:
            self.canvas.move(self.id, 0, -self.height)

        for i in self.tail:
            self.coord.append(tuple(self.canvas.coords(i.id)))

        for j in range(len(self.tail)):
            self.canvas.coords(self.tail[j].id, *self.coord[j])

        return pos_x, pos_y

    def eat(self):
        x, y = self.tail[-1].get_xc_yc()
        self.tail.append(Box(self.canvas, x + 2 * Box.size, y))
        self.coord.append(tuple(self.canvas.coords(self.tail[-1].id)))
        return self.coord

    def up(self, event):
        if self.direction[1] != 10:
            self.direction = [0, -10]

    def down(self, event):
        if self.direction[1] != -10:
            self.direction = [0, 10]

    def left(self, event):
        if self.direction[0] != 10:
            self.direction = [-10, 0]

    def right(self, event):
        if self.direction[0] != -10:
            self.direction = [10, 0]

    def check_collision(self):
        if self.coord[0] in self.coord[1:]:
            return True
        else:
            return False


class Food(Box):
    def __init__(self, canvas, width, height):
        super().__init__(canvas=canvas, xc=5, yc=5, color='yellow')
        self.canvas.move(self.id, 20, 20)
        field = []
        for i in range(0, height, 10):
            for j in range(0, width, 10):
                field.append((i, j))
        self.field = set(field)

    def get_random_place(self, occupied_position):
        occupied_field = set([x[:-2] for x in occupied_position])
        possible_position = list(self.field - occupied_field)
        chosen_position = random.choice(possible_position)
        self.canvas.coords(self.id, *chosen_position, chosen_position[0] + 10, chosen_position[1] + 10)


game = Game()

while True:
    if Game.play:
        head_x_y = game.frames[1].snake.run()
        if game.frames[1].snake.check_collision():
            Game.play = False
            game.frames[1].button_start.config(state=DISABLED)

        if game.frames[1].food.get_xc_yc() == head_x_y:
            occupied_by_snake = game.frames[1].snake.eat()
            game.frames[1].score += 1
            game.frames[1].score_label['text'] = f'Score - {game.frames[1].score}'
            game.frames[1].food.get_random_place(occupied_by_snake)
        game.update_idletasks()
        game.update()
        time.sleep(difficult)
    else:
        difficult = game.frames[1].difficulties_option[game.frames[1].dif.get()]
        game.update_idletasks()
        game.update()

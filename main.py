import random
from random import randint


#  создаем класс точки
class Dot:
    #  принимает x и y
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #  сравнивает x и y (a.__eq__(s))
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot{self.x}, {self.y}"


#  создаем необходимые исключения

# общий класс, который содержащий в себе все классы исключений
class GeneralClassException(Exception):
    pass


# если пользователь выстрелил за границу поля
class BoardOutException(GeneralClassException):
    def __str__(self):
        return "За границы выходить нельзя"


# если пользователь повторно стреляет в клетку
class BoardUserException(GeneralClassException):
    def __str__(self):
        return "В эту клетку вы уже стреляли"


# для размещения кораюлей
class BoardWrongShipException(GeneralClassException):
    pass


# создаем класс корабля

class Ship:
    def __init__(self, bow, l, o):  # ориентация корабля
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    #  точки корабля
    @property
    def dots(self):
        ship_dots = []  # в списке точки корабля
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:  # вертикальный
                cur_x += i

            elif self.o == 1:  # горизонтальный
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


#  создаем игровое поле
class Play_Board:
    def __init__(self, hid=False, size=6):  # скрытие поля и его размер
        #  размер поля
        self.size = size
        #  скрытие поля
        self.hid = hid
        # количество пораженных кораблей
        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"  # игровая доска
        for i, row in enumerate(self.field):  # проходимся по строкам доски
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("●", "O")
        return res

    # находится ли точка за пределами игрового поля
    def out_board(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    #  местоположение (чтобы во время убийства корабля вокруг появлялись точки)
    def contour(self, ship, verb=False):
        #  точка, в которой мы находимся
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for dot_x, dot_y in near:
                cur = Dot(dot.x + dot_x, dot.y + dot_y)
                if not (self.out_board(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "-"
                    self.busy.append(cur)

    #  размещение кораблей на доске пользователя
    def add_ship(self, ship):
        for d in ship.dots:
            #  не выходит за границы и не занята
            if self.out_board(d) or d in self.busy:
                raise BoardWrongShipException
        for d in ship.dots:
            self.field[d.x][d.y] = "●"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    #  выстрел человека
    def shot(self, d):
        if self.out_board(d):
            #  если точка за границей поля
            raise BoardOutException()
        #  если точка занята
        if d in self.busy:
            raise BoardUserException()

        self.busy.append(d)

        #  распознаем, ранен корабль или убит и вокруг корабля выделяем зону
        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "-"
        print("Промах!")
        return False

    def begin(self):
        self.busy = []


#  создаем класс игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    #  просим игроков сделать выстрел
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except GeneralClassException as e:
                print(e)


#  создаем класс ИИ (компьютер)
class Computer(Player):
    def ask(self):
        #  компьютер рандомно принимает две координаты
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Компьютер ходит: {d.x + 1} {d.y + 1}")
        return d


#  создаем класс пользователь (игрок-человек)
class Computer_User(Player):
    def ask(self):
        while True:
            #  просим игрока ввести координаты выстрела
            coordinats = input("Твой ход, человек: ").split()
            #  если ввел не две координаты
            if len(coordinats) != 2:
                print("Нужно ввести две координаты.")
                continue

            x, y = coordinats
            #  если ввел не числа
            if not (x.isdigit()) or not (y.isdigit()):
                print("Нужно ввести числа.")
                continue

            x, y = int(x), int(y)
            #  вычитается единица, так как индексация с нуля
            return Dot(x - 1, y - 1)


#  создаем игру
class Game:
    def __init__(self, size=6):
        self.size = size
        #  две доски для игрока и компьютера
        player_board = self.random_board()
        computer_board = self.random_board()
        #  скрытие доски игрока для компьютера
        computer_board.hid = True

        self.computer = Computer(computer_board, player_board)
        self.player = Computer_User(player_board, computer_board)

    def try_board(self):
        #  разновидности кораблей
        ships_list = [3, 2, 2, 1, 1, 1, 1]
        #  игровая доска
        board = Play_Board(size=self.size)
        #  попытки создания поля
        attempts = 0
        #  пробуем расставить все корабли по полю
        for l in ships_list:
            while True:
                attempts += 1
                #  если попыток больше 2000
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # постоянное создание поля
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    #  начало игры
    def hello_user(self):
        print("Привет, человек!\n"
              "Добро пожаловать в игру Морской бой!\n"
              "Введи строку и столбец")

    #  поля в начале игры
    def _boards(self):
        print("-" * 27)
        print("Доска игрока:")
        print(self.player.board)
        print("-" * 27)
        print("Доска компьютера:")
        print(self.computer.board)
        print("-" * 27)

    #  поля во время игры
    def visible_boards(self):
        num = 0
        while True:
            self._boards()
            if num % 2 == 0:
                print("Ходит человек.")
                repeat = self.player.move()
            else:
                print("Ходит компьютер.")
                repeat = self.computer.move()
            if repeat:
                num -= 1

            if self.computer.board.count == 7:
                self._boards()
                print("-" * 27)
                print("Выиграл человек.")
                break

            if self.player.board.count == 7:
                print("-" * 27)
                print("Выиграл компьютер.")
                break
            num += 1

    #  старт игры
    #  приветствие
    #  вывод игровых полей
    def start_game(self):
        self.hello_user()
        self.visible_boards()


g = Game()
g.start_game()
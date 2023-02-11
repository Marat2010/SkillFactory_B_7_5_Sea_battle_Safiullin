"""
Игра Морской бой
Дополнено следующее:
1. Вывод досок горизонтально.
2. Красивые значки и вид таблицы. Возможность расширения доски.
3. Выбор большого(10х10) и малого поля(6х6).
4. Два режима игры, обычное и с подсказками(поддавки).
5. Отдельный модуль "tools" для рисования досок.
6. Отображение расположение кораблей после проигрыша.
7. Ввод координат без пробела (только от 1 до 9). Для ввода
    на большом поле "10" вводить через пробел два числа.
    ...
Доски отображаются только в момент хода игрока, т.е. после хода компьютера
 доска не показывается. Потому введена "self.ai.board.result_text" для
  передачи информации предыдущего хода компьютера при ранении.
"""

# Для корректного отображения в windows (мерцания значков при победе),
#  необходимо установить colorama: "pip install colorama" и раскомментировать
#   две строки ниже:
# from colorama import init
# init(autoreset=True)

from random import randint
from tools import Table
from BoardException import *


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    PIC_SHIP = "🚢"
    PIC_FIRE = "🔥"
    BLINK = '\033[5m'
    RESET = '\033[0m'
    PIC_FIRE_BLINK = BLINK + "🔥" + RESET
    PIC_FAIL = " ☄ "
    PIC_BLANK = " " * 3

    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.giveaway = False
        self.count = 0
        self.busy = []
        self.ships = []
        self.field = [[self.PIC_BLANK] * size for _ in range(size)]
        self.result_text = ''  # Для сохранения хода компьютера.

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = self.PIC_SHIP
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = self.PIC_FAIL
                    self.busy.append(cur)

    def __str__(self):
        cs = []
        for i in self.field:
            cs += i

        tab = Table(cs, self.size)
        res = tab.show_fields()

        if self.hid:
            if self.giveaway:
                res = res.replace(self.PIC_SHIP, " .")
            else:
                res = res.replace(self.PIC_SHIP, "  ")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = self.PIC_FIRE
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    self.result_text = f"({d.x + 1} {d.y + 1}) - Корабль уничтожен!"
                    return False
                else:
                    self.result_text = f"({d.x + 1} {d.y + 1}) - Корабль ранен!"
                    return True

        self.field[d.x][d.y] = self.PIC_FAIL
        self.result_text = f"({d.x + 1} {d.y + 1}) - Мимо!"
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):

    def ask(self):
        # Желательно сделать проверку, чтобы при ранении добивал корабль.
        while True:
            d = Dot(randint(0, 5), randint(0, 5))
            if d not in self.enemy.busy:  # проверка пробитых точек
                break
        return d


class User(Player):
    def ask(self):
        while True:
            s = input("\n     Ваш ход: ")
            if len(s) == 2:
                x, y = s[0], s[1]
            else:
                cords = s.split()

                if len(cords) != 2:
                    print(" Введите 2 координаты! ")
                    continue

                x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6, big_game=False, giveaway=False):
        self.size = size  # размер поля (доски)
        self.lens = [3, 2, 2, 1, 1, 1, 1]  # корабли
        if big_game:
            self.lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]  # корабли
        pl = self.random_board()  # доска игрока
        co = self.random_board()  # доска компьютера
        co.hid = True  # спрятать корабли
        self.giveaway = giveaway  # показать места кораблей (поддавки)

        self.ai = AI(co, pl)  # игрок компьютер
        self.us = User(pl, co)  # игрок

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
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

    @staticmethod
    def greet():
        print()
        print("     ┌───────────────────────────────────────┐")
        print("     │ Приветствуем вас в игре `Морской бой` │")
        print("     ├───────────────────────────────────────┤")
        print("     │ формат ввода: x y (можно без пробела) │")
        print("     │  x - номер строки, y - номер столбца  │")
        print("     └───────────────────────────────────────┘", end='')

    def loop(self):
        num = 0
        s = ''
        repeat_ai = False

        self.ai.board.giveaway = self.giveaway

        while True:
            tables_str = Table.join_tables(self.ai.board.__str__(), self.us.board.__str__())

            if num % 2 == 0:
                print("\n " + '_' * 80 + "\n")
                print(" " * 10, "Доска компьютера:", " " * 30, "Ваши корабли:")
                print(tables_str)

                if repeat_ai:
                    print(s)
                    repeat_ai = False

                s = " " * 5 + f"Вы: {self.ai.board.result_text}"
                print(f"{s:<50}" + f"Компьютер: {self.us.board.result_text}")

                repeat = self.us.move()
            else:
                repeat = self.ai.move()
                if repeat:
                    repeat_ai = True
                    s = f"{' ':<50}" + f"Компьютер: {self.us.board.result_text}"

            if repeat:
                num -= 1
            if self.ai.board.count == len(self.lens):
                str_ai = self.ai.board.__str__()
                str_ai = str_ai.replace(Board.PIC_FIRE, Board.PIC_FIRE_BLINK)
                tables_str = Table.join_tables(str_ai, self.us.board.__str__())
                print(tables_str)
                s = " " * 5 + f"Вы: {self.ai.board.result_text}"
                print(f"{s:<50}" + f"Компьютер: {self.us.board.result_text}\n")
                print(Board.BLINK + "     *** Вы выиграли! ***\n" + Board.RESET)
                break

            if self.us.board.count == len(self.lens):
                self.ai.board.hid = False
                str_us = self.us.board.__str__()
                str_us = str_us.replace(Board.PIC_FIRE, Board.PIC_FIRE_BLINK)
                tables_str = Table.join_tables(self.ai.board.__str__(), str_us)
                print(tables_str)
                print(f"{s:<50}" + f"Компьютер: {self.us.board.result_text}\n")
                print(" " * 50 + Board.BLINK + "* Компьютер выиграл! *\n" + Board.RESET)
                break

            num += 1

    def start(self):
        self.greet()
        self.loop()


if __name__ == '__main__':
    Game.greet()
    print("\n\n     Чтобы оставить по умолчанию нажмите Enter")
    b_game = input("\n     Играть на большом поле? (по умолчанию НЕТ)\n"
                   "      (для изменения введите любой символ): ")
    give_away = input("\n     Играть в поддавки? (по умолчанию НЕТ)\n"
                      "      (для изменения введите любой символ): ")
    print("\n\n     Если не корректно отображаются доски, \n"
          "        особенно при 'Большой игре', \n"
          "     расширьте окно терминала(консоли) ")
    if b_game:
        g = Game(10, big_game=True, giveaway=give_away)
    else:
        g = Game(6, big_game=False, giveaway=give_away)

    g.start()

class Table:
    """
    Класс для формирования таблиц из списка элементов.
    Таблицы формируются в виде str, готовые для печати в консоли.
    Объединение таблиц для расположения по горизонтали.
    Количество таблиц возможно любое, определяется в зависимости
    от количества переданного в списке.
    """

    INDENT = 8  # Расстояние между таблицами

    def __init__(self, cells, size=6):
        self.size = size
        self.cells = cells

    @staticmethod
    def gen_row_cells(cells: list, size=6) -> list:
        """
        Генератор для последовательной выдачи значений ячейки
         в зависимости от размера таблицы, т.е. выдача строки.

        :param cells: список для помещения в таблицу.
        :param size: размер таблицы (6х6).
        :return: список для одной строки.
        """

        # Дополняем список клеток пустыми значениями, если не полный:
        cells_copy = cells + [' ' * 3] * (size ** 2 - len(cells))
        while True:
            row = cells_copy[:size]
            yield row
            cells_copy = cells_copy[size:]
            if not len(cells_copy):
                break

    def show_fields(self) -> str:
        """
        Показ таблицы, формирует длинную строку с "\n" для дальнейшей печати ее.
        :return: Общая строка для печати.
        """

        table_string = '\nx👇\y👉'
        for i in range(1, self.size + 1):
            table_string += f'{i:^5}'
        table_string += '\n'

        top = (' ' * 6 + '┌' + '────┬' * (self.size - 1) + '────┐\n' + f' {1:=3}  ')
        data_row = ('│' + '{:>2} ') * self.size
        middle_row = ('│\n' + ' ' * 6 + '├' + '────┼' * (self.size - 1) + '────┤\n' + ' {:=3}  ')
        bottom = ('│\n' + ' ' * 6 + '└' + '────┴' * (self.size - 1) + '────┘\n')

        lst = [top, ]
        for s in range(self.size - 1):
            lst.append(data_row)
            lst.append(middle_row.format(s + 2))
        lst.append(data_row)
        lst.append(bottom)

        gen_row = iter(self.gen_row_cells(self.cells, self.size))

        for i, s in enumerate(lst):
            if i % 2:  # Строки (нечетные) куда необходимо подставить значения из списка free_cells
                s = s.format(*next(gen_row))
            table_string += s

        return table_string

    @staticmethod
    def join_tables(*tables) -> str:
        """
        Метод для объединения нескольких таблиц горизонтально в одну строку.
        :param tables: список таблиц (таблица в виде строки), может быть 2, 3 ...
        :return: Общая строка для печати.
        """

        lst_tables = []
        for tab in tables:
            lst_tables.append(tab.split('\n'))
        new_str = ''
        for st in zip(*lst_tables):  # Объединение по строкам нескольких таблиц.
            for i in st:
                new_str += i + " " * Table.INDENT
            new_str += '\n'

        return new_str




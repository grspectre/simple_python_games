from tkinter import *
from tkinter import ttk
from collections import OrderedDict


class AppData:
    __value = 0

    @staticmethod
    def init():
        AppData.__value = 0

    @staticmethod
    def get_value():
        value = AppData.__value
        if value == 0:
            AppData.__value = 1
        else:
            AppData.__value = 0
        return value


class TkTicTacToe:

    __width__ = 3
    __height__ = 3

    def __init__(self):
        """
        Конструктор. Инициализируем TK, создаём кнопки и игровое поле.
        """
        self.game_ended = False

        self.root = Tk()
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid()

        self.subframe_text = ttk.Frame(self.frame, padding=10)
        self.subframe_text.grid(column=0, row=0)
        self.subframe_field = ttk.Frame(self.frame, padding=10)
        self.subframe_field.grid(column=0, row=1)

        ttk.Button(self.subframe_text, text="Новая игра", command=self.init_game).grid(column=0, row=0)
        ttk.Button(self.subframe_text, text="Выход", command=self.root.destroy).grid(column=1, row=0)

        self.elements = []
        for idx1 in range(self.__width__):
            row = []
            for idx2 in range(self.__height__):
                pos = (idx1, idx2)
                element = FieldElement(self.subframe_field, pos)
                element.grid(row=idx1, column=idx2)
                element.bind('<Button-1>', self.click)
                row.append(element)
            self.elements.append(row)

        self.root.mainloop()

    def init_game(self):
        """
        Инициализируем новую игру.
        :return:
        """
        for idx1 in range(self.__width__):
            for idx2 in range(self.__height__):
                self.elements[idx1][idx2].init()
        self.game_ended = False
        AppData.init()

    def end_game(self, positions):
        """
        Завершаем игру, показываем выигрышную комбинацию.
        :param positions: Координаты выигрышной комбинации.
        :return:
        """
        for idx1 in range(self.__width__):
            for idx2 in range(self.__height__):
                self.elements[idx1][idx2].end_game(positions)

    def click(self, event):
        """
        Обработчик клика на элементе поля.
        :param event: MousePress
        :return:
        """
        if event.widget.get_value() is not None or self.game_ended:
            return
        value = AppData.get_value()
        event.widget.set_value(value)
        self.check_field(event.widget.get_position())

    def check_field(self, position):
        """
        Проверяем выигрышные комбинации от последней выбранной позиции.
        :param position: tuple
        :return:
        """
        field = []
        for x, element_row in enumerate(self.elements):
            row = []
            for y, element in enumerate(element_row):
                row.append(element.get_value())
            field.append(row)
        positions = check_field(field, (self.__width__, self.__height__), position)
        if positions is not None:
            self.end_game(positions)
            self.game_ended = True


class FieldElement(ttk.Label):

    def __init__(self, parent, position):
        """
        Конструктор. Инициализация элемента игрового поля.
        :param parent: Элемент интерфейса, в котором находится.
        :param position: Позиция на игровом поле.
        """
        self.game_position = position
        self.game_value = None
        super().__init__(parent, text='-', cursor='hand2', padding=10)

    def set_value(self, value):
        """
        Установить значение элемента. O или 1.
        :param value: int
        :return:
        """
        if value not in (0, 1):
            raise ValueError('Value must be 0 or 1')
        self.game_value = value
        if self.game_value == 1:
            self.configure(text='X')
        if self.game_value == 0:
            self.configure(text='O')
        self.configure(cursor='arrow')

    def get_value(self):
        """
        Возвращает значение поля.
        :return: int|None
        """
        return self.game_value

    def get_position(self):
        """
        Возвращает позицию элемента на игровом поле.
        :return: tuple
        """
        return self.game_position

    def init(self):
        """
        Инициализация поля для новой игры.
        :return:
        """
        self.configure(cursor='hand2', foreground='black', text='-')
        self.game_value = None

    def end_game(self, positions):
        """
        Завершение игры. Если элемент находится в выигрышной комбинации, то
        выделить.
        :param positions:
        :return:
        """
        self.configure(cursor='arrow')
        if self.game_position in positions:
            self.configure(foreground='green')


def check_field(field, field_dimensions, last_step, win_line_height=3):
    """
    Функция нахождения выигрышной комбинации
    :param field: list Игровое поле
    :param field_dimensions: tuple Размер поля
    :param last_step: tuple Координаты последнего хода
    :param win_line_height: Сколько одинаковых элементов в выигрышной комбинации
    :return: list|None
    """
    multipliers = (((1, 0), (-1, 0)), ((0, 1), (0, -1)), ((1, 1), (-1, -1)), ((1, -1), (-1, 1)))
    value = field[last_step[0]][last_step[1]]
    last_x, last_y = last_step
    output = {}

    # Алгоритм простой: берём текущий сделанный ход и проверяем, нет ли
    # выигрышной комбинации на поле по четырём направлениям: две прямые и
    # две диагонали.
    for idx in range(win_line_height):
        for idx_line, coordinates in enumerate(multipliers):
            for coordinate in coordinates:
                x, y = coordinate
                cur_x = last_x + x * idx
                cur_y = last_y + y * idx
                width, height = field_dimensions
                if cur_x < 0 or cur_y < 0 or cur_x >= width or cur_y >= height:
                    continue
                if idx_line not in output:
                    output[idx_line] = OrderedDict()
                current_value = field[cur_x][cur_y]
                output[idx_line][(cur_x, cur_y)] = current_value

    # Сортируем по ключу, чтобы шло по порядку, и ищем первое вхождение
    # выигрышной серии.
    for _, items in output.items():
        ordered_dict = {key: items[key] for key in sorted(items)}
        wining_coordinates = []
        for coordinate, dict_value in ordered_dict.items():
            if dict_value is not None and dict_value == value:
                wining_coordinates.append(coordinate)
            else:
                wining_coordinates = []
            if len(wining_coordinates) == win_line_height:
                return wining_coordinates
    # Иначе возвращаем None
    return None


def main():
    TkTicTacToe()


if __name__ == '__main__':
    main()

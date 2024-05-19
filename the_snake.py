"""
Игра "Змейка" - учебный проект.

Когорта: 43_python_plus.
Выполнил: Александр Мясоед.
Telegram: @Aleksandr_Myasoеd
"""
import pygame as pg
from typing import Tuple, Optional, List
from abc import abstractmethod
from random import randint

# Константы для размеров поля и сетки.
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# Типы для координат и цветов.
COORDINATE = Tuple[int, int]
COLOR = Tuple[int, int, int]

# Направления движения.
UP: COORDINATE = (0, -1)
DOWN: COORDINATE = (0, 1)
LEFT: COORDINATE = (-1, 0)
RIGHT: COORDINATE = (1, 0)

# Цвет фона - черный.
BOARD_BACKGROUND_COLOR: COLOR = (0, 0, 0)

# Цвет объекта по умолчанию.
DEFAULT_COLOR: COLOR = (255, 255, 255)

# Цвет границы ячейки.
BORDER_COLOR: COLOR = (93, 216, 228)

# Цвет яблока.
APPLE_COLOR: COLOR = (255, 0, 0)

# Цвет змейки.
SNAKE_COLOR: COLOR = (0, 255, 0)

# Скорость движения змейки.
SPEED: int = 20

# Настройка игрового окна.
screen: pg.Surface = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени.
clock: pg.time.Clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position: COORDINATE = (0, 0),
                 body_color: COLOR = DEFAULT_COLOR) -> None:
        """
        Инициализация игрового объекта.

        Args:
            position (COORDINATE): Позиция объекта на игровом поле.
            body_color (COLOR): Цвет объекта в формате RGB.
        """
        self.position = position
        self.body_color = body_color

    @abstractmethod
    def draw(self) -> None:
        """Отрисовка игрового объекта."""
        raise NotImplementedError(
            "Метод draw() должен быть переопределен в дочерних классах"
        )


def handle_keys(snake) -> bool:
    """Обработка пользовательского ввода."""
    direction_mapping = {
        pg.K_UP: UP,
        pg.K_DOWN: DOWN,
        pg.K_LEFT: LEFT,
        pg.K_RIGHT: RIGHT,
    }
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                snake.paused = not snake.paused
            elif event.key == pg.K_x:
                if snake.game_over is True:
                    snake.game_over = not snake.game_over
                    snake.reset()
            new_direction = direction_mapping.get(event.key, None)
            if new_direction and (
                (snake.direction == UP and new_direction != DOWN)
                or (snake.direction == DOWN and new_direction != UP)
                or (snake.direction == LEFT and new_direction != RIGHT)
                or (snake.direction == RIGHT and new_direction != LEFT)
            ):
                snake.next_direction = new_direction

    return True


class Snake(GameObject):
    """Класс, описывающий змейку."""

    def __init__(self) -> None:
        """Инициализация змейки."""
        super().__init__((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), SNAKE_COLOR)
        self.speed: int = SPEED
        self.paused: bool = False
        self.game_over: bool = False
        self.direction: COORDINATE = RIGHT
        self.next_direction: Optional[COORDINATE] = None
        self.length: int = 1
        self.positions: List[COORDINATE] = [self.position]
        self.last: Optional[COORDINATE] = None

    def update_direction(self) -> None:
        """Обновление направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> COORDINATE:
        """Вычисление новой позиции Змейки."""
        self.update_direction()
        x, y = self.position
        dx, dy = self.direction
        new_x = (x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (y + dy * GRID_SIZE) % SCREEN_HEIGHT
        next_position = (new_x, new_y)
        return next_position

    def insert_next_position(self, next_position: COORDINATE) -> None:
        """Вставить новую позицию в тело Змейки."""
        self.position = next_position
        self.positions.insert(0, self.position)

    def del_last_segment(self) -> None:
        """Последний сегмент змейки удалить из списка позиций positions."""
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def get_length(self) -> int:
        """Вычислить длину Змейки."""
        return len(self.positions)

    def reset(self) -> None:
        """Сброс змейки в начальное состояние."""
        self.length = 1
        self.speed = 20
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None

    def get_head_position(self) -> COORDINATE:
        """Получить позицию головы змейки."""
        return self.positions[0]

    def is_game_over(self, next_position: COORDINATE) -> None:
        """Проверка, что змейка не врезалась в свой хвост."""
        if next_position in self.positions[2:]:
            self.game_over = True

    def draw(self) -> None:
        """Отрисовка змейки."""
        for position in self.positions:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Затирание последнего сегмента.
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


class Apple(GameObject):
    """Класс, описывающий яблоко."""

    def __init__(self, snake_positions: List[COORDINATE] = [(0, 0)]) -> None:
        """Инициализация яблока."""
        super().__init__(position=(0, 0), body_color=APPLE_COLOR)
        self.snake_positions = snake_positions
        self.randomize_position()

    def generate_new_position(self) -> COORDINATE:
        """Функция генерирует новую случайную позицию, не занятую Змейкой."""
        while True:
            x = randint(0, GRID_WIDTH - 1)
            y = randint(0, GRID_HEIGHT - 1)
            new_position = (x * GRID_SIZE, y * GRID_SIZE)
            if new_position not in self.snake_positions:
                return new_position

    def randomize_position(self) -> None:
        """Генерация случайной позиции яблока на игровом поле."""
        self.position = self.generate_new_position()

    def draw(self) -> None:
        """Отрисовка яблока."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


def main() -> None:
    """Основная функция."""
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)
    running = True
    while running:
        clock.tick(snake.speed)
        screen.fill(BOARD_BACKGROUND_COLOR)
        running = handle_keys(snake)
        if not (snake.game_over or snake.paused):
            next_position = snake.move()
            snake.is_game_over(next_position)
            snake.insert_next_position(next_position)
            snake.del_last_segment()
            if snake.position == apple.position:
                snake.length += 1
                if snake.speed < 100:
                    snake.speed += 1
                apple.position = apple.generate_new_position()
        snake.draw()
        apple.draw()
        if snake.paused:
            pg.display.set_caption(
                f'Пауза! | Скорость: {snake.speed} | '
                f'Длина: {snake.get_length()}'
            )
        elif snake.game_over:
            pg.display.set_caption(
                f'Игра окончена! | Скорость: {snake.speed} | '
                f'Длина: {snake.get_length()} | '
                f'Нажми: x'
            )
        else:
            pg.display.set_caption(
                f'Змейка | Скорость: {snake.speed} | '
                f'Длина: {snake.get_length()}'
            )
        pg.display.update()
        clock.tick(snake.speed)
    pg.quit()


if __name__ == '__main__':
    main()

from random import choice

import pygame

import os

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Рекорд
PERSONAL_BEST = 0

# Все возможные клетки
ALL_CELLS = set((x, y) for x in range(0, SCREEN_WIDTH, GRID_SIZE)
                for y in range(0, SCREEN_HEIGHT, GRID_SIZE))

# Все напправления
DIRECTIONS = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT
}


# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый игровой объект"""

    def __init__(self, pos=None, body_color=BOARD_BACKGROUND_COLOR) -> None:
        if not pos:
            self.position = SCREEN_CENTER
        else:
            self.position = pos
        self.body_color = body_color

    def draw(self):
        """Заготовка метода draw"""
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко"""

    def __init__(self) -> None:
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, snake_cells=set()):
        """Установить яблоко в случайное место"""
        self.position = choice(tuple(ALL_CELLS.difference(snake_cells)))

    def draw(self):
        """Отрисовка яблока"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку"""

    def __init__(self) -> None:
        super().__init__(body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None

    def update_direction(self):
        """Обновление направления змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещение змейки"""
        head_position = self.get_head_position()
        new_x = (head_position[0]
                 + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_position[1]
                 + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT

        self.positions.insert(0, (new_x, new_y))
        self.last = self.positions.pop()

    def draw(self):
        """Рисование змейки"""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возврат положения головы"""
        return self.positions[0]

    def reset(self):
        """Сброс змейки"""
        self.length = 1
        self.positions = [SCREEN_CENTER]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обработка кнопок управления"""
    global SPEED

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_data()
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN,
                             pygame.K_LEFT, pygame.K_RIGHT):
                game_object.next_direction = (
                    DIRECTIONS.get((event.key, game_object.direction),
                                   game_object.direction)
                )
            elif event.key == pygame.K_ESCAPE:
                save_data()
                pygame.quit()
                raise SystemExit
            elif event.key == pygame.K_RIGHTBRACKET:
                SPEED += 1
            elif event.key == pygame.K_LEFTBRACKET:
                if SPEED > 1:
                    SPEED -= 1


def handle_collisions(apple: Apple, snake: Snake):
    """Обработка коллизий"""
    global PERSONAL_BEST
    if apple.position == snake.get_head_position():
        snake.length += 1
        PERSONAL_BEST = max(PERSONAL_BEST, snake.length)
        snake.positions.append(snake.last)
        snake.last = None
        apple.randomize_position(snake.positions)

    if snake.get_head_position() in snake.positions[1:] and snake.length > 4:
        snake.reset()
        apple.randomize_position()
        screen.fill(BOARD_BACKGROUND_COLOR)


def update_caption():
    """Обновление заголовка"""
    global SPEED
    global PERSONAL_BEST
    pygame.display.set_caption(
        f'Змейка. Скорость (менять на []): {SPEED}. Рекорд: {PERSONAL_BEST}')


def load_data():
    """Загрузить данные о персональном рекорде"""
    global PERSONAL_BEST
    if os.path.exists('personal_best.txt'):
        with open('personal_best.txt', 'r') as f:
            PERSONAL_BEST = int(f.readline())


def save_data():
    """Загрузить данные о персональном рекорде"""
    global PERSONAL_BEST
    with open('personal_best.txt', 'w') as f:
        f.write(str(PERSONAL_BEST))


def main():
    """Главный алгоритм"""
    # Инициализация PyGame:
    pygame.init()
    # Создание экземпляров классов.
    snake = Snake()
    apple = Apple()
    load_data()
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        update_caption()
        snake.update_direction()
        snake.move()

        handle_collisions(apple, snake)

        snake.draw()
        apple.draw()

        pygame.display.update()


if __name__ == '__main__':
    main()

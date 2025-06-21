import pygame
import random
import sys
import os
import math

# 初始化
pygame.init()
WIDTH, HEIGHT = 800, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NK的大便大冒险")

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 215, 0)

# 游戏参数
GROUND_HEIGHT = HEIGHT - 50
GRAVITY = 1
JUMP_STRENGTH = 18
GAME_SPEED = 8
POOP_SPEED_VARIATION = 3  # 大便速度变化范围


# 自定义图片加载
def load_image(name, size):
    """加载图片并自动处理路径问题"""
    try:
        image = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(image, size)
    except:
        print(f"警告：无法加载图片 {name}，将使用方块代替")
        surface = pygame.Surface(size, pygame.SRCALPHA)
        if "dabian" in name:
            # 绘制简易大便
            pygame.draw.ellipse(surface, BROWN, (0, 0, size[0], size[1] * 0.8))
            pygame.draw.circle(surface, YELLOW, (size[0] // 2, size[1] // 3), size[0] // 6)
        else:
            # 绘制NK替代方块
            pygame.draw.rect(surface, (0, 120, 255), (0, 0, size[0], size[1]))
            pygame.draw.circle(surface, (255, 200, 0), (size[0] // 2, size[1] // 3), size[0] // 4)
        return surface


# 加载角色图片 - 使用你提供的文件名
NK_IMG = load_image("NK.png", (60, 60))  # 正常状态
NK_JUMP_IMG = load_image("NK_jump.png", (60, 60)) if os.path.exists("NK_jump.png") else NK_IMG
NK_DUCK_IMG = load_image("NK_duck.png", (80, 40)) if os.path.exists("NK_duck.png") else NK_IMG

# 加载大便图片
DABIAN_IMG = load_image("dabian.png", (60, 60))

# 游戏背景音乐（可选）
try:
    pygame.mixer.music.load("background.mp3")
    pygame.mixer.music.play(-1)  # 循环播放
except:
    print("背景音乐加载失败，继续无声游戏")


# NK角色类
class NK:
    def __init__(self):
        self.width = 60
        self.height = 60
        self.x = 50
        self.y = GROUND_HEIGHT - self.height
        self.jump_velocity = 0
        self.is_jumping = False
        self.ducking = False
        self.sliding = False  # 滑行状态（踩到大便）
        self.slide_timer = 0

    def jump(self):
        if not self.is_jumping:
            self.jump_velocity = -JUMP_STRENGTH
            self.is_jumping = True

    def duck(self):
        self.ducking = True
        self.height = 40
        self.y = GROUND_HEIGHT - self.height

    def stand(self):
        self.ducking = False
        self.height = 60
        self.y = GROUND_HEIGHT - self.height

    def slide(self):
        """踩到大便后滑行"""
        self.sliding = True
        self.slide_timer = 30  # 滑行30帧

    def update(self):
        # 滑行状态处理
        if self.sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.sliding = False
            # 滑行时降低高度
            self.height = 30
            self.y = GROUND_HEIGHT - self.height

        # 跳跃物理
        if self.is_jumping:
            self.y += self.jump_velocity
            self.jump_velocity += GRAVITY

            if self.y >= GROUND_HEIGHT - self.height:
                self.y = GROUND_HEIGHT - self.height
                self.is_jumping = False

    def draw(self):
        if self.sliding:
            # 滑行动画
            rotated_img = pygame.transform.rotate(NK_IMG, 30)  # 倾斜30度
            screen.blit(rotated_img, (self.x, self.y))
        elif self.is_jumping:
            screen.blit(NK_JUMP_IMG, (self.x, self.y))
        elif self.ducking:
            screen.blit(NK_DUCK_IMG, (self.x, self.y + 20))
        else:
            screen.blit(NK_IMG, (self.x, self.y))

        # 绘制滑行痕迹
        if self.sliding:
            for i in range(5):
                offset = random.randint(-5, 5)
                pygame.draw.circle(screen, BROWN,
                                   (self.x - i * 10 + offset, GROUND_HEIGHT + 5),
                                   random.randint(2, 5))


# 大便障碍物类
class Dabian:
    def __init__(self):
        # 随机大小
        size = random.randint(40, 70)
        self.size = size
        self.image = pygame.transform.scale(DABIAN_IMG, (size, size))
        self.x = WIDTH
        self.y = GROUND_HEIGHT - size + random.randint(-10, 10)  # 随机高度
        self.speed = GAME_SPEED + random.uniform(-POOP_SPEED_VARIATION, POOP_SPEED_VARIATION)
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)  # 随机旋转速度

    def update(self):
        self.x -= self.speed
        self.rotation += self.rotation_speed

    def draw(self):
        # 旋转大便
        rotated_poop = pygame.transform.rotate(self.image, self.rotation)
        # 保持中心位置不变
        rect = rotated_poop.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
        screen.blit(rotated_poop, rect.topleft)

        # 添加臭味粒子效果
        for i in range(3):
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-15, -5)
            alpha = random.randint(50, 150)
            pygame.draw.circle(screen, (100, 100, 0, alpha),
                               (self.x + self.size // 2 + offset_x, self.y + offset_y),
                               random.randint(2, 4))

    def collide(self, nk):
        # 圆形碰撞检测
        nk_center_x = nk.x + nk.width // 2
        nk_center_y = nk.y + nk.height // 2
        poop_center_x = self.x + self.size // 2
        poop_center_y = self.y + self.size // 2

        # 计算距离
        distance = math.sqrt((nk_center_x - poop_center_x) ** 2 + (nk_center_y - poop_center_y) ** 2)

        # 碰撞半径
        nk_radius = nk.width * 0.4
        poop_radius = self.size * 0.4

        return distance < (nk_radius + poop_radius)


# 游戏主函数
def game():
    clock = pygame.time.Clock()
    nk = NK()
    dabbians = []  # 大便列表
    score = 0
    high_score = 0
    obstacle_timer = 0
    game_over = False
    font = pygame.font.Font(None, 36)

    # 地面纹理
    ground_texture = pygame.Surface((WIDTH, 20))
    for i in range(20):
        pygame.draw.line(ground_texture, (100, 70, 30), (i * 40, 0), (i * 40, 20), 2)

    # 背景云朵
    clouds = []
    for i in range(5):
        clouds.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(50, 150),
            'speed': random.uniform(0.5, 1.5),
            'size': random.randint(30, 80)
        })

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if game_over:
                        # 重新开始游戏
                        return game()
                    else:
                        nk.jump()
                elif event.key == pygame.K_DOWN:
                    nk.duck()

            if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                nk.stand()

        if not game_over:
            # 更新NK角色
            nk.update()

            # 生成大便
            obstacle_timer += 1
            if obstacle_timer >= random.randint(40, 100):
                dabbians.append(Dabian())
                # 20%几率一次生成两坨
                if random.random() < 0.2:
                    dabbians.append(Dabian())
                obstacle_timer = 0

            # 更新大便
            for dabian in dabbians[:]:
                dabian.update()
                if dabian.x + dabian.size < 0:
                    dabbians.remove(dabian)
                elif dabian.collide(nk):
                    # 碰到大便滑行而不是立即结束
                    nk.slide()
                    # 10%几率移除大便（踩过去了）
                    if random.random() < 0.1:
                        dabbians.remove(dabian)

            # 更新云朵
            for cloud in clouds:
                cloud['x'] -= cloud['speed']
                if cloud['x'] + cloud['size'] < 0:
                    cloud['x'] = WIDTH
                    cloud['y'] = random.randint(50, 150)

            # 更新分数
            score += 0.1
            if score > high_score:
                high_score = score

        # 绘制游戏场景
        # 天空背景
        screen.fill((135, 206, 235))  # 天蓝色

        # 绘制云朵
        for cloud in clouds:
            pygame.draw.ellipse(screen, (250, 250, 250),
                                (cloud['x'], cloud['y'], cloud['size'], cloud['size'] // 2))

        # 绘制地面
        screen.blit(ground_texture, (0, GROUND_HEIGHT))
        pygame.draw.line(screen, (70, 50, 20), (0, GROUND_HEIGHT + 20), (WIDTH, GROUND_HEIGHT + 20), 2)

        # 绘制大便
        for dabian in dabbians:
            dabian.draw()

        # 绘制NK角色
        nk.draw()

        # 绘制分数
        score_text = font.render(f"分数: {int(score)}", True, BLACK)
        screen.blit(score_text, (WIDTH - 150, 20))

        high_score_text = font.render(f"最高分: {int(high_score)}", True, BLACK)
        screen.blit(high_score_text, (WIDTH - 150, 60))

        # 绘制游戏标题
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("NK的大便大冒险", True, (160, 0, 0))
        screen.blit(title_text, (20, 20))

        if game_over:
            game_over_text = font.render("游戏结束! 按空格键重新开始", True, BLACK)
            screen.blit(game_over_text, (WIDTH // 2 - 180, HEIGHT // 2 - 50))

        pygame.display.flip()
        clock.tick(60)


# 启动游戏
if __name__ == "__main__":
    game()
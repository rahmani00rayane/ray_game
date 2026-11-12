import pygame
import random


pygame.init()


# Background

class Background:

    def __init__(self, image, screen_width, screen_height):
        self.image = pygame.image.load(image)
        self.screen_width = screen_width
        self.screen_height = screen_height


# Character
class Character:

    def __init__(self, image_r, image_l, width, height, x, y):
        self.image_r = pygame.image.load(image_r)
        self.image_l = pygame.image.load(image_l)

        self.image = self.image_r

        self.width = width
        self.height = height

        self.x = x
        self.y = y

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# Hero
class Hero(Character):

    def __init__(self, image_r, image_l, width, height, x, y, speed):

        super().__init__(image_r, image_l, width, height, x, y)

        self.speed = speed
        self.health = 3
        self.facing = 1

    def take_damage(self):
        self.health -= 1

    def is_alive(self):
        return self.health > 0


# Hero Controller
class HeroController:

    def __init__(self, hero, screen_w, screen_h, margin=10, shoot_cooldown=200):

        self.hero = hero

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.margin = margin

        self.shoot_cooldown = shoot_cooldown
        self.last_shot = 0

    def update_direction(self, keys):

        if keys[pygame.K_x]:
            self.hero.image = self.hero.image_l
            self.hero.facing = -1

        if keys[pygame.K_c]:
            self.hero.image = self.hero.image_r
            self.hero.facing = 1

    def move(self, keys):

        h = self.hero
        m = self.margin

        if keys[pygame.K_LEFT] and h.x - h.speed > m:
            h.x -= h.speed

        if keys[pygame.K_RIGHT] and h.x + h.width + h.speed + m < self.screen_w:
            h.x += h.speed

        if keys[pygame.K_UP] and h.y - h.speed > m:
            h.y -= h.speed

        if keys[pygame.K_DOWN] and h.y + h.height + h.speed + m < self.screen_h:
            h.y += h.speed

    def shoot(self, keys, bullets, now):

        if keys[pygame.K_SPACE] and now - self.last_shot > self.shoot_cooldown:

            bullets.append(
                Bullet(
                    self.hero.x + self.hero.width // 2,
                    self.hero.y + self.hero.height // 2,
                    owner="hero",
                    direction=self.hero.facing
                )
            )

            self.last_shot = now


# Enemy
class Enemy(Character):

    def __init__(self, image_r, image_l, width, height, x, y, facing=1, now=0):

        super().__init__(image_r, image_l, width, height, x, y)

        self.facing = facing

        self.image = self.image_r if facing == 1 else self.image_l

        self.point = 5

        self.last_shot = now - random.randint(0, 5000)
        self.cooldown = 5000

    def take_damage(self):
        self.point -= 1

    def is_alive(self):
        return self.point > 0


# Enemy Behavior

class EnemyBehavior:

    @staticmethod
    def update(enemy, now, bullets):

        if now - enemy.last_shot > enemy.cooldown:

            bullets.append(
                Bullet(
                    enemy.x + enemy.width // 2,
                    enemy.y + enemy.height // 2,
                    owner="enemy",
                    color=(255, 255, 0),
                    direction=enemy.facing
                )
            )

            enemy.last_shot = now


# Enemy Spawner

class EnemySpawner:

    def __init__(self, image_r, image_l, width, height,
                 spawn_delay=3000, screen_w=800, screen_h=750):

        self.image_r = image_r
        self.image_l = image_l

        self.width = width
        self.height = height

        self.spawn_delay = spawn_delay

        self.screen_w = screen_w
        self.screen_h = screen_h

        self.enemies = []

        self.last_spawn = pygame.time.get_ticks()

    def spawn_enemy(self, now=None):

        if now is None:
            now = pygame.time.get_ticks()

        direction = random.choice(["left", "right"])

        y = random.randint(50, self.screen_h - self.height)

        if direction == "left":
            x = self.screen_w - 70
            facing = -1

        else:
            x = 20
            facing = 1

        enemy = Enemy(
            image_r=self.image_r,
            image_l=self.image_l,
            width=self.width,
            height=self.height,
            x=x,
            y=y,
            facing=facing,
            now=now
        )

        self.enemies.append(enemy)

    def update(self, now):

        if now - self.last_spawn >= self.spawn_delay:

            self.spawn_enemy(now)

            self.last_spawn = now


# Bullet

class Bullet:

    def __init__(self, x, y, owner, color=(255, 0, 0),
                 speed=10, radius=5, direction=1):

        self.x = x
        self.y = y

        self.owner = owner

        self.color = color

        self.speed = speed
        self.radius = radius

        self.direction = direction

    def move(self):

        self.x += self.speed * self.direction

    def rect(self):

        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def draw(self, win):

        pygame.draw.circle(
            win,
            self.color,
            (self.x, self.y),
            self.radius
        )

    def off_screen(self, width):

        return self.x < 0 or self.x > width


# Collision System
class CollisionSystem:

    @staticmethod
    def check(bullets, enemies, hero, score):

        for b in bullets[:]:

            # Hero bullets

            if b.owner == "hero":

                for e in enemies[:]:

                    if b.rect().colliderect(e.rect()):

                        e.take_damage()

                        bullets.remove(b)

                        if not e.is_alive():

                            enemies.remove(e)

                            score += 1

                        break

            # Enemy bullets

            elif b.owner == "enemy":

                if b.rect().colliderect(hero.rect()):

                    bullets.remove(b)

                    hero.take_damage()

        return score


# Renderer

class Renderer:

    @staticmethod
    def draw_background(win, background):

        win.blit(background.image, (0, -200))

    @staticmethod
    def draw_hero(win, hero):

        win.blit(hero.image, (hero.x, hero.y))

    @staticmethod
    def draw_enemies(win, enemies):

        for enemy in enemies:
            win.blit(enemy.image, (enemy.x, enemy.y))

    @staticmethod
    def draw_bullets(win, bullets):

        for bullet in bullets:
            bullet.draw(win)

    @staticmethod
    def draw_score(win, font, score):

        score_text = font.render(
            f"Score: {score}",
            True,
            (255, 255, 255)
        )

        win.blit(score_text, (20, 20))

    @staticmethod
    def draw_health(win, font, health):

        health_text = font.render(
            f"Health: {health}",
            True,
            (255, 0, 0)
        )

        win.blit(health_text, (300, 20))


# Game Initialization

background = Background(
    image="background_game.webp",
    screen_width=800,
    screen_height=750
)

hero = Hero(
    image_r="char_right.png",
    image_l="char_left.png",
    width=50,
    height=50,
    x=10,
    y=30,
    speed=3
)

hero_controller = HeroController(
    hero,
    screen_w=background.screen_width,
    screen_h=background.screen_height
)

enemy_spawner = EnemySpawner(
    image_r="enemy_right.png",
    image_l="enemy_left.png",
    width=50,
    height=50,
    screen_w=background.screen_width,
    screen_h=background.screen_height
)

# Initial enemies

enemy_spawner.spawn_enemy()
enemy_spawner.spawn_enemy()


screen = pygame.display.set_mode(
    (background.screen_width, background.screen_height)
)

pygame.display.set_caption("ray_game")

font = pygame.font.Font(None, 32)

clock = pygame.time.Clock()

bullets = []

score = 0

running = True


# Main Loop
while running:

    clock.tick(60)

    now = pygame.time.get_ticks()

    # Events

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    if not running:
        break

    # Hero

    keys = pygame.key.get_pressed()

    hero_controller.update_direction(keys)

    hero_controller.move(keys)

    hero_controller.shoot(keys, bullets, now)

    # Enemies

    enemy_spawner.update(now)

    for enemy in enemy_spawner.enemies:

        EnemyBehavior.update(enemy, now, bullets)

    # Bullets

    for bullet in bullets[:]:

        bullet.move()

        if bullet.off_screen(background.screen_width):
            bullets.remove(bullet)

    # Collision

    score = CollisionSystem.check(
        bullets,
        enemy_spawner.enemies,
        hero,
        score
    )

    # Game Over

    if not hero.is_alive():

        print("Game Over")

        running = False

    # Rendering

    Renderer.draw_background(screen, background)

    Renderer.draw_hero(screen, hero)

    Renderer.draw_enemies(screen, enemy_spawner.enemies)

    Renderer.draw_bullets(screen, bullets)

    Renderer.draw_score(screen, font, score)

    Renderer.draw_health(screen, font, hero.health)

    pygame.display.update()


pygame.quit()



'''
# hero
hero_left = pygame.image.load("char_left.png")
hero_right = pygame.image.load("char_right.png")

x = 10
y = 30
width = 50
height = 50
step = 3

left = False
right = True



# enemy
e_width = 50
e_height = 50
enemys = []
enemy_left_img  = pygame.image.load("enemy_left.png")
enemy_right_img = pygame.image.load("enemy_right.png")






# bullet
bullets = []
bullet_delay = 10





# color maybe i need 

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)





def spawn_enemy():
    direction = random.choice(["left", "right"])
    enemy_y = random.randint(50, 700)
    point_live = 5

    if direction == "left":
        enemy_x = 730
        image = enemy_left_img
    else:
        enemy_x = 20
        image = enemy_right_img

    enemys.append({
        "image": image,
        "x": enemy_x,
        "y": enemy_y,
        "point": point_live
    })


def redrawgame():
    screen.blit(bg, (0, -200))

    if left:
        screen.blit(hero_left, (x, y))
    else:
        screen.blit(hero_right, (x, y))

    for bullet in bullets:

        pygame.draw.circle(screen, RED, (bullet[0], bullet[1]), 4)
    

    for enemy in enemys:
        screen.blit(enemy["image"], (enemy["x"], enemy["y"]))
    
    pygame.display.update()





spawn_timer = 0
while True:
    pygame.time.delay(100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    keys = pygame.key.get_pressed()




    #===========================  hero ==============================


    #hero direction
    
    if keys[pygame.K_x] :
        left = True
        right = False

    if keys[pygame.K_c] :
        right = True
        left = False

    

    #hero moving

    if keys[pygame.K_LEFT] and x - step > 10:
        x -= step * 4
        

    if keys[pygame.K_RIGHT] and x + width + step + 10 < s_width:
        x += step * 4
        

    if keys[pygame.K_UP] and y - step > 10:
        y -= step * 4

    if keys[pygame.K_DOWN] and y + height + step + 10 < s_height:
        y += step * 4



    spawn_timer += 1
    if spawn_timer > 100:          
        if len(enemys) < 5:       
            spawn_enemy()
        spawn_timer = 0





    # ============================ bullet ==============================
    
    if keys[pygame.K_SPACE] and bullet_delay <=0:
        new_x = x + width // 2
        new_y = y + height // 2

        if left:
            speed = -100
        else:
            speed = 100

        bullets.append([new_x, new_y, speed, new_x])
        
        bullet_delay = 3

    if bullet_delay > 0:
        bullet_delay -= 1

    # Move bullets
    for b in bullets:
        b[3] = b[0]
        b[0] += b[2]

    # Check collision between bullets and enemies
    for b in bullets[:]:

        bullet_rect = pygame.Rect(
            min(b[3], b[0]) - 4,
            b[1] - 4,
            abs(b[0] - b[3]) + 8,
            8
        )

        for enemy in enemys[:]:

            enemy_rect = pygame.Rect(
                enemy["x"],
                enemy["y"],
                e_width,
                e_height
            )

            if bullet_rect.colliderect(enemy_rect):

                #enemy health
                enemy["point"] -= 1

                # Remove the bullet after hitting the enemy
                bullets.remove(b)

                # Kill the enemy
                if enemy["point"] <= 0:
                    enemys.remove(enemy)

                
                break

    # Delete bullets outside the screen
    bullets = [
        b for b in bullets
        if 0 <= b[0] <= s_width
    ]



    redrawgame()'''
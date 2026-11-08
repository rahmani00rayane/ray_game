import pygame
import random
from abc import ABC, abstractmethod


RED = (255, 0, 0)
YELLOW = (255, 255, 0)
successes, failures = pygame.init()


# background

class Bg:
    def __init__(self, image , s_width, s_height):
        self.bg = pygame.image.load(image)
        self.s_width = s_width
        self.s_height = s_height



class Character (ABC) :
    def __init__ (self, role, image_r, image_l, width, height, x, y):
        self.role = role 
        self.image_r = pygame.image.load(image_r)
        self.image_l = pygame.image.load(image_l)
        self.width = width
        self.height = height
        self.x = x 
        self.y = y


#hero 
class Hero(Character):
    def __init__(self, role, image_r, image_l, width, height, x, y, speed):
        super().__init__(role, image_r, image_l, width, height, x, y)
        self.image=self.image_r
        self.speed = speed
        self.health = 3

class Enemy(Character):
    def __init__(self, role, image_r, image_l, width, height, x, y):
        
        super().__init__(role, image_r, image_l, width, height, x, y)
        self.enemies = []
    def spawn_enemy(self):
        direction = random.choice(["left", "right"])
        enemy_y = random.randint(50, 700)
        point_live = 5

        if direction == "left":
            enemy_x = 730
            image = self.image_l
            facing = -1
        else:
            enemy_x = 20
            image = self.image_r
            facing = 1
        self.enemies.append({
            "image": image,
            "x": enemy_x,
            "y": enemy_y,
            "point": point_live,
            "facing": facing,
            "last_shot": pygame.time.get_ticks() - random.randint(0, 5000),
            "cooldown": 5000    

    })

class Bullet:
    def __init__(self, x, y,owner, color = RED, speed=10, radius=5, direction=1):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.direction = direction
        self.owner = owner

    
    
    def move(self):
        self.x += self.speed * self.direction

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)
    def off_screen(self, width):
        return self.x < 0 or self.x > width

hero = Hero (
    role = "hero",
    image_l="char_left.png",
    image_r="char_right.png",
    width=50,
    height=50,
    x=10,
    y=30,
    speed = 3
)
score = 0


enemy = Enemy(
    role = "enemy",
    image_l="enemy_left.png",
    image_r="enemy_right.png",
    width=50,
    height=50,
    x=10,
    y=30
)



backg = Bg( image = "background_game.webp",
           s_width=800,
           s_height=750
)





def check_collision(bullets, enemies, score):
    for b in bullets[:]:
        if b.owner != "hero" :
            continue
        bullet_rect = pygame.Rect(
            b.x - b.radius, b.y - b.radius,
            b.radius * 2, b.radius * 2
        )

        for e in enemy.enemies[:]:

            enemy_rect = pygame.Rect(
                e["x"],
                e["y"],
                enemy.width,
                enemy.height
            )

            if bullet_rect.colliderect(enemy_rect):

                #enemy health
                e["point"] -= 1
                if b in bullets:
                    bullets.remove(b)
                if e["point"] <= 0:
                    enemy.enemies.remove(e)
                    score += 1
                break

    hero_rect = pygame.Rect(hero.x, hero.y, hero.width, hero.height)
    for b in bullets[:]:
        if b.owner != "enemy":
            continue
        bullet_rect = pygame.Rect(
            b.x - b.radius, b.y - b.radius,
            b.radius * 2, b.radius * 2
        )
        if bullet_rect.colliderect(hero_rect):
            bullets.remove(b)
            hero.health -= 1
            if hero.health <= 0:
                print("Game Over")
                pygame.quit()
                exit()
    return score
enemy.spawn_enemy()
enemy.spawn_enemy()
last_shot = 400
last_enemy_spawn = pygame.time.get_ticks()
spawn_delay = 3000
screen = pygame.display.set_mode((backg.s_width, backg.s_height))
font = pygame.font.Font(None, 32)
pygame.display.set_caption("ray_game")
screen.blit(backg.bg, (0, -200))
screen.blit(hero.image, (hero.x, hero.y))
for e in enemy.enemies:
    screen.blit(e["image"], (e["x"], e["y"]))

clock = pygame.time.Clock()
bullets = [] 
while True :
    clock.tick(60)   
    now = pygame.time.get_ticks() 
    if now - last_enemy_spawn >= spawn_delay:
        enemy.spawn_enemy()
        last_enemy_spawn = now
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        
        
        
    keys = pygame.key.get_pressed()

    #hero direction
    if keys[pygame.K_x] :
        hero.image = hero.image_l

    if keys[pygame.K_c] :
        hero.image = hero.image_r

    

    #hero moving

    if keys[pygame.K_LEFT] and hero.x - hero.speed > 10:
        hero.x -= hero.speed 
        

    if keys[pygame.K_RIGHT] and hero.x + hero.width + hero.speed + 10 < backg.s_width:
        hero.x += hero.speed
        

    if keys[pygame.K_UP] and hero.y - hero.speed > 10:
        hero.y -= hero.speed

    if keys[pygame.K_DOWN] and hero.y + hero.height + hero.speed + 10 < backg.s_height:
        hero.y += hero.speed 


    #bullet 
    if keys[pygame.K_SPACE] and now - last_shot > 200:
        direction = 1 if hero.image is hero.image_r else -1
        bullets.append(Bullet(
            hero.x + hero.width // 2,
            hero.y + hero.height // 2,
            direction=direction,
            owner = "hero"))
        last_shot = now
    for b in bullets[:]:
        b.move()   
        if b.off_screen(backg.s_width):
            bullets.remove(b)
    score = check_collision(bullets, enemy.enemies, score)
    screen.blit(backg.bg, (0, -200))
    screen.blit(hero.image, (hero.x, hero.y))
    for e in enemy.enemies:
        if now - e["last_shot"] > e["cooldown"]:
            bullets.append(Bullet(
                e["x"] + enemy.width // 2,
                e["y"] + enemy.height // 2,
                owner="enemy",
                color=YELLOW,
                direction=e["facing"]))
            e["last_shot"] = now
        screen.blit(e["image"], (e["x"], e["y"]))
    for b in bullets:
        b.draw(screen)
    score_text = font.render(
    f"Score: {score}",
    True,
    (255, 255, 255)
    )
    screen.blit(score_text, (20, 20))
    health_text = font.render(
    f"Health: {hero.health}",
    True,
    (255, 0, 0)
)

    screen.blit(health_text, (300, 20))
    pygame.display.update()





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
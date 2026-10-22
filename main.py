import pygame
import random

#print (dir(pygame))

successes, failures = pygame.init()


#print(successes)
#print(failures)
#print ("="*30)

#============================================================

# background
bg = pygame.image.load("background_game.webp")

s_width = 800
s_height = 750


screen = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption("ray_game")

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



    redrawgame()
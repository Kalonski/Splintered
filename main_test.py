import pygame
import sys
import math
import os
from settings import *

#initialisation
pygame.init()
#setting up the screen
nativeRes = pygame.display.Info()
screen = pygame.display.set_mode((nativeRes.current_w,nativeRes.current_h), pygame.RESIZABLE)
pygame.display.set_caption("Splintered 0.0")
clock = pygame.time.Clock()

background = pygame.image.load("Assets/ground.png").convert()
#background = pygame.transform.scale(pygame.image.load("Assets/background.png").convert(), (nativeRes.current_w,nativeRes.current_h))
#atkImageList = ["Assets/knife/meleeattack/survivor-meleeattack_knife_0.png","Assets/knife/meleeattack/survivor-meleeattack_knife_1.png","Assets/knife/meleeattack/survivor-meleeattack_knife_2.png","Assets/knife/meleeattack/survivor-meleeattack_knife_3.png","Assets/knife/meleeattack/survivor-meleeattack_knife_4.png","Assets/knife/meleeattack/survivor-meleeattack_knife_5.png","Assets/knife/meleeattack/survivor-meleeattack_knife_6.png","Assets/knife/meleeattack/survivor-meleeattack_knife_7.png","Assets/knife/meleeattack/survivor-meleeattack_knife_8.png","Assets/knife/meleeattack/survivor-meleeattack_knife_9.png","Assets/knife/meleeattack/survivor-meleeattack_knife_10.png","Assets/knife/meleeattack/survivor-meleeattack_knife_11.png","Assets/knife/meleeattack/survivor-meleeattack_knife_12.png","Assets/knife/meleeattack/survivor-meleeattack_knife_13.png","Assets/knife/meleeattack/survivor-meleeattack_knife_14.png"]

class Player(pygame.sprite.Sprite):
    #creating the player
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2 (nativeRes.current_w // 2,nativeRes.current_h // 2)
        self.image = pygame.transform.rotozoom(pygame.image.load("Assets/knife/idle/survivor-idle_knife_0.png").convert_alpha(), 0, PLAYER_SIZE)
        self.base_player_image = self.image
        #self.rect = self.image.get_rect()
        self.hitbox_rect = self.base_player_image.get_rect(center = self.pos)
        self.rect = self.hitbox_rect.copy()
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.attack = False
        self.frame = 0 
        self.moving = False
        self.everything_offset = pygame.math.Vector2(0,0)
        self.velocity_x = 0
        self.velocity_y = 0

    def player_rotation(self):
        self.mouse_coords = pygame.mouse.get_pos()
        self.playermouse_x = (self.mouse_coords[0] - self.hitbox_rect.centerx)
        self.playermouse_y = (self.mouse_coords[1] - self.hitbox_rect.centery)
        self.angle = math.degrees(math.atan2(self.playermouse_y, self.playermouse_x ))
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center = self.hitbox_rect.center)


    def collisionDetect(self):
        self.velocity_x = 0
        self.velocity_y = 0
        self.colvelocity_x = 0
        self.colvelocity_y = 0
        for crate in crates:
            if self.hitbox_rect.colliderect(crate.rect) and self.hitbox_rect.right - 5 < crate.rect.left:
                self.colvelocity_x = -self.speed
            if self.hitbox_rect.colliderect(crate.rect) and self.hitbox_rect.left + 5 > crate.rect.right:
                self.colvelocity_x = self.speed
            if self.hitbox_rect.colliderect(crate.rect) and self.hitbox_rect.bottom - 5 < crate.rect.top:
                self.colvelocity_y = -self.speed
            if self.hitbox_rect.colliderect(crate.rect) and self.hitbox_rect.top + 5 > crate.rect.bottom:
                self.colvelocity_y = self.speed

    #detecting keystrokes and setting speeds
    def user_input(self):
        '''self.velocity_x = 0
        self.velocity_y = 0'''

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL]:
            self.speed /= 2 
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
        self.speed = PLAYER_SPEED

        if self.velocity_x != 0 or self.velocity_y != 0:
            self.moving = True
        else:
            self.moving = False
        
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)
        
        if pygame.mouse.get_pressed() == (1, 0, 0): 
        #if event.type() == pygame.MOUSEBUTTONDOWN:
            self.attack = True
    
    #calculating where the player should be after the movement
    def move(self):
        self.velocity_x += self.colvelocity_x
        self.velocity_y += self.colvelocity_y
        self.everything_offset = pygame.math.Vector2(-self.velocity_x, -self.velocity_y)
        #self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        #self.hitbox_rect.center = self.pos
        #self.rect.center = self.hitbox_rect.center


    def loadAnims(self):
        self.atkImageList = []
        self.moveImageList = []
        for i in range(0,15):
            self.image = pygame.image.load(os.path.join("Assets/knife/meleeattack", "survivor-meleeattack_knife_" + str(i) + ".png"))
            self.image = pygame.transform.rotozoom((self.image), 0, PLAYER_SIZE).convert_alpha()
            self.atkImageList.append(self.image)
        for i in range(0,20):
            self.image = pygame.image.load(os.path.join("Assets/knife/move", "survivor-move_knife_" + str(i) + ".png"))
            self.image = pygame.transform.rotozoom((self.image), 0, PLAYER_SIZE).convert_alpha()
            self.moveImageList.append(self.image)
    
    """ def collisionDetect(self):
        for crate in crates:
            if self.hitbox_rect.colliderect(crate.leftRect):
                self.velocity_x -= self.speed
            if self.hitbox_rect.colliderect(crate.rightRect):
                self.velocity_x += self.speed
            if self.hitbox_rect.colliderect(crate.topRect):
                self.velocity_y -= self.speed
            if self.hitbox_rect.colliderect(crate.bottomRect):
                self.velocity_y += self.speed
 """
    #Runs the 2 previous functions to check for and update movement
    def update(self):
        self.collisionDetect()
        self.user_input()
        self.move()
        self.player_rotation()

        
        if self.attack:
            if self.frame > 28:
                self.frame = 0
                self.attack = False
            #self.loadAttackAnim()
            self.image = pygame.transform.rotate(self.atkImageList[self.frame//2], -self.angle)
            self.rect = self.image.get_rect(center = self.pos)
            self.frame += 1
        elif self.moving and self.attack == False:
            if self.frame > 57:
                self.frame = 0
            self.image = pygame.transform.rotate(self.moveImageList[self.frame//3], -self.angle)
            self.rect = self.image.get_rect(center = self.pos)
            self.frame += 1
         
#        if self.attack_cooldown > 0 :
 #           self.attack_cooldown -= 1

class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = pygame.math.Vector2()
        self.floor_rect = background.get_rect(center = (0, 0))

    def customDraw(self):
        #self.offset.x = player.rect.centerx - nativeRes.current_w // 2
        #self.offset.y = player.rect.centery - nativeRes.current_h // 2

        self.floor_rect.center = self.floor_rect.center + player.everything_offset
        #screen.blit(background, self.floor_rect)
        #print(self.floor_rect)  

        for sprite in allSprites:
            #offset_pos = pygame.math.Vector2(0,0)
            sprite.rect.center = sprite.rect.center + player.everything_offset
            #sprite.pos = offset_pos
            #sprite.rect.center = sprite.pos
        for lists in enemy.routelist:
            for destinations in lists:
                destinations = pygame.math.Vector2(destinations) + player.everything_offset
                #item[1] += player.everything_offset[1]


class Crate(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.pos = pygame.math.Vector2 (position)
        self.image = pygame.transform.rotozoom(pygame.image.load("Assets/Wooden Crate Texture.png").convert_alpha(), 0, 3)
        self.hitbox_rect = self.image.get_rect(center = self.pos)
        self.rect = self.hitbox_rect.copy()
                        #rect values = (left, top, width, height)
        """ self.leftRect = (self.rect.left, self.rect.top, CRATE_RECT_SIZE, self.rect.height)
        self.rightRect = ((self.rect.right - CRATE_RECT_SIZE), self.rect.top, CRATE_RECT_SIZE, self.rect.height)
        self.topRect = (self.rect.left, self.rect.top, self.rect.width, CRATE_RECT_SIZE)
        self.bottomRect = (self.rect.left, (self.rect.bottom - CRATE_RECT_SIZE), self.rect.width, CRATE_RECT_SIZE) """

    def update(self):
        self.leftRect = (self.rect.left, self.rect.top, CRATE_RECT_SIZE, self.rect.height)
        self.rightRect = ((self.rect.right - CRATE_RECT_SIZE), self.rect.top, CRATE_RECT_SIZE, self.rect.height)
        self.topRect = (self.rect.left, self.rect.top, self.rect.width, CRATE_RECT_SIZE)
        self.bottomRect = (self.rect.left, (self.rect.bottom - CRATE_RECT_SIZE), self.rect.width, CRATE_RECT_SIZE)
    #def interact(self):
        #player.mouse_coords

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, route):
        super().__init__()
        self.pos = pygame.math.Vector2 (position)
        self.image = pygame.transform.rotozoom(pygame.image.load("Assets/Top_Down_Survivor/rifle/idle/survivor-idle_rifle_0.png").convert_alpha(), 0, 0.4)
        self.base_image = self.image.copy()
        self.hitbox_rect = self.image.get_rect(center = self.pos)
        self.rect = self.hitbox_rect.copy()
        self.size = 1
        self.speed = 4
        self.route = route
        self.routelist = [[(100, 100), (100, 400), (400, 400), (400, 100)], 
                          [(300, 300), (400, 400), (500, 500), (400, 400)], 
                          [(100, 100), (1000, 1000), (800, 300), (400, 100)], 
                          [(100, 100), (100, 400), (400, 400), (700, 700), (700, 900), (500, 500)]]
    

    def move(self):
        for enemy in enemies: 
            if self.route == 1:
                route_destinations = self.routelist[0]
            elif self.route == 2:
                route_destinations = self.routelist[1]
            elif self.route == 3:
                route_destinations = self.routelist[2]
            elif self.route == 4:
                route_destinations = self.routelist[3]

            for i in range((len(route_destinations)-1)):
                if self.pos == route_destinations[-1]:
                    self.destination = route_destinations[0]

                if self.pos == route_destinations[i]:
                    self.destination = route_destinations[i + 1]

            self.velocity_x = 0
            self.velocity_y = 0
            if self.pos.x != self.destination[0]:
                if self.pos.x < self.destination[0]:
                    self.velocity_x = 1
                elif self.pos.x > self.destination[0]:
                    self.velocity_x = -1

            if self.pos.y != self.destination[1]:
                if self.pos.y < self.destination[1]:
                    self.velocity_y = 1
                elif self.pos.y > self.destination[1]:
                    self.velocity_y = -1
            
            """if self.velocity_x != 0 and self.velocity_y != 0:
                self.velocity_x /= math.sqrt(2)
                self.velocity_y /= math.sqrt(2)"""

            self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
            self.hitbox_rect.center = self.pos
            self.rect.center = self.hitbox_rect.center    
            
    
    def rotation(self):
        for enemy in enemies:
            self.x_difference = self.destination[0] - self.hitbox_rect.centerx
            self.y_difference = self.destination[1] - self.hitbox_rect.centery
            if self.x_difference != 0 and self.y_difference != 0:
                self.angle = math.degrees(math.atan2(self.x_difference , self.y_difference))
                self.image = pygame.transform.rotate(self.base_image, (-self.angle))
                self.rect = self.image.get_rect(center = self.hitbox_rect.center)
            elif self.x_difference < 0 and self.y_difference == 0:
                self.angle = 180
            elif self.x_difference > 0 and self.y_difference == 0:
                self.angle = 0
            elif self.x_difference == 0 and self.y_difference > 0:
                self.angle = 90
            elif self.x_difference == 0 and self.y_difference < 0:
                self.angle = 270
            self.image = pygame.transform.rotate(self.base_image, (-self.angle))
            self.rect = self.image.get_rect(center = self.hitbox_rect.center)


    
    """ def rotation(self):
        self.mouse_coords = pygame.mouse.get_pos()
        self.playermouse_x = (self.mouse_coords[0] - self.hitbox_rect.centerx)
        self.playermouse_y = (self.mouse_coords[1] - self.hitbox_rect.centery)
        self.angle = math.degrees(math.atan2(self.playermouse_y, self.playermouse_x ))
        self.image = pygame.transform.rotate(self.base_image, -self.angle)
        self.rect = self.image.get_rect(center = self.hitbox_rect.center) """
    def update(self):
        self.move()
        self.rotation()
    
        
        

#camera = Camera()
player = Player()
#crate = Crate((CRATE_SPAWN_X, CRATE_SPAWN_Y))
crates = []
crates.append(Crate((CRATE_SPAWN_X, CRATE_SPAWN_Y)))
crates.append(Crate((400, 250)))
crates.append(Crate((1100, 450)))
allSprites = pygame.sprite.Group()
playerSprites = pygame.sprite.Group()
playerSprites.add(player)
for crate in crates:
    allSprites.add(crate)
player.loadAnims()

enemies = []
enemies.append(Enemy((100,100), 1))
#enemies.append(Enemy((300,300), 2))
#enemies.append(Enemy((100,100), 3))
#enemies.append(Enemy((100,100), 4))
camera = Camera()

for enemy in enemies:
    allSprites.add(enemy)

while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
    #screen.blit(background, (0,0))
    #for crate in crates:
        #screen.blit(crate.image, crate.rect)
    #camera.customDraw()
    #allSprites.draw(screen)
    camera.customDraw()
    screen.blit(background, camera.floor_rect)
    allSprites.update()
    allSprites.draw(screen)
    playerSprites.update()
    playerSprites.draw(screen)
    #player.update()
    #enemy.update()
    pygame.draw.rect(screen, "red", player.hitbox_rect, width = 2)
    #pygame.draw.rect(screen, "yellow", player.rect, width = 2)
    """ for crate in crates:
        pygame.draw.rect(screen, "blue", crate.rect, width = 2)
        pygame.draw.rect(screen, "green", crate.leftRect, width = 2)
        pygame.draw.rect(screen, "green", crate.rightRect, width = 2)
        pygame.draw.rect(screen, "green", crate.topRect, width = 2)
        pygame.draw.rect(screen, "green", crate.bottomRect, width = 2) """

    #print(player.rect, player.hitbox_rect, player.pos)
    #print(crate.rect)
    pygame.display.update()
    clock.tick(FPS)
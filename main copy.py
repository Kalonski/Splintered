import pygame
import sys
import math
import random

from pygame.sprite import Group
from constantsSettings import *
from spriteSheet import *


pygame.init()
#This code is responsible for getting the resolution of the screen, setting the screen to size, setting the name of the sceen,
#and making a variable for manipulating the clock to set FPS 
resolution = pygame.display.Info()
screen = pygame.display.set_mode((resolution.current_w , resolution.current_h),pygame.RESIZABLE) #Fits the screen to the size of the display
pygame.display.set_caption('Splintered')
background = pygame.transform.scale(pygame.image.load("Assets\Level images\Level1alt.png").convert_alpha(), (8000,8000))
#background = pygame.transform.rotozoom(pygame.image.load("Assets\Level images\BackgroundPlaceholderIce.jpg").convert_alpha(), 0, 1.5) #sets the image for the background
bg_rect = background.get_rect(center = ((resolution.current_w // 2, resolution.current_h // 2))) #This is to get the rectangular area of the backround and set the centre of the image to the center of the background
clock = pygame.time.Clock()
screen_rect = (0, 0, resolution.current_w, resolution.current_h)
start_game = False #game doesnt start immediately but rather opens the menu until the user interacts with the button.

#sprite_sheet = Spritesheet('')
#print(resolution.current_w, resolution.current_h)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() #initialises the inerited superclass (pygame.sprite.Sprite) which allows it to be added to sprite groups
        self.pos = pygame.math.Vector2((resolution.current_w // 2, resolution.current_h // 2)) #The starting posion coodinates of the player (with respect to the top left of the display)
        self.move_sheet = pygame.image.load("Assets\Player images\sprPWalkAxe_strip8green.png")
        self.legs_sheet = pygame.image.load("Assets\Player images\sprLegs_strip16green.png")
        self.atk_sheet = pygame.image.load("Assets\Player images\sprPAttackAxe_strip7green.png")
        #self.image = pygame.transform.rotate(pygame.transform.scale_by(pygame.image.load("Assets\Player images\Knife\idle\survivor-idle_knife_0.png").convert_alpha(), player_size), -90)
        self.image = pygame.transform.rotate(pygame.transform.scale_by(get_sprite(self.move_sheet, 0, 0, 44, 44).convert_alpha(), 4), -90)
        self.legs_image = pygame.transform.rotate(pygame.transform.scale_by(get_sprite(self.legs_sheet, 0, 0, 32, 32).convert_alpha(), 4), -90)
        self.base_image = self.image.copy() #copy made for if i need to easily switch back to the original image
        self.mask = pygame.mask.from_surface(self.image) #creates a mask based on the players image
        self.rect = self.image.get_rect(center = self.pos) #creates a rect from the player image (left, top, width, height)
        self.hitbox_rect = pygame.Rect(self.pos[0] - player_hitbox_width//2 ,self.pos[1] - player_hitbox_height, player_hitbox_width,player_hitbox_height) #sets a square as the hitbox rect for the player, will update in size if the variables are changed in the constantsSettings.py file
        self.hitbox_rect.center = self.pos
        self.speed = player_speed #variable will be used to update the veocity x and y variables 
        self.size = player_size
        self.general_offset = pygame.math.Vector2(0,0) #setting up as 0,0 for later use
        self.collision_velocity_x = 0
        self.collision_velocity_y = 0
        self.colour = "green"
        self.cone_colliding = 0
        self.frames_in_cone = coneFrames
        self.alive = True #determines if the game can continue or should be closed
        self.total_offset = pygame.math.Vector2(0,0)
        
        self.move_direct = 0 
        self.walk_frame = 0
        self.legs_frame = 0
        self.walk_count = 0
        self.legs_count = 0
        self.atk_frame = 0
        self.atk_count = 0


        self.attacking = False
        self.atk_rect = pygame.Rect(0,0,0,0)


    def player_rotation(self):
        self.mouse_coords = pygame.mouse.get_pos() #gets the pixel position of where the mouse pointer is on the screen
        #print(self.mouse_coords)
        self.x_difference = self.mouse_coords[0] - self.pos[0] #finds the x difference of the mouse and player
        self.y_difference = self.mouse_coords[1] - self.pos[1] #finds the y difference of the mouse and player
        self.angle = math.degrees(math.atan2(self.x_difference, self.y_difference)) #finds the angle of rotation between the player and mouse
        self.image = pygame.transform.rotate(self.base_image, self.angle) #rotates the image based on the angle of rotation
        self.rect = self.image.get_rect(center = self.pos) #updates the rect 
        self.mask = pygame.mask.from_surface(self.image) #updates the mask on each frame to the new rotation for the players image

    def collisions_check(self):
        self.collision_velocity_x = 0 #resets the offset movement so that it only occurs while colliding
        self.collision_velocity_y = 0
        for object in collidables: #iterates through all of the collidable objects on that level
            if self.hitbox_rect.colliderect(object.rect) and self.hitbox_rect.left + 15 > object.rect.right: #Checks if the player is on the right of the object
                self.collision_velocity_x = self.speed #offsets the A input
            if self.hitbox_rect.colliderect(object.rect) and self.hitbox_rect.right - 15 < object.rect.left: #Checks if the player is on the left of the object
                self.collision_velocity_x = -self.speed #offsets the D input
            if self.hitbox_rect.colliderect(object.rect) and self.hitbox_rect.top + 15 > object.rect.bottom: #Checks if the player is below the object
                self.collision_velocity_y = self.speed #offsets the W input
            if self.hitbox_rect.colliderect(object.rect) and self.hitbox_rect.bottom - 15 < object.rect.top: #Checks if the player is above the object
                self.collision_velocity_y = -self.speed #offsets the S input

        """ if rect.collide(object.level_exit) then
            level.current_level += 1 
            level.update_level()
        endif """

        for enemy in enemies: #iterates through all of the seperately instantiated enemies
            if self.hitbox_rect.colliderect(enemy.cone_rect):
                if self.mask.overlap(enemy.cone_mask, (enemy.cone_rect.x - self.rect.x, enemy.cone_rect.y -self.rect.y)): #checks if the player mask is touching the enemies mask and returns a true/false value
                    self.cone_colliding += 1 #this will show how many enemy vision cones the player has contacted on that frame
                    #print("overlap")

            if self.atk_rect.colliderect(enemy.rect):
                print("dead")
                all_sprites.remove(enemy)
                offset_sprites.remove(enemy)
                enemies.remove(enemy)

        if self.cone_colliding > 0: #for if there was any cone collision on this frame (doesnt matter which cone)
            self.colour = "red" #shows when the player IS colliding with a vision cone
            self.frames_in_cone -= 1 #counts down the maount of frames which the player is inside the vision cone
            self.cone_colliding = 0 #resets the collision counter for when it needs to check again on the next tick

        elif self.cone_colliding == 0: #for when there was no cone collision with any cone on this frame
            self.frames_in_cone = coneFrames #resets timer when the player moves out of range
            self.colour = "green" #shows when the player is NOT colliding with a vision cone

        #print(self.frames_in_cone)
        if self.frames_in_cone == 0: #checks if the counter is complete
            print("game over") #for testing
            self.alive = False
            print(all_sprites)
            for enemy in enemies:
                #enemy.kill()
                offset_sprites.remove(enemy)
                all_sprites.remove(enemy)
            enemies.clear()
            print(all_sprites)
            
        
    def user_input(self):
        self.velocity_x = 0 #assigns variables to int 0 (no movement detected yet)
        self.velocity_y = 0

        keys = pygame.key.get_pressed() #gets any keypressed and stores them in a variable
        if keys[pygame.K_LCTRL] or keys[pygame.K_LSHIFT]:
            self.speed /= 0.2 #speed is halved when ctrl button is held
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed #player moves in the negative y direction (up)
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed #player moves in the negative x direction (left)
        if keys[pygame.K_s]:
            self.velocity_y = self.speed #player moves in the positive y direction (down)
        if keys[pygame.K_d]:
            self.velocity_x = self.speed #player moves in the positive x direction (right)
        self.speed = player_speed #speed is reset in case it was changed by holding CTRL


        if self.velocity_x != 0 or self.velocity_y != 0: #checks if the player is moving at all 
            self.moving = True
        else:
            self.moving = False 
        
        if self.moving: #This calulates the angle which the legs will face when moving
            if self.velocity_x > 0 and self.velocity_y < 0:
                self.move_direct = 45
            elif self.velocity_x > 0 and self.velocity_y > 0:
                self.move_direct = 135
            elif self.velocity_x < 0 and self.velocity_y > 0:
                self.move_direct = 225
            elif self.velocity_x < 0 and self.velocity_y < 0:
                self.move_direct = 315
            elif self.velocity_x > 0:
                self.move_direct = 90
            elif self.velocity_x < 0:
                self.move_direct = 270
            elif self.velocity_y > 0:
                self.move_direct = 180
            elif self.velocity_y < 0:
                self.move_direct = 0
            

        if self.velocity_x != 0 and self.velocity_y != 0: #checks if the player is moving diagonally (two directions at once)
            self.velocity_x //= math.sqrt(2)
            self.velocity_y //= math.sqrt(2) #offsets the extra speed of moving diagonally
        
        if pygame.mouse.get_pressed() == (1, 0, 0): 
            self.attacking = True

    def move(self): #method is used to just update the position of player based on the velocity
        #NOT IN USE self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y) #updates the position with all changes from this tick
        self.velocity_x = self.velocity_x + self.collision_velocity_x
        self.velocity_y = self.velocity_y + self.collision_velocity_y
        self.general_offset = pygame.math.Vector2(-self.velocity_x, -self.velocity_y) #calculates the offset by which all objects on screen will be affected
        self.total_offset += self.general_offset
        self.rect.center = self.pos #updates the rect position
        self.hitbox_rect.center = self.pos

    def animate(self):
        if self.attacking == True:
            if self.atk_count == 4:
                self.atk_frame += 1
                self.atk_count = 0
            if self.atk_frame == 7:
                self.atk_frame = 0
                self.attacking = False 
            self.image = pygame.transform.rotate(pygame.transform.scale_by(get_sprite(self.atk_sheet, 0 + (60 * self.atk_frame), 0 , 60, 60).convert_alpha(), 4), self.angle - 90)
            self.rect = self.image.get_rect(center = self.pos)
            self.atk_count += 1
        if self.moving: 
            if self.legs_count == 3:
                self.legs_frame += 1
                self.legs_count = 0
            if self.legs_frame == 16:
                self.legs_frame = 0 
            self.legs_image = pygame.transform.rotate(pygame.transform.scale_by(get_sprite(self.legs_sheet, 0 + (32 * self.legs_frame), 0 , 32, 32).convert_alpha(), 4), 90 - self.move_direct)
            self.legrect = self.legs_image.get_rect(center = self.pos)
            screen.blit(self.legs_image, self.legrect)
            self.legs_count += 1 

            if self.attacking == False:
                if self.walk_count == 5: #every 6 frames this is true
                    self.walk_frame += 1 #iterates through each image in the sprite sheet
                    self.walk_count = 0
                if self.walk_frame == 8: #when it is at the end of the spritesheet
                    self.walk_frame = 0             
                self.image = pygame.transform.rotate(pygame.transform.scale_by(get_sprite(self.move_sheet, 0 + (44 * self.walk_frame), 0 , 44, 44).convert_alpha(), 4), self.angle - 90)
                self.rect = self.image.get_rect(center = self.pos)
                self.walk_count += 1


    def attack(self):
        store_angle = self.angle
        if 135 <= store_angle or store_angle <= -135: #player looking up
            self.atk_rect = pygame.Rect(self.pos.x - 100, self.pos.y - 100, 200, 80)
        elif 45 <= store_angle < 135: #player looking to the right
            self.atk_rect = pygame.Rect(self.pos.x + 20 , self.pos.y - 100, 80, 200)
        elif -45 <= store_angle < 45: #player looking down
            self.atk_rect = pygame.Rect(self.pos.x - 100, self.pos.y + 20, 200, 80)
        elif -135 <= store_angle < -45: #player looking to the left
            self.atk_rect = pygame.Rect(self.pos.x - 100, self.pos.y - 100, 80, 200)





    
    def update(self): #calls all player methods which need to be called each frame
        self.user_input() 
        self.collisions_check()  
        self.move()
        self.player_rotation()
        self.animate()
        if self.attacking:
            self.attack()
        else:
            self.atk_rect = pygame.Rect(0,0,0,0)
        


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, route, speed, level): #position is in form (x,y) with 2 integers, route is a 2d array, speed is an integer, level is an integer
        super().__init__()
        self.start_pos = pygame.math.Vector2(position)
        self.pos = pygame.math.Vector2(position) #sets starting position
        self.move_sheet = pygame.image.load("Assets\Enemy images\sprEWalkUnarmed_strip8green.png")
        self.image = pygame.transform.rotate(pygame.transform.scale_by(get_sprite(self.move_sheet, 0, 0, 32, 32).convert_alpha(), 4), -90) #sets an image for the enemy sprite, rotates the image 90 degrees anticlockwise, scales the image based on the enemy_size variable in constantsSettings.py
        self.base_image = self.image.copy() 
        self.cone_image = pygame.transform.rotate(pygame.transform.scale_by(pygame.image.load("Assets\Enemy images\cone3.png").convert_alpha(), 0.7), 180)
        self.cone_rect = self.cone_image.get_rect(center = self.pos)
        self.cone_base_image = self.cone_image.copy()
        self.cone_mask = pygame.mask.from_surface(self.cone_image)
        #self.cone_colliding = 0
        self.rect = self.image.get_rect(center = self.pos) #gets the rectangular area of the enemy
        self.size = enemy_size #setting speed (from constantsSettings.py)
        self.speed = speed #setting size (from constantsSettings.py)
        self.base_route = route
        self.route = self.base_route.copy()
        
        self.walk_frame = 0
        self.count = 0

        #self.cone_rect = Get.rect(self.cone_image)
        #self.native_level = level


    def move(self):
            #route_destinations = self.route_list[self.route] #selects list within the 2d array based on the self.route integer

            for i in range((len(self.route)-1)):
                if self.pos == self.route[-1]: #if the enemy reaches the end of the route
                    self.destination = self.route[0] #sets the destination back to the start of the route 

                elif self.pos == self.route[i]: #if the enemy reaches its destination
                    self.destination = self.route[i+1] #destination is set to next item in the list
                    #print(self.pos)

            self.velocity_x = 0
            self.velocity_y = 0
            if self.pos[0] != self.destination[0]: #checks if the player x is not at the destination x
                if self.pos[0] > self.destination[0]: #checks if enemy is on the right of the destination
                    self.velocity_x = -self.speed
                elif self.pos[0] < self.destination[0]: #checks if enemy is on the left of the destination
                    self.velocity_x = self.speed

            if self.pos[1] != self.destination[1]: #checks if the player y is not at the destination y
                if self.pos[1] > self.destination[1]: #checks if enemy is below the destination
                    self.velocity_y = -self.speed
                elif self.pos[1] < self.destination[1]: #checks if enemy is above the destination
                    self.velocity_y = self.speed
            self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
            self.rect.center = self.pos

    def rotation(self):
            self.x_difference = self.destination[0] - self.pos[0] #gets horizontal difference between where the enemy is and its destination
            self.y_difference = self.destination[1] - self.pos[1] #gets vertical difference between where the enemy is and its destination
            self.angle = math.degrees(math.atan2(self.x_difference , self.y_difference)) #calculates the angle of rotation between the two points using the 2 lengths
            self.image = pygame.transform.rotate(self.base_image, self.angle) #rotates the enemys image


    def draw_cone(self):
            self.cone_image = pygame.transform.rotate(self.cone_base_image, self.angle) #rotates the image using the angle calculated in rotation() and the cones base image, so that rotations arent appended
            self.cone_rect = self.cone_image.get_rect(center = self.cone_base_image.get_rect(center = self.pos).center) #updates the rect using the center of its original image(with center pos)
            if self.cone_rect.colliderect(screen_rect):
                screen.blit(self.cone_image, self.cone_rect) #draws the cone to the screen
                self.cone_mask = pygame.mask.from_surface(self.cone_image) #updates the mask on each frame to the new rotation from the cone rotation.
                #pygame.draw.rect(screen, "blue", self.cone_rect, 4) #draws the rect area (temporary)

    def animate(self):
            if self.count == 7: #every 6 frames this is true
                self.walk_frame += 1 #iterates through each image in the sprite sheet
                self.count = 0
            if self.walk_frame == 7: #when it is at the end of the spritesheet
                self.walk_frame = 0 
            self.image = pygame.transform.rotate(pygame.transform.scale_by(get_sprite(self.move_sheet, 0 + (32 * self.walk_frame), 0 , 32, 32).convert_alpha(), 4), self.angle - 90)
            self.rect = self.image.get_rect(center = self.pos)
            self.count += 1

    def update(self):
        self.move()
        self.rotation()
        self.draw_cone()
        self.animate()  
        #self.collisions_check() 


class Level(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.current_level = 0 #sets the level to the first level
        level_backgrounds = ["Assets\Level images\BackgroundPlaceholderIce.jpg"] #stores the images for the backgrounds
        self.offset = (0,0) #the offset vector of all the objects on screen
        background = pygame.image.load(level_backgrounds[self.current_level]) #sets the background for the first level
        self.floor_rect = background.get_rect() #gets the rectangular area of the current background image
        self.floor_rect.y -= 3200
        #self.floor_rect.bottom -= 3560 - resolution.current_h//2 #offsets the map by the differnce between the players centre position and the position of the starting pixel (spawn location)
        #self.floor_rect.left -= 440 - resolution.current_w//2
        #self.end_screen = pygame.image.load('gameover.png') #Commentted out as not in use at the moment


    def camera(self):
        self.floor_rect.center = self.floor_rect.center + player.general_offset #offsets the background image based on the players movements, updates from the centre
        screen.blit(background, self.floor_rect) #draws the background here 

        for sprite in offset_sprites:
            sprite.pos = sprite.pos + player.general_offset #updtates the position of the sprites for when the player moves
            sprite.rect.topleft = sprite.rect.topleft + player.general_offset #offsets the sprite position based on player movement

        for enemy in enemies:
            for destinations in enemy.route:
                destinations[0] = destinations[0] + player.general_offset[0] #offsets the x coordinates in the enemy route lists for when the camera moves
                destinations[1] = destinations[1] + player.general_offset[1] #offsets the y coordinates

    def reset(self):
        self.offset_store = player.total_offset
        player.total_offset = pygame.math.Vector2(0,0)
        
        print(enemy_library)
        enemies.extend(enemy_library)
        for enemy in enemies:
            offset_sprites.add(enemy)
            all_sprites.add(enemy)

        for object in objects:
            #sprite.pos = sprite.pos - self.offset_store
            object.rect.topleft -= self.offset_store

        for enemy in enemies:
            for destinations in enemy.route:
                destinations[0] = destinations[0] - self.offset_store[0] #resets the x coordinates for when a new gane starts
                destinations[1] = destinations[1] - self.offset_store[1] #resets the y coordinates
            enemy.pos = enemy.start_pos #resets enemy position
            enemy.destination = enemy.route[0] 
            
       
        self.floor_rect.center -= self.offset_store
        
        
        




class Object(pygame.sprite.Sprite):
    def __init__(self, position, type, level, rotation):
        super().__init__()
        self.native_level = level #holds the integer passed in as a parameter
        self.pos = (position) #holds the position vector passed in as a parameter
        if rotation == 0:
            self.image = pygame.transform.scale_by(pygame.image.load('Assets\Object images\spr' + type + '.png').convert_alpha(), 5) #scales up image by 5 times, no image rotation
        else:
            self.image = pygame.transform.rotate(pygame.transform.scale_by(pygame.image.load('Assets\Object images\spr' + type + '.png').convert_alpha(), 5), rotation) #scales up image by 5 times, with image rotation

        self.rect = self.image.get_rect(topleft = self.pos)

class Wall(pygame.sprite.Sprite):
    def __init__(self, position, type, level, length):
        super().__init__()
        self.native_level = level
        self.pos = (position)

        if type == 'horizontal_wall': 
            self.surface = pygame.Surface(((length*32), 8)) #creates a surface which is x pixels wide and y pixels tall
            for i in range(0, (length*32), 32): #iterates through the length of the wall that wants to be made - iterates every 32nd pixel as thats where the next image is added to it
                image = pygame.image.load('Assets\Object images\sprWallSoftH.png') #loads the image 
                self.surface.blit(image, (i, 0)) #draws the wall section at the next location (i) within the surface
        
        elif type == 'vertical_wall': 
            self.surface = pygame.Surface((8, (length*32))) #creates a surface which is x pixels wide and y pixels tall
            for i in range(0, (length*32), 32): #iterates through the length of the wall that wants to be made - iterates every 32nd pixel as thats where the next image is added to it
                image = pygame.image.load('Assets\Object images\sprWallSoftV.png') #loads the image 
                self.surface.blit(image, (0, i)) #draws the wall section at the next location (i) within the surface

        self.image = pygame.transform.scale_by(self.surface, 2.5) #scales the image by 2.5 times (because the wall takes up 2 squares but one square is scaled up by 5 times so the wall are scaled up by 5/2 times)
        self.rect = self.image.get_rect(topleft = self.pos) #sets the rect for collisions with the player
        
class Menu(pygame.sprite.Sprite):
    def __init__(self, type, pos):
        super().__init__()
        self.type = type
        self.image = pygame.transform.scale(pygame.image.load("Assets\Menu images\MenuScreen.jpeg"), (resolution.current_w, resolution.current_h)) #sets the background image for the menu
        self.rect = self.image.get_rect(center = (resolution.current_w //2, resolution.current_h//2)) #sets the rect with the centre being the center of the local monitor display
        self.game_over_image = pygame.transform.scale(pygame.image.load("Assets\Menu images\GameOverTemp.png"), (resolution.current_w, resolution.current_h))

        if type == 'new_game':
            self.button_image = pygame.transform.scale_by(pygame.image.load(r"Assets\Menu images\NewGameButton.png").convert_alpha(), 0.3) #sets the image for the button
            self.button_image_original = self.button_image.copy()
            self.button_image_alt = pygame.transform.scale_by(pygame.image.load(r"Assets\Menu images\NewGameButtonAlt.png").convert_alpha(), 0.3) #for when the mouse is hovering over the button
        
        elif type == 'exit':
            self.button_image = pygame.transform.scale_by(pygame.image.load(r"Assets\Menu images\ExitButton.png").convert_alpha(), 0.3)#sets the image for the button
            self.button_image_original = self.button_image.copy()
            self.button_image_alt = pygame.transform.scale_by(pygame.image.load(r"Assets\Menu images\ExitButtonAlt.png").convert_alpha(), 0.3)
        
        self.button_rect = self.button_image.get_rect(center = (pos))

    def button(self):
        global start_game #variable is global because this name wont be used for any other variables in the program and so it can be updated by the class without needing to be passed as a parameter
        self.mouse_coords = pygame.mouse.get_pos() #returns an x and y coordinate for the mouse position
        if self.button_rect.left <= self.mouse_coords[0] <= self.button_rect.right and self.button_rect.top <= self.mouse_coords[1] <= self.button_rect.bottom: 
            self.button_image = self.button_image_alt
            if pygame.mouse.get_pressed() == (1, 0, 0) and self.type == 'new_game' and start_game == False:
            #checks if the mouse is left clicked and if the mouse is on the button
                start_game = True
            elif pygame.mouse.get_pressed() == (1, 0, 0) and self.type == 'new_game' and start_game == True:
                level.reset()
                player.alive = True
            elif pygame.mouse.get_pressed() == (1, 0, 0) and self.type == 'exit':
                pygame.quit()
                sys.exit()
        else:
            self.button_image = self.button_image_original    


R = 10
G = 10
B = 10
def colour_change():
    global R
    global G
    global B
    if R >= 10 and R <= 245:
        R += random.randint(-10,10)
    elif R <= 10:
        R += random.randint(0,10)
    elif R >= 245:
        R += random.randint(-10,0)

    if G >= 10 and G <= 245:
        G += random.randint(-10,10)
    elif G <= 10:
        G += random.randint(0,10)
    elif G >= 245:
        G += random.randint(-10,0)

    if B >= 10 and B <= 245:
        B += random.randint(-10,10)
    elif B <= 10:
        B += random.randint(0,10)
    elif B >= 245:
        B += random.randint(-10,0)


level = Level() #intantiating the level class
player = Player() #intantiating the player class
start = Menu('new_game', (resolution.current_w//2, (resolution.current_h//2 - 120)))
end_new_game = Menu('new_game', ((resolution.current_w//2 + 500), resolution.current_h//2 - 200))
end_exit = Menu('exit', ((resolution.current_w//2 + 500), (resolution.current_h//2 + 150)))

objects = []
collidables = []

collidables.append(Object((2800,320), 'PoolTable', 0, 0))
collidables.append(Object((6720,-320), 'ConferenceTable', 0, 90))
collidables.append(Object((960,0), 'HospitalReception', 0, 90))
collidables.append(Object((960,605), 'HospitalReception', 0, 270))
collidables.append(Object((3600,-800), 'StoreShelf1', 0, 0))
#collidables.append(Object((960,605), 'StoreShelf2', 0, 0))
collidables.append(Object((3760,-760), 'Buffe', 0, 0))
collidables.append(Object((4200,-720), 'BuffePlates', 0, 0))
collidables.append(Object((3840,-400), 'BigTable1', 0, 0)) #top left table
collidables.append(Object((3840,-160), 'BigTable3', 0, 0)) #middle left table
collidables.append(Object((3840,80), 'BigTable4', 0, 0)) #bottom left table
collidables.append(Object((4320,-400), 'BigTable2', 0, 0)) #top right table
collidables.append(Object((4320,-160), 'BigTableBlank', 0, 0)) #middle right table
collidables.append(Object((4320,80), 'BigTable1', 0, 0)) #bottom right tablewa

objects.append(Object((720,0), 'CyanPlant1', 0, 90))
objects.append(Object((720,680), 'CyanPlant1', 0, 270))

#collidables.append(Object((400,400), 'Crate', 0, 0)) #making a crate object on level 0
#objects.append(Object((800,800), 'chest', 0, 0)) #making a chest object on level 0
#objects.append(Object((700,200), 'crate', 0, 0)) 
#objects.append(Object((1000,400), 'crate', 0, 0))
#objects.append(Object((0,0), 'horizontal_wall', 0, 2))
#objects.append(Object((0,0), 'vertical_wall', 0, 10))
#objects.append(Object((1600,0), 'vertical_wall', 0, 4))
#objects.append(Object((1600,480), 'vertical_wall', 0, 4))

horiz_walls = [(Wall((0,0), 'horizontal_wall', 0, 20)), (Wall((1600,-2800), 'horizontal_wall', 0, 10)), (Wall((2400,-2400), 'horizontal_wall', 0, 50)), 
               (Wall((6400,-2800), 'horizontal_wall', 0, 8)), (Wall((2400,-1620), 'horizontal_wall', 0, 22)), (Wall((4800,-1620), 'horizontal_wall', 0, 20)), 
               (Wall((3600,-800), 'horizontal_wall', 0, 7)), (Wall((4800,-800), 'horizontal_wall', 0, 20)), (Wall((7040,-800), 'horizontal_wall', 0, 2)), 
               (Wall((2400,0), 'horizontal_wall', 0, 15)), (Wall((4800,-340), 'horizontal_wall', 0, 20)), (Wall((4800,320), 'horizontal_wall', 0, 20)), 
               (Wall((0,780), 'horizontal_wall', 0, 90)), #This is all of the walls blocking the outside 
               
               (Wall((1600,-1620), 'horizontal_wall', 0, 2)), (Wall((2240,-1620), 'horizontal_wall', 0, 2)), #walls seperating rooms
               (Wall((4160,-1620), 'horizontal_wall', 0, 2)), (Wall((4640,-1620), 'horizontal_wall', 0, 2)), (Wall((4160,-800), 'horizontal_wall', 0, 2)), (Wall((4640,-800), 'horizontal_wall', 0, 2)), #walls seperating rooms
               (Wall((6400,-1620), 'horizontal_wall', 0, 2)), (Wall((6880,-1620), 'horizontal_wall', 0, 2)), (Wall((6400,-800), 'horizontal_wall', 0, 2)), (Wall((6880,-800), 'horizontal_wall', 0, 2)), #walls seperating rooms
               ]

vert_walls = [(Wall((-20,0), 'vertical_wall', 0, 10)), (Wall((1580,-2800), 'vertical_wall', 0, 35)), (Wall((2400,-2800), 'vertical_wall', 0, 5)), 
              (Wall((6380,-2800), 'vertical_wall', 0, 5)), (Wall((7040,-2800), 'vertical_wall', 0, 25)), (Wall((7200,-800), 'vertical_wall', 0, 20)), 
              (Wall((2400,-1600), 'vertical_wall', 0, 20)), (Wall((4140,-1600), 'vertical_wall', 0, 10)), (Wall((4800,-1600), 'vertical_wall', 0, 10)), 
              (Wall((6380,-1600), 'vertical_wall', 0, 10)), (Wall((3580,-800), 'vertical_wall', 0, 10)), (Wall((4800,-320), 'vertical_wall', 0, 8)), 
              (Wall((6380,-320), 'vertical_wall', 0, 8)), #This is all of the walls blocking the outside
              
              (Wall((1580,0), 'vertical_wall', 0, 3)), (Wall((1580,560), 'vertical_wall', 0, 3)), (Wall((2400,0), 'vertical_wall', 0, 3)), (Wall((2400,560), 'vertical_wall', 0, 3)), #walls seperating rooms
              (Wall((2400,-2400), 'vertical_wall', 0, 3)), (Wall((2400,-1840), 'vertical_wall', 0, 3))#walls seperating rooms
              ]

collidables.extend(vert_walls)
collidables.extend(horiz_walls)

objects.extend(collidables)

enemies = []
enemy_library = [Enemy((1800, 600), [[1800, 600], [2200, 600], [2200, -2120], [1800, -2120]], 2, 0),
    Enemy((2200, -2120), [[2200, -2120], [1800, -2120], [1800, 600], [2200, 600]], 2, 0),
    Enemy((3560, 120), [[3560, 120], [2520, 120]], 2, 0),
    Enemy((2520, 680), [[2520, 680], [3560, 680]], 2, 0),
    Enemy((3760, -240), [[3760, -240], [4640, -240]], 2, 0),
    Enemy((4640, 0), [[4640, 0], [3760, 0]], 2, 0)]

enemies.extend(enemy_library)


offset_sprites = pygame.sprite.Group() #sprite group which holds all of the sprites which will move when the player moves
for object in objects:
    offset_sprites.add(object) #adding all the objects in the object list
for enemy in enemies:
    offset_sprites.add(enemy)

all_sprites = pygame.sprite.Group() #sprite group which will hold all of the sprites
all_sprites.add(player)
for sprite in offset_sprites:
    all_sprites.add(sprite) #adding all of the sprites in the offset_sprites group 

while True: #This is the game loop which will run until the game is closed, events is used to check for when the exit button is clicked
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            pygame.quit() #closes the window
            sys.exit() #closes the program
            
    if player.alive == True:
        if start_game == True:
            colour_change()
            screen.fill((R, 0, B))
            #screen.fill('black')
            level.camera()
            all_sprites.update() #calls the update() method of all the sprites
            offset_sprites.draw(screen) #draws all of the sprites to the screen (takes self.image and self.rect as both arguements)
            screen.blit(player.image, player.rect)
            """ for sprite in offset_sprites:
                pygame.draw.rect(screen, "green", sprite.rect, width = 4)
            pygame.draw.rect(screen, player.colour, player.hitbox_rect, width = 4) """  #draws the rect of the player
            #print(player.atk_rect)
            #print(player.angle)
            pygame.draw.rect(screen, "green", player.atk_rect, width = 4)
            #print(player.pos)

            #print(resolution.current_w, resolution.current_h)
            #pygame.draw.rect(screen, "green", screen_rect, width = 4)
        else: 
            screen.blit(start.image, start.rect) #draws the starting menu background image
            screen.blit(start.button_image, start.button_rect) #draws the button image
            start.button() #checks if the user is hovering over the button/has clicked the button

    else:
        #print("test") #test that this is actually working
        screen.blit(end_new_game.game_over_image, ((0,0))) #draws the background image
        screen.blit(end_new_game.button_image, end_new_game.button_rect) #draws the new game button 
        screen.blit(end_exit.button_image, end_exit.button_rect) #draws the exit button
        end_new_game.button() #call the button methods
        end_exit.button()
    pygame.display.update() #updates the screen with all of the changes that happened this tick
    clock.tick(60) #Sets the FPS to 60
        #pygame.quit() #closes the window
        #sys.exit()
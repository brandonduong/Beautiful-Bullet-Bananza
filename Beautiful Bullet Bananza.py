import pygame
import time
import random

BLACK = (0, 0, 0)
GRAY = (211, 211, 211)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_GREEN = (0, 200, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0 ,200)
SKY_BLUE = (153, 194, 255)

#sound_effect = pygame.mixer.Sound("file_name.ogg") #Loads sound

class Game(): #Game Class
    def __init__(self, game_screen):
        """Constructor. Initialize game and variables"""
        self.game_display = game_screen #Game window
        
        self.spaceship = pygame.image.load("pusheen.png") #Loads player ship picture
        self.normal_bullet = pygame.image.load("bullet.png") #Loads normal bullet picture
        self.heart_img = pygame.image.load("heart.png") #Loads heart picture
        self.empty_heart_img = pygame.image.load("emptyheart.png") #Loads empty heart picture
        
        self.player_shoot_sound_list = [] #Player shoot sound list
        self.player_shoot_sound_list.append(pygame.mixer.Sound("player_shoot_1.ogg")) #Loads sound for player bullets
        self.player_shoot_sound_list.append(pygame.mixer.Sound("player_shoot_2.ogg")) #Loads sound for player bullets
        self.player_shoot_sound_list.append(pygame.mixer.Sound("player_shoot_3.ogg")) #Loads sound for player bullets
        self.player_shoot_sound_list.append(pygame.mixer.Sound("player_shoot_4.ogg")) #Loads sound for player bullets
        self.player_shoot_sound_list.append(pygame.mixer.Sound("player_shoot_5.ogg")) #Loads sound for player bullets
        self.player_shoot_sound_list.append(pygame.mixer.Sound("player_shoot_6.ogg")) #Loads sound for player bullets
        #self.background_music = pygame.mixer.Sound("background_music.ogg") #Loads background music
        #self.background_music.play() #Plays background music (30 min)
        
        self.money = 0 #Money
        self.player_health = 5 #Player's health
        self.bullet_damage = 1 #Player's bullet damage
        self.bullet_fire_rate = 50 #Player gun cooldown reset value


        
        self.left_pressed, self.right_pressed, self.up_pressed, self.down_pressed = [False for _ in range(4)] #Arrow key pressed confirmation

        self.player_sprite_list = pygame.sprite.Group() #Player sprites list
        self.player_bullets_list = pygame.sprite.Group() #Player bullet sprites list

        self.enemy_bullets_list = pygame.sprite.Group() #Enemy bullet sprites list

        self.level_list = [] #List of all level objects
        self.level_list.append(Level_01()) #Creates level 1 object
        self.level_list.append(Level_02()) #Creates level 2 object
        self.level_list.append(Level_03()) #Creates level 3 object
        self.level_list.append(Level_04()) #Creates level 4 object
        self.level_list.append(Level_05()) #Creates level 5 object
        self.level_num = 0 #Level num
        self.current_level = self.level_list[self.level_num] #Sets current level

        self.bullet_dmg_dict = {self.current_level.pug_bullet: 1, self.current_level.corgi_bullet: 2, self.current_level.sanic_bullet: 3} #Dictionary with enemy bullet types as keys, damage value as value
        self.enemy_money_dict = {self.current_level.pug: 50, self.current_level.corgi: 200, self.current_level.sanic: 1000} #Dictionary with enemy type as keys, money value as value

        self.player = Player(self.spaceship) #Player class object
        self.player_sprite_list.add(self.player) #Adding player to player sprite list

        pygame.mouse.set_visible(False) #Hide the mouse

        self.bullet_damage_upgrade_cost = 500 #Cost of the bullet damage upgrade
        self.fire_rate_upgrade_cost = 500 #Cost of the fire rate upgrade
        
    def process_events(self):
        """Process and catch all events"""
        for event in pygame.event.get(): #Gets any event happening
            if event.type == pygame.QUIT: #When "x" is clicked
                pygame.quit() #Closes pygame window
                quit() #Closes python in general

            if event.type == pygame.KEYDOWN: #If key being pressed down
                if event.key == pygame.K_LEFT: #Left arrow key
                    self.player.x_change += -8
                    self.left_pressed = True
                if event.key == pygame.K_RIGHT: #Right arrow key
                    self.player.x_change += 8
                    self.right_pressed = True
                if event.key == pygame.K_UP: #Up arrow key
                    self.player.y_change += -8
                    self.up_pressed = True
                if event.key == pygame.K_DOWN: #Down arrow key
                    self.player.y_change += 8
                    self.down_pressed = True
                if event.key == pygame.K_p: #P key
                    self.pause() #Pause the game
                if event.key == pygame.K_SPACE and self.player.gun_cd <= 0: #Spacebar
                    self.bullet = Bullets(self.normal_bullet, self.player.rect.x + 43, self.player.rect.y - 5, -5) #Creates bullet sprite
                    self.player_bullets_list.add(self.bullet) #Adds bullet sprite to all player bullet sprites list
                    self.player.gun_cd = self.bullet_fire_rate #Reset gun cooldown
                    
                    rng = random.randrange(0, len(self.player_shoot_sound_list)) #RNG
                    shoot_sound = self.player_shoot_sound_list[rng] #Random fire sound from sound list
                    shoot_sound.play() #Play player shoot sound
                    
            if event.type == pygame.KEYUP: #After key is pressed down
                if event.key == pygame.K_LEFT and self.left_pressed == True: #Left arrow key
                    self.player.x_change += 8
                    self.left_pressed = False
                if event.key == pygame.K_RIGHT and self.right_pressed == True: #Right arrow key
                    self.player.x_change += -8
                    self.right_pressed = False
                if event.key == pygame.K_UP and self.up_pressed == True: #Up arrow key
                    self.player.y_change += 8
                    self.up_pressed = False
                if event.key == pygame.K_DOWN and self.down_pressed == True: #Down arrow key
                    self.player.y_change += -8
                    self.down_pressed = False

    def game_logic(self):
        """ This method is run every frame.
            Updates things like positions and checks for collisions """
        self.current_level.update(self.player.rect.x) #Update level
        self.player_sprite_list.update() #Move and update player
        self.player_bullets_list.update() #Move and update player bullets
        self.enemy_bullets_list.update() #Move and update enemy bullets
        self.player_sprites_cleanup(self.player_bullets_list, -50) #Clean player bullets up
        self.enemy_sprites_cleanup(self.enemy_bullets_list, 1000) #Clean enemy bullets up
        self.enemy_sprites_cleanup(self.current_level.enemy_list, 1000) #Clean enemy sprites up

        if self.player.gun_cd > 0: #Player shooting bullets
            self.player.gun_cd -= 1
            
        for enemy in self.current_level.enemy_list: #Enemy shooting bullets
            if enemy.rect.y > -100 and enemy.gun_cooldown <= 0: #If enemy is on screen AND gun cd is 0
                self.enemy_bullets_list.add(enemy.fire()) #Shoot a bullet
            elif enemy.rect.y > -100: #If on screen but gun on cooldown, reduce gun cooldown by 1 until it is 0
                enemy.gun_cooldown -= 1       

        for bullet in self.player_bullets_list: #Player bullets hitting enemy ships
            self.bullet_enemy_collision_list = pygame.sprite.spritecollide(bullet, self.current_level.enemy_list, False) #Checks for collisions between enemy ships and player bullets
            if len(self.bullet_enemy_collision_list) > 0: #If a bullet and enemy ship collide
                self.player_bullets_list.remove(bullet) #Delete bullet from travelling forward
                enemies_hit = 0 #To prevent one bullet killing multiple (if in same place)
                for enemy in self.bullet_enemy_collision_list:
                    if enemies_hit == 0:
                        enemy.health -= self.bullet_damage #Reduce enemy health by bullet damage value
                        enemies_hit += 1
                    if enemy.health <= 0: #If enemy has no more health, delete it
                        self.current_level.enemy_list.remove(enemy) #Delete enemy ship
                        self.money += self.enemy_money_dict[enemy.image]
                        
                        
        for bullet in self.enemy_bullets_list: #Enemy bullets hitting player ship
            self.bullet_player_collision_list = pygame.sprite.spritecollide(bullet, self.player_sprite_list, False) #Checks for collisions between player ship and enemy bullets
            if len(self.bullet_player_collision_list) > 0: #If an enemy bullet and player ship collide
                self.enemy_bullets_list.remove(bullet) #Delete enemy bullet
                self.player_health -= self.bullet_dmg_dict[bullet.image] #Player loses health depending on what type of bullet hit by
 
        self.player_collision_list = pygame.sprite.spritecollide(self.player, self.current_level.enemy_list, True) #Checks for collisions between player ship and enemy ships
        if len(self.player_collision_list) > 0: #If player collides into enemy ship
            self.player_health -= len(self.player_collision_list)

        if self.player_health <= 0: #If player has no health
            self.game_over() #Run game over method
            main() #Replay game when game over

        if len(self.current_level.enemy_list) == 0: #If current level has no more enemies
            self.level_num += 1 #Advance to next level
            self.current_level = self.level_list[self.level_num] #Sets current level
            self.bullet_dmg_dict = {self.current_level.pug_bullet: 1, self.current_level.corgi_bullet: 2} #Dictionary with enemy bullet types as keys, damage value as value
            self.enemy_money_dict = {self.current_level.pug: 50, self.current_level.corgi: 200} #Dictionary with enemy type as keys, money value as value
            self.new_level() #Signifies new level has been reached
            self.upgrade_shop()
                
                

    def draw_frame(self, screen):
        """Displays and draws everything to screen"""
        screen.fill(WHITE) #Background white
        #self.upgrade_shop() #TO TEST SHOP
        self.current_level.draw(screen)
        self.player_sprite_list.draw(screen) #Draw all sprites in list to screen
        self.player_bullets_list.draw(screen) #Draw all player bullets
        self.enemy_bullets_list.draw(screen) #Draw all enemy bullets
        
        self.level_display() #Displays current level number
    
        self.health_display() #Displays current health
        self.money_display() #Displays current money
        
        #Draw above comment
        pygame.display.update() #Draws everything

    def pause(self):
        pause = True
        font = pygame.font.Font("freesansbold.ttf", 115)
        text = font.render("Pause", True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = ((600, 400)) #X and y
        self.game_display.blit(text, text_rect)
        pygame.display.update()

        while pause == True:
            for event in pygame.event.get(): #Gets any event happening
                if event.type == pygame.QUIT: #When "x" is clicked
                    pygame.quit() #Closes pygame window
                    quit() #Closes python in general

                if event.type == pygame.KEYDOWN: #If key being pressed down
                    if event.key == pygame.K_p: #P key
                        pause = False #Pause the game
            

    def game_over(self):
        """Handles player game over"""
        self.health_display()
        font = pygame.font.Font("freesansbold.ttf", 115)
        text = font.render("Game Over", True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = ((600, 400)) #X and y
        self.game_display.blit(text, text_rect)
        pygame.display.update()
        time.sleep(2)

    def level_display(self):
        """Displays player's current level"""
        font = pygame.font.Font("freesansbold.ttf", 30)
        text = font.render("Current Level: " + str(self.level_num + 1), True, BLACK)
        self.game_display.blit(text, (0, 0))

    def new_level(self):
        """Signifies when new level has been reached"""
        font = pygame.font.Font("freesansbold.ttf", 115)
        text = font.render("Level " + str(self.level_num + 1), True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = ((600, 400)) #X and y
        self.game_display.blit(text, text_rect)
        pygame.display.update()
        time.sleep(2)

    def health_display(self):
        """Displays player's current health"""
        full_counter = self.player_health
        for i in range(0, 425, 85):
            if full_counter > 0:
                self.game_display.blit(self.heart_img, (i, 730))
                full_counter -= 1
            else:
                self.game_display.blit(self.empty_heart_img, (i, 730))

    def money_display(self):
        font = pygame.font.Font("freesansbold.ttf", 30)
        text = font.render("Money: " + str(self.money), True, BLACK)
        self.game_display.blit(text, (0, 30))

    def player_sprites_cleanup(self, sprite_list, boundary):
        """Deletes player bullets that go off screen"""
        for sprite in sprite_list:
            if sprite.rect.y < boundary:
                sprite_list.remove(sprite)

    def enemy_sprites_cleanup(self, sprite_list, boundary):
        """Deletes enemy sprites that go off screen"""
        for sprite in sprite_list:
            if sprite.rect.y > boundary:
                sprite_list.remove(sprite)

    def upgrade_shop(self):
        """Upgrade shop screen"""
        shop_buttons_list = pygame.sprite.Group() #Sprite group list of all buttons in shop
        
        buy_power_upgrade = Button(GREEN, 180, 156, 100, 100, 1, self.bullet_damage_upgrade_cost) #Buying bullet power upgrade
        shop_buttons_list.add(buy_power_upgrade) #Add button to all button list

        buy_fire_rate_upgrade = Button(GREEN, 180, 284, 100, 100, 2, self.fire_rate_upgrade_cost) #Buying fire rate upgrade
        shop_buttons_list.add(buy_fire_rate_upgrade) #Add button to all button list

        exit_shop = Button(GREEN, 375, 672, 450, 100, 3, 0) #Buying fire rate upgrade
        shop_buttons_list.add(exit_shop) #Add button to all button list

        self.cursor_group = pygame.sprite.Group() #Player cursor list
        self.cursor = Cursor(self.normal_bullet) #Cursor class object
        self.cursor_group.add(self.cursor)

        Shopping = True #Player still shopping
        while Shopping == True: #Shop loop runs til exit shop
            clicked = False
            for event in pygame.event.get(): #Gets any event happening
                if event.type == pygame.QUIT: #When "x" is clicked
                    pygame.quit() #Closes pygame window
                    quit() #Closes python in general
                if event.type == pygame.MOUSEBUTTONUP: #If mouse click
                    clicked = True

            self.cursor.update() #Updates player's cursor

            for cursor in self.cursor_group:
                button_collision_list = pygame.sprite.spritecollide(cursor, shop_buttons_list, False) #Checks for collisions between buttons and player cursor
                for button in shop_buttons_list: #Check every button
                    if button in button_collision_list: #If button is colliding with mouse cursor
                        if button.update(clicked) == True and self.money >= button.cost: #Turn button dark green + When button is clicked
                            self.money -= button.cost #Subtract money when buying
                            if button.identity == 1: #Buying bullet damage upgrade
                                self.bullet_damage += 1 #Upgrade + 1
                                self.bullet_damage_upgrade_cost += 500 #Increase next upgrade by 500
                                button.cost = self.bullet_damage_upgrade_cost

                            elif button.identity == 2: #Buying fire rate upgrade
                                self.bullet_fire_rate -= 5
                                self.fire_rate_upgrade_cost += 500
                                button.cost = self.fire_rate_upgrade_cost\

                            elif button.identity == 3: #Exiting shop
                                Shopping = False
                                self.player.x_change = 0 #X pos changing speed
                                self.player.y_change = 0 #Y pos changing speed
                    else:
                        button.inactive() #Turn button green

            self.game_display.fill(WHITE) #Background white
            pygame.draw.rect(self.game_display, GRAY, (150, 0, 900, 800)) #Gray shop background
            pygame.draw.rect(self.game_display, SKY_BLUE, (180, 28, 840, 100))
            self.message_display("Pusheen Pilot Upgrade Shop!", 200, 50, 56) #Upgrade Shop Title

            self.message_display("Money: " + str(self.money), 510, 630, 30) #Money Display

            self.message_display("Bullet Damage Upgrade! / Cost: " + str(self.bullet_damage_upgrade_cost) , 300, 185, 40) #Bullet damage upgrade title
            self.message_display("Current Bullet Damage: " + str(self.bullet_damage) , 302, 220, 18) #Current bullet damage title

            self.message_display("Fire Rate Upgrade! / Cost: " + str(self.fire_rate_upgrade_cost) , 300, 313, 40) #Fire rate upgrade title
            self.message_display("Current Fire Rate: " + str(self.bullet_fire_rate) , 302, 348, 18) #Current fire rate title
            
            shop_buttons_list.draw(self.game_display) #Draw all buttons 
            self.message_display("Exit Shop!", 475, 700, 50) #Exit shop title
            
            self.cursor_group.draw(self.game_display) #Draws player's cursor on screen
            pygame.display.update()

    def message_display(self, msg, x, y, size):
        """Displays custom messages at x and y of font size, size"""
        font = pygame.font.Font("freesansbold.ttf", size)
        text = font.render(msg, True, BLACK)
        self.game_display.blit(text, (x, y))





class Cursor(pygame.sprite.Sprite): #Cursor Class, Parent Sprite
    def __init__(self, image):
        super().__init__()
        self.image = image #Picture for player sprite
        self.rect = self.image.get_rect() #Rectangle for sprite (Holds dimensions and has attributes x coord, y coord)
        self.rect.x = 575 #Starting x pos
        self.rect.y = 625 #Starting y pos

    def update(self): #Updates position of player
        mouse_pos = pygame.mouse.get_pos() #Gets position of mouse
        self.rect.x = mouse_pos[0] #x
        self.rect.y = mouse_pos[1] #y

class Button(pygame.sprite.Sprite): #Button Class, Parent Sprite
    def __init__(self, colour, x_pos, y_pos, width, height, identity, cost):
        super().__init__()
        self.image = pygame.Surface([width, height]) #Creates blank 100 x 100 square
        self.image.fill(colour) #Fills blank square with said colour
        self.rect = self.image.get_rect() #Gets rectangle (Holds dimensions, x coord, y coord)
        self.rect.x = x_pos #x coord
        self.rect.y = y_pos #y coord
        self.identity = identity
        self.cost = cost

    def update(self, clicked): #Updates button when active
        self.image.fill(DARK_GREEN)
        if clicked == True: #If mouse is clicked
            return True
        else:
            return False

    def inactive(self):
        """Updates button when inactive"""
        self.image.fill(GREEN)
            
        

class Player(pygame.sprite.Sprite): #Player Class, Parent Sprite
    def __init__(self, image):
        super().__init__()
        self.image = image #Picture for player sprite
        self.rect = self.image.get_rect() #Rectangle for sprite (Holds dimensions and has attributes x coord, y coord)
        self.rect.x = 575 #Starting x pos
        self.rect.y = 625 #Starting y pos
        self.x_change = 0 #X pos changing speed
        self.y_change = 0 #Y pos changing speed
        self.gun_cd = 0 #Initial gun cooldown

    def update(self): #Updates position of player
        if self.rect.x >= 0 and self.x_change < 0 or self.rect.x <= 1111 and self.x_change > 0: #X coord boundaries
            self.rect.x += self.x_change #Move left and right

        if self.rect.y >= 0 and self.y_change < 0 or self.rect.y <= 645 and self.y_change > 0: #Y coord boundaries
            self.rect.y += self.y_change #Move up and down

class Bullets(pygame.sprite.Sprite): #Bullet Class, Parent Sprite
    def __init__(self, img, x, y, speed):
        super().__init__()
        self.image = img #Picture for bullet sprite
        self.rect = self.image.get_rect()
        self.rect.x = x #Starting x pos
        self.rect.y = y #Starting y pos
        self.speed = speed

    def update(self): #Updates position of bullet
        self.rect.y += self.speed #Rate of movement of bullet

class Enemy(pygame.sprite.Sprite): #Enemy Class, Parent Sprite
    def __init__(self, ship_image, bullet_image, x , y, health, speed_off, speed_on_1, speed_on_2, refresh, ai):
        super().__init__()
        self.image = ship_image #Picture for enemy sprite
        self.bullet_image = bullet_image #Picture for enemy bullet
        self.rect = self.image.get_rect() #Rectangle for sprite (Holds dimensions and has attributes x coord, y coord)
        self.rect.x = x #Initial x pos
        self.rect.y = y #Initial y pos
        self.speed_off = speed_off #Speed off screen
        self.speed_on_start = speed_on_1 #Speed in phase 1
        self.speed_on_mid = speed_on_2 #Speed in phase 2
        self.health = health #Enemy health
        self.gun_refresh_time = refresh #Initial gun refresh time
        self.gun_cooldown = 0
        self.phase = 1 #Set path phase number WIP
        self.ai = ai #Set level of ai of enemy WIP

    def update(self, player_x): #Updates position of enemy
        if self.rect.y < 0: #Speed if offscreen
            self.rect.y += self.speed_off
        elif 170 > self.rect.y >= 0: #Speed if onscreen in beggining
            self.rect.y += self.speed_on_start
        elif self.rect.y >= 170: #Speed if onscreen in middle
            self.rect.y += self.speed_on_mid

        if self.ai == 2:
            if player_x < self.rect.x: #If enemy is to the right of player, move left
                self.rect.x -= 2 #Move left by 2 pixels
            elif player_x > self.rect.x: #If enemy is to the left of player, move right
                self.rect.x += 2 #Move right by 2 pixels

    def fire(self): #Firing bullets
        enemy_bullet = Bullets(self.bullet_image, self.rect.x + 40, self.rect.y + 85, 8)
        self.gun_cooldown = self.gun_refresh_time
        return enemy_bullet #Return enemy_bullet class sprite

    
        

class Level(): #Level class, parent of all level classes
    def __init__(self):
        """Constructor. Initializes everything needed for levels"""
        self.enemy_list = pygame.sprite.Group() #All enemies in level list
        #self.enemy_bullet_list = pygame.sprite.Group() #All bullets from enemies
        self.background = None #Background image if needed

        #Load all enemy pictures
        self.pug = pygame.image.load("pug.png") #Image for pug enemies
        self.corgi = pygame.image.load("corgi.png") #Image for corgi enemies
        self.sanic = pygame.image.load("sanic.png") #Image for sanic enemies

        self.pug_bullet = pygame.image.load("pug_bullet.png") #Loads pug bullet picture
        self.corgi_bullet = pygame.image.load("corgi_bullet.png") #Loads corgi bullet picture
        self.sanic_bullet = pygame.image.load("sanic_bullet.png") #Loads sanic bullet picture

    def update(self, player_x):
        """Updates everything in the level"""
        self.enemy_list.update(player_x)

    def draw(self, screen):
        """Draw everything in the level"""
        self.enemy_list.draw(screen)

    def level_maker(self, level):
        """Converts the level array to enemy ship placements and creation"""
        for enemy in level: #Go through the array above and add enemies
            item = Enemy(enemy[0], enemy[1], enemy[2], enemy[3], enemy[4], enemy[5], enemy[6], enemy[7], enemy[8], enemy[9]) #Creates multiple enemy objects
            self.enemy_list.add(item) #Adds all enemy objects to enemy_list

class Level_01(Level):
    """Level 1"""
    def __init__(self):
        """Initializing level 1"""
        super().__init__()
        
        level = [[self.pug, self.pug_bullet, 300, -600, 1, 2, 3, 1, 150, 1], [self.pug, self.pug_bullet, 810, -600, 1, 2, 3, 1, 150, 1],
                 [self.pug, self.pug_bullet, 500, -800, 1, 2, 1, 3, 150, 1], [self.pug, self.pug_bullet, 610, -800, 1, 2, 1, 3, 150, 1],
                 [self.pug, self.pug_bullet, 555, -900, 1, 2, 2, 2, 150, 1], [self.pug, self.pug_bullet, 100, -1200, 1, 2, 2, 2, 150, 1],
                 [self.pug, self.pug_bullet, 1010, -1200, 1, 2, 2, 2, 150, 1], [self.pug, self.pug_bullet, 0, -1500, 1, 2, 2, 2, 150, 1],
                 [self.pug, self.pug_bullet, 122, -1500, 1, 2, 2, 2, 150, 1], [self.pug, self.pug_bullet, 244, -1500, 1, 2, 2, 2, 150, 1],
                 [self.pug, self.pug_bullet, 366, -1500, 1, 2, 2, 2, 150, 1], [self.pug, self.pug_bullet, 488, -1500, 1, 2, 2, 2, 150, 1],
                 [self.pug, self.pug_bullet, 610, -1500, 1, 2, 2, 2, 150, 1], [self.pug, self.pug_bullet, 732, -1500, 1, 2, 2, 2, 150, 1],
                 [self.pug, self.pug_bullet, 854, -1500, 1, 2, 2, 2, 150, 1], [self.pug, self.pug_bullet, 976, -1500, 1, 2, 2, 2, 150, 1],
                 [self.pug, self.pug_bullet, 1098, -1500, 1, 2, 2, 2, 150, 1]] #Array with image, x coord, and y coord, and health

        self.level_maker(level)

class Level_02(Level):
    """Level 2"""
    def __init__(self):
        """Initializing level 1"""
        super().__init__()
        
        level = [[self.pug, self.pug_bullet, 300, -600, 1, 2, 3, 1, 150, 1], [self.pug, self.pug_bullet, 810, -600, 1, 2, 3, 1, 150, 1],
                 [self.corgi, self.corgi_bullet, 525, -600, 3, 1.5, 1, 1, 300, 1], [self.corgi, self.corgi_bullet, 200, -900, 3, 1.5, 1, 1, 300, 1],
                 [self.corgi, self.corgi_bullet, 850, -900, 3, 1.5, 1, 1, 300, 1], [self.corgi, self.corgi_bullet, 525, -900, 3, 1.5, 1, 1, 300, 1],
                 [self.corgi, self.corgi_bullet, 0, -1800, 3, 1.5, 1, 3, 300, 1],
                 [self.corgi, self.corgi_bullet, 262, -1900, 3, 1.5, 1, 3, 300, 1], [self.corgi, self.corgi_bullet, 525, -2000, 3, 1.5, 1, 3, 300, 1],
                 [self.corgi, self.corgi_bullet, 787, -2100, 3, 1.5, 1, 3, 300, 1], [self.corgi, self.corgi_bullet, 1050, -2200, 3, 1.5, 1, 3, 300, 1]] #Array with image, x coord, and y coord, and health
        
        self.level_maker(level)

class Level_03(Level): #ship_image, bullet_image, x , y, health, speed_off, speed_on_1, speed_on_2, refresh)
    """Level 3"""
    def __init__(self):
        """Initializing level 1"""
        super().__init__()
        
        level = [[self.pug, self.pug_bullet, 0, -600, 1, 2, 1, 1, 150, 1], [self.pug, self.pug_bullet, 240, -600, 1, 2, 1, 1, 150, 1],
                 [self.pug, self.pug_bullet, 480, -600, 1, 2, 1, 1, 150, 1], [self.pug, self.pug_bullet, 720, -600, 1, 2, 1, 1, 150, 1],
                 [self.pug, self.pug_bullet, 960, -600, 1, 2, 1, 1, 150, 1],
                 
                 [self.pug, self.pug_bullet, 120, -1200, 1, 2, 1, 1, 150, 1], [self.pug, self.pug_bullet, 360, -1200, 1, 2, 1, 1, 150, 1],
                 [self.pug, self.pug_bullet, 600, -1200, 1, 2, 1, 1, 150, 1], [self.pug, self.pug_bullet, 840, -1200, 1, 2, 1, 1, 150, 1],
                 [self.pug, self.pug_bullet, 1080, -1200, 1, 2, 1, 1, 150, 1],

                 [self.pug, self.pug_bullet, 0, -1800, 1, 2, 1, 1, 150, 1], [self.pug, self.pug_bullet, 240, -1800, 1, 2, 1, 1, 150, 1],
                 [self.pug, self.pug_bullet, 480, -1800, 1, 2, 1, 1, 150, 1], [self.pug, self.pug_bullet, 720, -1800, 1, 2, 1, 1, 150, 1],
                 [self.pug, self.pug_bullet, 960, -1800, 1, 2, 1, 1, 150, 1],
                 
                 [self.pug, self.pug_bullet, 120, -2700, 1, 2, 2, 3, 150, 1], [self.pug, self.pug_bullet, 360, -2700, 1, 2, 2, 3, 150, 1],
                 [self.pug, self.pug_bullet, 600, -2700, 1, 2, 2, 3, 150, 1], [self.pug, self.pug_bullet, 840, -2700, 1, 2, 2, 3, 150, 1],
                 [self.pug, self.pug_bullet, 1080, -2700, 1, 2, 2, 3, 150, 1],

                 [self.pug, self.pug_bullet, 0, -3000, 1, 2, 2, 3, 150, 1], [self.pug, self.pug_bullet, 240, -3000, 1, 2, 2, 3, 150, 1],
                 [self.pug, self.pug_bullet, 480, -3000, 1, 2, 2, 3, 150, 1], [self.pug, self.pug_bullet, 720, -3000, 1, 2, 2, 3, 150, 1],
                 [self.pug, self.pug_bullet, 960, -3000, 1, 2, 2, 3, 150, 1],
                 
                 [self.pug, self.pug_bullet, 120, -3300, 1, 2, 2, 3, 150, 1], [self.pug, self.pug_bullet, 360, -3300, 1, 2, 2, 3, 150, 1],
                 [self.pug, self.pug_bullet, 600, -3300, 1, 2, 2, 3, 150, 1], [self.pug, self.pug_bullet, 840, -3300, 1, 2, 2, 3, 150, 1],
                 [self.pug, self.pug_bullet, 1080, -3300, 1, 2, 2, 3, 150, 1]] #Array with image, x coord, and y coord, and health
        
        self.level_maker(level)

        #boss = Enemy(image, bullet_pic, 555, -2200, 300, 2, 2, 2, 25) #CREATING BOSS, WIP, create boss class?
        #self.enemy_list.add(boss)

class Level_04(Level):
    """Level 4"""
    def __init__(self):
        """Initializing level 1"""
        super().__init__()
        ez = [[self.pug, self.pug_bullet, 555, -600 - i, 1, 2, 1, 1, 150, 2] for i in range (0, 50, 5)]
        ez.append([self.pug, self.pug_bullet, -1800, -1400, 1, 2, 1, 1, 150, 2])
        ez.append([self.pug, self.pug_bullet, 2900, -1400, 1, 2, 1, 1, 150, 2])
        level = ez #Array with image, x coord, and y coord, and health
        
        self.level_maker(level)

class Level_05(Level):
    """Level 5"""
    def __init__(self):
        """Initializing level 1"""
        super().__init__()
        
        level = [[self.pug, self.pug_bullet, 500, -800, 1, 2, 2, 3, 150, 1], [self.pug, self.pug_bullet, 610, -800, 1, 2, 2, 3, 150, 1],
                 [self.pug, self.pug_bullet, 555, -900, 1, 2, 2, 3, 150, 1],

                 [self.pug, self.pug_bullet, 100, -1000, 1, 2, 2, 3, 150, 1], [self.pug, self.pug_bullet, 210, -1000, 1, 2, 2, 3, 150, 1],
                 [self.pug, self.pug_bullet, 155, -1100, 1, 2, 2, 3, 150, 1],

                 [self.pug, self.pug_bullet, 810, -1000, 1, 2, 2, 3, 150, 1], [self.pug, self.pug_bullet, 920, -1000, 1, 2, 2, 3, 150, 1],
                 [self.pug, self.pug_bullet, 865, -1100, 1, 2, 2, 3, 150, 1],

                [self.corgi, self.corgi_bullet, 2750, -1600, 3, 2, 1, 0, 300, 2], [self.corgi, self.corgi_bullet, -1700, -1600, 3, 2, 1, 0, 300, 2],
                
                 [self.sanic, self.sanic_bullet, 555, -2300, 15, 2, 0, 0, 75, 2],

                 [self.pug, self.pug_bullet, 0, -2500, 1, 2, 0, 0, 150, 1], [self.pug, self.pug_bullet, 240, -2600, 1, 2, 0, 0, 150, 1],
                 [self.pug, self.pug_bullet, 480, -2700, 1, 2, 0, 0, 150, 1], [self.pug, self.pug_bullet, 720, -2800, 1, 2, 0, 0, 150, 1],
                 [self.pug, self.pug_bullet, 960, -2900, 1, 2, 0, 0, 150, 1],

                 [self.corgi, self.corgi_bullet, 525, -2900, 3, 2, 0, 0, 300, 1], [self.corgi, self.corgi_bullet, 200, -3200, 3, 2, 0, 0, 300, 1],
                 [self.corgi, self.corgi_bullet, 850, -3200, 3, 2, 0, 0, 300, 1],
                 
                 [self.pug, self.pug_bullet, 120, -3000, 1, 2, 0, 0, 150, 1], [self.pug, self.pug_bullet, 360, -3100, 1, 2, 0, 0, 150, 1],
                 [self.pug, self.pug_bullet, 600, -3200, 1, 2, 0, 0, 150, 1], [self.pug, self.pug_bullet, 840, -3300, 1, 2, 0, 0, 150, 1],
                 [self.pug, self.pug_bullet, 1080, -3400, 1, 2, 0, 0, 150, 1],
                 
                [self.corgi, self.corgi_bullet, 2750, -2700, 3, 2, 1, 0, 300, 2], [self.corgi, self.corgi_bullet, -1700, -2700, 3, 2, 1, 0, 300, 2],

                 [self.pug, self.pug_bullet, 37, -4000, 1, 2, 0, 0, 150, 1], [self.pug, self.pug_bullet, 277, -4200, 1, 2, 0, 0, 150, 1],
                 [self.pug, self.pug_bullet, 517, -4300, 1, 2, 0, 0, 150, 1], [self.pug, self.pug_bullet, 757, -4400, 1, 2, 0, 0, 150, 1],
                 [self.pug, self.pug_bullet, 997, -4500, 1, 2, 0, 0, 150, 1],

                 [self.pug, self.pug_bullet, 157, -4600, 1, 2, 0, 0, 150, 1], [self.pug, self.pug_bullet, 397, -4700, 1, 2, 0, 0, 150, 1],
                 [self.pug, self.pug_bullet, 637, -4800, 1, 2, 0, 0, 150, 1], [self.pug, self.pug_bullet, 877, -4900, 1, 2, 0, 0, 150, 1],
                 [self.pug, self.pug_bullet, 1117, -5000, 1, 2, 0, 0, 150, 1]

                 
                 ] #Array with image, x coord, and y coord, and health
        
        self.level_maker(level)


def main():
    """Main Function for the game"""
    pygame.init()

    #Setting width and height of screen
    DISPLAY_WIDTH = 1200
    DISPLAY_HEIGHT = 800

    game_display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT)) #Sets screen
    pygame.display.set_caption("Spaceship Bullet Hell Game") #Sets window title
    clock = pygame.time.Clock() #Used to manage how fast screen updates

    game = Game(game_display) #Create object Game (Initializes variables, game)

    while True: #GAME LOOP
        game.process_events() #Process events method (Keys, mouse clicks, etc)

        game.game_logic() #Updates object positions and checks for collisions

        game.draw_frame(game_display) #Draw and print frame

        clock.tick(60) #Manage fps


if __name__ == "__main__":
    main()

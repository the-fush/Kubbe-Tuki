import pygame
from pygame.locals import *
import csv, os
import random as r
from math import sin, cos, atan2, sqrt, modf, pi, degrees
from time import time

import ctypes
def readData() -> dict:
    with open("data.txt","r") as file:
        return eval(file.read())
def writeData(write) -> None:
    with open("data.txt", "w") as file:
        file.write(write)
def fade(self, fadelevel):
    bg = pygame.surface.Surface((self.rect.width, self.rect.height))
    bg.blit(DISPSURF.subsurface((self.x-scrollX, self.y), (self.img.get_width(), self.img.get_height())), (0,0))
    bg.fill((255,255,255,fadelevel/100*255))
    try:
        bg.blit(self.image, self.rect)
    except AttributeError:
        bg.blit(self.img, self.rect)
    return bg.copy()
def findOverlap(self, colision):
    overlapRects = [r.clip(colision.rect) for r in tuple(self.hitboxes.values())]
    overlapAreas = [r.width * r.height for r in overlapRects]
    
    overlapAreas[2] += 0.0001
    overlapAreas[3] += 0.0001

    colisionSide = ("left", "right", "top", "bottom")[overlapAreas.index(max(overlapAreas))]

    return overlapAreas, colisionSide

def tick():
    global running, scrollX, actualX, paused
    for event in pygame.event.get():
        if event == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()
            player.pressed(event.key)
        if event.type == pygame.KEYUP:
            player.unpressed(event.key)
    if not paused:
        player.keyPressed["lmouse"], player.keyPressed["rmouse"] = pygame.mouse.get_pressed()[0], pygame.mouse.get_pressed()[2]
        if player.keyPressed["lmouse"]: player.activate_skill("bo")
        if player.keyPressed["rmouse"]:
            player.activate_skill("so")
    #    DISPSURF.fill((50,50,255))

    DISPSURF.blit(BACKGROUND_IMG, (0-scrollX/12,0))
    if (scrollX/12)-WIDTH>BACKGROUND_IMG.get_width():
        DISPSURF.blit(BACKGROUND_IMG, ((0-scrollX/12)+BACKGROUND_IMG.get_width(),0), pygame.rect.Rect(0,0,WIDTH,HEIGHT))
        DISPSURF.blit(BACKGROUND_IMG, ((0-scrollX/12)+(BACKGROUND_IMG.get_width()*2),0), pygame.rect.Rect(0,0,WIDTH,HEIGHT))
    try:
        for i in range(int(0-scrollX/6) % -BACKGROUND_IMG_2.get_width(),int(0-scrollX/6) % BACKGROUND_IMG_2.get_width()+(BACKGROUND_IMG_2.get_width()*3),BACKGROUND_IMG_2.get_width()):
            if (0-scrollX/6)+i > WIDTH:
                break
            DISPSURF.blit(BACKGROUND_IMG_2, (((0-scrollX/6)+i,300)))        
    except NameError:
        pass
    if player.health>0:
        DISPSURF.blit(pygame.transform.scale(pygame.image.load(os.path.join(UI_DIR, f"health{min(player.health, 5)}.png")), (150,150)), (0,0))
    else:
        if player.deadCounter == 0:
            SFX["lose"].play()

        player.state = "death"
        if player.deadCounter < 170:
            player.frame = 1
        else:
            player.frame = 2
        player.keyPressed = dict(zip(player.keyPressed.keys(), [False]*len(player.keyPressed)))
        player.deadCounter += 1
    
    if player.deadCounter == 0:
        actualX = 0
        scrollX = (player.x-(WIDTH/2)+(player.image.get_width()/2))
        try:
            origActualX = actualX+0
        except NameError:
            pass
        if scrollX<levelEnd-WIDTH-TILE_SIZE:
            actualX = (((player.x-(WIDTH/2)+(player.image.get_width()/2))-scrollX)/5*4)
        else:
            actualX = (((player.x-(WIDTH/2)+(player.image.get_width()/2))-scrollX)/5*4) + (TILE_SIZE*0.75)
        if scrollX<levelEnd-WIDTH-TILE_SIZE:
            scrollX += ((player.x-(WIDTH/2)+(player.image.get_width()/2))-scrollX)/5
        
        #Preventing over-scrolling
        scrollX = max(0, scrollX)
        if scrollX>levelEnd-WIDTH:
            scrollX = levelEnd-WIDTH
            actualX += 1

                    



    #player tick
    player.onGround = False
    if not paused:
        player.gravity()
        player.update_hitboxes()
        collideList = pygame.sprite.spritecollide(player,tileGroup, False)
        for colision in collideList:
            if player.isHurt:
                player.isHurt = False
                player.invinciblility = 100

            overlapAreas, colisionSide = findOverlap(player, colision)

            
            
            if colision.interactable:
                colision.interact(dy=player.dy, top=colision.rect.collidepoint(player.rect.centerx, player.y - player.image.get_width()*0.5), side=colisionSide)
            if colision.coltype == "none":
                continue
            if colisionSide=="left":
                if colision.coltype != "lower":
                    player.dx = 0
                    player.speed = 0
                    player.x = colision.x + colision.image.get_width()
            elif colisionSide == "right":
                if colision.coltype != "lower":
                    player.dx = 0
                    player.speed = 0
                    player.x = colision.x - player.image.get_width()
            elif colisionSide == "bottom":
                if colision.coltype != "lower" or player.dy < 0:
                    if colision.rect.collidepoint(player.rect.centerx, player.y + player.image.get_width()*1.5):
                        player.dy = -1
                        player.y = colision.rect.y - player.image.get_height()
                        player.onGround = True
                else: pass
            elif colisionSide == "top":
                if colision.coltype != "lower" and overlapAreas[3]/(player.rect.width*player.rect.height)*100<30:
                    if colision.rect.collidepoint(player.rect.centerx, player.y - player.image.get_width()*0.5):
                        player.y = colision.y + colision.image.get_height()
                        player.dy = -5 
        
        

        player.control()
        player.runSkill()
    
    #tile tick
    tileGroup.update()
    
    player.draw()
    
    #Particles tick
    #tileGroup.draw(DISPSURF)
    particles.update()

    if not paused:
        #Projectiles tick
        projectileGroup.update()

        #enemy tick
        enemyGroup.update()
    if player.winCounter > 500:
        player.winCounter += 1  
        tro("out", min((player.winCounter-500)*1.2, 100))
        paused = True
        if player.winCounter >= 650:
            if player.winCounter == 650:
                global gameEnd
                gameEnd = time()
                SFX["results"].play()
                SFX["results"].play(-1)
                data = readData()
                if data["curLvl"] == currentCourse:
                    if [f for f in os.listdir(MAP_DIR) if f"{currentCourse[0]}-{int(currentCourse[2:])+1}.csv" in f]:
                        data["curLvl"] = f"{currentCourse[0]}-{int(currentCourse[2:])+1}"
                    else:
                        data["curLvl"] = f"{int(currentCourse[0])+1}-1"
                    writeData(str(data))
            print(player.winCounter)
            DISPSURF.blit(FONT.render(f"Time taken: {int((gameEnd-gameStart)/60)}:{round((gameEnd-gameStart) % 60, 3)}", False, (255,255,255)), (200,200))
            if player.winCounter >= 1000:
                SFX["results"].fadeout(1)
                
                if player.winCounter == 1100:
                    running = False

                
    elif player.winCounter > 0:
        player.winCounter += 1  
def getCorner(self, side=""):
    if side == "tl":
        return (self.x, self.y)
    elif side == "tr":
        return (self.x + self.image.get_width(), self.y)
    elif side == "bl":
        return (self.x, self.y + self.image.get_height())
    elif side == "br":
        return (self.x + self.image.get_width(), self.y + self.image.get_height())

def tro(way="out", percentage=100):
    tro = pygame.surface.Surface((WIDTH, HEIGHT))
    tro.fill((0,0,0))
    DISPSURF.blit(tro, (0,HEIGHT*(100-percentage)/100))
def draw(self):
    DISPSURF.blit(self.image, (self.x-scrollX, self.y))
def getMask(selfSurface):
    return pygame.mask.from_surface(selfSurface).to_surface()
def center(obj):
    return (obj.x+(obj.img.get_width()/2),obj.y+(obj.img.get_height()/2))
def dist(obj1, obj2):
    return sqrt(((obj1[0]-obj2[0])**2)+((obj1[1]-obj2[1])**2))
def colision(self, target, **kwargs):
    selfPos = {"x1":self.x,
                "y1":self.y,
                "x2":self.x+self.image.get_width(),
                "y2":self.y+self.image.get_height()}
    targetPos = {"x1":target.x,
                    "y1":target.y,
                    "x2":target.x+target.img.get_width(),
                    "y2":target.y+target.img.get_height()}
    isPlayer = type(self)==Player
    if isPlayer and abs(center(self)[0]-center(target)[0])>abs(center(target)[1]-center(target)[1]):
        kwargs["axis"] = "x"
    elif isPlayer:
        kwargs["axis"] = "y"


    #check the colision, axis==y             =>   like this 
    if (selfPos["x1"] >= targetPos["x1"] and selfPos["x1"] <= targetPos["x2"]):
        if (
            selfPos["y1"] >= targetPos["y1"] and selfPos["y1"] <= targetPos["y2"]
        ) or (
            selfPos["y2"] >= targetPos["y1"] and selfPos["y2"] <= targetPos["y2"]
        ):
            return True
    if targetPos["x1"] >= selfPos["x1"] and targetPos["x1"] <= selfPos["x2"]:
        if (
            targetPos["y1"] >= selfPos["y1"] and targetPos["y1"] <= selfPos["y2"]
        ) or (
            targetPos["y2"] >= selfPos["y1"] and targetPos["y2"] <= selfPos["y2"]
        ):
            return True
    return False
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        self.x, self.y = x, y
        if type(image) == list:
            self.images = [img.convert_alpha() for img in image]
            self.frame = 0
            self.image = self.images[self.frame]
        else:
            self.image = image.convert_alpha()
        
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        super().__init__()
class Bullet(Projectile):
    def __init__(self, x, y, image, way, speed):
        Projectile.__init__(self, x, y, image)
        self.dx = self.dy = 0
        if way=="up":
            self.dy = speed
            self.image = pygame.transform.rotate(self.image, -90)
        else:
            self.dx = speed
            if way == "left":
                self.image = pygame.transform.rotate(self.image, -180)
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.x += self.dx
        self.y -= self.dy
        for enemy in pygame.sprite.spritecollide(self, enemyGroup, False):
            enemy.hurt(2)
            particles.add(Hitspark(self.x, self.y, PARTICLE_IMGS["hitspark.png"], 90))
            self.kill()
        DISPSURF.blit(self.image, (self.x-scrollX, self.y))
class SpikeProjectile(Projectile):
    def __init__(self, x, y, image, dir, speed):
        Projectile.__init__(self, x, y, image)
        self.dx = self.dy = 0
        self.dir = dir
        self.dx = sin(dir)*speed
        self.dy = cos(dir)*speed
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.x += self.dx
        self.y -= self.dy
        if pygame.sprite.spritecollide(self, [player], False):
            player.hurt(2, (self.x, self.y))
        if not 0<self.x-scrollX<WIDTH or not 0<self.y<HEIGHT:
            self.kill()
            pass
        DISPSURF.blit(pygame.transform.rotate(self.image, 0-(self.dir-90)), (self.x-scrollX, self.y))
class Firewave(Projectile):
    def __init__(self, x, y, image, dir, speed):
        Projectile.__init__(self, x, y, image)
        self.dx = self.dy = 0
        self.dir = dir
        self.maxSpeed = speed
        self.speed = 0
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.speed = min(self.speed + 1, self.maxSpeed)
        self.dx = sin(self.dir)*self.speed
        self.dy = cos(self.dir)*self.speed
        self.x += self.dx
        self.y -= self.dy
        if pygame.sprite.spritecollide(self, [player], False):
            player.hurt(1, (self.x, self.y))
        if not 0<self.x-scrollX<WIDTH or not 0<self.y<HEIGHT:
            self.kill()
            pass
        DISPSURF.blit(pygame.transform.rotate(self.image, 0-(self.dir-90)), (self.x-scrollX, self.y))
class Apple(Projectile):
    def __init__(self, x, y, image, dir, speed):
        Projectile.__init__(self, x, y, image)
        self.dx = self.dy = 0
        self.dir = dir
        self.dx = -abs(sin(dir)*speed)
        self.dy = cos(dir)*speed
        self.hit = False
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.x += self.dx
        self.y -= self.dy
        if pygame.sprite.spritecollide(self, [player], False):
            player.hurt(1, (self.x  , self.y))
        try:
            boss = [s for s in enemyGroup.sprites() if type(s) == Whispy][0]
            if hasattr(boss, "mask") and self.hit and pygame.mask.from_surface(self.image).overlap(boss.mask, (boss.x-self.x, boss.y-self.y)):
                boss.hurt(10000)
                boss.x += 2
                self.kill()
            if self.y>HEIGHT:
                self.kill()
        except IndexError:
            self.kill()
            #pass
        DISPSURF.blit(pygame.transform.rotate(self.image, (self.dir)), (self.x-scrollX, self.y))
class Root(Projectile):
    def __init__(self, x, y, image):
        Projectile.__init__(self, x, y, image)
        self.attack = -TILE_SIZE
    def update(self):
        self.attack += 1
        if self.attack > 0:
            if self.attack == 1:
                self.ox = self.x + 0
                self.oy = self.y + 0
            if 1 < self.attack < 6:
                self.x += r.randint(-4,4)
                self.y -= r.randint(-4,4)
            if self.attack > 6:
                self.x, self.y = self.ox, self.oy
                if self.attack == 20:
                    self.kill()
            if pygame.sprite.spritecollide(self, [player], False):
                player.hurt(1, (self.x, self.y))
            
        else:
            self.y -= 1

        
        DISPSURF.blit(pygame.transform.chop(self.image, pygame.rect.Rect(self.x, HEIGHT-(TILE_SIZE*3), self.image.get_width(), TILE_SIZE)), (self.x-scrollX, self.y))

class Bone(Projectile):
    def __init__(self, x, y, image, dir, origin):
        Projectile.__init__(self, x, y, image)
        self.dx = self.dy = 0
        self.origin = origin
        self.movedir = dir
        self.wave = 0
        self.lifespan = 0
        self.dir = r.randint(0,360)
        self.range = 400
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())    
        self.wave += 0.1
        self.dir += 1
        
        if pygame.sprite.spritecollide(self, [player], False):
            player.hurt(1, (self.x, self.y))
        
        self.lifespan += 1
        if self.lifespan > 350:

            self.dy -= 0.3
            #self.dx *= 0.8
            self.y -= self.dy
            self.x += self.dx
        self.lifespan += 1
        if self.lifespan > 300:
            self.dy -= 0.3
            #self.dx *= 0.8
            self.y -= self.dy
            self.x += self.dx
        elif self.lifespan < 300:
            
            self.x = self.origin.x + (sin(self.wave)*200*sin(self.movedir))
            self.y = self.origin.y + (sin(self.wave)*200*cos(self.movedir))
        if  not 0 < self.y < HEIGHT or not 0 < self.x < WIDTH:
            self.kill()
            

        DISPSURF.blit(pygame.transform.rotate(self.image, self.dir-90), (self.x-scrollX, self.y))

class Gasterblaster(Projectile):
    def __init__(self, image):
        #self.wave = 0
        #self.lifespan = 0
        self.dir = r.randint(0,360)
        #self.x = WIDTH/2
        #self.y = HEIGHT/2
        #while 0 < self.x < WIDTH or 0 < self.y < HEIGHT:
        #    self.x += sin(180-self.dir)
        #    self.y -= cos(180-self.dir)
        #self.speed = 0
        #self.slow = False
        self.x, self.y = r.randint(0,WIDTH), r.randint(0, HEIGHT)
        self.dx = self.dy = 0
        self.i = 0
        Projectile.__init__(self, self.x, self.y, image)

    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())    
        
        #if (0 < self.x < WIDTH or 0 < self.y < HEIGHT) and not self.slow:
        #    self.speed += 1
        #    self.slow = True
        #elif self.slow:
        #    self.speed -= 1
        if self.i < 30:
            self.i += 1
            self.dx = sin(self.dir)
            self.dy = cos(self.dir)
        else:
            self.dx = self.dy = 0
            projectileGroup.add(Beam(self.rect.centerx, self.rect.centery, ))
            
        self.x += self.dx
        self.y -= self.dy

        DISPSURF.blit(pygame.transform.rotate(self.image, 90 - self.dir), (self.x-scrollX, self.y))
class Beam(Projectile):
    def __init__(self, x, y, image, dir):
        Projectile.__init__(self, x, y, image)
        self.dir = dir
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())    
        DISPSURF.blit(pygame.transform.rotate(self.image, 90 - self.dir), (self.x-scrollX, self.y))
        
class Questionblock(Projectile):
    def __init__(self, x, y, image, dx, dy):
        Projectile.__init__(self, x, y, image)
        self.dx, self.dy = dx, dy
        self.dir = dir
        self.dir = 0
        self.hit = False
        self.hitFrame = 0
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.dy -= 0.3
        if self.dx > 0:
            self.dir += 3
        else:
            self.dir -= 3
        if pygame.sprite.spritecollide(self, [player], False):
            if player.dy > 7:
                if not self.hit:
                    SFX["block"].play()
                self.hit = True
                self.dy = 20
                self.dx = 0
                
            elif not self.hit:
                player.hurt(1, (self.x, self.y)) 
                self.kill()
        if pygame.sprite.spritecollide(self, [BOSS], False) and self.hit:
            BOSS.hurt(10000)
            self.kill()


        self.x += self.dx
        self.y -= self.dy

        if self.y > HEIGHT:
            self.kill()

        DISPSURF.blit(pygame.transform.rotate(self.image, self.dir), (self.x-scrollX, self.y))
class Explosion(Projectile):
    def __init__(self, cx, cy, image):
        Enemy.__init__(self, cx-(image.get_width()/2), cy-(image.get_height()/2), image)
        self.rect.bottomright = cx, cy
        self.boomFrame = 2
        self.i = 0.02
        SFX["explode"].play()
        self.hits = []
    def update(self):
        self.boomFrame -= self.i
        self.i += 0.01

        if self.boomFrame > 0:     
            showImage = pygame.transform.scale_by(self.image, self.boomFrame)
            self.rect = pygame.rect.Rect(self.x, self.y, showImage.get_width(), showImage.get_height())
            if pygame.mask.from_surface(showImage).overlap(pygame.mask.from_surface(player.image), (player.x - self.x, player.y - self.y)) and player not in self.hits:
                player.hurt(2, self.rect.center)
                self.hits.append(player)
            for en in [e for e in enemyGroup.sprites() if type(e) not in [CrystalOfMultiverses, Explosion]]:
                if pygame.mask.from_surface(showImage).overlap(pygame.mask.from_surface(en.image), (en.x - self.x, en.y - self.y)) and en not in self.hits:
                    en.hurt(4)
                    self.hits.append(en)
            self.rect.center = self.x, self.y
            DISPSURF.blit(showImage, (self.rect.left-scrollX, self.rect.top))
        else:
            self.kill()

class Bomb(Projectile):
    def __init__(self, x, y, image, dx, dy):
        Projectile.__init__(self, x, y, image)
        self.dx, self.dy = dx, dy
        self.dir = 0
        self.hit = False
        self.blow = 0
        
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.dy -= 0.3
        if self.dx > 0:
            self.dir += 3
        else:
            self.dir -= 3
        
        if pygame.sprite.spritecollide(self, [t for t in tileGroup.sprites() if type(t) == Grass], False) and not self.hit:
            self.dy = 12
            self.hit = True
        if self.hit:
            self.blow += 1
        if self.blow > 30:
            projectileGroup.add(Explosion(self.rect.centerx, self.rect.centery, PROJECTILE_IMGS["explosion"]))
            self.kill()


        self.x += self.dx
        self.y -= self.dy

        if self.y > HEIGHT:
            self.kill()

        DISPSURF.blit(pygame.transform.rotate(self.image, self.dir), (self.x-scrollX, self.y))

class Arrow(Projectile):
    def __init__(self, x, y, image, dir, speed):
        Projectile.__init__(self, x, y, image)
        self.dx = self.dy = 0
        self.dir = dir
        self.dx = sin(dir)*speed
        self.dy = cos(dir)*speed
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

        if pygame.sprite.spritecollide(self, [player], False):
            player.hurt(2, (self.x, self.y))
        if not 0<self.x-scrollX<WIDTH or not 0<self.y<HEIGHT:
            self.kill()
            pass
        showImg = self.image.copy()
        DISPSURF.blit(pygame.transform.rotate(self.image, (self.dir-90)), (self.x-scrollX, self.y))

class menuObj:
    def __init__(self, x, y, img):
        self.x, self.y = x, y
        if type(img)==list:
            self.imgs = [i.convert_alpha() for i in img]
            self.img = self.imgs[0]
        else:
            self.img = img
        try:
            self.rect = pygame.Rect(self.x-menuScroll, self.y, self.img.get_width(), self.img.get_height())
        except NameError:
            self.rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        self.img.convert_alpha()
    def setTarget(self, tx, ty, speed):
        self.tx, self.ty, self.speed = tx, ty, speed
    def move(self):
        self.x += (self.tx-self.x)/(100-self.speed)
        self.y += (self.ty-self.y)/(100-self.speed)        
    def draw(self):
        try:
            if self is test:
                DISPSURF.blit(self.img, ((self.x-menuScroll) % self.img.get_width()-self.img.get_width(), self.y))
                DISPSURF.blit(self.img, ((self.x-menuScroll) % self.img.get_width(), self.y))
                DISPSURF.blit(self.img, ((self.x-menuScroll) % self.img.get_width()+self.img.get_width(), self.y))
            else:
                DISPSURF.blit(self.img, ((self.x-menuScroll), self.y))
        except NameError:
            DISPSURF.blit(self.img, ((self.x), self.y))
class Button(menuObj):
    def __init__(self, x, y, img, menu):
        menuObj.__init__(self, x, y, img)
        self.hover = False
        self.size = 0
        self.menu = menu
    def onHover(self):
        try:
            self.rect = pygame.Rect(self.x-menuScroll, self.y, self.img.get_width(), self.img.get_height())
        except NameError:
            self.rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if self.rect.collidepoint(*pygame.mouse.get_pos()):
            if not self.hover:
                self.hover = True          
                SFX["hover"].play()
            self.img = self.imgs[1]
            if pygame.mouse.get_pressed()[0]:
                global curMenu
                curMenu = f"{self.menu}"
                changeMenu()
                return True
            #self.rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())    
            #self.x, self.y = self.rect.center


        else:
            if self.hover:
                self.hover = False
            self.rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())    
            self.img = self.imgs[0]
class Text(menuObj):
    def __init__(self,x,y, text):
        self.text = text
        self.x = x
        self.y = y
        #set font from system
        self.font = pygame.font.SysFont("BLOXAT", 50)
        self.fontSize = 24
        #counter for blinking
        self.counter = 0
        self.colorCounter = 0
    def write(self):
        DISPSURF.blit(self.font.render(self.text, False, (0,0,0)), (self.x-menuScroll, self.y))
        #          ^^^^^^^^^^^^^^^^^           ^^^^^                 ^^^^
        #        built-in text build func    parameters            position

class Hitbox(pygame.sprite.Sprite):
    def __init__(self, rect):
        self.rect = rect
        self.x, self.y = self.rect.x, self.rect.y
        #self.image = pygame.Surface((self.rect.width, self.rect.height))
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        try:
            super().__init__(enemyGroup)
        except TypeError:
            pygame.sprite.Sprite.__init__(self, enemyGroup)
        self.x, self.y = x, y
        self.images = img
        self.frame = 0
        self.move = True
        self.dead = False
        if type(img) in (tuple, list):
            self.images = [i.convert_alpha() for i in img]
            self.frame = 0
            self.image = self.images[self.frame]
        else:
            self.image = img.convert_alpha()
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.onGround = False
    def doColision(self):
        global tileGroup
        self.onGround = False
        self.hitboxes = {"left":pygame.Rect(*getCorner(self, "tl"), self.image.get_width()/2, self.image.get_height()),
                        "right":pygame.Rect(getCorner(self, "tl")[0] + self.image.get_width()/2, getCorner(self, "tl")[1], self.image.get_width()/2, self.image.get_height()),
                        "top":pygame.Rect(*getCorner(self, "tl"), self.image.get_width(), self.image.get_height()/2),
                        "bottom":pygame.Rect(getCorner(self, "tl")[0], getCorner(self, "tl")[1]+self.image.get_height()/2, self.image.get_width(), self.image.get_height()/2)}
        collideList = pygame.sprite.spritecollide(self,tileGroup, False)
        for colision in collideList:
            if colision.coltype == "none":
                continue
            
            overlapAreas, colisionSide = findOverlap(self, colision)
            
            if colisionSide=="left":
                if colision.coltype != "lower":
                    self.dx = 0
                    self.x = colision.x + colision.image.get_width()
            elif colisionSide == "right":
                if colision.coltype != "lower":
                    self.dx = 0
                    self.x = colision.x - self.image.get_width()
            elif colisionSide == "bottom":
                if colision.coltype != "lower" or self.dy < 0:
                    if colision.rect.collidepoint(self.rect.centerx, self.y + self.image.get_width()*1.5):
                        self.dy = -1
                        self.y = colision.rect.y - self.image.get_height()
                        self.onGround = True
                else: pass
            elif colisionSide == "top":
                if colision.coltype != "lower":
                    if colision.rect.collidepoint(self.rect.centerx, self.y - self.image.get_width()*0.5):
                        self.y = colision.y + colision.image.get_height()
                        self.dy = -5
    def hurt(self, hp):
        if type(self) in [Whispy, Molduga, CrystalOfMultiverses]:
            if abs(hp) > 100:
                self.hp -= hp
            if type(self) == Whispy:
                self.frame = len(self.images)-2
                self.cooldown = 100
            elif type(self) == Molduga:
                self.damaged = True
            elif type(self) == CrystalOfMultiverses:
                SFX["crack"].play()
                if 40000 <= self.hp:
                    self.phase = 0
                elif 20000 <= self.hp:
                    self.phase = 1
                elif 0 < self.hp:
                    self.phase = 2
                self.damaged = True

        else:
            self.hp -= hp
        if self.hp <= 0:
            if type(self) == Whispy:
                pygame.mixer.music.fadeout(10)
                self.frame = len(self.images)-1
                self.cooldown = 9999999999999
            elif type(self) == Molduga:
                self.dead = True
            elif type(self) == CrystalOfMultiverses:
                self.kill()
                pygame.mixer.music.fadeout(1)
                for _ in range(10):
                    particles.add(Crystalbreak(*self.rect.center, PARTICLE_IMGS["crystalbreak.png"], r.randint(-90, 90)))
                player.winCounter += 1
                    
            else:    
                self.dead = True
                self.kill()
class Glubo(Enemy):
    def __init__(self, x, y, img):
        Enemy.__init__(self, x, y, img)
        self.wave = 0
        self.dx = self.dy = 0
        self.hp = 10
    def update(self):
        global scrollX, tileGroup, player
        
        if self.move and not self.dead:
            self.rect = pygame.Rect(self.x, self.y, self.images[0].get_width(), self.images[0].get_height())
            if dist((self.x, self.y), (player.x, player.y))>500:
                self.wave += 0.016
                self.dx += sin(self.wave)/10
            else:
                self.wave = 0
                if player.rect.centerx>self.rect.centerx:
                    self.dx += 0.2
                else:
                    self.dx -= 0.2
            


            self.doColision()
            if self.onGround:
                if player.rect.centery < self.rect.centery and dist((self.x, self.y), (player.x, player.y))<500:
                    self.dy = 4
            else:
                self.dy -= 0.3

            self.frame += 0.05
            if self.frame > 1.5: self.frame = 0
    
            if self.rect.colliderect(player.rect):
                player.hurt(1, (self.rect.centerx, self.rect.centery))
        
        self.x += self.dx
        self.y -= self.dy        
        self.dx *= 0.95
        
        if self.dx > 0:
            DISPSURF.blit(self.images[round(self.frame)], (self.x-scrollX, self.y))
        else:
            DISPSURF.blit(pygame.transform.flip(self.images[round(self.frame)], True, False), (self.x-scrollX, self.y))

class Bumblebee(Enemy):
    def __init__(self, x, y, img):
        Enemy.__init__(self, x, y, img)
        self.dx = self.dy = 0
        self.charge = 0
        self.dir = 90
        self.hp = 6
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if self.move and not self.dead:

            self.doColision()
            if getDist(self.x, player.x, self.y, player.y) > 500:
                self.x += sin(self.dir)*2
                self.y -= cos(self.dir)*2
                self.dir += 0.025
                self.frame += 0.2
                self.frame = self.frame % 2
            else:
                self.charge = 31
                self.dir = 180-atan2(-(self.y-player.y), self.x-player.x)
                self.frame = 2
                if self.charge > 30:
                    self.x += sin(self.dir)*5
                    self.y -= cos(self.dir)*5
                if pygame.sprite.spritecollide(self, [player], False):
                    player.hurt(1, (self.x, self.y))
             
            if sin(self.dir) > 0:
                DISPSURF.blit(self.images[int(self.frame)], (self.x-scrollX, self.y))
            else:
                DISPSURF.blit(pygame.transform.flip(self.images[int(self.frame)], True, False), (self.x-scrollX, self.y))
class Hedgehog(Enemy):
    def __init__(self, x, y, image):
        Enemy.__init__(self, x, y, image)
        self.wave = 0
        self.hp = 8
        self.dx = self.dy = 0
        self.defense = False
    def update(self):
        if self.move and not self.dead:
            self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
            if dist((self.x, self.y), (player.x, player.y))>500:
                self.defense = False
                self.wave += 0.016
                self.dx += sin(self.wave)/10
                self.frame += 0.05
                if self.frame > 1.5: self.frame = 0
            else:
                if not self.defense:
                    self.dy = 3
                    #70 x 7
                    projectileGroup.add(*(SpikeProjectile(self.rect.left - 70, self.rect.centery-7, PROJECTILE_IMGS["spike"], -90, 7),
                                          SpikeProjectile(self.rect.left - 70, self.rect.centery-70, PROJECTILE_IMGS["spike"], -45,7),
                                          SpikeProjectile(self.rect.centerx-7, self.rect.centery-70, PROJECTILE_IMGS["spike"], 0,  7),
                                          SpikeProjectile(self.rect.right, self.rect.centery-70, PROJECTILE_IMGS["spike"], 45,     7),
                                          SpikeProjectile(self.rect.right, self.rect.centery-70, PROJECTILE_IMGS["spike"], 90,     7)))
                    self.defense = True
                self.wave = 0
                self.frame = 2
            

            self.doColision()
            if self.onGround:
                if player.rect.centery < self.rect.centery and dist((self.x, self.y), (player.x, player.y))<500 and not self.defense:
                    self.dy = 4
            else:
                self.dy -= 0.3

    
            if self.rect.colliderect(player.rect):
                player.hurt(1, (self.rect.centerx, self.rect.centery))
        
        self.x += self.dx
        self.y -= self.dy        
        self.dx *= 0.95
        
        if self.dx > 0:
            DISPSURF.blit(self.images[round(self.frame)], (self.x-scrollX, self.y))
        else:
            DISPSURF.blit(pygame.transform.flip(self.images[round(self.frame)], True, False), (self.x-scrollX, self.y))
class Skeleton(Enemy):
    def __init__(self, x, y, img):
        Enemy.__init__(self, x, y, img)
        self.wave = 0
        self.dx = self.dy = 0
        self.hp = 10
        self.charge = 0
        
    def update(self):
        global scrollX, tileGroup, player
        
        if self.move and not self.dead:
            self.rect = pygame.Rect(self.x, self.y, self.images[0].get_width(), self.images[0].get_height())
            if getDist(self.x, player.x, self.y, player.y)>500:
                self.wave += 0.016
                self.dx += sin(self.wave)/10

                self.frame += 0.05
                self.frame = self.frame % 2
            else:
                if self.charge > 30:
                    self.charge = -50
                    if self.dx > 0:
                        side = (self.rect.right,self.rect.centery-50)
                    else:
                        side = (self.rect.left-80,self.rect.centery-50)
                    way = r.randint(-180,180)
                    projectileGroup.add(Bone(*side, PROJECTILE_IMGS["bone"], way, self))
                elif self.charge < 0:
                    self.frame = int(self.charge/10)+2
            self.charge += 1
            
        self.doColision()
        if self.onGround:
            pass
        else:
            self.dy -= 0.3
    
        if self.rect.colliderect(player.rect):
            player.hurt(1, (self.rect.centerx, self.rect.centery))
        
        self.x += self.dx
        self.y -= self.dy        
        self.dx *= 0.95
        
        if not self.onGround:
            self.dy 
        if self.dx > 0:
            DISPSURF.blit(self.images[int(self.frame)], (self.x-scrollX, self.y))
        else:
            DISPSURF.blit(pygame.transform.flip(self.images[int(self.frame)], True, False), (self.x-scrollX, self.y))
class Whispy(Enemy):
    def __init__(self, x, y, image):
        Enemy.__init__(self, x, y, image)
        self.x = 0
        self.y = 0
        self.charges = {"blow":r.randint(0,60), "apple":r.randint(0,40), "root":r.randint(0,60)}
        self.hp = 30000
        self.cooldown = 0
        
    
    def update(self):
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.mask = pygame.mask.from_surface(self.image)

        if self.cooldown > 0:
            if self.cooldown > 10000: self.cooldown += 1
            self.cooldown -= 1
            if self.cooldown == 1:
                self.frame = 0
        else:
            for skill, charge in self.charges.items():
                if skill == "blow":
                    if charge > 200 and False:
                        self.frame = 1
                        player.dx -= 5
                        self.x += r.randint(-10, 10)
                        #self.y -= r.randint(-10, 10)
                        if charge > 240:
                            self.charges[skill] = r.randint(0,10)
                            self.frame = 0
                            self.x = self.y = 0

                elif skill == "apple":
                    if charge > 150:
                        projectileGroup.add(Apple(r.randint(int(WIDTH/2), int(WIDTH)), -83, PROJECTILE_IMGS["apple"], r.randint(-180,-90), 10))
                        if charge > 160:
                            self.charges[skill] = 0
                elif skill == "root":
                    if charge > 200:
                        projectileGroup.add([Root(x+(TILE_SIZE*int(r.randint(0,1))), HEIGHT-(TILE_SIZE*2), PROJECTILE_IMGS["root"]) for x in range(0,TILE_SIZE*20, TILE_SIZE*2)])
                        self.charges[skill] = 0
                self.charges[skill] += 1
        if player.x>self.x+(self.image.get_width()*0.6) and self.cooldown < 10000:
            player.x = self.x+(self.image.get_width()*0.6)
        DISPSURF.blit(self.images[int(self.frame)], (self.x-scrollX, self.y))
        #DISPSURF.blit(self.mask.to_surface(), (self.x-scrollX, self.y))
class Molduga(Enemy):
    def __init__(self, x, y, image):
        Enemy.__init__(self, x, y, image)
        self.dx = self.dy = 0
        self.jumpCounter = -100
        self.jumpType = 0
        self.dir = 90
        self.flip = False
        self.way = 1
        self.wave = 180
        self.groundLevel = TILE_SIZE*10
        self.y = self.groundLevel - 169
        self.mask = pygame.mask.from_surface(self.images[0])
        self.hp = 40000
        self.damaged = False
        self.dead = False
    def update(self):
        if player.x > 3000 and not self.dead:
            player.x = 3000
        if self.damaged or self.dead:
            self.dx = 0
            self.dy -= 0.3
            self.dir = -90
            if self.dead and self.y >= self.groundLevel - self.image.get_height():
                self.y = self.groundLevel - self.image.get_height()
            if self.dead and self.y > self.groundLevel:
                self.kill()
                del self
                
        else:
            #vvv please uncomment after presenting
            #self.jumpCounter += ((5-(self.hp/10000))/2)+0.5
            
            self.jumpCounter += 1
            self.rect = pygame.Rect(self.x, self.y, self.images[int(self.frame)].get_width(), self.images[int(self.frame)].get_height())

            self.hitboxes = {"left":pygame.Rect(*getCorner(self, "tl"), self.image.get_width()/2, self.image.get_height()),
                    "right":pygame.Rect(getCorner(self, "tl")[0] + self.image.get_width()/2, getCorner(self, "tl")[1], self.image.get_width()/2, self.image.get_height()),
                    "top":pygame.Rect(*getCorner(self, "tl"), self.image.get_width(), self.image.get_height()/2),
                    "bottom":pygame.Rect(getCorner(self, "tl")[0], getCorner(self, "tl")[1]+self.image.get_height()/2, self.image.get_width(), self.image.get_height()/2)}
            
            if self.jumpCounter > 200:
                if self.jumpCounter == 201:
                    self.y = self.groundLevel - 200
                if self.jumpType == 0:
                    if self.jumpCounter == 201:
                        self.dy = 20
                        if self.way == 1: 
                            self.dir = -135
                        else:
                            self.dir = -45
                    self.dy -= 0.2
                    
                    
                    self.dir += self.way
                    #2000 line celebration :DDDD
                else:
                    if self.jumpCounter == 201:
                        self.dy = 10
                    self.dy -= 0.2
                if self.y > self.groundLevel:
                    for _ in range(int(300*abs(self.dy) * (1-(int(self.jumpType == 1)*0.4)))):
                        particles.add(SandParticle(r.randint(self.rect.left, self.rect.right), self.groundLevel, PARTICLE_IMGS["sand.png"], r.randint(-90,90)))
                    if [type(t) for t in tileGroup.sprites()].count(SandGeyser) >= 5:
                        for tt, t in [(type(t), t) for t in tileGroup.sprites()]:
                            if tt==SandGeyser:
                                t.lower()
                                break
    
                    tileGroup.add(SandGeyser(self.rect.centerx, r.randint(520, 800), TILES_IMGS["sg"]))
                    self.dy = 0
                    self.jumpCounter = r.randint(-50,0)
            
            if self.y > self.groundLevel - 169 and self.jumpCounter < 160:
                self.dy += 0.3
            else:
                if self.jumpCounter < 160:
                    self.dy = 0
                    self.y = self.groundLevel - 169
                elif self.jumpCounter < 200:

                    #choose jumptype
                    if self.jumpCounter == 161:
                        self.jumpType = r.randint(0,1)
                    
                    if self.jumpType == 0:
                        self.dy = -3
                    else:
                        self.dy = 2
                
            #if self.y >= self.groundLevel-169:
            if self.x < 0:
                self.way = 1
            elif self.x > 3000:
                self.way = -1
                
                
            self.flip = self.way == -1
                

            if self.hp >= 40000:
                self.dx += 5 * self.way * 0.7
            elif self.hp >= 30000:
                self.dx += 5 * self.way * 1
            elif self.hp >= 20000:
                self.dx += 5 * self.way * 1.3
            elif self.hp >=10000:
                self.dx += 5 * self.way * 1.6

            if player.deadCounter == 0 and self.mask.overlap(pygame.mask.from_surface(player.image), (player.x-self.x, player.y-self.y)):
                overlapSide = findOverlap(player, self)\

                if (-135<self.dir<-45) and self.jumpType == 0 and overlapSide[1] == "top":
                    self.hurt(10000)
                else:
                    player.hurt(2, self.rect.center)                    

        if self.y >= self.groundLevel-169:
            if self.damaged:
                if self.hp > 0:
                    for _ in range(1000):
                        particles.add(SandParticle(r.randint(self.rect.left, self.rect.right), self.groundLevel, PARTICLE_IMGS["sand.png"], r.randint(-90,90)))
                    self.damaged = False

                    for sg in [t for t in tileGroup.sprites() if type(t) == SandGeyser]:
                        sg.lower()

                    self.dy = 0
                else:
                    self.y = self.groundLevel - self.image.get_height()
                    self.dir = 180
                    self.dy = -2
            if self.dir > 93:
                self.dir -= 3
            elif self.dir < 87:
                self.dir += 3
            elif abs(self.dir-90) < 3 and self.dir != 90:
                self.dir = 90

        self.x += self.dx
        self.y -= self.dy
        self.dx *= 0.6
        
        showImg = self.images[int(self.frame)]
        if self.flip or self.jumpCounter>200 and self.jumpType==0:
            showImg = pygame.transform.flip(showImg, False, True)
            showImg = pygame.transform.rotate((showImg), self.dir+90)
        else:
            showImg = pygame.transform.rotate((showImg), self.dir-90)
        
        self.mask = pygame.mask.from_surface(showImg)

        DISPSURF.blit(showImg, (self.x-scrollX, self.y),pygame.rect.Rect(0,0, self.images[0].get_width(), ((self.groundLevel))-self.y))
        #pygame.draw.rect(DISPSURF, (255,0,255), pygame.rect.Rect(self.hitboxes["top"].x-scrollX, self.hitboxes["top"].y, self.hitboxes["top"].width, self.hitboxes["top"].height))

class CrystalOfMultiverses(Enemy):
    def __init__(self, x, y, image):
        Enemy.__init__(self, x, y, image)
        self.dx = self.dy = 0
        self.x = WIDTH-TILE_SIZE
        self.y = 200
        self.wave = 180
        self.phase = 0
        self.skills = {"projectile1":0,"enemy":0, "pound":0}
        self.i = 0
        self.cooldown = 0
        self.dir = 0
        self.hp = 50000
        self.damaged = False
        #self.hurt(500000)
    def update(self):
        #update rect
        self.rect = pygame.rect.Rect(self.x, self.y, self.images[0].get_width(), self.images[0].get_height())
        
        #update
        if self.damaged:
            self.x += r.randint(-5,5)
            self.y -= r.randint(-5,5)
            self.cooldown += 1
            if self.cooldown > 14:
                self.cooldown = 0
                self.damaged = False
        else:
            if self.phase == 0:
                self.wave += 0.02
                self.dx = sin(self.wave)*15
                
                #damage player
                if pygame.sprite.spritecollide(self, [player], False):
                    player.hurt(1, (self.x, self.y))
                
                #skill
                self.skills["projectile1"] += 1
            elif self.phase == 1:
                if self.skills["pound"] < 1000:
                    self.wave += 0.02
                    self.x =(WIDTH/2) + sin(self.wave)*WIDTH/3
                    self.y = (HEIGHT/3) - cos(self.wave)*HEIGHT/3.5
                else:
                    self.hurt(5000)
                    self.skills["pound"] = 0

                #skill
                self.skills["projectile1"] += 1
                self.skills["enemy"] += 1
                self.skills["pound"] += 1
            elif self.phase == 2:
                if self.skills["pound"] < 1000:
                    self.wave += 0.02
                    self.x =(WIDTH/2) + sin(self.wave)*WIDTH/3
                    self.y = (HEIGHT/3) - cos(self.wave)*HEIGHT/3.5
                else:
                    self.hurt(5000)
                    self.skills["pound"] = 0

                #skill
                self.skills["projectile1"] += 2
                self.skills["enemy"] += 2
                self.skills["pound"] += 2
            player.hp = 6
            player.invinciblility = 100
            for n, charge in self.skills.items():
                if n=="projectile1":
                    if 100 < charge < 107:
                        self.frame = 1
                    elif 107 < charge:
                        self.frame = 0
                        if charge == 108:
                            if self.phase == 0:
                                self.i = r.randint(1, 3)
                            elif self.phase == 1:
                                self.i = r.randint(2, 3)

                            self.dir = r.randint(-135, 135)
                        if self.i == 1:
                            projectileGroup.add(Questionblock(*self.rect.center, PROJECTILE_IMGS["qblock"], r.randint(-15, 15), 7))
                            self.skills["projectile1"] = 50
                        elif self.i == 2:
                            for _ in range(r.randint(2, 3)):
                                projectileGroup.add(Bomb(*self.rect.center, PROJECTILE_IMGS["bomb"], r.randint(-10, 10), 7))
                            self.skills["projectile1"] = 0
                        elif self.i == 3:
                            if (charge - 107) % 6 == 0:
                                for _ in range(r.randint(1,3)):
                                    projectileGroup.add(Firewave(*self.rect.center, PROJECTILE_IMGS["firewave"], r.randint(-10, 10), 7))
                                if charge > 167:
                                    self.skills["projectile1"] = -20  
                elif n=="enemy":
                    if 100 < charge < 107:
                        self.frame = 1
                    elif 107 < charge:
                        self.frame = 0
                        en = r.choice(["gb", "h"])

                        enemyGroup.add(ENEMIES[en](*self.rect.center, ENEMIES_IMGS[en]))
                        self.skills["enemy"] = -500
                        if r.randint(0,3) == 0:
                            tileGroup.add(Collectable(*self.rect.center, TILES_IMGS["co"]))
                elif n=="pound":
                    if 1000 < charge < 1007:
                        self.frame = 1
                    elif 1007 < charge:
                        pass
                        
                        


        self.x += self.dx
        self.y -= self.dy
        #draw
        DISPSURF.blit(self.images[self.frame], (self.x-scrollX, self.y))
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self, particles)
        self.x, self.y = x, y
        if type(img) == list:
            self.images = [i.convert_alpha() for i in img]
            self.frame = 0
            self.image = self.images[self.frame]
        else:
            self.image = img
            self.image.convert_alpha()
        self.rect = pygame.Rect(*getCorner(self, "tl"), *getCorner(self, "br"))
        self.dx = self.dy = 0
        # self.image = img
        # self.type = moveType
        # self.dir = moveDir
        # self.doSpin = doSpin
        # self.speed = moveSpd
        # self.spinSpd = spinSpd
        # self.life = 0
        # self.lifespan = lifespan
        # if "directional" in moveType:
        #     self.dx = sin(moveDir)*moveSpd
        #     self.dy = cos(moveDir)*moveSpd
        # if "fall" in moveType:
        #     moveDir = r.randint(-90,90)
        #     self.dx = sin(moveDir)*moveSpd
        #     self.dy = cos(moveDir)*moveSpd
class Cratebreak(Particle):
    def __init__(self, x, y, img, dir):
        Particle.__init__(self, x, y, img)
        self.dx, self.dy = sin(dir)*5, cos(dir)*2.5
        self.dir = 90
        self.way = r.randint(0,1)*2-1
    def update(self):
        self.x += self.dx
        self.y -= self.dy
        self.dx *= 0.8
        self.dy -= 0.3
        self.dir += self.way
        if self.y>HEIGHT:
            self.kill()
        DISPSURF.blit(pygame.transform.rotate(self.image, self.dir), (self.x-scrollX, self.y))     
class Crystalbreak(Particle):
    def __init__(self, x, y, img, dir):
        Particle.__init__(self, x, y, img)
        self.dx, self.dy = sin(dir)*5, cos(dir)*2.5
        self.dir = 90
        self.way = r.randint(0,1)*2-1
    def update(self):
        self.x += self.dx
        self.y -= self.dy
        self.dx *= 0.8
        self.dy -= 0.3
        self.dir += self.way
        if self.y>HEIGHT:
            self.kill()
        DISPSURF.blit(pygame.transform.rotate(self.image, self.dir), (self.x-scrollX, self.y))            
class Stopspark(Particle):
    def __init__(self, x, y, img, dir, doSpin):
        Particle.__init__(self, x, y, img)
        self.dir = dir
        self.speed = 10
        self.way = (r.randint(0,1)*2-1)*(r.randint(0,15)/10)*int(doSpin)
        del self.dx, self.dy
    def update(self):
        self.x += sin(self.dir)*self.speed
        self.y -= cos(self.dir)*self.speed
        self.speed *= 0.9
        
        self.dir += self.way*0.1
        if self.speed < 0.1:
            self.kill()
        DISPSURF.blit(pygame.transform.rotate(self.image, self.dir), (self.x-scrollX, self.y))
class Hitspark(Particle):
    def __init__(self, x, y, img, dir):
        Particle.__init__(self, x, y, img)
        self.dir = dir
        self.speed = 10
        self.way = (r.randint(0,1)*2-1)*(r.randint(0,30)/10)
        del self.dx, self.dy
    def update(self):
        self.x += sin(self.dir)*self.speed
        self.y -= cos(self.dir)*self.speed
        self.speed *= 0.9
        
        self.dir += self.way*0.1
        if self.speed < 0.1:
            self.kill()
        DISPSURF.blit(pygame.transform.rotate(self.image, self.dir), (self.x-scrollX, self.y))

class SandParticle(Particle):
    def __init__(self, x, y, img, dir):
        Particle.__init__(self, x, y, img)
        self.dx, self.dy = sin(dir)*r.randint(28,48), cos(dir)*r.randint(10,25)
        self.dir = 90
        self.way = r.randint(0,1)*2-1
    def update(self):
        self.x += self.dx
        self.y -= self.dy
        self.dx *= 0.8
        self.dy -= 0.3
        if self.y>HEIGHT:
            self.kill()
        DISPSURF.blit(self.image, (self.x-scrollX, self.y))        
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        self.x, self.y, self.image = x, y, img
        self.image.convert_alpha()
        self.speed = 0
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.keyPressed = {"space":False, "a":False, "d":False, "s":False, "q":False, "w":False}
        self.skillCooldown = {"bm": 0,
                              "sm": 0,
                              "bo": 0,
                              "so": 0}
        self.dx=self.dy=self.ox=self.oy=0
        self.activeSkill = ""
        self.onGround = False
        self.animationLock = False
        self.win = False
        self.dir = "right"
        self.state, self.frame = "", 1
        self.charge = 0
        self.isHurt, self.dogravity, self.movable = False, True, True
        self.health = 4
        #Get hitboxes to check side colisions
        self.invinciblility = 0
        self.deadCounter = self.winCounter = 0
        self.slip = False
    def unpressed(self, key):
        if key == pygame.K_SPACE:
            self.keyPressed["space"] = False
        elif key == pygame.K_a:
            self.keyPressed["a"] = False
        elif key == pygame.K_d:
            self.keyPressed["d"] = False
        elif key == pygame.K_s:
            pass                                                                                                                                    
        elif key == pygame.K_q:
            self.keyPressed["q"] = False
        elif key == pygame.K_w:
            self.keyPressed["w"] = False
        elif key == pygame.K_e:
            self.keyPressed["e"] = False

    def activate_skill(self, skill):
        global enemyGroup
        if self.skillCooldown[skill] == 0 and self.activeSkill == "" and Vine not in [type(e) for e in pygame.sprite.spritecollide(self, enemyGroup, False)]:
            self.activeSkill = playerCurSkills[skill]
            if playerCurSkills[skill] == "spin":
                self.dy = 12
                self.dx *= 0.5
                self.speed = 0
                self.state = "spin"
                self.animationLock = True
            if playerCurSkills[skill] == "drop":
                self.dy -= 5
                self.charge = 0
                self.state = "drop"
                self.animationLock = True
            if playerCurSkills[skill] == "punch" and self.onGround:
                self.state = "punch"
                self.animationLock = True
            if playerCurSkills[skill] == "groundpound" and not self.onGround:
                self.dy = 0
                self.dx = 0
                self.charge = 0
                self.state = "groundpound"
                self.animationLock = True
            if playerCurSkills[skill] == "shoot" and self.onGround:
                self.charge = 0
                self.animationLock = True
                if abs(player.x-pygame.mouse.get_pos()[0]) > abs(self.y-pygame.mouse.get_pos()[1]):
                    way = self.dir+""
                    self.state = "shootright"
                    if self.dir == "left":
                        side = (self.rect.left-80, self.rect.centery-60)
                    else:
                        side = (self.rect.right, self.rect.centery-60)
                else:
                    way = "up"
                    self.state = "shootup"
                    side = (self.rect.centerx-60, self.rect.top-80)
                projectileGroup.add(Bullet(*side ,PROJECTILE_IMGS["bullet"], way, -11 if way == "left" else 11))
                del way, side

                self.skillCooldown[skill] = 15
                self.activeSkill = ""


    def update_hitboxes(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.hitboxes = {"left":pygame.Rect(*getCorner(self, "tl"), self.image.get_width()/2, self.image.get_height()),
                        "right":pygame.Rect(getCorner(self, "tl")[0] + self.image.get_width()/2, getCorner(self, "tl")[1], self.image.get_width()/2, self.image.get_height()),
                        "top":pygame.Rect(*getCorner(self, "tl"), self.image.get_width(), self.image.get_height()/2),
                        "bottom":pygame.Rect(getCorner(self, "tl")[0], getCorner(self, "tl")[1]+self.image.get_height()/2, self.image.get_width(), self.image.get_height()/2)}
    def pressed(self, key):
        if self.movable:
            if key == pygame.K_SPACE:
                if self.onGround:
                    SFX["jump"].play()
                    self.dy = 12 + round(abs(self.dx)/6)
                self.keyPressed["space"] = True
                    
            elif key == pygame.K_a:
                self.keyPressed["a"] = True
            elif key == pygame.K_d:
                self.keyPressed["d"] = True
            elif key == pygame.K_s:
                pass
            elif key == pygame.K_q:
                self.keyPressed["q"] = True
            elif key == pygame.K_w:
                self.keyPressed["w"] = True
                self.activate_skill("bm")
            elif key == pygame.K_e:
                self.keyPressed["e"] = True
                self.activate_skill("sm")
            elif key == pygame.K_0:
                global paused
                pass

    def runSkill(self):
        for skill, name in playerCurSkills.items():
            if name == "spin":
                if self.activeSkill == "spin":
                    if self.onGround:
                        self.activeSkill = ""
                    self.skillCooldown[skill] = 1
                if self.onGround:
                    self.skillCooldown[skill] = 0
            elif name == "drop":
                if self.activeSkill == "drop":
                    if self.onGround:
                        self.activeSkill = ""
                        if abs(self.charge)!=0: SFX["bounce"].play()
                        self.dy = 0 - max(self.charge, -18)
                        self.charge = 0
                    else:
                        self.frame = 1
                        self.animationLock = True
                        if self.dy < 0:
                            self.charge = self.dy+5
                    self.skillCooldown[skill] = 1
                if self.onGround:
                    self.skillCooldown[skill] = 0
            elif name == "punch":
                if self.activeSkill == "punch":
                    if self.onGround:
                        self.activeSkill = ""
                    if self.state == "punch" and self.frame < 4:
                        global enemyGroup
                        SFX["punch"].play()
                        hitbox = Hitbox(self.hitboxes[self.dir])
                        hitbox.rect.width += 100
                        if self.dir == "left": hitbox.rect.x -= 100
                        way = self.rect.midright if self.dir == "right" else self.rect.midleft
                        for hit in pygame.sprite.spritecollide(hitbox, enemyGroup.sprites(), False):
                            if (hasattr(hit, "mask") and pygame.mask.from_surface(self.image).overlap(hit.mask, (hit.x-self.x, hit.y-self.y))) or not hasattr(hit, "mask"):
                                for _ in range(6):
                                    particles.add(Hitspark(*way, PARTICLE_IMGS["hitspark.png"], 90 if self.dir == "right" else -90))
                                    
                                if self.dir == "right":
                                    hit.dx = 6
                                else:
                                    hit.dx = -6
                                hit.hurt(2)
                        for hit in pygame.sprite.spritecollide(hitbox, [p for p in projectileGroup.sprites() if type(p) in [Apple]], False):
                            if type(hit) == Apple:
                                hit.dx = 10
                                hit.dy = 0
                                hit.hit = True
                            

                        del way

                    self.skillCooldown[skill] = 20
                if self.skillCooldown[skill] > 0:
                    self.skillCooldown[skill] -= 1
            elif name == "groundpound":
                self.charge += 1
                if self.activeSkill == "groundpound":
                    if self.onGround:
                        self.activeSkill = ""
                        if self.charge != 0:
                            SFX["land"].play()

                            side = (self.rect.left-35, self.rect.centery-35)
                            particles.add(Stopspark(*side, pygame.transform.scale_by(PARTICLE_IMGS["stopspark.png"], 3), -90, False))
                            side = (self.rect.right, self.rect.centery-35)
                            particles.add(Stopspark(*side, pygame.transform.scale_by(PARTICLE_IMGS["stopspark.png"], 3), 90, False))

                            

                    else:
                        self.dy = -20 * int(self.charge > 10)
                        self.state = "groundpound"
                        self.animationLock = True
                        hitbox = Hitbox(pygame.rect.Rect(self.rect.left, self.rect.centery, self.rect.width, self.rect.height*1.2))
                        colideList = pygame.sprite.spritecollide(hitbox, enemyGroup, False)
                        if colideList:
                            for enemy in colideList:
                                enemy.hurt(4)
                                if self.dir == "right":
                                    enemy.dx = 6
                                else:
                                    enemy.dx = -6
                        del hitbox, colideList
            elif name == "shoot":
                if self.skillCooldown[skill]>0: self.skillCooldown[skill] -= 1
                if self.activeSkill == "shoot":
                    self.activeSkill = ""
                                
                
    def control(self):
        if not all((self.keyPressed["a"],self.keyPressed["d"])) and not any((self.isHurt, not self.dogravity)):
            if self.keyPressed["a"]:
                self.dir = "left"
            elif self.keyPressed["d"]:
                self.dir = "right"
            if self.keyPressed["a"]:
                #self.dx = self.dx + ((-2 + self.speed))
                self.dx = self.dx + ((-2 + self.speed)*(1-(int(self.activeSkill in SLOWING_SKILLS)*0.9)))
                if self.dx>0 and self.onGround:
                    if self.slip:
                        self.dx *= 0.9
                    else:
                        self.dx *= 0.7
                    self.state = "stop"
                    self.animationLock = True
                else:
                    if not self.animationLock:
                        self.state = "run"
            if self.keyPressed["d"]:
                #self.dx = self.dx + ((2 + self.speed))
                self.dx = self.dx + ((2 + self.speed)*(1-(int(self.activeSkill in SLOWING_SKILLS)*0.9)))
                if self.dx<0 and self.onGround:
                    if self.slip:
                        self.dx *= 0.9
                    else:
                        self.dx *= 0.7
                    self.state = "stop"
                    self.animationLock = True
                else:
                    if not self.animationLock:
                        self.state = "run"
            if self.keyPressed["q"]:
                if self.dir == "left":
                    if self.speed>-4:
                        self.speed -= 0.05
                else:
                    if self.speed<4:
                        self.speed += 0.05
            else:
                if round(self.speed, 1)!=0:
                    if not self.slip:
                        self.speed *= 0.6
                    else:
                        self.speed *= 0.9
        elif not self.dogravity and not all((self.keyPressed["a"],self.keyPressed["d"])):
            if self.keyPressed["a"]:
                self.dir = "left"
                self.dx -= 1
            elif self.keyPressed["d"]:
                self.dir = "right"
                self.dx += 1
        

            
        if self.y>HEIGHT or self.deadCounter>0:
            if self.y>HEIGHT:
                SFX["fall"].play()
                if 180<self.deadCounter<220:
                    global scrollX
                    scrollX += round(sin((self.deadCounter-180))*5)
            pygame.mixer.music.fadeout(100)
            self.deadCounter += 1

            if self.deadCounter>279:
                global enemyGroup
                enemyGroup.empty()
                main()
                if MUSIC:
                    pygame.mixer.music.play()
                    pygame.mixer.music.play(-1)
        if self.x>levelEnd-(TILE_SIZE*10):
            self.invinciblility = 1
            if self.winCounter == 0: self.winCounter = 1 
            self.keyPressed = dict(zip(self.keyPressed.keys(), [False]*len(self.keyPressed)))
            self.keyPressed["d"] = True
            if not self.win:
                self.win = True
                SFX["levelComplete"].play()
                pygame.mixer.music.fadeout(1000) 
            
        if self.isHurt:
            self.state = "hurt"
            if self.onGround:
                self.isHurt = False
                self.invinciblility = 100
        if self.invinciblility>0: self.invinciblility -= 1
        

    def gravity(self):
        
        self.x += self.dx
        if self.dogravity:
            self.y -= self.dy
            self.dy -= 0.3
        else:
            if self.state == "climb" and any((self.keyPressed["a"],self.keyPressed["d"])): self.frame = 1
            if Vine not in [type(e) for e in pygame.sprite.spritecollide(self, enemyGroup, False)]:
                self.dogravity = True
            if self.keyPressed["space"]:
                self.dy = 12
        if not any((self.keyPressed["a"], self.keyPressed["d"])) or self.slip:
            self.speed *= 0.8
        if all ((self.keyPressed["a"], self.keyPressed["d"])) and round(abs(self.dx), 1)>0 and self.onGround:
            self.state = "stop"
            self.animationLock = True
        #Prevent out of bounds
        if self.x < 170:
            self.x = 170
        if not self.isHurt:
            #self.dx *= (0.4-(int(self.onGround)*0.2))
            maxSpeed = 999
            if self.keyPressed["a"] or self.keyPressed["d"]:
                if self.keyPressed["q"]:
                    maxSpeed = 6
                else:
                    maxSpeed = 2.5
            else:
                if not self.slip:
                    if self.dx > 0:
                        self.dx -= 0.5
                    elif self.dx < 0:
                        self.dx += 0.5
                self.slip = False
                if abs(self.dx)<0.5: self.dx = 0
            if abs(self.dx)>maxSpeed:
                if self.dx>0:
                    self.dx = maxSpeed
                else:
                    self.dx = -maxSpeed
        

    def hurt(self, hp, orgin):
        if self.invinciblility==0 and not self.isHurt:
            self.dy = 4
            self.health -= hp
            if orgin[0]>self.rect.centerx:
                self.dx = -5
            else:
                self.dx = 5
            self.state = "hurt"
            self.skillCooldown = dict(zip(self.skillCooldown.keys(), [1]*4))
            self.isHurt = True
            self.animationLock = True
            
    def chState(self, state, spd):      
        if self.state == state:
            self.frame += spd
            if PLAYER_IMGS.get(f"player{state}{int(self.frame)}", False) == False:
                if PLAYER_CYCLE_FRAMES[state]<0:
                    self.frame = len([0 for name in tuple(PLAYER_IMGS.keys()) if state in name])-abs(PLAYER_CYCLE_FRAMES[state])
                else:
                    self.frame = PLAYER_CYCLE_FRAMES[state]
                
                if not self.isHurt: self.animationLock = False
        else:
            self.state = state
            self.frame = 1
    def draw(self):
        if self.animationLock:
            self.chState(self.state, 0.175)
            if self.state == "stop":
                way = self.rect.midleft if self.dir == "right" else self.rect.midright
                particles.add(Stopspark(*way, PARTICLE_IMGS["stopspark.png"], 90 if self.dir == "left" else -90, True))
                del way
        else:
            if self.onGround:
                if round(abs(self.dx), 1)>0:
                    self.chState("run", 0.125*max(abs(self.speed), 1))
                else:
                    self.chState("idle",0.03125)
            else:
                if self.dy>0:
                    self.chState("jump",0.125)
                else:
                    self.chState("fall",0.125)
        self.image = PLAYER_IMGS[f"player{self.state}{int(self.frame)}"]
        if self.dir == "left":
            self.image = pygame.transform.flip(self.image, True, False)


        if self.winCounter > 0 and currentCourse[2] != "4":
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
        else:
            DISPSURF.blit(self.image, (min(((WIDTH/2)-(self.image.get_width()/2)+actualX),self.x), self.y))
        #pygame.draw.rect(DISPSURF, (0, 0, 255), self.hitboxes["left"])
        #pygame.draw.rect(DISPSURF, (0, 255, 0), self.hitboxes["right"])
        #pygame.draw.rect(DISPSURF, (255, 0, 0), self.hitboxes["top"])
        #pygame.draw.rect(DISPSURF, (0, 0, 0), self.hitboxes["bottom"])
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, img, colType, interactable):
        super().__init__()
        global scrollX
        self.ox, self.oy = x, y
        if type(img) in (list, tuple):
            self.images = [i.convert_alpha() for i in img]
            self.frame = 0
            self.image = self.images[self.frame]
        else:
            self.image = img.convert_alpha()
        self.x, self.y = x, y
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.interactable, self.coltype = interactable, colType

        

class Grass(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "normal", False)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
class Ground(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "normal", False)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))

class Dirt(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "normal", False)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))

class Sand(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "normal", False)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))

class Sandbrick(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "normal", False)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))

class SandGeyser(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "lower", True)
        self.wave = 0
        self.dy = 0
        self.ty = y + 0
        self.y = HEIGHT
        self.dead = False
        self.spawn = -1
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

        if self.dead:
            self.lower()
        else:
            if self.y > self.ty:
                self.dy += 0.6
            else:
                if [e for e in enemyGroup.sprites() if type(e) == Molduga] and self.spawn == -1:
                    self.spawn = r.randint(0,4)
                    if self.spawn == 2:
                        tileGroup.add(Collectable(self.rect.centerx, self.y - TILE_SIZE, TILES_IMGS["co"]))
                    
                self.wave += 0.07
                self.dy = sin(self.wave)*2
                if pygame.sprite.spritecollide(self, [player], False):
                    if sin(self.wave)*2<0:
                        player.y += sin(self.wave)*6
                    player.onGround = True

        self.y -= self.dy
    
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
    def interact(self, *args, **kwargs):
        if kwargs["side"] != "bottom" and not self.dead:
            player.dy = 3
            player.dx = 0
            player.speed = 0
    def lower(self):
        self.dead = True
        self.dy -= 2
        

class Ice(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "normal", True)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
    def interact(self, *args, **kwargs):
        player.slip = True

class BrokenIce(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "normal", True)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
    def interact(self, *args, **kwargs):
        if kwargs["side"] == "top":
            self.kill()

class QuickSand(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "none", True)
    def update(self):
        self.frame += 0.05
        self.frame %= 3
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.images[int(self.frame)], (self.x-scrollX, self.y))
    def interact(self, *args, **kwargs):
        global player
        player.onGround = True
        player.dy = max(player.dy - 3, -5)


class Crate(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "normal", True)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
    def interact(self, *args, **kwargs):
        if kwargs["side"]=="top" and kwargs["dy"]>2 and kwargs["top"]:
            SFX["blockbreak"].play()
            for _ in range(6):
                particles.add(Cratebreak(*self.rect.center, PARTICLE_IMGS["cratebreak.png"], r.randint(-90, 90)))
            self.kill()

class Block(Tile,pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "normal", True)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
    def interact(self, *args, **kwargs):
        if kwargs["side"]=="top" and kwargs["dy"]>2 and kwargs["top"]:
            SFX["blockbreak"].play()
            for _ in range(6):
                particles.add(Particle(*[pos+r.randint(int(0-(self.rect.width/2)),int(self.rect.width/2)) for pos in self.rect.center], PARTICLE_IMGS["blockbreak.png"], "fall", False, 1, r.randint(-90, 90)))
            self.kill()

class Bridge(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "lower", False)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y+42, self.image.get_width(), 38)
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
            #pygame.draw.rect(DISPSURF, (0,0,0), (self.x-scrollX, self.y, self.rect.width, self.rect.height))
class Tree(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "none", False)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y+42, self.image.get_width(), 38)
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
class Leaves(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "lower", False)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y+50, self.image.get_width(), 30)
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
            #pygame.draw.rect(DISPSURF, (0,0,0), (self.x-scrollX, self.y, self.rect.width, self.rect.height))
class FakeGrass(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "none", True)
        self.origImage = self.image
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
        self.image = self.origImage
    def interact(self,*args, **kwargs):
        self.image.fill((0,0,0))
class FakeDirt(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "none", True)
        self.origImage = self.image
        
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
        self.image = self.origImage
    def interact(self,*args, **kwargs):
        self.image.fill((0,0,0))

class Spike(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "none", True)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
    def interact(self, *args, **kwargs):
        player.hurt(1, self.rect.center)

class Cactus(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "normal", True)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
    def interact(self, *args, **kwargs):
        player.hurt(1, self.rect.center)

class Goal(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        global levelEnd
        Tile.__init__(self, x, y, img, "none", False)
        levelEnd = self.x + (TILE_SIZE*6)
    def update(self):
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
class SemiSolidPlatform(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "none", False)
        self.updated = False
    def update(self):
        if not self.updated:
            global tileList
            haveLower = haveUpper = haveLeft = haveRight = False
            for t in tileList:
                if type(t) == SemiSolidPlatform:
                    if t.x == self.x and t.y == self.y + TILE_SIZE:
                        haveLower = True
                    elif t.x == self.x and t.y == self.y - TILE_SIZE:
                        haveUpper = True
                    if t.x == self.x - TILE_SIZE and t.y == self.y:
                        haveLeft = True
                    elif t.x == self.x + TILE_SIZE and t.y == self.y:
                        haveRight = True
            if haveLower and not haveUpper:
                self.image = TILES_IMGS["sspt"]
                self.coltype = "lower"
            if haveLeft and haveUpper and not haveRight:
                self.image = TILES_IMGS["sspl"]
            elif not haveLeft and haveUpper and haveRight:
                self.image = TILES_IMGS["sspr"]
        self.rect = pygame.Rect(self.x, self.y+42, self.image.get_width(), 38)
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))     
            #pygame.draw.rect(DISPSURF, (0,0,0), (self.x-scrollX, self.y, self.rect.width, self.rect.height))

class Lift(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "lower", False)
        self.updated = False
        self.wave = 0
    #def find(self, returnList, side):
    #    for t in tileList:
    #        if type(t) == Lift:
    #            if side=="right" and self.x + TILE_SIZE == t.x:
                    
    def update(self):
        if self.updated:
            self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
            if pygame.sprite.spritecollide(self, [player], False):
                self.wave += 0.02
                self.y += sin(self.wave)*1.5
                if sin(self.wave)*1.5>0:
                    player.y += sin(self.wave)*3
                player.onGround = True
            else:
                self.wave += 0.02
                self.y += sin(self.wave)*1.5
        else:
            global tileList
            haveLower = haveUpper = haveLeft = haveRight = False
            for t in tileList:
                if type(t) == Lift:
                    if t.x == self.x and t.y == self.y + TILE_SIZE:
                        haveLower = True
                    elif t.x == self.x and t.y == self.y - TILE_SIZE:
                        haveUpper = True
                    if t.x == self.x - TILE_SIZE and t.y == self.y:
                        haveLeft = True
                    elif t.x == self.x + TILE_SIZE and t.y == self.y:
                        haveRight = True
                self.image = TILES_IMGS["l"]
            if haveLeft and not haveRight:
                self.image = TILES_IMGS["lr"]
            elif not haveLeft and haveRight:
                self.image = TILES_IMGS["lll"]
            self.updated = True

        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))    
class Vine(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "none", True)
    def update(self):
        self.rect = pygame.Rect(self.x+20, self.y, self.image.get_width()-20, self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
            #pygame.draw.rect(DISPSURF, (0,0,0), (self.x-scrollX, self.y, self.rect.width, self.rect.height))
    def interact(*args, **kwargs):
        global player
        if player.keyPressed["w"]:
            player.dy = 0
            player.state = "climb"
            player.activeSkill = ""
            player.skillCooldown["bm"] = 0
            player.dogravity = False
            player.animationLock = True
class Collectable(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "none", True)
        self.bobbing = 0
    def update(self):
        self.bobbing += 0.1
        self.y += sin(self.bobbing)/2
        self.rect = pygame.Rect(self.ox, self.oy, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
    def interact(self, *args, **kwargs):
        SFX["collect"].play()
        player.health += 1
        self.kill()        
class Crystal(Tile, pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        Tile.__init__(self, x, y, img, "none", True)
        self.skill = {"1-2":"bounce",
                      "1-3":"punch",
                      "2-2":"spin",
                      "2-3":"groundpound",
                      "3-2":"shoot"}[currentCourse]
        self.bobbing = 0
    def update(self):
        self.bobbing += 0.1
        self.y += sin(self.bobbing)/2
        self.rect = pygame.Rect(self.ox, self.oy, self.image.get_width(), self.image.get_height())
        if 0-self.image.get_width()<self.x-scrollX<WIDTH:
            DISPSURF.blit(self.image, (self.x-scrollX, self.y))
    def interact(self, **kwargs):
        global skillunlock, paused
        SFX["collectbig"].play()
        light = 100
        skillunlockimg = pygame.image.load(os.path.join(UI_DIR, f"{self.skill}unlock.png"))
        skillunlock = Button(100,100, [pygame.transform.scale_by(pygame.image.load(os.path.join(UI_DIR, f"{self.skill}unlock.png")), 0.6)]*2, self)
        paused = True
        while True:
            tick()
            #skillunlock.img = fade(skillunlock, light)
            skillunlock.draw()
            if skillunlock.onHover():
                break
            pygame.display.update()

        
        with open("data.txt", "r") as file:
            data = eval(file.read())
        data["skills"] = list(data["skills"])
        data["skills"].append(self.skill)
        with open("data.txt", "w") as file:
            file.write(str(data))

        paused = False
        self.kill()      
        

def read_map():
    with open(os.path.join(ORIG_DIR, "maps", f'{currentCourse}.csv'), 'r') as file:
        my_reader = csv.reader(file, delimiter=',')
        out = []
        for row in my_reader:
            out.append(row)
        
        #zip(*out) = [1,2,3],[4,5,6],[7,8,9]
        #             0 1 2   0 1 2   0 1 2
        out = [list(row) for row in zip(*out)]
        for c in range(len(out)):
            out[c].pop(0)
        
        out = dict(enumerate(out))
            
    #with open("map.csv", "r") as file:
    #    data = tuple(data.items())
    #    converted = {}
    #    for c in data:
    #        for r in c:
    #            if type(r) == pandas.Series:
    #                for i in r:
    #                    converted[current].append(i)
    #            else:
    #                converted[r] = []
    #                current = r
    return out

def init():
    #global ORIG_DIR, UI_DIR, DISPSURF, HEIGHT, WIDTH, TILE_SIZE, MUSIC, MUSIC_DIR, TILES_IMGS, PLAYER_CYCLE_FRAMES, PLAYER_IMGS, SFX, TILES_NAMES, TILES, FPS, PARTICLE_DIR, PARTICLE_IMGS, playerCurSkills, SLOWING_SKILLS, ENEMIES, ENEMY_NAMES, BACKGROUND_IMG, dist, ENEMIES_IMGS, enemyGroup, particles
    global SIDE_COLOUR, WIDTH, HEIGHT, TILE_SIZE, DISPSURF, MUSIC, theme
    SIDE_COLOUR = {"top": (255,0,0),
                "left": (0,255,0),
                "right": (100,100,255),
                "bottom": (60,50,50)}


    #Projectiles
    global projectileGroup, PROJECTILES, PROJECTILE_IMGS
    PROJECTILES = {"bullet":Bullet,
                   "spike":SpikeProjectile,
                   "bone":Bone,
                   "apple":Apple,
                   "root":Root,
                   "qblock":Questionblock,
                   "arrow":Arrow,
                   "bomb":Bomb,
                   "explosion": Explosion,
                   "firewave": Firewave,
                   "gasterblaster":Gasterblaster}
    PROJECTILE_IMGS = {}
    for part in PROJECTILES:
        if os.path.isdir(os.path.join(PROJECTILE_DIR, part)):
            PROJECTILE_IMGS[part] = [pygame.image.load(os.path.join(PROJECTILE_DIR, part, file)) for file in os.listdir(os.path.join(PROJECTILE_DIR, part))]
        elif os.path.isfile(os.path.join(PROJECTILE_DIR, f"{part}.png")):
            PROJECTILE_IMGS[part] = pygame.image.load(os.path.join(PROJECTILE_DIR, f"{part}.png"))

    projectileGroup = pygame.sprite.Group()
    #Enemy
    global ENEMY_NAMES, ENEMIES, enemyGroup, ENEMIES_IMGS
    ENEMY_NAMES = {"gb":"glubo",
                "bb":"bumblebee",
                "h":"hedgehog",
                "sk":"skeleton",
                "whispy":"whispywoods",
                "molduga":"molduga",
                "crystalofmv":"crystalofmultiverses"}
    ENEMIES = {"gb":Glubo,
            "bb":Bumblebee,
            "h":Hedgehog,
            "sk": Skeleton,
            "whispy":Whispy,
            "molduga":Molduga,
            "crystalofmv":CrystalOfMultiverses}
    enemyGroup = pygame.sprite.Group()
    ENEMIES_IMGS = {}

    for sn, n in ENEMY_NAMES.items():
        try:
            ENEMIES_IMGS[sn] = [pygame.image.load(os.path.join(ENEMY_DIR, n, _)) for _ in os.listdir(os.path.join(ENEMY_DIR,n)) if ".png" in _]
        except pygame.error:
            print(os.listdir(os.path.join(ENEMY_DIR,n)))
            exit()


    #Sound and Music
    global SFX_LIST, SFX
    SFX_LIST = ("jump", "blockbreak", "collect", "collectbig", "punch", "fall", "levelComplete", "hover", "bounce", "land", "lose", "results", "block", "explode", "crack")
    SFX = dict(zip(SFX_LIST, [pygame.mixer.Sound(rf"{SOUND_DIR}\{sound}.mp3") for sound in SFX_LIST]))

    #Particles
    global particles, PARTICLE_IMGS
    particles = pygame.sprite.Group()
    #Particle names(Last updated: 2/6): 
    #1.stopspark.png
    #2.blockbreak.png
    #3.hitspark.png
    PARTICLE_IMGS = dict(zip([file for file in os.listdir(PARTICLE_DIR) if ".png" in file],[pygame.image.load(os.path.join(PARTICLE_DIR, file)) for file in os.listdir(PARTICLE_DIR) if ".png" in file]))
    #Background

    #Player
    global PLAYER_STANCES, PLAYER_IMGS, PLAYER_CYCLE_FRAMES, SLOWING_SKILLS, playerCurSkills
    PLAYER_STANCES = ("idle",
                      "run",
                      "jump",
                      "fall",
                      "spin",
                      "stop",
                      "drop",
                      "hurt",
                      "punch",
                      "climb",
                      "groundpound",
                      "shootright",
                      "shootup",
                      "death")
    player_imgs = {}
    for s in PLAYER_STANCES:
        i = 0
        while True:
            i+=1
            if os.path.isfile(os.path.join(ASSET_DIR, "player", f"player{s}{i}.png")):
                player_imgs[f"player{s}{i}"] = pygame.image.load(os.path.join(ASSET_DIR, "player", f"player{s}{i}.png"))
            else:   
                break
    PLAYER_IMGS = player_imgs
    PLAYER_CYCLE_FRAMES = {"idle": 1,
                        "run": 1,
                        "jump": 1,
                        "fall": 1,
                        "spin":1,
                        "stop":1,
                        "drop":1,
                        "hurt": 1,
                        "punch":1,
                        "climb":1,
                        "groundpound":1,
                        "shootright":1,
                        "shootup":1,
                        "death":1}
    for n in PLAYER_STANCES:
        if n not in PLAYER_CYCLE_FRAMES:
            PLAYER_CYCLE_FRAMES[n] = 1


    del player_imgs
    playerCurSkills = {"bm": "spin",
                    "sm": "bounce",
                    "bo": "punch",
                    "so": "shoot"}
    #with open("skill.txt", "r") as file:
    #    playerCurSkills = dict(zip(playerCurSkills.keys(), [skill.split(":")[1].strip() for skill in file.read().split("\n")]))
    SLOWING_SKILLS = ("spin", "drop", "groundpound")


    global FPS, paused
    FPS = 60
    paused = False
    #pygame.key.set_repeat(10,10)
def main():
    global scrollX, actualX, scrollY, particles, tileGroup, tileList, player, gameStart, running, BOSS
    gameStart = time()
    #Map
    scrollX, scrollY = 1, 0
    running = True
    read = read_map()
    
    #Tiles
    tileGroup = pygame.sprite.Group()
    tileList = list(tileGroup)

    #Enemies
    enemyGroup = pygame.sprite.Group()

    #Player
    #player = Player(10000,0, PLAYER_IMGS["playeridle1"])
    player = Player(0,0, PLAYER_IMGS["playeridle1"])
    FPS_CLOCK = pygame.time.Clock()
    
    current = ""
    for c, x in zip(tuple(read.values()), tuple(range(0,len(read)*TILE_SIZE,TILE_SIZE))):
        for r, y in zip(c, tuple(range(0,TILE_SIZE*len(c),TILE_SIZE))):
            if r != "a" and str(r) != "nan":
                if r in TILES_NAMES:
                    try:
                        current = TILES.get(r,None)(x, y, TILES_IMGS[r])
                    except TypeError:
                        print(r)
                        exit()
                    tileGroup.add(current)
                elif r in ENEMY_NAMES:
                    print(r)
                    current = ENEMIES.get(r,None)(x, y, ENEMIES_IMGS[r])
                    enemyGroup.add(current)
                    if r in ("crystalofmv", "whispywood", "molduga"):
                        BOSS = current
                tileList.append(current)   
    if MUSIC:
        if currentCourse[2] == "4":
            pygame.mixer.music.load(os.path.join(MUSIC_DIR, f"{currentCourse[0]}boss.mp3"))
        else:
            pygame.mixer.music.load(os.path.join(MUSIC_DIR, f"{currentCourse[0]}.mp3"))
        pygame.mixer.music.play()
        pygame.mixer.music.play(-1)
    while running:
        tick()
        pygame.display.update()
        FPS_CLOCK.tick(FPS)
            


def changeMenu():
    global curMenu, test, gameTitle, startBtn, MAP_DIR, courses
    if curMenu == "courseSelect":
        gameTitle.setTarget(gameTitle.x, -700, gameTitle.speed)
        startBtn.setTarget(startBtn.x, HEIGHT+400, gameTitle.speed)
        courses = []
        try:
            data = readData()
            for no, m in enumerate([file.replace(".csv","") for file in os.listdir(MAP_DIR)]):
                if ".ini" not in m and ( int(data["curLvl"][0]) > int(m[0]) or int(data["curLvl"][0]) == int(m[0]) and int(data["curLvl"][2:]) >= int(m[2:])) or ".ini" not in m and int(data["curLvl"][0]) > int(m[0]):
                    courses.append([Button((no+1)*(WIDTH/2), HEIGHT, [pygame.image.load(os.path.join(UI_DIR, f"world {m[0]}.png"))]*2,m)])
                    courses[-1][0].setTarget(courses[-1][0].x, (HEIGHT/2)-300, 50)
                    courses[-1].append(Text(((no+1)*(WIDTH/2))+200, HEIGHT, f"World{m}"))
                    courses[-1][1].setTarget(courses[-1][1].x, (HEIGHT/2)+200, 50)
        except FileNotFoundError:
            pass
    else:
        with open("data.txt", 'r') as file:
            data = eval(file.read())
        if data["curLvl"][0]>curMenu[0] or data["curLvl"][0]==curMenu[0] and data["curLvl"][2:]>=curMenu[2:]:
            global running, currentCourse
            running = False
            currentCourse = curMenu
        else:
            curMenu = "courseSelect"
        

def getDist(x1,x2,y1,y2):
    return sqrt(((x1-x2)**2)+((y1-y2)**2))
def menu():
    global gameTitle, test, startBtn, courses, running
    global curMenu
    curMenu = ""
    running = True
    
    
    bgImg = pygame.image.load(os.path.join(UI_DIR, "menuBackground.jpg"))
    titleImg = pygame.image.load(os.path.join(UI_DIR, "gameTitle.png"))
    startBtnImg = [pygame.image.load(os.path.join(UI_DIR, "startbtn.png")), pygame.image.load(os.path.join(UI_DIR, "startbtnLight.png"))]

    test = menuObj(-250,0, bgImg)
    gameTitle = menuObj(400, -500, titleImg)
    startBtn = Button(0, HEIGHT, startBtnImg, "courseSelect")
    

    gameTitle.x = (WIDTH/1.2)-gameTitle.img.get_width()
    startBtn.x = (WIDTH/1.6)-startBtn.img.get_width()
    
    test.setTarget(250,0,1)
    gameTitle.setTarget(gameTitle.x, 200, 75)
    startBtn.setTarget(startBtn.x, startBtn.y - 500, 50)
    
    courses = []
    
    global FPS_CLOCK, menuScroll
    menuScroll = 0
    pygame.key.set_repeat(10,10)
    FPS_CLOCK = pygame.time.Clock()
    while running:
        DISPSURF.fill((255,255,255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if curMenu == "courseSelect":
                    if event.key == K_a and menuScroll>0:
                        menuScroll -= 10
                    elif event.key == K_d:
                        menuScroll += 10
        for w in (test, gameTitle):
            if w is test:
                if abs(w.x - w.tx) < 50:
                    w.setTarget(500 if w.x<0 else -300, w.y, 1)
            
            if (w is test and curMenu != "courseSelect") or not w is test: w.move()
            w.draw()
        
        startBtn.move()
        startBtn.onHover()
        startBtn.draw()
        
        for c in courses:
            c[0].onHover()
            for i in c: 
                i.move()
                if type(i) == Button:
                    i.draw()
        
            c[1].write()

            

        pygame.display.update()
        FPS_CLOCK.tick(60)
    del running, startBtn, test, gameTitle, menuScroll, courses
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    #global ORIG_DIR, ASSET_DIR, MUSIC_DIR, SOUND_DIR, PARTICLE_DIR, ENEMY_DIR, UI_DIR
    #init paths
    ORIG_DIR = os.getcwd()
    MAP_DIR = os.path.join(ORIG_DIR, "maps")
    ASSET_DIR = os.path.join(ORIG_DIR, "assets")
    MUSIC_DIR = os.path.join(ASSET_DIR, "music")
    SOUND_DIR = os.path.join(ASSET_DIR, "sfx")
    PROJECTILE_DIR = os.path.join(ASSET_DIR, "projectile")
    PARTICLE_DIR = os.path.join(ASSET_DIR, "particle")
    ENEMY_DIR = os.path.join(ASSET_DIR, "enemy")
    UI_DIR = os.path.join(ASSET_DIR, "ui")
    BACKGROUND_DIR = os.path.join(ASSET_DIR, "background")

    #init screen
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    WIDTH = screensize[0]
    HEIGHT = screensize[1]
    TILE_SIZE = 80
    DISPSURF = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kubbe Tuki")
    pygame.display.set_icon(pygame.image.load(os.path.join(UI_DIR, "health4.png")))
    MUSIC = True


    
    init()
    
    menu()
    #currentCourse = "3-4"

    theme = currentCourse[0]
    #currentCourse = "1-1"

    #uncomment after boss testing
    del curMenu 
    
    
    #Tiles
    global TILES, TILE_DIR, TILES_NAMES, TILES_IMGS
    THEMED_TILES = ("ssp",
                    "sspt",
                    "sspr",
                    "sspl",
                    "g",
                    "d",
                    "t",
                    "ll")
    THEMES = ("", "desert", "snow")
    TILES = {"g":Grass,
            "d":Dirt,
            "b":Block,
            "br":Bridge,
            "c":Crate,
            "co":Collectable,
            "ssp":SemiSolidPlatform,
            "sspt":SemiSolidPlatform,
            "v":Vine,
            "fg":FakeGrass,
            "fd":FakeDirt,
            "sp":Spike,
            "goal":Goal,
            "s":Sand,
            "qs":QuickSand,
            "l":Lift,
            "i":Ice,
            "bi":BrokenIce,
            "crystal":Crystal,
            "sb":Sandbrick,
            "ca":Cactus,
            "sg":SandGeyser,
            "t":Tree,
            "ll":Leaves}
    TILE_DIR = os.path.join(ASSET_DIR, "tiles")
    TILES_NAMES = {"g":"grass",
                "d":"dirt",
                "mb":"marioblock",
                "mqb":"marioqblock",
                "br":"bridge",
                "c":"crate",
                "co":"collectable",
                "ssp": "semisolidplatformmiddle",
                "sspt": "semisolidplatformtop",
                "sspr": "semisolidplatformleft",
                "sspl": "semisolidplatformright",
                "v":"vine",
                "fg":"fakegrass",
                "fd":"fakedirt",
                "sp":"spike",
                "bv":"blackvoid",
                "goal":"goal",
                "s":"sand",
                "qs":"quicksand",
                "i":"ice",
                "bi":"brokenice",
                "l":"liftmiddle",
                "lll":"liftleft",
                "lr":"liftright",
                "ld":"liftdest",
                "crystal":"crystal",
                "sb":"sandbrick",
                "ca":"cactus",
                "sg":"sandgeyser",
                "t":"log",
                "ll":"leaves"}
    #TILES_IMGS = dict(zip(tuple(TILES_NAMES.keys()), tuple([pygame.image.load(os.path.join(TILE_DIR,f"{TILES_NAMES.get(tn)}.png")).convert_alpha() for tn in TILES_NAMES])))
    TILES_IMGS = {}
    for n, rn in TILES_NAMES.items():
        if os.path.isdir(os.path.join(TILE_DIR, rn)):
            TILES_IMGS[n] = [pygame.image.load(os.path.join(TILE_DIR, rn, file)) for file in os.listdir(os.path.join(TILE_DIR, rn)) if ".png" in file]
        elif os.path.isfile(os.path.join(TILE_DIR, f"{rn}.png")):
            if n in THEMED_TILES:
                TILES_IMGS[n] = pygame.image.load(os.path.join(TILE_DIR, f"{rn}{THEMES[int(theme)-1]}.png"))
            else:
                assert n not in THEMED_TILES
                TILES_IMGS[n] = pygame.image.load(os.path.join(TILE_DIR, f"{rn}.png"))
        else:
            print(os.path.join(TILE_DIR, f"{n}.png"))

    FONT = pygame.font.SysFont("Daydream", 70)
    
    if currentCourse == "3-4":
        BACKGROUND_IMG = pygame.image.load(os.path.join(BACKGROUND_DIR, "boss.jpg"))
    else:
        BACKGROUND_IMG = pygame.image.load(os.path.join(BACKGROUND_DIR, "sky.jpg"))
    if currentCourse[0] == "1":
        BACKGROUND_IMG_2 = pygame.image.load(os.path.join(BACKGROUND_DIR, f"world {currentCourse[0]}.jpg")).convert_alpha() 
    main()
    while True:
        init()
        menu()
        if currentCourse[0] == "1":
            BACKGROUND_IMG_2 = pygame.image.load(os.path.join(BACKGROUND_DIR, f"world {currentCourse[0]}.jpg")).convert_alpha() 
        main()

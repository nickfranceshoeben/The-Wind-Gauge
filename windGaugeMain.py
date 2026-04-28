import pygame as pg
import time
from math import atan, atan2,cos,sin
import numpy as np
from classes import ship, straightWind, background


'''
The goal is to demonstrate some of the maneuvers described in the Aubrey-Maturin series (specifically, I aim to get a better understanding of the
encounter towards the end of HMS Surprise.) This will be accomplished through, in no particular order:

- Creating a robust dynamic model for the ship:
    - Sail spread and trim
    - Wind direction
    - Handling
-Visualising the wind gauge through a wheel following the ship
- Creating a seemingly endless environment in which to sail
- Allowing the ship to fire, within a certain range
- Modelling the presence of other ships (potentially even allowing them to move)
- Modelling collision
- Static wind model based on vector field permeating the domain (might be challenging with the infinite range)


CONTROLS:

- So far, she will try to follow your mouse as well as she can. Putting it further to the sides of her will make her turn faster (up to a point.
Aim for 90 degrees for the sharpest turn)


NOTES:

 - So far she handles a bit sluggishly. Tuning the speeds may be helpful in this regard.
 - Odd motion when laying off is explained by the object's coordinates being defined off-centre. FIXED
 - Tried making velocity a conservative value, but it resulted in it moving rather oddly. Certainly some resistance should be felt by the ship,
 but not as excessive as that. Think of alternatives.
 - Might be more visually appealing if one made nicer sprites for the ship and sea.

'''



#Initialise Pygame:
pg.init()

domain = np.array([10000,10000])
screen = pg.display.set_mode((1280,720))
clock = pg.time.Clock()

#Load in graphics:

shipImage = pg.image.load('shipTemporary.png').convert()
shipImage = pg.transform.scale(shipImage,
                               (shipImage.get_width()*3,
                               shipImage.get_height()*3))
shipImage = pg.transform.flip(shipImage,1,0)
shipImage.set_colorkey((255,255,255))
shipImageRef = shipImage

'''
background = pg.image.load('paper50.png').convert()
background = pg.transform.scale(background,
                                (background.get_width()/1.9,
                                background.get_height()/2.78))
                                '''

backGround = background('paper50.png',np.array([1280,720]),domain,screen)
 


running = True
dt = 0.001 #Dynamically adjusted, just requires starting value

shipStartingSpeed = 1

rCamera = np.array([5000.,5000.])
cameraSpeedX = np.array([250.,0])
cameraSpeedY = np.array([0,250.])

rShip = np.array([5500.,5360.])
vShip = np.array([2,0.])*shipStartingSpeed

testShip = ship(rShip,vShip,0.0,screen,'Frigate','HMS Indomitable',True)
testShip2 = ship(np.array([5800.,5200.]),np.array([0.,-0.5]),270.0,screen,'Frigate','HMS Bellerophon',False)

wind = straightWind(np.array([5,1]),np.array([1280,720]),screen)

plotWind = False
wPressed = False
dPressed = False
aPressed = False
sPressed = False
    
while running:
    #screen.blit(background, (5000-rCamera[0],5000-rCamera[1]))

    backGround.drawBackground(rCamera)
    
    for event in pg.event.get():
        
        if event.type == pg.QUIT:
            running = False
            
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            if event.key == pg.K_v:
                if plotWind:
                    plotWind = False
                elif not plotWind:
                    plotWind = True

            #Camera motion##################
            if event.key == pg.K_w:
                wPressed = True
            if event.key == pg.K_s:
                sPressed = True
            if event.key == pg.K_d:
                dPressed = True
            if event.key == pg.K_a:
                aPressed = True
            ################################
        
        elif event.type == pg.KEYUP:

            if event.key == pg.K_w:
                wPressed = False
            if event.key == pg.K_s:
                sPressed = False
            if event.key == pg.K_d:
                dPressed = False
            if event.key == pg.K_a:
                aPressed = False

    if wPressed:
        rCamera += -cameraSpeedY*dt
    if sPressed:
        rCamera += cameraSpeedY*dt
    if dPressed:
        rCamera += cameraSpeedX*dt
    if aPressed:
        rCamera += -cameraSpeedX*dt

    if plotWind:
        wind.plotWind()
    
    testShip.updateShip(dt,rCamera,wind)
    #testShip2.updateShip(dt,rCamera,wind)
                
    pg.display.flip()
    
    dt = clock.tick(60) / 1000
    dt = max(0.001, min(0.1, dt))
            
pg.quit()
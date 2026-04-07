import pygame as pg
import time
from math import atan, atan2,cos,sin
import numpy as np
from classes import ship


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

background = pg.image.load('paper50.png').convert()
background = pg.transform.scale(background,
                                (background.get_width()/1.9,
                                background.get_height()/2.78))



running = True
dt = 0.001 #Dynamically adjusted, just requires starting value

shipAccel = 1
shipSpeedLimit = 20
shipAngle = 0
shipAngularVelocity = 0
shipAngularAccel = 15 #This can eventually be made dependent on angle.
shipSpeedNorm = 0

shipStartingSpeed = 1

rShip = np.array([500.,360.])
vShip = np.array([1.,0.])*shipStartingSpeed

testShip = ship(np.array([500.,370.]),np.array([1.,0.]),0.0,screen,'Frigate','HMS Indomitable',True)
testShip2 = ship(np.array([800.,200.]),np.array([0.,-0.5]),270.0,screen,'Frigate','HMS PeepeePooPoo',False)
    
while running:
    screen.blit(background)
    
    
    for event in pg.event.get():
        
        if event.type == pg.QUIT:
            running = False
            
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
    
    testShip.updateShip(dt)
    testShip2.updateShip(dt)
                
    pg.display.flip()
    
    dt = clock.tick(60) / 1000
    dt = max(0.001, min(0.1, dt))
            
pg.quit()
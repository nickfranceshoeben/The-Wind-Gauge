import pygame as pg
import time
from math import atan, atan2,cos,sin
import numpy as np


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
 - Odd motion when laying off is explained by the object's coordinates being defined off-centre.
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

'''
while running:
    screen.fill((0,0,0))
    shipImage = pg.transform.rotate(shipImageRef,shipAngle)
    
    mx, my = pg.mouse.get_pos()
    relativeToShipX = shipX - mx
    relativeToShipY = shipY - my
    angleFromFrame = atan2(relativeToShipY,relativeToShipX) #Angle from coordinate frame to mouse position
    angleFromShip = (angleFromFrame - shipAngle)*180/3.141592
    
    print(angleFromShip)
    if angleFromShip > 0 and angleFromShip < 180:
        
        angleFromShip = min(90, angleFromShip)
        rotationFactor = angleFromShip/90
        
    if angleFromShip > 180 and angleFromShip < 360:
        
        angleFromShip = max(270,angleFromShip)
        rotationFactor = (angleFromShip-270)/90
        
    vectorX = 40*cos(angleFromShip)
    vectorY = 40*sin(angleFromShip)
    
    screen.blit(shipImage, (shipX,shipY))
    pg.draw.line(screen,(255,0,0),(int(shipX+60),int(shipY+15)),(int(shipX+vectorX),int(shipY+vectorY)),width=1)
    
    for event in pg.event.get():
        
        if event.type == pg.QUIT:
            running = False
            
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
                
    shipAngularVelocity = rotationFactor*shipAngularAccel     
    shipAngle += -shipAngularVelocity*dt
    shipSpeedX = shipSpeedLimit*cos(angleFromShip*3.141592/180)
    shipSpeedY = shipSpeedLimit*sin(angleFromShip*3.141592/180)
    shipSpeedNorm = (shipSpeedX**2 + shipSpeedY**2)**(1/2)
    
    if shipSpeedNorm > 1:
        shipSpeedX = (shipSpeedX/shipSpeedNorm)*shipSpeedLimit
        shipSpeedY = (shipSpeedY/shipSpeedNorm)*shipSpeedLimit
    shipX += shipSpeedX*dt
    shipY += shipSpeedY*dt
    
    '''
    
while running:
    screen.fill((0,0,0))
    shipImage = pg.transform.rotate(shipImageRef,shipAngle)
    
    mx, my = pg.mouse.get_pos()
    relativeToShipX = rShip[0] - mx
    relativeToShipY = rShip[1] - my
    dShip = np.array([relativeToShipX,relativeToShipY])#Distance vector between mouse position and ship position
    angleFromShip = np.degrees(np.acos(np.dot(-vShip,dShip)/(np.linalg.norm(vShip)*np.linalg.norm(dShip))))
    
    w = -1*dShip
    cross = np.cross(vShip,w)
    
    if cross>0:
        
        angleFromShip = min(90, angleFromShip)
        rotationFactor = -angleFromShip/90
        
    if cross<0:
        
        angleFromShip = max(-90,-angleFromShip)
        rotationFactor = -angleFromShip/90
    
    #print(angleFromShip)
    vectorX = 40*cos(angleFromShip)
    vectorY = 40*sin(angleFromShip)
    
    screen.blit(shipImage, (rShip[0],rShip[1]))
    
    for event in pg.event.get():
        
        if event.type == pg.QUIT:
            running = False
            
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
                
    shipAngularVelocity = rotationFactor*shipAngularAccel
    shipAngle += shipAngularVelocity*dt
    
    vShip = shipSpeedLimit*np.array([cos(np.radians(shipAngle)),-sin(np.radians(shipAngle))])
    
    
    
    if np.linalg.norm(vShip) > 1:
        
        vShip = shipSpeedLimit*vShip/np.linalg.norm(vShip)
    
    rShip += vShip*dt
    
                
    pg.display.flip()
    
    dt = clock.tick(60) / 1000
    dt = max(0.001, min(0.1, dt))
            
pg.quit()
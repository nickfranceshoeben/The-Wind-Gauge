import numpy as np
import pygame as pg
import pickle as pk


class ship():
    
    def __init__(self,rShipInitial:np.array, vShipInitial:np.array, shipAngleInitial:np.array,onScreen=pg.surface.Surface, shipClass='Frigate',name='HMS Surprise', control=False):
        
        print(f'The {shipClass} {name} has left drydock!')
        
        if shipClass.lower() == 'frigate':
            
            self.shipImage = pg.image.load('shipTemporary.png').convert()
            self.shipImage = pg.transform.scale(self.shipImage,
                                        (self.shipImage.get_width()*3,
                                        self.shipImage.get_height()*3))
            self.shipImage = pg.transform.flip(self.shipImage,1,0)
            self.shipImage.set_colorkey((255,255,255))
            
            self.shipAccel = 1
            self.shipSpeedLimit = 20
            self.shipAngularAccel = 15 #This can eventually be made dependent on angle.
                        
            #You can add ship class-specific 
            
        
        self.shipImageRef = self.shipImage
        self.rShip = rShipInitial
        self.vShip = vShipInitial
        self.shipAngle = shipAngleInitial
        self.screen = onScreen
        self.control = control
        
    def updateShip(self,dt,camera:np.array):
        
        shipImage = pg.transform.rotate(self.shipImageRef,self.shipAngle)
        
        if self.control:
    
            mx, my = pg.mouse.get_pos()
            relativeToShipX = self.rShip[0] - camera[0] - mx
            relativeToShipY = self.rShip[1] - camera[1] - my
            dShip = np.array([relativeToShipX,relativeToShipY])#Distance vector between mouse position and ship position
            angleFromShip = np.degrees(np.acos(np.dot(self.vShip,dShip)/(np.linalg.norm(self.vShip)*np.linalg.norm(dShip))))
            
            w = -1*dShip
            cross = np.cross(self.vShip,w)
            
            
            #########Determine angle right or left############
            if cross>0:
                
                angleFromShip = min(90, angleFromShip)
                rotationFactor = -angleFromShip/90
                
            if cross<0:
                
                angleFromShip = max(-90,-angleFromShip)
                rotationFactor = -angleFromShip/90
                
        else:
            rotationFactor=0
        
        shipRect = shipImage.get_rect(center = (self.rShip[0]-camera[0],self.rShip[1]-camera[1]))    
        self.screen.blit(shipImage, (shipRect))
                    
        shipAngularVelocity = rotationFactor*self.shipAngularAccel
        self.shipAngle += shipAngularVelocity*dt
        
        self.vShip = self.shipSpeedLimit*np.array([np.cos(np.radians(self.shipAngle)),-np.sin(np.radians(self.shipAngle))])
        
        
        
        if np.linalg.norm(self.vShip) > 1:
            
            self.vShip = self.shipSpeedLimit*self.vShip/np.linalg.norm(self.vShip)
        
        self.rShip += self.vShip*dt

class straightWind():

    def __init__(self,directionVector:np.array, screenResolution:np.array, onScreen:pg.surface.Surface):

        self.directionVector = directionVector
        self.screenResolution = screenResolution
        repetitions = self.screenResolution/88 #44 is about twice the length of the arrows
        self.posVector = np.zeros([2,int(repetitions[0]),int(repetitions[1])])
        self.screen = onScreen
        self.windVector = pg.image.load('simpleArrow.png').convert()
        self.windVector = pg.transform.flip(self.windVector,1,0)
        self.windVector.set_colorkey((0,0,0))
        self.windVector.set_alpha(125)

        for i in range(0,self.posVector.shape[2]):
            for e in range(0,self.posVector.shape[1]):
                
                self.posVector[:,e,i] = np.array([(screenResolution[0]/repetitions[0])*e,i*screenResolution[1]/repetitions[1]])

    def plotWind(self):

        angle = np.degrees(np.acos(np.dot(self.directionVector,np.array([1,0]))/(np.linalg.norm(self.directionVector)*np.linalg.norm(np.array([1,0])))))
        windVectorOriented = pg.transform.rotate(self.windVector,angle)

        for i in range(0,self.posVector.shape[2]):
            for e in range(0,self.posVector.shape[1]):

                self.screen.blit(windVectorOriented, (self.posVector[0,e,i],self.posVector[1,e,i]))


        

'''



class differentialWind():

    def __init__()

'''
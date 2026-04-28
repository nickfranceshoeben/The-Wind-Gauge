import numpy as np
import pygame as pg
import pickle as pk


class background():

    def __init__(self,file:str,screenResolution:np.array, domain:np.array, screen:pg.surface.Surface):

        self.screenResolution = screenResolution
        self.screen = screen
        background = pg.image.load(file).convert()
        self.background = pg.transform.scale(background,
                                (background.get_width()/1.9,
                                background.get_height()/2.78)) #Not sure what these numbers are atm, has to do
                                #with particular background scaling. Will adapt in the future for new background

        #Divide the entire domain into parts that have the dimensions of the background image.
        xFit = domain[0]/self.background.get_width()
        yFit = domain[1]/self.background.get_height()
        dx = domain[0]/xFit
        dy = domain[1]/yFit
        self.xPos = np.zeros([int(xFit)+1,2])
        self.yPos = np.zeros([int(yFit)+1,2])
        
        for i in range(0, int(xFit)+1):
            
            self.xPos[i,:] = np.array([dx*i,dx*(i+1)])

        for i in range(0, int(yFit)+1):

            self.yPos[i,:] = np.array([dy*i,dy*(i+1)])

    def drawBackground(self,camera:np.array):

        #The whole domain is treated as a grid (where each part is shaped like the background image).
        whereX = np.zeros([self.xPos.shape[0]]) #Create arrays shaped like 
        whereY = np.zeros([self.yPos.shape[0]])
        for i in range(0,self.xPos.shape[0]):
            
            if camera[0] >= self.xPos[i,0] and camera[0] <= self.xPos[i,1]:

                whereX[i] = 1

            elif (camera[0]-self.screenResolution[0]/2) >= self.xPos[i,0] and (camera[0]-self.screenResolution[0]/2) <= self.xPos[i+1,1]:

                whereX[i] = 1


        for i in range(0,self.yPos.shape[0]-1):
            
            if camera[1] >= self.yPos[i,0] and camera[1] <= self.yPos[i,1]:

                whereY[i] = 1

            elif (camera[1]-self.screenResolution[1]/2) >+ self.yPos[i,0] and (camera[1]-self.screenResolution[1]/2) <= self.yPos[i+1,1]:

                whereY[i] = 1

        toDraw = []

        for i in range(self.yPos.shape[0]):
            for e in range(self.xPos.shape[0]):
                if whereY[i]==1 and whereX[e]==1:

                    arr = np.vstack((self.xPos[e],self.yPos[i]))
                    toDraw.append(arr)


        for i in toDraw:

            xCoord = i[0,0] + (i[0,1] - i[0,0])/2
            yCoord = i[1,0] + (i[1,1] - i[1,0])/2

            self.screen.blit(self.background, (xCoord+(self.screenResolution[0]/2)-camera[0], yCoord+(self.screenResolution[1]/2)-camera[1]))
        


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
            self.sailCoeff = 0.032
            self.dragCoeff = 0.012
            self.shipAngularAccel = 15 #This can eventually be made dependent on angle.
            self.shipDragCoeff = 0.0015 #Complete guess as to what this should be
            self.steerCoefficient = 0.05
            self.angularDragCoeff = 0.15
                        
            #You can add ship class-specific 
            
        
        self.shipImageRef = self.shipImage
        self.rShip = rShipInitial
        self.vShip = vShipInitial
        self.shipAngle = shipAngleInitial
        self.shipAngularVelocity = 0
        self.screen = onScreen
        self.control = control
        
    def updateShip(self,dt,camera:np.array,wind):
        
        shipImage = pg.transform.rotate(self.shipImageRef,self.shipAngle)
        
        if self.control:
    
            mx, my = pg.mouse.get_pos()
            relativeToShipX = self.rShip[0] - camera[0] - mx
            relativeToShipY = self.rShip[1] - camera[1] - my
            dShip = np.array([relativeToShipX,relativeToShipY])#Distance vector between mouse position and ship position
            orientationVector = np.array([np.cos(np.radians(self.shipAngle)),np.sin(np.radians(self.shipAngle))])
            angleFromShip = 180 - np.degrees(np.acos(np.dot(orientationVector,dShip)/(np.linalg.norm(orientationVector)*np.linalg.norm(dShip))))
            
            w = -dShip
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
                    
        self.shipAngularVelocity += self.steerCoefficient * rotationFactor*np.linalg.norm(self.vShip) - (self.angularDragCoeff * self.shipAngularVelocity)
        self.shipAngle += self.shipAngularVelocity*dt
        shipAngleClean = self.shipAngle%360
        
        print(f'Vector:{orientationVector}, angleFromShip: {angleFromShip}, angularVelocity:{self.shipAngularVelocity}')


        angleOfWind = np.degrees(np.acos(np.dot(wind.directionVector,np.array([1,0]))/np.linalg.norm(wind.directionVector))) #Computes wind angle wrt (1,0)
        windToShipAngle = abs(shipAngleClean-angleOfWind)
        windScore = abs(windToShipAngle-180)/180


        self.vShip += self.sailCoeff*windScore*np.array([np.cos(np.radians(shipAngleClean)),np.sin(np.radians(shipAngleClean))])*dt - dt*self.shipDragCoeff*self.vShip**2

        #self.vShip = self.shipSpeedLimit*windScore*np.array([np.cos(np.radians(self.shipAngle)),-np.sin(np.radians(self.shipAngle))])

        '''
        if np.linalg.norm(self.vShip) > 1:
            
            self.vShip = self.shipSpeedLimit*self.vShip/np.linalg.norm(self.vShip)'''
        
        self.rShip += self.vShip*dt
        '''
        self.vShip = self.shipSpeedLimit*np.array([np.cos(np.radians(self.shipAngle)),-np.sin(np.radians(self.shipAngle))])
        
        
        
        if np.linalg.norm(self.vShip) > 1:
            
            self.vShip = self.shipSpeedLimit*self.vShip/np.linalg.norm(self.vShip)
        
        self.rShip += self.vShip*dt

        '''

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
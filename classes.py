import numpy as np
import pygame as pg
import pickle as pk
from tools import R_w_s,R_s_w


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
    
    def __init__(self,rShipInitial:np.array, vShipInitial:np.array, thetaShipInitial:np.array,onScreen=pg.surface.Surface, shipClass='Frigate',name='HMS Surprise', control=False):
        
        print(f'The {shipClass} {name} has left drydock!')
        
        if shipClass.lower() == 'frigate':
            
            self.shipImage = pg.image.load('shipTemporary.png').convert()
            self.shipImage = pg.transform.scale(self.shipImage,
                                        (self.shipImage.get_width()*3,
                                        self.shipImage.get_height()*3))
            self.shipImage = pg.transform.flip(self.shipImage,1,0)
            self.shipImage.set_colorkey((255,255,255))
            self.shipImageRef = self.shipImage
            
            self.sailImage = pg.image.load('sailTemporary.png').convert()
            self.sailImage = pg.transform.scale(self.sailImage,
                                                (self.sailImage.get_width()*3,
                                                self.sailImage.get_height()*3))
            self.sailImage = pg.transform.flip(self.sailImage,1,0)
            self.sailImage.set_colorkey((255,255,255))
            self.sailImageRef = self.sailImage
            
            
            
            self.screen = onScreen
            self.control = control
            
            ################################### Coefficients ############################
            self.sailCoeff = 0.065          # Regulates sail (think of it as surface area)
            self.dragCoeff = 0.020          # How much drag is created by the sail

            self.dampCoeff1 = 0.145         # forward water drag
            self.hydroCoeff1 = 0.53         # lateral drag (translation)
            self.hydroCoeff2 = 0.014        # Rotational drag (velocity)
            
            self.rudderCoefficient = 0.028  # Rudder strength
            self.angularDragCoeff = 0.48    # Rotational drag (angular rate)
            
            
        ################### Ship state ###################
        
        self.rShip = rShipInitial
        self.vShip = vShipInitial
        self.thetaShip = thetaShipInitial
        self.thetaDotShip = 0
        
        #################### Ship inputs #################
        
        self.sailAngle = 0  # These will be controllable soon
        self.shipAngle = 0
        
        
    def updateShip(self, dt, camera: np.array, wind, sailAngle):
        
        #################### STEERING ####################
        rotationFactor = 0.0
        if self.control:
            mx, my = pg.mouse.get_pos()
            mouse_vec = np.array([
                mx + camera[0] - self.rShip[0],
                my + camera[1] - self.rShip[1]
            ])
            
            fwd = np.array([np.cos(self.thetaShip), np.sin(self.thetaShip)])
            
            angle_diff = np.degrees(np.arctan2(
                fwd[0]*mouse_vec[1] - fwd[1]*mouse_vec[0],
                fwd[0]*mouse_vec[0] + fwd[1]*mouse_vec[1]
            ))
            
            rotationFactor = np.clip(angle_diff / 90.0, -1.0, 1.0)
            
        #################### SAIL #########################
        self.sailAngle = sailAngle


        # ====================== SAIL FORCES ======================
        Rws = R_w_s(self.thetaShip)
        Rsw = R_s_w(self.thetaShip)
        
        vs = self.vShip
        was = Rws @ (-wind.directionVector - vs)        # <--- Inverted wind here, forgot a sign somewhere
        normWas = np.linalg.norm(was)
        
        if normWas < 1e-6:
            sailForceShip = np.zeros(2)
        else:
            d = was / normWas
            
            # Square sail: stronger drive when wind is coming from behind/side
            windFromBehind = max(0.0, -d[0])           # -d[0] > 0 when wind pushes ship forward
            sailMagnitude = self.sailCoeff * (normWas ** 2) * windFromBehind
            
            sailDrag = self.dragCoeff * (normWas ** 2) * d * 0.8
            
            sailForceShip = np.array([sailMagnitude, 0.0]) - sailDrag


        # ====================== WATER FORCES ======================
        vsShip = Rws @ self.vShip
        
        waterForceShip = np.array([
            -self.dampCoeff1 * vsShip[0] * abs(vsShip[0]) - 0.05 * vsShip[0],   # forward + small linear
            -self.hydroCoeff1 * vsShip[1] * abs(vsShip[1])                        # strong lateral
        ])

        totalForceShip = sailForceShip + waterForceShip
        totalForceWorld = Rsw @ totalForceShip


        # ====================== ANGULAR DYNAMICS ======================
        speed = np.linalg.norm(self.vShip)
        
        rudderTorque = self.rudderCoefficient * speed * rotationFactor
        angularDamping = self.angularDragCoeff * self.thetaDotShip + self.hydroCoeff2 * (speed ** 2) * self.thetaDotShip
        
        thetaDotDot = rudderTorque - angularDamping


        # ====================== INTEGRATION ======================
        self.vShip += totalForceWorld * dt
        self.rShip += self.vShip * dt
        
        self.thetaDotShip += thetaDotDot * dt
        self.thetaShip = (self.thetaShip + self.thetaDotShip * dt) % (2 * np.pi)
        
        self.shipAngle = np.degrees(self.thetaShip)

        # ====================== DRAWING ======================
        rotated = pg.transform.rotate(self.shipImageRef, -self.shipAngle)
        rect = rotated.get_rect(center=(self.rShip[0] - camera[0], self.rShip[1] - camera[1]))
        self.screen.blit(rotated, rect)
        
        rotatedSail = pg.transform.rotate(self.sailImageRef, -self.shipAngle-self.sailAngle)
        
        foreDistance = 18*np.array([np.cos(self.thetaShip),np.sin(self.thetaShip)])
        aftDistance = 18*np.array([np.cos(self.thetaShip),np.sin(self.thetaShip)])
        rectSailMain = rotatedSail.get_rect(center=(self.rShip[0]-camera[0],self.rShip[1]-camera[1]))
        rectSailFore = rotatedSail.get_rect(center=(self.rShip[0]-camera[0]+foreDistance[0],self.rShip[1]-camera[1]+foreDistance[1]))
        rectSailAft = rotatedSail.get_rect(center=(self.rShip[0]-camera[0]-aftDistance[0],self.rShip[1]-camera[1]-aftDistance[1]))
        self.screen.blit(rotatedSail, rectSailMain)
        self.screen.blit(rotatedSail, rectSailFore)
        self.screen.blit(rotatedSail, rectSailAft)
        
        print(f'Sail Angle: {self.sailAngle}')
        
        
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
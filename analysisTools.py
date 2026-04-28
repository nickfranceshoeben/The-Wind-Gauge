import numpy as np
import matplotlib.pyplot as plt


#A test for how a ship's speed evolves based on parameters (drag coeff, top speed, etc):

rShip = np.array([0.,0.])
vShip = np.array([0.,0.])
windScore = 0.85 #Fair sailing
windSpeed = 5
dragCoeff = 0.015
shipSpeed = 25
sailCoeff = [0.02,0.01,0.005,0.002,0.001]

velocity = np.zeros([10000,5])
velocityRatio = np.zeros([10000,5])
dt = 0.1
time = np.arange(0,1000,dt)

Ratio = 0.015/0.04

sailCoeff2 = [0.02,0.01,0.005,0.002,0.001]

index = 0
for coeff in sailCoeff:
    rShip = np.array([0.,0.])
    vShip = np.array([0.,0.])
    rShipRatio = np.array([0.,0.])
    vShipRatio = np.array([0.,0.])
    for i in range(len(time)):

        rShip += vShip*dt
        vShip += coeff * (windSpeed**2) * windScore * np.array([1,0])*dt - dt*dragCoeff*vShip**2

        rShipRatio += vShip*dt
        vShipRatio += sailCoeff2[index] * (windSpeed**2) * windScore * np.array([1,0])*dt - dt*Ratio*sailCoeff[index]*vShipRatio**2

        velocity[i,index] = np.linalg.norm(vShip)
        velocityRatio[i,index] = np.linalg.norm(vShipRatio)
    index += 1

print(f'Ratio:{Ratio}, drag:{Ratio*0.008}')
fig,ax = plt.subplots(1,2)
ax[0].plot(time[:1000],velocity[:1000,0],label='0.02')
ax[0].plot(time[:1000],velocity[:1000,1],label='0.01')
ax[0].plot(time[:1000],velocity[:1000,2],label='0.005')
ax[0].plot(time[:1000],velocity[:1000,3],label='0.002')
ax[0].plot(time[:1000],velocity[:1000,4],label='0.001')


ax[1].plot(time[:],velocityRatio[:,0],label='0.02')
ax[1].plot(time[:],velocityRatio[:,1],label='0.01')
ax[1].plot(time[:],velocityRatio[:,2],label='0.005')
ax[1].plot(time[:],velocityRatio[:,3],label='0.002')
ax[1].plot(time[:],velocityRatio[:,4],label='0.001')

ax[0].legend()
ax[1].legend()

plt.show()

#Something around sailCoeff = 0.007/8 and 0.003. This means top speed in about 220 seconds (3 minutes and 40 seconds).
#In reality this would have been much slower (anywhere from 5 to 15 minutes) but that makes for a very boring simulation.

#In fact, 3 minutes 40 seconds also makes for a dull simulation. Try 0.02 and 0.0075 (50 seconds to top)

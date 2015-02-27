__author__ = 'Alan'
import random



class Punch():
    def __init__(self,limb):
        self.limb=limb
        self.attacker=limb.owner
        self.arm=limb.attachpoint
        if self.arm.attachpoint:
            self.anchor=self.arm.attachpoint
            self.strength=self.arm.stats['str']+0.6*self.anchor.stats['str']
        else:
            self.anchor=None
            self.strength=self.arm.stats['str']
        self.strikelength=limb.length+limb.attachpoint.length
        self.strikearea=3.14*limb.radius**2
        self.strikemass=limb.movemass+limb.owner.movemass


    def do(self,target):
        maxtargetmass=target.owner.mass
        movemass=random.triangular(low=target.movemass,high=maxtargetmass,mode=target.movemass)
        strikemass=random.triangular(low=self.limb.mass,high=self.strikemass,mode=self.strikemass)
        reducedmass=strikemass*movemass/(strikemass+movemass)
        pushforce=10*self.strength*reducedmass**0.5
        highspeed=max(4.4*(self.strength/self.arm.movemass)**0.5,5)
        speed=random.triangular(low=1,high=highspeed,mode=5)
        deliveredforce=speed*(1000000000*reducedmass*self.strikearea/(self.limb.thickness/self.limb.youngs+target.thickness/target.youngs))**0.5+pushforce
        deliveredpressure=deliveredforce/self.strikearea
        print(pushforce,deliveredforce,deliveredpressure)
        target.damageresolve(deliveredforce,deliveredpressure,self.limb)
        self.limb.damageresolve(deliveredforce,deliveredpressure,target)
        time=2*self.strikelength/speed


#A person can swing with two hands an object with a moment of inertia of 0.1646 kg m^2 with a top radial speed
#of about 30 rad/sec. It seems that I*w^4 is approximately constant, though there is clearly more work that needs done.



def SwingSpeed(attacker,twohand=False):
    if twohand==True:
        weapon=attacker.weapon
        arm1=attacker.rightarm
        arm2=attacker.leftarm
        I=2*weapon.I+((1/3)*arm1.mass*arm1.length**2+(1/3)*arm2.mass*arm2.length**2)+weapon.mass*((arm1.length+arm2.length)/2)**2
        torque=(5*arm1.stats['strength']+5*arm2.stats['strength'])*I**0.5
        vmax=(weapon.length+((arm1.length+arm2.length)/2))(2*3.14*torque/I)**(0.5)
        swingtime=I*(vmax/(weapon.length+((arm1.length+arm2.length)/2)))/torque

    return (swingtime,vmax)


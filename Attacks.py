__author__ = 'Alan'
import random
from BaseClasses import *
from UI_Elements import *



def targetchoice(defender):
    limbs = defender.limbs
    targetingsize = 0
    for limb in limbs:
        targetingsize += limb.sizefactor
    targetroll = random.uniform(0, targetingsize)
    target = None
    for limb in limbs:
        if targetroll <= limb.sizefactor:
            target = limb
            # messages.append("{}'s {} was hit!".format(limb.owner.name,limb.name))
            return limb
        elif target is None:
            targetroll = targetroll - limb.sizefactor

def hostilitycheck(attacker,defender):
    for i in attacker.classification:
        if i in defender.hostile:
            return True
    for i in defender.classification:
        if i in attacker.hostile:
            return True
    return False


class Attack():
    def __init__(self):
        self.disabled=False
        self.hands=1
        self.useless=False
        self.blocked=False
        self.dodged=False
        self.parried=False
        self.penetrate=False
        self.weapon=None
        self.absolute_depth_limit=1
        self.cutlimit=1
        self.piercelimit=1
        self.results=[]
        self.touchedobjects=[]
        self.damagedobjects=[]


    def resolve(self):
        f=self.force
        #print(self.name,'Force of',f,'time of',self.time,'pressure of',self.pressure)
        #print(self.recoverytime)

        self.damage_dealt = 0

        if self.dodged==True:
            messages.append("The attack was avoided!")
            self.unstatweapon()
            self.attacker.recoverytime=self.recoverytime
            return
        if self.parried==True:
            messages.append("The attack was parried with the {}".format(self.target.name))
            self.target.damageresolve(self,self.limb)
            self.target.functioncheck()
            self.unstatweapon()
            self.attacker.recoverytime=(1+random.random())*self.recoverytime

            return
        if self.blocked==True:
            messages.append("The attack was blocked with the {}".format(self.target.name))
            self.target.damageresolve(self,self.limb)
            self.target.functioncheck()
            self.unstatweapon()
            self.attacker.recoverytime=(1+random.random())*self.recoverytime

            return

        self.target.on_struck(self)

        self.target.damageresolve(self, self.limb)

        self.attacker.on_strike(self)

        try: self.weapon.on_strike(self)
        except AttributeError:
            try: self.limb.on_strike(self)
            except AttributeError: pass

        if self.damage_dealt <= 0 and self.parried==False:
            messages.append("The attack glances off harmlessly")
            self.attacker.recoverytime=random.random()*self.recoverytime
        self.basetarget.owner.combataction = True
        self.attacker.focus[0] -= 1

        self.penetrate=False
        self.arpen = -15
        self.force = f / (10*self.damagefactor)
        self.pressure = f / self.strikearea
        self.reaction_damage_processed = False
        self.oldtype=self.type
        self.type='crush'
        if hasattr(self,'weapon') and self.weapon:
            basetarget=self.basetarget
            self.target=self.weapon
            self.basetarget=self.weapon
            if self.attacker.stats['luc']<random.gauss(12,8):
                self.weapon.damageresolve(self,basetarget,reactionforce=True)
            self.basetarget=basetarget
        else:
            basetarget=self.basetarget
            self.target=self.limb
            self.basetarget=self.limb
            if self.attacker.stats['luc']<random.gauss(12,8):
                self.limb.damageresolve(self,basetarget, reactionforce=True)
            self.basetarget=basetarget
        self.type=self.oldtype
        self.unstatweapon()


    def unstatweapon(self):
        if self.weapon==None:
            return
        if self.stattedweapon==True:
            pass
        if self.stattedweapon==False:
            del self.weapon.stats

    def test_usability(self,hands):

        if hands==1:
            if self.hands!=1:
                self.useless=True
                return
            if self.arm.ability>0 and self.limb.ability>0:
                self.useless=False
            else:
                self.useless=True
        if hands==2:
            if self.hands==1:
                self.useless=True
                return
            if any(limb.ability<=0 for limb in self.limbs):
                self.useless=True
                return
            for i in self.limbs:
                if i.attachpoint!=None:
                    if i.attachpoint.ability<=0:
                        self.useless=True
                        return
            else:
                self.useless=False

    def armor_penetration(self):
        if self.hands==1:
            tec=self.limb.stats['tec']
        else:
            tec=sum(i.stats['tec']**2 for i in self.limbs)**0.5
        if hasattr(self.target,"armor") and self.target.armor is not None:
            thickness=self.target.thickness+self.target.armor.thickness
            density=self.target.armor.density
            coverage=self.target.armor.coverage-self.arpen
                #mode shifts down for higher defender luck or per. Shifts up for higher attacker tec or luck.
            mode=(tec+0.5*tec)/(2*self.target.stats['luc']+self.target.stats['per'])
            mode=min(mode,1)
            if random.triangular(0,1,mode)>coverage:
                #if self.target.armor.coverage*abs(random.gauss(self.target.stats['luc'],1))<random.random()*(self.limb.stats['luc']+2*self.limb.stats['tec'])/3+self.arpen:
                self.youngs=self.target.arpen_youngs
                self.shear=self.target.arpen_shear
                thickness=self.target.thickness
                density=self.target.layers[len(self.target.layers)-1].density
                self.penetrate=True
            else:
                self.youngs=self.target.youngs
                self.shear=self.target.shear
        else:
            thickness=self.target.thickness
            self.youngs=self.target.youngs
            self.shear=self.target.shear
            if hasattr(self.target,'density'):
                density=self.target.density
            elif hasattr(self.target,'layers'):
                density=self.target.layers[len(self.target.layers)-1].density
            else:
                density=5000
        return (thickness,density)




class Punch(Attack):
    def __init__(self, limb):
        super().__init__()
        self.damagefactor=1
        self.weapon = None
        self.type = 'crush'
        self.oldtype = 'crush'
        self.limb = limb
        self.attacker = limb.owner
        if self.attacker.player == True:
            self.name = 'a punch with your {}'.format(limb.name)
        else:
            self.name = 'a punch with its {}'.format(limb.name)
        self.arpen = -0.1
        self.accuracy=5
        limb = self.limb
        if hasattr(self.limb,"attachpoint") and self.limb.attachpoint is not None:
            self.arm = limb.attachpoint
            if hasattr(self.arm,"attachpoint") and self.arm.attachpoint is not None:
                self.anchor = self.arm.attachpoint
                self.basestrength = (self.arm.stats['str'] * self.arm.ability + 0.6 * self.anchor.stats[
                    'str'] * self.anchor.ability) * limb.ability ** 0.2 + 0.1
            else:
                self.anchor = None
                self.basestrength = (self.arm.stats['str'] * self.arm.ability) * limb.ability ** 0.2 +0.1
            self.strikelength = limb.length + limb.attachpoint.length
            self.area = 3.14 * limb.radius ** 2 + 0.0001
            self.strikemass = limb.movemass + limb.owner.mass
            self.strength = self.basestrength * (max(self.attacker.stamina[0] / self.attacker.stamina[1],0) ** 0.5)
        else:
            self.arm=self.limb
            self.strikelength=limb.length
            self.area=3.14 * limb.radius ** 2 + 0.0001
            self.strikemass = limb.movemass
            self.basestrength=0.5*self.limb.stats['str']
            self.strength = self.basestrength * (max(self.attacker.stamina[0] / self.attacker.stamina[1],0) ** 0.5)
        self.strikearea=self.area


    def do(self, target):
        self.__init__(self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True
        highspeed = max(4 * (max(self.strikelength*self.strength / self.arm.movemass,0)) ** 0.5, 8)
        self.speed = random.triangular(low=1, high=highspeed, mode=4) * (
            (self.attacker.stamina[0] / self.attacker.stamina[1]) ** 0.5) + 0.1
        broadcast_time=2*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*(self.attacker.focus[0]+1))
        self.time = broadcast_time+self.strikelength / self.speed

        self.target.owner.evasion(self)

        movemass = abs(random.gauss(self.target.movemass, 5))*(self.limb.stats['tec']+15)/15
        thickness,density=self.armor_penetration()
        self.strikemass = random.triangular(low=self.limb.movemass, high=self.strikemass, mode=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec']))
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        self.pushforce = 10 * self.strength * self.reducedmass ** 0.5
        self.force = self.damagefactor*0.5* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.limb.thickness / self.limb.youngs + thickness / self.youngs)**0.25) + self.pushforce)+1
        self.pressure = self.force / self.area
        self.energy = 0.5 * self.strikemass * self.speed ** 2

        self.time = broadcast_time+self.strikelength / self.speed
        self.attacker.stamina[0] -= int(max(1, 7 * self.arm.movemass / self.basestrength))
        self.strikearea=self.area

        self.recoverytime=random.random()*2*self.attacker.focus[1]/max((self.attacker.stats['tec']*self.attacker.focus[0],1))
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        self.resolve()


    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.speed = (2 * self.energy / self.strikemass) ** 0.5
        self.force = self.damagefactor*0.5* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[len(self.basetarget.layers)-1].density**0.25)*(
            self.limb.thickness / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1

class Kick(Attack):
    def __init__(self, limb):
        super().__init__()
        self.damagefactor=1
        self.weapon = None
        self.type = 'crush'
        self.oldtype = 'crush'
        self.limb = limb
        self.attacker = limb.owner
        if self.attacker.player == True:
            self.name = 'a kick with your {}'.format(limb.name)
        else:
            self.name = 'a kick with its {}'.format(limb.name)
        self.arpen = -0.2
        self.accuracy=3
        limb = self.limb
        if hasattr(self.limb,"attachpoint") and self.limb.attachpoint is not None:
            self.leg = limb.attachpoint
            if hasattr(self.leg,"attachpoint") and self.leg.attachpoint is not None:
                self.anchor = self.leg.attachpoint
                self.basestrength = (self.leg.stats['str'] * self.leg.ability + 0.6 * self.anchor.stats[
                    'str'] * self.anchor.ability) * limb.ability ** 0.2 + 0.1
            else:
                self.anchor = None
                self.basestrength = (self.leg.stats['str'] * self.leg.ability) * limb.ability ** 0.2 + 0.1
            self.strikelength = limb.length + limb.attachpoint.length
            self.strikearea = limb.length*limb.radius*2
            self.strikemass = limb.movemass + limb.owner.mass
            self.strength = self.basestrength * (max(self.attacker.stamina[0] / self.attacker.stamina[1],0) ** 0.5)
        else:
            self.leg=self.limb
            self.strikelength=limb.length
            self.strikearea=limb.length*limb.radius*2
            self.strikemass = limb.movemass
            self.basestrength=0.5*self.limb.stats['str']
            self.strength = self.basestrength * (max(self.attacker.stamina[0] / self.attacker.stamina[1],0) ** 0.5)
        self.I=0.25*self.leg.movemass*self.leg.length**2+limb.movemass*self.leg.length**2

    def do(self, target,anglefactor=1):
        self.__init__(self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True

        torque =  7 * self.strength * self.I ** 0.5 + 0.001
        swingangle = random.triangular(low=0.5, high=3, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * swingangle / self.I) ** 0.5)
        self.collidepoint = self.leg.length + self.limb.length / 2
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.001, 1)+0.0001
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=10*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        #print('broadcast time of',broadcast_time,'top w of',self.w,'I of',self.I,'with applied torque of',torque)
        self.time = broadcast_time+(self.I**1.25) * self.w / torque

        self.target.owner.evasion(self)

        movemass = abs(random.gauss(self.target.movemass, 5))
        thickness,density=self.armor_penetration()
        self.strikemass = random.triangular(low=self.limb.movemass, high=self.strikemass, mode=self.strikemass)
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        self.pushforce = 9 * self.strength * self.reducedmass ** 0.5
        #self.force = self.damagefactor*((self.limb.ability ** 0.2) * 1.1 * 0.016 * self.speed * (1000000000 * self.reducedmass / (
         #   self.limb.thickness / self.limb.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce + 1)
        self.force = self.damagefactor*0.5* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.limb.thickness / self.limb.youngs + thickness / self.youngs)**0.25) + self.pushforce)
        self.pressure = self.force / self.strikearea
        #self.energy = 0.5 * self.strikemass * self.speed ** 2


        self.attacker.stamina[0] -= int(max(1, 7 * self.leg.movemass / self.basestrength))

        self.recoverytime=self.I*self.w/torque
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        #print('kick with time of',self.time,'push force of',self.pushforce,'and total force of',self.force,'. speed is',self.speed)

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        new = self.damagefactor*0.5* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.limb.thickness / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

    def test_usability(self):
        if self.leg.ability>0 and self.limb.ability>0:
            self.useless=False
        else:
            self.useless=True

class Slash_1H(Attack):
    def __init__(self, weapon, limb):
        super().__init__()
        self.damagefactor=1
        self.type = 'cut'
        self.oldtype = 'cut'
        self.weapon = weapon
        self.absolute_depth_limit=weapon.length
        self.arpen = 0.05
        self.limb = limb
        self.accuracy=self.limb.dexterity
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        self.strikearea = weapon.edge * weapon.length*(1-weapon.curvature)
        if hasattr(self.arm,'attachpoint') and self.arm.attachpoint is not None:
            self.anchor = self.arm.attachpoint
            self.basestrength = 0.2 * self.limb.stats['str'] * self.limb.ability + 0.7 * self.arm.stats[
                'str'] * self.arm.ability + 0.1 * self.anchor.stats['str'] * self.anchor.ability + 0.1
            armlength = self.arm.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =  weapon.I + 0.5*weapon.mass * (self.arm.length/2+weapon.centermass) ** 2
        elif self.limb.attachpoint is not None:
            self.anchor = None
            self.basestrength = 0.5 * self.limb.stats['str'] * self.limb.ability + 0.5 * self.arm.stats['str'] * self.arm.ability + 0.1
            armlength = self.limb.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =  weapon.I + 0.5*weapon.mass * (self.arm.length/2+weapon.centermass) ** 2
        else:
            self.basestrength=self.limb.stats['str']
            armlength=self.limb.length
            self.arm=self.limb
            self.strikemass = self.limb.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = weapon.I
        self.I+=self.arm.I

        if self.attacker.player == True:
            self.name = 'a slash with your {}'.format(weapon.name)
        else:
            self.name = 'a slash with its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(
            mode=(self.attacker.stats['tec'] + 0.5 * self.attacker.stats['luc']) / (
                target.stats['luc'] + 0.5 * target.stats['tec']))
        self.pushforce = torque #/ self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.05, 0.5, mode=0.5/self.attacker.stats['tec']**0.5)
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1.5,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+(self.I) * self.w / torque

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass/2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass*self.collidepoint**2, 1))
        self.reducedmass = self.I * movemass / (self.I + movemass)
        thickness,density=self.armor_penetration()
        '''if hasattr(self.target,"armor") and self.target.armor is not None:
            thickness=self.target.thickness+self.target.armor.thickness
            density=self.target.armor.density
            coverage=self.target.armor.coverage-self.arpen
            if random.random()>coverage*(2*self.limb.stats['tec']+self.limb.stats['luc']+self.target.stats['luc'])/(2*self.limb.stats['tec']+self.limb.stats['luc']):
            #if self.target.armor.coverage*abs(random.gauss(self.target.stats['luc'],1))<random.random()*(self.limb.stats['luc']+2*self.limb.stats['tec'])/3+self.arpen:
                self.youngs=self.target.arpen_youngs
                self.shear=self.target.arpen_shear
                thickness=self.target.thickness
                density=self.target.layers[len(self.target.layers)-1].density
                self.penetrate=True
            else:
                self.youngs=self.target.youngs
                self.shear=self.target.shear
        else:
            thickness=self.target.thickness
            self.youngs=self.target.youngs
            self.shear=self.target.shear
            if hasattr(self.target,'density'):
                density=self.target.density
            elif hasattr(self.target,'layers'):
                density=self.target.layers[len(self.target.layers)-1].density
            else:
                density=5000'''
        #self.force = self.damagefactor* (self.speed * (1000000000 * self.reducedmass * self.area / (
        #    self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        self.force = self.damagefactor*0.5* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + thickness / self.youngs)**0.25) + self.pushforce)

        #print(self.w,self.reducedmass,1/( self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs))

        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats
        self.attacker.stamina[0] -= int(max(1, 5 * (self.arm.movemass + self.I) / self.basestrength))

        self.recoverytime=random.random()*self.I*self.w/torque
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        self.resolve()

    def energy_recalc(self):
        if self.energy <= 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        target = self.target
        try:
            new = self.damagefactor* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[len(self.basetarget.layers)-1].density**0.25)*(
                self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        except AttributeError: new=self.force
        self.force = min(new, 0.9 * self.force)

class Stab_1H(Attack):
    def __init__(self, weapon, limb):
        super().__init__()
        self.damagefactor=1
        self.type = 'pierce'
        self.oldtype = 'pierce'
        self.absolute_depth_limit=weapon.length
        self.weapon = weapon
        self.arpen = 0.1
        self.limb = limb
        self.accuracy=self.limb.dexterity
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        if hasattr(weapon,'tip'):
            self.strikearea = weapon.tip
        else:
            self.strikearea = 3.14*weapon.radius**2
        if hasattr(self.arm,'attachpoint') and self.arm.attachpoint is not None:
            self.anchor = self.arm.attachpoint
            self.basestrength = 0.2 * self.limb.stats['str'] * self.limb.ability + 0.7 * self.arm.stats[
                'str'] * self.arm.ability + 0.1 * self.anchor.stats['str'] * self.anchor.ability + 0.1
            armlength = self.arm.length
            self.strikemass = self.arm.movemass + weapon.mass + (self.attacker.stats['tec']/(15+self.attacker.stats['tec']))*self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = weapon.I + (1 / 3) * self.arm.mass * armlength ** 2 + weapon.mass * self.arm.length ** 2
        elif self.limb.attachpoint is not None:
            self.anchor = None
            self.basestrength = 0.5 * self.limb.stats['str'] * self.limb.ability + 0.5 * self.arm.stats['str'] * self.arm.ability + 0.1
            armlength = self.limb.length
            self.strikemass = self.arm.movemass + weapon.mass + (self.attacker.stats['tec']/(15+self.attacker.stats['tec']))*self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = weapon.I + (1 / 3) * self.arm.mass * armlength ** 2 + weapon.mass * self.arm.length ** 2
        else:
            self.basestrength=self.limb.stats['str']
            armlength=self.limb.length
            self.arm=self.limb
            self.strikemass = self.limb.movemass + weapon.mass + (self.attacker.stats['tec']/(15+self.attacker.stats['tec']))*self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = weapon.I

        if self.attacker.player == True:
            self.name = 'a stab with your {}'.format(weapon.name)
        else:
            self.name = 'a stab with its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True

        self.pushforce=6*self.strength*self.strikemass**0.5

        self.speed = (random.triangular(0.01,0.8,0.1)*self.strikelength*self.pushforce/self.strikemass)**0.5
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+0.5*(self.speed*self.strikemass**1.25)/self.pushforce


        self.area = self.strikearea
        self.energy = 0.5 * self.strikemass * self.speed ** 2

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass/2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass, 1))*(self.limb.stats['tec']+15)/15+0.1
        self.strikemass = random.triangular(low=self.limb.movemass, high=self.strikemass, mode=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec']))
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        thickness,density=self.armor_penetration()
        #self.force = self.damagefactor* (self.speed * (1000000000 * self.reducedmass * (self.area**0.5) / (
        #    self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        self.force = self.damagefactor*0.5* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.limb.thickness / self.limb.youngs + thickness / self.youngs)**0.25) + self.pushforce)+1


        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats
        self.attacker.stamina[0] -= int(max(1, 5 * (self.arm.movemass + self.weapon.mass) / self.basestrength))

        #print(self.time,self.speed,self.pushforce,self.force,self.pressure)

        self.recoverytime=random.random()*0.5*self.speed*self.strikemass/self.pushforce
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.speed = (2 * self.energy / self.strikemass) ** 0.5
        target = self.target
        new = self.damagefactor * (0.001 * self.speed * (1000000000 * self.reducedmass / (
            self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.target.youngs)) ** 0.5 + self.pushforce)
        self.force = min(new, 0.9 * self.force)

class Bludgeon_1H(Attack):
    def __init__(self, weapon, limb):
        super().__init__()
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.arpen = -0.15
        self.limb = limb
        self.accuracy=self.limb.dexterity
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        self.strikearea = weapon.contactarea
        if hasattr(self.arm,'attachpoint') and self.arm.attachpoint is not None:
            self.anchor = self.arm.attachpoint
            self.basestrength = 0.2 * self.limb.stats['str'] * self.limb.ability + 0.7 * self.arm.stats[
                'str'] * self.arm.ability + 0.1 * self.anchor.stats['str'] * self.anchor.ability + 0.1
            armlength = self.arm.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =  weapon.I + 0.5*weapon.mass * (self.arm.length/2+weapon.centermass) ** 2
        elif self.limb.attachpoint is not None:
            self.anchor = None
            self.basestrength = 0.5 * self.limb.stats['str'] * self.limb.ability + 0.5 * self.arm.stats['str'] * self.arm.ability + 0.1
            armlength = self.limb.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =  weapon.I + 0.5*weapon.mass * (self.arm.length/2+weapon.centermass) ** 2
        else:
            self.basestrength=self.limb.stats['str']
            armlength=self.limb.length
            self.arm=self.limb
            self.strikemass = self.limb.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = weapon.I
        self.I+=self.arm.I

        if self.attacker.player == True:
            self.name = 'a swing of your {}'.format(weapon.name)
        else:
            self.name = 'a swing of its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + (self.I) * self.w / torque

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass / 2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass*self.collidepoint**2, 1))
        self.reducedmass = self.I * movemass / (self.I + movemass)
        thickness,density=self.armor_penetration()
        self.force = self.damagefactor* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + thickness / self.youngs)**0.25) + self.pushforce)
        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats
        self.attacker.stamina[0] -= int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        self.recoverytime=random.random()*self.I*self.w/torque
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.w * (10**3.5) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

class Bite(Attack):
    def __init__(self, limb):
        super().__init__()
        self.damagefactor=1
        self.weapon = None
        self.type = 'pierce'
        self.oldtype = 'pierce'
        self.limb = limb
        self.absolute_depth_limit=limb.radius*2
        self.attacker = limb.owner
        if self.attacker.player == True:
            self.name = 'a bite'
        else:
            self.name = 'a bite'
        self.arpen = -0.2
        self.accuracy=2
        limb = self.limb
        if hasattr(limb,'attachpoint') and self.limb.attachpoint is not None:
            self.head=limb.attachpoint
        else:
            self.head=limb
        self.strikelength=self.head.length
        if any(hasattr(i,'is_teeth') for i in self.limb.limbs):
            self.teeth=[i for i in limb.limbs if hasattr(i,'is_teeth')]
            self.teeth=random.choice(self.teeth)
            self.weapon=self.teeth
        else:
            self.teeth=self.limb
            self.useless=True
        self.bitesize=max(self.limb.radius,self.limb.length)
        self.basestrength=self.limb.stats['str'] * self.bitesize + self.limb.stats['str'] * self.teeth.radius
        self.strength=self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.2) + 0.01


    def do(self, target):
        self.__init__(self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True

        broadcast_time=4*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*(self.attacker.focus[0]+1))
        self.time = broadcast_time+self.head.movemass / self.head.stats['str']
        self.strikearea=(self.teeth.biting_surface)
        self.area=self.strikearea

        self.target.owner.evasion(self,parryable=False)

        if hasattr(self.target,"armor") and self.target.armor is not None:
            thickness=self.target.thickness+self.target.armor.thickness
        else:
            thickness=self.target.thickness

        if thickness<self.limb.length/2:
            self.type='cut'

        if thickness>self.teeth.radius:
            self.damagefactor=self.damagefactor**0.3


        self.reducedmass=1000

        self.force = self.damagefactor*self.strength*250
        self.pressure = self.force / self.area
        self.energy = self.force*self.limb.length

        #print('biting attack force, pressure, time',self.force,self.pressure,self.time)

        self.attacker.stamina[0] -= int(max(1, 7 * self.head.movemass / self.basestrength))

        self.recoverytime=self.head.movemass/self.head.stats['str']
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        self.resolve()

    def energy_recalc(self):
        self.force = self.damagefactor*self.strength*250
        self.pressure = self.force / (self.teeth.length*self.teeth.radius)
        self.energy = self.force*self.limb.length

    def test_usability(self):
        if any(hasattr(i,'is_teeth') for i in self.limb.limbs):
            self.teeth=[i for i in self.limb.limbs if hasattr(i,'is_teeth')]
            self.teeth=random.choice(self.teeth)
            self.weapon=self.teeth
            self.stattedweapon=True
            if self.limb.ability>0:
                self.useless=False
        else:
            self.useless=True
            print('no teeth')
            return
            #self.limb.attacks.remove(self)

class Swing_Pierce_1H(Bludgeon_1H):
    def __init__(self,weapon,limb):
        super().__init__(weapon,limb)
        self.type='pierce'
        self.oldtype='pierce'
        self.arpen=0
        self.absolute_depth_limit=0.1
        self.strikearea=weapon.tip
        self.area=self.strikearea

    def do(self,target,anglefactor=1):
        super().do(target,anglefactor)

class Shield_Bash(Bludgeon_1H):
    def __init__(self,weapon,limb):
        super().__init__(weapon,limb)
        if self.arm is not None:
            self.accuracy=(self.limb.ability+self.arm.ability)*4/weapon.mass
        else:
            self.accuracy=self.limb.ability*4/weapon.mass
        if self.attacker.player == True:
            self.name = 'a bash with your {}'.format(weapon.name)
        else:
            self.name = 'a bash with its {}'.format(weapon.name)

        self.strength=self.strength/8
        self.arpen-=1

    def do(self, target):
        super().do(target,anglefactor=0.1/self.weapon.mass)
        if self.blocked==False and self.parried==False and self.dodged==False:
            creature=self.basetarget.owner
            if 2*self.strikemass*random.random()*self.attacker.stats['per']**0.5>(creature.mass**0.5)*random.random()*creature.stats['per']*creature.balance*creature.focus[0]/creature.focus[1]:
                if "off_balance" not in creature.conditions:
                    creature.conditions.append("off_balance")
                    messages.append("{} is knocked off balance!".format(creature.name))

class Strike_1H(Attack):
    def __init__(self, weapon, limb=None):
        super().__init__()
        if limb==None:
            limb=weapon
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.arpen = -0.15
        self.limb = limb
        self.accuracy=self.limb.dexterity
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        self.strikearea = weapon.radius*weapon.thickness
        if hasattr(self.weapon,'centermass'):
            centermass=self.weapon.centermass
        else:
            centermass=self.weapon.length/2
        if hasattr(self.arm,'attachpoint') and self.arm.attachpoint is not None:
            self.anchor = self.arm.attachpoint
            self.basestrength = 0.2 * self.limb.stats['str'] * self.limb.ability + 0.7 * self.arm.stats[
                'str'] * self.arm.ability + 0.1 * self.anchor.stats['str'] * self.anchor.ability + 0.1
            armlength = self.arm.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =  weapon.I + 0.5*weapon.mass * (self.arm.length/2+centermass) ** 2
        elif self.limb.attachpoint is not None:
            self.anchor = None
            self.basestrength = 0.5 * self.limb.stats['str'] * self.limb.ability + 0.5 * self.arm.stats['str'] * self.arm.ability + 0.1
            armlength = self.limb.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =  weapon.I + 0.5*weapon.mass * (self.arm.length/2+centermass) ** 2
        else:
            self.basestrength=self.limb.stats['str']
            armlength=self.limb.length
            self.arm=self.limb
            self.strikemass = self.limb.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = weapon.I
        self.I+=self.arm.I

        if self.weapon==self.limb:
            self.strikelength=self.weapon.length
            self.I=self.weapon.I
            self.strikemass=self.weapon.mass+self.attacker.mass

        if self.attacker.player == True:
            self.name = 'a strike with your {}'.format(weapon.name)
        else:
            self.name = 'a strike with its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + (self.I) * self.w / torque

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass / 2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass*self.collidepoint**2, 1))
        self.reducedmass = self.I * movemass / (self.I + movemass)
        thickness,density=self.armor_penetration()
        if not hasattr(self.weapon,'thickness'):
            self.weapon.thickness=2*self.weapon.radius
        self.force = self.damagefactor* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + thickness / self.youngs)**0.25) + self.pushforce)
        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats
        self.attacker.stamina[0] -= int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        self.recoverytime=random.random()*self.I*self.w/torque
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        print(self.time,self.recoverytime,self.w)

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.w * (10**3.5) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

class Scratch(Attack):
    def __init__(self, weapon, limb=None):
        super().__init__()
        if limb==None:
            limb=weapon
        self.damagefactor=1
        self.type = 'cut'
        self.oldtype = 'cut'
        self.weapon = weapon
        self.arpen = 0
        self.limb = limb
        self.absolute_depth_limit=self.weapon.length
        self.accuracy=self.limb.ability*5
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        self.strikearea = weapon.tip
        if hasattr(self.weapon,'centermass'):
            centermass=self.weapon.centermass
        else:
            centermass=self.weapon.length/2
        if hasattr(self.arm,'attachpoint') and self.arm.attachpoint is not None:
            self.anchor = self.arm.attachpoint
            self.basestrength = 0.2 * self.limb.stats['str'] * self.limb.ability + 0.7 * self.arm.stats[
                'str'] * self.arm.ability + 0.1 * self.anchor.stats['str'] * self.anchor.ability + 0.1
            armlength = self.arm.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =  weapon.I + 0.5*weapon.mass * (self.arm.length/2+centermass) ** 2
        elif self.limb.attachpoint is not None:
            self.anchor = None
            self.basestrength = 0.5 * self.limb.stats['str'] * self.limb.ability + 0.5 * self.arm.stats['str'] * self.arm.ability + 0.1
            armlength = self.limb.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =  weapon.I + 0.5*weapon.mass * (self.arm.length/2+centermass) ** 2
        else:
            self.basestrength=self.limb.stats['str']
            armlength=self.limb.length
            self.arm=self.limb
            self.strikemass = self.limb.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = weapon.I
        self.I+=self.arm.I

        if self.weapon==self.limb:
            self.strikelength=self.weapon.length
            self.I=self.weapon.I
            self.strikemass=self.weapon.mass+self.attacker.mass

        if self.attacker.player == True:
            self.name = 'a scratch with your {}'.format(weapon.name)
        else:
            self.name = 'a scratch with its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + (self.I) * self.w / torque

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass / 2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass*self.collidepoint**2, 1))
        self.reducedmass = self.I * movemass / (self.I + movemass)
        thickness,density=self.armor_penetration()
        if not hasattr(self.weapon,'thickness'):
            self.weapon.thickness=2*self.weapon.radius
        self.force = self.damagefactor* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + thickness / self.youngs)**0.25) + self.pushforce)
        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats
        self.attacker.stamina[0] -= int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        self.recoverytime=random.random()*self.I*self.w/torque
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        print(self.time,self.recoverytime,self.w)

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.w * (10**3.5) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

class Touch(Attack):
    def __init__(self, weapon, limb=None):
        super().__init__()
        if limb==None:
            limb=weapon
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.arpen = -0.15
        self.limb = limb
        self.accuracy=self.limb.dexterity
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        self.strikearea = weapon.radius*weapon.thickness
        if hasattr(self.weapon,'centermass'):
            centermass=self.weapon.centermass
        else:
            centermass=self.weapon.length/2
        if hasattr(self.arm,'attachpoint') and self.arm.attachpoint is not None:
            self.anchor = self.arm.attachpoint
            self.basestrength = 0.2 * self.limb.stats['str'] * self.limb.ability + 0.7 * self.arm.stats[
                'str'] * self.arm.ability + 0.1 * self.anchor.stats['str'] * self.anchor.ability + 0.1
            armlength = self.arm.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =  weapon.I + 0.5*weapon.mass * (self.arm.length/2+centermass) ** 2
        elif self.limb.attachpoint is not None:
            self.anchor = None
            self.basestrength = 0.5 * self.limb.stats['str'] * self.limb.ability + 0.5 * self.arm.stats['str'] * self.arm.ability + 0.1
            armlength = self.limb.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =  weapon.I + 0.5*weapon.mass * (self.arm.length/2+centermass) ** 2
        else:
            self.basestrength=self.limb.stats['str']
            armlength=self.limb.length
            self.arm=self.limb
            self.strikemass = self.limb.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = weapon.I
        self.I+=self.arm.I

        if self.weapon==self.limb:
            self.strikelength=self.weapon.length
            self.I=self.weapon.I
            self.strikemass=self.weapon.mass+self.attacker.mass

        if self.attacker.player == True:
            self.name = 'a touch with your {}'.format(weapon.name)
        else:
            self.name = 'a touch with its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + (self.I) * self.w / torque

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass / 2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)

        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats

        self.attacker.stamina[0] -= int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        self.recoverytime=random.random()*self.I*self.w/torque
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        self.resolve()

    def resolve(self):
        if hasattr(self.weapon,'layers'):
            self.weapon=self.weapon.layers[len(self.weapon.layers)-1]
        if self.dodged==True:
            messages.append("The attack was avoided!")
            self.unstatweapon()
            self.attacker.recoverytime=self.recoverytime
            return
        if self.parried==True:
            messages.append("The attack was parried with the {}".format(self.target.name))
            for i in self.weapon.coatings:
                i.add(self.target)
            self.target.functioncheck()
            self.unstatweapon()
            self.attacker.recoverytime=(1+random.random())*self.recoverytime

            return
        if self.blocked==True:
            messages.append("The attack was blocked with the {}".format(self.target.name))
            for i in self.weapon.coatings:
                i.add(self.target)
            self.target.functioncheck()
            self.unstatweapon()
            self.attacker.recoverytime=(1+random.random())*self.recoverytime

            return

        for i in self.weapon.coatings:
            i.add(self.target)

        self.target.on_struck(self)

        self.basetarget.owner.combataction = True
        self.attacker.focus[0] -= 1





    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.w * (10**3.5) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

class Blunt_Thrust_1H(Stab_1H):
    def __init__(self,weapon,limb):
        super().__init__(weapon,limb)
        self.type='crush'
        self.oldtype='crush'
        if self.attacker.player == True:
            self.name = 'a thrust with your {}'.format(weapon.name)
        else:
            self.name = 'a thrust with its {}'.format(weapon.name)




class Slash_2H(Attack):
    def __init__(self, weapon, limb):
        super().__init__()
        self.limb=limb
        self.hands=2
        self.damagefactor=1
        self.absolute_depth_limit=weapon.length
        self.type = 'cut'
        self.oldtype = 'cut'
        self.weapon = weapon
        self.arpen = 0
        self.limbs = self.weapon.equipped
        self.attacker = limb.owner
        self.strikearea = weapon.edge * weapon.length*(1-weapon.curvature)
        self.accuracy=0
        self.basestrength=0
        self.strikemass=weapon.mass + self.attacker.mass
        self.strikelength=100
        self.I = weapon.I

        for i in self.limbs:
            self.accuracy=(i.dexterity**2+self.accuracy**2)**0.5
            arm = i.attachpoint
            if hasattr(arm,'attachpoint') and arm.attachpoint is not None:
                anchor = arm.attachpoint
                self.basestrength = ((0.2 * i.stats['str'] * i.ability + 0.7 * arm.stats[
                    'str'] * arm.ability + 0.1 * anchor.stats['str'] * anchor.ability + 0.1)**2+self.basestrength**2)**0.5
                armlength = arm.length
                self.strikemass += arm.movemass
                self.strikelength = min(weapon.length + armlength,self.strikelength)
            elif i.attachpoint is not None:
                anchor = None
                self.basestrength = ((0.5 * i.stats['str'] * i.ability + 0.5 * arm.stats['str'] * arm.ability + 0.1)**2+self.basestrength**2)**0.5
                armlength = i.length
                self.strikemass += arm.movemass
                self.strikelength =  min(weapon.length + armlength,self.strikelength)
            else:
                self.basestrength=(i.stats['str']**2+self.basestrength**2)**0.5
                armlength=i.length
                arm=i
                self.strikemass += i.movemass
                self.strikelength = min(weapon.length + armlength,self.strikelength)
            self.I+=arm.I

        self.I+=0.5*weapon.mass * ((self.strikelength-weapon.length)/2+weapon.centermass) ** 2

        if self.attacker.player == True:
            self.name = 'a slash with your {}'.format(weapon.name)
        else:
            self.name = 'a slash with its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * swingangle / self.I) ** 0.5)
        self.collidepoint = self.strikelength * random.triangular(
            mode=(self.attacker.stats['tec'] + 0.5 * self.attacker.stats['luc']) / (
                target.stats['luc'] + 0.5 * target.stats['tec']))
        self.pushforce = torque #/ self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.05, 0.5, mode=0.5/self.attacker.stats['tec']**0.5)
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1.5,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+(self.I) * self.w / torque

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass/2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass*self.collidepoint**2, 1))
        self.reducedmass = self.I * movemass / (self.I + movemass)
        thickness,density=self.armor_penetration()
        '''if hasattr(self.target,"armor") and self.target.armor is not None:
            thickness=self.target.thickness+self.target.armor.thickness
            density=self.target.armor.density
            if self.target.armor.coverage*abs(random.gauss(self.target.stats['luc'],1))<random.random()*(random.choice(self.limbs).stats['luc']+2*random.choice(self.limbs).stats['tec'])/3+self.arpen:
                self.youngs=self.target.arpen_youngs
                self.shear=self.target.arpen_shear
                thickness=self.target.thickness
                density=self.target.layers[len(self.target.layers)-1].density
                self.penetrate=True
            else:
                self.youngs=self.target.youngs
                self.shear=self.target.shear
        else:
            thickness=self.target.thickness
            self.youngs=self.target.youngs
            self.shear=self.target.shear
            if hasattr(self.target,'density'):
                density=self.target.density
            elif hasattr(self.target,'layers'):
                density=self.target.layers[len(self.target.layers)-1].density
            else:
                density=5000
        '''
        #self.force = self.damagefactor* (self.speed * (1000000000 * self.reducedmass * self.area / (
        #    self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        self.force = self.damagefactor*0.5* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + thickness / self.youngs)**0.25) + self.pushforce)

        #print(self.w,self.reducedmass,1/( self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs))

        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.attacker.stats
        self.attacker.stamina[0] -= int(max(1, 10 * (self.strikemass-self.attacker.mass + self.I) / self.basestrength))

        self.recoverytime=random.random()*self.I*self.w/torque
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        target = self.target
        new = self.damagefactor* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[len(self.basetarget.layers)-1].density**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

class Stab_2H(Attack):
    def __init__(self, weapon, limb):
        super().__init__()
        self.hands=2
        self.damagefactor=1
        self.type = 'pierce'
        self.oldtype = 'pierce'
        self.absolute_depth_limit=weapon.length
        self.weapon = weapon
        self.limbs=weapon.equipped
        if hasattr(weapon,'tip'):
            self.strikearea = weapon.tip
        else:
            self.strikearea = 3.14*weapon.radius**2
        self.arpen = 0.1
        self.limb = limb
        self.attacker = limb.owner
        self.accuracy=0
        self.basestrength=0
        self.strikelength=100
        self.strikemass=weapon.mass
        self.I=weapon.I

        for i in self.limbs:
            self.accuracy=(i.dexterity**2+self.accuracy**2)**0.5
            arm = i.attachpoint
            if hasattr(arm,'attachpoint') and arm.attachpoint is not None:
                anchor = arm.attachpoint
                self.basestrength = ((0.2 * i.stats['str'] * i.ability + 0.7 * arm.stats[
                    'str'] * arm.ability + 0.1 * anchor.stats['str'] * anchor.ability + 0.1)**2+self.basestrength**2)**0.5
                armlength = arm.length
                self.strikemass += arm.movemass + (i.stats['tec']/(15+i.stats['tec']))*self.attacker.mass
                self.strikelength = min(weapon.length + armlength,self.strikelength)
                self.I += arm.I
            elif i.attachpoint is not None:
                anchor = None
                self.basestrength = ((0.5 * i.stats['str'] * i.ability + 0.5 * arm.stats['str'] * arm.ability + 0.1)**2+self.basestrength**2)**0.5
                armlength = i.length
                self.strikemass += arm.movemass + (i.stats['tec']/(15+i.stats['tec']))*self.attacker.mass
                self.strikelength = min(weapon.length + armlength,self.strikelength)
                self.I += arm.I
            else:
                self.basestrength=i.stats['str']
                armlength=i.length
                self.strikemass += i.movemass + (i.stats['tec']/(15+i.stats['tec']))*self.attacker.mass
                self.strikelength = min(weapon.length + armlength,self.strikelength)
                self.I += arm.I

        if self.attacker.player == True:
            self.name = 'a stab with your {}'.format(weapon.name)
        else:
            self.name = 'a stab with its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True

        self.pushforce=6*self.strength*self.strikemass**0.5

        self.speed = (random.triangular(0.01,0.8,0.1)*self.strikelength*self.pushforce/self.strikemass)**0.5
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+0.5*(self.speed*self.strikemass**1.25)/self.pushforce


        self.area = self.strikearea
        self.energy = 0.5 * self.strikemass * self.speed ** 2

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass/2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        tec=sum(i.stats['tec']**2 for i in self.limbs)**0.5
        movemass = abs(random.gauss(self.target.movemass, 1))*(tec+15)/15+0.1
        self.strikemass = random.triangular(low=self.weapon.mass, high=self.strikemass, mode=1.5*self.strikemass*tec/(10+tec))
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        thickness,density=self.armor_penetration()

        #self.force = self.damagefactor* (self.speed * (1000000000 * self.reducedmass * (self.area**0.5) / (
        #    self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        self.force = self.damagefactor*0.5* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.limb.thickness / self.limb.youngs + thickness / self.youngs)**0.25) + self.pushforce)+1


        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats
        self.attacker.stamina[0] -= int(max(1, 10 * (sum(i.movemass for i in self.limbs) + self.weapon.mass) / (self.basestrength+0.01)))

        self.recoverytime=random.random()*0.5*self.speed*self.strikemass/self.pushforce
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        #print(self.time,self.speed,self.pushforce,self.force,self.pressure)

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.speed = (2 * self.energy / self.strikemass) ** 0.5
        target = self.target
        new = self.damagefactor * (0.001 * self.speed * (1000000000 * self.reducedmass / (
            self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.target.youngs)) ** 0.5 + self.pushforce)
        self.force = min(new, 0.9 * self.force)

class Bludgeon_2H(Attack):
    def __init__(self, weapon, limb):
        super().__init__()
        self.hands=2
        self.limbs=weapon.equipped
        self.attacker = limb.owner
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.arpen = -0.15
        self.limb = limb
        self.accuracy=0
        self.basestrength=0
        self.strikelength=100
        self.strikemass=weapon.mass+self.attacker.mass
        self.strikearea = weapon.contactarea
        self.I=weapon.I


        for i in self.limbs:
            self.accuracy=(i.dexterity**2+self.accuracy**2)**0.5
            arm = i.attachpoint
            if hasattr(arm,'attachpoint') and arm.attachpoint is not None:
                anchor = arm.attachpoint
                self.basestrength = ((0.2 * i.stats['str'] * i.ability + 0.7 * arm.stats[
                    'str'] * arm.ability + 0.1 * anchor.stats['str'] * anchor.ability + 0.1)**2+self.basestrength**2)**0.5
                armlength = arm.length
                self.strikemass += arm.movemass
                self.strikelength = min(weapon.length + armlength,self.strikelength)
            elif i.attachpoint is not None:
                anchor = None
                self.basestrength = ((0.5 * i.stats['str'] * i.ability + 0.5 * arm.stats['str'] * arm.ability + 0.1)**2+self.basestrength**2)**0.5
                armlength = i.length
                self.strikemass += arm.movemass
                self.strikelength =  min(weapon.length + armlength,self.strikelength)
            else:
                self.basestrength=(i.stats['str']**2+self.basestrength**2)**0.5
                armlength=i.length
                arm=i
                self.strikemass += i.movemass
                self.strikelength = min(weapon.length + armlength,self.strikelength)
            self.I+=arm.I

        self.I+=0.5*weapon.mass * ((self.strikelength-weapon.length)/2+weapon.centermass) ** 2

        if self.attacker.player == True:
            self.name = 'a swing of your {}'.format(weapon.name)
        else:
            self.name = 'a swing of its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.strikelength - self.weapon.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + (self.I) * self.w / torque

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass / 2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass*self.collidepoint**2, 1))
        self.reducedmass = self.I * movemass / (self.I + movemass)
        thickness,density=self.armor_penetration()
        self.force = self.damagefactor* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + thickness / self.youngs)**0.25) + self.pushforce)
        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats
        self.attacker.stamina[0] -= int(max(1, 8 * (sum(i.movemass for i in self.limbs) + self.I) / (self.basestrength+0.01)))

        self.recoverytime=self.I*self.w/torque
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.w * (10**3.5) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

class Swing_Pierce_2H(Bludgeon_2H):
    def __init__(self,weapon,limb):
        super().__init__(weapon,limb)
        self.type='pierce'
        self.oldtype='pierce'
        self.arpen=0
        self.absolute_depth_limit=0.1
        self.strikearea=weapon.tip
        self.area=self.strikearea

    def do(self,target,anglefactor=1):
        super().do(target,anglefactor)

class Shield_Bash_2H(Bludgeon_2H):
    def __init__(self,weapon,limb):
        super().__init__(weapon,limb)
        self.accuracy=0
        for i in self.limbs:
            if hasattr(i,'attachpoint') and i.attachpoint is not None:
                self.accuracy+=(i.ability+i.attachpoint.ability)*4/weapon.mass
            else:
                self.accuracy=i.ability*4/weapon.mass
        if self.attacker.player == True:
            self.name = 'a bash with your {}'.format(weapon.name)
        else:
            self.name = 'a bash with its {}'.format(weapon.name)

        self.strength=self.strength/8
        self.arpen-=1

    def do(self, target):
        super().do(target,anglefactor=0.1/self.weapon.mass)
        if self.blocked==False and self.parried==False and self.dodged==False:
            creature=self.basetarget.owner
            if 2*self.strikemass*random.random()*self.attacker.stats['per']**0.5>(creature.mass**0.5)*random.random()*creature.stats['per']*creature.balance*creature.focus[0]/creature.focus[1]:
                if "off_balance" not in creature.conditions:
                    creature.conditions.append("off_balance")
                    messages.append("{} is knocked off balance!".format(creature.name))

class Strike_2H(Attack):
    def __init__(self, weapon, limb):
        super().__init__()
        self.hands=2
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.arpen = -0.15
        self.limb = limb
        self.limbs= weapon.equipped
        self.accuracy=0
        self.basestrength=0
        self.attacker = limb.owner
        self.strikearea = weapon.radius*weapon.thickness
        if hasattr(self.weapon,'centermass'):
            centermass=self.weapon.centermass
        else:
            centermass=self.weapon.length/2
        self.strikelength=100
        self.strikemass=weapon.mass+self.attacker.mass
        self.I=self.weapon.I


        for i in self.limbs:
            arm = i.attachpoint
            self.accuracy=(i.dexterity**2+self.accuracy**2)**0.5
            if hasattr(arm,'attachpoint') and arm.attachpoint is not None:
                anchor = arm.attachpoint
                self.basestrength = ((0.2 * i.stats['str'] * i.ability + 0.7 * arm.stats[
                    'str'] * arm.ability + 0.1 * anchor.stats['str'] * anchor.ability + 0.1)**2+self.basestrength**2)**0.5
                armlength = arm.length
                self.strikemass += arm.movemass
                self.strikelength = min(weapon.length + armlength,self.strikelength)
            elif self.limb.attachpoint is not None:
                anchor = None
                self.basestrength = ((0.5 * i.stats['str'] * i.ability + 0.5 * arm.stats['str'] * arm.ability + 0.1)**2+self.basestrength**2)**0.5
                armlength = i.length
                self.strikemass += arm.movemass
                self.strikelength = min(weapon.length + armlength,self.strikelength)
            else:
                self.basestrength=(i.stats['str']**2+self.basestrength**2)**0.5
                armlength=i.length
                arm=i
                self.strikemass += i.movemass
                self.strikelength = min(weapon.length + armlength,self.strikelength)
            self.I+=arm.I

        self.I+=0.5*weapon.mass * ((self.strikelength-weapon.length)/2+centermass) ** 2

        if self.attacker.player == True:
            self.name = 'a strike with your {}'.format(weapon.name)
        else:
            self.name = 'a strike with its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        defender_reach=target.owner.reach
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.strikelength - self.weapon.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + (self.I) * self.w / torque

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass / 2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass*self.collidepoint**2, 1))
        self.reducedmass = self.I * movemass / (self.I + movemass)
        thickness,density=self.armor_penetration()
        if not hasattr(self.weapon,'thickness'):
            self.weapon.thickness=2*self.weapon.radius
        self.force = self.damagefactor* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + thickness / self.youngs)**0.25) + self.pushforce)
        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats
        self.attacker.stamina[0] -= int(max(1, 8 * (sum(i.movemass for i in self.limbs) + self.I) / (self.basestrength+0.01)))

        self.recoverytime=random.random()*self.I*self.w/torque
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        print(self.time,self.recoverytime,self.w)

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.w * (10**3.5) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

class Blunt_Thrust_2H(Stab_2H):
    def __init__(self,weapon,limb):
        super().__init__(weapon,limb)
        self.type='crush'
        self.oldtype='crush'
        if self.attacker.player == True:
            self.name = 'a thrust with your {}'.format(weapon.name)
        else:
            self.name = 'a thrust with its {}'.format(weapon.name)

class Experimental_Bash(Attack):
    def __init__(self, weapon, limb):
        super().__init__()
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.arpen = -0.1
        self.limb = limb
        self.accuracy=self.limb.dexterity
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        self.strikearea = weapon.contactarea
        if hasattr(self.arm,'attachpoint') and self.arm.attachpoint is not None:
            self.anchor = self.arm.attachpoint
            self.basestrength = 0.2 * self.limb.stats['str'] * self.limb.ability + 0.7 * self.arm.stats[
                'str'] * self.arm.ability + 0.1 * self.anchor.stats['str'] * self.anchor.ability + 0.1
            armlength = self.arm.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = 3 * weapon.I + 0.5*weapon.mass * (self.arm.length/2+weapon.centermass) ** 2
        elif self.limb.attachpoint is not None:
            self.anchor = None
            self.basestrength = 0.5 * self.limb.stats['str'] * self.limb.ability + 0.5 * self.arm.stats['str'] * self.arm.ability + 0.1
            armlength = self.limb.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = 3 * weapon.I + 0.5*weapon.mass * (self.arm.length/2+weapon.centermass) ** 2
        else:
            self.basestrength=self.limb.stats['str']
            armlength=self.limb.length
            self.arm=self.limb
            self.strikemass = self.limb.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = 3*weapon.I

        if self.attacker.player == True:
            self.name = 'a swing of your {}'.format(weapon.name)
        else:
            self.name = 'a swing of its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 8 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + (self.I) * self.w / torque

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass / 2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass*self.collidepoint**2, 1))
        self.reducedmass = self.I * movemass / (self.I + movemass)
        if hasattr(self.target,"armor") and self.target.armor is not None:
            thickness=self.target.thickness+self.target.armor.thickness
            density=self.target.armor.density
        else:
            thickness=self.target.thickness
            if hasattr(self.target,'density'):
                density=self.target.density
            elif hasattr(self.target,'layers'):
                density=self.target.layers[len(self.target.layers)-1].density
            else:
                density=5000
        self.force = self.damagefactor* (self.w * (10**3.4) * (self.target.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)**0.25) + self.pushforce)
        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats
        self.attacker.stamina[0] -= int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        target = self.target
        new = self.damagefactor*(self.w * (10**3.5) * (self.target.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[len(self.basetarget.layers)-1].density**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.target.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

#Abilities go below here

class Targeted_Ability(Attack):
    pass






# A person can swing with two hands an object with a moment of inertia of 0.1646 kg m^2 with a top radial speed
#of about 30 rad/sec. It seems that I*w^4 is approximately constant, though there is clearly more work that needs done.

#Old slash is stored here:
'''
class Slash_1H(Attack):
    def __init__(self, weapon, limb):
        super().__init__()
        self.damagefactor=1
        self.type = 'cut'
        self.oldtype = 'cut'
        self.weapon = weapon
        self.arpen = 0.05
        self.limb = limb
        self.accuracy=self.limb.dexterity
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        self.strikearea = weapon.edge * weapon.length*(1-weapon.curvature)
        if hasattr(self.arm,'attachpoint') and self.arm.attachpoint is not None:
            self.anchor = self.arm.attachpoint
            self.basestrength = 0.2 * self.limb.stats['str'] * self.limb.ability + 0.7 * self.arm.stats[
                'str'] * self.arm.ability + 0.1 * self.anchor.stats['str'] * self.anchor.ability + 0.1
            armlength = self.arm.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = 10*weapon.I + (1 / 24) * self.arm.movemass * armlength ** 2 + weapon.mass * (self.arm.length/2+weapon.centermass) ** 2
        elif self.limb.attachpoint is not None:
            self.anchor = None
            self.basestrength = 0.5 * self.limb.stats['str'] * self.limb.ability + 0.5 * self.arm.stats['str'] * self.arm.ability + 0.1
            armlength = self.limb.length
            self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I =10*weapon.I + (1 / 24) * self.arm.movemass * armlength ** 2 + weapon.mass * (self.arm.length/2+weapon.centermass) ** 2
        else:
            self.basestrength=self.limb.stats['str']
            armlength=self.limb.length
            self.arm=self.limb
            self.strikemass = self.limb.movemass + weapon.mass + self.attacker.mass
            self.strikelength = weapon.length + armlength
            self.I = 10*weapon.I

        if self.attacker.player == True:
            self.name = 'a slash with your {}'.format(weapon.name)
        else:
            self.name = 'a slash with its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1):
        self.__init__(self.weapon, self.limb)
        self.basetarget = target
        self.target = target
        self.contact = True
        torque =  10 * self.strength * self.I ** 0.5
        swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])*anglefactor
        self.w = ((2 * torque * swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(
            mode=(self.attacker.stats['tec'] + 0.5 * self.attacker.stats['luc']) / (
                target.stats['luc'] + 0.5 * target.stats['tec']))
        self.pushforce = torque #/ self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.001, 1, mode=1/self.attacker.stats['tec']**0.5)
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1.5,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+1.5*(self.I) * self.w / torque

        self.target.owner.evasion(self)

        maxtargetmass = self.target.movemass + target.owner.movemass/2
        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass*self.collidepoint**2, 1))
        self.I=self.I*4
        self.reducedmass = self.I * movemass / (self.I + movemass)
        if hasattr(self.target,"armor") and self.target.armor is not None:
            thickness=self.target.thickness+self.target.armor.thickness
        else:
            thickness=self.target.thickness
        #self.force = self.damagefactor* (self.speed * (1000000000 * self.reducedmass * self.area / (
        #    self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        self.force = self.damagefactor* (0.005 * self.w * (1000000000 * self.reducedmass / (
            self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        #print(self.w,self.reducedmass,1/( self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs))

        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats
        self.attacker.stamina[0] -= int(max(1, 5 * (self.arm.movemass + self.I) / self.basestrength))

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        target = self.target
        new = self.damagefactor* (0.005 * self.w * (1000000000 * self.reducedmass / (
            self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.target.youngs)) ** 0.5 + self.pushforce)
        self.force = min(new, 0.9 * self.force)
'''

def SwingSpeed(attacker, twohand=False):
    if twohand == True:
        weapon = attacker.weapon
        arm1 = attacker.rightarm
        arm2 = attacker.leftarm
        I = 2 * weapon.I + (
            (1 / 3) * arm1.mass * arm1.length ** 2 + (1 / 3) * arm2.mass * arm2.length ** 2) + weapon.mass * ((
                                                                                                                  arm1.length + arm2.length) / 2) ** 2
        torque = (5 * arm1.stats['strength'] + 5 * arm2.stats['strength']) * I ** 0.5
        vmax = (weapon.length + ((arm1.length + arm2.length) / 2))*(2 * 3.14 * torque / I) ** 0.5
        swingtime = I * (vmax / (weapon.length + ((arm1.length + arm2.length) / 2))) / torque

    return swingtime, vmax




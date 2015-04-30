__author__ = 'Alan'
import random
from BaseClasses import *
from UI_Elements import *

#TODO: 2-handed attacks still require implementation. All weapons should be 1- or 2- handable at least. More than 2 hands is also a possibility

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
        elif target == None:
            targetroll = targetroll - limb.sizefactor


class Attack():
    def __init__(self):
        pass

    def resolve(self):
        f=self.force

        self.blocked=False
        self.dodged=False
        self.parried=False


        self.damage_dealt = 0
        self.target.owner.evasion(self)

        if self.dodged==True:
            messages.append("The attack was avoided!")
            return
        if self.parried==True:
            messages.append("The attack was parried with the {}".format(self.target.name))
            self.target.damageresolve(self,self.limb)
            self.target.functioncheck()

            return

        self.target.damageresolve(self, self.limb)
        if self.damage_dealt <= 0 and self.parried==False:
            messages.append("The attack glances off harmlessly")
        self.basetarget.owner.combataction = True
        self.attacker.focus[0] -= 1

        self.arpen = -15
        self.force = f / 10
        self.pressure = f / self.strikearea
        self.reaction_damage_processed = False
        if hasattr(self,'weapon') and self.weapon:
            self.weapon.damageresolve(self,self.basetarget,reactionforce=True)
        else:
            self.limb.damageresolve(self, self.basetarget, reactionforce=True)








class Punch(Attack):
    def __init__(self, limb):
        self.weapon = None
        self.type = 'crush'
        self.limb = limb
        self.attacker = limb.owner
        if self.attacker.player == True:
            self.name = 'a punch with your {}'.format(limb.name)
        else:
            self.name = 'a punch from its {}'.format(limb.name)


    def do(self, target):
        self.arpen = -0.1
        self.accuracy=5
        limb = self.limb
        self.arm = limb.attachpoint
        if self.arm.attachpoint:
            self.anchor = self.arm.attachpoint
            self.basestrength = (self.arm.stats['str'] * self.arm.ability + 0.6 * self.anchor.stats[
                'str'] * self.anchor.ability) * limb.ability ** 0.2
        else:
            self.anchor = None
            self.basestrength = (self.arm.stats['str'] * self.arm.ability) * limb.ability ** 0.2
        self.strikelength = limb.length + limb.attachpoint.length
        self.strikearea = 3.14 * limb.radius ** 2
        self.strikemass = limb.movemass + limb.owner.movemass
        self.strength = self.basestrength * (max(self.attacker.stamina[0] / self.attacker.stamina[1],0) ** 0.5)
        self.basetarget = target
        self.target = target
        self.contact = True
        maxtargetmass = target.movemass + target.owner.mass
        movemass = random.triangular(low=target.movemass, high=maxtargetmass, mode=target.movemass)
        self.strikemass = random.triangular(low=self.limb.mass, high=self.strikemass, mode=self.strikemass)
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        self.pushforce = 11 * self.strength * self.reducedmass ** 0.5
        highspeed = max(4 * (max(self.strength / self.arm.movemass,0)) ** 0.5, 8)
        self.speed = random.triangular(low=1, high=highspeed, mode=4) * (
            (self.attacker.stamina[0] / self.attacker.stamina[1]) ** 2) + 0.1
        self.force = (limb.ability ** 0.2) * 1.1 * self.speed * (1000000000 * self.reducedmass * self.strikearea / (
            self.limb.thickness / self.limb.youngs + target.thickness / target.youngs)) ** 0.5 + self.pushforce + 1
        self.pressure = self.force / self.strikearea
        f = self.force
        self.energy = 0.5 * self.strikemass * self.speed ** 2
        broadcast_time=2*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*(self.attacker.focus[0]+1))
        self.time = broadcast_time+self.strikelength / self.speed
        self.attacker.stamina[0] -= int(max(1, 7 * self.arm.movemass / self.attacker.stats['str']))


        self.resolve()




    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            return
        self.speed = (2 * self.energy / self.strikemass) ** 0.5
        self.force = self.speed * (1000000000 * self.reducedmass * self.strikearea / (
            self.limb.thickness / self.limb.youngs + self.basetarget.thickness / self.basetarget.youngs)) ** 0.5 + self.pushforce


class Slash_1H(Attack):
    def __init__(self, weapon, limb):
        self.type = 'cut'
        self.weapon = weapon
        self.arpen = 0.05
        self.limb = limb
        self.accuracy=self.limb.dexterity
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        if self.arm.attachpoint:
            self.anchor = self.arm.attachpoint
            self.basestrength = 0.2 * self.limb.stats['str'] * self.limb.ability + 0.7 * self.arm.stats[
                'str'] * self.arm.ability + 0.1 * self.anchor.stats['str'] * self.anchor.ability
            armlength = self.arm.length
        else:
            self.anchor = None
            self.basestrength = 0.5 * self.limb['str'] * self.limb.ability + 0.5 * self.arm['str'] * self.arm.ability
            armlength = self.limb.length
        self.strikelength = weapon.length + armlength
        self.strikearea = weapon.edge * weapon.length
        self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
        self.I = weapon.I + (1 / 3) * self.arm.mass * armlength ** 2 + weapon.mass * self.arm.length ** 2
        if self.attacker.player == True:
            self.name = 'a slash with your {}'.format(weapon.name)
        else:
            self.name = 'a slash with its {}'.format(weapon.name)


    def do(self, target):
        self.__init__(self.weapon, self.limb)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01
        self.basetarget = target
        self.target = target
        self.contact = True
        maxtargetmass = target.movemass + target.owner.movemass
        movemass = random.triangular(low=target.movemass, high=maxtargetmass, mode=target.movemass)
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        torque = 8 * self.strength * self.I ** 0.5
        swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])
        self.w = ((2 * torque * swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(
            mode=(self.attacker.stats['tec'] + 0.5 * self.attacker.stats['luc']) / (
                target.stats['luc'] + 0.5 * target.stats['tec']))
        self.pushforce = torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.0001, 1, mode=target.radius)
        self.energy = 0.5 * self.I * self.w ** 2
        self.force = self.speed * (1000000000 * self.reducedmass * self.area / (
            self.weapon.thickness / self.weapon.material.youngs + target.thickness / target.youngs)) ** 0.5 + self.pushforce
        self.pressure = self.force / self.area
        f = self.force
        #print(self.pushforce, self.force, self.pressure, self.speed)
        self.weapon.stats = self.limb.stats
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*(self.attacker.focus[0]+1))
        self.time = broadcast_time+self.I * self.w / torque
        self.attacker.stamina[0] -= int(max(1, 5 * (self.arm.movemass + self.I) / self.attacker.stats['str']))
        #print(self.time)

        self.resolve()



    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        target = self.target
        new = self.speed * (1000000000 * self.reducedmass * self.area / (
            self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.basetarget.youngs)) ** 0.5 + self.pushforce
        self.force = min(new, 0.9 * self.force)


class Bludgeon_1H(Attack):
    def __init__(self, weapon, limb):
        self.type = 'crush'
        self.weapon = weapon
        self.arpen = -0.1
        self.limb = limb
        self.accuracy=self.limb.dexterity
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        if self.arm.attachpoint:
            self.anchor = self.arm.attachpoint
            self.basestrength = 0.2 * self.limb.stats['str'] * self.limb.ability + 0.7 * self.arm.stats[
                'str'] * self.arm.ability + 0.1 * self.anchor.stats['str'] * self.anchor.ability
            armlength = self.arm.length
        else:
            self.anchor = None
            self.basestrength = 0.5 * self.limb['str'] * self.limb.ability + 0.5 * self.arm['str'] * self.arm.ability
            armlength = self.limb.length
        self.strikelength = weapon.length + armlength
        self.strikearea = weapon.contactarea
        self.strikemass = self.arm.movemass + weapon.mass + self.attacker.mass
        self.I = weapon.I + (1 / 3) * self.arm.mass * armlength ** 2 + weapon.mass * self.arm.length ** 2
        if self.attacker.player == True:
            self.name = 'a swing of your {}'.format(weapon.name)
        else:
            self.name = 'a swing of its {}'.format(weapon.name)

    def do(self, target):
        self.__init__(self.weapon, self.limb)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01
        self.basetarget = target
        self.target = target
        self.contact = True
        maxtargetmass = target.movemass + target.owner.mass / 2
        movemass = random.triangular(low=target.movemass, high=maxtargetmass, mode=target.movemass)
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        torque = 8 * self.strength * self.I ** 0.5
        swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / target.stats['luc'])
        self.w = ((2 * torque * swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(mode=1) * (
            self.attacker.stats['tec'] + 0.5 * self.attacker.stats['luc']) / (
                                                  target.stats['luc'] + 0.5 * target.stats['tec'])
        self.pushforce = torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.0001, 1, mode=target.radius)
        self.energy = 0.5 * self.I * self.w ** 2
        self.force = self.speed * (1000000000 * self.reducedmass * self.area / (
            2 * self.weapon.head / self.weapon.material.youngs + target.thickness / target.youngs)) ** 0.5 + self.pushforce
        self.pressure = self.force / self.area
        f = self.force
        print(self.pushforce, self.force, self.pressure, self.speed)
        self.weapon.stats = self.limb.stats
        broadcast_time=4*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + self.I * self.w / torque
        print(self.time)
        self.attacker.stamina[0] -= int(max(1, 5 * (self.arm.movemass + self.I) / self.attacker.stats['str']))

        self.resolve()

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            return
        self.w = (2 * self.energy / self.I) ** 0.5
        self.speed = self.w * self.collidepoint
        target = self.target
        new = self.speed * (1000000000 * self.reducedmass * self.area / (
            self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.basetarget.youngs)) ** 0.5 + self.pushforce
        self.force = min(new, 0.9 * self.force)


# A person can swing with two hands an object with a moment of inertia of 0.1646 kg m^2 with a top radial speed
#of about 30 rad/sec. It seems that I*w^4 is approximately constant, though there is clearly more work that needs done.



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


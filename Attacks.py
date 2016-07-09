__author__ = 'Alan'
import random
#from BaseClasses import *
#from UI_Elements import *
import UI_Elements
import Shell
#import Enchantments






def hostilitycheck(attacker,defender):
    if attacker.hostilitycheck(defender):
        return True
    if defender.hostilitycheck(attacker):
        return True
    else:
        return False
    #Old
    for i in attacker.classification:
        if i in defender.hostile:
            return True
    for i in defender.classification:
        if i in attacker.hostile:
            return True
    return False


class Attack():
    def __init__(self):
        if not hasattr(self,'disabled'):
            self.disabled=False
        self.killingblow=False
        self.hands=1
        self.useless=False
        self.blocked=False
        self.blockable=1
        self.dodged=False
        self.dodgeable=1
        self.parried=False
        self.parryable=1
        self.penetrate=False
        self.weapon=None
        self.classification=['melee','physical','chargeable']
        self.absolute_depth_limit=1
        self.cutlimit=1
        self.piercelimit=1
        self.results=[]
        self.touchedobjects=[]
        self.damagedobjects=[]

    def resolve(self):
        import Enchantments
        f=self.force
        #print(self.name,'Force of',f,'time of',self.time,'pressure of',self.pressure)
        #print(self.recoverytime)
        #print(self.area)

        self.attacker.focus[0] -= 1
        self.damage_dealt = 0
        self.initialforce=0
        try: alive=self.basetarget.owner.alive
        except: alive=False


        if self.dodged==True:
            if self.basetarget.owner in Shell.shell.player.visible_creatures: Shell.messages.append("The attack was avoided!")
            self.unstatweapon()
            self.attacker.recoverytime=self.recoverytime*(1-(50-self.attacker.tension)/100)
            return
        if self.parried==True:
            if self.basetarget.owner in Shell.shell.player.visible_creatures: Shell.messages.append("The attack was parried with the {}".format(self.target.name))
            self.target.damageresolve(self,self.limb)
            self.target.on_struck(self)
            self.attacker.on_strike(self)
            self.target.functioncheck()
            self.unstatweapon()
            self.attacker.recoverytime=(1+(self.basetarget.owner.tension-self.attacker.tension)/50)*self.recoverytime

            return
        if self.blocked==True:
            if self.basetarget.owner in Shell.shell.player.visible_creatures: Shell.messages.append("The attack was blocked with the {}".format(self.target.name))
            self.target.damageresolve(self,self.limb)
            self.target.on_struck(self)
            self.attacker.on_strike(self)
            self.target.functioncheck()
            self.unstatweapon()
            self.attacker.recoverytime=(1+random.random()*self.attacker.tension/100)*self.recoverytime

            return

        #self.target.on_struck(self)
        self.initialforce=self.force

        self.target.damageresolve(self, self.limb)

        try:
            self.basetarget.owner.survivalcheck()
            if self.basetarget.owner.alive==False and alive==True:
                self.killingblow=True
        except: pass

        limb_processed=False
        for i in self.touchedobjects:
            i.on_struck(self)
            try:
                if i in self.basetarget.layers and limb_processed==False:
                    self.basetarget.on_struck(self)
                    limb_processed=True
            except:
                self.target.on_struck(self)


        self.attacker.on_strike(self)

        try: self.weapon.on_strike(self)
        except AttributeError:
            try: self.limb.on_strike(self)
            except AttributeError: pass

        if self.damage_dealt <= 0 and self.parried==False:
            if self.basetarget.owner in Shell.shell.player.visible_creatures: Shell.messages.append("The attack glances off harmlessly")
            self.attacker.recoverytime=random.random()*self.recoverytime
        try: self.basetarget.owner.combataction = True
        except: pass

        for i in self.damagedobjects:
            crush=i.damage['crush']-i.olddamage['crush']
            cut=i.damage['cut']-i.olddamage['cut']
            pierce=i.damage['pierce']-i.olddamage['pierce']
            broken=i.damage['break']-i.olddamage['break']
            shatter=i.damage['shatter']-i.olddamage['shatter']
            if crush>0:
                Enchantments.Bleeding(i,strength=5)
            if cut>0:
                Enchantments.Bleeding(i,strength=cut*3)
            if pierce>0:
                Enchantments.Bleeding(i,strength=pierce*5)
            if broken>0:
                Enchantments.Bleeding(i,strength=broken)
            if shatter>0:
                Enchantments.Bleeding(i,strength=shatter)



        self.penetrate=False
        self.arpen = -15
        self.force = f / (10*self.damagefactor)
        self.pressure = f / self.strikearea
        self.reaction_damage_processed = False
        self.oldtype=self.type
        self.type='crush'
        if hasattr(self,'weapon') and self.weapon and self.weapon!=self.limb:
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
            '''
            if any(limb.ability<=0 for limb in self.limbs):
                self.useless=True
                return
            '''
#            for i in self.limbs:
#                if i.attachpoint!=None:
#                    if i.attachpoint.ability<=0:
#                        self.useless=True
#                        return

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
            elif hasattr(self.target,'layers') and self.target.layers!=[]:
                density=self.target.layers[len(self.target.layers)-1].density
            else:
                density=5000
        return (thickness,density)

    def average_values(self):
        information={'Attack Name':'','Damage Type':'','Strike Length':0,'Execution Time':0,'Average Force':0,'Average Pressure':0}
        return information

    def pre_evasion(self,**kwargs):
        if 'accuracy' in kwargs:
            self.accuracy=self.accuracy*kwargs['accuracy']
        if 'parryable' in kwargs:
            self.parryable=kwargs['parryable']
        if 'blockable' in kwargs:
            self.blockable=kwargs['blockable']
        if 'dodgeable' in kwargs:
            self.dodgeable=kwargs['dodgeable']
        if 'timefactor' in kwargs:
            self.time*=kwargs['timefactor']
        if 'damagefactor' in kwargs:
            self.damagefactor*=kwargs['damagefactor']
        if 'energyfactor' in kwargs:
            self.energy*=kwargs['energyfactor']
        if 'energyplus' in kwargs:
            self.energy+=kwargs['energyplus']
        if 'call_before_evasion' in kwargs:
            kwargs['call_before_evasion'](self)
        try:
            for i in self.weapon.enchantments:
                i.attack_modification(self)
        except:
            try:
                for i in self.limb.enchantments:
                    i.attack_modification(self)
            except: pass


class Punch(Attack):
    def __init__(self, limb=None,weapon=None):
        super().__init__()
        self.classification.append('weaponless')
        self.sig=(Punch,limb)
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

        self.area=max(self.area,0.0001)
        self.strikearea=self.area

    def do(self, target,**kwargs):
        self.__init__(self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        self.basetarget = target
        self.target = target
        self.contact = True
        highspeed = max(4 * (max(self.strikelength*self.strength / self.arm.movemass,0)) ** 0.5, 8)
        self.speed = random.triangular(low=1, high=highspeed, mode=3.5) * (
            max(self.attacker.stamina[0] / self.attacker.stamina[1],0) ** 0.5) + 0.1
        broadcast_time=2*random.gauss(1,0.2)*self.attacker.focus[1]/max((self.attacker.stats['tec']*(self.attacker.focus[0])),1)
        self.time = broadcast_time+self.strikelength / self.speed
        self.strikemass = random.triangular(low=self.limb.movemass, high=self.strikemass, mode=self.strikemass*self.limb.stats['tec']/(12+self.limb.stats['tec']))
        self.energy = 0.5 * self.strikemass * self.speed ** 2

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

        movemass = abs(random.gauss(self.target.movemass, 5))*(self.limb.stats['tec']+15)/15
        thickness,density=self.armor_penetration()

        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        self.pushforce = 7 * self.strength * self.reducedmass ** 0.5
        self.force = self.damagefactor*0.5* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.limb.thickness / self.limb.youngs + thickness / self.youngs)**0.25) + self.pushforce)+1
        self.pressure = self.force / self.area


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
        target=self.target
        try:
            self.force = self.damagefactor*0.5* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(target)-1].density**0.25)*(
                self.limb.thickness / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1
        except:
            self.force = self.damagefactor*0.5* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[len(self.basetarget.layers)-1].density**0.25)*(
                self.limb.thickness / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1

    def average_values(self):
        information={'Attack Name':'Punch ({})'.format(self.limb.name),'Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=2/self.attacker.stats['tec']
        speed=3.5
        swingtime=self.strikelength/speed
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        strikemass= self.strikemass*self.limb.stats['tec']/(12+self.limb.stats['tec'])
        pushforce= 7 * self.strength * strikemass ** 0.5

        avgforce=0.5 * (speed * (10**3) * (strikemass**0.75) / ((5000**0.25)*(
            self.limb.thickness / self.limb.youngs + 1)**0.25) + pushforce)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.area)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 7 * self.arm.movemass / self.basestrength))
        return information

    def test_usability(self,hands):
        if self.limb.ability<=0:
            self.useless=True
            return
        if self.arm.ability<=0:
            self.useless=True
            return
        else:
            self.useless=False

class Kick(Attack):
    def __init__(self, limb=None,weapon=None):
        super().__init__()
        self.classification.append('weaponless')
        self.damagefactor=1
        self.weapon = None
        self.type = 'crush'
        self.oldtype = 'crush'
        self.limb = limb
        self.sig=(Kick,self.limb)
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
            self.strikemass = limb.movemass + limb.owner.mass * limb.stats['tec']/(15+limb.stats['tec'])
            self.strength = self.basestrength * (max(self.attacker.stamina[0] / self.attacker.stamina[1],0) ** 0.5)
        else:
            self.leg=self.limb
            self.strikelength=limb.length
            self.strikearea=limb.length*limb.radius*2
            self.strikemass = limb.movemass
            self.basestrength=0.5*self.limb.stats['str']
            self.strength = self.basestrength * (max(self.attacker.stamina[0] / self.attacker.stamina[1],0) ** 0.5)
        self.I=0.25*self.leg.movemass*self.leg.length**2+limb.movemass*self.leg.length**2

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        self.basetarget = target
        self.target = target
        self.contact = True
        if hasattr(target,'stats'):
            luc=target.stats['luc']
        else:
            luc=10

        torque =  5 * self.strength * self.I ** 0.5 + 0.001
        swingangle = random.triangular(low=0.5, high=3, mode=2 * self.attacker.stats['tec'] / luc)*anglefactor
        self.w = ((2 * torque * swingangle / self.I) ** 0.5)
        self.collidepoint = self.leg.length + self.limb.length / 2
        self.speed = self.w * self.collidepoint
        self.area = max(self.strikearea * random.triangular(0.001, 1),0.0001)
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=8*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        #print('broadcast time of',broadcast_time,'top w of',self.w,'I of',self.I,'with applied torque of',torque)
        self.time = broadcast_time+(self.I**1.25) * self.w / torque

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

        movemass = abs(random.gauss(self.target.movemass, 5))
        thickness,density=self.armor_penetration()
        self.strikemass = random.triangular(low=self.limb.movemass, high=self.strikemass, mode=self.strikemass)
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        self.pushforce = 7 * self.strength * self.reducedmass ** 0.5
        #self.force = self.damagefactor*((self.limb.ability ** 0.2) * 1.1 * 0.016 * self.speed * (1000000000 * self.reducedmass / (
         #   self.limb.thickness / self.limb.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce + 1)
        self.force = self.damagefactor*0.25* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.limb.thickness / self.limb.youngs + thickness / self.youngs)**0.25) + self.pushforce)
        self.pressure = self.force / max(self.strikearea,0.0000000001)
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
        target=self.target
        try:
            new = self.damagefactor*0.25* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(target)-1].density**0.25)*(
                self.limb.thickness / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        except:
            new = self.damagefactor*0.25* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
                self.limb.thickness / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

    def test_usability(self,hands=1):
        if self.leg.ability>0 and self.limb.ability>0:
            self.useless=False
        else:
            self.useless=True

    def average_values(self):
        information={'Attack Name':'Kick ({})'.format(self.limb.name),'Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=8/self.attacker.stats['tec']
        torque =  5 * self.strength * self.I ** 0.5 + 0.001
        swingangle=2 * self.attacker.stats['tec'] / 12
        w=((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=(self.I**1.25) * w / torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        collidepoint = self.leg.length + self.limb.length / 2
        strikemass=self.strikemass
        speed=w*collidepoint
        pushforce= 7 * self.strength * self.strikemass ** 0.5

        avgforce=0.25 * (speed * (10**3) * (strikemass**0.75) / ((5000**0.25)*(
            self.limb.thickness / self.limb.youngs + 1)**0.25) + pushforce)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 7 * self.leg.movemass / self.basestrength))

        return information

class Slash_1H(Attack):
    def __init__(self, weapon=None, limb=None):
        super().__init__()
        self.damagefactor=1
        self.type = 'cut'
        self.oldtype = 'cut'
        self.weapon = weapon
        self.sig=(Slash_1H,self.weapon)
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
        self.I+=0.2*self.arm.I

        if self.attacker.player == True:
            self.name = 'a slash with your {}'.format(weapon.name)
        else:
            self.name = 'a slash with its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.weapon, self.limb)
        try:
            defender_reach=self.target.owner.reach
        except:
            defender_reach=0.01
        if hasattr(target,'stats'):
            luc=target.stats['luc']
            tec=target.stats['tec']
        else:
            luc=10
            tec=10
        self.basetarget = target
        self.target = target
        self.contact = True
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / luc)*anglefactor
        self.w = ((2 * torque * swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(
            mode=(self.attacker.stats['tec'] + 0.5 * self.attacker.stats['luc']) / (
                luc + 0.5 * tec))
        self.pushforce = torque #/ self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.05, 0.5, mode=0.5/self.attacker.stats['tec']**0.5)
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+1.5*(self.I) * self.w / torque

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

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
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        try:
            new = self.damagefactor* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(target)-1].density**0.25)*(
                self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        except:
            new = self.damagefactor* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
                self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'1H Slash','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / 12
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=1.5*self.I*w/torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        avgforce = 0.5* (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            (self.weapon.thickness / self.weapon.material.youngs) + 1)**0.25) + torque)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea*0.5/self.attacker.stats['tec']**0.5)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 5 * (self.arm.movemass + self.I) / self.basestrength))

        return information

class Stab_1H(Attack):
    def __init__(self, weapon=None, limb=None):
        super().__init__()
        self.damagefactor=1
        self.type = 'pierce'
        self.oldtype = 'pierce'
        self.absolute_depth_limit=weapon.length
        self.weapon = weapon
        self.sig=(Stab_1H,self.weapon)
        self.arpen = 0.1
        self.limb = limb
        self.accuracy=self.limb.dexterity
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        if hasattr(weapon,'tip'):
            self.strikearea = weapon.tip+0.0000000001
        else:
            self.strikearea = 3.14*weapon.radius**2+0.0000000001
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

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.weapon, self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        self.basetarget = target
        self.target = target
        self.contact = True

        self.pushforce=6*self.strength*self.strikemass**0.5

        self.speed = (random.triangular(0.01,0.8,0.1)*self.strikelength*self.pushforce/self.strikemass)**0.5
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+0.75*(self.speed*self.strikemass**1.25)/self.pushforce


        self.area = self.strikearea
        self.energy = 0.5 * self.strikemass * self.speed ** 2

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass, 1))*(self.limb.stats['tec']+15)/15+0.1
        self.strikemass = random.triangular(low=self.limb.movemass, high=self.strikemass, mode=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec']))
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        thickness,density=self.armor_penetration()
        #self.force = self.damagefactor* (self.speed * (1000000000 * self.reducedmass * (self.area**0.5) / (
        #    self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        self.force = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.length / self.weapon.youngs + thickness / self.youngs)**0.25) + self.pushforce)+1


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
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        try:
            new = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(target)-1].density**0.25)*(
                self.limb.length / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1
        except:
            new = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
                self.limb.length / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'1H Stab','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        pushforce=6*self.strength*self.strikemass**0.5
        speed=0.274*(self.strikelength*pushforce/self.strikemass)**0.5
        swingtime=0.5*(speed*self.strikemass**1.25)/pushforce
        striketime=1.5*swingtime+broadcast_time
        information['Execution Time']=striketime

        strikemass=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec'])

        avgforce=0.2 * (speed * (10**3) * (strikemass**0.75) / ((5000**0.25)*(
            self.weapon.length / self.weapon.youngs + 1)**0.25) + pushforce)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 5 * (self.arm.movemass + self.weapon.mass) / self.basestrength))

        return information

class Bludgeon_1H(Attack):
    def __init__(self, weapon=None, limb=None):
        super().__init__()
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.sig=(Bludgeon_1H,self.weapon)
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

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.weapon, self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        if hasattr(target,'stats'):
            luc=target.stats['luc']
            tec=target.stats['tec']
        else:
            luc=10
            tec=10
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / luc)*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))+0.0000000001
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + 1.5*(self.I) * self.w / torque

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

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
        try:
            new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(self.target)-1].density**0.25)*(
                self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        except:
            new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
                self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'1H Strike','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / 12
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=1.5*self.I*w/torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        avgforce = (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + 1)**0.25) + 3*torque/(self.arm.length+self.weapon.length))

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea/self.attacker.stats['tec']**0.5)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        return information

class Bite(Attack):
    def __init__(self, weapon=None,limb=None):
        super().__init__()
        self.classification.append('weaponless')
        self.classification.remove('chargeable')
        self.damagefactor=1
        self.weapon = None
        self.type = 'pierce'
        self.oldtype = 'pierce'
        self.limb = limb
        self.sig=(Bite,self.limb)
        self.absolute_depth_limit=limb.radius*4
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
        #print(limb.limbs)
        if any(hasattr(i,'is_teeth') for i in self.limb.limbs):
            self.teeth=[i for i in limb.limbs if hasattr(i,'is_teeth')]
            self.teeth=random.choice(self.teeth)
            self.weapon=self.teeth
            self.strikearea=(self.teeth.biting_surface)
        else:
            self.teeth=self.limb
            self.useless=True
            self.strikearea=1
        self.bitesize=max(self.limb.radius,self.limb.length)
        self.basestrength=self.limb.stats['str'] * self.bitesize + self.limb.stats['str'] * self.teeth.radius
        self.strength=self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.2) + 0.01

    def do(self, target,**kwargs):
        self.__init__(limb=self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        self.basetarget = target
        self.target = target
        self.contact = True

        broadcast_time=4*random.gauss(1,0.2)*self.attacker.focus[1]/max((self.attacker.stats['tec']*self.attacker.focus[0]),0.01)
        self.time = broadcast_time+self.head.movemass / self.head.stats['str']
        self.strikearea=(self.teeth.biting_surface)
        self.area=self.strikearea

        self.parryable=0
        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

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
        self.pressure = self.force / (self.teeth.biting_surface)
        self.energy = self.force*self.limb.length

    def test_usability(self,hands=1):
        if any(hasattr(i,'is_teeth') for i in self.limb.limbs):
            self.teeth=[i for i in self.limb.limbs if hasattr(i,'is_teeth')]
            self.teeth=random.choice(self.teeth)
            self.weapon=self.teeth
            self.stattedweapon=True
            if self.limb.ability>0:
                self.useless=False
        else:
            self.useless=True
            #print('no teeth')
            return
            #self.limb.attacks.remove(self)

    def average_values(self):
        information={'Attack Name':'Bite ({})'.format(self.limb.name),'Damage Type':'pierce/cut','Strike Length':self.strikelength}
        broadcast_time=4/self.attacker.stats['tec']
        swingtime= self.head.movemass / self.head.stats['str']
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime


        avgforce=self.strength*250

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea)
        print(self.strikearea)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 7 * self.head.movemass / self.head.stats['str']))

        return information

class Swing_Pierce_1H(Bludgeon_1H):
    def __init__(self,weapon=None,limb=None):
        super().__init__(weapon,limb)
        self.type='pierce'
        self.oldtype='pierce'
        self.arpen=0
        self.absolute_depth_limit=0.1
        self.strikearea=weapon.tip
        self.area=self.strikearea
        self.sig=(Swing_Pierce_1H,self.weapon)

    def do(self,target,anglefactor=1,**kwargs):
        super().do(target,anglefactor,**kwargs)

    def average_values(self):
        information={'Attack Name':'Spike Pierce','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / 12
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=self.I*w/torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        avgforce = (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + 1)**0.25) + 3*torque/(self.arm.length+self.weapon.length))

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea/self.attacker.stats['tec']**0.5)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        return information

class Shield_Bash(Bludgeon_1H):
    def __init__(self,weapon=None,limb=None):
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
        self.sig=(Shield_Bash,self.weapon)

    def do(self, target,**kwargs):
        super().do(target,anglefactor=min(0.1/self.weapon.mass,1),**kwargs)
        try:
            if self.blocked==False and self.parried==False and self.dodged==False:
                creature=self.basetarget.owner
                if 2*self.strikemass*random.random()*self.attacker.stats['per']**0.5>(creature.mass**0.5)*random.random()*creature.stats['per']*creature.balance*creature.focus[0]/creature.focus[1]:
                    if "off_balance" not in creature.conditions:
                        creature.conditions.append("off_balance")
                        if creature in Shell.shell.player.visible_creatures: Shell.messages.append("{} is knocked off balance!".format(creature.name))
        except: pass

    def average_values(self):
        information={'Attack Name':'Shield Bash','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / (12*max(self.weapon.mass,1))
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=self.I*w/torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        avgforce = (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + 1)**0.25) + 3*torque/(self.arm.length+self.weapon.length))

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea/self.attacker.stats['tec']**0.5)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        return information

class Strike_1H(Attack):
    def __init__(self, weapon=None, limb=None):
        super().__init__()
        if limb==None:
            limb=weapon
            self.classification.append('weaponless')
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.sig=(Strike_1H,self.weapon)
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
        self.I+=0.2*self.arm.I

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

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.weapon, self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        if hasattr(target,'stats'):
            luc=target.stats['luc']
            tec=target.stats['tec']
        else:
            luc=10
            tec=10
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / luc)*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + 2*(self.I) * self.w / torque

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

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
        try:
            new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(self.target)-1].density**0.25)*(
                self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        except:
            new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
                self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'1H Strike','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / 12
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=self.I*w/torque
        striketime=2*swingtime+broadcast_time
        information['Execution Time']=striketime

        avgforce = (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            self.weapon.thickness / self.weapon.youngs + 1)**0.25) + 3*torque/(self.arm.length+self.weapon.length))

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea/self.attacker.stats['tec']**0.5)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        return information

class Scratch(Attack):
    def __init__(self, weapon=None, limb=None):
        super().__init__()
        self.classification.append('weaponless')
        if limb==None:
            limb=weapon
        self.damagefactor=1
        self.type = 'cut'
        self.oldtype = 'cut'
        self.weapon = weapon
        self.arpen = 0
        self.limb = limb
        self.sig=(Scratch,self.limb)
        self.absolute_depth_limit=self.weapon.length
        self.accuracy=self.limb.ability*5
        self.attacker = limb.owner
        self.arm = limb.attachpoint
        self.strikearea = weapon.tip
        self.area=self.strikearea
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

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.weapon, self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        if hasattr(target,'stats'):
            luc=target.stats['luc']
        else:
            luc=10
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / luc)*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + (self.I) * self.w / torque

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

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

        #print(self.time,self.recoverytime,self.w)

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
        try:
            new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(self.target)-1].density**0.25)*(
                self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        except:
            new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
                self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'Scratch ({})'.format(self.limb.name),'Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque = 7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / 12
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        collidepoint = self.arm.length + self.weapon.length
        speed = w * collidepoint
        swingtime=(self.I) * w / torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        pushforce= 3 * torque/collidepoint

        avgforce= (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            self.weapon.thickness / self.weapon.youngs + 1)**0.25) + pushforce)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.area)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        return information

class Touch(Attack):
    def __init__(self, weapon=None, limb=None):
        super().__init__()
        self.damage_dealt=0
        self.classification.append('weaponless')
        self.classification.remove('chargeable')
        if limb==None:
            limb=weapon
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.sig=(Touch,self.weapon)
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
        self.area=self.strikearea

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.weapon, self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        if hasattr(target,'stats'):
            luc=target.stats['luc']
        else:
            luc=10
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / luc)*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.arm.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + (self.I) * self.w / torque

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        #self.force=1
        #self.pressure=1

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
        self.basetarget.owner.combataction = True
        self.attacker.focus[0] -= 1
        #if hasattr(self.weapon,'layers'):
            #oldweapon=self.weapon
            #self.weapon=self.weapon.layers[len(self.weapon.layers)-1]
        if self.dodged==True:
            Shell.messages.append("The attack was avoided!")
            self.unstatweapon()
            self.attacker.recoverytime=self.recoverytime
            #self.weapon=oldweapon
            return
        if self.parried==True:
            Shell.messages.append("The attack was parried with the {}".format(self.target.name))
            for i in self.weapon.coatings:
                i.add(self.target)
            self.target.functioncheck()
            self.unstatweapon()
            self.attacker.recoverytime=(1+random.random())*self.recoverytime
            #self.weapon=oldweapon
            return
        if self.blocked==True:
            Shell.messages.append("The attack was blocked with the {}".format(self.target.name))
            for i in self.weapon.coatings:
                i.add(self.target)
            self.target.functioncheck()
            self.unstatweapon()
            self.attacker.recoverytime=(1+random.random())*self.recoverytime
            #self.weapon=oldweapon
            return

        for i in self.weapon.coatings:
            i.add(self.target)

        self.target.on_struck(self)
        self.limb.on_strike(self)
        #self.weapon=oldweapon

    def test_usability(self,hands):
        if self.limb.ability<=0:
            self.useless=True
        else:
            self.useless=False

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
        new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'Touch ({})'.format(self.limb.name),'Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque = 7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / 12
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        collidepoint = self.arm.length + self.weapon.length
        speed = w * collidepoint
        swingtime=(self.I) * w / torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        pushforce= 3 * torque/collidepoint

        avgforce= self.strength

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.area)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 4 * (self.arm.movemass + self.I) / self.basestrength))

        return information

class Blunt_Thrust_1H(Stab_1H):
    def __init__(self,weapon=None,limb=None):
        super().__init__(weapon,limb)
        self.type='crush'
        self.oldtype='crush'
        if self.attacker.player == True:
            self.name = 'a thrust with your {}'.format(weapon.name)
        else:
            self.name = 'a thrust with its {}'.format(weapon.name)
        self.sig=(Blunt_Thrust_1H,self.weapon)

    def average_values(self):
        information={'Attack Name':'1H Thrust','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        pushforce=6*self.strength*self.strikemass**0.5
        speed=0.1*(self.strikelength*pushforce/self.strikemass)**0.5
        swingtime=0.5*(speed*self.strikemass**1.25)/pushforce
        striketime=1.5*swingtime+broadcast_time
        information['Execution Time']=striketime

        strikemass=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec'])

        avgforce=0.5 * (speed * (10**3) * (strikemass**0.75) / ((5000**0.25)*(
            self.weapon.length / self.weapon.youngs + 1)**0.25) + pushforce)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 5 * (self.arm.movemass + self.weapon.mass) / self.basestrength))

        return information

class Pinch(Attack):
    def __init__(self, limb=None,weapon=None):
        super().__init__()
        self.classification.append('weaponless')
        self.sig=(Pinch,limb)
        self.damagefactor=1
        self.weapon = None
        self.type = random.choice(['cut','pierce'])
        self.oldtype = self.type
        self.limbs=[]
        self.limb=limb
        if limb.attachpoint==None:
            self.useless=True
            return
        else:
            for i in limb.attachpoint.limbs:
                if 'pinching' in i.target_class:
                    self.limbs.append(i)
        if len(self.limbs)<2:
            self.useless=True
            return
        self.accuracy=2*len(self.limbs)
        while len(self.limbs)>2:
            self.limbs.remove(random.choice(self.limbs))
        self.attacker = limb.owner
        if type(self.limbs[0])==type(self.limbs[1]):
            if self.attacker.player == True:
                self.name = 'a pinch with your {}s'.format(limb.target_class[1])
            else:
                self.name = 'a pinch with its {}s'.format(limb.target_class[1])
        else:
            if self.attacker.player == True:
                self.name = 'a pinch with your {} and {}'.format(self.limbs[0].name,self.limbs[1].name)
            else:
                self.name = 'a pinch with its {} and {}'.format(self.limbs[0].name,self.limbs[1].name)
        self.arpen = 0
        self.head=self.limb.attachpoint

        s1=self.limbs[0].stats['str']*self.limbs[0].ability
        s2=self.limbs[1].stats['str']*self.limbs[1].ability
        self.basestrength=(s1*s1+s2*s2)**0.5
        self.strikelength=min(self.limbs[0].length,self.limbs[1].length)
        if self.type=='cut':
            self.strikearea=self.limbs[0].edge*self.limbs[0].length+self.limbs[1].edge*self.limbs[1].length
        elif self.type=='pierce':
            self.strikearea=self.limbs[0].tip+self.limbs[1].tip
        self.strength = self.basestrength * (max(self.attacker.stamina[0] / self.attacker.stamina[1],0) ** 0.5)
        self.strikemass=self.limbs[0].mass+self.limbs[1].mass
        self.area=self.strikearea
        self.absolute_depth_limit=self.strikelength

    def do(self, target,**kwargs):
        self.__init__(self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        self.basetarget = target
        self.target = target
        self.contact = True
        broadcast_time=4*random.gauss(1,0.2)*self.attacker.focus[1]/max((self.attacker.stats['tec']*self.attacker.focus[0]),0.01)

        self.time = broadcast_time+10*(self.limbs[0].I+self.limbs[1].I) / self.strength
        self.parryable=0
        maxlength=min(self.limbs[0].length,self.limbs[1].length)
        musclelength=0.1*maxlength
        if self.target.thickness>2*maxlength:
            self.type='pierce'
            self.area=self.limbs[0].tip+self.limbs[1].tip
            self.strikearea=self.area
        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

        if self.type=='pierce':
            contactlength=maxlength
        elif self.type=='cut':
            contactlength=maxlength*random.random()
            self.area=self.limbs[0].edge*min(self.limbs[0].length,self.target.thickness)+self.limbs[1].edge*min(self.limbs[1].length,self.target.thickness)
            self.strikearea=self.area
        self.reducedmass=1000

        self.force = self.damagefactor*self.strength*250*musclelength/contactlength
        self.pressure = self.force / self.area
        self.energy = self.force*self.target.thickness

        self.attacker.stamina[0] -= int(max(1, 7 * self.head.movemass / self.basestrength))

        self.recoverytime=self.head.movemass/self.head.stats['str']
        self.recoverytime=self.recoverytime*defender_reach/self.strikelength

        self.resolve()

    def energy_recalc(self):
        if self.energy<0:
            self.energy=0
        pass

    def test_usability(self,hands=1):
        pincers=0
        for i in self.limbs:
            if 'pinching' in i.target_class and i.ability>0:
                pincers+=1
        if pincers>=2:
            self.useless=False
            return
        else:
            self.useless=True
            return

    def average_values(self):
        information={'Attack Name':'Pinch ({})'.format(self.limb.name),'Damage Type':'pierce/cut','Strike Length':self.strikelength}
        broadcast_time=4/self.attacker.stats['tec']
        swingtime= 10*(self.limbs[0].I+self.limbs[1].I) / self.strength
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime


        avgforce=self.strength*50

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.limbs[0].tip+self.limbs[1].tip)
        #print(self.strikearea)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 7 * self.head.movemass / self.head.stats['str']))

        return information

class Sting(Attack):
    def __init__(self, limb=None,weapon=None):
        super().__init__()
        self.damagefactor=1
        self.type = 'pierce'
        self.oldtype = 'pierce'
        self.absolute_depth_limit=limb.length
        self.sig=(Sting,limb)
        self.arpen = 0.1
        self.limb = limb
        self.accuracy=3
        self.attacker = limb.owner
        self.body = limb.attachpoint
        self.strikearea = limb.tip
        if self.attacker.player == True:
            self.name = 'a sting with your {}'.format(limb.name)
        else:
            self.name = 'a sting with its {}'.format(limb.name)
        if self.body==None:
            self.useless=True
            self.strikelength=0
            return

        self.basestrength=self.body.stats['str']*self.body.ability
        self.strikelength=self.limb.length
        self.strikemass=self.attacker.movemass


        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.limb,None)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        self.basetarget = target
        self.target = target
        self.contact = True

        self.pushforce=6*self.strength*self.strikemass**0.5

        self.speed = (random.triangular(0.01,0.8,0.1)*self.strikelength*self.pushforce/self.strikemass)**0.5
        broadcast_time=5*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+0.75*(self.speed*self.strikemass**1.25)/self.pushforce


        self.area = self.strikearea
        self.energy = 0.5 * self.strikemass * self.speed ** 2

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass, 1))*(self.limb.stats['tec']+15)/15+0.1
        self.strikemass = random.triangular(low=self.limb.movemass, high=self.strikemass, mode=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec']))
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        thickness,density=self.armor_penetration()
        #self.force = self.damagefactor* (self.speed * (1000000000 * self.reducedmass * (self.area**0.5) / (
        #    self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        self.force = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.limb.length / self.limb.youngs + thickness / self.youngs)**0.25) + self.pushforce)+1


        self.pressure = self.force / self.area
        f = self.force
        self.attacker.stamina[0] -= int(max(1, 5 * (self.body.movemass + self.limb.mass) / self.basestrength))

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
        try:
            new = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(target)-1].density**0.25)*(
                self.limb.length / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1
        except:
            new = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[len(self.basetarget.layers)-1].density**0.25)*(
                self.limb.length / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'Sting','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=5/self.attacker.stats['tec']
        pushforce=6*self.strength*self.strikemass**0.5
        speed=0.274*(self.strikelength*pushforce/self.strikemass)**0.5
        swingtime=0.5*(speed*self.strikemass**1.25)/pushforce
        striketime=1.5*swingtime+broadcast_time
        information['Execution Time']=striketime

        strikemass=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec'])

        avgforce=0.2 * (speed * (10**3) * (strikemass**0.75) / ((5000**0.25)*(
            self.limb.length / self.limb.youngs + 1)**0.25) + pushforce)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 5 * (self.body.movemass + self.limb.mass) / max(self.basestrength,1)))

        return information

    def test_usability(self,hands):
        if self.limb.ability<=0:
            self.useless=True
        elif self.limb.attachpoint==None:
            self.useless=True
        elif self.limb.attachpoint.ability<=0:
            self.useless=True
        else:
            self.useless=False

class Spider_Bite(Attack):
    def __init__(self, limb=None,weapon=None):
        super().__init__()
        self.damagefactor=1
        self.type = 'pierce'
        self.oldtype = 'pierce'
        self.absolute_depth_limit=limb.length
        self.sig=(Sting,limb)
        self.arpen = 0.1
        self.limb = limb
        self.accuracy=3
        self.attacker = limb.owner
        self.body = limb.attachpoint
        self.strikearea = limb.tip
        if self.attacker.player == True:
            self.name = 'a bite with your {}'.format(limb.name)
        else:
            self.name = 'a bite with its {}'.format(limb.name)
        if self.body==None:
            self.useless=True
            self.strikelength=0
            return

        self.basestrength=self.limb.stats['str']*self.limb.ability
        self.strikelength=self.limb.length
        self.strikemass=self.attacker.movemass


        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.limb,None)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        self.basetarget = target
        self.target = target
        self.contact = True

        self.pushforce=6*self.strength*self.strikemass**0.5

        self.speed = (random.triangular(0.01,0.8,0.1)*self.strikelength*self.pushforce/self.strikemass)**0.5
        broadcast_time=5*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+0.75*(self.speed*self.strikemass**1.25)/self.pushforce


        self.area = self.strikearea
        self.energy = 0.5 * self.strikemass * self.speed ** 2

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass, 1))*(self.limb.stats['tec']+15)/15+0.1
        self.strikemass = random.triangular(low=self.limb.movemass, high=self.strikemass, mode=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec']))
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        thickness,density=self.armor_penetration()
        #self.force = self.damagefactor* (self.speed * (1000000000 * self.reducedmass * (self.area**0.5) / (
        #    self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        self.force = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.limb.length / self.limb.youngs + thickness / self.youngs)**0.25) + self.pushforce)+1


        self.pressure = self.force / self.area
        f = self.force
        self.attacker.stamina[0] -= int(max(1, 5 * (0.1*self.body.movemass+self.limb.mass) / self.basestrength))

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
        try:
            new = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(target)-1].density**0.25)*(
                self.limb.length / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1
        except:
            new = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[len(self.basetarget.layers)-1].density**0.25)*(
                self.limb.length / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'Bite','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=5/self.attacker.stats['tec']
        pushforce=6*self.strength*self.strikemass**0.5
        speed=0.274*(self.strikelength*pushforce/self.strikemass)**0.5
        swingtime=0.5*(speed*self.strikemass**1.25)/pushforce
        striketime=1.5*swingtime+broadcast_time
        information['Execution Time']=striketime

        strikemass=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec'])

        avgforce=0.2 * (speed * (10**3) * (strikemass**0.75) / ((5000**0.25)*(
            self.limb.length / self.limb.youngs + 1)**0.25) + pushforce)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 5 * (0.1*self.body.movemass+self.limb.mass) / max(self.basestrength,1)))

        return information

    def test_usability(self,hands):
        if self.limb.ability<=0:
            self.useless=True
        elif self.limb.attachpoint==None:
            self.useless=True
        elif self.limb.attachpoint.ability<=0:
            self.useless=True
        else:
            self.useless=False

class Peck(Attack):
    def __init__(self, limb=None,weapon=None):
        super().__init__()
        self.damagefactor=1
        self.type = 'pierce'
        self.oldtype = 'pierce'
        self.absolute_depth_limit=limb.length
        self.sig=(Sting,limb)
        self.arpen = 0.1
        self.limb = limb
        self.accuracy=3
        self.attacker = limb.owner
        self.head = limb.attachpoint
        self.strikearea = limb.tip
        if self.attacker.player == True:
            self.name = 'a peck with your {}'.format(limb.name)
        else:
            self.name = 'a peck with its {}'.format(limb.name)
        if self.head==None:
            self.useless=True
            self.strikelength=0
            return
        self.neck=self.head.attachpoint
        if self.neck==None:
            self.basestrength=self.head.stats['str']*self.head.ability
            self.strikelength=self.limb.length
            self.strikemass=self.head.movemass
        else:
            self.basestrength=self.neck.stats['str']*self.neck.ability
            self.strikelength=self.neck.length+self.limb.length
            self.strikemass=self.head.movemass+self.neck.movemass
        self.strikemass+=self.limb.owner.mass



        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.limb,None)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        self.basetarget = target
        self.target = target
        self.contact = True

        self.pushforce=6*self.strength*self.strikemass**0.5

        self.speed = (random.triangular(0.01,0.8,0.1)*self.strikelength*self.pushforce/self.strikemass)**0.5
        broadcast_time=5*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+0.75*(self.speed*self.strikemass**1.25)/self.pushforce


        self.area = self.strikearea
        self.energy = 0.5 * self.strikemass * self.speed ** 2

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass, 1))*(self.limb.stats['tec']+15)/15+0.1
        self.strikemass = random.triangular(low=self.limb.movemass, high=self.strikemass, mode=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec']))
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        thickness,density=self.armor_penetration()
        #self.force = self.damagefactor* (self.speed * (1000000000 * self.reducedmass * (self.area**0.5) / (
        #    self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        self.force = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.limb.length / self.limb.youngs + thickness / self.youngs)**0.25) + self.pushforce)+1


        self.pressure = self.force / self.area
        f = self.force
        self.attacker.stamina[0] -= int(max(1, 5 * (self.head.movemass + self.limb.mass) / self.basestrength))

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
        try:
            new = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(target)-1].density**0.25)*(
                self.limb.length / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1
        except:
            new = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[len(self.basetarget.layers)-1].density**0.25)*(
                self.limb.length / self.limb.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'Peck','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=5/self.attacker.stats['tec']
        pushforce=6*self.strength*self.strikemass**0.5
        speed=0.274*(self.strikelength*pushforce/self.strikemass)**0.5
        swingtime=0.5*(speed*self.strikemass**1.25)/pushforce
        striketime=1.5*swingtime+broadcast_time
        information['Execution Time']=striketime

        strikemass=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec'])

        avgforce=0.2 * (speed * (10**3) * (strikemass**0.75) / ((5000**0.25)*(
            self.limb.length / self.limb.youngs + 1)**0.25) + pushforce)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea)
        information['Average Pressure']=avgpressure

        information['Stamina Cost']=int(max(1, 5 * (self.head.movemass + self.limb.mass) / max(self.basestrength,1)))

        return information

    def test_usability(self,hands):
        if self.limb.ability<=0:
            self.useless=True
        elif self.limb.attachpoint==None:
            self.useless=True
        elif self.limb.attachpoint.ability<=0:
            self.useless=True
        else:
            self.useless=False


class Slash_2H(Attack):
    def __init__(self, weapon=None, limb=None):
        super().__init__()
        self.limb=limb
        self.hands=2
        self.damagefactor=1
        self.absolute_depth_limit=weapon.length
        self.type = 'cut'
        self.oldtype = 'cut'
        self.weapon = weapon
        self.sig=(Slash_2H,self.weapon)
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

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.weapon, self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01
        if hasattr(target,'stats'):
            luc=target.stats['luc']
            tec=target.stats['tec']
        else:
            luc=10
            tec=10
        self.basetarget = target
        self.target = target
        self.contact = True
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / luc)*anglefactor
        self.w = ((2 * torque * swingangle / self.I) ** 0.5)
        self.collidepoint = self.strikelength * random.triangular(
            mode=(self.attacker.stats['tec'] + 0.5 * self.attacker.stats['luc']) / (
                luc + 0.5 * tec))
        self.pushforce = torque #/ self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.05, 0.5, mode=0.5/self.attacker.stats['tec']**0.5)
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+1.5*(self.I) * self.w / torque

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        movemass = abs(random.gauss(self.target.movemass*self.collidepoint**2, 1))
        self.reducedmass = self.I * movemass / (self.I + movemass)
        thickness,density=self.armor_penetration()

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
        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        self.attacker.stamina[0] -= int(max(1, 5 * (movemass + self.I) / (self.basestrength+0.01)))

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
        try: newdensity=self.basetarget.layers[len(self.basetarget.layers)-1].density
        except AttributeError:
            try: newdensity=self.basetarget.density
            except AttributeError: newdensity=5000
        try:
            new = self.damagefactor*0.5* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(self.target)-1].density**0.25)*(
                self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        except:
            new = self.damagefactor*0.5* (self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((newdensity**0.25)*(
                self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'2H+ Slash','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / 12
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=1.5*self.I*w/torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        avgforce = 0.5* (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            (self.weapon.thickness / self.weapon.material.youngs) + 1)**0.25) + torque)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea*0.5/self.attacker.stats['tec']**0.5)
        information['Average Pressure']=avgpressure

        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        information['Stamina Cost']=int(max(1, 5 * (movemass + self.I) / (self.basestrength+0.01)))

        return information

class Stab_2H(Attack):
    def __init__(self, weapon=None, limb=None):
        super().__init__()
        self.hands=2
        self.damagefactor=1
        self.type = 'pierce'
        self.oldtype = 'pierce'
        self.absolute_depth_limit=weapon.length
        self.weapon = weapon
        self.sig=(Stab_2H,self.weapon)
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
            if arm==None: arm=i
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

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.weapon, self.limb)
        try:
            defender_reach=target.owner.reach
        except:
            defender_reach=0.01

        self.basetarget = target
        self.target = target
        self.contact = True

        self.pushforce=6*self.strength*self.strikemass**0.5

        self.speed = (random.triangular(0.01,0.8,0.1)*self.strikelength*self.pushforce/self.strikemass)**0.5
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/max(self.attacker.stats['tec']*(self.attacker.focus[0]+1),1)
        self.time = broadcast_time+0.75*(self.speed*self.strikemass**1.25)/self.pushforce


        self.area = self.strikearea
        self.energy = 0.5 * self.strikemass * self.speed ** 2

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass
        

        #movemass = random.triangular(low=self.target.movemass, high=maxtargetmass, mode=self.target.movemass)
        tec=sum(i.stats['tec']**2 for i in self.limbs)**0.5
        movemass = abs(random.gauss(self.target.movemass, 1))*(tec+15)/15+0.1
        self.strikemass = random.triangular(low=self.weapon.mass, high=self.strikemass, mode=1.5*self.strikemass*tec/(10+tec))
        self.reducedmass = self.strikemass * movemass / (self.strikemass + movemass)
        thickness,density=self.armor_penetration()

        #self.force = self.damagefactor* (self.speed * (1000000000 * self.reducedmass * (self.area**0.5) / (
        #    self.weapon.thickness / self.weapon.material.youngs + thickness / self.target.youngs)) ** 0.5 + self.pushforce)

        self.force = self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.length / self.weapon.youngs + thickness / self.youngs)**0.25) + self.pushforce)+1


        self.pressure = self.force / self.area
        f = self.force
        if hasattr(self.weapon,'stats'):
            self.stattedweapon=True
            pass
        else:
            self.stattedweapon=False
            self.weapon.stats = self.limb.stats

        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        self.attacker.stamina[0] -= int(max(1, 5 * (movemass + self.weapon.mass) / (self.basestrength+0.01)))

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
        try:
            new=self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(self.target)-1].density**0.25)*(
                self.weapon.length / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1

        except:
            try: newdensity=self.basetarget.layers[len(self.basetarget.layers)-1].density
            except AttributeError:
                try: newdensity=self.basetarget.density
                except AttributeError: newdensity=5000
            new=self.damagefactor*0.2* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((newdensity**0.25)*(
                self.weapon.length / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)+1
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'2H+ Stab','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        pushforce=6*self.strength*self.strikemass**0.5
        speed=0.274*(self.strikelength*pushforce/self.strikemass)**0.5
        swingtime=0.5*(speed*self.strikemass**1.25)/pushforce
        striketime=1.5*swingtime+broadcast_time
        information['Execution Time']=striketime

        strikemass=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec'])

        avgforce=0.2 * (speed * (10**3) * (strikemass**0.75) / ((5000**0.25)*(
            self.weapon.length / self.weapon.youngs + 1)**0.25) + pushforce)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea)
        information['Average Pressure']=avgpressure
        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        information['Stamina Cost']=int(max(1, 5 * (movemass + self.weapon.mass) / (self.basestrength+0.01)))

        return information

class Bludgeon_2H(Attack):
    def __init__(self, weapon=None, limb=None):
        super().__init__()
        self.hands=2
        self.limbs=weapon.equipped
        self.attacker = limb.owner
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.sig=(Bludgeon_2H,self.weapon)
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
            #print(self.I,self.basestrength)

        self.I+=0.5*weapon.mass * ((self.strikelength-weapon.length)/2+weapon.centermass) ** 2
        #print(self.I)

        if self.attacker.player == True:
            self.name = 'a swing of your {}'.format(weapon.name)
        else:
            self.name = 'a swing of its {}'.format(weapon.name)
        self.strength = self.basestrength * (
            (max(self.attacker.stamina[0] / self.attacker.stamina[1], 0)) ** 0.5) + 0.01

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.weapon, self.limb)
        try:
            defender_reach=target.owner.reach
        except: defender_reach=0.01
        if hasattr(target,'stats'):
            luc=target.stats['luc']
            tec=target.stats['tec']
        else:
            luc=10
            tec=10
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / luc)*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.strikelength - self.weapon.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + 2*(self.I) * self.w / torque

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

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
        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        self.attacker.stamina[0] -= int(max(1, 4 * (movemass + self.I) / (self.basestrength+0.01)))

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
        try:
            new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(self.target)-1].density**0.25)*(
                self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)

        except:
            new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
                self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'2H+ Strike','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / 12
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=1.5*self.I*w/torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        avgforce = (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + 1)**0.25) + 3*torque/(self.strikelength))

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea/self.attacker.stats['tec']**0.5)
        information['Average Pressure']=avgpressure

        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        information['Stamina Cost']=int(max(1, 4 * (movemass + self.I) / (self.basestrength+0.01)))

        return information

class Swing_Pierce_2H(Bludgeon_2H):
    def __init__(self,weapon=None,limb=None):
        super().__init__(weapon,limb)
        self.type='pierce'
        self.oldtype='pierce'
        self.arpen=0
        self.absolute_depth_limit=0.1
        self.strikearea=weapon.tip
        self.area=self.strikearea
        self.sig=(Swing_Pierce_2H,self.weapon)
        if self.attacker.player == True:
            self.name = 'a swing with the point of your {}'.format(weapon.name)
        else:
            self.name = 'a swing with the point of its {}'.format(weapon.name)

    def do(self,target,anglefactor=1,**kwargs):
        super().do(target,anglefactor,**kwargs)

    def average_values(self):
        information={'Attack Name':'2H+ Spike Pierce','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / 12
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=1.5*self.I*w/torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        avgforce = (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + 1)**0.25) + 3*torque/(self.strikelength))

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea/self.attacker.stats['tec']**0.5)
        information['Average Pressure']=avgpressure

        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        information['Stamina Cost']=int(max(1, 4 * (movemass + self.I) / (self.basestrength+0.01)))

        return information

class Shield_Bash_2H(Bludgeon_2H):
    def __init__(self,weapon=None,limb=None):
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
        self.sig=(Shield_Bash_2H,self.weapon)

    def do(self, target,**kwargs):
        super().do(target,anglefactor=0.1/self.weapon.mass,**kwargs)
        try:
            if self.blocked==False and self.parried==False and self.dodged==False:
                creature=self.basetarget.owner
                if 2*self.strikemass*random.random()*self.attacker.stats['per']**0.5>(creature.mass**0.5)*random.random()*creature.stats['per']*creature.balance*creature.focus[0]/creature.focus[1]:
                    if "off_balance" not in creature.conditions:
                        creature.conditions.append("off_balance")
                        if creature in Shell.shell.player.visible_creatures: Shell.messages.append("{} is knocked off balance!".format(creature.name))
        except: pass

    def average_values(self):
        information={'Attack Name':'2H+ Shield Bash','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / (12*max(self.weapon.mass,1))
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=1.5*self.I*w/torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        avgforce = (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + 1)**0.25) + 3*torque/(self.strikelength))

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea/self.attacker.stats['tec']**0.5)
        information['Average Pressure']=avgpressure
        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        information['Stamina Cost']=int(max(1, 4 * (movemass + self.I) / (self.basestrength+0.01)))

        return information

class Strike_2H(Attack):
    def __init__(self, weapon=None, limb=None):
        super().__init__()
        self.hands=2
        self.damagefactor=1
        self.type = 'crush'
        self.oldtype = 'crush'
        self.weapon = weapon
        self.sig=(Strike_2H,self.weapon)
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
            elif i.attachpoint is not None:
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

    def do(self, target,anglefactor=1,**kwargs):
        self.__init__(self.weapon, self.limb)
        try: defender_reach=target.owner.reach
        except: defender_reach=0.01
        if hasattr(target,'stats'):
            luc=target.stats['luc']
            tec=target.stats['tec']
        else:
            luc=10
            tec=10
        self.basetarget = target
        self.target = target
        self.contact = True
        torque = 7 * self.strength * self.I ** 0.5
        self.swingangle = random.triangular(low=0.5, high=4.5, mode=2 * self.attacker.stats['tec'] / luc)*anglefactor
        self.w = ((2 * torque * self.swingangle / self.I) ** 0.5)
        self.collidepoint = self.strikelength - self.weapon.length + self.weapon.length * random.triangular(mode=1)
        self.pushforce = 3 * torque / self.collidepoint
        self.speed = self.w * self.collidepoint
        self.area = self.strikearea * random.triangular(0.1, 1,mode=max(1/self.attacker.stats['tec']**0.5,0.1))
        self.energy = 0.5 * self.I * self.w ** 2
        broadcast_time=3*random.gauss(1,0.2)*self.attacker.focus[1]/(self.attacker.stats['tec']*max(self.attacker.focus[0],1))
        self.time = broadcast_time + 2 *(self.I) * self.w / torque

        self.pre_evasion(**kwargs)
        try: self.target.owner.evasion(self)
        except: pass

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

        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        self.attacker.stamina[0] -= int(max(1, 4 * (movemass + self.I) / (self.basestrength+0.01)))

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
        try:
            new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[self.basetarget.layers.index(self.target)-1].density**0.25)*(
                self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        except:
            new = self.damagefactor*(self.w * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
                self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25) + self.pushforce)
        self.force = min(new, 0.9 * self.force)

    def average_values(self):
        information={'Attack Name':'2H+ Strike','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        torque =  7 * self.strength * self.I ** 0.5
        swingangle = 2 * self.attacker.stats['tec'] / 12
        w = ((2 * torque * swingangle / self.I) ** 0.5)
        swingtime=2*self.I*w/torque
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        avgforce = (w * (10**3) * (self.I**0.75) / ((5000**0.25)*(
            self.weapon.thickness / self.weapon.youngs + 1)**0.25) + 3*torque/(self.strikelength))

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea/self.attacker.stats['tec']**0.5)
        information['Average Pressure']=avgpressure

        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        information['Stamina Cost']=int(max(1, 4 * (movemass + self.I) / (self.basestrength+0.01)))

        return information

class Blunt_Thrust_2H(Stab_2H):
    def __init__(self,weapon=None,limb=None):
        super().__init__(weapon,limb)
        self.type='crush'
        self.oldtype='crush'
        if self.attacker.player == True:
            self.name = 'a thrust with your {}'.format(weapon.name)
        else:
            self.name = 'a thrust with its {}'.format(weapon.name)
        self.sig=(Blunt_Thrust_2H,self.weapon)

    def average_values(self):
        information={'Attack Name':'2H+ Thrust','Damage Type':self.type,'Strike Length':self.strikelength}
        broadcast_time=3/self.attacker.stats['tec']
        pushforce=6*self.strength*self.strikemass**0.5
        speed=0.1*(self.strikelength*pushforce/self.strikemass)**0.5
        swingtime=0.5*(speed*self.strikemass**1.25)/pushforce
        striketime=swingtime+broadcast_time
        information['Execution Time']=striketime

        strikemass=1.5*self.strikemass*self.limb.stats['tec']/(10+self.limb.stats['tec'])

        avgforce=0.5 * (speed * (10**3) * (strikemass**0.75) / ((5000**0.25)*(
            self.weapon.length / self.weapon.youngs + 1)**0.25) + pushforce)

        information['Average Force']=avgforce

        avgpressure=avgforce/(self.strikearea)
        information['Average Pressure']=avgpressure

        movemass=0
        for i in self.limbs:
            try: movemass+=i.movemass+i.attachpoint.movemass
            except: movemass+=i.movemass
        information['Stamina Cost']=int(max(1, 5 * (movemass + self.weapon.mass) / (self.basestrength+0.01)))

        return information

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

        try: self.target.owner.evasion(self)
        except: pass

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
        new = self.damagefactor*(self.w * (10**3) * (self.target.shear**0.25) * (self.reducedmass**0.75) / ((self.basetarget.layers[len(self.basetarget.layers)-1].density**0.25)*(
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

        try: self.target.owner.evasion(self)
except: pass

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




__author__ = 'Alan'

from UI_Elements import *

import kivy
import random
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import Shell
import Attacks as A
import re
import Items



def inventoryadd(item):
    print('{} added to inventory'.format(item))


incapacitate=re.compile("incapacitated")


'''
All of this is necessary to build further classes, and contains useful common routines for subclasses.
Importantly:

-Materials are used in the construction of Items, in that all items must be made of some material or another.

-Material damageresolve processes differently according to the mode (failure mode) of the material in question. Options
are soft, brittle, and ductile.

-Materials pass the damage they process to the Item, which stores the damage in the dictionary self.damage. The
functioncheck method determines how functional the item is (standard range is 0-1, but perhaps blessings can
surpass this)

-Items (notably the items comprising limb layers) are capable of recovering by calling the recover() method. Shattering
and crushing cannot be recovered by normal means.

-Items have a location attribute so that they can be appropriately placed on the grid, but for inventoried/wielded items
this does not need to be updated.

-Limbs are made of layers of items. The damage resolution on limbs is set up to distribute this damage appropriately
to each layer. Limbs are also capable of creating pain when their items are damaged (the pain is actually generated
within the damageresolve of the items comprising the layers)

-Each limb has an ability attribute determining how able the limb is overall. It is generally the minimum value of the
functions of each layer (exceptions may be made for things like the head).

-Great care must be taken with attacks. They typically target -limbs-, and are set up primarily to do so, but
strictly speaking CAN target items which may lack certain expected attributes. This needs tested whenever changes
are made.

'''

#TODO: Burns and pierces are still not implemented


class Limb():
    def __init__(self,stats,natural=True,color=(1,1,1,1),owner=None,*args,**kwargs):
        self.owner=owner
        self.stats=stats
        self.grasp=False
        self.support=False
        self.sight=False
        self.hear=False
        self.smell=False
        self.ability=1
        self.painfactor=1
        self.plural=False
        self.contains_vitals=False
        self.image='./images/limb.png'
        self.location=[None,None]
        self.color=color
        self.passable=True
        self.targetable=False
        self.hostile=[]
        self.staminacost=0
        self.focuscost=0
        self.armor=None
        self.limbs=[]
        self.inoperable=False
        self.primaryequip=[]

    def youngscalc(self):
        layersum=0
        i=len(self.layers)-1
        j=0
        masssum=0
        ltotal=0
        limbmass=self.mass
        if self.armor is not None:
            layersum+=self.armor.thickness/self.armor.material.youngs
            masssum+=self.armor.mass
            ltotal+=self.armor.thickness
            limbmass=self.mass+self.armor.mass
        while i>=0 and j<3:
            layersum+=(self.layers[i].thickness/self.layers[i].material.youngs)*(1-masssum/limbmass)
            masssum+=self.layers[i].mass
            ltotal+=self.layers[i].thickness
            i-=1
            j+=1
        self.youngs=ltotal/layersum
        self.thickness=ltotal*2

    def damageresolve(self,attack,attacker,reactionforce=False):
        i=len(self.layers)-1
        f=attack.force
        pressure=attack.pressure
        if pressure==0:
            area=1
        else:
            area=attack.force/pressure
        mass=self.mass
        if self.armor is not None:
            mass=self.mass+self.armor.mass
            if self.armor.coverage*abs(random.gauss(self.stats['luc'],1))>random.random()*(attacker.stats['luc']+2*attacker.stats['tec'])/3+attack.arpen:
                attack.target=self.armor
                self.armor.damageresolve(attack,attacker,reactionforce=reactionforce)
                if attack.contact==False and self.armor is not None:
                    f-=f*self.armor.mass/mass
                    area=area+(self.armor.material.shear**0.7)*(3.54*self.armor.thickness*area**0.5+3.14*self.armor.thickness**2)
                    pressure=f/area
                    attack.force=f
                    attack.pressure=pressure
                if self.armor is not None:
                    self.armor.functioncheck()
            else:
                messages.append("The blow strikes an opening in the armor!")
                attack.contact=True
        while i>=0:
            attack.target=self.layers[i]
            if attack.type=='pierce':
                if i!=len(self.layers)-1:
                    further_pierce_chance=1-self.layers[i+1].thickness/(self.layers[i+1].radius+0.01)
                    if further_pierce_chance<random.random():
                        print("failed at layer",i)
                        #self.layers[i].damageresolve(attack,attacker,reactionforce=reactionforce)
                        i=-1
                        break

            self.layers[i].damageresolve(attack,attacker,reactionforce=reactionforce)


            if self.layers[i].material.mode=='soft':
                softnessfactor=0.3
            else:
                softnessfactor=1

            if attack.contact==False:
                f-=softnessfactor*f*self.layers[i].mass/mass
                area=area+(3.54*self.layers[i].thickness*area**0.5+3.14*self.layers[i].thickness**2)*(self.layers[i].material.shear**0.7)/softnessfactor
                pressure=f/area
                attack.force=f
                attack.pressure=pressure

            if i==len(self.layers)-1 and self.layers[i].damage['shatter']>=1:
                self.layers.remove(self.layers[i])
            i-=1


        severed=True
        for i in self.layers:
            if i.damage['cut']<1 and i.damage['break']<1:
                severed=False
        if severed==True:
            self.sever()
        else:
            self.updateability()
        self.additional_effects()

    def unequip(self,slot,cascade=False,destroyed=False,drop=False,log=True):
        if not slot in self.equipment:
            if cascade==False:
                print("no {} on {}".format(slot,self.name))
            return
        if slot=='grasp':
            self.attacks=self.defaultattacks
        if self.equipment[slot] is not None:
            if cascade==False:
                if destroyed==False:
                    if drop==True:
                        #Need to drop item here
                        self.equipment[slot].location[0]=min(max(self.owner.location[0]+int(random.gauss(0,2)),0),Shell.shell.dungeonmanager.current_screen.dimensions[0]-1)
                        self.equipment[slot].location[1]=min(max(self.owner.location[1]+int(random.gauss(0,2)),0),Shell.shell.dungeonmanager.current_screen.dimensions[1]-1)
                        if Shell.shell.dungeonmanager.current_screen.cells[self.equipment[slot].location[0]][self.equipment[slot].location[1]]:
                            if any(isinstance(x,MapTiles.Wall) for x in Shell.shell.dungeonmanager.current_screen.cells[self.equipment[slot].location[0]][self.equipment[slot].location[1]].contents):
                                Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]].contents.append(self.equipment[slot])
                            else:
                                Shell.shell.dungeonmanager.current_screen.cells[self.equipment[slot].location[0]][self.equipment[slot].location[1]].contents.append(self.equipment[slot])
                        else:
                            Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]].contents.append(self.equipment[slot])
                        if self.equipment[slot] in self.owner.inventory:
                            self.owner.inventory.remove(self.equipment[slot])
                    elif self.equipment[slot] not in self.owner.inventory:
                        self.owner.inventory.append(self.equipment[slot])
                if self.equipment[slot].mass:
                    self.movemass-=self.equipment[slot].mass
                if log==True and destroyed==True:
                    messages.append("The {} is destroyed!".format(self.equipment[slot].name))
                if destroyed==True and self.equipment[slot] in self.owner.inventory:
                    self.owner.inventory.remove(self.equipment[slot])
            if self.equipment[slot] in self.owner.equipped_items:
                self.owner.equipped_items.remove(self.equipment[slot])
            self.equipment[slot].equipped=None
            self.equipment[slot]=None
            self.armor=self.equipment[self.armortype]
            if self.limbs:
                for i in self.limbs:
                    i.unequip(slot,cascade=True)

    def updateability(self):
        self.ability=1
        for i in self.layers:
            i.functioncheck()
            self.ability=min(self.ability,i.function)
        self.ability=max(self.ability,0)
        if hasattr(self,'dexterity'):
            self.dex_calc()
        if hasattr(self.attachpoint,'dexterity'):
            self.attachpoint.dex_calc()
        if hasattr(self,'balance'):
            self.balance_calc()
        if hasattr(self.attachpoint,'balance'):
            self.attachpoint.balance_calc()
        if hasattr(self,'vision'):
            self.vision_calc()
        if hasattr(self,'smell_sense'):
            self.smell_calc()
        if hasattr(self,'hearing'):
            self.hearing_calc()

    def sever(self, primary=True):
        if primary:
            self.owner.pain+=75*self.painfactor
            messages.append("{}'s {} is severed from the body!".format(self.owner.name,self.name))
            if self.attachpoint:
                if self not in self.attachpoint.limbs:
                    print("Tried to remove {}'s {} from {} and failed".format(self.owner.name,self.name,self.attachpoint.name))
                    print(self.attachpoint.limbs)
                self.attachpoint.limbs.remove(self)
            self.location[0]=min(max(self.owner.location[0]+int(random.gauss(0,2)),0),Shell.shell.dungeonmanager.current_screen.dimensions[0])
            self.location[1]=min(max(self.owner.location[1]+int(random.gauss(0,2)),0),Shell.shell.dungeonmanager.current_screen.dimensions[1])
            if Shell.shell.dungeonmanager.current_screen.cells[self.location[0]][self.location[1]]:
                Shell.shell.dungeonmanager.current_screen.cells[self.location[0]][self.location[1]].contents.append(self)
            else:
                Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]].contents.append(self)
        if self.owner:
            self.owner.limbs.remove(self)
        for i in self.layers:
            i.function=0

        for i in self.limbs:
            i.sever(primary=False)

    def recover(self,turns=1,**kwargs):
        for i in self.layers:
            if i.function<1:
                i.recover(self.stats)
        self.updateability()
        if self.inoperable==True:
            self.ability=0

    def additional_effects(self):
        pass

    def vision_calc(self):
        self.vision=self.ability
        if hasattr(self.armor,'vision_blocking'):
            self.vision=self.vision*(1-self.armor.vision_blocking)
        if self.vision<=0:
            self.sight=False

    def smell_calc(self):
        self.smell_sense=self.ability
        if hasattr(self.armor,"smell_blocking"):
            self.smell_sense=self.smell_sense*(1-self.armor.smell_blocking)
        if self.smell_sense<=0:
            self.smell=False

    def hearing_calc(self):
        self.hearing=self.ability
        if hasattr(self.armor,'sound_blocking'):
            self.hearing=self.hearing*(1-self.armor.sound_blocking)
        if self.hearing<=0:
            self.hear=False

    def mass_calc(self):
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        for i in self.primaryequip:
            if self.equipment[i] is not None:
                self.mass+=self.equipment[i].mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.mass

    def on_turn(self,turns=1,**kwargs):
        if self.ability<1:
            self.recover(turns=turns,**kwargs)
        if self.ability>0 and self.owner is not None:
            self.owner.attacks.extend(self.attacks)

    def on_strike(self):
        pass

    def on_struck(self):
        pass

    def change_material(self,oldmaterial,newmaterial):
        for i in self.layers:
            if isinstance(i.material,oldmaterial):
                oldname=i.material.name
                oldquality=i.material.quality
                i.material=newmaterial(quality=oldquality)
                i.recalc()
                print("Changed {} material from {} to {}".format(self.name,oldname,i.material.name))
        self.mass_calc()
        if self.owner!=None:
            self.owner.mass_calc()

class Creature():
    def __init__(self,**kwargs):
        self.attacked=False
        self.location=[None,None]
        self.alive=True
        self.pain=0
        self.combataction=False
        self.can_grasp=False
        self.can_walk=False
        self.can_see=False
        self.can_smell=False
        self.can_hear=False
        self.balance=0
        self.vision=0
        self.hearing=0
        self.smell_sense=0
        self.esp=0
        self.equipped_items=[]
        self.inventory=[]
        self.conditions=[]
        self.balance_recovery=0
        self.classification=[]
        self.hostile=[]

    def updateattacks(self):
        self.attacks=[]
        for i in self.limbs:
            if i.ability>0:
                self.attacks.extend(i.attacks)

    def on_turn(self,turns=1):
        if self.location==[None,None]:
            return

        if self.alive==True:

        #collapse from exhaustion if stamina runs too low
            if self.stamina[0]<self.stats['str']*random.gauss(4/self.stats['luc']**0.5,1/self.stats['luc']):
                if 'stamina_incapacitated' not in self.conditions:
                    self.conditions.append('stamina_incapacitated')
                    messages.append('{} collapses from exhaustion'.format(self.name))
            elif 'stamina_incapacitated' in self.conditions:
                self.stamina[0]+=int(self.stats['str']**0.8)+1
                if (self.stats['str']*self.stats['luc'])**0.5>random.gauss(300,60)/self.stamina[0]:
                    self.conditions.remove('stamina_incapacitated')
                    messages.append("{} recovers from exhaustion".format(self.name))
            if "off_balance" in self.conditions:
                if self.balance_recovery==1:
                    while "off_balance" in self.conditions:
                        self.conditions.remove("off_balance")
                    self.balance_recovery=0
                else:
                    self.balance_recovery=1



        #handle regeneration of stamina and focus, if applicable
            if self.attacked==False:
                self.stamina[0]+=max(int(self.stats['str']**0.8-self.movemass/self.stats['str']**1.5),0)+1
                self.stamina[0]=min(self.stamina[0],self.stamina[1])
                self.stamina[0]=max(0,self.stamina[0])
                if self.combataction==False:
                    self.focus[0]+=int((self.focus[1]-self.focus[0])*self.stats['per']*self.stamina[0]/(100*self.stamina[1]))+1
            self.attacked=False
            self.combataction=False

        #If alive, test to see if creature has sustained fatal damage

            if self.limbs==[]:
                self.die()
                return
            for i in self.vitals:
                if i.function==0:
                    self.die()
                    return

        #If alive, recover, and test for senses
            self.attacks=[]
            for i in self.limbs:
                i.on_turn()
            self.sense_awareness()



        #Test for pain-related loss of focus or incapacitation
            self.pain-=((self.stats['wil'])**0.8)/2
            self.pain=max(0,self.pain)
            self.focus[0]=min(self.focus[0],self.focus[1]-self.pain**0.9)
            self.focus[0]=int(max(0,self.focus[0]))
            if self.pain*random.gauss(1,0.3)>self.stats['wil']**1.9:
                if 'pain_incapacitated' not in self.conditions:
                    self.conditions.append('pain_incapacitated')
                    messages.append('{} collapses in pain!'.format(self.name))
            elif 'pain_incapacitated' in self.conditions:
                if self.stats['luc']*self.stats['wil']>self.pain*random.gauss(1,0.4):
                    self.conditions.remove('pain_incapacitated')
                    messages.append('{} recovers from the pain.'.format(self.name))


        #recalculate mass and movemass of creature
            self.mass=0
            for i in self.limbs:
                self.mass+=i.mass
            self.movemass=self.mass
            for i in self.equipped_items:
                if i.mass:
                    self.movemass+=i.mass

        #Make sure action is possible
            for i in self.conditions:
                if incapacitate.search(i):
                    return

            #run AI routines
            if self.player==False and self.alive==True:
                self.chase(Shell.shell.player)
                pass

    def equip(self,item,log=True):
        for i in self.limbs:
            if item.wield in i.equipment and item.wield in i.primaryequip:
                if i.equipment[item.wield] is None and item.equipped is None:
                    i.equip(item)
                    if item.wield=='grasp' and log==True:
                        messages.append("{} is now held in {}".format(item.name,i.name))
                    elif log==True:
                        messages.append("{} is now equipped on {}".format(item.name,i.name))
                    self.updateattacks()
                    self.mass_calc()
                    return
        self.mass_calc()

    def unequip(self,item,log=True):
        for i in self.limbs:
            if item.wield in i.equipment:
                if i.equipment[item.wield]==item:
                    i.unequip(item.wield,log=log)

    def die(self):
        #self.targetable=False
        self.alive=False
        self.hostile=[]
        self.passable=True
        messages.append("{} has been slain!".format(self.name))
        if self.player==True:
            messages.append("YOU HAVE DIED!")

    def move(self,movement):
        if self.can_walk==True:
            Shell.shell.move(self,movement)
        else:
            Shell.shell.move(self,movement,mobile=False)

    def wander(self):
        self.move([random.choice([1,0,-1]),random.choice([1,0,-1])])

    def chase(self,target):
        movement=[]
        if target.location[0]>self.location[0]:
            movement.append(1)
        elif target.location[0]<self.location[0]:
            movement.append(-1)
        else:
            movement.append(0)
        if target.location[1]>self.location[1]:
            movement.append(1)
        elif target.location[1]<self.location[1]:
            movement.append(-1)
        else:
            movement.append(0)
        self.move(movement)

    def attack(self,target):
        self.updateattacks()
        if self.attacks==[] or "off_balance" in self.conditions:
            return
        endattack=False
        attacksmade=0
        if target==self:
            return
        atk=[]
        atk.append(random.choice(self.attacks))
        unusable_attacks=[atk[0]]
        while endattack==False:
            hit_location=A.targetchoice(target)
            if hit_location is None:
                return
            while hit_location.ability<=0 and hit_location.contains_vitals==False:
                retargeted=False
                for i in target.conditions:
                    if incapacitate.search(i):
                        hit_location=A.targetchoice(target)
                        retargeted=True
                if random.random()*self.stats['tec']>random.random()*(target.stats['per']**0.5)*(target.stats['luc']**0.5) and retargeted==False:
                    break
                if retargeted==False:
                    hit_location=A.targetchoice(target)
            for i in self.attacks:
                if i.weapon==atk[attacksmade].weapon or i.limb==atk[attacksmade].limb:
                    unusable_attacks.append(i)
            if self.player==True:
                messages.append('You attack {} in the {} with {}'.format(target.name,hit_location.name,atk[attacksmade].name))
                atk[attacksmade].do(hit_location)
                self.attacked=True
                attacksmade+=1
            elif target.player==True:
                messages.append('{} attacks your {} with {}'.format(self.name,hit_location.name,atk[attacksmade].name))
                atk[attacksmade].do(hit_location)
                self.attacked=True
                attacksmade+=1
            else:
                messages.append('{} attacks {} in the {} with {}'.format(self.name,target.name,hit_location.name,atk[attacksmade].name))
                atk[attacksmade].do(hit_location)
                self.attacked=True
                attacksmade+=1
            #test to see if another attack can be made
            if self.stats['tec']/attacksmade**0.8>random.triangular()*target.stats['per']**2/(2*(self.stats['luc'])**0.3):
                atk.append(random.choice(self.attacks))
                if atk[attacksmade] in unusable_attacks:
                    endattack=True
            else:
                endattack=True

    def evasion(self,attack):
        self.combataction=True

        #incapacitated foes are unable to make even the most basic of evasive maneuvers and take much greater damage
        for i in self.conditions:
            if incapacitate.search(i):
                attack.damagefactor=attack.attacker.stats['tec']
                attack.arpen+=0.5
                messages.append('{} is defenseless!'.format(self.name))
                self.stamina[0]-=attack.basetarget.staminacost
                self.focus[0]-=attack.basetarget.staminacost
                return


        reactiontime=(1/(self.stats['per'])**0.5)*random.gauss(1-(self.stats['luc']**0.5)/100,0.2)*random.gauss((self.focus[1]/max(self.focus[0],1)),0.1)

        #Test to see if target can see or hear the attacker. If not, suffer a large penalty to reaction ability.
        if attack.attacker.stats['tec']*random.random()>self.vision:
            if attack.attacker.stats['tec']>self.hearing*random.random():
                reactiontime=reactiontime*(1+(40-self.esp)/self.stats['per'])

        if attack.time<reactiontime or "off_balance" in self.conditions:
            attack.damagefactor=attack.attacker.stats['tec']**0.5
            messages.append('The attack takes {} completely unaware!'.format(self.name))
            return

        #Attempt to dodge
        dodgetime=reactiontime+((self.focus[1]/(1+self.focus[0]))**0.5)*random.gauss(3/(self.stats['tec']*self.stats['luc']**0.5),.01)*(self.movemass/(self.stats['str']*self.stamina[0]/(max(self.stamina[1],1))))*1.5*attack.accuracy/(self.balance+0.01)
        if dodgetime<attack.time and random.random()*attack.attacker.stats['tec']<random.random()*self.stats['per']:
            attack.dodged=True
            self.stamina[0]-=2*attack.basetarget.movemass/attack.basetarget.stats['str']
            print(attack.time,dodgetime)
            return

        #Attempt to block
        for i in self.equipped_items:
            if i.block==True:
                if i.equipped.attachpoint is not None:
                    basemass=i.equipped.attachpoint.movemass
                    strength=i.equipped.attachpoint.stats['str']*self.stamina[0]/(self.stamina[1]+1)
                else:
                    basemass=i.equipped.movemass
                    strength=i.equipped.stats['str']*self.stamina[0]/(self.stamina[1]+1)
                tec=i.equipped.stats['tec']*self.focus[0]/(self.focus[1]+1)

                blocktime=reactiontime+0.5*attack.accuracy*((self.focus[1]/(self.focus[0]+1))**0.4)*random.gauss(1/(self.stats['luc']**0.5),.1)*(2*i.mass/strength**2+1/(tec*i.radius+0.5)**2+1/(tec/(2*i.mass+basemass*0.5)+1.57*strength*i.radius**2))
                #print("{} block time is {}. Blocking attack of time {}".format(i.name,blocktime,attack.time))
                if blocktime<attack.time and random.random()*attack.attacker.stats['tec']<random.random()*self.stats['per']:
                    attack.blocked=True
                    attack.target=i
                    attack.basetarget=i
                    self.stamina[0]-=int(6*i.mass/i.equipped.stats['str'])
                    luc=self.stats['luc']
                    attack.damagefactor=1/random.triangular(1,(luc/(10+luc))*self.stats['tec']**0.5)
                    attack.strikearea*=50
                    return


        #Attempt to parry
        for i in self.equipped_items:
            if i.parry==True:
                if i.equipped.attachpoint==None:
                    armmass=10
                else:
                    armmass=i.equipped.attachpoint.mass
                parrytime=reactiontime+5*attack.accuracy*((self.focus[1]/(self.focus[0]+1))**0.5)*random.gauss(6/(self.stats['tec']*self.stats['luc']**0.5),.04)*(30*i.I+i.equipped.movemass+armmass*0.5)/max(i.equipped.stats['str']*i.length*i.equipped.dexterity,0.001)
                if parrytime<attack.time and random.random()*attack.attacker.stats['tec']<random.random()*self.stats['per']:
                    print(reactiontime,parrytime,attack.time)
                    attack.parried=True
                    attack.target=i
                    attack.basetarget=i
                    luc=self.stats['luc']
                    attack.damagefactor=0.05*(attack.attacker.stats['tec']/self.stats['tec'])/random.triangular(1,self.stats['tec'],(luc/(10+luc))*self.stats['tec'])
                    attack.strikearea*=5*i.equipped.stats['tec']**0.5
                    return

    def sense_awareness(self):
        self.can_walk=False
        self.can_grasp=False
        self.can_see=False
        self.can_smell=False
        self.can_hear=False
        self.hearing=0
        self.balance=0
        self.vision=0
        self.smell_sense=0
        for i in self.limbs:
            if i.support==True:
                self.can_walk=True
                self.balance+=i.balance
            if i.grasp==True:
                self.can_grasp=True
            if i.sight==True:
                self.can_see=True
                self.vision+=i.vision*i.stats['per']
            if i.hear==True:
                self.can_hear=True
                self.hearing+=i.hearing*i.stats['per']
            if i.smell==True:
                self.can_smell=True
                self.smell_sense+=i.smell_sense*i.stats['per']

        if self.vision<=0 and self.smell_sense<=0 and self.hearing<=0 and self.esp<=0:
            self.conditions.append('sensory_incapacitated')
        elif "sensory_incapacitated" in self.conditions:
            self.conditions.remove("sensory_incapacitated")

    def recover(self,effect=1):
        for i in self.limbs:
            i.recover()

    def make_skeleton(self,terminal=False):
        for i in self.limbs[:]:
            for j in i.layers[:]:
                if isinstance(j,Items.Flesh):
                    if j in self.vitals:
                        self.vitals.remove(j)
                    i.layers.remove(j)
            if len(i.layers)==0:
                if i.attachpoint:
                    i.attachpoint.limbs.remove(i)
                self.limbs.remove(i)
        self.name+="'s skeleton"
        self.classification.append('skeleton')
        self.classification.append('undead')
        self.esp+=40

    def mass_calc(self):
        self.mass=0
        for i in self.limbs:
            i.mass_calc()
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.inventory:
            self.movemass+=i.mass

    def on_strike(self):
        pass

    def on_struck(self):
        pass

class Material():
    pass
    def damageresolve(self,attack,attacker,reactionforce=False):
        self.reactionforce=reactionforce
        if attack.pressure==0:
            attack.rootarea=1
        else:
            attack.rootarea=(attack.force/attack.pressure)**0.5

        self.bruisable=True
        self.crushable=True
        damagedobject=attack.target
        basetarget=attack.basetarget
        if isinstance(attack.basetarget,Limb)==True:
            defenderstats=attack.basetarget.stats
        elif isinstance(attack.basetarget,Creature)==True:
            defenderstats=attack.basetarget.stats
        elif hasattr(attack.basetarget,'stats'):
            defenderstats=attack.basetarget.stats
        elif hasattr(attack.basetarget,'equipped'):
            defenderstats=attack.basetarget.equipped.stats
        else:
            defenderstats={'str':10,'tec':10,'per':10,'wil':10,'luc':10}
        self.m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)
        self.contact=False

        if self.mode=='brittle':
#Cutting
            self.cut(attack,attacker,damagedobject,defenderstats)

#Crushing
            self.crush(attack,attacker,damagedobject,defenderstats)

#Cracking, Breaking, and Shattering
            self.crack(attack,attacker,damagedobject,defenderstats)

#Piercing
            self.pierce(attack,attacker,damagedobject,defenderstats)

        elif self.mode=='soft':

#Cutting
            self.cut(attack,attacker,damagedobject,defenderstats)

#Crushing
            self.crush(attack,attacker,damagedobject,defenderstats)

#Piercing
            self.pierce(attack,attacker,damagedobject,defenderstats)

#Bruising
            self.bruise(attack,attacker,damagedobject,defenderstats)




        elif self.mode=='ductile':
#Cutting
            self.cut(attack,attacker,damagedobject,defenderstats)

#Crushing
            self.crush(attack,attacker,damagedobject,defenderstats)

#Piercing
            self.pierce(attack,attacker,damagedobject,defenderstats)

#Denting and bending. MUST COME LAST!
            self.dent(attack,attacker,damagedobject,defenderstats)




#Final resolution
        if self.contact==True:
            attack.contact=True
            attack.energy-=7*self.fracture_energy*1000*attack.rootarea*damagedobject.thickness
            attack.energy_recalc()
        else:
            attack.contact=False

    def bruise(self,attack,attacker,damagedobject,defenderstats):
        if attack.pressure>self.tensile_strength*300000 and self.bruisable==True:
            severity=((attack.force/(attack.force+1000))*attack.pressure/(self.tensile_strength*300000)-1)*random.gauss(0.5*attacker.stats['luc']/defenderstats['luc'],0.5)
            pythagoreanseverity=(severity**2+damagedobject.damage['bruise']**2)**0.5
            damagedobject.damage['bruise']=pythagoreanseverity

        pass

    def cut(self,attack,attacker,damagedobject,defenderstats):
        if attack.pressure==0:
            rootarea=1
        else:
            rootarea=(attack.force/attack.pressure)**0.5
        shearforce=1.5*attack.force*(1/(3.5*damagedobject.thickness*rootarea)-self.density*rootarea/(3.5*damagedobject.mass))
        if isinstance(attack.basetarget,Limb):
            shearforce=min(shearforce*(damagedobject.mass/attack.basetarget.movemass)**0.5,shearforce)
        if shearforce>self.shear_strength*1000000 and attack.contact==True and attack.type=='cut':
            severity=abs(random.gauss(((attack.force/(100*self.shear_strength+attack.force))*0.1/(self.shear_strength*damagedobject.thickness+0.1))
                                          *(attacker.stats['tec']+0.2*attacker.stats['luc'])/(defenderstats['luc']
                                            +0.2*defenderstats['tec']),0.4))
            damagedobject.damage['cut']=(damagedobject.damage['cut']**2+severity**2)**0.5
            if damagedobject.damage['cut']>=1: self.contact=True
            self.bruisable=False
            self.crushable=False
            attack.rootarea=rootarea
        return

    def crush(self,attack,attacker,damagedobject,defenderstats):
        if attack.force>(1-(damagedobject.damage['dent']+damagedobject.damage['crack']))*self.tensile_strength*(1200000-200000*random.triangular(low=0,high=1,mode=self.m))*damagedobject.length*damagedobject.radius and damagedobject.damage['crush']==0 and attack.contact==True and self.crushable==True:
                damagedobject.damage['crush']=1
                self.contact=True
                self.bruisable=False
        pass

    def crack(self,attack,attacker,damagedobject,defenderstats):
        hitloc=random.triangular(low=0.00001,high=1,mode=self.m)*damagedobject.length
        crackforce=min(attack.force*(damagedobject.mass/attack.basetarget.movemass)**0.5,attack.force)
        if crackforce>10*(1-damagedobject.damage['crack']**2)*(self.tensile_strength*1000000*damagedobject.r*damagedobject.thickness**2)/hitloc:
            severity=max(crackforce/(10*(1.00001-damagedobject.damage['crack']**2)*(self.tensile_strength*1000000*damagedobject.r*damagedobject.thickness**2)/hitloc),1)-1
            cracklength=damagedobject.damage['crack']**0.5+severity**0.5
            #Cracked but not broken
            if cracklength<1:
                damagedobject.damage['crack']+=severity


        #Broken but not shattered
            elif severity<3 and damagedobject.damage['break']==0:
                damagedobject.damage['crack']=1
                damagedobject.damage['break']=1
                if attack.contact==True:
                    self.contact=True


        #Shattered
            elif severity>=3 and damagedobject.damage['shatter']==0:
                damagedobject.damage['crack']=1
                damagedobject.damage['break']=1
                damagedobject.damage['shatter']=1
                if attack.contact==True:
                    self.contact=True


        if self.contact==True:
            attack.contact=True
            attack.energy-=7*self.fracture_energy*1000*attack.rootarea*damagedobject.thickness
            attack.energy_recalc()
        else:
            attack.contact=False
        pass

    def pierce(self,attack,attacker,damagedobject,defenderstats):
        if attack.pressure==0:
            rootarea=1
        else:
            rootarea=(attack.force/attack.pressure)**0.5
        shearforce=1.5*attack.force*(1/(3.5*damagedobject.thickness*rootarea)-self.density*rootarea/(3.5*damagedobject.mass))
        if isinstance(attack.basetarget,Limb):
            shearforce=min(shearforce*(damagedobject.mass/attack.basetarget.movemass)**0.5,shearforce)
        if shearforce>self.shear_strength*1000000 and attack.contact==True and attack.type=='pierce':
            severity=abs(random.gauss(((attack.force/(10*self.shear_strength+attack.force))*0.2/(self.shear_strength*damagedobject.thickness+0.1))
                                          *(attacker.stats['tec']+0.2*attacker.stats['luc'])/(defenderstats['luc']
                                            +0.2*defenderstats['tec']),0.4))
            damagedobject.damage['pierce']=(damagedobject.damage['pierce']**2+severity**2)**0.5
            if damagedobject.damage['pierce']>=0.3: self.contact=True
            self.bruisable=False
            self.crushable=False
            attack.rootarea=rootarea
        return

    def dent(self,attack,attacker,damagedobject,defenderstats):
        hitloc=random.triangular(low=0.00001,high=1,mode=self.m)*damagedobject.length
        dentforce=min(attack.force*(damagedobject.mass/attack.basetarget.movemass)**0.5,attack.force)
        #print(damagedobject.name,damagedobject.thickness,dentforce)
        if dentforce>0.05*(1-damagedobject.damage['dent']**2)*(self.shear_strength*1000000*damagedobject.r*damagedobject.thickness):
            if self.reactionforce==True:
                severity=max(0.002*dentforce/(0.05*(self.shear_strength*1000000*(damagedobject.r)**2*damagedobject.thickness)),1)-1
            else:
                severity=max(0.002*dentforce/(0.05*(self.shear_strength*1000000*damagedobject.r*damagedobject.thickness**2)),1)-1
            pythagoreanseverity=(damagedobject.damage['dent']**2+severity**2)**0.5
            #dented but not bent
            damagedobject.damage['dent']=pythagoreanseverity
            attack.force=attack.force*(1+severity)
            attack.pressure=attack.pressure*(1+severity)


        #bent but not crushed
            if severity>0.8 and damagedobject.damage['dent']>1:
                damagedobject.damage['bend']+=damagedobject.damage['dent']-1
                damagedobject.damage['dent']=1
                attack.force=attack.force*(1+damagedobject.damage['bend'])
                attack.pressure=attack.pressure*(1+damagedobject.damage['bend'])
                damagedobject.damage['bend']=min(damagedobject.damage['bend'],1)
                self.contact=True

    def on_turn(self):
        pass

    def on_strike(self):
        pass

    def on_struck(self):
        pass


#TODO: The self.equipped attribute of items should probably be a list, for those items which are on multiple body parts or are held in multiple hands.


class Item():
    def __init__(self,painfactor=1,**kwargs):
        self.location=[None,None]
        self.image='./images/Defaultitem.png'
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.breakcounter=0
        self.owner=None
        self.function=1
        self.equipped=None
        self.block=False
        self.parry=False
        self.painfactor=painfactor
        self.curvature=0
        self.attacks=[]
        self.passable=True
        self.hostile=[]
        self.targetable=False
        self.plural=False

    def recalc(self):
        '''This is configured for a cylindrical object. Non-cylindrical objects will need to modify this method
        '''
        self.material_import()
        if hasattr(self,'in_radius'):
            self.mass=self.density*(self.length*(self.radius**2-self.in_radius**2))*3.14
            self.thickness=self.radius-self.in_radius
        else:
            self.mass=self.density*self.length*(self.radius**2)*3.14
            self.thickness=self.radius
        self.r=self.thickness
        self.centermass=self.length/2
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.movemass=self.mass
        pass

    def damageresolve(self,attack,attacker,reactionforce=False):
        pain=self.painfactor*attack.basetarget.painfactor
        self.olddamage=self.damage.copy()
        self.material.damageresolve(attack,attacker,reactionforce=reactionforce)

#TODO: Need to pair down the amount of information reported on successful attack. Only the most significant injury should be reported

        attack.damage_dealt+=1

        if reactionforce==True:
            if attack.weapon is not None:
                name=attack.weapon.name
            elif attack.limb:
                name=attack.limb.name
            else:
                return
            reactiondamage=False
            for keys in self.olddamage:
                if self.olddamage[keys]<self.damage[keys]:
                    reactiondamage=True
            if reactiondamage==True and attack.reaction_damage_processed==False:
                messages.append("The attacker's {} is damaged!".format(name))
                attack.reaction_damage_processed=True

        if self.damage['crush']==0 and self.damage['bend']<1.12 and self.damage['break']==0 and self.damage['shatter']==0 and self.damage['cut']<1:
            if hasattr(self,'edge') or hasattr(self,'tip'):
                if attack.oldtype=='cut' or attack.oldtype=='crush':
                    if self.damage['dent']>0 and hasattr(self,'edge'):
                        self.edge=self.edge*(1+self.damage['dent'])**0.5
                        messages.append("The edge of the {} is dulled".format(self.name))
                        self.damage['dent']=0
                        return
                    if self.damage['crack']>self.olddamage['crack'] and hasattr(self,'edge'):
                        self.edge=self.edge*(1+self.damage['dent'])**0.5
                        messages.append("The edge of the {} is chipped".format(self.name))
                        return
                if attack.type=='stab' and reactionforce==True:
                    if self.damage['dent']>0:
                        self.tip=self.tip*(1+self.damage['dent'])**0.5
                        messages.append("The tip of the {} is dulled".format(self.name))
                        self.damage['dent']=0
                        return
                    if self.damage['crack']>0:
                        self.tip=self.tip*(1+self.damage['cracked'])**2
                        messages.append("The tip of the {} is chipped".format(self.name))
                        self.damage['crack']=0
                        return


        #test for crushing. If crushed, no other wounds need be recognized
        if self.damage['crush']>self.olddamage['crush']:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} is crushed!".format(self.name))
            if self.plural==True:
                messages.append("The {} are crushed!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*250*self.damage['crush']/attack.basetarget.owner.stats['wil']**0.5
            self.functioncheck()
            return

        #test for shattering. If shattered, no other wounds are significant
        if self.damage['shatter']>self.olddamage['shatter']:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} is shattered!".format(self.name))
            if self.plural==True:
                messages.append("The {} are shattered!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*250*self.damage['shatter']/attack.basetarget.owner.stats['wil']**0.5
            self.functioncheck()
            return
        elif self.damage['shatter']==1:
            self.functioncheck()
            return


        #test for cutting. If cut all the way through, no further wounds need be processed
        if self.damage['cut']>self.olddamage['cut']:
            attack.damage_dealt+=1
            if self.damage['cut']<0.2:
                statement='scratched'
            elif self.damage['cut']<0.4:
                statement='cut!'
            elif self.damage['cut']<1:
                statement='deeply cut!'
            else:
                statement='cut all the way through!'
            if self.plural==False:
                messages.append("The {} is {}".format(self.name,statement))
            if self.plural==True:
                messages.append("The {} are {}".format(self.name,statement))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*50*self.damage['cut']/attack.basetarget.owner.stats['wil']**0.5
            if self.damage['cut']>=1:
                self.functioncheck()
                return


        #test for piercing. Piercing renders bruising irrelevant
        if self.damage['pierce']>self.olddamage['pierce']:
            attack.damage_dealt+=1
            if self.damage['pierce']<0.2:
                statement='scratched'
            elif self.damage['pierce']<1:
                statement='pierced!'
                self.damage['cut']+=(self.damage['pierce'])*0.01/(0.01+self.thickness)
            else:
                statement='skewered!'
                self.damage['cut']+=(self.damage['pierce'])*0.01/(0.01+self.thickness)
            if self.plural==False:
                messages.append("The {} is {}".format(self.name,statement))
            if self.plural==True:
                messages.append("The {} are {}".format(self.name,statement))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*50*self.damage['pierce']/attack.basetarget.owner.stats['wil']**0.5



        #Test for bruising.
        if self.damage['bruise']>self.olddamage['bruise']:
            if self.damage['bruise']<4:
                if self.plural==False:
                    messages.append('The {} is bruised'.format(self.name))
                if self.plural==True:
                    messages.append('The {} are bruised'.format(self.name))
            elif self.damage['bruise']<7:
                if self.plural==False:
                    messages.append('The {} is badly bruised!'.format(self.name))
                if self.plural==True:
                    messages.append('The {} are badly bruised!'.format(self.name))
            elif self.damage['bruise']<10:
                if self.plural==False:
                    messages.append('The {} is severely bruised and swells with blood!'.format(self.name))
                if self.plural==True:
                    messages.append('The {} are severely bruised and swell with blood!'.format(self.name))
            elif self.damage['bruise']>=10:
                if self.plural==False:
                    messages.append('The structure of the {} collapses under the impact!'.format(self.name))
                if self.plural==True:
                    messages.append('The structure of the {} collapse under the impact!'.format(self.name))
                self.damage['crush']=1
            attack.damage_dealt+=1
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*5*min(self.damage['bruise'],10)/attack.basetarget.owner.stats['wil']**0.5


        #Test for bending. If bent, dents don't need to be mentioned and no material should both shatter and bend
        if self.damage['bend']>self.olddamage['bend']:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} is bent!".format(self.name))
            if self.plural==True:
                messages.append("The {} are bent!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*200*self.damage['bend']/attack.basetarget.owner.stats['wil']**0.5
            self.functioncheck()
            return
        elif self.damage['bend']==1:
            self.functioncheck()
            return

        #Test for denting. If dented, no cracking or shattering will occur
        if self.damage['dent']>self.olddamage['dent'] and self.olddamage['dent']==0:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} is dented!".format(self.name))
            if self.plural==True:
                messages.append("The {} are dented!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*100*self.damage['dent']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return
        elif self.damage['dent']>self.olddamage['dent']:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} is further dented!".format(self.name))
            if self.plural==True:
                messages.append("The {} are further dented!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*150*self.damage['dent']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return



        #test for breaking. If broken, further cracks are irrelevant
        if self.damage['break']>self.olddamage['break']:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} is broken!".format(self.name))
            if self.plural==True:
                messages.append("The {} are broken!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*175*self.damage['break']/attack.basetarget.owner.stats['wil']**0.5
            self.functioncheck()
            return
        elif self.damage['break']==1:
            self.functioncheck()
            return

        #test for cracks and update function accordingly
        if self.damage['crack']>self.olddamage['crack'] == 0:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} is cracked!".format(self.name))
            if self.plural==True:
                messages.append("The {} are cracked!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*100*self.damage['crack']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return
        elif self.damage['crack']>self.olddamage['crack']:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} cracks further!".format(self.name))
            if self.plural==True:
                messages.append("The {} crack further!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*100*self.damage['crack']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return
        self.functioncheck()
        attack.damage_dealt-=1

    def recover(self,stats,turns=1,**kwargs):
        if self.damage['bruise']>0:
            self.damage['bruise']-=min(self.damage['bruise'],self.damage['bruise']*random.random()*stats['luc']/200)
        if self.damage['crack']>0:
            self.damage['crack']-=min(self.damage['crack'],random.random()*stats['luc']/500)
        if self.damage['break']>0 and self.damage['shatter']==0:
            if stats['luc']>random.uniform(0,100):
                self.breakcounter+=1
            if self.breakcounter>100:
                self.damage['break']=0
                self.breakcounter=0
        if self.damage['shatter']>0:
            if stats['luc']>random.triangular(0,200,200):
                self.damage['shatter']=0
                self.damage['break']=1
                permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
        if self.damage['crush']>0:
            if stats['luc']>random.triangular(0,200,200):
                self.damage['crush']=0
                if self.material.mode=='soft':
                    self.damage['bruise']=20
                if self.material.mode=='brittle':
                    self.damage['break']=1
                if self.material.mode=='ductile':
                    self.damage['bend']=1
                permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
        if self.damage['cut']>0:
            if stats['luc']>random.uniform(0,100):
                self.damage['cut']-=min(self.damage['cut'],self.damage['cut']*random.random()*stats['luc']/100)
        self.functioncheck()

    def on_equip(self):
        pass

    def on_turn(self):
        pass

    def on_strike(self):
        pass

    def on_struck(self):
        pass

    def functioncheck(self):
        if self.damage['shatter']+self.damage['crush']+self.damage['break']+self.damage['bend']>=1:
            self.function=0
        else:
            self.function=1-self.damage['crack']-0.9*self.damage['dent']-self.damage['bruise']/20-self.damage['cut']-self.damage['deform']-0.7*self.damage['pierce']
        if isinstance(self.equipped,Limb):
            if self.function<=0:
                if self.equipped.attachpoint:
                    self.equipped.attachpoint.unequip(self.wield,destroyed=True)
                if self.equipped is not None:
                    self.equipped.unequip(self.wield,destroyed=True)

    def material_import(self):
        self.youngs=self.material.youngs
        self.density=self.material.density
        self.shear=self.material.shear
        self.tensile_strength=self.material.tensile_strength
        self.shear_strength=self.material.shear_strength
        self.mode=self.material.mode
        self.damagetype=self.material.damagetype
        self.dissipationfactor=self.material.dissipationfactor

class Floor(Screen):
    def __init__(self,name,max_x=60,max_y=60,*args,**kwargs):
        super().__init__(name=name,**kwargs)
        floors[str(name)]=self
        self.cells={}
        self.dimensions=[max_x,max_y]
        self.nonindexedcells=[]
        self.creaturelist=[]
        for i in range(0,max_x):
            self.cells[i]={}
            for j in range(0,max_y):
                self.cells[i][j]=Cell(size=(cellsize,cellsize),pos=(i*cellsize,j*cellsize))
                self.cells[i][j].location=[i,j]
                self.cells[i][j].open=False
                self.cells[i][j].probability=0
                self.add_widget(self.cells[i][j])
                self.nonindexedcells.append(self.cells[i][j])
        dungeonmanager.add_widget(self)
        dungeonmanager.size=(max_x*cellsize+1,max_y*cellsize+1)
        for i in range(0,max_x):
            for j in range(0,max_y):
                self.cells[i][j].immediate_neighbors=[]
    
    #stuff to the right
                if i+1 in range (0,max_x):
                    if j+1 in range (0,max_y):
                        self.cells[i][j].immediate_neighbors.append(self.cells[i+1][j+1])
                    self.cells[i][j].immediate_neighbors.append(self.cells[i+1][j])
                    if j-1 in range(0,max_y):
                        self.cells[i][j].immediate_neighbors.append(self.cells[i+1][j-1])
    #stuff to the left
                if i-1 in range(0,max_x):
                    self.cells[i][j].immediate_neighbors.append(self.cells[i-1][j])
                    if j+1 in range (0,max_y):
                        self.cells[i][j].immediate_neighbors.append(self.cells[i-1][j+1])
                    if j-1 in range(0,max_y):
                        self.cells[i][j].immediate_neighbors.append(self.cells[i-1][j-1])
    #straight above
                if j+1 in range(0,max_y):
                    self.cells[i][j].immediate_neighbors.append(self.cells[i][j+1])
    #and straight below
                if j-1 in range(0,max_y):
                    self.cells[i][j].immediate_neighbors.append(self.cells[i][j-1])
    #And now next-nearest neighbors (with corners. May want to remove)
        for i in self.nonindexedcells:
            i.second_order_neighbors=[]
            for j in i.immediate_neighbors:
                i.second_order_neighbors.extend(j.immediate_neighbors)
            i.second_order_neighbors=set(i.second_order_neighbors)-set(i.immediate_neighbors)- {i}
    
        FloorGen.experimental_automaton(self)
        for i in self.nonindexedcells:
            i.on_contents(None,None)



    def place_creature(self,creature,location=[0,0],retry='random'):
        attempts=0
        placed=False
        attempted_location=location
        if retry=='random':
            while placed==False:
                if self.cells[attempted_location[0]][attempted_location[1]].passable==True:
                    creature.location=attempted_location
                    self.cells[attempted_location[0]][attempted_location[1]].contents.append(creature)
                    placed=True
                attempted_location=[random.randint(0,self.dimensions[0]-1),random.randint(0,self.dimensions[1]-1)]
        elif retry=='near':
            while placed==False:
                if self.cells[attempted_location[0]][attempted_location[1]].passable==True:
                    creature.location=attempted_location
                    self.cells[attempted_location[0]][attempted_location[1]].contents.append(creature)
                    placed=True
                for i in self.cells[attempted_location[0]][attempted_location[1]].immediate_neighbors:
                    if i.passable:
                        self.place_creature(creature,i.location)
                        return
                attempted_location=random.choice(self.cells[attempted_location[0]][attempted_location[1]].immediate_neighbors).location
                attempts+=1
                if attempts>=20:
                    print('could not place {}'.format(creature.name))
                    return


        pass

    def place_item(self,item):
        pass

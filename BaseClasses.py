__author__ = 'Alan'

from UI_Elements import *

import kivy
import random
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics.fbo import Fbo
from kivy.graphics import Canvas
from kivy.properties import ObjectProperty
import Shell
import Attacks as A
import Contamination
import re
import Items
import copy




def inventoryadd(item):
    print('{} added to inventory'.format(item))

def get_line(start,stop):
    x1,y1=start
    x2,y2=stop

    coordinateswitch=False
    if abs(y2-y1)>abs(x2-x1):
        x1,y1=y1,x1
        x2,y2=y2,x2
        coordinateswitch=True

    pointswitch=False
    if x1>x2:
        x1,x2=x2,x1
        y1,y2=y2,y1
        pointswitch=True

    dx=x2-x1
    dy=y2-y1

    try: slope=dy/dx
    except ZeroDivisionError: slope=1000
    if slope>0:
        sign=1
    else: sign=-1
    points=[]

    for x in range(0,dx+1):
        y=int(y1+slope*x+0.5)
        if coordinateswitch==True:
            point=(y,x+x1)
        else:
            point=(x+x1,y)
        points.append(point)

    if pointswitch:
        points.reverse()
    return points







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


class Limb():
    def __init__(self,stats,natural=True,color=(1,1,1,1),owner=None,*args,**kwargs):
        self.sortingtype='misc'
        self.inventory_index=None
        self.can_attack=True
        self.enchantments=[]
        self.target_class=[]
        self.kills=[]
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
        self.floor=None
        self.vision_blocking=False
        self.color=color
        self.passable=True
        self.targetable=False
        self.hostile=[]
        self.visual_acuity=1
        self.smell_acuity=1
        self.hearing_acuity=1
        self.staminacost=0
        self.focuscost=0
        self.armor=None
        self.limbs=[]
        self.inoperable=False
        self.primaryequip=[]
        self.attacks=[]
        self.descriptor=''
        self.note=''
        self.coverage=1

    def youngscalc(self):
        if self.layers==[]:
            return
        self.I=0
        shearsum=0
        shear=0
        totalcross=0
        layersum=0
        i=len(self.layers)-1
        j=0
        masssum=0
        ltotal=0
        limbmass=self.mass
        if self.armor is not None:
            self.I+=self.armor.I
            shear=self.armor.shear
            layersum+=self.armor.thickness/self.armor.material.youngs
            masssum+=self.armor.mass
            ltotal+=self.armor.thickness
            limbmass=self.mass+self.armor.mass
            totalcross+=(self.armor.radius**2-self.armor.in_radius**2)*3.14
            shearsum+=self.armor.shear*(self.armor.radius**2-self.armor.in_radius**2)*3.14
        while i>=0: # and j<3:
            layersum+=(self.layers[i].thickness/self.layers[i].material.youngs)*(1-masssum/limbmass)+10**-20
            masssum+=self.layers[i].mass
            ltotal+=self.layers[i].thickness
            layercross=(self.layers[i].radius**2-self.layers[i].in_radius**2)*3.14
            totalcross+=layercross
            shearsum+=layercross*self.layers[i].shear
            i-=1
            j+=1
        if shear==0 and self.layers!=[]:
            shear=self.layers[len(self.layers)-1].shear
        self.youngs=ltotal/layersum
        self.shear=shear
        #self.shear=shearsum/totalcross
        self.cross_section=totalcross
        self.thickness=ltotal*2
        if self.armor is not None:
            layersum=0
            i=len(self.layers)-1
            j=0
            masssum=0
            ltotal=0
            limbmass=self.mass
            while i>=0: # and j<3:
                layersum+=(self.layers[i].thickness/self.layers[i].material.youngs)*(1-masssum/limbmass)
                masssum+=self.layers[i].mass
                ltotal+=self.layers[i].thickness
                layercross=(self.layers[i].radius**2-self.layers[i].in_radius**2)*3.14
                totalcross+=layercross
                shearsum+=layercross*self.layers[i].shear
                i-=1
                j+=1
            self.arpen_youngs=ltotal/layersum
            self.arpen_shear=self.layers[len(self.layers)-1].shear
        else:
            self.arpen_youngs=self.youngs
            self.arpen_shear=self.shear
        self.I+=sum(i.I for i in self.layers)

    def damageresolve(self,attack,attacker,reactionforce=False):
        i=len(self.layers)-1
        f=attack.force
        pressure=attack.pressure
        if attack.weapon==None:
            aweapon=attack.limb
        else:
            aweapon=attack.weapon
        if pressure==0:
            area=1
        else:
            area=attack.force/pressure
        mass=self.mass
        if self.armor is not None:
            mass=self.mass+self.armor.mass

            if attack.penetrate==False:
                attack.touchedobjects.append(self.armor)
                oldarea=area
                attack.target=self.armor
                f-=f*self.armor.mass/mass
                    #area=area+(self.armor.material.shear**0.7)*(3.54*self.armor.thickness*area**0.5+3.14*self.armor.thickness**2)
                #area+=max((self.armor.function)*((self.armor.shear*attack.reducedmass*(self.armor.thickness/self.armor.youngs+aweapon.thickness/aweapon.youngs)/self.armor.density)**1.5)/area**1.5,0)*(random.random()+0.1)/(1+pressure/(500000000*self.armor.youngs))
                #area=max(min(area,self.armor.radius*self.armor.length),oldarea)
                #pressure-=2*self.armor.yield*(1-self.armor.poissons)/(1-2*self.armor.poissons)
                #pressure=(pressure*area**1.5)/(self.armor.yeild_strength*self.armor.thickness**3)
                layer=self.layers[len(self.layers)-1]
                armor=self.armor
                pressure=(self.armor.youngs)*(pressure*area)/(3*self.armor.shear*(self.armor.thickness*armor.function+area**0.5)**2)
                pressure=(pressure*2*(layer.density*layer.youngs)**0.5)/((layer.density*layer.youngs)**0.5+(armor.density*armor.youngs)**0.5)
                #pressure=f/area
                self.armor.damageresolve(attack,attacker,reactionforce=reactionforce)
                attack.force=f
                attack.pressure=max(pressure,f/(2*layer.radius*layer.length))
                if self.armor is not None:
                    if self.armor.damage['dent']>self.armor.olddamage['dent'] or self.armor.damage['bend']>self.armor.olddamage['bend']:
                        attack.pressure=self.armor.damage['dent']*attack.pressure
                    else:
                        attack.pressure=pressure

                if attack.contact==False and self.armor is not None:
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
                        #print("failed at layer",i)
                        #self.layers[i].damageresolve(attack,attacker,reactionforce=reactionforce)
                        i=-1
                        break
            pre_contact=attack.contact
            self.layers[i].damageresolve(attack,attacker,reactionforce=reactionforce)


            if self.layers[i].material.mode=='soft':
                softnessfactor=0.3
            else:
                softnessfactor=1

            if random.random()>self.layers[i].coverage and pre_contact==True:
                attack.contact=True
            elif attack.contact==False:
                f-=(self.layers[i].function/2+0.5)*softnessfactor*f*self.layers[i].mass/mass
                #area=area+(3.54*self.layers[i].thickness*area**0.5+3.14*self.layers[i].thickness**2)*(self.layers[i].material.shear**0.7)/softnessfactor
                if attack.weapon==None:
                    aweapon=attack.limb
                else:
                    aweapon=attack.weapon
                #area+=0.5*((self.layers[i].shear*attack.reducedmass*(self.layers[i].thickness/self.layers[i].youngs+aweapon.thickness/aweapon.youngs)/self.layers[i].density)**1.5)/area**2
                if self.layers[i].damage['crush']==0:
                    #oldarea=area
                    #area+=max((self.layers[i].function)*0.5*((self.layers[i].shear*attack.reducedmass*(self.layers[i].thickness/self.layers[i].youngs+aweapon.thickness/aweapon.youngs)/self.layers[i].density)**1.5)/area**1.5,0)*(random.random()+0.1)/(1+pressure/(500000000*self.layers[i].youngs))
                    #area=max(min(area,self.layers[i].radius*self.layers[i].length),oldarea)
                    pressure=attack.pressure
                    area=attack.area
                    layer=self.layers[i]
                    try: newlayer=self.layers[i-1]
                    except KeyError: newlayer=self.layers[i]
                    pressure=(layer.youngs)*(pressure*area)/(3*layer.shear*(layer.thickness*layer.function+area**0.5)**2)
                    pressure=(pressure*2*(newlayer.density*newlayer.youngs)**0.5)/((newlayer.density*newlayer.youngs)**0.5+(layer.density*layer.youngs)**0.5)
                    assert type(pressure)!=complex,(pressure,area,self,self.owner)
                    attack.pressure=max(pressure,f/(2*newlayer.radius*newlayer.length))
                    attack.area+=(layer.thickness*layer.function)**2
            if attack.contact==True:
                attack.touchedobjects.append(self.layers[i])
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

    def unequip(self,slot,cascade=False,destroyed=False,drop=False,log=True):
        if not slot in self.equipment:
            if cascade==False:
                #print("no {} on {}".format(slot,self.name))
                pass
            return
        if slot=='grasp':
            self.attacks=self.defaultattacks
        if self.equipment[slot] is not None:
            print(self.equipment[slot],self.equipment[slot].equipped)
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
            if self.equipment[slot] in self.owner.equipped_items and self.equipment[slot].equipped==[self]:
                self.owner.equipped_items.remove(self.equipment[slot])
            try: self.equipment[slot].equipped.remove(self)
            except ValueError: self.equipment[slot].equipped=[]
            self.equipment[slot]=None
            try: self.armor=self.equipment[self.armortype]
            except KeyError: self.armor=None
            if self.limbs:
                for i in self.limbs:
                    i.unequip(slot,cascade=True)
        self.youngscalc()

    def updateability(self):
        self.ability=1
        for i in self.layers:
            i.functioncheck()
            self.ability=min(self.ability,i.function)
        self.ability=max(self.ability,0)
        if hasattr(self,'dexterity'):
            self.dex_calc()
        #if hasattr(self.attachpoint,'dexterity'):
        #    self.attachpoint.dex_calc()
        if hasattr(self,'balance'):
            self.balance_calc()
        #if hasattr(self.attachpoint,'balance'):
        #    self.attachpoint.balance_calc()
        if hasattr(self,'vision'):
            self.vision_calc()
        if hasattr(self,'smell_sense'):
            self.smell_calc()
        if hasattr(self,'hearing'):
            self.hearing_calc()

    def sever(self, primary=True):
        if hasattr(self,'equipped') and self.equipped!=[]:
            return
        for i in self.equipment:
            if self.equipment[i] is not None:
                if self.equipment[i].wield in self.primaryequip and self in self.equipment[i].equipped:
                    if self.equipment[i].equipped==[self]:
                        self.unequip(i,drop=True,log=False)
                    else: self.unequip(i,drop=False,log=False)
                else:
                    self.unequip(i,drop=False,log=False)
        if primary:
            if self.natural==True: self.owner.missing_limbs.append(copy.copy(self))
            self.owner.pain+=75*self.painfactor
            messages.append("{}'s {} is severed from the body!".format(self.owner.name,self.name))
            if self.attachpoint:
                if self not in self.attachpoint.limbs:
                    print("Tried to remove {}'s {} from {} and failed".format(self.owner.name,self.name,self.attachpoint.name))
                    print(self.attachpoint.limbs)
                else: self.attachpoint.limbs.remove(self)
            if self.owner.location is not None:
                self.location[0]=min(max(self.owner.location[0]+int(random.gauss(0,2)),0),Shell.shell.dungeonmanager.current_screen.dimensions[0])
                self.location[1]=min(max(self.owner.location[1]+int(random.gauss(0,2)),0),Shell.shell.dungeonmanager.current_screen.dimensions[1])
                try:
                    Shell.shell.dungeonmanager.current_screen.cells[self.location[0]][self.location[1]].contents.append(self)
                except KeyError:
                    Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]].contents.append(self)
            self.on_destruction()
        if self.owner and self in self.owner.limbs:
            self.owner.limbs.remove(self)
        for i in self.layers:
            i.function=0
        self.attacks=[A.Strike_1H,A.Strike_2H]
        self.wield='grasp'
        self.equipped=[]
        self.block=False
        self.parry=False

        for i in self.limbs:
            i.sever(primary=False)

    def recover(self,turns=1,fullheal=False,**kwargs):
        for i in self.layers:
            if i.function<1:
                i.recover(self.stats,fullheal=fullheal)
        self.updateability()
        if self.inoperable==True:
            self.ability=0

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
        self.movemass=self.mass
        for i in self.primaryequip:
            if self.equipment[i] is not None:
                self.movemass+=self.equipment[i].mass
        for i in self.limbs:
            self.movemass+=i.movemass

    def on_turn(self,turns=1,**kwargs):
        if self.owner is not None and self in self.owner.limbs:
            if self.ability<1:
                self.recover(turns=turns,**kwargs)
            if self.ability>0 and self.owner is not None:
                for i in self.attacks:
                    if i.sig in self.owner.disabled_attacks:
                        i.disabled=True
                    if i.weapon==None:
                        self.owner.attacks.append(i)
                    elif not hasattr(i.weapon,'equipped'):
                        self.owner.attacks.append(i)
                    elif len(i.weapon.equipped)==1 and i.hands==1:
                        self.owner.attacks.append(i)
                    elif len(i.weapon.equipped)>1 and i.hands>1:
                        if not any((i.weapon.equipped,i.name)==(j.weapon.equipped,j.name) for j in self.owner.attacks):
                            self.owner.attacks.append(i)
        self.process_coatings()
        for i in self.enchantments:
            i.on_turn()

    def on_strike(self,attack):
        for i in self.enchantments:
            i.on_strike(attack)
        pass

    def on_struck(self,attack):
        self.owner.on_struck(attack)
        for i in self.enchantments:
            i.on_struck(attack)
        pass

    def on_destruction(self):
        for i in self.enchantments:
            i.on_destruction()

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

    def describe_damage(self):
        self.damagemessage=''
        for i in self.layers:
            self.damagemessage=''.join((self.damagemessage,i.describe_damage(title=''.join(('The ',i.name)))))
        return self.damagemessage

    def can_equip(self,item,override=False):
        if override==True:
            return (True,True)
        if item.wield not in self.primaryequip:
            return (False,True)
        if item.wield=='grasp' and self.grasp:
            return (True,True)
        if not hasattr(item,'in_radius'):
            return (False,True)
        if self.radius<0.5*item.in_radius:
            return (False,'size conflict')
        if self.radius>2*item.in_radius:
            return (False,'size conflict')
        else:
            return (True,True)

    def generate_descriptions(self,per=0):
        pass

    def process_coatings(self):
        for i in self.layers:
            i.process_coatings(self)

    def burn(self,temp,intensity,log=True,with_armor=True,**kwargs):
        message=''

        if self.armor is not None and with_armor==True:
            new=self.armor.burn(temp,intensity,in_limb=True,limb=self)
            newmessage=new[0]
            temp=new[1]
            intensity=new[2]
            message=''.join((message,newmessage))
            print(temp,intensity)
        for i in reversed(self.layers):
            old_damage=i.damage.copy()
            new=i.burn(temp,intensity,in_limb=True,limb=self)
            newmessage=new[0]
            temp=new[1]
            intensity=new[2]
            message=''.join((message,newmessage))
            for j in ['burn','bend','dent','deform']:
                try: self.owner.pain+=(i.damage[j]-old_damage[j])*150*self.painfactor*i.painfactor/self.stats['wil']**0.5
                except AttributeError: pass
                except KeyError: pass
        if message!='' and log==True: messages.append(message)
        self.updateability()

    def add_outer_layer(self,itemtype,material,thickness,name=None,plural=False,quality=1,threshold=0,**kwargs):
        if name==None:
            self.layers.append(itemtype(length=self.length,in_radius=self.radius,out_radius=self.radius+thickness,material=material,plural=plural,quality=quality,threshold=threshold,**kwargs))
        else:
            self.layers.append(itemtype(length=self.length,in_radius=self.radius,out_radius=self.radius+thickness,material=material,name=name,plural=plural,quality=quality,threshold=threshold,**kwargs))
        self.radius+=thickness
        self.mass_calc()
        pass

    def join_to(self,target):
        self.attachpoint=target
        target.limbs.append(self)

class Creature():
    def __init__(self,**kwargs):
        self.basicname=''
        self.attacked=False
        self.enchantments=[]
        self.kills=[]
        self.location=[None,None]
        self.floor=None
        self.vision_blocking=False
        self.visible_cells=[]
        self.missing_limbs=[]
        self.alive=True
        self.tension=0
        self.pain=0
        self.oldpain=0
        self.recoverytime=0
        self.reach=0.01
        self.combataction=False
        self.can_grasp=False
        self.can_walk=False
        self.can_see=False
        self.can_smell=False
        self.can_hear=False
        self.feels_pain=True
        self.seen_by_player=False
        self.action_queue=[]
        self.balance=0
        self.vision=0
        self.hearing=0
        self.smell_sense=0
        self.esp=0
        self.iprefs={'mass':-1,'length':1,'edge':1,'tip':1,'I':-1,'quality':1,'thickness':1,'type':[],'material':[],'collection threshold':5,'weight threshold':170}
        self.item_values={}
        self.equipped_items=[]
        self.inventory=[]
        self.conditions=[]
        self.balance_recovery=0
        self.classification=[]
        self.hostile=[]
        self.target=None
        self.target_preference='random'
        self.preference_enforcement=False
        self.disabled_attack_types=[]
        self.disabled_attacks=[]
        self.magic_contamination={'dark':0,'elemental':0,'summoning':0,'transmutation':0,'arcane':0,'total':0}
        self.descriptor=''
        self.note=''

    def updateattacks(self):
        self.reach=0.01
        for i in self.attacks:
            if i.disabled==True and i.sig not in self.disabled_attacks:
                disabled_attack=i.sig
                self.disabled_attacks.append(disabled_attack)
        self.attacks=[]
        for i in self.limbs:
            if i.ability>0 and i.can_attack==True:
                for j in i.attacks:
                    if j.sig in self.disabled_attacks: #(j.name,j.limb,j.weapon)
                        j.disabled=True
                    if j.weapon is not None and hasattr(j.weapon,'equipped'):
                        hands=len(j.weapon.equipped)
                    else:
                        hands=1
                    try:
                        j.test_usability(hands)
                    except TypeError:
                        j.test_usability()
                    if j.useless==False and any(type(j)is k for k in self.disabled_attack_types)==False and j.disabled==False:
                        self.attacks.append(j)
                        self.reach=max(self.reach,j.strikelength)
                    elif j.useless==False:
                        self.reach=max(self.reach,j.strikelength)

    def on_turn(self,turns=1):
        if self.location==[None,None]:
            return
        for i in self.inventory:
            i.on_turn()
        for i in self.enchantments:
            i.on_turn()

        self.survivalcheck()

        if self.alive==True:
            self.recoverytime=0

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
                self.stamina[0]+=int(max(self.stats['str']**0.8-self.movemass/(self.stats['str']**1.5),0))+1
                self.stamina[0]=min(self.stamina[0],self.stamina[1])
                self.stamina[0]=max(0,self.stamina[0])
                if self.combataction==False:
                    self.focus[0]+=int((self.focus[1]-self.focus[0])*self.stats['per']*self.stamina[0]/(100*self.stamina[1]))+1
            self.attacked=False
            self.combataction=False





        #If alive, recover, and test for senses
            for i in self.attacks:
                if i.disabled==True and i.sig not in self.disabled_attacks:
                    self.disabled_attacks.append(i.sig)
            self.sense_awareness()
            self.attacks=[]
            for i in self.limbs:
                i.on_turn()
            for i in self.attacks:
                if i.sig in self.disabled_attacks:
                    i.disabled=True






        #Test for pain-related loss of focus or incapacitation
            if self.feels_pain==True:
                if self.pain<=self.oldpain:
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
                self.oldpain=self.pain
            else: self.pain=0


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
                self.choose_action()

            total_contamination=-self.magic_contamination['total']
            for keys in self.magic_contamination:
                total_contamination+=self.magic_contamination[keys]
            self.magic_contamination['total']=total_contamination

    def survivalcheck(self):
        if self.alive==False: return
        if self.limbs==[]:
            self.die()
            return
        for i in self.vitals:
            if i.function==0:
                self.die()
                return

    def equip(self,item,log=True):
        item.in_inventory=self
        for i in self.limbs:
            if item.wield in i.equipment and item.wield in i.primaryequip:
                if i.equipment[item.wield] is None and item.equipped==[]:
                    i.equip(item)
                    if i in item.equipped:
                        if item.wield=='grasp' and log==True:
                            messages.append("{} is now held in {}".format(item.name,i.name))
                        elif log==True:
                            messages.append("{} is now equipped on {}".format(item.name,i.name))
                        self.updateattacks()
                        self.mass_calc()
                        return
                if i.equipment[item.wield] is None and item.wield=='grasp' and len(item.equipped)>0:
                    i.equip(item)
                    if log==True:
                        Shell.shell.log.addtext("{} is now also held in {}".format(item.name,i.name))
                    self.updateattacks()
                    self.mass_calc()
                    return
        self.mass_calc()

    def unequip(self,item,log=True,drop=False):

        for i in self.limbs:
            if hasattr(item,'wield') and item.wield in i.equipment:
                if i.equipment[item.wield]==item:
                    i.unequip(item.wield,log=log,drop=drop)

    def die(self):
        #self.targetable=False
        self.alive=False
        self.hostile=[]
        self.passable=True
        items_to_drop=[]
        messages.append("{} has been slain!".format(self.name))
        if self.player==True:
            messages.append("YOU HAVE DIED!")
        for i in self.inventory:
            self.unequip(i,log=False)
            items_to_drop.append(i)
        for i in items_to_drop:
            i.equipped=[]
            self.inventory.remove(i)
            Shell.shell.dungeonmanager.current_screen.cells[self.location[0]][self.location[1]].contents.append(i)

    def choose_action(self):
        #If no target, choose a target
        if self.target!=None and self.target not in self.visible_creatures:
            self.target=None
        if self.target!=None and self.target.alive==False:
            self.target=None
        if self.target==None:
            potential_targets=[]
            for i in self.visible_creatures:
                if A.hostilitycheck(self,i) and i.alive:
                    potential_targets.append(i)
            if potential_targets!=[]:
                self.target=random.choice(potential_targets)
        #If we have a target and it is visible, chase and kill
        if self.target!=None and self.target in self.visible_creatures:
            self.chase(self.target)
            return
        #Follow steps in the action queue if they exist
        if self.action_queue!=[]:
            instructions=self.action_queue.pop(0)
            if instructions[0]=='unequip':
                #format is command, item, current equipment location
                if self in Shell.shell.player.visible_creatures:
                    self.unequip(instructions[1],log=True)
                else:
                    self.unequip(instructions[1],log=False)
            elif instructions[0]=='equip':
                #format is command, item, limb
                instructions[2].equip(instructions[1])
                if self in Shell.shell.player.visible_creatures:
                    messages.append("{} equips {}".format(self.name,instructions[1].name))

        #If we are not in combat, maybe we should pick up some items
        #take inventory of surrounding items
        for i in self.visible_items:
            if isinstance(i,Item) or isinstance(i,Limb): pass
            else: break
            self.value_item(i)
            if hasattr(i,'wield') and self.movemass+i.mass<self.iprefs['weight threshold']:
                #See if it outvalues what we currently have equipped
                for j in self.limbs:
                    if i.wield in j.primaryequip:
                        if j.equipment[i.wield]==None or self.item_values[i]>self.item_values[j.equipment[i.wield]]:
                            #If we are standing on it, pick it up
                            if i.location==self.location:
                                self.inventory_add(i)
                                self.floor.cells[self.location[0]][self.location[1]].contents.remove(i)
                                i.location=[None,None]
                                if j.equipment[i.wield]!=None:
                                    self.action_queue.append(['unequip',j.equipment[i.wield],j])
                                self.action_queue.append(['equip',i,j])
                            else: self.chase(i)
                            return

        #Even if it's useless for us, take it if it is above collection threshold but won't put us over weight
            if self.movemass+i.mass<self.iprefs['weight threshold'] and self.item_values[i]>self.iprefs['collection threshold']:
                if i.location==self.location:
                    self.inventory_add(i)
                    self.floor.cells[self.location[0]][self.location[1]].contents.remove(i)
                    i.location=[None,None]
                else: self.chase(i)
                return



        self.wander()

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
        accuracy=1
        if self.target_preference=='random':
            pref='limb'
        elif self.target_preference=='vital organs':
            pref='vital'
        elif self.target_preference=='nonvital organs':
            pref='nonvital'
        elif self.target_preference=='attacking limbs':
            pref='attacking'
        elif self.target_preference=='ambulatory limbs':
            pref='moving'
        elif self.target_preference=='grasping limbs':
            pref='grasping'
        elif self.target_preference=='sensory organs':
            pref='sensory'
        elif self.target_preference=='balancing limbs':
            pref='balancing'

        while endattack==False:
            accuracy=1+(len(self.attacks)-len(unusable_attacks))/10
            hit_location=A.targetchoice(target)
            if hit_location is None:
                return
            attempts=0
            while pref not in hit_location.target_class and attempts<self.stats['tec']:
                retargeted=False
                for i in target.conditions:
                    if incapacitate.search(i):
                        hit_location=A.targetchoice(target)
                        retargeted=True
                if hit_location.ability<=0 and 'vital' not in hit_location.target_class:
                    if random.random()*self.stats['tec']>random.random()*(target.stats['per']**0.3)*(target.stats['luc']**0.3):
                        hit_location=A.targetchoice(target)
                        retargeted=True
                if random.random()*self.stats['tec']<random.random()*(target.stats['per']**0.3)*(target.stats['luc']**0.3) and retargeted==False:
                    break
                if retargeted==False:
                    hit_location=A.targetchoice(target)
                    accuracy=accuracy*0.9
                attempts+=1
            if self.preference_enforcement==True and pref not in hit_location.target_class:
                if not any(pref in i.target_class for i in target.limbs) and self.player==True:
                    messages.append('The target does not have any limbs matching your targeting preference')
                elif self.player==True:
                    messages.append('You cannot find an opening to attack your preferred target')
                return
            for i in self.attacks:
                if i.weapon==atk[attacksmade].weapon or i.limb==atk[attacksmade].limb:
                    unusable_attacks.append(i)
            if self.player==True:
                messages.append('You attack {} in the {} with {}'.format(target.name,hit_location.name,atk[attacksmade].name))
                atk[attacksmade].do(hit_location,accuracy=accuracy)
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

    def evasion(self,attack,blockable=True,dodgeable=True,parryable=True):
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


        reactiontime=(1/(self.stats['per'])**0.5)*random.gauss(1-(self.stats['luc']**0.5)/100,0.2)*random.gauss((self.focus[1]/max(self.focus[0],1)),0.1)+self.recoverytime

        #Test to see if target can see or hear the attacker. If not, suffer a large penalty to reaction ability.
        if attack.attacker.stats['tec']*random.random()>self.vision:
            if attack.attacker.stats['tec']>self.hearing*random.random():
                reactiontime=reactiontime*(1+(40-self.esp)/self.stats['per'])

        if attack.time<reactiontime or "off_balance" in self.conditions:
            attack.damagefactor=attack.attacker.stats['tec']**0.5
            messages.append('The attack takes {} completely unaware!'.format(self.name))
            return

        #Attempt to dodge
        dodgetime=reactiontime+((self.focus[1]/(1+self.focus[0]))**0.5)*random.gauss(3/(self.stats['tec']*self.stats['luc']**0.5),.01)*(self.movemass**1.2/(self.stats['str']*max(self.stamina[0],1)/self.stamina[1]))*1.5*attack.accuracy*self.targetsize/(7*self.balance+0.01)
        if dodgetime<attack.time and random.random()*attack.attacker.stats['tec']<0.8*random.random()*self.stats['per'] and dodgeable==True:
            attack.dodged=True
            self.stamina[0]-=2*attack.basetarget.movemass/attack.basetarget.stats['str']
            print("Attach dodged. Attack time of {} and dodge time of {}".format(attack.time,dodgetime))
            return

        #Attempt to block
        for i in self.equipped_items:
            if i.block==True and blockable==True:
                encumbrance=0.1*(self.movemass-self.mass)/self.stats['str']
                if len(i.equipped)==1:
                    if i.equipped[0].attachpoint is not None:
                        basemass=i.equipped[0].attachpoint.movemass+encumbrance
                        strength=i.equipped[0].attachpoint.stats['str']*self.stamina[0]/(self.stamina[1]+1)
                    else:
                        basemass=i.equipped[0].movemass+encumbrance
                        strength=i.equipped[0].stats['str']*self.stamina[0]/(self.stamina[1]+1)
                    tec=i.equipped[0].stats['tec']*self.focus[0]/(self.focus[1]+1)
                    blocktime=reactiontime+0.5*(self.targetsize/7)*attack.accuracy*((self.focus[1]/(self.focus[0]+1))**0.4)*random.gauss(1/(self.stats['luc']**0.5),.1)*(2*i.mass/strength**2+1/(tec*i.radius+0.5)**2+1/(tec/(2*i.mass+basemass*0.5)+1.57*strength*i.radius**2))
                elif len(i.equipped)>1:
                    basemass=0
                    strength=0
                    tec=0
                    for j in i.equipped:
                        if j.attachpoint is not None:
                            basemass+=j.attachpoint.movemass+encumbrance
                            strength+=j.attachpoint.stats['str']*self.stamina[0]/(self.stamina[1]+1)
                        else:
                            basemass+=j.movemass+encumbrance
                            strength+=j.stats['str']*self.stamina[0]/(self.stamina[1]+1)
                        tec+=j.stats['tec']*self.focus[0]/(self.focus[1]+1)
                    blocktime=reactiontime+0.5*(self.targetsize/7)*attack.accuracy*((self.focus[1]/(self.focus[0]+1))**0.4)*random.gauss(1/(self.stats['luc']**0.5),.1)*(2*i.mass/strength**2+1/(tec*i.radius+0.5)**2+1/(tec/(2*i.mass+basemass*0.5)+1.57*strength*i.radius**2))

                #print("{} block time is {}. Blocking attack of time {}".format(i.name,blocktime,attack.time))
                if blocktime<attack.time and random.random()*attack.attacker.stats['tec']<random.random()*self.stats['per']:
                    attack.blocked=True
                    attack.target=i
                    attack.basetarget=i
                    self.stamina[0]-=int(6*i.mass/strength)
                    luc=self.stats['luc']
                    attack.damagefactor=1/random.triangular(1,(luc/(10+luc))*self.stats['tec']**0.5)
                    attack.strikearea*=50
                    attack.area*=50
                    return


        #Attempt to parry
        for i in self.equipped_items:
            if i.parry==True and parryable==True:
                encumbrance=0.3*(self.movemass-self.mass)/self.stats['str']
                basemass=0
                strength=0
                tec=0
                dex=0
                for j in i.equipped:
                    if j.attachpoint is not None:
                        basemass+=j.attachpoint.movemass+encumbrance
                        strength+=j.attachpoint.stats['str']*self.stamina[0]/(self.stamina[1]+1)
                    else:
                        basemass+=j.movemass+encumbrance
                        strength+=j.stats['str']*self.stamina[0]/(self.stamina[1]+1)
                    tec+=j.stats['tec']*self.focus[0]/(self.focus[1]+1)
                    dex+=j.dexterity
                parrytime=reactiontime+5*attack.accuracy*((self.focus[1]/(self.focus[0]+1))**0.5)*random.gauss(6/(self.stats['tec']*self.stats['luc']**0.5),.04)*(30*i.I+basemass)/max(strength*i.length*dex*7/self.targetsize,0.001)
                if parrytime<attack.time and random.random()*attack.attacker.stats['tec']<0.8*random.random()*self.stats['per']:
                    #print(reactiontime,parrytime,attack.time)
                    attack.parried=True
                    if attack.type=='pierce':
                        attack.type='crush'
                    attack.target=i
                    attack.basetarget=i
                    luc=self.stats['luc']
                    attack.damagefactor=0.05*(attack.attacker.stats['tec']/self.stats['tec'])/random.triangular(1,self.stats['tec'],(luc/(10+luc))*self.stats['tec'])
                    attack.strikearea*=5*tec**0.5
                    attack.area+=attack.area*4*tec**0.5
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

        if self.vision<=0 and self.smell_sense<=0 and self.hearing<=0 and self.esp<=0 and 'mindless' not in self.classification:
            self.conditions.append('sensory_incapacitated')
        elif "sensory_incapacitated" in self.conditions:
            self.conditions.remove("sensory_incapacitated")
        self.check_visible_cells()

    def recover(self,fullheal=False,effect=1):
        for i in self.limbs:
            i.recover(fullheal=fullheal)

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
        self.targetsize=0
        for i in self.limbs:
            i.mass_calc()
            self.mass+=i.mass
            self.targetsize+=i.length
        self.movemass=self.mass
        for i in self.inventory:
            self.movemass+=i.mass
        #print(self.mass,self.targetsize)

    def magic_effects(self):
        mode=self.stats['luc']/(10+self.stats['luc'])
        if random().random()*self.magic_contamination['total']>self.stats['wil']*self.stats['wil']*random.triangular(0,1,mode=mode):
            effect_type=random.randint(0,self.magic_contamination['total'])
            if effect_type<self.magic_contamination['dark']:
                #dark-type magic contamination effect
                Contamination.dark_effect(self)
                return

            effect_type-=self.magic_contamination['dark']
            if effect_type<self.magic_contamination['elemental']:
                #elemental-type magic contamination effect
                Contamination.elemental_effect(self)
                return

            effect_type-=self.magic_contamination['elemental']
            if effect_type<self.magic_contamination['summoning']:
                #summoning-type magic contamination effect
                Contamination.summoning_effect(self)
                return

            effect_type-=self.magic_contamination['summoning']
            if effect_type<self.magic_contamination['transmutation']:
                #transmutation-type magic contamination effect
                Contamination.transmutation_effect(self)
                return

            effect_type-=self.magic_contamination['transmutation']
            if effect_type<self.magic_contamination['arcane']:
                #arcane-type magic contamination effect
                Contamination.arcane_effect(self)
                return

        else: return

    def on_strike(self,attack):
        pass

    def on_struck(self,attack):
        pass

    def inventory_add(self,item):
        if self==Shell.shell.player:
            item.touched_by_player=True
            if self.can_see==True:
                item.seen_by_player=True
            item.generate_descriptions(self.stats['per'])
            letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-='
        if item not in self.inventory:
            self.inventory.append(item)
            item.in_inventory=self
            item.location=[None,None]
        if self.player:
            if not hasattr(self,'indexed_inventory'):
                self.inventory_setup()
            if item.inventory_index not in (None,'') and self.indexed_inventory[item.inventory_index]==item:
                self.mass_calc()
                return
            for letter in letters:
                try: self.indexed_inventory[letter]
                except KeyError:
                    self.indexed_inventory[letter]=item
                    item.inventory_index=letter
                    self.mass_calc()
                    return
            for key in self.indexed_inventory:
                if self.indexed_inventory[key] not in self.inventory:
                    self.indexed_inventory[key]=item
                    item.inventory_index=key
                    self.mass_calc()
                    return

        self.mass_calc()

    def inventory_order(self):
        letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-='
        newinventory=[]
        for letter in letters:
            for i in self.inventory:
                if i.inventory_index==letter:
                    newinventory.append(i)
        for i in self.inventory:
            if i.inventory_index in ('',None):
                newinventory.append(i)
        if len(newinventory)!=len(self.inventory):
            print("inventory ordering has changed the number of items in the inventory. Operation aborted")
        else:
            self.inventory=newinventory

    def inventory_setup(self):
        if not self.player: return
        self.indexed_inventory={}
        letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-='
        number=0
        for i in self.inventory:
            try: letter=letters[number]
            except: letter=''
            i.in_inventory=self
            i.touched_by_player=True
            if self.can_see==True:
                i.seen_by_player=True
            self.indexed_inventory[letter]=i
            i.inventory_index=letter
            number+=1

    def check_visible_cells(self):
        self.visible_cells=[]
        vision_radius=2*(self.vision)**0.5
        outermost_points=[]
        radius_squared=vision_radius*vision_radius
        '''
        for x in range (0,int(vision_radius)+1):
            y=(radius_squared-x*x)**0.5
            y=int(y)
            outermost_points.append([self.location[0]+x,self.location[1]+y])
            outermost_points.append([self.location[0]+x,self.location[1]-y])
            outermost_points.append([self.location[0]-x,self.location[1]+y])
            outermost_points.append([self.location[0]-x,self.location[1]-y])
            while y>0:
                y=y-1
                length=int((x*x+y*y)**0.5)
                if length==int(vision_radius) or length+1==int(vision_radius):
                    outermost_points.append([self.location[0]+x,self.location[1]+y])
                    outermost_points.append([self.location[0]+x,self.location[1]-y])
                    outermost_points.append([self.location[0]-x,self.location[1]+y])
                    outermost_points.append([self.location[0]-x,self.location[1]-y])
        x1,y1=self.location[0],self.location[1]
        for i in outermost_points:
            #generate a set of points on connecting line
            visible_indices=get_line([x1,y1],i)
            cease_line=False
            for j in visible_indices:
                try:
                    cell=self.floor.cells[j[0]][j[1]]
                    self.visible_cells.append(cell)
                    if cell.transparent==False:
                        cease_line=True
                except KeyError:
                    cease_line=True
                if cease_line==True:
                    break
        '''
        visible_indices=[]
        for x in range(0,int(vision_radius*0.70710678)+1):
            visible_indices.append([])
            for y in range(0,x+1):
                visible_indices[x].append([x,y])
        for x in range(int(vision_radius*0.70710678)+1,int(vision_radius)+1):
            ymax=(radius_squared-x*x)**0.5
            visible_indices.append([])
            for y in range(0,int(ymax)+1):
                visible_indices[x].append([x,y])
        self.visible_cells=self.floor.shadowcasting(visible_indices,self.location)
        #print(self.visible_cells)
        #self.visible_cells=set(self.visible_cells)
        self.visible_creatures=[]
        self.visible_items=[]
        for i in self.visible_cells:
            self.visible_creatures.extend(i.creatures)
            self.visible_items.extend(i.items)
            if self==Shell.shell.player:
                i.visible_to_player=True
                i.seen_by_player=True
                i.update_graphics()
        if self==Shell.shell.player:
            for i in self.visible_items:
                i.seen_by_player=True
            for i in self.visible_creatures:
                i.seen_by_player=True
        return

    def value_item(self,item):
        if item in self.item_values:
            return

        value=0

        equippable=False
        if hasattr(item,'wield'):
            for i in self.limbs:
                if i.can_equip(item)[0]:
                    equippable=True
                    break
        #for weapons
        if hasattr(item,'sortingtype') and item.sortingtype=='weapon' and equippable==True:
            if hasattr(item,'mass'):
                value+=self.iprefs['mass']*item.mass/5
            if hasattr(item,'length'):
                value+=self.iprefs['length']*item.length
            if hasattr(item,'edge'):
                value+=self.iprefs['edge']*1/(100000*item.edge)
            if hasattr(item,'tip'):
                value+=self.iprefs['tip']*1/(10000000*item.tip)
            if hasattr(item,'I'):
                value+=self.iprefs['I']*item.I
            if hasattr(item,'quality'):
                value+=self.iprefs['quality']*item.quality
        #for armor
        elif hasattr(item,'sortingtype') and item.sortingtype=='armor' and equippable==True:
            if hasattr(item,'mass'):
                value+=self.iprefs['mass']*item.mass/5
            if hasattr(item,'thickness'):
                value+=self.iprefs['thickness']*item.thickness/0.005
            if hasattr(item,'quality'):
                value+=self.iprefs['quality']*item.quality

        for i in self.iprefs['type']:
            if isinstance(item,i[0]):
                value=max(value+i[1],value*i[1])

        for i in self.iprefs['material']:
            if hasattr(item,'material') and isinstance(item.material,i[0]):
                value=max(value+i[1],value*i[1])

        print(item.name,value)
        self.item_values[item]=value

    def generate_equipment(self):
        pass

class Material():
    def __init__(self):
        self.wetdamage=None
        self.fluid=None
        self.identification_difficulty=15
        self.acid_reaction='corrode'
        self.acid_resistance=5
        self.heat_reaction='melt'
        self.burn_temp=1000
        self.heat_conduction=1
        self.burn_resistance=1
        self.note=''

    def damageresolve(self,attack,attacker,reactionforce=False):
        if attacker.owner.player==True: print(self.name,attack.force,attack.pressure)
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
            try: defenderstats=random.choice(attack.basetarget.equipped).stats
            except: defenderstats={'str':10,'tec':10,'per':10,'wil':10,'luc':10}
        else:
            defenderstats={'str':10,'tec':10,'per':10,'wil':10,'luc':10}
        self.m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)
        self.contact=False

        if damagedobject.thickness==0 or damagedobject.mass==0:
            print(damagedobject, damagedobject.thickness,damagedobject.mass)

        attack.cutlimit=attack.absolute_depth_limit/(damagedobject.thickness+0.000001)
        attack.piercelimit=attack.absolute_depth_limit/(damagedobject.thickness+0.0000001)

        if self.mode=='brittle':
#Cutting
            self.cut(attack,attacker,damagedobject,defenderstats)

#Piercing
            self.pierce(attack,attacker,damagedobject,defenderstats)

#Crushing
            self.crush(attack,attacker,damagedobject,defenderstats)

#Cracking, Breaking, and Shattering
            self.crack(attack,attacker,damagedobject,defenderstats)



        elif self.mode=='soft':

#Cutting
            self.cut(attack,attacker,damagedobject,defenderstats)

#Piercing
            self.pierce(attack,attacker,damagedobject,defenderstats)

#Crushing
            self.crush(attack,attacker,damagedobject,defenderstats)

#Bruising
            self.bruise(attack,attacker,damagedobject,defenderstats)




        elif self.mode=='ductile':
#Cutting
            self.cut(attack,attacker,damagedobject,defenderstats)

#Piercing
            self.pierce(attack,attacker,damagedobject,defenderstats)

#Crushing
            self.crush(attack,attacker,damagedobject,defenderstats)

#Denting and bending. MUST COME LAST!
            self.dent(attack,attacker,damagedobject,defenderstats)


        elif self.mode=='fabric':
            attack.energy-=self.youngs*self.thickness*attack.area
#Cutting
            self.cut(attack,attacker,damagedobject,defenderstats)

#Piercing
            self.pierce(attack,attacker,damagedobject,defenderstats)








#Final resolution
        if self.contact==True:
            attack.contact=True
            attack.energy_recalc()
        else:
            attack.contact=False

    def bruise(self,attack,attacker,damagedobject,defenderstats):
        if type(attack.pressure)==complex:
            return
        if attack.pressure>self.tensile_strength*300000*damagedobject.thickness / attack.area**0.5 and self.bruisable==True:
            severity=(attack.pressure/(self.tensile_strength*300000)-1)*random.gauss(0.5*attacker.stats['luc']/defenderstats['luc'],0.5) * min(attack.area**0.5 / damagedobject.thickness,5)
            if attack.type=='cut' and self.contact==True and severity>10:
                severity=abs(random.gauss(((attack.force/(100*self.shear_strength+attack.force))*0.1/(self.shear_strength*damagedobject.thickness+0.1))
                                          *(attacker.stats['tec']+0.2*attacker.stats['luc'])/(defenderstats['luc']
                                            +0.2*defenderstats['tec']),0.4))
                damagedobject.damage['cut']=(damagedobject.damage['cut']**2+severity**2)**0.5
                if damagedobject.damage['cut']>=1: self.contact=True
                return

            elif attack.type=='pierce' and self.contact==True and severity>10:
                severity=abs(random.gauss(((attack.force/(10*self.shear_strength+attack.force))*0.2/(self.shear_strength*damagedobject.thickness+0.1))
                                          *(attacker.stats['tec']+0.2*attacker.stats['luc'])/(defenderstats['luc']
                                            +0.2*defenderstats['tec']),0.4))
                damagedobject.damage['pierce']=(damagedobject.damage['pierce']**2+severity**2)**0.5
                if damagedobject.damage['pierce']>=0.3: self.contact=True
                return

            pythagoreanseverity=(severity**2+damagedobject.damage['bruise']**2)**0.5
            damagedobject.damage['bruise']=pythagoreanseverity

    def cut(self,attack,attacker,damagedobject,defenderstats):
        if type(attack.pressure)==complex:
            return
        if attack.pressure<=0 or attack.force<=0:
            rootarea=1
        else:
            rootarea=(attack.force/attack.pressure)**0.5
        assert damagedobject.mass>=0,damagedobject
        shearforce=attack.force*(1/(3.5*(damagedobject.thickness+0.00000000001)*rootarea)-self.density*rootarea/(3.5*damagedobject.mass))*0.0002/(0.0002+rootarea**2)
     #   if isinstance(attack.basetarget,Limb):
      #      assert damagedobject.mass>0,damagedobject
       #     shearforce=min(shearforce*(damagedobject.mass/attack.basetarget.movemass)**0.5,shearforce)
        if shearforce>self.shear_strength*1000000 and attack.contact==True and attack.type=='cut':
            failure_energy=((rootarea*self.thickness*self.shear*1000000000*self.shear_strength**2*self.thickness)/(self.shear_strength+80)**2)**0.5+\
                           self.fracture_energy*self.thickness*rootarea*1000
            #severity=max(random.gauss((2*attack.energy/(4000000*self.fracture_energy*damagedobject.thickness*rootarea+attack.energy))
            #                              *(attacker.stats['tec']+0.2*attacker.stats['luc'])/(defenderstats['luc']
            #                                +0.2*defenderstats['tec']),0.2),0)
            severity=max(random.gauss((attack.energy/failure_energy)*(attacker.stats['tec']+0.2*attacker.stats['luc'])/
                                      (defenderstats['luc']+0.2*defenderstats['tec']),0.2),0)
            severity=min(severity,attack.cutlimit)
            damagedobject.damage['cut']=(damagedobject.damage['cut']**2+severity**2)**0.5
            if damagedobject.damage['cut']>=0.8: self.contact=True
            attack.energy-=min(self.fracture_energy*attack.rootarea*self.thickness*100000,0.9*attack.energy)
            attack.energy_recalc()
            self.bruisable=False
            self.crushable=False
            attack.rootarea=rootarea
        return

    def crush(self,attack,attacker,damagedobject,defenderstats):
        if type(attack.force)==complex:
            return
        if attack.force>(1-(damagedobject.damage['dent']+damagedobject.damage['crack']))*self.tensile_strength*(1200000-200000*random.triangular(low=0,high=1,mode=self.m))*damagedobject.length*damagedobject.radius and damagedobject.damage['crush']==0 and attack.contact==True and self.crushable==True:
                damagedobject.damage['crush']=1
                self.contact=True
                self.bruisable=False
                attack.energy-=7*self.fracture_energy*1000*attack.rootarea*damagedobject.thickness
                attack.energy_recalc()
        pass

    def crack(self,attack,attacker,damagedobject,defenderstats):
        hitloc=random.triangular(low=0.00001,high=1,mode=self.m)*damagedobject.length
        crackforce=min(attack.force*(damagedobject.mass/attack.basetarget.movemass)**0.5,attack.force)*2*attack.pressure/(50000*self.shear_strength+attack.pressure)
        if crackforce>(1-damagedobject.damage['crack']**2)*(self.tensile_strength*1000000*damagedobject.r*damagedobject.thickness**2)/hitloc:
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
        if type(attack.pressure)==complex:
            return
        attack.force=max(attack.force,0.001)
        if attack.pressure==0:
            rootarea=1
        else:
            rootarea=(attack.force/attack.pressure)**0.5
        shearforce=1.5*attack.force*(1/(3.5*(damagedobject.thickness+0.0000000001)*rootarea)-self.density*rootarea/(3.5*(damagedobject.mass+0.00000001)))*0.000002/(0.000002+rootarea**2)
        #if isinstance(attack.basetarget,Limb):
         #   shearforce=min(shearforce*(damagedobject.mass/attack.basetarget.movemass)**0.5,shearforce)
        if shearforce>self.shear_strength*1000000 and attack.contact==True and attack.type=='pierce':
            failure_energy=((rootarea*self.thickness*self.shear*1000000000*self.shear_strength**2*self.thickness)/(self.shear_strength+80)**2)**0.5+\
                           self.fracture_energy*self.thickness*rootarea*1000
            '''severity=abs(random.gauss(((attack.force/(10*self.shear_strength+attack.force))*0.2/(self.shear_strength*damagedobject.thickness+0.1))
                                          *(attacker.stats['tec']+0.2*attacker.stats['luc'])/(defenderstats['luc']
                                            +0.2*defenderstats['tec']),0.4))
            severity=max(random.gauss((2*attack.energy/(2000000*self.fracture_energy*damagedobject.thickness**2+attack.energy))
                                          *(attacker.stats['tec']+0.2*attacker.stats['luc'])/(defenderstats['luc']
                                            +0.2*defenderstats['tec']),0.2),0)'''
            severity=attack.energy/failure_energy
            attack.energy-=min(severity**2*failure_energy,failure_energy,0.9*attack.energy)
            attack.energy_recalc()
            if severity>1:
                severity=0.5+random.random()
            severity=min(severity,attack.piercelimit)
            damagedobject.damage['pierce']=(damagedobject.damage['pierce']**2+severity**2)**0.5
            damagedobject.damage['pierce']=min(damagedobject.damage['pierce'],1)
            #print('current severity is', severity, 'failure energy is',failure_energy)
            if damagedobject.damage['pierce']>=0.2: self.contact=True
            self.bruisable=False
            self.crushable=False
            attack.rootarea=rootarea
        return

    def dent(self,attack,attacker,damagedobject,defenderstats):
        hitloc=random.triangular(low=0.00001,high=1,mode=self.m)*damagedobject.length
        pressurefactor=(0.3*attack.pressure*attack.energy**0.5+10000000*self.shear_strength)/(10000000*self.shear_strength)
        pressurebonus=(pressurefactor-1)/pressurefactor
        dentforce=min(attack.force*(damagedobject.mass/attack.basetarget.movemass)**0.5,attack.force)
        #print(damagedobject.name,damagedobject.thickness,dentforce)
        if dentforce*pressurefactor>0.1*(1-damagedobject.damage['dent']**2)*(self.shear_strength*1000000*damagedobject.r*damagedobject.thickness):
            if self.reactionforce==True:
                severity=(max(0.001*dentforce/(0.05*(self.shear_strength*1000000*(damagedobject.r)**2*damagedobject.thickness)),1)-1)+(pressurebonus**3)/3
            else:
                severity=(max(0.001*dentforce/(0.05*(self.shear_strength*1000000*damagedobject.r*damagedobject.thickness**2)),1)-1)+(pressurebonus**3)/3
            if attack.type=='pierce':
                severity=severity/(severity+1)
            pythagoreanseverity=(damagedobject.damage['dent']**2+severity**2)**0.5
            attack.energy-=min(self.thickness*attack.rootarea*self.youngs*100000,0.9*attack.energy)
            attack.energy_recalc()
            #dented but not bent
            damagedobject.damage['dent']=pythagoreanseverity
            #attack.force=attack.force*(1+severity)
            #attack.pressure=attack.pressure*(1+severity)


        #bent but not crushed
            if severity>0.8 and damagedobject.damage['dent']>1:
                damagedobject.damage['bend']+=damagedobject.damage['dent']-1
                damagedobject.damage['dent']=1
                #attack.force=attack.force*(1+damagedobject.damage['bend'])
                #attack.pressure=attack.pressure*(1+damagedobject.damage['bend'])
                damagedobject.damage['bend']=min(damagedobject.damage['bend'],1)
                self.contact=True

    def on_turn(self):
        pass

    def on_strike(self):
        pass

    def on_struck(self):
        pass
    
    def on_destruction(self):
        pass

class Item():
    def __init__(self,painfactor=1,id=False,**kwargs):
        self.fluid=None
        self.coatings=[]
        self.enchantments=[]
        self.kills=[]
        self.base_thickness=0
        self.base_radius=0
        self.radius=0
        self.color=(1,1,1,1)
        self.name=''
        self.sortingtype='misc'
        self.inventory_index=None
        self.in_inventory=None
        self.location=[None,None]
        self.floor=None
        self.vision_blocking=False
        self.image='./images/Defaultitem.png'
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,
                     'pierce':0,'edgedull':0,'tipdull':0,'edgechip':0,'tipchip':0,'rust':0,'corrode':0,'disintegrate':0}
        self.damagemessage=''
        self.breakcounter=0
        self.regrowthcounter=0
        self.owner=None
        self.function=1
        self.equipped=[]
        self.block=False
        self.parry=False
        self.wield=None
        self.useable=False
        self.painfactor=painfactor
        self.curvature=0
        self.attacks=[]
        self.passable=True
        self.hostile=[]
        self.targetable=False
        self.plural=False
        self.threshold=0
        self.coverage=1
        self.magic_contamination={'dark':0,'elemental':0,'summoning':0,'transmutation':0,'arcane':0,'total':0}
        self.descriptor=''
        self.info={}
        self.note=''
        if id==False:
            self.knowledge_level={'truename':0,'name':0,'material':0,'mass':0,'length':0,'moment of inertia':0,'edge':0,'tip':0,
                              'thickness':0,'force delivery':0,'cutting effectiveness':0,'piercing effectivemess':0,'quality':0,
                              'magic':0,'special':0,'radius':0}
        else:
            self.knowledge_level={'truename':1,'name':2,'material':2,'mass':2,'length':2,'moment of inertia':2,'edge':2,'tip':2,
                              'thickness':2,'force delivery':2,'cutting effectiveness':2,'piercing effectivemess':2,'quality':2,
                              'magic':2,'special':2,'radius':2}
        self.identification_difficulty={'basic':5,'base_material':7,'mass':15,'length':15,'radius':15,
                                        'moment of inertia':20,'material':15,'edge':18,'tip':18,'thickness':18,
                                        'magic':30,'force_delivery':20,'cutting_effectiveness':20,'quality':17,
                                        'piercing_effectiveness':20,'average_time':20,'special':30}
        self.identification_set=False
        self.seen_by_player=False
        self.touched_by_player=False

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
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius
        self.centermass=self.length/2
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.movemass=self.mass

    def damageresolve(self,attack,attacker,reactionforce=False):
        pain=self.painfactor*attack.basetarget.painfactor
        self.olddamage=self.damage.copy()
        self.material.damageresolve(attack,attacker,reactionforce=reactionforce)
        for i in self.damage:
            if self.damage[i]>self.olddamage[i]:
                attack.results.append((i,self.damage[i]-self.olddamage[i]))
                if self not in attack.damagedobjects: attack.damagedobjects.append(self)


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

#Handling edge dulling through chipping or bending of the blade edge
        if self.damage['crush']==0 and self.damage['bend']<1.12 and self.damage['break']==0 and self.damage['shatter']==0 and self.damage['cut']<1:
            if hasattr(self,'edge') or hasattr(self,'tip'):
                if attack.oldtype=='cut' or attack.oldtype=='crush':
                    if self.damage['dent']>0 and hasattr(self,'edge'):
                        self.edge=self.edge*(1+self.damage['dent'])**0.5
                        messages.append("The edge of the {} is dulled".format(self.name))
                        self.damage['edgedull']+=(1+self.damage['dent'])**0.5-1
                        self.damage['dent']=0
                        return
                    if self.damage['crack']>self.olddamage['crack'] and hasattr(self,'edge'):
                        self.edge=self.edge*(1+self.damage['dent'])**0.5
                        messages.append("The edge of the {} is chipped".format(self.name))
                        self.damage['edgechip']+=(1+self.damage['dent'])**0.5-1
                        return
                elif attack.oldtype=='pierce' and reactionforce==True:
                    if self.damage['dent']>0:
                        self.tip=self.tip*(1+self.damage['dent'])**0.5
                        messages.append("The tip of the {} is dulled".format(self.name))
                        self.damage['tipdull']+=(1+self.damage['dent'])**0.5-1
                        self.damage['dent']=0
                        return
                    if self.damage['crack']>0:
                        self.tip=self.tip*(1+self.damage['crack'])**2
                        messages.append("The tip of the {} is chipped".format(self.name))
                        self.damage['tipchip']+=(1+self.damage['crack'])**2-1
                        self.damage['crack']=self.olddamage['crack']
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
            if self.fluid!=None:
                self.fluid.splatter(intensity=(attack.energy**0.5)/15,volume=3)
                if attack.weapon:
                    self.fluid.add(attack.weapon)
                else:
                    self.fluid.add(attack.limb)
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

#From here on out, damage types are no longer boolean. Need to determine which to report, if multiple present

        report_type=max(self.damage['cut']-self.olddamage['cut'],self.damage['crack']-self.olddamage['crack'],(self.damage['pierce']-self.olddamage['pierce'])*0.7,self.damage['bend']-self.olddamage['bend'])


        #test for cutting. If cut all the way through, no further wounds need be processed
        if self.damage['cut']>self.olddamage['cut'] and report_type==self.damage['cut']-self.olddamage['cut']:
            if self.fluid!=None:
                self.fluid.splatter(intensity=(attack.energy**0.5)/15,volume=self.damage['cut']*3)
                if attack.weapon:
                    self.fluid.add(attack.weapon)
                else:
                    self.fluid.add(attack.limb)
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
        if self.damage['pierce']>self.olddamage['pierce'] and report_type==(self.damage['pierce']-self.olddamage['pierce'])*0.7:
            if self.fluid!=None:
                self.fluid.splatter(intensity=(attack.energy**0.5)/15,volume=3*self.damage['pierce'])
                if attack.weapon:
                    self.fluid.add(attack.weapon)
                else:
                    self.fluid.add(attack.limb)
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
                attack.basetarget.owner.pain+=pain*30*self.damage['pierce']/attack.basetarget.owner.stats['wil']**0.5



        #Test for bruising.
        if self.damage['bruise']>self.olddamage['bruise'] and report_type==0:
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
                if self.fluid!=None:
                    self.fluid.splatter(intensity=(attack.energy**0.5)/15,volume=3)
                    if attack.weapon:
                        self.fluid.add(attack.weapon)
                    else:
                        self.fluid.add(attack.limb)
            attack.damage_dealt+=1
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*5*min(self.damage['bruise'],10)/attack.basetarget.owner.stats['wil']**0.5


        #Test for bending. If bent, dents don't need to be mentioned and no material should both shatter and bend
        if self.damage['bend']>self.olddamage['bend'] and report_type==self.damage['bend']-self.olddamage['bend']:
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
        if self.damage['dent']>self.olddamage['dent'] and self.olddamage['dent']==0 and report_type==0:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} is dented!".format(self.name))
            if self.plural==True:
                messages.append("The {} are dented!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*100*self.damage['dent']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return
        elif self.damage['dent']>self.olddamage['dent'] and report_type==0:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} is further dented!".format(self.name))
            if self.plural==True:
                messages.append("The {} are further dented!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*150*self.damage['dent']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return



        #test for cracks and update function accordingly
        if self.damage['crack']>self.olddamage['crack'] == 0 and report_type==self.damage['crack']-self.olddamage['crack']:
            attack.damage_dealt+=1
            if self.plural==False:
                messages.append("The {} is cracked!".format(self.name))
            if self.plural==True:
                messages.append("The {} are cracked!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*100*self.damage['crack']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return
        elif self.damage['crack']>self.olddamage['crack'] and report_type==self.damage['crack']-self.olddamage['crack']:
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

    def process_coatings(self,limb,log=True):
        #This method is only called for coatings on an item which is part of a limb
        self.olddamage=self.damage.copy()
        for i in self.coatings:
            i.process(log=False,limb=limb)
        pain=self.painfactor*limb.painfactor

        if self.olddamage['rust']<self.damage['rust'] and log==True:
            if self.olddamage==0:
                if limb.owner!=Shell.shell.player:
                    messages.append("The {} on {}'s {} rusts. ".format(self.name,limb.owner.name,limb.name))
                else:
                    messages.append("The {} on your {} rusts. ".format(self.name,limb.name))
            else:
                if limb.owner!=Shell.shell.player:
                    messages.append("The {} on {}'s {} rusts further. ".format(self.name,limb.owner.name,limb.name))
                else:
                    messages.append("The {} on your {} rusts further. ".format(self.name,limb.name))

        if self.olddamage['disintegrate']<self.damage['disintegrate']:
            if limb.owner!=Shell.shell.player and log==True:
                messages.append("The {} on {}'s {} dissolves! ".format(self.name,limb.owner.name,limb.name))
            elif log==True:
                messages.append("The {} on your {} dissolves! ".format(self.name,limb.name))
            limb.owner.pain+=pain*200/limb.owner.stats['wil']**0.5


        elif self.olddamage['corrode']<self.damage['corrode']:
            if limb.owner!=Shell.shell.player and log==True:
                messages.append("The {} on {}'s {} is burned by the acid! ".format(self.name,limb.owner.name,limb.name))
            elif log==True:
                messages.append("The {} on your {} is burned by the acid! ".format(self.name,limb.name))
            limb.owner.pain+=150*pain*self.damage['corrode']/limb.owner.stats['wil']**0.5

        if self.damage['disintegrate']>=1:
            try:
                for i in copy.copy(self.coatings):
                    if limb.layers[0]==self:
                        pass
                    else: i.add(limb.layers[limb.layers.index(self)-1])
            except IndexError:
                pass
            for i in self.coatings: i.remove()

        limb.updateability()

    def recover(self,stats,turns=1,fullheal=False,**kwargs):
        if fullheal==True:
            self.damage['bruise']=0
            self.damage['crack']=0
            self.damage['break']=0
            self.damage['shatter']=0
            self.damage['crush']=0
            self.damage['cut']=0
            self.damage['pierce']=0
            self.damage['corrode']=0
            if self.damage['disintegrate']!=0:
                self.radius=self.base_radius
                self.thickness=self.base_thickness
            self.damage['disintegrate']=0
            self.damage['dent']=0
            self.damage['bend']=0
            self.recalc()
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
            if self.damage['cut']>0.8:
                if stats['luc']*random.random()<0.005:
                    permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                    self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
                    self.damage['cut']=0.8
        if self.damage['pierce']>0:
            if stats['luc']>random.uniform(0,100):
                self.damage['pierce']-=min(self.damage['pierce'],self.damage['pierce']*random.random()*stats['luc']/100)
        if self.damage['corrode']>0:
            self.thickness=min(self.base_thickness,self.base_thickness+random.random()*0.001)
            self.radius=min(self.base_radius,self.base_radius+random.random()*0.001)
            self.damage['corrode']=1-min((self.thickness+0.00001)/(self.base_thickness+0.00001),(self.radius+0.00001)/(self.base_radius+0.00001))
        if self.damage['disintegrate']>0:
            if stats['luc']>random.uniform(0,100):
                self.regrowthcounter+=1
            if self.regrowthcounter>100:
                self.damage['disintegrate']=0
                self.damage['corrode']=1
                self.recalc()
                permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
        if self.damage['bend']>0:
            if stats['luc']>random.uniform(0,500):
                self.damage['bend']=0
                self.damage['dent']=1
                permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
        if self.damage['dent']>0:
            if stats['luc']>random.uniform(0,100):
                self.damage['dent']-=min(self.damage['dent'],self.damage['dent']*random.random()*stats['luc']/100)
        if self.damage['burn']>=1:
            if stats['luc']/(100+stats['luc'])>random.triangular(0,1,1):
                self.damage['burn']-=0.01*stats['luc']/15
        else: self.damage['burn']-=min(0.01*stats['luc']/15,self.damage['burn'])

        self.functioncheck()

    def acid_burn(self,strength,log=True):
        message=''
        if self.damage['disintegrate']>=1:
            return
        if self.acid_resistance/strength<random.gauss(0.9,0.2):
            oldcorrosion=self.damage['corrode']
            burnseverity=0.5*(random.random()**2)*strength/self.acid_resistance
            if self.acid_reaction=='embrittle':
                self.material.shear_strength=self.material.shear_strength/(1+burnseverity)**0.5
                self.material.tensile_strength=self.material.tensile_strength/(1+burnseverity)**0.5
                if random.random()>0.85:
                    self.material.mode='brittle'
                self.material_import(primary=False)
            if hasattr(self,'thickness') and burnseverity>0.1:
                self.thickness-=burnseverity/500
                if self.thickness<=0:
                    self.thickness=0
                    self.damage['disintegrate']=1
                    if log==True: messages.append('The {} is dissolved by the acid'.format(self.name))
                    self.functioncheck()
                    return
                else:
                    message='The acid corrodes the {}'.format(self.name)
            if hasattr(self,'head') and burnseverity>0.1:
                self.head-=burnseverity/500
                if self.head<=0:
                    self.head=0
                    self.damage['disintegrate']=1
                    if log==True: messages.append('The {} is dissolved by the acid'.format(self.name))
                    self.functioncheck()
                    return
                else:
                    message='The acid corrodes the {}'.format(self.name)
            if hasattr(self,'radius') and burnseverity>0.1:
                self.radius-=burnseverity/500
                if self.radius<=0:
                    self.radius=0
                    self.damage['disintegrate']=1
                    if log==True: messages.append('The {} is dissolved by the acid'.format(self.name))
                    self.functioncheck()
                    return
                else:
                    message='The acid corrodes the {}'.format(self.name)
            self.damage['corrode']=1-min((self.radius+0.00001)/(self.base_radius+0.00001),(self.thickness+0.00001)/(self.base_thickness+0.00001))
            if hasattr(self,'edge') and burnseverity>0.2 and random.random()>0.6:
                self.edge=self.edge*(1+burnseverity)**0.5
                message='The acid corrodes the edge of the {}'.format(self.name)
            if hasattr(self,'tip') and burnseverity>0.2 and random.random()>0.6:
                self.tip=self.tip*(1+burnseverity)**0.5
                message='The acid corrodes the tip of the {}'.format(self.name)
            self.recalc()
            self.functioncheck()
            if log==True and message!='':
                if self.equipped==[]:
                    messages.append(message)
                elif self.equipped[0].owner==Shell.shell.player:
                    messages.append(message.replace(' the ',' your ',1))
                elif self.equipped[0].owner!=None:
                    messages.append(message.replace(' the '," {}'s ").format(self.equipped[0].owner.name))

    def burn(self,temp,intensity=1,in_limb=False,limb=None,log=True):
        message=''
        ignition=False
        removed_coatings=[]
        for i in self.coatings:
            if i.flammable==True:
                if in_limb==False:
                    messages.append('the {} on the {} catches fire!'.format(i.name,self.name))
                    temp+=random.random()*temp
                    intensity+=3*random.random()
                    removed_coatings.append(i)
                else:
                    messages.append('the {} coating on the {} of the {} catches fire!'.format(i.name,self.name,limb.name))
                    temp+=random.random()*temp
                    intensity+=3*random.random()
                    removed_coatings.append(i)
            elif random.random()*temp*intensity>1000 and i.evaporate==True:
                removed_coatings.append(i)
        for i in removed_coatings:
            self.coatings.remove(i)
        if temp<0.8*self.burn_temp:
            burn_severity=0
        elif temp<=self.burn_temp:
            burn_severity=min(random.random()*intensity*(temp-0.8*self.burn_temp)/(self.burn_temp*self.mass**0.5),0.1)
        else:
            burn_severity=random.random()*(temp-self.burn_temp)*intensity/(1000*self.mass**0.5)+\
                            random.random()*intensity*(temp-0.8*self.burn_temp)/(self.burn_temp*self.mass**0.5)
        burn_severity=burn_severity/self.burn_resistance
        if self.heat_reaction=='ignite' and burn_severity>1:
            if in_limb==False:
                message='the {} is consumed in flames!'.format(self.name)
            else:
                message='the {} on the {} is consumed in flames!'.format(self.name,limb.name)
            self.damage['burn']=1
            igniton=True
            #need to destroy object and add to the flames
        elif self.heat_reaction=='burn' or self.heat_reaction=='ignite':
            severity=(burn_severity**2+self.damage['burn']**2)**0.5
            if severity>=1:
                if in_limb==False:
                    message='the {} is burned to ash by the heat!'.format(self.name)
                else:
                    message='the {} on the {} is burned to ash by the heat!'.format(self.name,limb.name)
                self.damage['burn']=1
            elif severity>=0.7:
                if in_limb==False:
                    message='the {} is badly burned by the heat'.format(self.name)
                else:
                    message='the {} on the {} is badly burned by the heat'.format(self.name,limb.name)
                self.damage['burn']=severity
            elif severity>0.4:
                if in_limb==False:
                    message='the {} is burned by the heat'.format(self.name)
                else:
                    message='the {} on the {} is burned by the heat'.format(self.name,limb.name)
                self.damage['burn']=severity
            elif severity>0.05:
                if in_limb==False:
                    message='the {} is scorched by the heat'.format(self.name)
                else:
                    message='the {} on the {} is scorched by the heat'.format(self.name, limb.name)
                self.damage['burn']=severity
        elif self.heat_reaction=='melt':
            severity=(burn_severity**2+self.damage['burn']**2)**0.5
            if severity>=1:
                if in_limb==False:
                    message='the {} is melted by the heat!'.format(self.name)
                else:
                    message='the {} on the {} is melted by the heat!'.format(self.name,limb.name)
                self.damage['burn']=1
            elif severity>=0.7:
                if in_limb==False:
                    message='the {} is deformed by the heat'.format(self.name)
                else:
                    message='the {} on the {} is deformed by the heat'.format(self.name,limb.name)
                self.damage['bend']+=abs(random.gauss(0,0.1))
                self.damage['deform']+=abs(random.gauss(0,0.1))
                self.tensile_strength=self.tensile_strength*(1-random.gauss(0,0.1)**2)
                self.shear_strength=self.shear_strength*(1-random.gauss(0,0.1)**2)
                self.material.tensile_strength=self.tensile_strength
                self.material.shear_strength=self.shear_strength
            elif severity>0.4:
                if in_limb==False:
                    message='the {} is damaged by the heat'.format(self.name)
                else:
                    message='the {} on the {} is damaged by the heat'.format(self.name,limb.name)
                if severity>random.random(): self.damage['bend']+=abs(random.gauss(0,0.1))
                if severity>random.random():
                    self.tensile_strength=self.tensile_strength*(1-random.gauss(0,0.1)**2)
                    self.material.tensile_strength=self.tensile_strength
                if severity>random.random():
                    self.shear_strength=self.shear_strength*(1-random.gauss(0,0.1)**2)
                    self.material.shear_strength=self.shear_strength
            elif severity>0.05:
                if in_limb==False:
                    message='the {} is softened by the heat'.format(self.name)
                else:
                    message='the {} on the {} is softened by the heat'.format(self.name, limb.name)
                if severity>random.random(): self.damage['dent']+=abs(random.gauss(0,0.1))
                if severity>random.random():
                    self.tensile_strength=self.tensile_strength*(1-random.gauss(0,0.1)**2)
                    self.material.tensile_strength=self.tensile_strength
                if severity>random.random():
                    self.shear_strength=self.shear_strength*(1-random.gauss(0,0.1)**2)
                    self.material.shear_strength=self.shear_strength
        if self.plural==True:
            message=message.replace(' is ',' are ')
        self.functioncheck()
        if in_limb==True:
            if ignition==False:
                conduction_factor=intensity*self.heat_conduction/self.thickness
                newtemp=temp*conduction_factor/(50000+conduction_factor)
                newintensity=intensity*(conduction_factor/(50000+conduction_factor))**0.5
            else:
                newtemp=(temp**2+self.mass*self.burn_temp**2)**0.5
                newintensity=intensity+self.mass**0.5
            return message,newtemp,newintensity
        elif log==True and message!='':
            messages.append(message)

    def on_equip(self):
        pass

    def on_turn(self):
        for i in self.enchantments:
            i.on_turn()
        for i in self.coatings:
            i.process()
        total_contamination=-self.magic_contamination['total']
        for keys in self.magic_contamination:
            total_contamination+=self.magic_contamination[keys]
        self.magic_contamination['total']=total_contamination

    def on_strike(self,attack):
        for i in self.coatings:
            i.on_strike(attack)
        for i in self.enchantments:
            i.on_strike(attack)

    def on_struck(self,attack):
        for i in self.coatings:
            i.on_struck(attack)
        for i in self.enchantments:
            i.on_struck(attack)
    
    def on_destruction(self):
        for i in self.enchantments:
            i.on_destruction()
        self.material.on_destruction()

    def functioncheck(self):
        if self.damage['shatter']+self.damage['crush']+self.damage['break']+self.damage['bend']>=1:
            self.function=0
        elif self.damage['disintegrate']>=1:
            self.function=0
            self.radius=self.base_radius
            self.thickness=self.base_thickness
            if self.location!=[None,None]:
                try: Shell.shell.dungeonmanager.current_screen.cells[self.location[0]][self.location[1]].contents.remove(self)
                except ValueError: pass
        else:
            self.function=max(1-self.damage['burn']-self.damage['crack']-0.6*self.damage['dent']-self.damage['bruise']/20
                              -self.damage['cut']-self.damage['deform']-0.7*self.damage['pierce']-0.8*self.damage['corrode'],0)
        if self.function<self.threshold:
            self.function=0
        if self.function<=0:
            self.on_destruction()
        for i in self.equipped:
            if isinstance(i,Limb):
                if self.function<=self.threshold:
                    if i.attachpoint:
                        i.attachpoint.unequip(self.wield,destroyed=True)
                    if self.equipped!=[]:
                        i.unequip(self.wield,destroyed=True)

    def material_import(self,primary=True):
        self.quality=self.material.quality
        self.burn_temp=self.material.burn_temp
        self.heat_reaction=self.material.heat_reaction
        self.heat_conduction=self.material.heat_conduction
        self.burn_resistance=self.material.burn_resistance
        self.acid_reaction=self.material.acid_reaction
        self.acid_resistance=self.material.acid_resistance
        self.wetdamage=self.material.wetdamage
        self.color=self.material.color
        self.youngs=self.material.youngs
        self.density=self.material.density
        self.shear=self.material.shear
        self.tensile_strength=self.material.tensile_strength
        self.shear_strength=self.material.shear_strength
        self.mode=self.material.mode
        self.damagetype=self.material.damagetype
        self.dissipationfactor=self.material.dissipationfactor
        if primary==True:
            self.identification_difficulty['material']=self.material.identification_difficulty
            self.identification_difficulty['quality']=(self.identification_difficulty['quality']+self.material.identification_difficulty)/2

    def describe_damage(self,title='default',d={'has':'has','is':'is','it':'it','It':'It','its':'its','Its':'Its','s':'s'},bloody='bloody',blood='blood'):
        if self.fluid!=None:
            bloody=self.fluid.adjective
            blood=self.fluid.basicname
        self.damagemessage=''
        if title=='default':
            if self.plural==True:
                d={'has':'have','is':'are','it':'they','It':'They','its':'their','s':'','Its':'Their'}
            else:
                d=d
        else:
            if self.plural==True:
                d={'has':'have','is':'are','it':title,'It':title,'its':'their','s':'','Its':'Their'}
            else:
                d={'has':'has','is':'is','it':title,'It':title,'its':'its','s':'s','Its':'Its'}

        if self.damage['shatter']>=1:
            self.damagemessage=''.join((self.damagemessage,'{} {} been shattered. '.format(d['It'],d['has'])))
            return self.damagemessage
        if self.damage['crush']>=1:
            self.damagemessage=''.join((self.damagemessage,'{} {} been crushed. '.format(d['It'],d['has'])))
            return self.damagemessage
        if self.damage['break']>=1:
            self.damagemessage=''.join((self.damagemessage,'{} {} been broken in two. '.format(d['It'],d['has'])))
            return self.damagemessage
        if self.damage['cut']>=1:
            self.damagemessage=''.join((self.damagemessage,'{} {} been cleaved fully apart. '.format(d['It'],d['has'])))
            return self.damagemessage
        if self.damage['cut']>0.6:
            self.damagemessage=''.join((self.damagemessage,'{} {} cut most of the way through. '.format(d['It'],d['is'])))
        elif self.damage['cut']>0.2:
            self.damagemessage=''.join((self.damagemessage,'{} {} been cut partway through. '.format(d['It'],d['has'])))
        elif self.damage['cut']>0.01:
            self.damagemessage=''.join((self.damagemessage,'{} {} scratched. '.format(d['It'],d['is'])))
        if self.damage['bend']>=1:
            self.damagemessage=''.join((self.damagemessage,'{} {} been mangled into a useless form. '.format(d['It'],d['has'])))
        elif self.damage['bend']>0:
            self.damagemessage=''.join((self.damagemessage,'{} {} bent out of {} original shape. '.format(d['It'],d['is'],d['its'])))
        elif self.damage['dent']>0.6:
            self.damagemessage=''.join((self.damagemessage,'{} {} badly dented and barely resemble{} {} original form. '.format(d['It'],d['is'],d['s'],d['its'])))
        elif self.damage['dent']>0.2:
            self.damagemessage=''.join((self.damagemessage,'{} {} dented. '.format(d['It'],d['is'])))
        elif self.damage['dent']>0.01:
            self.damagemessage=''.join((self.damagemessage,'{} show{} some minor denting. '.format(d['It'],d['s'])))
        if self.damage['crack']>0.6:
            self.damagemessage=''.join((self.damagemessage,'{} {} cracked nearly through. '.format(d['It'],d['is'])))
        elif self.damage['crack']>0.2:
            self.damagemessage=''.join((self.damagemessage,'{} {} cracked. '.format(d['It'],d['is'])))
        elif self.damage['crack']>0.01:
            self.damagemessage=''.join((self.damagemessage,'{} {} some minor hairline fractures. '.format(d['It'],d['has'])))
        if self.damage['pierce']>=1:
            self.damagemessage=''.join((self.damagemessage,'{} {} pierced straight through. '.format(d['It'],d['is'])))
        elif self.damage['pierce']>0.6:
            self.damagemessage=''.join((self.damagemessage,'{} {} been punctured. '.format(d['It'],d['has'])))
        elif self.damage['pierce']>0.2:
            self.damagemessage=''.join((self.damagemessage,'{} {} been pierced partway through. '.format(d['It'],d['has'])))
        elif self.damage['pierce']>0.01:
            self.damagemessage=''.join((self.damagemessage,'{} bear{} some minor scratching. '.format(d['It'],d['s'])))
        if self.damage['bruise']>10:
            self.damagemessage=''.join((self.damagemessage,'{} {} smashed to a {} pulp. '.format(d['It'],d['is'],bloody)))
        elif self.damage['bruise']>7:
            self.damagemessage=''.join((self.damagemessage,'{} {} swollen with {}. '.format(d['It'],d['is'],blood)))
        elif self.damage['bruise']>4:
            self.damagemessage=''.join((self.damagemessage,'{} {} badly bruised. '.format(d['It'],d['is'])))
        elif self.damage['bruise']>0.01:
            self.damagemessage=''.join((self.damagemessage,'{} {} bruised. '.format(d['It'],d['is'])))
        if self.damage['deform']>=1:
            self.damagemessage=''.join((self.damagemessage,'{} {} deformed to the point of uselessness. '.format(d['It'],d['is'])))
        elif self.damage['deform']>0.6:
            self.damagemessage=''.join((self.damagemessage,'{} {} grotesquely deformed. '.format(d['It'],d['is'])))
        elif self.damage['deform']>0.01:
            self.damagemessage=''.join((self.damagemessage,'{} {} deformed. '.format(d['It'],d['is'])))
        if self.damage['edgechip']>1:
            self.damagemessage=''.join((self.damagemessage,'{} edge is badly chipped. '.format(d['Its'])))
        elif self.damage['edgechip']>0.01:
            self.damagemessage=''.join((self.damagemessage,'{} edge is chipped in places. '.format(d['Its'])))
        if self.damage['edgedull']>1:
            self.damagemessage=''.join((self.damagemessage,'{} edge is badly worn. '.format(d['Its'])))
        elif self.damage['edgedull']>0.01:
            self.damagemessage=''.join((self.damagemessage,'{} edge is slightly dulled from use. '.format(d['Its'])))
        if self.damage['tipchip']>1:
            self.damagemessage=''.join((self.damagemessage,'{} tip is cracked. '.format(d['Its'])))
        elif self.damage['tipchip']>0.01:
            self.damagemessage=''.join((self.damagemessage,'{} tip is chipped. '.format(d['Its'])))
        if self.damage['tipdull']>1:
            self.damagemessage=''.join((self.damagemessage,'{} tip is badly worn. '.format(d['Its'])))
        elif self.damage['tipdull']>0.01:
            self.damagemessage=''.join((self.damagemessage,'{} tip is slightly dulled from use. '.format(d['Its'])))
        if self.damage['rust']>=1:
            self.damagemessage=''.join((self.damagemessage,'{} {} completely rusted through. '.format(d['It'],d['is'])))
        elif self.damage['rust']>=0.6:
            self.damagemessage=''.join((self.damagemessage,'{} {} badly rusted. '.format(d['It'],d['is'])))
        elif self.damage['rust']>=0.3:
            self.damagemessage=''.join((self.damagemessage,'{} {} rusted. '.format(d['It'],d['is'])))
        elif self.damage['rust']>0.1:
            self.damagemessage=''.join((self.damagemessage,'{} {} slightly rusted. '.format(d['It'],d['is'])))
        if self.damage['corrode']>=1:
            self.damagemessage=''.join((self.damagemessage,'{} {} thoroughly corroded. '.format(d['It'],d['is'])))
        elif self.damage['corrode']>=0.6:
            self.damagemessage=''.join((self.damagemessage,'{} {} badly corroded. '.format(d['It'],d['is'])))
        elif self.damage['corrode']>=0.3:
            self.damagemessage=''.join((self.damagemessage,'{} {} corroded. '.format(d['It'],d['is'])))
        elif self.damage['corrode']>0.1:
            self.damagemessage=''.join((self.damagemessage,'{} {} slightly corroded. '.format(d['It'],d['is'])))
        if self.damage['burn']>=1:
            if self.heat_reaction=='burn' or self.heat_reaction=='ignite':
                self.damagemessage=''.join((self.damagemessage,'{} {} burned to ashes. '.format(d['It'],d['is'])))
            elif self.heat_reaction=='melt':
                self.damagemessage=''.join((self.damagemessage,'{} {} been melted. '.format(d['It'],d['has'])))
        elif self.damage['burn']>=0.6:
            self.damagemessage=''.join((self.damagemessage,'{} {} badly burned. '.format(d['It'],d['is'])))
        elif self.damage['burn']>=0.3:
            self.damagemessage=''.join((self.damagemessage,'{} {} burned. '.format(d['It'],d['is'])))
        elif self.damage['burn']>0.1:
            self.damagemessage=''.join((self.damagemessage,'{} {} scorched. '.format(d['It'],d['is'])))

        #Now to describe coatings
        if len(self.coatings)==0:
            pass
        elif len(self.coatings)==1:
            if Shell.shell.player.stats['per']>self.coatings[0].identification_difficulty:
                self.damagemessage=''.join((self.damagemessage,'{} {} coated in {}. '.format(d['It'],d['is'],self.coatings[0].name)))
            elif Shell.shell.player.stats['per']*2>self.coatings[0].identification_difficulty:
                self.damagemessage=''.join((self.damagemessage,'{} {} coated in {}. '.format(d['It'],d['is'],self.coatings[0].basicname)))
            else:
                self.damagemessage=''.join((self.damagemessage,'{} {} coated in an unknown substance. '.format(d['It'],d['is'])))
        elif len(self.coatings)==2:
            if Shell.shell.player.stats['per']>self.coatings[0].identification_difficulty:
                self.damagemessage=''.join((self.damagemessage,'{} {} coated in {} '.format(d['It'],d['is'],self.coatings[0].name)))
            elif Shell.shell.player.stats['per']*2>self.coatings[0].identification_difficulty:
                self.damagemessage=''.join((self.damagemessage,'{} {} coated in {} '.format(d['It'],d['is'],self.coatings[0].basicname)))
            else:
                self.damagemessage=''.join((self.damagemessage,'{} {} coated in an unknown substance '.format(d['It'],d['is'])))
            if Shell.shell.player.stats['per']>self.coatings[1].identification_difficulty:
                self.damagemessage=''.join((self.damagemessage,'and {}. '.format(self.coatings[1].name)))
            elif Shell.shell.player.stats['per']*2>self.coatings[1].identification_difficulty:
                self.damagemessage=''.join((self.damagemessage,'and {}. '.format(self.coatings[1].basicname)))
            else:
                self.damagemessage=''.join((self.damagemessage,'and an unknown substance. '))
        elif len(self.coatings)>2:
            if Shell.shell.player.stats['per']>self.coatings[0].identification_difficulty:
                self.damagemessage=''.join((self.damagemessage,'{} {} coated in {}, '.format(d['It'],d['is'],self.coatings[0].name)))
            elif Shell.shell.player.stats['per']*2>self.coatings[0].identification_difficulty:
                self.damagemessage=''.join((self.damagemessage,'{} {} coated in {}, '.format(d['It'],d['is'],self.coatings[0].basicname)))
            else:
                self.damagemessage=''.join((self.damagemessage,'{} {} coated in an unknown substance, '.format(d['It'],d['is'])))
            for i in self.coatings:
                if i!=self.coatings[0] and i!=self.coatings[len(self.coatings)-1]:
                    if Shell.shell.player.stats['per']>i.identification_difficulty:
                        self.damagemessage=''.join((self.damagemessage,'{}, '.format(i.name)))
                    elif Shell.shell.player.stats['per']*2>i.identification_difficulty:
                        self.damagemessage=''.join((self.damagemessage,'{}, '.format(i.basicname)))
                    else:
                        self.damagemessage=''.join((self.damagemessage,'an unknown substance, '))
            lastcoating=self.coatings[len(self.coatings)-1]
            if Shell.shell.player.stats['per']>lastcoating.identification_difficulty:
                self.damagemessage=''.join((self.damagemessage,'and {}. '.format(lastcoating.name)))
            elif Shell.shell.player.stats['per']*2>lastcoating.identification_difficulty:
                self.damagemessage=''.join((self.damagemessage,'and {}. '.format(lastcoating.basicname)))
            else:
                self.damagemessage=''.join((self.damagemessage,'and an unknown substance. '))
        return self.damagemessage

    def generate_descriptions(self,per=0):
        if per==0:
            try: per=Shell.shell.player.stats['per']
            except: pass
        if self.identification_set==False:
            self.pre_identify()
        base_per=per

        #If the true name is known, there is no need to figure out the name
        if self.knowledge_level['truename']==1:
            self.name=self.truename
            self.descriptor=self.base_descriptor
            self.info['material']=self.material.name
        else:
            #Either seeing OR touching an object is important for identifying what it is
            if self.seen_by_player==False and self.touched_by_player==False:
                per=base_per/3
            #See if we can correctly identify WHAT the thing is. 0 for no info, 1 for basic, 2 for full
            if per>self.identification_difficulty['basic'] and self.knowledge_level['truename']!=1:
                self.name=self.names[len(self.names)-1]
                self.knowledge_level['name']=2
                self.descriptor=self.base_descriptor
            elif per>self.identification_difficulty['basic']/2 and self.knowledge_level['name']==0:
                self.name=self.names[0]
                self.descriptor='this is a {}'.format(self.name)
            elif self.knowledge_level['name']==0:
                self.name=self.names[len(self.names)-2]
                self.knowledge_level['name']=1
                self.descriptor='this is a {}'.format(self.name)
            #For identifying the material, both sight and touch are important. Sight somewhat moreso
            per=base_per
            if self.touched_by_player==False:
                per=per/1.5
            if self.seen_by_player==False:
                per=per/2
            if self.name==self.material.name:
                pass
            #Now for the material. 2 for full recognition, 1 for basic recognition, 0 for none
            elif per>self.identification_difficulty['material'] or self.knowledge_level['material']==2:
                self.name=''.join((self.material.name,' ',self.name))
                self.knowledge_level['material']=2
                self.info['material']=self.material.name
            elif per>self.identification_difficulty['base_material'] or self.knowledge_level['material']==1:
                self.name=''.join((self.material.basicname,' ',self.name))
                self.knowledge_level['material']=1
                self.info['material']=''.join(('unknown ',self.material.basicname))
            if self.name==self.truename:
                self.knowledge_level['truename']=1

        #can we identify the mass correctly?
        #Holding is very important for determining mass. Seeing is only important if it has not been held
        per=base_per
        if self.touched_by_player==False:
            if self.seen_by_player==False:
                per=per/3
            else:
                per=per/2
        if per>self.identification_difficulty['mass'] or self.knowledge_level['mass']==2:
            self.info['mass']='{} kg'.format(int(1000*self.mass)/1000)
            self.knowledge_level['mass']=2
        elif per*2>self.identification_difficulty['mass']:
            self.info['mass']='about {} kg'.format(int(10*self.mass*(1+(random.random()-0.5)/per))/10)
            self.knowledge_level['mass']=1
        elif self.knowledge_level['mass']==0:
            self.info['mass']='unknown mass'

        #can we identify the length correctly?
        #Either seeing or holding will work for identifying length
        per=base_per
        if self.seen_by_player==False and self.touched_by_player==False:
            per=per/3
        if per>self.identification_difficulty['length'] or self.knowledge_level['length']==2:
            self.info['length']='{} m'.format(int(1000*self.length)/1000)
            self.knowledge_level['length']=2
        elif per*2>self.identification_difficulty['length']:
            self.info['length']='about {} m'.format(int(10*self.length*(1+(random.random()-0.5)/per))/10)
            self.knowledge_level['length']=1
        elif self.knowledge_level['length']==0:
            self.info['length']='unknown length'

        #can we identify the radius of armor correctly?
        #Either seeing or holding will work for identifying the radius.
        if self.sortingtype=='armor' and self.wield!='grasp':
            per=base_per
            if self.seen_by_player==False and self.touched_by_player==False:
                per=per/3
            if per>self.identification_difficulty['radius'] or self.knowledge_level['radius']==2:
                self.info['radius']='{} m'.format(int(1000*self.in_radius)/1000)
                self.knowledge_level['radius']=2
            elif per*2>self.identification_difficulty['radius']:
                self.info['radius']='about {} m'.format(int(10*self.in_radius*(1+(random.random()-0.5)/per))/10)
                self.knowledge_level['radius']=1
            elif self.knowledge_level['radius']==0:
                self.info['radius']='unknown radius'

        #Much like mass, holding is more important than seeing for determining moment of inertia
        per=base_per
        if self.touched_by_player==False:
            if self.seen_by_player==False:
                per=per/3
            else:
                per=per/2
        if hasattr(self,'I') and self.sortingtype=='weapon':
            if per>self.identification_difficulty['moment of inertia'] or self.knowledge_level['moment of inertia']==2:
                self.info['moment of inertia']='{} kgm[sup]2[/sup]'.format(int(1000*self.I)/1000)
                self.knowledge_level['moment of inertia']=2
            elif per*2>self.identification_difficulty['moment of inertia']:
                self.info['moment of inertia']='about {} kgm[sup]2[/sup]'.format(int(10*self.I*(1+(random.random()-0.5)/per))/10)
                self.knowledge_level['moment of inertia']=1
            elif self.knowledge_level['moment of inertia']==0:
                self.info['moment of inertia']='unknown'

        #Edge sharpness is best determined by touch
        per=base_per
        if self.touched_by_player==False:
            if self.seen_by_player==False:
                per=per/3
            else:
                per=per/2
        if hasattr(self,'edge'):
            sharpness=int(1/(int(10000000*self.edge)/10000))
            if per>self.identification_difficulty['edge'] or self.knowledge_level['edge']==2:
                self.info['edge sharpness']='{} mm[sup]-1[/sup]'.format(sharpness)
                self.knowledge_level['edge']=2
            elif per*2>self.identification_difficulty['edge']:
                if sharpness>=500:
                    self.info['edge sharpness']='unfathomably sharp'
                elif sharpness>=200:
                    self.info['edge sharpness']='extremely sharp'
                elif sharpness>=150:
                    self.info['edge sharpness']='very sharp'
                elif sharpness>=100:
                    self.info['edge sharpness']='sharp'
                elif sharpness>=50:
                    self.info['edge sharpness']='somewhat sharp'
                elif sharpness>=30:
                    self.info['edge sharpness']='slightly dull'
                elif sharpness>=10:
                    self.info['edge sharpness']='dull'
                else:
                    self.info['edge sharpness']='blunt'
                self.knowledge_level['edge']=1
            elif self.knowledge_level['edge']==0:
                self.info['edge sharpness']='unknown'

        #Tip sharpness is just like edge sharpness
        per=base_per
        if self.touched_by_player==False:
            if self.seen_by_player==False:
                per=per/3
            else:
                per=per/2
        if hasattr(self,'tip'):
            sharpness=int(1/(int(1000000000*self.tip)/10000))
            if per>self.identification_difficulty['tip'] or self.knowledge_level['tip']==2:
                self.info['tip sharpness']='{} mm[sup]-2[/sup]'.format(sharpness)
                self.knowledge_level['tip']=2
            elif per*2>self.identification_difficulty['tip']:
                if sharpness>=500:
                    self.info['tip sharpness']='unfathomably sharp'
                elif sharpness>=200:
                    self.info['tip sharpness']='extremely sharp'
                elif sharpness>=150:
                    self.info['tip sharpness']='very sharp'
                elif sharpness>=100:
                    self.info['tip sharpness']='sharp'
                elif sharpness>=50:
                    self.info['tip sharpness']='somewhat sharp'
                elif sharpness>=30:
                    self.info['tip sharpness']='slightly dull'
                elif sharpness>=10:
                    self.info['tip sharpness']='dull'
                else:
                    self.info['tip sharpness']='blunt'
                self.knowledge_level['tip']=1
            elif self.knowledge_level['tip']==0:
                self.info['tip sharpness']='unknown'

        #Thickness is best determined by touch, but can be ascertained by vision as well. Only relevant for armor
        per=base_per
        if self.touched_by_player==False:
            if self.seen_by_player==False:
                per=per/3
            else:
                per=per/1.5
        if self.sortingtype=='armor':
            thickness=int(self.thickness*100000)/100
            if per>self.identification_difficulty['thickness'] or self.knowledge_level['thickness']==2:
                self.info['thickness']='{} mm'.format(thickness)
                self.knowledge_level['thickness']=2
            elif per*2>self.identification_difficulty['thickness']:
                thicknessfactor=self.thickness/self.default_thickness
                if thicknessfactor>=2:
                    self.info['thickness']='extremely thick'
                elif thicknessfactor>=1.5:
                    self.info['thickness']='very thick'
                elif thicknessfactor>=1.2:
                    self.info['thickness']='thick'
                elif thicknessfactor>=0.8:
                    self.info['thickness']='about average'
                elif thicknessfactor>=0.6:
                    self.info['thickness']='thin'
                elif thicknessfactor>=0.4:
                    self.info['thickness']='very thin'
                else:
                    self.info['thickness']='extremely thin'
                self.knowledge_level['thickness']=1
            elif self.knowledge_level['thickness']==0:
                self.info['thickness']='unknown'

        #quality is best judged by touch
        per=base_per
        if self.touched_by_player==False:
            per=per/3
        if self.seen_by_player==False:
            per=per/2
        if per/2>self.identification_difficulty['quality']:
            if self.material.quality>=4:
                self.info['quality']='masterwork ({})'.format(int(self.material.quality*100)/100)
            elif self.material.quality>=3:
                self.info['quality']='exceptional ({})'.format(int(self.material.quality*100)/100)
            elif self.material.quality>=2:
                self.info['quality']='fine ({})'.format(int(self.material.quality*100)/100)
            elif self.material.quality>=1.2:
                self.info['quality']='high ({})'.format(int(self.material.quality*100)/100)
            elif self.material.quality>=0.8:
                self.info['quality']='average ({})'.format(int(self.material.quality*100)/100)
            elif self.material.quality>=0.6:
                self.info['quality']='low ({})'.format(int(self.material.quality*100)/100)
            else:
                self.info['quality']='poor ({})'.format(int(self.material.quality*100)/100)
            self.knowledge_level['quality']=2
        if per>self.identification_difficulty['quality'] and self.knowledge_level['quality']!=2:
            if self.material.quality>=4:
                self.info['quality']='masterwork'
            elif self.material.quality>=3:
                self.info['quality']='exceptional'
            elif self.material.quality>=2:
                self.info['quality']='fine'
            elif self.material.quality>=1.2:
                self.info['quality']='high'
            elif self.material.quality>=0.8:
                self.info['quality']='average'
            elif self.material.quality>=0.6:
                self.info['quality']='low'
            else:
                self.info['quality']='poor'
            self.knowledge_level['quality']=1
        if self.knowledge_level['quality']==0:
            self.info['quality']='unknown'


        if per>self.identification_difficulty['magic'] or self.knowledge_level['magic']:
            self.info['magic']='None detected'
            self.knowledge_level['magic']=2
        elif per/2>self.identification_difficulty['magic']:
            self.info['magic']='None detected'
            self.knowledge_level['magic']=1
        elif self.knowledge_level['magic']==0:
            self.info['magic']='Unknown'
#TODO: Must implement detection of magic, blessing, and possession


        if self.wield==None:
            self.info['equippable by player']='No (not equippable at all)'
            return
        reasons=[]
        for i in Shell.shell.player.limbs:
            x=i.can_equip(self)
            if x[0]==True:
                if self.wield=='grasp':
                    bodypart='grasp'
                elif self.wield=='glove':
                    bodypart='hand'
                elif self.wield=='boot':
                    bodypart='foot'
                elif self.wield=='chest':
                    bodypart='torso'
                elif self.wield=='legging':
                    bodypart='leg'
                elif self.wield=='armlet':
                    bodypart='arm'
                elif self.wield=='helmet':
                    bodypart='head'
                elif self.wield=='ring':
                    bodypart='finger'
                elif self.wield=='necklace':
                    bodypart='neck'
                elif self.wield=='bracelet':
                    bodypart='wrist'
                self.info['equippable by player']='Yes ({})'.format(bodypart)
                return
            else:
                reasons.append(x[1])
        if 'size conflict' in reasons:
            self.info['equippable by player']='No (size conflict)'
        else:
            self.info['equippable by player']='No (no appropriate body parts)'

    def pre_identify(self):
        for i in self.identification_difficulty:
            self.identification_difficulty[i]+=random.triangular(-3,3,0)
        self.identification_set=True

    def randomize(self,stdev=0.1,material_set=None):
        r={}
        if hasattr(self,'length'): r['length']=self.length*random.triangular(1/2,1.5,1)
        else: r['length']=None
        if hasattr(self,'thickness'): r['thickness']=self.thickness*random.triangular(1/3,2,1)
        else: r['thickness']=None
        if hasattr(self,'edge'): r['edge']=self.edge*random.triangular(1/4,5,1)
        else: r['edge']=None
        if hasattr(self,'tip'): r['tip']=self.tip*random.triangular(1/4,5,1)
        else: r['tip']=None
        if hasattr(self,'head'): r['head']=self.head*random.triangular(2/3,1.5,1)
        else: r['head']=None
        if hasattr(self,'headvolume'): r['headvolume']=self.headvolume*random.triangular(0.5,2,1)
        else: r['headvolume']=None
        if hasattr(self,'headsize'): r['headsize']=self.headsize*random.triangular(0.5,2,1)
        else: r['headsize']=None
        if hasattr(self,'width'): r['width']=self.width*random.triangular(2/3,1.5,1)
        else: r['width']=None
        if hasattr(self,'in_radius'): r['in radius']=self.in_radius*random.triangular(0.5,2,1)
        else: r['in radius']=None
        if hasattr(self,'quality'): r['quality']=self.quality*random.triangular(0.2,5,1)
        else: r['quality']=None

        self.material=type(self.material)
        if material_set==None:
            pass
        else:
            self.material=random.choice(material_set)
        self.__init__(painfactor=self.painfactor,length=r['length'],thickness=r['thickness'],edge=r['edge'],tip=r['tip'],
                      head=r['head'],headvolume=r['headvolume'],headsize=r['headsize'],width=r['width'],in_radius=r['in radius'],
                      quality=r['quality'],material=self.material)


class Fluid():
    def __init__(self,owner,**kwargs):
        self.owner=owner
        self.image=None
        self.identification_difficulty=5
        self.passable=True
        self.targetable=False
        self.vision_blocking=False
        self.on=None
        self.flammable=False
        self.evaporate=True

    def process(self,**kwargs):
        pass

    def remove(self,**kwargs):
        if self.on!= None:
            self.on.coatings.remove(self)
        else:
            for i in Shell.shell.dungeonmanager.current_screen.nonindexedcells:
                if self in i.contents:
                    i.contents.remove(self)
        pass

    def add(self,target,**kwargs):
        new=copy.copy(self)
        if isinstance(target,Limb):
            new.defenderstats=target.stats
            try:
                if target.armor is not None and random.random()>target.armor.coverage:
                    if not any(i.name==self.name for i in target.armor.coatings):
                        target.armor.coatings.append(new)
                        new.on=target.armor
                elif not any(i.name==self.name for i in target.layers[len(target.layers)-1].coatings):
                    target.layers[len(target.layers)-1].coatings.append(new)
                    new.on=target.layers[len(target.layers)-1]
            except IndexError: pass
        elif isinstance(target,Item) and not any(i.name==self.name for i in target.coatings):
            new.defenderstats=Shell.shell.player.stats
            target.coatings.append(new)
            new.on=target

    def splatter(self,intensity=0,volume=1,**kwargs):
        targets=0
        while targets<volume:
            newsplatter=copy.copy(self)
            newsplatter.location=[None,None]
            if self.owner.location is not None:
                newsplatter.location[0]=min(max(self.owner.location[0]+int(random.gauss(0,intensity)),0),Shell.shell.dungeonmanager.current_screen.dimensions[0])
                newsplatter.location[1]=min(max(self.owner.location[1]+int(random.gauss(0,intensity)),0),Shell.shell.dungeonmanager.current_screen.dimensions[1])
                try: loc=Shell.shell.dungeonmanager.current_screen.cells[newsplatter.location[0]][newsplatter.location[1]]
                except KeyError: loc=Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]]
                if loc:
                    if loc.contents!=[]:
                        splattertarget=random.choice(loc.contents)
                        if splattertarget==self.owner and not any(i.name==self.name for i in loc.contents): loc.contents.append(newsplatter)
                        elif isinstance(splattertarget,Creature):
                            try: splattertarget=random.choice(splattertarget.limbs)
                            except IndexError: splattertarget=None
                        self.add(splattertarget)
                    elif not any(i.name==self.name for i in loc.contents): loc.contents.append(newsplatter)
                else:
                    Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]].contents.append(newsplatter)

            targets+=1

    def on_turn(self,**kwargs):
        if random.random()<0.01:
            self.remove()
        pass

    def on_strike(self,attack,**kwargs):
        if random.random()>0.9:
            self.add(attack.basetarget)

    def on_struck(self,attack,**kwargs):
        if random.random()>0.9:
            try: self.add(attack.weapon)
            except AttributeError:
                try: self.add(attack.limb)
                except AttributeError: pass


class Enchantment():
    def __init__(self,target,turns='permanent',**kwargs):
        self.target=target
        self.turns=turns
        self.category='magic'
        self.detected=False
        self.identified=False
        self.detection_difficulty=20
        self.identification_difficulty=30
        try: self.target.enchantments.append(self)
        except AttributeError: pass
        pass
    
    def on_turn(self):
        if self.turns=='permanent':
            pass
        else:
            self.turns-=1
        if self.turns==0:
            self.target.enchantments.remove(self)
        if self.detected==False or self.identified==False:
            self.attempt_identification()
            
    def on_strike(self,attack):
        pass
    
    def on_struck(self,attack):
        pass
    
    def on_destruction(self):
        pass

    def attempt_identification(self,modifier=0):
        if self.target in Shell.shell.player.inventory or self.target in Shell.shell.player.limbs or self.target==Shell.shell.player:
            pass
        else:
            modifier-=10
        if Shell.shell.player.stats['per']*random.gauss(1,0.1)+modifier>self.detection_difficulty:
            self.detected=True
        if self.detected==True and Shell.shell.player.stats['per']*random.gauss(1,0.1)+modifier>self.identification_difficulty:
            self.identified=True


        

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
            i.floor=self

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

    def shadowcasting(self,visible_indices,start_location):
        visible_cells=[self.cells[start_location[0]][start_location[1]]]
        octants=[[],[],[],[],[],[],[],[]]
        translation_index1=0
        translation_index2=0
        #octant 1
        for i in visible_indices:
            for oct in octants:
                oct.append([])
            for j in i:
                for oct in octants:
                    for con in oct:
                        con.append([])
                #octant 1
                x1,y1=j[0]+start_location[0],j[1]+start_location[1]
                octants[0][translation_index1][translation_index2]=[x1,y1]

                #octant 2
                x2,y2=start_location[0]+j[1],start_location[1]+j[0]
                octants[1][translation_index1][translation_index2]=[x2,y2]

                #octant 3
                x,y=start_location[0]-j[1],start_location[1]+j[0]
                octants[2][translation_index1][translation_index2]=[x,y]

                #octant 4
                x,y=start_location[0]-j[0],start_location[1]+j[1]
                octants[3][translation_index1][translation_index2]=[x,y]

                #octant 5
                x,y=start_location[0]-j[0],start_location[1]-j[1]
                octants[4][translation_index1][translation_index2]=[x,y]

                #octant 6
                x,y=start_location[0]-j[1],start_location[1]-j[0]
                octants[5][translation_index1][translation_index2]=[x,y]

                #octant 7
                x,y=start_location[0]+j[1],start_location[1]-j[0]
                octants[6][translation_index1][translation_index2]=[x,y]

                #octant 8
                x,y=start_location[0]+j[0],start_location[1]-j[1]
                octants[7][translation_index1][translation_index2]=[x,y]

                translation_index2+=1
            translation_index1+=1
            translation_index2=0
        visible_cells.extend(self.shadow_octant(octants[0]))
        visible_cells.extend(self.shadow_octant(octants[1]))
        visible_cells.extend(self.shadow_octant(octants[2]))
        visible_cells.extend(self.shadow_octant(octants[3]))
        visible_cells.extend(self.shadow_octant(octants[4]))
        visible_cells.extend(self.shadow_octant(octants[5]))
        visible_cells.extend(self.shadow_octant(octants[6]))
        visible_cells.extend(self.shadow_octant(octants[7]))
        return visible_cells

    def shadow_octant(self,visible_indices,minslope=0,maxslope=1,startx=1,starty=0):
        visible_cells=[]
        opaque_encounter=False
        new_maxslope=maxslope
        next_minslope=minslope
        opening=False
        y_enc=False
        for x in range(startx,len(visible_indices)):
            opaque_encounter=False
            next_minslope=minslope
            try:
                for y in range(starty,len(visible_indices[x])):
                    lowslope=(y-0.5)/(x+0.5)
                    highslope=(y+0.5)/(x-0.5)
                    if highslope<minslope:
                        continue
                    if lowslope>maxslope:
                        break
                    try:
                        cell=self.cells[visible_indices[x][y][0]][visible_indices[x][y][1]]
                        visible_cells.append(cell)
                    except KeyError:

                        break

                    if cell.transparent:
                        opening=True
                        if opaque_encounter==False:
                    #Have not yet encountered an opaque cell. Continue onwards
                            continue
                    #or if we HAVE seen an opaque cell, set our minslope for the next iteration
                        elif next_minslope==minslope:
                            next_minslope=(y-0.5)/(x-0.5)
                            y_enc=y
                            continue

                    elif opaque_encounter==False:
                    #We have just found our first opaque cell
                        new_maxslope=lowslope
                        opaque_encounter=True
                        continue
                    elif next_minslope!=minslope:
                    #We have found a new batch of opaque cells. We need to start a new search.
                        visible_cells.extend(self.shadow_octant(visible_indices,next_minslope,lowslope,x+1,y_enc))
                        next_minslope=minslope
                        continue
            except IndexError: pass
            if opaque_encounter and next_minslope!=minslope and opening==True:
                visible_cells.extend(self.shadow_octant(visible_indices,next_minslope,maxslope,x+1,y_enc))
            maxslope=new_maxslope
            if maxslope<=0 or maxslope<minslope: return visible_cells
            opaque_encounter=False
            if opening==False:
                return visible_cells
            else: opening=False



        return visible_cells


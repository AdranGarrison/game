__author__ = 'Alan'

#from UI_Elements import *
import UI_Elements
import kivy
import random
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics.fbo import Fbo
from kivy.graphics import Canvas
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
import Shell
import Attacks as A
import Contamination
import re
#import Items
import copy
import queue
import functools
import MapTiles
import FloorGen
#import Deities




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

def targetchoice(defender):
    if isinstance(defender,Item) or isinstance(defender,Limb):
        return defender
    limbs = defender.limbs
    targetingsize = 0
    for limb in limbs:
        targetingsize += limb.sizefactor
    targetroll = random.uniform(0, targetingsize)
    target = None
    for limb in limbs:
        if targetroll <= limb.sizefactor:
            target = limb
            # Shell.messages.append("{}'s {} was hit!".format(limb.owner.name,limb.name))
            return limb
        elif target is None:
            targetroll = targetroll - limb.sizefactor





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
        self.statmodifiers={'s':0,'t':0,'p':0,'w':0,'l':0}
        self.grasp=False
        self.support=False
        self.sight=False
        self.hear=False
        self.smell=False
        self.ability=1
        self.painfactor=1
        self.plural=False
        self.contains_vitals=False
        self.severage_item=self
        self.image='./images/limb.png'
        self.location=[None,None]
        self.floor=None
        self.vision_blocking=False
        self.color=color
        self.passable=True
        self.targetable=False
        self.listed_in_limbs=True
        self.seen_by_player=False
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
        self.magic_contamination={'dark':0,'elemental':0,'summoning':0,'transmutation':0,'arcane':0,'total':0}
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
                pressure2=(self.armor.youngs)*(pressure*area)/(3*self.armor.shear*(self.armor.thickness*armor.function+area**0.5)**2)
                pressure=pressure/(1+((self.armor.thickness*self.armor.function)**2)/area)**0.5
                #print(pressure2,pressure)
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
                if self.owner in Shell.shell.player.visible_creatures: Shell.messages.append("The blow strikes an opening in the armor!")
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
                    pressure2=(layer.youngs)*(pressure*area)/(3*layer.shear*(layer.thickness*layer.function+area**0.5)**2)
                    pressure=pressure/(1+((layer.thickness*layer.function)**2)/area)**0.5
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
            if i.damage['cut']<1 and i.damage['break']<1 and i.damage['disintegrate']<1 and i.damage['burn']<1:
                severed=False
        if severed==True and self.owner!=None and self in self.owner.limbs:
            self.sever()
        else:
            self.updateability()

    def equip(self,item):
        for i in self.equipment:
            if self.equipment[i]==item:
                self.youngscalc()
                return
        if item.wield!='grasp':
            if self.can_equip(item)[0]:
                self.equipment[item.wield]=item
                self.owner.equipped_items.append(item)
                item.equipped.append(self)
                if item.mass:
                    self.movemass+=item.mass
                item.on_equip()
                self.youngscalc()
        if self.grasp==True:
            if item.wield=='grasp' and self.can_equip(item)[0]==True:
                if self.equipment['grasp'] is not None:
                    self.unequip('grasp')

                self.equipment['grasp']=item
                item.equipped.append(self)
                if item.mass:
                    self.movemass+=item.mass

                self.attacks=[]
                for i in item.attacks:
                    try: self.attacks.append(i(item,self))
                    except TypeError:
                        if isinstance(item,Limb):
                            item.attacks=[A.Strike_1H,A.Strike_2H]
                            for j in item.attacks: self.attacks.append(j(item,self))
                            break
                self.owner.equipped_items.append(item)
                item.on_equip()
                self.youngscalc()
        pass

    def unequip(self,slot,cascade=False,destroyed=False,drop=False,log=True):
        if not slot in self.equipment:
            if cascade==False:
                #print("no {} on {}".format(slot,self.name))
                pass
            return
        if slot=='grasp':
            self.attacks=self.defaultattacks
        if self.equipment[slot] is not None:
            #print(self.equipment[slot],self.equipment[slot].equipped)
            if cascade==False:
                if destroyed==False:
                    if drop==True:
                        #Need to drop item here
                        item=self.equipment[slot]
                        loc=[None,None]
                        loc[0]=min(max(self.owner.location[0]+int(random.gauss(0,3)),0),Shell.shell.dungeonmanager.current_screen.dimensions[0]-1)
                        loc[1]=min(max(self.owner.location[1]+int(random.gauss(0,3)),0),Shell.shell.dungeonmanager.current_screen.dimensions[1]-1)
                        try:
                            line=get_line(self.owner.location,loc)
                            loc=line[0]
                            if len(line)>1: line.pop(0)
                            for i in line:
                                if not any(j.passable==False for j in self.owner.floor.cells[i[0]][i[1]].dungeon):
                                    loc=i
                                else:
                                    line=get_line(self.owner.location,loc)
                                    break
                                if self.owner.floor.cells[i[0]][i[1]].passable==False:
                                    line=get_line(self.owner.location,loc)
                                    break
                            if any(self.owner.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                                self.owner.floor.animate_travel(item,self.owner.floor.cells[self.owner.location[0]][self.owner.location[1]],self.owner.floor.cells[loc[0]][loc[1]])
                            Clock.schedule_once(lambda dx: Shell.shell.dungeonmanager.current_screen.cells[loc[0]][loc[1]].contents.append(item),1/6)

                        except KeyError:
                            #print("Problematic")
                            Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]].contents.append(self)
                        if self.equipment[slot] in self.owner.inventory:
                            self.owner.inventory.remove(self.equipment[slot])
                        item.in_inventory=None
                        '''
                        if Shell.shell.dungeonmanager.current_screen.cells[self.equipment[slot].location[0]][self.equipment[slot].location[1]]:
                            if any(isinstance(x,MapTiles.Wall) for x in Shell.shell.dungeonmanager.current_screen.cells[self.equipment[slot].location[0]][self.equipment[slot].location[1]].contents):
                                Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]].contents.append(self.equipment[slot])
                            else:
                                Shell.shell.dungeonmanager.current_screen.cells[self.equipment[slot].location[0]][self.equipment[slot].location[1]].contents.append(self.equipment[slot])
                        else:
                            Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]].contents.append(self.equipment[slot])
                        if self.equipment[slot] in self.owner.inventory:
                            self.owner.inventory.remove(self.equipment[slot])
                        '''
                    elif self.equipment[slot] not in self.owner.inventory:
                        self.owner.inventory.append(self.equipment[slot])
                if self.equipment[slot].mass:
                    self.movemass-=self.equipment[slot].mass
                if log==True and destroyed==True:
                    if self in Shell.shell.player.visible_creatures: Shell.messages.append("The {} is destroyed!".format(self.equipment[slot].name))
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

    def manage_stats(self):
        if self.owner==None:
            return
        if self.natural:
            self.stats['s']=self.owner.stats['s']
            self.stats['t']=self.owner.stats['t']
            self.stats['p']=self.owner.stats['p']
            self.stats['w']=self.owner.stats['w']
            self.stats['l']=self.owner.stats['l']
        self.stats['str']=self.stats['s']+self.statmodifiers['s']+self.owner.statmodifiers['s']
        self.stats['tec']=self.stats['t']+self.statmodifiers['t']+self.owner.statmodifiers['t']
        self.stats['per']=self.stats['p']+self.statmodifiers['p']+self.owner.statmodifiers['p']
        self.stats['wil']=self.stats['w']+self.statmodifiers['w']+self.owner.statmodifiers['w']
        self.stats['luc']=self.stats['l']+self.statmodifiers['l']+self.owner.statmodifiers['l']

    def dex_calc(self):
        pass

    def balance_calc(self):
        pass

    def sever(self, primary=True,log=True):
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
            if self.natural==True and self in self.owner.limbs: #self.owner.missing_limbs.append(copy.copy(self))
                self.owner.missing_limbs.append(self.copyself())
            self.owner.pain+=75*self.painfactor
            if self.owner in Shell.shell.player.visible_creatures and self in self.owner.limbs and log==True: Shell.messages.append("{}'s {} is severed from the body!".format(self.owner.name,self.name))
            elif self in Shell.shell.player.visible_items and self.attachpoint!=None and log==True: Shell.messages.append("The {} is severed from the {}".format(self.name,self.attachpoint.name))
            if self.attachpoint:
                if self not in self.attachpoint.limbs:
                    print("Tried to remove {}'s {} from {} and failed".format(self.owner.name,self.name,self.attachpoint.name))
                    #print(self.attachpoint.limbs)
                else: self.attachpoint.limbs.remove(self)
            goahead=False
            if self.location not in (None,[None,None]):
                loc=[None,None]
                loc[0]=min(max(self.location[0]+int(random.gauss(0,2)),0),Shell.shell.dungeonmanager.current_screen.dimensions[0])
                loc[1]=min(max(self.location[1]+int(random.gauss(0,2)),0),Shell.shell.dungeonmanager.current_screen.dimensions[1])
                goahead=True
                startloc=self.location
                floor=self.floor
            elif self.owner.location is not None:
                loc=[None,None]
                loc[0]=min(max(self.owner.location[0]+int(random.gauss(0,2)),0),Shell.shell.dungeonmanager.current_screen.dimensions[0])
                loc[1]=min(max(self.owner.location[1]+int(random.gauss(0,2)),0),Shell.shell.dungeonmanager.current_screen.dimensions[1])
                goahead=True
                startloc=self.owner.location
                floor=self.owner.floor
            if goahead:
                try:
                    line=get_line(self.owner.location,loc)
                    loc=line[0]
                    if len(line)>1: line.pop(0)
                    for i in line:
                        if not any(j.passable==False for j in self.owner.floor.cells[i[0]][i[1]].dungeon):
                            loc=i
                        else:
                            line=get_line(startloc,loc)
                            break
                        if self.owner.floor.cells[i[0]][i[1]].passable==False:
                            line=get_line(startloc,loc)
                            break
                    if any(self.owner.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                        self.owner.floor.animate_travel(self,floor.cells[startloc[0]][startloc[1]],floor.cells[loc[0]][loc[1]])
                    Clock.schedule_once(lambda dx: floor.cells[loc[0]][loc[1]].contents.append(self.severage_item),1/6)
                except KeyError:
                    #print("Problematic")
                    Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]].contents.append(self.severage_item)
            self.on_destruction()
        if self.owner and self in self.owner.limbs:
            self.owner.limbs.remove(self)
            if self.attachpoint!=None:
                import Enchantments
                for i in self.attachpoint.layers:
                    if i.fluid!=None:
                        Enchantments.Bleeding(i,strength=3)
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
                i.recover(self.stats,fullheal=fullheal,turns=turns,**kwargs)
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
                        try:
                            if not any((i.weapon.equipped,i.name)==(j.weapon.equipped,j.name) for j in self.owner.attacks):
                                self.owner.attacks.append(i)
                            else: pass
                        except:
                            pass
        self.process_coatings()
        for i in self.enchantments:
            i.on_turn()
        for i in self.layers:
            i.on_turn()
        self.manage_stats()

    def on_strike(self,attack):
        if self.owner!=None and self.owner.alive: self.owner.on_strike(attack)
        for i in self.enchantments:
            i.on_strike(attack)
        pass

    def on_struck(self,attack):
        if self.owner!=None and self.owner.alive: self.owner.on_struck(attack)
        for i in self.enchantments:
            i.on_struck(attack)
        pass

    def on_destruction(self):
        for i in self.enchantments:
            i.on_destruction()

    def on_equip(self,**kwargs):
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

        if self.armor is not None and with_armor==True and random.random()<self.armor.coverage:
            new=self.armor.burn(temp,intensity,in_limb=True,limb=self)
            newmessage=new[0].capitalize()
            temp=new[1]
            intensity=new[2]
            message=''.join((message,newmessage))
            print(temp,intensity)
        for i in reversed(self.layers):
            chance=1-i.damage['burn']-i.damage['disintegrate']
            if random.random()>chance:
                continue
            old_damage=i.damage.copy()
            new=i.burn(temp,intensity,in_limb=True,limb=self)
            newmessage=new[0].capitalize()
            temp=new[1]
            intensity=new[2]
            message=''.join((message,newmessage))
            for j in ['burn','bend','dent','deform']:
                try: self.owner.pain+=(i.damage[j]-old_damage[j])*150*self.painfactor*i.painfactor/self.stats['wil']**0.5
                except AttributeError: pass
                except KeyError: pass
        if message!='' and log==True: Shell.messages.append(message)
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

    def copyself(self):
        limbtype=type(self)
        if hasattr(self,'boneradius'):
            boneradius=self.boneradius
        else:
            boneradius=0
        try: item=self.layers[0]
        except: item=None
        newlimb=limbtype(self.stats.copy(),length=self.length,radius=self.radius,natural=self.natural,owner=self.owner,boneradius=boneradius,item=item)
        newlimb.name=self.name
        if newlimb in self.owner.limbs: self.owner.limbs.remove(newlimb)
        if hasattr(self,'biting_surface'):
            newlimb.biting_surface=self.biting_surface
        if hasattr(self,'tip'):
            newlimb.tip=self.tip
        for i in self.limbs:
            if i.natural:
                attachedlimb=i.copyself()
                attachedlimb.join_to(newlimb)
        if self.owner is not None:
            self.owner.process_new_limb(newlimb)
        newlimb.can_attack=self.can_attack
        newlimb.attachpoint=self.attachpoint
        return newlimb

    def recalc_from_mass(self,mass=None,material=None,ratio=None):
        mass_proportions={}
        materials={}
        ratios={}
        uniform=False
        if mass==None:
            mass=self.mass
        for i in self.layers:
            mass_proportions[i]=i.mass/self.mass
            if material==None:
                materials[i]=i.material
            else:
                materials[i]=material
                uniform=True
            if ratio==None:
                ratios[i]=i.length/i.radius
            else:
                ratios[i]=ratio
        if uniform==False:
            newlayers=[]
            scale=(mass/self.mass)**(1/3)
            for i in self.layers:
                new=type(i)(length=i.length*scale,in_radius=i.in_radius*scale,out_radius=i.radius*scale,radius=i.radius*scale,material=i.material,quality=i.quality)
                newlayers.append(new)
            self.layers=newlayers
            self.youngscalc()
            self.mass_calc()

class Creature():
    def __init__(self,**kwargs):
        import Deities
        import Items
        import Materials
        self.basicname=''
        self.attacked=False
        self.enchantments=[]
        self.kills=[]
        self.location=[None,None]
        self.floor=None
        self.vision_blocking=False
        self.visible_cells=[]
        self.visible_creatures=[]
        self.detected_creatures=[]
        self.enemies=[]
        self.friendly=[]
        self.minions=[]
        self.master=None
        self.psychic_detected_creatures=[]
        self.visible_items=[]
        self.missing_limbs=[]
        self.gods=[]
        self.damage_level=0
        self.statmodifiers={'s':0,'t':0,'p':0,'w':0,'l':0}
        self.alive=True
        self.sizefactor=1
        self.tension=0
        self.pain=0
        self.oldpain=0
        self.recoverytime=0
        self.blood=[100,100]
        self.fatal_bleeding=True
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
        self.iprefs={'mass':-1,'length':1,'edge':1,'tip':1,'I':-1,'quality':1,'thickness':1,'type':[],'material':[],
                     'collection threshold':5,'weight threshold':170,'desired weapons':1,'wield preference':1,'enchantment':0}
        self.item_weights=[(Items.Bone,0),(Items.Flesh,0),(Items.Hair,0),(Items.LongSword,10),(Items.Gladius,5),
                           (Items.Knife,7),(Items.Saber,4),(Items.Claymore,4),(Items.Mace,8),(Items.WarHammer,3),
                           (Items.Spear,5),(Items.Axe,6),(Items.QuarterStaff,3),(Items.Chest,8),(Items.Glove,12),
                           (Items.Legging,12),(Items.Armlet,12),(Items.Boot,12),(Items.Helm,8),(Items.GreatHelm,3),
                           (Items.Shield,6),(Items.Buckler,6)]
        self.hard_material_weights=[(Materials.Iron,10),(Materials.Bone_Material,7),(Materials.Wood,10),(Materials.Copper,10),(Materials.Brass,6),
                                    (Materials.Bronze,5),(Materials.Steel,4),(Materials.Aluminum,3),(Materials.Silver,2),(Materials.Duraluminum,1),(Materials.Zicral,1)]
        self.soft_material_weights=[(Materials.Leather,10),(Materials.Cotton,10),(Materials.Wool,9),(Materials.Silk,5),(Materials.Spider_Silk,2),
                                    (Materials.Basalt_Fiber,1),(Materials.Fur,3),(Materials.Flesh_Material,1)]
        self.item_values={}
        self.equipped_items=[]
        self.inventory=[]
        self.conditions=[]
        self.balance_recovery=0
        self.classification=[]
        self.hostile=[]
        self.affinity={}
        self.limbs=[]
        self.path=[]
        self.indefinitename=''
        self.player=False
        self.target=None
        self.target_preference='random'
        self.preference_enforcement=False
        self.disabled_attack_types=[]
        self.disabled_attacks=[]
        self.abilities=[]
        self.magic_contamination={'dark':0,'elemental':0,'summoning':0,'transmutation':0,'arcane':0,'total':0}
        self.descriptor=''
        self.note=''
        #This is a placeholder. Gods should be different for different races
        self.gods.append(random.choice([Deities.istia,Deities.cypselus]))
        self.gods.append(random.choice([Deities.kolomae,Deities.medeina]))
        self.gods.append(random.choice([Deities.volos,Deities.zaephex]))
        for i in self.gods:
            i.add_follower(self)

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
            self.psychic_detected_creatures=[]

        #collapse from exhaustion if stamina runs too low
            if self.stamina[0]<self.stats['str']*random.gauss(4/self.stats['luc']**0.5,1/self.stats['luc']):
                if 'stamina_incapacitated' not in self.conditions:
                    self.conditions.append('stamina_incapacitated')
                    if self in Shell.shell.player.visible_creatures: Shell.messages.append('{} collapses from exhaustion'.format(self.name))
            elif 'stamina_incapacitated' in self.conditions:
                self.stamina[0]+=int(self.stats['str']**0.8)+1
                if (self.stats['str']*self.stats['luc'])**0.5>random.gauss(300,60)/self.stamina[0]:
                    self.conditions.remove('stamina_incapacitated')
                    if self in Shell.shell.player.visible_creatures: Shell.messages.append("{} recovers from exhaustion".format(self.name))
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
                    self.focus[0]=min(self.focus[0],self.focus[1])
                    self.focus[0]=max(self.focus[0],0)
            self.attacked=False
            self.combataction=False
            if self.blood[0]<self.blood[1]:
                self.blood[0]+=1


        #handle recovery of tension
            self.tension=max(min(self.tension,100),0)
            if self.tension>0: recover_tension=True
            else: recover_tension=False
            for i in self.detected_creatures:
                if self==i: continue
                if self.hostilitycheck(i) and self in i.detected_creatures and i.level-self.level>random.randint(-5,5):
                    if self.tension<100: self.tension+=1
                    recover_tension=False
            if recover_tension==True:
                self.tension-=1



        #If alive, recover, and test for senses
            self.damage_level=0
            for i in self.attacks:
                if i.disabled==True and i.sig not in self.disabled_attacks:
                    self.disabled_attacks.append(i.sig)
            self.sense_awareness()
            self.attacks=[]
            for i in self.limbs:
                i.on_turn()
                self.damage_level+=1-i.ability
            for i in self.attacks:
                if i.sig in self.disabled_attacks:
                    i.disabled=True
            self.damage_level=self.damage_level/len(self.limbs)






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
                        if self in Shell.shell.player.visible_creatures: Shell.messages.append('{} collapses in pain!'.format(self.name))
                    else:
                        self.pain=max(self.pain-self.pain*self.stats['wil']*0.005,0)
                elif 'pain_incapacitated' in self.conditions:
                    self.pain=max(self.pain-self.pain*self.stats['wil']*0.005,0)
                    if self.stats['luc']*self.stats['wil']>self.pain*random.gauss(1,0.4):
                        self.conditions.remove('pain_incapacitated')
                        if self in Shell.shell.player.visible_creatures: Shell.messages.append('{} recovers from the pain.'.format(self.name))
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
        if self.fatal_bleeding==True and self.blood[0]<=0:
            if self in Shell.shell.player.visible_creatures:
                if self.player==False: Shell.messages.append("{} has bled to death".format(self.name))
                else: Shell.messages.append("You have bled to death")
            self.die()
            return

    def equip(self,item,log=True,limb=None):
        item.in_inventory=self
        if limb!=None:
            if item.wield in limb.equipment and item.wield in limb.primaryequip:
                if limb.equipment[item.wield] is None and item.equipped==[]:
                    #print('equipping',item.name,'to',limb.name)
                    limb.equip(item)
                    if limb in item.equipped:
                        if item.wield=='grasp' and log==True:
                            if self in Shell.shell.player.visible_creatures: Shell.messages.append("{} is now held in {}".format(item.name,limb.name))
                        elif log==True:
                            if self in Shell.shell.player.visible_creatures: Shell.messages.append("{} is now equipped on {}".format(item.name,limb.name))
                        self.updateattacks()
                        self.mass_calc()
                        #print('equipped',item.name,'to',limb.name)
                        return
                elif limb.equipment[item.wield] is None and item.wield=='grasp' and len(item.equipped)>0:
                    limb.equip(item)
                    if log==True and self in Shell.shell.player.visible_creatures and limb in item.equipped:
                        Shell.shell.log.addtext("{} is now also held in {}".format(item.name,limb.name))
                    self.updateattacks()
                    self.mass_calc()
                    return
        for i in self.limbs:
            if item.wield in i.equipment and item.wield in i.primaryequip:
                if i.equipment[item.wield] is None and item.equipped==[]:
                    #print('equipping',item.name,'to',i.name)
                    i.equip(item)
                    if i in item.equipped:
                        if item.wield=='grasp' and log==True:
                            if self in Shell.shell.player.visible_creatures: Shell.messages.append("{} is now held in {}".format(item.name,i.name))
                        elif log==True:
                            if self in Shell.shell.player.visible_creatures: Shell.messages.append("{} is now equipped on {}".format(item.name,i.name))
                        self.updateattacks()
                        self.mass_calc()
                        #print('equipped',item.name,'to',i.name)
                        return
                elif i.equipment[item.wield] is None and item.wield=='grasp' and len(item.equipped)>0:
                    #print('equipping {} to {}'.format(item.name,i.name))
                    i.equip(item)
                    if log==True and self in Shell.shell.player.visible_creatures and i in item.equipped:
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

    def die(self,scatter=1,corpse=True,**kwargs):
        import Items
        #self.targetable=False
        self.alive=False
        self.hostile=[]
        self.passable=True
        items_to_drop=[]
        if self in Shell.shell.player.visible_creatures: Shell.messages.append("{} has been slain!".format(self.name))
        if self.player==True:
            Shell.messages.append("YOU HAVE DIED!")
        for i in self.inventory:
            self.unequip(i,log=False)
            items_to_drop.append(i)
        for i in items_to_drop:
            i.equipped=[]
            self.inventory.remove(i)
            loc=[self.location[0]+int(random.gauss(0,scatter)),self.location[1]+int(random.gauss(0,scatter))]
            line=get_line(self.location,loc)
            loc=line.pop(0)
            for j in line:
                if not any(j.passable==False for j in self.floor.cells[j[0]][j[1]].dungeon):
                    loc=j
                else:
                    line=get_line(self.location,loc)
                    break
                if self.floor.cells[j[0]][j[1]].passable==False:
                    line=get_line(self.location,loc)
                    break
            if any(self.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.floor.animate_travel(i,self.floor.cells[self.location[0]][self.location[1]],self.floor.cells[loc[0]][loc[1]])
            Clock.schedule_once(functools.partial(Shell.shell.dungeonmanager.current_screen.place_into_cell,i,loc),1/6)
        cell=self.floor.cells[self.location[0]][self.location[1]]
        if self in cell.contents: cell.contents.remove(self)
        if corpse: cell.contents.append(Items.Corpse(self))
        #self.floor.cells[self.location[0]][self.location[1]].on_contents(None,None)

    def choose_action(self):
        #start with non-turn-consuming actions
        for i in self.equipped_items:
            if hasattr(i,'sortingtype') and i.sortingtype=='weapon':
                if len(i.equipped)<self.iprefs['wield preference']:
                    self.equip(i)

        #decide if any abilities should be used
        random.shuffle(self.abilities)
        for i in self.abilities:
            chance=i.decide()
            if random.random()<chance[0]:
                i.enemy_activation()
                return

        #If no target, choose a target
        if self.target!=None and self.target not in self.detected_creatures:
            if random.random()>0.9:
                self.target=None
            elif len(self.path)>1:
                self.follow_path()
                return
            else: self.target=None
        if self.target!=None and self.target.alive==False:
            self.target=None
            self.path=[]
        if self.target==None:
            targetvalue=0
            for i in self.detected_creatures:
                if self.hostilitycheck(i) and i.alive:
                    if self.affinity[i]<targetvalue:
                        targetvalue=self.affinity[i]
                        self.target=i
        #If we have a target and it is visible, chase and kill
        if self.target!=None and self.target in self.detected_creatures:
            if self.path==[] or self.target not in self.path[0].contents:
                self.get_path(self.target.floor.cells[self.target.location[0]][self.target.location[1]])

            self.follow_path()
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
                    Shell.messages.append("{} equips {}".format(self.name,instructions[1].name))

        #If we are not in combat, maybe we should pick up some items
        #How many weapons are we currently wielding?
        equipped_weapons=0
        for i in self.equipped_items:
            if hasattr(i,'sortingtype') and i.sortingtype=='weapon':
                equipped_weapons+=1
        #take inventory of surrounding items
        for i in self.visible_items:
            if isinstance(i,Item) or isinstance(i,Limb): pass
            else: continue
            self.value_item(i)
            if hasattr(i,'wield') and self.movemass+i.mass<self.iprefs['weight threshold']:
                #See if it outvalues what we currently have equipped
                for j in self.limbs:
                    if i.wield in j.primaryequip:
                        if j.equipment[i.wield]==None and i.wield=='grasp':
                            #don't wield more weapons than you want
                            if hasattr(i,'sortingtype') and i.sortingtype=='weapon' and equipped_weapons>=self.iprefs['desired weapons']:
                                continue
                            #don't wield shields until you have the number of weapons you desire
                            elif hasattr(i,'sortingtype') and i.sortingtype=='armor' and equipped_weapons<self.iprefs['desired weapons']:
                                continue
                        if j.equipment[i.wield]==None or self.item_values[i]>self.item_values[j.equipment[i.wield]]:
                            #If we are standing on it, pick it up
                            if i.location==self.location:
                                self.inventory_add(i)
                                try: self.floor.cells[self.location[0]][self.location[1]].contents.remove(i)
                                except ValueError: pass
                                i.location=[None,None]
                                if j.equipment[i.wield]!=None:
                                    self.action_queue.append(['unequip',j.equipment[i.wield],j])
                                self.action_queue.append(['equip',i,j])
                            else:
                                self.get_path(self.floor.cells[i.location[0]][i.location[1]])
                                self.target=i
                                self.follow_path()
                                self.target=None
                            #self.chase(i)
                            return

        #Even if it's useless for us, take it if it is above collection threshold but won't put us over weight
            if self.movemass+i.mass<self.iprefs['weight threshold'] and self.item_values[i]>self.iprefs['collection threshold']:
                if i.location==self.location:
                    self.inventory_add(i)
                    try: self.floor.cells[self.location[0]][self.location[1]].contents.remove(i)
                    except: pass
                    i.location=[None,None]
                else: self.chase(i)
                return



        self.wander()

    def get_path(self,target):
        currentcell=self.floor.cells[self.location[0]][self.location[1]]
        searchables=queue.PriorityQueue()
        searchables.put((0,0,currentcell))
        camefrom={}
        cost={}
        camefrom[currentcell]=None
        cost[currentcell]=0
        steps=0

        while not searchables.empty():
            current=searchables.get()[2]
            #print(current.location,target.location)
            if current.location==target.location:
                break
            random.shuffle(current.immediate_neighbors)
            for next in current.immediate_neighbors:
                if next.passable==False and next.location!=target.location:
                    continue
                else:
                    newcost=cost[current]+next.movementcost_to+current.movementcost_from
                if next not in cost or newcost<cost[next]:
                    steps+=1
                    cost[next]=newcost
                    diag_distance=min(abs(target.location[0]-next.location[0]),abs(target.location[1]-next.location[1]))
                    cardinal_distance=max(abs(target.location[0]-next.location[0]),abs(target.location[1]-next.location[1]))-diag_distance
                    priority=newcost+diag_distance+cardinal_distance
                    #print(priority,steps,next.location)
                    searchables.put((priority,steps,next))
                    camefrom[next]=current
                if next.location==target.location:
                    continue
        #return camefrom
        self.path=[target]
        try:
            while hasattr(camefrom[self.path[len(self.path)-1]],'location'):
                self.path.append(camefrom[self.path[len(self.path)-1]])
            #print(self.path)
        except: self.path=[]

    def follow_path(self):
        #first make sure path is followable
        for i in self.path:
            if i.location in (self.path[0].location,self.path[len(self.path)-1].location): continue
            #If the path is blocked, try to path around it
            if not i.passable and self.target!=None:
                self.get_path(self.target.floor.cells[self.target.location[0]][self.target.location[1]])
                break
            #If we have no target, we have nothing to path to
            elif not i.passable:
                self.path=[]
                return
        #Make sure that, at minimum, the path has 2 points on it (start and end)
        if len(self.path)<2:
            return
        #If we get here, the path CAN be followed. So let's follow it
        currentcell=self.path.pop()
        movement=[self.path[-1].location[0]-currentcell.location[0],self.path[-1].location[1]-currentcell.location[1]]
        self.move(movement)
        if self.location==currentcell.location:
            self.path.append(currentcell)
        if len(self.path)==1: self.path=[]


        pass

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
        accuracy=1*(1+(50-self.tension)/200)
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
            accuracy*=1-len(unusable_attacks)/(5*len(self.attacks))
            hit_location=targetchoice(target)
            if hit_location is None:
                return
            attempts=0
            while pref not in hit_location.target_class and attempts<self.stats['tec']:
                retargeted=False
                for i in target.conditions:
                    if incapacitate.search(i):
                        hit_location=targetchoice(target)
                        retargeted=True
                if hit_location.ability<=0 and 'vital' not in hit_location.target_class:
                    if random.random()*self.stats['tec']>random.random()*(target.stats['per']**0.3)*(target.stats['luc']**0.3):
                        hit_location=targetchoice(target)
                        retargeted=True
                if random.random()*self.stats['tec']<random.random()*(target.stats['per']**0.3)*(target.stats['luc']**0.3) and retargeted==False:
                    break
                if retargeted==False:
                    hit_location=targetchoice(target)
                    accuracy=accuracy*0.9
                attempts+=1
            if self.preference_enforcement==True and pref not in hit_location.target_class:
                if not any(pref in i.target_class for i in target.limbs) and self.player==True:
                    Shell.messages.append('The target does not have any limbs matching your targeting preference')
                elif self.player==True:
                    Shell.messages.append('You cannot find an opening to attack your preferred target')
                return
            for i in self.attacks:
                if i.weapon==atk[attacksmade].weapon or i.limb==atk[attacksmade].limb:
                    unusable_attacks.append(i)
            if self.player==True:
                Shell.messages.append('You attack {} in the {} with {}'.format(target.name,hit_location.name,atk[attacksmade].name))
                atk[attacksmade].do(hit_location,accuracy=accuracy)
                self.attacked=True
                attacksmade+=1
            elif target.player==True:
                Shell.messages.append('{} attacks your {} with {}'.format(self.name,hit_location.name,atk[attacksmade].name))
                atk[attacksmade].do(hit_location,accuracy=accuracy)
                self.attacked=True
                attacksmade+=1
            else:
                if self in Shell.shell.player.visible_creatures: Shell.messages.append('{} attacks {} in the {} with {}'.format(self.name,target.name,hit_location.name,atk[attacksmade].name))
                atk[attacksmade].do(hit_location,accuracy=accuracy)
                self.attacked=True
                attacksmade+=1
            #test to see if another attack can be made
            self.tension=min(self.tension,100)
            if self.stats['tec']/attacksmade**0.8>random.triangular(0,1,self.tension/100)*target.stats['per']**2/(2*(self.stats['luc'])**0.3):
                atk.append(random.choice(self.attacks))
                if atk[attacksmade] in unusable_attacks:
                    endattack=True
            else:
                endattack=True

    def hostilitycheck(self,defender):
        if self.master!=None:
            if self.master.alive==False:
                self.affinity={}
            else:
                return self.master.hostilitycheck(defender)
        if defender.master==self:
            return False
        if defender not in self.affinity:
            self.affinity[defender]=0
            for i in self.hostile:
                if i in defender.classification:
                    self.affinity[defender]-=10
            for i in self.friendly:
                if i in defender.classification:
                    self.affinity[defender]+=4
        if self.affinity[defender]<0:
            return True
        else: return False
        #Old. Holding on to for the moment
        if defender in self.friends:
            return False
        if defender in self.allies:
            return False
        if defender==self.master:
            return False
        if defender in self.minions:
            return False
        elif defender in self.enemies:
            return True
        for i in self.classification:
            if i in defender.hostile:
                return True
        for i in defender.classification:
            if i in self.hostile:
                return True

        return False

    def evasion(self,attack,blockable=1,dodgeable=1,parryable=1,surprisable=1,exploitable=1,**kwargs):
        if not self.alive: return
        self.combataction=True
        parrytime=0
        blocktime=0
        dodgetime=0

        #incapacitated foes are unable to make even the most basic of evasive maneuvers and take much greater damage
        for i in self.conditions:
            if incapacitate.search(i) and exploitable>=random.random():
                attack.damagefactor*=attack.attacker.stats['tec']
                attack.arpen+=0.5
                if self.player: Shell.messages.append("You are defenseless!")
                elif self in Shell.shell.player.visible_creatures: Shell.messages.append('{} is defenseless!'.format(self.name))
                self.stamina[0]-=attack.basetarget.staminacost
                self.focus[0]-=attack.basetarget.staminacost
                return


        reactiontime=(1/(self.stats['per'])**0.5)*random.gauss(1-(self.stats['luc']**0.5)/100,0.2)*random.gauss((self.focus[1]/max(self.focus[0],1)),0.1)+self.recoverytime

        #Test to see if target can see or hear the attacker. If not, suffer a large penalty to reaction ability.
        if attack.attacker.stats['tec']*random.random()>self.vision:
            if attack.attacker.stats['tec']>self.hearing*random.random():
                reactiontime=reactiontime*(1+(40-self.esp)/self.stats['per'])

        if attack.time<reactiontime or "off_balance" in self.conditions and surprisable>=random.random():
            attack.damagefactor*=attack.attacker.stats['tec']**0.5
            if self in Shell.shell.player.visible_creatures: Shell.messages.append('The attack takes {} completely unaware!'.format(self.name))
            return
        elif attack.attacker not in self.detected_creatures and surprisable>=random.random():
            attack.damagefactor*=attack.attacker.stats['tec']**0.5
            if self in Shell.shell.player.visible_creatures: Shell.messages.append('The attack takes {} completely unaware!'.format(self.name))
            return

        #Attempt to dodge
        try:
            dodgetime=reactiontime+((self.focus[1]/(1+self.focus[0]))**0.5)*random.gauss(3/(self.stats['tec']*self.stats['luc']**0.5),.01)*(self.movemass**1.2/(self.stats['str']*max(self.stamina[0],1)/self.stamina[1]))*attack.accuracy*self.targetsize/(7*self.balance+0.01)
            if dodgetime<attack.time and random.random()*attack.attacker.stats['tec']<random.random()*self.stats['per'] and attack.dodgeable>=random.random():
                attack.dodged=True
                attack.attacker.tension+=1
                self.stamina[0]-=2*attack.basetarget.movemass/attack.basetarget.stats['str']
                #print("Attach dodged. Attack time of {} and dodge time of {}".format(attack.time,dodgetime))
                self.on_avoid(attack)
                return
        except ZeroDivisionError: pass

        #Attempt to block
        try:
            for i in self.equipped_items:
                if i.block==True and attack.blockable>=random.random():
                    encumbrance=0.1*(self.movemass-self.mass)/self.stats['str']
                    if len(i.equipped)==1:
                        if i.equipped[0].attachpoint is not None:
                            basemass=i.equipped[0].attachpoint.movemass+encumbrance
                            strength=i.equipped[0].attachpoint.stats['str']*self.stamina[0]/(self.stamina[1]+1)
                        else:
                            basemass=i.equipped[0].movemass+encumbrance
                            strength=i.equipped[0].stats['str']*self.stamina[0]/(self.stamina[1]+1)
                        tec=i.equipped[0].stats['tec']*self.focus[0]/(self.focus[1]+1)
                        blocktime=reactiontime+0.3*(self.targetsize/7)*attack.accuracy*((self.focus[1]/(self.focus[0]+1))**0.4)*random.gauss(1/(self.stats['luc']**0.5),.1)*(2*i.mass/strength**2+1/(tec*i.radius+0.5)**2+1/(tec/(2*i.mass+basemass*0.5)+1.57*strength*i.radius**2))
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
                        blocktime=reactiontime+0.3*(self.targetsize/7)*attack.accuracy*((self.focus[1]/(self.focus[0]+1))**0.4)*random.gauss(1/(self.stats['luc']**0.5),.1)*(2*i.mass/strength**2+1/(tec*i.radius+0.5)**2+1/(tec/(2*i.mass+basemass*0.5)+1.57*strength*i.radius**2))
                    elif len(i.equipped)<=0:
                        blocktime=1000000

                    #print("{} block time is {}. Blocking attack of time {}".format(i.name,blocktime,attack.time))
                    if blocktime<attack.time and random.random()*attack.attacker.stats['tec']<random.random()*self.stats['per']:
                        attack.blocked=True
                        attack.attacker.tension+=1
                        attack.target=i
                        #attack.basetarget=i
                        self.stamina[0]-=int(6*i.mass/strength)
                        luc=self.stats['luc']
                        attack.damagefactor*=1/random.triangular(1,(luc/(10+luc))*self.stats['tec']**0.5)
                        attack.strikearea*=50
                        attack.area*=50
                        self.on_avoid(attack)
                        return
        except ZeroDivisionError: pass


        #Attempt to parry
        for i in self.equipped_items:
            if i.parry==True and attack.parryable>=random.random():
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
                    attack.attacker.tension+=1
                    if attack.type=='pierce':
                        attack.type='crush'
                    attack.target=i
                    #attack.basetarget=i
                    luc=self.stats['luc']
                    attack.damagefactor*=0.05*(attack.attacker.stats['tec']/self.stats['tec'])/random.triangular(1,self.stats['tec'],(luc/(10+luc))*self.stats['tec'])
                    attack.strikearea*=5*tec**0.5
                    attack.area+=attack.area*4*tec**0.5
                    self.on_avoid(attack)
                    return
        #print('reaction time',reactiontime,'attacktime',attack.time,'dodge:',dodgetime,'parry',parrytime,'blocktime',blocktime)

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
        for i in self.enchantments:
            i.sense_modification()

        if self.vision<=0 and self.smell_sense<=0 and self.hearing<=0 and self.esp<=0 and 'mindless' not in self.classification:
            self.conditions.append('sensory_incapacitated')
        elif "sensory_incapacitated" in self.conditions:
            self.conditions.remove("sensory_incapacitated")
        self.check_visible_cells()

    def recover(self,fullheal=False,effect=1):
        for i in self.limbs:
            i.recover(fullheal=fullheal)

    def make_skeleton(self,terminal=False):
        import Items
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
        for i in self.enchantments:
            i.on_strike(attack)
        for i in self.gods:
            i.on_strike(self,attack)
        if attack.killingblow:
            self.on_kill(attack.basetarget.owner)
        pass

    def on_avoid(self,attack):
        for i in self.gods:
            i.on_avoid(self,attack)

    def on_struck(self,attack):
        if not self.alive: return
        self.hostilitycheck(attack.attacker)
        self.affinity[attack.attacker]-=1
        for i in self.enchantments:
            i.on_struck(attack)
        for i in self.gods:
            i.on_struck(self,attack)
        if attack.attacker!=self and self.hostilitycheck(attack.attacker)==False:
            self.enemies.append(attack.attacker)
            attack.attacker.enemies.append(self)

    def on_kill(self,creature):
        self.kills.append(creature)
        for i in self.gods:
            i.on_kill(self,creature)

    def on_ability_use(self,ability,**kwargs):
        for i in self.gods:
            i.on_ability_use(self,ability,**kwargs)
        for i in self.enchantments:
            i.on_ability_use(ability,**kwargs)
        return True

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
        import Enchantments
        self.visible_cells=[]
        self.vision_radius=2*(self.vision)**0.5
        outermost_points=[]
        radius_squared=self.vision_radius*self.vision_radius
        if self.player==False:
            self.visible_creatures=[]
            self.visible_items=[]
            self.detected_creatures=[]
            possible_detections=[]

            if self.floor.vision_check(self,Shell.shell.player)==True:
                possible_detections.append(Shell.shell.player)
            for i in self.floor.creaturelist:
                if self.floor.vision_check(self,i)==True:
                    possible_detections.append(i)
            for i in self.floor.itemlist:
                if self.floor.vision_check(self,i)==True:
                    self.visible_items.append(i)
            for i in possible_detections:
                if not any(isinstance(j,Enchantments.Stealth) for j in i.enchantments):
                    self.visible_creatures.append(i)
                elif i==self:
                    self.visible_creatures.append(i)
                else:
                    strength=0
                    for j in i.enchantments:
                        if isinstance(j,Enchantments.Stealth):
                            s=j.strength-j.get_bonus(self)
                            strength=(strength*strength+s*s)**0.5
                    if random.random()*self.stats['per']/self.floor.cells[i.location[0]][i.location[1]].distance_to(self.floor.cells[self.location[0]][self.location[1]])>strength:
                        print(i.name," is seen")
                        self.visible_creatures.append(i)


            self.detected_creatures.extend(self.visible_creatures)
            return


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
        for x in range(0,int(self.vision_radius*0.70710678)+1):
            visible_indices.append([])
            for y in range(0,x+1):
                visible_indices[x].append([x,y])
        for x in range(int(self.vision_radius*0.70710678)+1,int(self.vision_radius)+1):
            ymax=(radius_squared-x*x)**0.5
            visible_indices.append([])
            for y in range(0,int(ymax)+1):
                visible_indices[x].append([x,y])
        self.visible_cells=self.floor.shadowcasting(visible_indices,self.location)
        #print(self.visible_cells)
        #self.visible_cells=set(self.visible_cells)
        self.visible_creatures=[self]
        self.visible_items=[]
        for i in self.visible_cells:
            for j in i.creatures:
                if not any(isinstance(k,Enchantments.Stealth) for k in j.enchantments):
                    self.visible_creatures.append(j)
                    self.detected_creatures.append(j)
                    #print('unstealthed {} is seen'.format(j.name))
                elif j==self:
                    continue
                else:
                    strength=0
                    for k in j.enchantments:
                        if isinstance(k,Enchantments.Stealth):
                            s=k.strength-k.get_bonus(self)
                            strength=(strength*strength+s*s)**0.5
                    if random.random()*self.stats['per']/i.distance_to(self.floor.cells[self.location[0]][self.location[1]])>strength:
                        #print(j.name," is seen")
                        self.visible_creatures.append(j)
                        self.detected_creatures.append(j)


            #self.visible_creatures.extend(i.creatures)
            self.visible_items.extend(i.items)
            if self==Shell.shell.player:
                schedule_update=False
                if i.seen_by_player==False or i.fog or i.location==self.location:
                    schedule_update=True
                    #print('Update scheduled!',i.location)
                i.visible_to_player=True
                i.seen_by_player=True
                if schedule_update==True: i.update_graphics()
        if self==Shell.shell.player:
            for i in self.visible_items:
                if hasattr(i,'seen_by_player') and i.seen_by_player==False:
                    i.seen_by_player=True
                    i.generate_descriptions()
            for i in self.visible_creatures:
                i.seen_by_player=True
                for j in i.equipped_items:
                    if j.seen_by_player==False:
                        j.seen_by_player=True
                        j.generate_descriptions()
        self.detected_creatures=[]
        self.detected_creatures.extend(self.visible_creatures)
        self.detected_creatures.extend(self.psychic_detected_creatures)
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
        elif isinstance(item,Limb):
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

        if hasattr(item,'enchantments'):
            value+=self.iprefs['enchantment']*len(item.enchantments)

        for i in self.iprefs['type']:
            if isinstance(item,i[0]):
                value=max(value+i[1],value*i[1])

        for i in self.iprefs['material']:
            if hasattr(item,'material') and isinstance(item.material,i[0]):
                value=max(value+i[1],value*i[1])

        #print(item.name,value)
        self.item_values[item]=value

    def generate_equipment(self,items=1,item_weights=None,hard_materials=None,soft_materials=None,scale=None):
        import Items
        if item_weights==None:
            item_weights=self.item_weights
        if hard_materials==None:
            hard_materials=self.hard_material_weights
        if soft_materials==None:
            soft_materials=self.soft_material_weights
        if scale==None:
            scale=self.sizefactor
        totalweight=sum(i[1] for i in item_weights)
        choice_items=[]
        equipped_weapons=0
        for i in self.equipped_items:
            if hasattr(i,'sortingtype') and i.sortingtype=='weapon':
                equipped_weapons+=1
        for i in range(0,items):
            newitem=Items.weighted_generation(weighted_items=item_weights,totalweight=totalweight,hard_materials=hard_materials,soft_materials=soft_materials,size=scale)
            choice_items.append(newitem)
        print([i.name for i in choice_items])
        for i in choice_items:
            if isinstance(i,Item) or isinstance(i,Limb): pass
            else: continue
            self.value_item(i)
            if hasattr(i,'wield') and self.movemass+i.mass<self.iprefs['weight threshold']:
                #See if it outvalues what we currently have equipped
                for j in self.limbs:
                    if i.wield in j.primaryequip:
                        if j.equipment[i.wield]==None and i.wield=='grasp':
                            #don't wield more weapons than you want
                            if hasattr(i,'sortingtype') and i.sortingtype=='weapon' and equipped_weapons>=self.iprefs['desired weapons']:
                                continue
                            #don't wield shields until you have the number of weapons you desire
                            elif hasattr(i,'sortingtype') and i.sortingtype=='armor' and equipped_weapons<self.iprefs['desired weapons']:
                                continue
                        if j.equipment[i.wield]==None or self.item_values[i]>self.item_values[j.equipment[i.wield]]:
                            self.inventory_add(i)
                            i.location=[None,None]
                            if j.equipment[i.wield]!=None:
                                self.unequip(j.equipment[i.wield],log=False)
                            self.equip(i,limb=j,log=False)

    def process_new_limb(self,limb):
        for i in limb.layers:
            i.in_limb=limb

    def regrow_limb(self,limb):
        if limb not in self.missing_limbs:
            return
        self.limbs.append(limb)
        self.missing_limbs.remove(limb)
        limb.join_to(limb.attachpoint)

class Material():
    def __init__(self,**kwargs):
        self.wetdamage=None
        self.fluid=None
        self.identification_difficulty=15
        self.poisonable=False
        self.poison_resistance=0
        self.acid_reaction='corrode'
        self.acid_resistance=5
        self.heat_reaction='melt'
        self.burn_temp=1000
        self.heat_conduction=1
        self.burn_resistance=1
        self.note=''
        self.plasticity=0
        self.quality=1

    def damageresolve(self,attack,attacker,reactionforce=False):
        #if attacker.owner.player==True: print(self.name,attack.force,attack.pressure)
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
        if hasattr(attacker,'stats'):
            self.m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)
        else:
            self.m=min(5/defenderstats['luc'],1)
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
        if hasattr(attacker,'stats'): attackerstats=attacker.stats
        else:
            try:
                attackerstats=attacker.equipped[0].owner.stats
            except:
                attackerstats={'str':10,'tec':10,'per':10,'wil':10,'luc':10}
        if type(attack.pressure)==complex:
            return
        if attack.area<=0:
            return
        if attack.pressure>self.tensile_strength*300000*damagedobject.thickness / attack.area**0.5 and self.bruisable==True:
            severity=(attack.pressure/(self.tensile_strength*300000)-1)*random.gauss(0.5*attackerstats['luc']/defenderstats['luc'],0.5) * min(attack.area**0.5 / damagedobject.thickness,5)
            if attack.type=='cut' and self.contact==True and severity>10:
                severity=abs(random.gauss(((attack.force/(100*self.shear_strength+attack.force))*0.1/(self.shear_strength*damagedobject.thickness+0.1))
                                          *(attackerstats['tec']+0.2*attackerstats['luc'])/(defenderstats['luc']
                                            +0.2*defenderstats['tec']),0.4))
                damagedobject.damage['cut']=(damagedobject.damage['cut']**2+severity**2)**0.5
                if damagedobject.damage['cut']>=1: self.contact=True
                return

            elif attack.type=='pierce' and self.contact==True and severity>10:
                severity=abs(random.gauss(((attack.force/(10*self.shear_strength+attack.force))*0.2/(self.shear_strength*damagedobject.thickness+0.1))
                                          *(attackerstats['tec']+0.2*attackerstats['luc'])/(defenderstats['luc']
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
        assert damagedobject.mass>=0,(damagedobject,damagedobject.mass)
        shearforce=attack.force*(1/(3.5*(damagedobject.thickness+0.00000000001)*rootarea)-self.density*rootarea/(3.5*damagedobject.mass))#*0.0002/(0.0002+rootarea**2)
     #   if isinstance(attack.basetarget,Limb):
      #      assert damagedobject.mass>0,damagedobject
       #     shearforce=min(shearforce*(damagedobject.mass/attack.basetarget.movemass)**0.5,shearforce)
        if shearforce>self.shear_strength*1000000 and attack.contact==True and attack.type=='cut':
            failure_energy=((rootarea*self.thickness*self.shear*1000000000*self.shear_strength**2*self.thickness)/(self.shear_strength+80)**2)**0.5+\
                           self.fracture_energy*self.thickness*rootarea*1000
            #failure_energy=(rootarea*self.thickness*1000*self.shear_strength**2)/self.shear+\
            #               self.fracture_energy*self.thickness*rootarea*1000
            #print('attack energy:',attack.energy,'failure energy:',failure_energy)
            #severity=max(random.gauss((2*attack.energy/(4000000*self.fracture_energy*damagedobject.thickness*rootarea+attack.energy))
            #                              *(attacker.stats['tec']+0.2*attacker.stats['luc'])/(defenderstats['luc']
            #                                +0.2*defenderstats['tec']),0.2),0)
            severity=max(random.gauss((attack.energy/failure_energy)*(attacker.stats['tec']+0.2*attacker.stats['luc'])/
                                      (defenderstats['luc']+0.2*defenderstats['tec']),0.2),0)
            #print('cut severity:',severity)
            severity=min(severity,attack.cutlimit,1)
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
        if attack.pressure<=0:
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
            damagedobject.damage['pierce']=min(damagedobject.damage['pierce'],1.5)
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
        dentforce=max(min(attack.force*(damagedobject.mass/attack.basetarget.movemass)**0.5,attack.force),0)
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
        self.in_radius=0
        self.radius=0
        self.color=(1,1,1,1)
        self.name=''
        self.in_limb=None
        self.sortingtype='misc'
        if 'power' in kwargs:
            self.power=kwargs['power']
        else:
            self.power=1
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

        if attack.basetarget.owner!=None:
            defender=attack.basetarget.owner
        else:
            defender=attack.basetarget

        visible_things=[]
        visible_things.extend(Shell.shell.player.visible_creatures)
        visible_things.extend(Shell.shell.player.visible_items)

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
                if attacker in visible_things: Shell.messages.append("The attacker's {} is damaged!".format(name))
                attack.reaction_damage_processed=True

#Handling edge dulling through chipping or bending of the blade edge
        if self.damage['crush']==0 and self.damage['bend']<1.12 and self.damage['break']==0 and self.damage['shatter']==0 and self.damage['cut']<1:
            if hasattr(self,'edge') or hasattr(self,'tip'):
                if attack.oldtype=='cut' or attack.oldtype=='crush':
                    if self.damage['dent']>0 and hasattr(self,'edge'):
                        self.edge=self.edge*(1+self.damage['dent'])**0.5
                        if attacker in visible_things: Shell.messages.append("The edge of the {} is dulled".format(self.name))
                        self.damage['edgedull']+=(1+self.damage['dent'])**0.5-1
                        self.damage['dent']=0
                        return
                    if self.damage['crack']>self.olddamage['crack'] and hasattr(self,'edge'):
                        self.edge=self.edge*(1+self.damage['dent'])**0.5
                        if attacker in visible_things: Shell.messages.append("The edge of the {} is chipped".format(self.name))
                        self.damage['edgechip']+=(1+self.damage['dent'])**0.5-1
                        return
                elif attack.oldtype=='pierce' and reactionforce==True:
                    if self.damage['dent']>0:
                        self.tip=self.tip*(1+self.damage['dent'])**0.5
                        if attacker in visible_things: Shell.messages.append("The tip of the {} is dulled".format(self.name))
                        self.damage['tipdull']+=(1+self.damage['dent'])**0.5-1
                        self.damage['dent']=0
                        return
                    if self.damage['crack']>0:
                        self.tip=self.tip*(1+self.damage['crack'])**2
                        if attacker in visible_things: Shell.messages.append("The tip of the {} is chipped".format(self.name))
                        self.damage['tipchip']+=(1+self.damage['crack'])**2-1
                        self.damage['crack']=self.olddamage['crack']
                        return


        #test for crushing. If crushed, no other wounds need be recognized
        if self.damage['crush']>self.olddamage['crush']:
            attack.damage_dealt+=1
            if self.plural==False:
                if defender in visible_things: Shell.messages.append("The {} is crushed!".format(self.name))
            if self.plural==True:
                if defender in visible_things: Shell.messages.append("The {} are crushed!".format(self.name))
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
                if defender in visible_things: Shell.messages.append("The {} is shattered!".format(self.name))
            if self.plural==True:
                if defender in visible_things: Shell.messages.append("The {} are shattered!".format(self.name))
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
                if defender in visible_things: Shell.messages.append("The {} is broken!".format(self.name))
            if self.plural==True:
                if defender in visible_things: Shell.messages.append("The {} are broken!".format(self.name))
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
                self.fluid.splatter(intensity=(attack.energy**0.5)/15,volume=min(self.damage['cut']*3,5))
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
                if defender in visible_things: Shell.messages.append("The {} is {}".format(self.name,statement))
            if self.plural==True:
                if defender in visible_things: Shell.messages.append("The {} are {}".format(self.name,statement))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*50*self.damage['cut']/attack.basetarget.owner.stats['wil']**0.5
            if self.damage['cut']>=1:
                self.functioncheck()
                return


        #test for piercing. Piercing renders bruising irrelevant
        if self.damage['pierce']>self.olddamage['pierce'] and report_type==(self.damage['pierce']-self.olddamage['pierce'])*0.7:
            if self.fluid!=None:
                self.fluid.splatter(intensity=(attack.energy**0.5)/15,volume=min(3*self.damage['pierce'],8))
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
                if defender in visible_things: Shell.messages.append("The {} is {}".format(self.name,statement))
            if self.plural==True:
                if defender in visible_things: Shell.messages.append("The {} are {}".format(self.name,statement))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*30*self.damage['pierce']/attack.basetarget.owner.stats['wil']**0.5



        #Test for bruising.
        if self.damage['bruise']>self.olddamage['bruise'] and report_type==0:
            if self.damage['bruise']<4:
                if self.plural==False:
                    if defender in visible_things: Shell.messages.append('The {} is bruised'.format(self.name))
                if self.plural==True:
                    if defender in visible_things: Shell.messages.append('The {} are bruised'.format(self.name))
            elif self.damage['bruise']<7:
                if self.plural==False:
                    if defender in visible_things: Shell.messages.append('The {} is badly bruised!'.format(self.name))
                if self.plural==True:
                    if defender in visible_things: Shell.messages.append('The {} are badly bruised!'.format(self.name))
            elif self.damage['bruise']<10:
                if self.plural==False:
                    if defender in visible_things: Shell.messages.append('The {} is severely bruised and swells with blood!'.format(self.name))
                if self.plural==True:
                    if defender in visible_things: Shell.messages.append('The {} are severely bruised and swell with blood!'.format(self.name))
            elif self.damage['bruise']>=10:
                if self.plural==False:
                    if defender in visible_things: Shell.messages.append('The structure of the {} collapses under the impact!'.format(self.name))
                if self.plural==True:
                    if defender in visible_things: Shell.messages.append('The structure of the {} collapse under the impact!'.format(self.name))
                self.damage['crush']=1
                if self.fluid!=None:
                    self.fluid.splatter(intensity=(attack.energy**0.5)/15,volume=4)
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
                if defender in visible_things: Shell.messages.append("The {} is bent!".format(self.name))
            if self.plural==True:
                if defender in visible_things: Shell.messages.append("The {} are bent!".format(self.name))
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
                if defender in visible_things: Shell.messages.append("The {} is dented!".format(self.name))
            if self.plural==True:
                if defender in visible_things: Shell.messages.append("The {} are dented!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*100*self.damage['dent']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return
        elif self.damage['dent']>self.olddamage['dent'] and report_type==0:
            attack.damage_dealt+=1
            if self.plural==False:
                if defender in visible_things: Shell.messages.append("The {} is further dented!".format(self.name))
            if self.plural==True:
                if defender in visible_things: Shell.messages.append("The {} are further dented!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*150*self.damage['dent']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return



        #test for cracks and update function accordingly
        if self.damage['crack']>self.olddamage['crack'] == 0 and report_type==self.damage['crack']-self.olddamage['crack']:
            attack.damage_dealt+=1
            if self.plural==False:
                if defender in visible_things: Shell.messages.append("The {} is cracked!".format(self.name))
            if self.plural==True:
                if defender in visible_things: Shell.messages.append("The {} are cracked!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*100*self.damage['crack']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return
        elif self.damage['crack']>self.olddamage['crack'] and report_type==self.damage['crack']-self.olddamage['crack']:
            attack.damage_dealt+=1
            if self.plural==False:
                if defender in visible_things: Shell.messages.append("The {} cracks further!".format(self.name))
            if self.plural==True:
                if defender in visible_things: Shell.messages.append("The {} crack further!".format(self.name))
            if isinstance(attack.basetarget,Limb) and self in attack.basetarget.layers:
                attack.basetarget.owner.pain+=pain*100*self.damage['crack']/attack.basetarget.owner.stats['wil']**0.5+2
            self.functioncheck()
            return
        self.functioncheck()
        attack.damage_dealt-=1

    def process_coatings(self,limb,log=True,log_override=False):
        #This method is only called for coatings on an item which is part of a limb
        self.olddamage=self.damage.copy()
        for i in self.coatings:
            i.process(log=False,limb=limb)
        pain=self.painfactor*limb.painfactor

        if not log_override:
            if limb.owner in Shell.shell.player.visible_creatures and limb in limb.owner.limbs:
                log=True
            elif limb in Shell.shell.player.visible_items:
                log=True
            else:
                log=False
        if self.olddamage['rust']<self.damage['rust'] and log==True:
            if self.olddamage==0:
                if limb.owner!=Shell.shell.player:
                    Shell.messages.append("The {} on {}'s {} rusts. ".format(self.name,limb.owner.name,limb.name))
                else:
                    Shell.messages.append("The {} on your {} rusts. ".format(self.name,limb.name))
            else:
                if limb.owner!=Shell.shell.player:
                    Shell.messages.append("The {} on {}'s {} rusts further. ".format(self.name,limb.owner.name,limb.name))
                else:
                    Shell.messages.append("The {} on your {} rusts further. ".format(self.name,limb.name))

        if self.olddamage['disintegrate']<self.damage['disintegrate']:
            if limb.owner!=Shell.shell.player and log==True:
                Shell.messages.append("The {} on {}'s {} dissolves! ".format(self.name,limb.owner.name,limb.name))
            elif log==True:
                Shell.messages.append("The {} on your {} dissolves! ".format(self.name,limb.name))
            limb.owner.pain+=pain*200/limb.owner.stats['wil']**0.5


        elif self.olddamage['corrode']<self.damage['corrode']:
            if limb.owner!=Shell.shell.player and log==True:
                Shell.messages.append("The {} on {}'s {} is burned by the acid! ".format(self.name,limb.owner.name,limb.name))
            elif log==True:
                Shell.messages.append("The {} on your {} is burned by the acid! ".format(self.name,limb.name))
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
        if self.olddamage!=self.damage:
            limb.updateability()

    def recover(self,stats,turns=1,fullheal=False,**kwargs):
        safe=False
        if 'divine_healing' in kwargs: safe=True
        if fullheal==True:
            print(self.name)
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
            self.damage['bruise']-=min(self.damage['bruise'],turns*self.damage['bruise']*random.random()*stats['luc']/200)
        if self.damage['crack']>0:
            self.damage['crack']-=min(self.damage['crack'],turns*random.random()*stats['luc']/500)
        if self.damage['break']>0 and self.damage['shatter']==0:
            for i in range(0,turns):
                if stats['luc']>random.uniform(0,100):
                    self.breakcounter+=1
                if self.breakcounter>100:
                    self.damage['break']=0
                    self.breakcounter=0
        if self.damage['shatter']>0:
            for i in range(0,turns):
                if stats['luc']>random.triangular(0,200,200):
                    self.damage['shatter']=0
                    self.damage['break']=1
                    permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                    if safe==False: self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
                    break
        if self.damage['crush']>0:
            for i in range(0,turns):
                if stats['luc']>random.triangular(0,200,200):
                    self.damage['crush']=0
                    if self.material.mode=='soft':
                        self.damage['bruise']=20
                    if self.material.mode=='brittle':
                        self.damage['break']=1
                    if self.material.mode=='ductile':
                        self.damage['bend']=1
                    permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                    if safe==False: self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
                    break
        if self.damage['cut']>0:
            for i in range(0,turns):
                if stats['luc']>random.uniform(0,100):
                    self.damage['cut']-=min(self.damage['cut'],self.damage['cut']*random.random()*stats['luc']/100)
                if self.damage['cut']>0.8:
                    if stats['luc']*random.random()<0.005:
                        permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                        if safe==False: self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
                        self.damage['cut']=0.8
        if self.damage['pierce']>0:
            for i in range(0,turns):
                if stats['luc']>random.uniform(0,100):
                    self.damage['pierce']-=min(self.damage['pierce'],self.damage['pierce']*random.random()*stats['luc']/100)
        if self.damage['corrode']>0:
            self.thickness=min(self.base_thickness,self.base_thickness+turns*random.random()*0.001)
            self.radius=min(self.base_radius,self.base_radius+turns*random.random()*0.001)
            for i in range(0,turns):
                self.damage['corrode']=1-min((self.thickness+0.00001)/(self.base_thickness+0.00001),(self.radius+0.00001)/(self.base_radius+0.00001))
        if self.damage['disintegrate']>0:
            for i in range(0,turns):
                if stats['luc']>random.uniform(0,100):
                    self.regrowthcounter+=1
                if self.regrowthcounter>100:
                    self.damage['disintegrate']=0
                    self.damage['corrode']=1
                    self.recalc()
                    self.regrowthcounter=0
                    permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                    if safe==False: self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
                    break
        if self.damage['bend']>0:
            for i in range(0,turns):
                if stats['luc']>random.uniform(0,500):
                    self.damage['bend']=0
                    self.damage['dent']=1
                    permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                    if safe==False: self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
                    break
        if self.damage['dent']>0:
            for i in range(0,turns):
                if stats['luc']>random.uniform(0,100):
                    self.damage['dent']-=min(self.damage['dent'],self.damage['dent']*random.random()*stats['luc']/100)
        if self.damage['burn']>=1:
            for i in range(0,turns):
                if stats['luc']/(100+stats['luc'])>random.triangular(0,1,1):
                    self.damage['burn']-=0.01*stats['luc']/15
                if self.damage['burn']<1 and safe==False:
                    permanent_injury=min(max(random.gauss(2/stats['luc'],1/stats['luc']),0),1/stats['luc']**0.5)
                    self.damage['deform']=(self.damage['deform']**2+permanent_injury**2)**0.5
        elif self.damage['burn']>0: self.damage['burn']-=min(turns*0.01*stats['luc']/15,self.damage['burn'])

        self.functioncheck()

    def acid_burn(self,strength,log=True,log_override=False):
        if not log_override:
            if self in Shell.shell.player.visible_items:
                log=True
            elif self in Shell.shell.player.inventory and Shell.shell.player.can_see:
                log=True
            elif any(self in i.equipped_items for i in Shell.shell.player.visible_creatures):
                log=True
            else:
                log=False
        message=''
        if self.damage['disintegrate']>=1 or self.acid_reaction=='indestructable':
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
                    if log==True: Shell.messages.append('The {} is dissolved by the acid'.format(self.name))
                    self.functioncheck()
                    return
                else:
                    message='The acid corrodes the {}'.format(self.name)
            if hasattr(self,'head') and burnseverity>0.1:
                self.head-=burnseverity/500
                if self.head<=0:
                    self.head=0
                    self.damage['disintegrate']=1
                    if log==True: Shell.messages.append('The {} is dissolved by the acid'.format(self.name))
                    self.functioncheck()
                    return
                else:
                    message='The acid corrodes the {}'.format(self.name)
            if hasattr(self,'radius') and burnseverity>0.1:
                self.radius-=burnseverity/500
                if self.radius<=0:
                    self.radius=0
                    self.damage['disintegrate']=1
                    if log==True: Shell.messages.append('The {} is dissolved by the acid'.format(self.name))
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
                    Shell.messages.append(message)
                elif self.equipped[0].owner==Shell.shell.player:
                    Shell.messages.append(message.replace(' the ',' your ',1))
                elif self.equipped[0].owner!=None:
                    Shell.messages.append(message.replace(' the '," {}'s ").format(self.equipped[0].owner.name))

    def burn(self,temp,intensity=1,in_limb=False,limb=None,log=True,log_override=False):
        if self.heat_reaction=='indestructable': return
        if not log_override and in_limb==False:
            if self in Shell.shell.player.visible_items:
                log=True
            elif self in Shell.shell.player.inventory and Shell.shell.player.can_see:
                log=True
            elif any(self in i.equipped_items for i in Shell.shell.player.visible_creatures):
                log=True
            else:
                log=False
        elif not log_override and in_limb==True:
            if limb in Shell.shell.player.limbs:
                log=True
            elif limb in Shell.shell.player.visible_items:
                log=True
            elif any(limb in i.limbs for i in Shell.shell.player.visible_creatures):
                log=True
            else:
                log=False
        message=''
        ignition=False
        removed_coatings=[]
        for i in self.coatings:
            if i.flammable==True:
                if in_limb==False:
                    Shell.messages.append('the {} on the {} catches fire! '.format(i.name,self.name))
                    temp+=random.random()*temp
                    intensity+=3*random.random()
                    removed_coatings.append(i)
                else:
                    Shell.messages.append('the {} coating on the {} of the {} catches fire! '.format(i.name,self.name,limb.name))
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
                message='the {} is consumed in flames! '.format(self.name)
            else:
                message='the {} on the {} is consumed in flames! '.format(self.name,limb.name)
            self.damage['burn']=1
            ignition=True
            #need to destroy object and add to the flames
        elif self.heat_reaction=='burn' or self.heat_reaction=='ignite':
            severity=(burn_severity**2+self.damage['burn']**2)**0.5
            if severity>=1:
                if in_limb==False:
                    message='the {} is burned to ash by the heat! '.format(self.name)
                else:
                    message='the {} on the {} is burned to ash by the heat! '.format(self.name,limb.name)
                self.damage['burn']=1
            elif severity>=0.7:
                if in_limb==False:
                    message='the {} is badly burned by the heat. '.format(self.name)
                else:
                    message='the {} on the {} is badly burned by the heat. '.format(self.name,limb.name)
                self.damage['burn']=severity
            elif severity>0.4:
                if in_limb==False:
                    message='the {} is burned by the heat. '.format(self.name)
                else:
                    message='the {} on the {} is burned by the heat. '.format(self.name,limb.name)
                self.damage['burn']=severity
            elif severity>0.05:
                if in_limb==False:
                    message='the {} is scorched by the heat. '.format(self.name)
                else:
                    message='the {} on the {} is scorched by the heat. '.format(self.name, limb.name)
                self.damage['burn']=severity
        elif self.heat_reaction=='melt':
            severity=(burn_severity**2+self.damage['burn']**2)**0.5
            if severity>=1:
                if in_limb==False:
                    message='the {} is melted by the heat! '.format(self.name)
                    self.heat_conduction=500
                else:
                    message='the {} on the {} is melted by the heat! '.format(self.name,limb.name)
                    self.heat_conduction=500
                self.damage['burn']=1
            elif severity>=0.7:
                if in_limb==False:
                    message='the {} is deformed by the heat. '.format(self.name)
                else:
                    message='the {} on the {} is deformed by the heat. '.format(self.name,limb.name)
                self.damage['bend']+=abs(random.gauss(0,0.1))
                self.damage['deform']+=abs(random.gauss(0,0.1))
                self.tensile_strength=self.tensile_strength*(1-random.gauss(0,0.1)**2)
                self.shear_strength=self.shear_strength*(1-random.gauss(0,0.1)**2)
                self.material.tensile_strength=self.tensile_strength
                self.material.shear_strength=self.shear_strength
            elif severity>0.4:
                if in_limb==False:
                    message='the {} is damaged by the heat. '.format(self.name)
                else:
                    message='the {} on the {} is damaged by the heat. '.format(self.name,limb.name)
                if severity>random.random(): self.damage['bend']+=abs(random.gauss(0,0.1))
                if severity>random.random():
                    self.tensile_strength=self.tensile_strength*(1-random.gauss(0,0.1)**2)
                    self.material.tensile_strength=self.tensile_strength
                if severity>random.random():
                    self.shear_strength=self.shear_strength*(1-random.gauss(0,0.1)**2)
                    self.material.shear_strength=self.shear_strength
            elif severity>0.05:
                if in_limb==False:
                    message='the {} is softened by the heat. '.format(self.name)
                else:
                    message='the {} on the {} is softened by the heat. '.format(self.name, limb.name)
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
            Shell.messages.append(message)

    def on_equip(self):
        for i in self.enchantments:
            i.on_equip()

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
        if attack.killingblow:
            self.kills.append(attack.basetarget.owner)

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
        self.poisonable=self.material.poisonable
        self.poison_resistance=self.material.poison_resistance
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

    def full_identify(self):
        self.knowledge_level={'truename':1,'name':2,'material':2,'mass':2,'length':2,'moment of inertia':2,'edge':2,'tip':2,
                              'thickness':2,'force delivery':2,'cutting effectiveness':2,'piercing effectivemess':2,'quality':2,
                              'magic':2,'special':2,'radius':2}
        self.generate_descriptions()

    def randomize(self,stdev=0.1,material_set=None):
        old_in_inventory=self.in_inventory
        old_inventory_index=self.inventory_index
        touched=self.touched_by_player
        seen=self.seen_by_player
        loc=self.location
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
        if hasattr(self,'in_radius'):
            r['in radius']=self.in_radius*random.triangular(0.5,2,1)
            if self.equipped!=[]:
                self.in_radius=max(self.equipped[0].radius,self.in_radius)
                self.in_radius=min(self.equipped[0].radius*2,self.in_radius)
        else: r['in radius']=None
        if hasattr(self,'quality'): r['quality']=self.quality*random.triangular(0.2,5,1)
        else: r['quality']=None

        self.material=type(self.material)
        if material_set==None:
            pass
        else:
            self.material=random.choice(material_set)
        equipped=self.equipped.copy()
        self.__init__(painfactor=self.painfactor,length=r['length'],thickness=r['thickness'],edge=r['edge'],tip=r['tip'],
                      head=r['head'],headvolume=r['headvolume'],headsize=r['headsize'],width=r['width'],in_radius=r['in radius'],
                      quality=r['quality'],material=self.material,power=self.power)
        self.equipped=equipped
        self.in_inventory=old_in_inventory
        self.inventory_index=old_inventory_index
        self.seen_by_player=seen
        self.touched_by_player=touched
        self.location=loc
        self.generate_descriptions(per=Shell.shell.player.stats['per'])


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
        self.magic_contamination={'dark':0,'elemental':0,'summoning':0,'transmutation':0,'arcane':0,'total':0}

    def process(self,**kwargs):
        pass

    def remove(self,**kwargs):
        if self.on!= None:
            self.on.coatings.remove(self)
        else:
            try: self.floor.cells[self.location[0]][self.location[1]].contents.remove(self)
            except: pass
            '''
            for i in Shell.shell.dungeonmanager.current_screen.nonindexedcells:
                if self in i.contents:
                    i.contents.remove(self)'''
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
        try: self.owner.blood[0]-=volume
        except: pass
        if self.owner.alive==False:
            return
        targets=0
        while targets<volume:
            newsplatter=copy.copy(self)
            newsplatter.location=[None,None]
            if self.owner.location is not None:
                newsplatter.location[0]=min(max(self.owner.location[0]+int(random.gauss(0,intensity)),0),Shell.shell.dungeonmanager.current_screen.dimensions[0])
                newsplatter.location[1]=min(max(self.owner.location[1]+int(random.gauss(0,intensity)),0),Shell.shell.dungeonmanager.current_screen.dimensions[1])
                line=get_line(self.owner.location,newsplatter.location)
                newsplatter.location=line.pop(0)
                for i in line:
                    newsplatter.location=i
                    if self.owner.floor.cells[i[0]][i[1]].passable==False:
                        break
                line=get_line(self.owner.location,newsplatter.location)
                try: loc=Shell.shell.dungeonmanager.current_screen.cells[newsplatter.location[0]][newsplatter.location[1]]
                except KeyError: loc=Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]]
                if loc:
                    if loc.contents!=[]:
                        splattertarget=random.choice(loc.contents)
                        if splattertarget==self.owner and not any(i.name==self.name for i in loc.contents): loc.contents.append(newsplatter)
                        elif isinstance(splattertarget,Creature):
                            try: splattertarget=random.choice(splattertarget.limbs)
                            except IndexError: splattertarget=None
                        if any(self.owner.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                            self.owner.floor.animate_travel(newsplatter,self.owner.floor.cells[self.owner.location[0]][self.owner.location[1]],loc)
                        Clock.schedule_once(lambda dx: self.add(splattertarget),1/6)
                    elif not any(i.name==self.name for i in loc.contents):
                        if any(self.owner.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                            self.owner.floor.animate_travel(newsplatter,self.owner.floor.cells[self.owner.location[0]][self.owner.location[1]],loc)
                        Clock.schedule_once(lambda dx: loc.contents.append(newsplatter),1/6)
                        print(newsplatter)

                else:
                    Shell.shell.dungeonmanager.current_screen.cells[self.owner.location[0]][self.owner.location[1]].contents.append(newsplatter)

            targets+=1

    def burn(self,temp,intensity,**kwargs):
        if random.random()>0.5 and self.evaporate==True:
            self.remove()

    def on_turn(self,**kwargs):
        if random.random()<0.01:
            self.remove()
        pass

    def on_strike(self,attack,**kwargs):
        for i in attack.touchedobjects:
            if random.random()>0.9:
                self.add(i)

    def on_struck(self,attack,**kwargs):
        if random.random()>0.9:
            try: self.add(attack.weapon)
            except AttributeError:
                try: self.add(attack.limb)
                except AttributeError: pass

class Enchantment():
    def __init__(self,target,turns='permanent',combination_type="pythagorean",turn_type='max',strength=6,combine=True,**kwargs):
        self.target=target
        self.turns=turns
        self.category='magic'
        self.classification=['magic']
        self.display=True
        self.detected=False
        self.identified=False
        self.detection_difficulty=20
        self.identification_difficulty=30
        if not hasattr(target,"enchantments"):
            return
        if combine==False:
            self.target.enchantments.append(self)
            return
        for i in target.enchantments:
            if type(i)==type(self):
                if combination_type=='pythagorean':
                    newstrength=(i.strength*i.strength+strength*strength)**0.5
                    i.strength=max(i.strength+1,int(newstrength))
                elif combination_type=='sum':
                    i.strength+=strength
                elif combination_type=='max':
                    i.strength=max(i.strength,strength)
                if i.turns=='permanent':
                    pass
                elif turns=='permanent':
                    i.turns='permanent'
                elif turn_type=='max':
                    i.turns=max(turns,i.turns)
                elif turn_type=='pythagorean':
                    newturns=(i.turns*i.turns+turns*turns)**0.5
                    i.turns=max(i.turns+1,int(newturns))
                elif turn_type=='sum':
                    i.turns+=turns
                return
        self.target.enchantments.append(self)

    def on_turn(self):
        if self.turns=='permanent':
            pass
        else:
            self.turns-=1
            if self.turns<=0:
                self.on_removal()
                self.target.enchantments.remove(self)
        if self.detected==False or self.identified==False:
            self.attempt_identification()
            
    def on_strike(self,attack):
        pass
    
    def on_struck(self,attack):
        pass
    
    def on_destruction(self):
        pass

    def on_dispel(self,**kwargs):
        pass

    def on_equip(self):
        pass

    def attack_modification(self,attack,**kwargs):
        pass

    def on_ability_use(self,ability,**kwargs):
        if 'magic' in ability.classification:
            self.on_magic_use(ability,**kwargs)

    def on_magic_use(self,ability,**kwargs):
        pass

    def sense_modification(self):
        pass

    def attempt_identification(self,modifier=0):
        if isinstance(self.target,Item):
            if self.target.in_inventory in Shell.shell.player.visible_creatures or self.target in Shell.shell.player.visible_items:
                pass
            else:
                return
            if self.target in Shell.shell.player.inventory or self.target in Shell.shell.player.limbs or self.target==Shell.shell.player:
                pass
            else:
                modifier-=10
            if Shell.shell.player.stats['per']*random.gauss(1,0.1)+modifier>self.detection_difficulty:
                self.detected=True
            if self.detected==True and Shell.shell.player.stats['per']*random.gauss(1,0.1)+modifier>self.identification_difficulty:
                self.identified=True
        if isinstance(self.target,Creature):
            if self.target not in Shell.shell.player.visible_creatures:
                return
            if Shell.shell.player.stats['per']*random.gauss(1,0.1)+modifier>self.detection_difficulty:
                self.detected=True
            if self.detected==True and Shell.shell.player.stats['per']*random.gauss(1,0.1)+modifier>self.identification_difficulty:
                self.identified=True

    def on_removal(self,**kwargs):
        self.on_dispel(**kwargs)


class Deity():
    def __init__(self):
        self.name=''
        self.followers=[]
        self.favor={}
        self.alignment='N'
        pass

    def add_follower(self,follower):
        self.followers.append(follower)
        self.favor[follower]=0

    def invoke(self,power,**kwargs):
        pass

    def on_turn(self):
        for i in self.followers:
            if not i.alive:
                self.followers.remove(i)
                del self.favor[i]
            elif self.favor[i]<0 and i.stats['luc']>random.randint(0,1000):
                self.favor[i]+=1

    def on_strike(self,follower,attack):
        pass

    def on_struck(self,follower,attack):
        pass

    def on_kill(self,follower,creature):
        pass

    def on_ability_use(self,follower,ability):
        pass

    def on_avoid(self,follower,attack):
        pass



class Floor(Screen):
    def __init__(self,name,max_x=60,max_y=60,generator=FloorGen.experimental_automaton,*args,**kwargs):
        super().__init__(name=name,**kwargs)
        self.stored_keyboard_mode='play'
        self.animations={}
        self.name=name
        self.itemlist=[]
        UI_Elements.floors[str(name)]=self
        self.cells={}
        self.dimensions=[max_x,max_y]
        self.nonindexedcells=[]
        self.creaturelist=[]
        cellsize=UI_Elements.cellsize
        dungeonmanager=UI_Elements.dungeonmanager
        for i in range(0,max_x):
            self.cells[i]={}
            for j in range(0,max_y):
                self.cells[i][j]=UI_Elements.Cell(size=(cellsize,cellsize),pos=(i*cellsize,j*cellsize))
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
    
        generator(self)
        for i in self.nonindexedcells:
            i.on_contents(None,None)
            i.floor=self
        upstair_location=[None,None]
        while upstair_location==[None,None]:
            newloc=[random.randint(0,max_x-1),random.randint(0,max_y-1)]
            if self.cells[newloc[0]][newloc[1]].passable:
                upstair_location=newloc
        MapTiles.Upstair(self,upstair_location[0],upstair_location[1])
        downstair_location=[None,None]
        while downstair_location==[None,None]:
            newloc=[random.randint(0,max_x-1),random.randint(0,max_y-1)]
            if self.cells[newloc[0]][newloc[1]].passable and newloc!=upstair_location:
                downstair_location=newloc
        MapTiles.Downstair(self,downstair_location[0],downstair_location[1])

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
                    return
                attempted_location=[random.randint(0,self.dimensions[0]-1),random.randint(0,self.dimensions[1]-1)]
        elif retry=='near':
            while placed==False:
                if self.cells[attempted_location[0]][attempted_location[1]].passable==True:
                    creature.location=attempted_location
                    self.cells[attempted_location[0]][attempted_location[1]].contents.append(creature)
                    placed=True
                    return
                for i in self.cells[attempted_location[0]][attempted_location[1]].immediate_neighbors:
                    if i.passable:
                        self.place_creature(creature,i.location)
                        return
                attempted_location=random.choice(self.cells[attempted_location[0]][attempted_location[1]].immediate_neighbors).location
                attempts+=1
                if attempts>=20:
                    #print('could not place {}'.format(creature.name))
                    creature.location=[None,None]
                    return

    def place_item(self,item,location=None,retry='random'):
        attempts=0
        placed=False
        if location==None:
            location=[random.randint(0,self.dimensions[0]-1),random.randint(0,self.dimensions[1]-1)]
        if retry=='random':
            while placed==False:
                if self.cells[location[0]][location[1]].passable==True:
                    item.location=location
                    self.cells[location[0]][location[1]].contents.append(item)
                    placed=True
                    return
                location=[random.randint(0,self.dimensions[0]-1),random.randint(0,self.dimensions[1]-1)]
        elif retry=='near':
            while placed==False:
                if self.cells[location[0]][location[1]].passable==True:
                    item.location=location
                    self.cells[location[0]][location[1]].contents.append(item)
                    placed=True
                    return
                for i in self.cells[location[0]][location[1]].immediate_neighbors:
                    if i.passable:
                        self.place_item(item,i.location)
                location=random.choice(self.cells[location[0]][location[1]].immediate_neighbors).location
                attempts+=1
                if attempts>=20:
                    print('could not place {}'.format(item.name))
                    return

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

    def vision_check(self,a,b):
        if None in a.location or None in b.location:
            #print(a,'or',b,'has no location')
            return False
        acell=self.cells[a.location[0]][a.location[1]]
        if b==a or b.location==a.location:
            return True
        bcell=self.cells[b.location[0]][b.location[1]]
        if acell.distance_to(bcell)<a.vision_radius:
            line=get_line(a.location,b.location)
            line.pop(0)
            line.pop(len(line)-1)
        else:
            return False
        for i in line:
            if self.cells[i[0]][i[1]].transparent:
                continue
            else: return False
        return True

    def passability_check(self,a,b,range=None):
        if None in a.location or None in b.location:
            #print(a,'or',b,'has no location')
            return False
        acell=self.cells[a.location[0]][a.location[1]]
        if b==a or b.location==a.location:
            return True
        bcell=self.cells[b.location[0]][b.location[1]]
        if range==None:
            range=acell.distance_to(bcell)
        if acell.distance_to(bcell)<=range:
            line=get_line(a.location,b.location)
            line.pop(0)
            line.pop(len(line)-1)
        else:
            return False
        for i in line:
            if self.cells[i[0]][i[1]].passable:
                continue
            else: return False
        return True

    def animate_travel(self,item,start,finish,slowness=10,kbstored='play'):
        if Shell.shell.keyboard_mode!='standby':
            self.stored_keyboard_mode=kbstored
            Shell.shell.keyboard_mode='standby'
        self.animations[item]=Shell.Widget(pos=start.pos,size=start.size)
        self.animations[item].start=start
        start.add_widget(self.animations[item])
        self.animations[item].image=item.image
        if isinstance(item,Fluid):
            self.animations[item].image='./images/droplet.png'
        with self.animations[item].canvas:
            if isinstance(item,Fluid):
                Shell.Color(item.color[0],item.color[1],item.color[2],0.6)
            else:
                Shell.Color(item.color[0],item.color[1],item.color[2],item.color[3])
            Shell.Rectangle(pos=self.animations[item].pos,size=self.animations[item].size,source=self.animations[item].image)
        self.animations[item].k=0
        self.animations[item].x_distance=finish.pos[0]-start.pos[0]
        self.animations[item].y_distance=finish.pos[1]-start.pos[1]
        self.animations[item].f=functools.partial(self.travel,item,slowness)
        Clock.schedule_interval(self.animations[item].f,1/60)

    def travel(self,item,slowness=10,*args,**kwargs):
        try:
            self.animations[item].k+=1
            self.animations[item].canvas.clear()
            with self.animations[item].canvas:
                if isinstance(item,Fluid):
                    Shell.Color(item.color[0],item.color[1],item.color[2],0.6)
                else:
                    Shell.Color(item.color[0],item.color[1],item.color[2],item.color[3])
                Shell.Rectangle(pos=[self.animations[item].pos[0]+self.animations[item].k*self.animations[item].x_distance/slowness,
                                     self.animations[item].pos[1]+self.animations[item].k*self.animations[item].y_distance/slowness],
                                size=self.animations[item].size,source=self.animations[item].image)
            if self.animations[item].k>=slowness:
                self.animations[item].canvas.clear()
                Clock.unschedule(self.animations[item].f)
                self.animations[item].start.remove_widget(self.animations[item])
                del self.animations[item]
                if len(self.animations)==0:
                    Shell.shell.keyboard_mode=self.stored_keyboard_mode
        except KeyError:
            Shell.shell.keyboard_mode=self.stored_keyboard_mode
            pass

    def place_into_cell(self,item,cell_index,*args,**kwargs):
        item.in_inventory=None
        self.cells[cell_index[0]][cell_index[1]].contents.append(item)

    def get_circle(self,start,radius,require_los=False):
        cells_to_highlight=[]
        for i in range(int(start[0]-radius),int(start[0]+radius+1)):
            for j in range(int(start[1]-radius),int(start[1]+radius+1)):
                delta_x=start[0]-i
                delta_y=start[1]-j
                distance=(delta_x*delta_x+delta_y*delta_y)**0.5
                if distance<radius:
                    try:
                        cells_to_highlight.append(self.cells[i][j])
                    except:
                        pass
        if require_los==False:
            return cells_to_highlight
        elif require_los==True:
            cells=[]
            for i in cells_to_highlight:
                if self.passability_check(self.cells[start[0]][start[1]],i):
                    cells.append(i)
            return cells


            pass
            '''
            cells_to_highlight=set([self.cells[start[0]][start[1]]])
            outermost_points=[]
            for i in range(0,int(radius)):
                y=int((radius*radius-i*i)**0.5)
                for j in ([start[0]+i,start[1]+y],[start[0]+i,start[1]-y],[start[0]-i,start[1]+y],[start[0]-i,start[1]-y]):
                    outermost_points.append(j)
            for i in outermost_points:
                line=get_line(start,i)
                for j in line:
                    try:
                        if self.cells[j[0]][j[1]].passable:
                            cells_to_highlight.add(self.cells[j[0]][j[1]])
                        else:
                            cells_to_highlight.add(self.cells[j[0]][j[1]])
                            break
                    except KeyError:
                        break
            return cells_to_highlight
            '''



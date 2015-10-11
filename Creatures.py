__author__ = 'Alan'



from Items import *
from Attacks import *
from BaseClasses import *
from Materials import *
from Limbs import *
import Shell as S
import NameGen
import Fluids


import random
import kivy
from kivy.properties import ListProperty, DictProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.app import EventDispatcher


def flatten(l,ltypes=(list,tuple)):
    ltype=type(l)
    l=list(l)
    i=0
    while i<len(l):
        while isinstance(l[i],ltypes):
            if not l[i]:
                l.pop(i)
                i-=1
                break
            else:
                l[i:i+1]=l[i]
        i+=1
    return ltype(l)





def inventoryadd(item):
    print('{} added to inventory'.format(item))

def dropitem(item):
    print('You drop the {}'.format(item))


##############################################CREATURES###############################################################

#s,t,p,w, and l are the -base- stats, free of modifiers. 'str','tec','per','wil' and 'luc' are the modified stats

'''The following classification schemes exist:
humanoid, intelligent, mindless, unnatural, spirit, undead, law, chaos, neutral, angel, demon, beast, evil, good, magic,
antimagic, psychic, deity, living, animated, unstable, untrustworthy, as well as each individual type
'''

def humanoid_assembler(creature,stats,name,scale=1):
    #Torso first
    creature.torso=Upper_Torso(stats,'torso',owner=creature,scale=scale)

    creature.abdomen=Abdomen(stats,'abdomen',owner=creature,scale=scale)
    creature.torso.limbs.append(creature.abdomen)
    creature.abdomen.attachpoint=creature.torso

    #Left arm and associates
    creature.leftarm=Arm(stats,'left ',owner=creature,scale=scale)
    creature.torso.limbs.append(creature.leftarm)
    creature.leftarm.attachpoint=creature.torso

    creature.lefthand=Hand(stats,'left hand',owner=creature,scale=scale)
    creature.leftarm.limbs.append(creature.lefthand)
    creature.lefthand.attachpoint=creature.leftarm

    creature.leftthumb=Finger(stats,'thumb, left hand',owner=creature,scale=scale)
    creature.leftthumb.attachpoint=creature.lefthand
    creature.lefthand.limbs.append(creature.leftthumb)

    creature.leftindex=Finger(stats,'first finger, left hand',owner=creature,scale=scale)
    creature.leftindex.attachpoint=creature.lefthand
    creature.lefthand.limbs.append(creature.leftindex)

    creature.leftmiddle=Finger(stats,'second finger, left hand',owner=creature,scale=scale)
    creature.leftmiddle.attachpoint=creature.lefthand
    creature.lefthand.limbs.append(creature.leftmiddle)

    creature.leftring=Finger(stats,'third finger, left hand',owner=creature,scale=scale)
    creature.leftring.attachpoint=creature.lefthand
    creature.lefthand.limbs.append(creature.leftring)
    
    creature.leftlittle=Finger(stats,'fourth finger, left hand',owner=creature,scale=scale)
    creature.leftlittle.attachpoint=creature.lefthand
    creature.lefthand.limbs.append(creature.leftlittle)

    #Right arm, inc.
    creature.rightarm=Arm(stats,'right ',owner=creature,scale=scale)
    creature.torso.limbs.append(creature.rightarm)
    creature.rightarm.attachpoint=creature.torso

    creature.righthand=Hand(stats,'right hand',owner=creature,scale=scale)
    creature.rightarm.limbs.append(creature.righthand)
    creature.righthand.attachpoint=creature.rightarm

    creature.rightthumb=Finger(stats,'thumb, right hand',owner=creature,scale=scale)
    creature.rightthumb.attachpoint=creature.righthand
    creature.righthand.limbs.append(creature.rightthumb)

    creature.rightindex=Finger(stats,'first finger, right hand',owner=creature,scale=scale)
    creature.rightindex.attachpoint=creature.righthand
    creature.righthand.limbs.append(creature.rightindex)

    creature.rightmiddle=Finger(stats,'second finger, right hand',owner=creature,scale=scale)
    creature.rightmiddle.attachpoint=creature.righthand
    creature.righthand.limbs.append(creature.rightmiddle)

    creature.rightring=Finger(stats,'third finger, right hand',owner=creature,scale=scale)
    creature.rightring.attachpoint=creature.righthand
    creature.righthand.limbs.append(creature.rightring)
    
    creature.rightlittle=Finger(stats,'fourth finger, right hand',owner=creature,scale=scale)
    creature.rightlittle.attachpoint=creature.righthand
    creature.righthand.limbs.append(creature.rightlittle)

    #Left leg and friends
    creature.leftleg=Leg(stats,'left ',owner=creature,scale=scale)
    creature.abdomen.limbs.append(creature.leftleg)
    creature.leftleg.attachpoint=creature.abdomen

    creature.leftfoot=Foot(stats,'left foot',owner=creature,scale=scale)
    creature.leftleg.limbs.append(creature.leftfoot)
    creature.leftfoot.attachpoint=creature.leftleg

    creature.leftbigtoe=Toe(stats,'big toe, left foot',owner=creature,scale=scale)
    creature.leftfoot.limbs.append(creature.leftbigtoe)
    creature.leftbigtoe.attachpoint=creature.leftfoot

    creature.leftsecondtoe=Toe(stats,'second toe, left foot',owner=creature,scale=scale)
    creature.leftfoot.limbs.append(creature.leftsecondtoe)
    creature.leftsecondtoe.attachpoint=creature.leftfoot

    creature.leftthirdtoe=Toe(stats,'third toe, left foot',owner=creature,scale=scale)
    creature.leftfoot.limbs.append(creature.leftthirdtoe)
    creature.leftthirdtoe.attachpoint=creature.leftfoot

    creature.leftfourthtoe=Toe(stats,'fourth toe, left foot',owner=creature,scale=scale)
    creature.leftfoot.limbs.append(creature.leftfourthtoe)
    creature.leftfourthtoe.attachpoint=creature.leftfoot
    
    creature.leftlittletoe=Toe(stats,'little toe, left foot',owner=creature,scale=scale)
    creature.leftfoot.limbs.append(creature.leftlittletoe)
    creature.leftlittletoe.attachpoint=creature.leftfoot
    
    #The law offices of right leg
    creature.rightleg=Leg(stats,'right ',owner=creature,scale=scale)
    creature.abdomen.limbs.append(creature.rightleg)
    creature.rightleg.attachpoint=creature.abdomen

    creature.rightfoot=Foot(stats,'right foot',owner=creature,scale=scale)
    creature.rightleg.limbs.append(creature.rightfoot)
    creature.rightfoot.attachpoint=creature.rightleg

    creature.rightbigtoe=Toe(stats,'big toe, right foot',owner=creature,scale=scale)
    creature.rightfoot.limbs.append(creature.rightbigtoe)
    creature.rightbigtoe.attachpoint=creature.rightfoot

    creature.rightsecondtoe=Toe(stats,'second toe, right foot',owner=creature,scale=scale)
    creature.rightfoot.limbs.append(creature.rightsecondtoe)
    creature.rightsecondtoe.attachpoint=creature.rightfoot

    creature.rightthirdtoe=Toe(stats,'third toe, right foot',owner=creature,scale=scale)
    creature.rightfoot.limbs.append(creature.rightthirdtoe)
    creature.rightthirdtoe.attachpoint=creature.rightfoot

    creature.rightfourthtoe=Toe(stats,'fourth toe, right foot',owner=creature,scale=scale)
    creature.rightfoot.limbs.append(creature.rightfourthtoe)
    creature.rightfourthtoe.attachpoint=creature.rightfoot
    
    creature.rightlittletoe=Toe(stats,'little toe, right foot',owner=creature,scale=scale)
    creature.rightfoot.limbs.append(creature.rightlittletoe)
    creature.rightlittletoe.attachpoint=creature.rightfoot
    
    #And the head brigade
    creature.neck=Neck(stats,'neck',owner=creature,scale=scale)
    creature.torso.limbs.append(creature.neck)
    creature.neck.attachpoint=creature.torso
    
    creature.head=Head(stats,'head',owner=creature,scale=scale)
    creature.neck.limbs.append(creature.head)
    creature.head.attachpoint=creature.neck
    
    creature.nose=Nose(stats,'nose',owner=creature,scale=scale)
    creature.head.limbs.append(creature.nose)
    creature.nose.attachpoint=creature.head
    
    creature.righteye=Eye(stats,'right ',owner=creature,scale=scale)
    creature.head.limbs.append(creature.righteye)
    creature.righteye.attachpoint=creature.head
    
    creature.lefteye=Eye(stats,'left ',owner=creature,scale=scale)
    creature.head.limbs.append(creature.lefteye)
    creature.lefteye.attachpoint=creature.head
    
    creature.rightear=Ear(stats,'right ',owner=creature,scale=scale)
    creature.head.limbs.append(creature.rightear)
    creature.rightear.attachpoint=creature.head
    
    creature.leftear=Ear(stats,'left ',owner=creature,scale=scale)
    creature.head.limbs.append(creature.leftear)
    creature.leftear.attachpoint=creature.head

    creature.upperteeth=Teeth(stats,'upper teeth',owner=creature,scale=scale)
    creature.head.limbs.append(creature.upperteeth)
    creature.upperteeth.attachpoint=creature.head
    
    creature.jaw=Jaw(stats,'jaw',owner=creature,scale=scale)
    creature.head.limbs.append(creature.jaw)
    creature.jaw.attachpoint=creature.head

    creature.lowerteeth=Teeth(stats,'lower teeth',owner=creature,scale=scale)
    creature.jaw.limbs.append(creature.lowerteeth)
    creature.lowerteeth.attachpoint=creature.jaw



    pass


class Human(Creature):
    def __init__(self,color=(1,1,1,1),name='the human',job='',named=False,hostile=True,player=False,stats='random'):
        super().__init__()
        self.basicname='human'
        if stats=='random':
            self.stats= {'s': int(random.triangular(low=5, high=25, mode=15)),
                         't': int(random.triangular(low=5, high=25, mode=15)),
                         'p': int(random.triangular(low=5, high=25, mode=15)),
                         'w': int(random.triangular(low=5, high=25, mode=15)),
                         'l': int(random.triangular(low=5, high=25, mode=15))}
        else:
            self.stats=stats
        self.stats['str']=self.stats['s']
        self.stats['tec']=self.stats['t']
        self.stats['per']=self.stats['p']
        self.stats['wil']=self.stats['w']
        self.stats['luc']=self.stats['l']
        self.level=1
        self.exp=[0,100]
        self.focus=[int(20*(self.stats['p']**0.7+self.level**0.3)),int(20*(self.stats['p']**0.7+self.level**0.3))]
        self.stamina=[int(10*(2*self.stats['s']**2+self.level**2)**0.5),int(10*(2*self.stats['s']**2+self.level**2)**0.5)]
        self.maxstamina=int(10*(2*self.stats['s']**2+self.level**2)**0.5)
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'a ',1)
        self.targetable=True
        self.player=player
        self.limbs=[]
        self.vitals=[]
        self.attacks=[]
        self.disabled_attack_types=[Bite]
        #self.body=Torso(self.stats,'torso',owner=self)
        humanoid_assembler(self,self.stats,self.name)
        self.mass_calc()
        self.updateattacks()

        for i in self.limbs:
            for j in i.layers:
                if isinstance(j.material,Flesh_Material):
                    j.fluid=Fluids.Blood(self)

        self.classification.append('humanoid')
        self.classification.append('intelligent')
        self.classification.append('living')
        self.classification.append('human')
        if self.player==True:
            self.classification.append('player')
        if hostile==True:
            self.hostile.append('player')

class Giant(Creature):
    def __init__(self,color=(1,1,1,1),name='the giant',job='',named=False,hostile=True,player=False,stats='random'):
        super().__init__()
        self.basicname='giant'
        if stats=='random':
            self.stats= {'s': int(random.triangular(low=45, high=200, mode=125)),
                         't': int(random.triangular(low=3, high=18, mode=10)),
                         'p': int(random.triangular(low=3, high=17, mode=9)),
                         'w': int(random.triangular(low=5, high=25, mode=15)),
                         'l': int(random.triangular(low=5, high=25, mode=15))}
        else:
            self.stats=stats
        self.stats['str']=self.stats['s']
        self.stats['tec']=self.stats['t']
        self.stats['per']=self.stats['p']
        self.stats['wil']=self.stats['w']
        self.stats['luc']=self.stats['l']
        self.level=1
        self.exp=[0,100]
        self.focus=[int(20*(self.stats['p']**0.7+self.level**0.3)),int(20*(self.stats['p']**0.7+self.level**0.3))]
        self.stamina=[int(10*(2*self.stats['s']**2+self.level**2)**0.5),int(10*(2*self.stats['s']**2+self.level**2)**0.5)]
        self.maxstamina=int(10*(2*self.stats['s']**2+self.level**2)**0.5)
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'a ',1)
        self.targetable=True
        self.player=player
        self.limbs=[]
        self.vitals=[]
        self.attacks=[]
        #self.body=Torso(self.stats,'torso',owner=self)
        humanoid_assembler(self,self.stats,self.name,scale=3)
        self.mass_calc()
        self.updateattacks()

        for i in self.limbs:
            for j in i.layers:
                if isinstance(j.material,Flesh_Material):
                    j.fluid=Fluids.Blood(self)

        self.classification.append('humanoid')
        self.classification.append('intelligent')
        self.classification.append('living')
        self.classification.append('giant')
        if self.player==True:
            self.classification.append('player')
        if hostile==True:
            self.hostile.append('player')

class Goblin(Creature):
    def __init__(self,color=(1,1,1,1),name='the goblin',job='',named=False,hostile=True,player=False,stats='random'):
        super().__init__()
        self.basicname='goblin'
        if stats=='random':
            self.stats= {'s': int(random.triangular(low=7, high=20, mode=10)),
                         't': int(random.triangular(low=3, high=12, mode=9)),
                         'p': int(random.triangular(low=5, high=22, mode=14)),
                         'w': int(random.triangular(low=5, high=25, mode=15)),
                         'l': int(random.triangular(low=3, high=15, mode=10))}
        else:
            self.stats=stats
        self.stats['str']=self.stats['s']
        self.stats['tec']=self.stats['t']
        self.stats['per']=self.stats['p']
        self.stats['wil']=self.stats['w']
        self.stats['luc']=self.stats['l']
        self.level=1
        self.exp=[0,100]
        self.focus=[int(20*(self.stats['p']**0.7+self.level**0.3)),int(20*(self.stats['p']**0.7+self.level**0.3))]
        self.stamina=[int(10*(2*self.stats['s']**2+self.level**2)**0.5),int(10*(2*self.stats['s']**2+self.level**2)**0.5)]
        self.maxstamina=int(10*(2*self.stats['s']**2+self.level**2)**0.5)
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'a ',1)
        self.targetable=True
        self.player=player
        self.limbs=[]
        self.vitals=[]
        self.attacks=[]
        #self.body=Torso(self.stats,'torso',owner=self)
        humanoid_assembler(self,self.stats,self.name,scale=0.7)
        self.mass_calc()
        self.updateattacks()

        for i in self.limbs:
            for j in i.layers:
                if isinstance(j.material,Flesh_Material):
                    j.fluid=Fluids.Blood(self)

        self.classification.append('humanoid')
        self.classification.append('intelligent')
        self.classification.append('living')
        self.classification.append('gobline')
        self.classification.append('evil')
        self.classification.append('chaos')

        self.hostile.append('human')
        if self.player==True:
            self.classification.append('player')
        if hostile==True:
            self.hostile.append('player')

class Halfling(Creature):
    def __init__(self,color=(1,1,1,1),name='the halfling',job='',named=False,hostile=True,player=False,stats='random'):
        super().__init__()
        self.basicname='halfling'
        if stats=='random':
            self.stats= {'s': int(random.triangular(low=7, high=16, mode=11)),
                         't': int(random.triangular(low=10, high=35, mode=17)),
                         'p': int(random.triangular(low=9, high=32, mode=16)),
                         'w': int(random.triangular(low=5, high=20, mode=12)),
                         'l': int(random.triangular(low=10, high=40, mode=17))}
        else:
            self.stats=stats
        self.stats['str']=self.stats['s']
        self.stats['tec']=self.stats['t']
        self.stats['per']=self.stats['p']
        self.stats['wil']=self.stats['w']
        self.stats['luc']=self.stats['l']
        self.level=1
        self.exp=[0,100]
        self.focus=[int(20*(self.stats['p']**0.7+self.level**0.3)),int(20*(self.stats['p']**0.7+self.level**0.3))]
        self.stamina=[int(10*(2*self.stats['s']**2+self.level**2)**0.5),int(10*(2*self.stats['s']**2+self.level**2)**0.5)]
        self.maxstamina=int(10*(2*self.stats['s']**2+self.level**2)**0.5)
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'a ',1)
        self.targetable=True
        self.player=player
        self.limbs=[]
        self.vitals=[]
        self.attacks=[]
        self.disabled_attack_types=[Bite]
        #self.body=Torso(self.stats,'torso',owner=self)
        humanoid_assembler(self,self.stats,self.name,scale=0.6)
        self.mass_calc()
        self.updateattacks()

        for i in self.limbs:
            for j in i.layers:
                if isinstance(j.material,Flesh_Material):
                    j.fluid=Fluids.Blood(self)

        self.classification.append('humanoid')
        self.classification.append('intelligent')
        self.classification.append('living')
        self.classification.append('hobbit')
        if self.player==True:
            self.classification.append('player')
        if hostile==True:
            self.hostile.append('player')

class Fairy(Creature):
    def __init__(self,color=(1,1,1,1),name='the human',job='',named=False,hostile=True,player=False,stats='random'):
        super().__init__()
        self.basicname='fairy'
        if stats=='random':
            self.stats= {'s': int(random.triangular(low=1, high=4, mode=2)),
                         't': int(random.triangular(low=5, high=20, mode=12)),
                         'p': int(random.triangular(low=9, high=40, mode=20)),
                         'w': int(random.triangular(low=7, high=32, mode=18)),
                         'l': int(random.triangular(low=10, high=45, mode=21))}
        else:
            self.stats=stats
        self.stats['str']=self.stats['s']
        self.stats['tec']=self.stats['t']
        self.stats['per']=self.stats['p']
        self.stats['wil']=self.stats['w']
        self.stats['luc']=self.stats['l']
        self.level=1
        self.exp=[0,100]
        self.focus=[int(20*(self.stats['p']**0.7+self.level**0.3)),int(20*(self.stats['p']**0.7+self.level**0.3))]
        self.stamina=[int(10*(2*self.stats['s']**2+self.level**2)**0.5),int(10*(2*self.stats['s']**2+self.level**2)**0.5)]
        self.maxstamina=int(10*(2*self.stats['s']**2+self.level**2)**0.5)
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'a ',1)
        self.targetable=True
        self.player=player
        self.limbs=[]
        self.vitals=[]
        self.attacks=[]
        self.disabled_attack_types=[Bite]
        #self.body=Torso(self.stats,'torso',owner=self)
        humanoid_assembler(self,self.stats,self.name,scale=0.15)

        self.leftwing=Wing(self.stats,'left wing',owner=self,scale=0.1)
        self.torso.limbs.append(self.leftwing)
        self.leftwing.attachpoint=self.torso

        self.rightwing=Wing(self.stats,'right wing',owner=self,scale=0.1)
        self.torso.limbs.append(self.rightwing)
        self.rightwing.attachpoint=self.torso

        self.mass_calc()
        print(self.mass,self.movemass)
        self.updateattacks()

        for i in self.limbs:
            for j in i.layers:
                if isinstance(j.material,Flesh_Material):
                    j.fluid=Fluids.Blood(self)

        self.classification.append('humanoid')
        self.classification.append('intelligent')
        self.classification.append('living')
        self.classification.append('fairy')
        if self.player==True:
            self.classification.append('player')
        if hostile==True:
            self.hostile.append('player')


class Wolf(Creature):
    def __init__(self,color=(1,1,1,1),name='the wolf',job='',named=False,hostile=True,player=False,stats='random'):
        super().__init__()
        self.basicname='wolf'
        if stats=='random':
            self.stats= {'s': int(random.triangular(low=5, high=15, mode=10)),
                         't': int(random.triangular(low=5, high=8, mode=7)),
                         'p': int(random.triangular(low=15, high=25, mode=15)),
                         'w': int(random.triangular(low=10, high=15, mode=12)),
                         'l': int(random.triangular(low=5, high=25, mode=15))}
        else:
            self.stats=stats
        self.stats['str']=self.stats['s']
        self.stats['tec']=self.stats['t']
        self.stats['per']=self.stats['p']
        self.stats['wil']=self.stats['w']
        self.stats['luc']=self.stats['l']
        self.level=1
        self.exp=[0,100]
        self.focus=[int(20*(self.stats['p']**0.7+self.level**0.3)),int(20*(self.stats['p']**0.7+self.level**0.3))]
        self.stamina=[int(10*(2*self.stats['s']**2+self.level**2)**0.5),int(10*(2*self.stats['s']**2+self.level**2)**0.5)]
        self.maxstamina=int(10*(2*self.stats['s']**2+self.level**2)**0.5)
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'a ',1)
        self.targetable=True
        self.player=player
        self.limbs=[]
        self.vitals=[]
        self.attacks=[]
        self.disabled_attack_types=[Kick]

        #Creating the body of the wolf.

        self.body=Upper_Torso(self.stats,name='body',length=0.3,radius=0.07,owner=self)               #main body
        self.body.add_outer_layer(Hair,Fur,0.05,name='fur')

        #all the legs
        self.front_right_leg=Leg(self.stats,name='front right ',length=0.3,boneradius=0.008,owner=self)
        self.front_left_leg=Leg(self.stats,name='front left ',length=0.3,boneradius=0.008,owner=self)
        self.hind_right_leg=Leg(self.stats,name='right hind ',length=0.3,boneradius=0.008,owner=self)
        self.hind_left_leg=Leg(self.stats,name='left hind ',length=0.3,boneradius=0.008,owner=self)
        self.flank=Abdomen(self.stats,name='flank',length=0.2,radius=0.06,owner=self)
        self.flank.add_outer_layer(Hair,Fur,0.04,name='fur')
        self.hind_right_leg.add_outer_layer(Hair,Fur,0.03,name='fur')
        self.hind_left_leg.add_outer_layer(Hair,Fur,0.03,name='fur')
        self.hind_left_leg.join_to(self.flank)
        self.hind_right_leg.join_to(self.flank)
        self.flank.join_to(self.body)
        for i in (self.front_left_leg,self.front_right_leg):
            i.add_outer_layer(Hair,Fur,0.03,name='fur')
            i.attachpoint=self.body
            self.body.limbs.append(i)
        self.neck=Neck(self.stats,owner=self)                                       #neck
        self.neck.add_outer_layer(Hair,Fur,0.05,name='fur')
        self.neck.attachpoint=self.body
        self.body.limbs.append(self.neck)
        self.head=Head(self.stats,length=0.1,radius=0.04,owner=self)                #head
        self.head.add_outer_layer(Hair,Fur,0.03,name='fur')
        self.head.join_to(self.neck)
        self.muzzle=Snout(self.stats,name='muzzle',length=0.15,radius=0.04,owner=self)
        self.lefteye=Eye(self.stats,name='left ',owner=self)
        self.righteye=Eye(self.stats,name='right ',owner=self)
        self.leftear=Ear(self.stats,name='left ',radius=0.03,owner=self)
        self.leftear.add_outer_layer(Hair,Fur,0.005,name='fur')
        self.rightear=Ear(self.stats,name='right ',radius=0.03,owner=self)
        self.rightear.add_outer_layer(Hair,Fur,0.005,name='fur')
        self.jaw=Jaw(self.stats,length=0.3,radius=0.015,owner=self)
        self.jaw.add_outer_layer(Hair,Fur,0.01,name='fur')
        self.jaw.stats['s']*=2
        self.jaw.stats['str']*=2
        for i in (self.muzzle,self.lefteye,self.righteye,self.leftear,self.rightear,self.jaw):
            i.join_to(self.head)
        self.upper_teeth=Teeth(self.stats,name='upper teeth',length=0.18,radius=0.01,owner=self)
        self.upper_teeth.join_to(self.muzzle)
        self.lower_teeth=Teeth(self.stats,name='lower teeth',length=0.18,radius=0.01,owner=self,biting_surface=0.00005)
        self.lower_teeth.join_to(self.jaw)
        self.front_right_paw=Foot(self.stats,name='front right paw',length=0.05,radius=0.02,owner=self)
        self.front_left_paw=Foot(self.stats,name='front left paw',length=0.05,radius=0.02,owner=self)
        self.hind_right_paw=Foot(self.stats,name='hind right paw',length=0.05,radius=0.02,owner=self)
        self.hind_left_paw=Foot(self.stats,name='hind left paw',length=0.05,radius=0.02,owner=self)
        for i in (self.front_right_paw,self.front_left_paw,self.hind_right_paw,self.hind_left_paw):
            i.add_outer_layer(Hair,Fur,0.01,name='fur')
            for j in ('first','second','third','fourth'):
                newclaw=Claw(self.stats,name='{} claw, {}'.format(j,i.name),length=0.01,radius=0.001,owner=self)
                newclaw.join_to(i)
        self.front_right_paw.join_to(self.front_right_leg)
        self.front_left_paw.join_to(self.front_left_leg)
        self.hind_left_paw.join_to(self.hind_left_leg)
        self.hind_right_paw.join_to(self.hind_right_leg)
        self.tail=Balancing_Tail(self.stats,length=0.3,radius=0.02,owner=self)
        self.tail.add_outer_layer(Hair,Fur,0.06,name='fur')
        self.tail.join_to(self.flank)




        self.mass_calc()
        self.updateattacks()

        for i in self.limbs:
            for j in i.layers:
                if isinstance(j.material,Flesh_Material):
                    j.fluid=Fluids.Blood(self)


        self.classification.append('beast')
        self.classification.append('living')
        self.classification.append('wolf')
        if self.player==True:
            self.classification.append('player')
        if hostile==True:
            self.hostile.append('player')


class Blob(Creature):
    def __init__(self,color=(1,1,1,1),name='the blob',job='',named=False,hostile=True,player=False,stats='random',mass=500,material=Slime):
        super().__init__()
        self.basicname='blob'
        if stats=='random':
            self.stats= {'s': int(random.triangular(low=5, high=20, mode=10)),
                         't': int(random.triangular(low=1, high=10, mode=5)),
                         'p': int(random.triangular(low=1, high=5, mode=3)),
                         'w': int(random.triangular(low=1, high=1, mode=1)),
                         'l': int(random.triangular(low=5, high=25, mode=15))}
        else:
            self.stats=stats
        self.stats['str']=self.stats['s']
        self.stats['tec']=self.stats['t']
        self.stats['per']=self.stats['p']
        self.stats['wil']=self.stats['w']
        self.stats['luc']=self.stats['l']
        self.level=1
        self.exp=[0,100]
        self.focus=[int(20*(self.stats['p']**0.7+self.level**0.3)),int(20*(self.stats['p']**0.7+self.level**0.3))]
        self.stamina=[int(10*(2*self.stats['s']**2+self.level**2)**0.5),int(10*(2*self.stats['s']**2+self.level**2)**0.5)]
        self.maxstamina=int(10*(2*self.stats['s']**2+self.level**2)**0.5)
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'an ',1)
        self.targetable=True
        self.feels_pain=False
        self.player=player
        self.material=material
        self.limbs=[]
        self.body=Blob_Body(self.stats,owner=self,material=material)
        self.body.recalculate_from_mass(mass)
        self.vitals=[self.body.layers[0]]
        self.attacks=[]

        self.classification.append('magic')
        self.classification.append('mindless')
        self.classification.append('blob')
        if hostile==True:
            self.hostile.append('player')

        #Variables specific to shifting creatures
        self.rounding_loss=0
        self.basemass=mass
        self.mass=mass
        self.reform()


        self.movemass=self.mass
        self.updateattacks()

    def reform(self):
        equipped_copy=self.equipped_items.copy()
        available_mass=self.mass+self.rounding_loss
        for i in equipped_copy:
            self.unequip(i,log=False)
        pseudopodmass=available_mass*0.5*random.random()
        self.limbs=[self.body]
        self.vitals=[self.body.layers[0]]
        self.body.recalculate_from_mass(available_mass-pseudopodmass)
        current_mass=0
        self.targetsize=self.body.length

        while current_mass<pseudopodmass:
            newpod=Pseudopod(self.stats,owner=self,material=self.material)
            podmass=0.3*random.random()*pseudopodmass
            newpod.recalculate_from_mass(podmass)
            self.targetsize+=newpod.length
            newpod.attachpoint=self.body
            self.body.limbs.append(newpod)
            current_mass+=podmass
        self.limbs.pop()
        self.mass_calc()
        self.rounding_loss=available_mass-self.mass

        for i in self.inventory:
            self.equip(i,log=False)

        self.fluidize()

    def fluidize(self):
        for i in self.limbs:
            for j in i.layers:
                j.fluid=Fluids.Slime_Fluid(self)
                j.fluid.add(j)

    def on_turn(self):
        if self.alive:
            self.stamina[0]=self.stamina[1]
            for i in self.limbs:
                i.updateability
            super().on_turn()
            self.reform()

class Acid_Blob(Blob):
    def __init__(self,color=(1,1,1,1),name='the acid blob',job='',named=False,hostile=True,player=False,stats='random',mass=500,material=Slime):
        super().__init__(color=color,name=name,job=job,named=named,hostile=hostile,player=player,stats=stats,mass=mass,material=material)

    def fluidize(self):
        for i in self.limbs:
            for j in i.layers:
                j.fluid=Fluids.Acid(self,strength=5+random.uniform(0,3))
                j.fluid.add(j)

class Amorphous_Horror(Creature):
    def __init__(self,color=(1,1,1,1),name='the amorphous horror',job='',named=False,hostile=True,player=False,stats='random',mass=500,decay=True):
        super().__init__()
        self.basicname='amorphous horror'
        if stats=='random':
            self.stats= {'s': int(random.triangular(low=5, high=25, mode=15)),
                         't': int(random.triangular(low=5, high=25, mode=15)),
                         'p': int(random.triangular(low=5, high=25, mode=15)),
                         'w': int(random.triangular(low=5, high=25, mode=15)),
                         'l': int(random.triangular(low=5, high=25, mode=15))}
        else:
            self.stats=stats
        self.stats['str']=self.stats['s']
        self.stats['tec']=self.stats['t']
        self.stats['per']=self.stats['p']
        self.stats['wil']=self.stats['w']
        self.stats['luc']=self.stats['l']
        self.level=1
        self.exp=[0,100]
        self.focus=[int(20*(self.stats['p']**0.7+self.level**0.3)),int(20*(self.stats['p']**0.7+self.level**0.3))]
        self.stamina=[int(10*(2*self.stats['s']**2+self.level**2)**0.5),int(10*(2*self.stats['s']**2+self.level**2)**0.5)]
        self.maxstamina=int(10*(2*self.stats['s']**2+self.level**2)**0.5)
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'an ',1)
        self.targetable=True
        self.player=player
        self.limbs=[]
        self.vitals=[]
        self.attacks=[]

        self.classification.append('magic')
        self.classification.append('unnatural')
        self.classification.append('chaos')
        if decay==True:
            self.classification.append('unstable')
        if hostile==True:
            self.hostile.append('player')

        #Variables specific to Amorphous Horror. Rounding Loss should only be used if decay is set to False
        self.decay=decay
        self.rounding_loss=0
        self.basemass=mass
        self.mass=mass
        self.reform()


        self.movemass=self.mass
        self.updateattacks()

    def reform(self):
        equipped_copy=self.equipped_items.copy()
        if self.decay==True:
            available_mass=self.mass
        else:
            available_mass=self.mass+self.rounding_loss
        for i in equipped_copy:
            self.unequip(i,log=False)
        self.vitals=[]
        current_mass=0
        self.targetsize=0
        self.limbs=[]
        possible_limbs=[Arm,Leg,Finger,Head,Upper_Torso,Neck,Toe,Eye,Nose,Ear,Jaw,Teeth,Hand,Abdomen,Foot,Wing,Tentacle]
        while current_mass<=available_mass:
            limbstats= {'s': int(random.triangular(low=5, high=25, mode=15)),
                         't': int(random.triangular(low=5, high=25, mode=15)),
                         'p': int(random.triangular(low=5, high=25, mode=15)),
                         'w': int(random.triangular(low=5, high=25, mode=15)),
                         'l': int(random.triangular(low=5, high=25, mode=15))}
            limbstats['str']=limbstats['s']
            limbstats['tec']=limbstats['t']
            limbstats['per']=limbstats['p']
            limbstats['wil']=limbstats['w']
            limbstats['luc']=limbstats['l']
            newlimb=random.choice(possible_limbs)(limbstats,scale=random.uniform(0.5,2),owner=self)
            current_mass+=newlimb.mass
            self.targetsize+=newlimb.length
            if len(self.limbs)>1:
                attempts=0
                joint_location=random.choice(self.limbs)
                while joint_location==newlimb and attempts<10:
                    joint_location=random.choice(self.limbs)
                    attempts+=1
                newlimb.attachpoint=joint_location
                joint_location.limbs.append(newlimb)
        self.limbs.pop()
        self.mass_calc()
        self.rounding_loss=available_mass-self.mass
        '''while current_mass>=available_mass:
            if self.limbs==[]:
                return
            unformed_limb=random.choice(self.limbs)
            current_mass-=unformed_limb.mass
            self.limbs.remove(unformed_limb)
        self.rounding_loss=available_mass-current_mass
        self.mass=current_mass
        for i in self.limbs:
            attempts=0
            joint_location=random.choice(self.limbs)
            while joint_location==i and attempts<=10:
                joint_location=random.choice(self.limbs)
                attempts+=1
            i.attachpoint=joint_location
            joint_location.limbs.append(i)'''
        for i in self.inventory:
            self.equip(i,log=False)
        for i in self.limbs:
            for j in i.layers:
                if isinstance(j.material,Flesh_Material):
                    j.fluid=random.choice([Fluids.Blood,Fluids.Water,Fluids.Acid])(self,strength=random.gauss(5,1))

    def on_turn(self):
        if self.alive:
            super().on_turn()
            self.reform()

    def die(self):
        super().die()
        S.shell.dungeonmanager.current_screen.cells[self.location[0]][self.location[1]].contents.remove(self)


#Acidic horror is not yet implemented
class Acidic_Horror(Creature):
    def __init__(self,color=(1,1,1,1),name='the acidic horror',job='',named=False,hostile=True,player=False,stats='random'):
        super().__init__()
        self.basicname='acidic horror'
        if stats=='random':
            self.stats= {'s': int(random.triangular(low=5, high=25, mode=15)),
                         't': int(random.triangular(low=5, high=25, mode=15)),
                         'p': int(random.triangular(low=5, high=25, mode=15)),
                         'w': int(random.triangular(low=5, high=25, mode=15)),
                         'l': int(random.triangular(low=5, high=25, mode=15))}
        else:
            self.stats=stats
        self.stats['str']=self.stats['s']
        self.stats['tec']=self.stats['t']
        self.stats['per']=self.stats['p']
        self.stats['wil']=self.stats['w']
        self.stats['luc']=self.stats['l']
        self.level=1
        self.exp=[0,100]
        self.focus=[int(20*(self.stats['p']**0.7+self.level**0.3)),int(20*(self.stats['p']**0.7+self.level**0.3))]
        self.stamina=[int(10*(2*self.stats['s']**2+self.level**2)**0.5),int(10*(2*self.stats['s']**2+self.level**2)**0.5)]
        self.maxstamina=int(10*(2*self.stats['s']**2+self.level**2)**0.5)
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'a ',1)
        self.targetable=True
        self.player=player
        self.limbs=[]
        self.vitals=[]
        self.attacks=[]
        self.disabled_attack_types=[]
        self.mass_calc()
        self.updateattacks()

        for i in self.limbs:
            for j in i.layers:
                if isinstance(j.material,Flesh_Material):
                    j.fluid=Fluids.Acid(self)

        self.classification.append('humanoid')
        self.classification.append('intelligent')
        self.classification.append('living')
        self.classification.append('human')
        if self.player==True:
            self.classification.append('player')
        if hostile==True:
            self.hostile.append('player')

class Target_Dummy(Creature):
    def __init__(self,color=(1,1,1,1),name='the target dummy',job='',named=False,hostile=True,player=False,stats='random'):
        super().__init__()
        if stats=='random':
            self.stats= {'s': int(random.triangular(low=5, high=25, mode=15)),
                         't': int(random.triangular(low=5, high=25, mode=15)),
                         'p': int(random.triangular(low=5, high=25, mode=15)),
                         'w': int(random.triangular(low=5, high=25, mode=15)),
                         'l': int(random.triangular(low=5, high=25, mode=15))}
        else:
            self.stats=stats
        self.stats['str']=self.stats['s']
        self.stats['tec']=self.stats['t']
        self.stats['per']=self.stats['p']
        self.stats['wil']=self.stats['w']
        self.stats['luc']=self.stats['l']
        self.level=1
        self.exp=[0,100]
        self.focus=[int(20*(self.stats['p']**0.7+self.level**0.3)),int(20*(self.stats['p']**0.7+self.level**0.3))]
        self.stamina=[int(10*(2*self.stats['s']**2+self.level**2)**0.5),int(10*(2*self.stats['s']**2+self.level**2)**0.5)]
        self.maxstamina=int(10*(2*self.stats['s']**2+self.level**2)**0.5)
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'an ',1)
        self.targetable=True
        self.player=player
        self.limbs=[]
        self.vitals=[]
        self.attacks=[]

        self.classification.append('magic')
        self.classification.append('unnatural')
        self.classification.append('chaos')
        if hostile==True:
            self.hostile.append('player')

        self.hitdict={}
        self.averagehits={}
        self.reform()
        self.mass_calc()


        self.movemass=self.mass
        self.updateattacks()


    def reform(self):
        self.pain=0
        equipped_copy=self.equipped_items.copy()
        for i in equipped_copy:
            self.unequip(i,log=False)
        self.vitals=[]
        self.targetsize=0
        self.limbs=[]
        humanoid_assembler(self,self.stats,self.name)
#        for i in self.inventory:
#            self.equip(i,log=False)
        self.mass_calc()

    def on_turn(self):
        self.reform()
        self.sense_awareness()

    def die(self):
        self.reform
        pass

    def evasion(self,attack,blockable=True,dodgeable=True,parryable=True):
        pass

    def on_struck(self,attack):
        self.hitdict.setdefault(str(type(attack)),[])
        self.averagehits.setdefault(str(type(attack)),[])
        self.hitdict[str(type(attack))].append((attack.time,attack.force,attack.pressure,attack.energy))


    def report(self):
        for keys in self.hitdict:
            count=0
            totalspeed=0
            totalforce=0
            totalpressure=0
            totalenergy=0
            for i in self.hitdict[keys]:
                totalspeed+=i[0]
                totalforce+=i[1]
                totalpressure+=i[2]
                totalenergy+=i[3]
                count+=1
            self.averagehits[keys]=(totalspeed/count,totalforce/count,totalpressure/count,totalenergy/count,count)
        for keys in self.averagehits:
            print(keys[16:-2],self.averagehits[keys][4],'iterations')
            print('average execution time:',self.averagehits[keys][0])
            print('average force delivered:',self.averagehits[keys][1])
            print('average pressure:',self.averagehits[keys][2])
            print('average energy:',self.averagehits[keys][3])


##################################################






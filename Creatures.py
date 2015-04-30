__author__ = 'Alan'



from Items import *
from Attacks import *
from BaseClasses import *
from Materials import *
from Limbs import *


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


def human_assembler(creature,stats,name):
    #Torso first
    creature.torso=Torso(stats,'torso',owner=creature)

    #Left arm and associates
    creature.leftarm=Arm(stats,'left',owner=creature)
    creature.torso.limbs.append(creature.leftarm)
    creature.leftarm.attachpoint=creature.torso

    creature.lefthand=Hand(stats,'left hand',owner=creature)
    creature.leftarm.limbs.append(creature.lefthand)
    creature.lefthand.attachpoint=creature.leftarm

    creature.leftthumb=Finger(stats,'thumb, left hand',owner=creature)
    creature.leftthumb.attachpoint=creature.lefthand
    creature.lefthand.limbs.append(creature.leftthumb)

    creature.leftindex=Finger(stats,'first finger, left hand',owner=creature)
    creature.leftindex.attachpoint=creature.lefthand
    creature.lefthand.limbs.append(creature.leftindex)

    creature.leftmiddle=Finger(stats,'second finger, left hand',owner=creature)
    creature.leftmiddle.attachpoint=creature.lefthand
    creature.lefthand.limbs.append(creature.leftmiddle)

    creature.leftring=Finger(stats,'third finger, left hand',owner=creature)
    creature.leftring.attachpoint=creature.lefthand
    creature.lefthand.limbs.append(creature.leftring)
    
    creature.leftlittle=Finger(stats,'fourth finger, left hand',owner=creature)
    creature.leftlittle.attachpoint=creature.lefthand
    creature.lefthand.limbs.append(creature.leftlittle)

    #Right arm, inc.
    creature.rightarm=Arm(stats,'right',owner=creature)
    creature.torso.limbs.append(creature.rightarm)
    creature.rightarm.attachpoint=creature.torso

    creature.righthand=Hand(stats,'right hand',owner=creature)
    creature.rightarm.limbs.append(creature.righthand)
    creature.righthand.attachpoint=creature.rightarm

    creature.rightthumb=Finger(stats,'thumb, right hand',owner=creature)
    creature.rightthumb.attachpoint=creature.righthand
    creature.righthand.limbs.append(creature.rightthumb)

    creature.rightindex=Finger(stats,'first finger, right hand',owner=creature)
    creature.rightindex.attachpoint=creature.righthand
    creature.righthand.limbs.append(creature.rightindex)

    creature.rightmiddle=Finger(stats,'second finger, right hand',owner=creature)
    creature.rightmiddle.attachpoint=creature.righthand
    creature.righthand.limbs.append(creature.rightmiddle)

    creature.rightring=Finger(stats,'third finger, right hand',owner=creature)
    creature.rightring.attachpoint=creature.righthand
    creature.righthand.limbs.append(creature.rightring)
    
    creature.rightlittle=Finger(stats,'fourth finger, right hand',owner=creature)
    creature.rightlittle.attachpoint=creature.righthand
    creature.righthand.limbs.append(creature.rightlittle)

    #Left leg and friends
    creature.leftleg=Leg(stats,'left',owner=creature)
    creature.torso.limbs.append(creature.leftleg)
    creature.leftleg.attachpoint=creature.torso

    creature.leftfoot=Foot(stats,'left foot',owner=creature)
    creature.leftleg.limbs.append(creature.leftfoot)
    creature.leftfoot.attachpoint=creature.leftleg

    creature.leftbigtoe=Toe(stats,'big toe, left foot',owner=creature)
    creature.leftfoot.limbs.append(creature.leftbigtoe)
    creature.leftbigtoe.attachpoint=creature.leftfoot

    creature.leftsecondtoe=Toe(stats,'second toe, left foot',owner=creature)
    creature.leftfoot.limbs.append(creature.leftsecondtoe)
    creature.leftsecondtoe.attachpoint=creature.leftfoot

    creature.leftthirdtoe=Toe(stats,'third toe, left foot',owner=creature)
    creature.leftfoot.limbs.append(creature.leftthirdtoe)
    creature.leftthirdtoe.attachpoint=creature.leftfoot

    creature.leftfourthtoe=Toe(stats,'fourth toe, left foot',owner=creature)
    creature.leftfoot.limbs.append(creature.leftfourthtoe)
    creature.leftfourthtoe.attachpoint=creature.leftfoot
    
    creature.leftlittletoe=Toe(stats,'little toe, left foot',owner=creature)
    creature.leftfoot.limbs.append(creature.leftlittletoe)
    creature.leftlittletoe.attachpoint=creature.leftfoot
    
    #The law offices of right leg
    creature.rightleg=Leg(stats,'right',owner=creature)
    creature.torso.limbs.append(creature.rightleg)
    creature.rightleg.attachpoint=creature.torso

    creature.rightfoot=Foot(stats,'right foot',owner=creature)
    creature.rightleg.limbs.append(creature.rightfoot)
    creature.rightfoot.attachpoint=creature.rightleg

    creature.rightbigtoe=Toe(stats,'big toe, right foot',owner=creature)
    creature.rightfoot.limbs.append(creature.rightbigtoe)
    creature.rightbigtoe.attachpoint=creature.rightfoot

    creature.rightsecondtoe=Toe(stats,'second toe, right foot',owner=creature)
    creature.rightfoot.limbs.append(creature.rightsecondtoe)
    creature.rightsecondtoe.attachpoint=creature.rightfoot

    creature.rightthirdtoe=Toe(stats,'third toe, right foot',owner=creature)
    creature.rightfoot.limbs.append(creature.rightthirdtoe)
    creature.rightthirdtoe.attachpoint=creature.rightfoot

    creature.rightfourthtoe=Toe(stats,'fourth toe, right foot',owner=creature)
    creature.rightfoot.limbs.append(creature.rightfourthtoe)
    creature.rightfourthtoe.attachpoint=creature.rightfoot
    
    creature.rightlittletoe=Toe(stats,'little toe, right foot',owner=creature)
    creature.rightfoot.limbs.append(creature.rightlittletoe)
    creature.rightlittletoe.attachpoint=creature.rightfoot
    
    #And the head brigade
    creature.neck=Neck(stats,'neck',owner=creature)
    creature.torso.limbs.append(creature.neck)
    creature.neck.attachpoint=creature.torso
    
    creature.head=Head(stats,'head',owner=creature)
    creature.neck.limbs.append(creature.head)
    creature.head.attachpoint=creature.neck
    
    creature.nose=Nose(stats,'nose',owner=creature)
    creature.head.limbs.append(creature.nose)
    creature.nose.attachpoint=creature.head
    
    creature.righteye=Eye(stats,'right eye',owner=creature)
    creature.head.limbs.append(creature.righteye)
    creature.righteye.attachpoint=creature.head
    
    creature.lefteye=Eye(stats,'left eye',owner=creature)
    creature.head.limbs.append(creature.lefteye)
    creature.lefteye.attachpoint=creature.head
    
    creature.rightear=Ear(stats,'right ear',owner=creature)
    creature.head.limbs.append(creature.rightear)
    creature.rightear.attachpoint=creature.head
    
    creature.leftear=Ear(stats,'left ear',owner=creature)
    creature.head.limbs.append(creature.leftear)
    creature.leftear.attachpoint=creature.head

    creature.upperteeth=Teeth(stats,'upper teeth',owner=creature)
    creature.head.limbs.append(creature.upperteeth)
    creature.upperteeth.attachpoint=creature.head
    
    creature.jaw=Jaw(stats,'jaw',owner=creature)
    creature.head.limbs.append(creature.jaw)
    creature.jaw.attachpoint=creature.head

    creature.lowerteeth=Teeth(stats,'lower teeth',owner=creature)
    creature.jaw.limbs.append(creature.lowerteeth)
    creature.lowerteeth.attachpoint=creature.jaw



    pass

class Human(Creature):
    def __init__(self,color=(1,1,1,1),name='the human',job='',named=False,hostile=True,player=False,stats='random'):
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
        self.indefinitename=name.replace('the ', 'a ',1)
        self.targetable=True
        self.hostile=hostile
        self.player=player
        self.limbs=[]
        self.vitals=[]
        self.attacks=[]
        #self.body=Torso(self.stats,'torso',owner=self)
        human_assembler(self,stats,self.name)
        self.mass=self.torso.movemass
        self.movemass=self.mass
        self.updateattacks()

##################################################






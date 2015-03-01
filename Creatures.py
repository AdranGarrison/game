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

class Human(Creature):
    def __init__(self,color=(1,1,1,1),name='the human',job='',named=False,hostile=True,player=False,stats='random'):
        if stats=='random':
            self.stats={}
            self.stats['str']=int(random.triangular(low=5,high=25,mode=15))
            self.stats['tec']=int(random.triangular(low=5,high=25,mode=15))
            self.stats['per']=int(random.triangular(low=5,high=25,mode=15))
            self.stats['wil']=int(random.triangular(low=5,high=25,mode=15))
            self.stats['luc']=int(random.triangular(low=5,high=25,mode=15))
        else:
            self.stats=stats
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+job
        self.indefinitename=name.replace('the ', 'a ',1)
        self.targetable=True
        self.hostile=hostile
        self.player=player
        self.body=Torso(self.stats,'torso',owner=self)
        self.mass=self.body.movemass
        self.movemass=self.mass

        pass
##################################################





stats={'str':20,'tec':15,'per':15,'wil':15,'luc':15}
bob=Human(stats=stats)
#        testlimb=Head(stats,'test',owner=bob)
#        testmass=testlimb.mass
#       for i in testlimb.limbs:
#            testmass+=i.mass
print(bob.mass,bob.stats,bob.body.limbs[4].youngs)
        #testhand=Hand(stats,'bob',owner=Bob)
        #testhand.wounds.append('crushed')
        #testhand.wounds[0]=2
        #print(testhand.diagnosis)

#print(bob.body.limbs[0].limbs[0].youngs)
#bob.body.limbs[0].limbs[0].armor=LongSword(thickness=0.0000001)
#bob.body.limbs[0].limbs[0].youngscalc()
#print(bob.body.limbs[0].limbs[0].youngs)

punch=Punch(bob.body.limbs[0].limbs[0])

punch.do(bob.body)

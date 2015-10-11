__author__ = 'Alan'

import BaseClasses
import random


class Blood(BaseClasses.Fluid):
    def __init__(self,owner,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(1,0,0,0.3)
        self.adjective='bloody'
        self.basicname='blood'
        self.name=''.join((self.owner.basicname,' blood'))

    def process(self,log=True):
        if self.on is not None:
            if self.on.wetdamage=='rust':
                if random.random()<1/self.defenderstats['luc']:
                    self.on.damage['rust']+=(1/self.defenderstats['luc']**2)*random.random()

        if random.random()<0.05:
            self.remove()
        pass

class Water(BaseClasses.Fluid):
    def __init__(self,owner,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(0,0,1,0.3)
        self.adjective='wet'
        self.basicname='water'
        self.name='water'

    def process(self,log=True):
        if self.on is not None:
            if self.on.wetdamage=='rust':
                if random.random()<1/self.defenderstats['luc']:
                    self.on.damage['rust']+=(1/self.defenderstats['luc']**2)*random.random()

        if random.random()<0.05:
            self.remove()
        pass

class Acid(BaseClasses.Fluid):
    def __init__(self,owner,strength=6,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(0.95,0.75,0.34,0.3)
        self.adjective='acidic'
        self.basicname='acid'
        if self.owner!=None:
            self.name=''.join((self.owner.basicname,' acid'))
        else:
            self.name='acid'
        self.strength=strength

    def process(self,log=True):
        if self.on is not None:
            if random.random()<(self.strength/(self.strength+self.defenderstats['luc'])):
                self.on.acid_burn(self.strength,log=log)
        if random.random()<0.05:
            self.remove()
        pass

class Slime_Fluid(BaseClasses.Fluid):
    def __init__(self,owner,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(0.30,0.59,0.30,0.3)
        self.adjective='slimy'
        self.basicname='slime'
        self.name='slime'

    def process(self,log=True):
        if random.random()<0.05:
            self.remove()
        pass
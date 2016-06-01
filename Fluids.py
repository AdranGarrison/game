__author__ = 'Alan'

import BaseClasses
import random
import Enchantments




class Blood(BaseClasses.Fluid):
    def __init__(self,owner,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(1,0,0,0.3)
        self.adjective='bloody'
        self.basicname='blood'
        if self.owner!=None:
            try: self.name=''.join((self.owner.basicname,' blood'))
            except: self.name='blood'
        else:
            self.name='blood'

    def process(self,log=True,limb=None,**kwargs):
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

    def process(self,log=True,limb=None,**kwargs):
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
            try: self.name=''.join((self.owner.basicname,' acid'))
            except: self.name='acid'
        else:
            self.name='acid'
        self.strength=strength

    def process(self,log=True,limb=None,**kwargs):
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

    def process(self,log=True,limb=None,**kwargs):
        if random.random()<0.05:
            self.remove()
        pass

class Magma(BaseClasses.Fluid):
    def __init__(self,owner,temp=1000,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(1,0.2,0.2,0.3)
        self.adjective='igneous'
        self.basicname='magma'
        if self.owner!=None:
            try: self.name=''.join((self.owner.basicname,' magma'))
            except: self.name='magma'
        else:
            self.name='magma'
        self.temp=temp

    def process(self,log=True,limb=None,**kwargs):
        if self.on is not None:
            if random.random()<(self.temp/(self.temp+self.defenderstats['luc']**2)):
                if limb==None: self.on.burn(self.temp,5*random.random(),log=log)
                else: limb.burn(self.temp,5*random.random(),log=log)
        if random.random()<0.05:
            self.remove()
        pass

class Numbing_Poison(BaseClasses.Fluid):
    def __init__(self,owner,strength=6,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(0.2,0.4,0.2,0.3)
        self.strength=strength
        self.adjective='poisonous'
        self.basicname='numbing poison'
        self.name='numbing poison'
        if 'applied' in kwargs:
            self.applied=True
        else: self.applied=False


    def process(self,log=True,limb=None,**kwargs):
        if self.on is not None:
            if hasattr(self.on,'in_limb') and self.on.in_limb!=None:
                damage=self.on.damage['cut']+self.on.damage['pierce']+self.on.damage['crush']
                if (self.strength-self.on.poison_resistance)*random.random()*damage>=1 and self.on.poisonable==True:
                    target=self.on.in_limb
                    attempts=0
                    while any(isinstance(i,Enchantments.Numb) for i in target.enchantments) and attempts<self.strength:
                        potential_targets=[]
                        if target.attachpoint!=None:
                            potential_targets.append(target.attachpoint)
                        potential_targets.extend(target.limbs)
                        if potential_targets==[]:
                            break
                        else:
                            target=random.choice(potential_targets)
                            attempts+=1
                    Enchantments.Numb(target,turns=random.randint(1,2*self.strength-attempts),strength=max(self.strength-attempts,1))
                    self.strength-=1
            elif self.applied==False:
                self.strength-=1
        else:
            self.strength-=1
        if self.strength<=0:
            self.remove()


    def on_strike(self,attack,**kwargs):
        added=False
        for i in attack.touchedobjects:
            if random.random()<0.9:
                self.add(i)
                added=True
                #print("added numbing poison to",i.name)
        if added==True and random.random()>0.5:
            self.strength-=1
        if self.strength<=0: self.remove()
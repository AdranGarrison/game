__author__ = 'Alan'

import BaseClasses
import random
import Enchantments
import Shell




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
            res=self.on.resistance['acid']
            if random.random()*res<(self.strength/(self.strength+self.defenderstats['luc'])):
                self.on.acid_burn(self.strength/res,log=log)
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
        elif random.random()<0.01 and self.on is not None:
            res=random.choice(['teleport','fire','ice','physical','acid','lightning','poison','pain','psychic','divine',
                               'magic','dark','disable','rot','death','arcane','elemental','transmutation'])
            if hasattr(self.on,'in_limb') and self.on.in_limb!=None:
                luc=self.on.in_limb.stats['luc']
                self.on.in_limb.resistance[res]*=0.9+random.triangular(0,0.2,0.2*luc/(13+luc))
            else:
                self.on.resistance[res]*=0.9+random.random()*0.2



class Magma(BaseClasses.Fluid):
    def __init__(self,owner,temp=1000,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(1,0.2,0.2,0.3)
        self.classification=['fluid','magma']
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
                if limb==None: self.on.burn(self.temp,5*random.random(),log=log,source=self)
                else: limb.burn(self.temp,5*random.random(),log=log,source=self)
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
            res=self.on.resistance['poison']
            if hasattr(self.on,'in_limb') and self.on.in_limb!=None:
                res*=self.on.in_limb.resistance['poison']
                damage=self.on.damage['cut']+self.on.damage['pierce']+self.on.damage['crush']
                if (self.strength-self.on.poison_resistance)*random.random()*damage>=res and self.on.poisonable==True:
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
                    effect=Enchantments.Numb(target,turns=int(random.randint(1,2*self.strength-attempts)/res),strength=int(max(self.strength-attempts,1)/res))
                    effect.category="poison"
                    effect.classification=["poison","negative","physical"]
                    self.strength-=1
                elif random.random()>0.8:
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
            if self.owner!=None and 5>random.random()*self.owner.stats['luc']:
                self.strength-=1
        if self.strength<=0: self.remove()

class Agonizing_Poison(BaseClasses.Fluid):
    def __init__(self,owner,strength=6,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(0.2,0.4,0.2,0.3)
        self.strength=strength
        self.adjective='poisonous'
        self.basicname='agonizing poison'
        self.name='agonizing poison'
        if 'applied' in kwargs:
            self.applied=True
        else: self.applied=False


    def process(self,log=True,limb=None,**kwargs):
        if self.on is not None:
            if hasattr(self.on,'in_limb') and self.on.in_limb!=None and self.on.poisonable==True:
                damage=self.on.damage['cut']+self.on.damage['pierce']+self.on.damage['crush']
                if self.on.in_limb.owner!=None and damage>0:
                    res=self.on.resistance['poison']*self.on.resistance['pain']
                    pain=(15*random.random()*self.strength*self.strength*self.on.painfactor*self.on.in_limb.painfactor)/(
                        self.on.poison_resistance+self.on.in_limb.owner.stats['wil']**0.5)/res
                    if self.on.in_limb in self.on.in_limb.owner.limbs:
                        self.on.in_limb.owner.pain+=pain
                    self.strength-=1
                    if self.on.in_limb.owner==Shell.shell.player:
                        Shell.messages.append("[color=C21D25]Pain shoots through your {}![/color]".format(self.on.in_limb.name))
                    elif self.on.in_limb.owner in Shell.shell.player.visible_creatures:
                        if "{} convulses in pain!".format(self.on.in_limb.owner.name) not in Shell.messages:
                            Shell.messages.append("[color=1F4CAD]{} convulses in pain![/color]".format(self.on.in_limb.owner.name))
                elif random.random()>0.8:
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
            if self.owner!=None and 5>random.random()*self.owner.stats['luc']:
                self.strength-=1
        if self.strength<=0: self.remove()

class Necrotic_Poison(BaseClasses.Fluid):
    def __init__(self,owner,strength=6,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(0.2,0.4,0.2,0.3)
        self.strength=strength
        self.adjective='poisonous'
        self.basicname='necrotic poison'
        self.name='necrotic poison'
        if 'applied' in kwargs:
            self.applied=True
        else: self.applied=False


    def process(self,log=True,limb=None,**kwargs):
        if self.on is not None:
            res=self.on.resistance['poison']*self.on.resistance['rot']
            if hasattr(self.on,'in_limb') and self.on.in_limb!=None:
                res*=self.on.in_limb.resistance['poison']*self.on.in_limb.resistance['rot']
                damage=self.on.damage['cut']+self.on.damage['pierce']+self.on.damage['crush']
                if (self.strength-self.on.rot_resistance)*random.random()*damage>=res and self.on.rottable==True:
                    target=self.on
                    effect=Enchantments.Rot(target,strength=self.strength)
                    effect.category="poison"
                    effect.classification=["poison","negative","physical"]
                    self.strength-=1
                elif random.random()>0.8:
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
        if added==True and random.random()>0.5:
            if self.owner!=None and 5>random.random()*self.owner.stats['luc']:
                self.strength-=1
        if self.strength<=0: self.remove()

class Debilitating_Poison(BaseClasses.Fluid):
    def __init__(self,owner,strength=6,**kwargs):
        super().__init__(owner,**kwargs)
        self.color=(0.2,0.4,0.2,0.3)
        self.strength=strength
        self.adjective='poisonous'
        self.basicname='debilitating poison'
        self.name='debilitating poison'
        if 'applied' in kwargs:
            self.applied=True
        else: self.applied=False


    def process(self,log=True,limb=None,**kwargs):
        if self.on is not None:
            res=self.on.resistance['poison']
            if hasattr(self.on,'in_limb') and self.on.in_limb!=None:
                res*=self.on.in_limb.resistance['poison']
                damage=self.on.damage['cut']+self.on.damage['pierce']+self.on.damage['crush']
                if (self.strength-self.on.poison_resistance)*random.random()*damage>=res and self.on.poisonable==True:
                    target=self.on.in_limb
                    turns=int(self.strength*self.strength*2*random.triangular(0,1,1/self.on.in_limb.owner.stats['luc'])/res)
                    effect=Enchantments.Limb_Stat_Modification(target,turns=turns,strength=int(self.strength/res),stat=random.choice(['s','t']))
                    effect.category="poison"
                    effect.classification=["poison","negative","physical"]
                    self.strength-=1
                elif random.random()>0.8:
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
            if self.owner!=None and 5>random.random()*self.owner.stats['luc']:
                self.strength-=1
        if self.strength<=0: self.remove()
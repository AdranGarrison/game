__author__ = 'Alan'

import BaseClasses
import Fluids
import random


class Acidic(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,**kwargs)
        self.strength=strength
        self.target.acid_resistance=2*strength
        self.target.material.acid_resistance=2*strength
        self.acid=Fluids.Acid(None,strength=self.strength)

    def on_turn(self):
        super().on_turn()
        for i in self.target.equipped:
            if random.random()<(1/i.stats['luc'])**1.5:
                self.acid.add(i)
                self.attempt_identification(15)
        if random.random()>0.7: self.acid.add(self.target)

    def on_strike(self,attack):
        super().on_strike(attack)
        luc=attack.attacker.stats['luc']
        for i in attack.touchedobjects:
            if random.random()<luc/(10+luc):
                self.acid.add(i)
                self.attempt_identification(10)

    def on_struck(self,attack):
        super().on_struck(attack)
        if random.random()>0.9:
            if self.target.location==[None,None]:
                self.acid=Fluids.Acid(self.target.in_inventory,strength=self.strength)
                self.acid.splatter(intensity=1,volume=1)
                self.attempt_identification(10)
            else:
                self.acid=Fluids.Acid(self.target,strength=self.strength)
                self.acid.splatter(intensity=1,volume=1)

    def on_destruction(self):
        if self.target.location==[None,None]:
            self.acid=Fluids.Acid(self.target.in_inventory,strength=self.strength)
            self.acid.splatter(intensity=3,volume=self.strength*2)
        else:
            self.acid=Fluids.Acid(self.target,strength=self.strength)
            self.acid.splatter(intensity=3,volume=self.strength*2)

class Burning(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,**kwargs)
        self.strength=strength
        self.target.burn_resistance=2*strength*self.target.burn_resistance
        self.target.material.burn_resistance=2*strength*self.target.material.burn_resistance

    def on_turn(self):
        super().on_turn()
        for i in self.target.equipped:
            if random.random()<(1/i.stats['luc'])**1.5:
                if random.random()<(1/i.stats['luc'])**1.5:
                    i.burn(random.gauss(self.strength*100,100),random.gauss(2,0.5),with_armor=False)
                    self.attempt_identification(20)
                else:
                    i.burn(random.gauss(self.strength*100,100),random.gauss(2,0.5))
                    if i.armor is None:
                        self.attempt_identification(20)
                    else:
                        self.attempt_identification(10)



    def on_strike(self,attack):
        super().on_strike(attack)
        luc=attack.attacker.stats['luc']
        for i in attack.touchedobjects:
            if random.random()<luc/(10+luc):
                i.burn(random.gauss(self.strength*100,100),random.gauss(len(attack.touchedobjects)**0.5,0.1))
                self.attempt_identification(15)

    def on_struck(self,attack):
        super().on_struck(attack)
        if random.random()>0.3:
            try: attack.weapon.burn(random.gauss(self.strength*100,100),random.gauss(2,0.5))
            except AttributeError: attack.limb.burn(random.gauss(self.strength*100,100),random.gauss(2,0.5))
            self.attempt_identification(10)

    def on_destruction(self):
        if self.target.location==[None,None]:
            self.magma=Fluids.Magma(self.target.in_inventory,temp=random.gauss(self.strength*200,100))
            self.magma.splatter(intensity=3,volume=self.strength*2)
        else:
            self.magma=Fluids.Acid(self.target,temp=random.gauss(self.strength*200,100))
            self.magma.splatter(intensity=3,volume=self.strength*2)



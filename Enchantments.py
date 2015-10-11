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
        if random.random()>0.7: self.acid.add(self.target)

    def on_strike(self,attack):
        super().on_strike(attack)
        luc=attack.attacker.stats['luc']
        for i in attack.touchedobjects:
            if random.random()<luc/(10+luc):
                self.acid.add(i)

    def on_struck(self,attack):
        super().on_struck(attack)
        if random.random()>0.9:
            if self.target.location==[None,None]:
                self.acid=Fluids.Acid(self.target.in_inventory,strength=self.strength)
                self.acid.splatter(intensity=1,volume=1)
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

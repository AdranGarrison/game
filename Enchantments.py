__author__ = 'Alan'

import BaseClasses
import Fluids
import random
import Shell



class Acidic(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,**kwargs)
        self.strength=strength
        self.old_acid_resistance=self.target.acid_resistance
        self.old_mat_acid_resistance=self.target.material.acid_resistance
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

    def on_dispel(self):
        self.target.acid_resistance=self.old_acid_resistance
        self.target.material.acid_resistance=self.old_mat_acid_resistance

class Burning(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,**kwargs)
        self.strength=strength
        self.old_burn_resistance=self.target.burn_resistance
        self.old_mat_burn_resistance=self.target.material.burn_resistance
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
            self.magma=Fluids.Magma(self.target,temp=random.gauss(self.strength*200,100))
            self.magma.splatter(intensity=3,volume=self.strength*2)

    def on_dispel(self):
        self.target.burn_resistance=self.old_burn_resistance
        self.target.material.burn_resistance=self.old_mat_burn_resistance

class BloodDrinking(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,**kwargs)
        self.strength=strength
        self.blood=100
        if hasattr(target,'edge'):
            self.base_edge=target.edge
            self.has_edge=True
        else:
            self.has_edge=False
        if hasattr(target,'tip'):
            self.base_tip=target.tip
            self.has_tip=True
        else:
            self.has_tip=False

    def on_turn(self):
        super().on_turn()
        if any(isinstance(i,Fluids.Blood) for i in self.target.coatings):
            self.blood+=1
            if self.has_edge==True:
                self.target.edge=self.base_edge*min(100/self.blood,0.99)
            if self.has_tip==True:
                self.target.tip=self.base_tip*min(100/self.blood,0.99)
            self.target.recover({'luc':2*self.strength})
            if self.target.equipped!=[]:
                owner=self.target.equipped[0].owner
                if owner!=None:
                    owner.stamina[0]=min(owner.stamina[0]+self.strength,owner.stamina[1])
                    owner.focus[0]=min(owner.focus[0]+self.strength,owner.focus[1])
                    owner.pain=max(owner.pain-self.strength,0)
            if self.blood>100:
                self.target.damage['deform']=max(0,self.target.damage['deform']-0.0001*self.blood)
            self.attempt_identification(10)
            return
        for i in self.target.equipped:
            if i.owner!=None and random.random()<1/i.stats['luc']:
                i.owner.stamina[0]-=3*self.strength
                i.owner.focus[0]-=3*self.strength
                i.owner.pain+=3*self.strength
                i.owner.combataction=True
                i.owner.attacked=True
                random.choice(i.layers).damage['cut']+=0.1*random.random()
                self.attempt_identification(10)
        if self.target.equipped==[] and random.random()<0.2:
            self.blood-=1
            if self.blood<=1:
                Shell.shell.log.addtext('The {} crumbles to dust!'.format(self.target.name))
                self.target.location=[None,None]
                if self.target.in_inventory:
                    self.target.in_inventory.inventory.remove(self.target)
                    self.target.in_inventory=None
            if self.has_edge==True:
                self.target.edge=self.base_edge*100/self.blood
            if self.has_tip==True:
                self.target.tip=self.base_tip*100/self.blood
            damagetype=random.choice(['dent','crack','rust','corrode','deform'])
            self.target.damage[damagetype]+=self.strength*random.random()/self.blood



    def on_strike(self,attack):
        super().on_strike(attack)
        luc=attack.attacker.stats['luc']
        drains=0
        for i in attack.damagedobjects:
            if hasattr(i,'fluid') and isinstance(i.fluid,Fluids.Blood):
                attack.basetarget.owner.stamina[0]-=2*self.strength
                attack.basetarget.owner.focus[0]-=2*self.strength
                attack.basetarget.owner.pain+=2*self.strength
                drains+=1
        if drains==0: return
        self.blood+=drains
        if self.has_edge==True:
            self.target.edge=self.target.edge*min(100/self.blood,0.99)
        if self.has_tip==True:
            self.target.tip=self.target.tip*min(100/self.blood,0.99)
        self.target.recover({'luc':2*drains*self.strength})
        if self.target.equipped!=[]:
            owner=self.target.equipped[0].owner
            if owner!=None:
                owner.stamina[0]=min(owner.stamina[0]+drains*self.strength,owner.stamina[1])
                owner.focus[0]=min(owner.focus[0]+drains*self.strength,owner.focus[1])
                owner.pain=max(owner.pain-drains*self.strength,0)
        if self.blood>100:
            self.target.damage['deform']=max(0,self.target.damage['deform']-0.0001*self.blood)
        self.attempt_identification(10)


    def on_struck(self,attack):
        super().on_struck(attack)
        if random.random()>0.3:
            if attack.weapon in (None,attack.limb):
                for i in attack.limb.layers:
                    i.damage['cut']+=random.random()*0.01*self.strength
                    if i.mode=='soft':
                        i.damage['bruise']+=random.random()*0.1*self.strength
                    elif i.mode=='ductile':
                        i.damage['dent']+=random.random()*0.01*self.strength
                    elif i.mode=='brittle':
                        i.damage['crack']+=random.random()*0.01*self.strength
                    self.blood+=1
                attack.attacker.stamina[0]-=self.strength
                attack.attacker.focus[0]-=self.strength
                attack.attacker.pain+=self.strength


    def on_destruction(self):
        if self.target.location==[None,None]:
            self.magma=Fluids.Blood(self.target.in_inventory,temp=random.gauss(self.strength*200,100))
            self.magma.splatter(intensity=3,volume=self.strength*2)
        else:
            self.magma=Fluids.Blood(self.target,temp=random.gauss(self.strength*200,100))
            self.magma.splatter(intensity=3,volume=self.strength*2)


    def on_dispel(self):
        if self.has_edge:
            self.target.edge=self.base_edge
        if self.has_tip:
            self.target.tip=self.base_tip

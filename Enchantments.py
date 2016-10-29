__author__ = 'Alan'

import BaseClasses
import Fluids
import random
import Shell
import Materials as Mats
import ai
from kivy.clock import Clock
import functools
from kivy.graphics import Color,Rectangle



#Item enchantments

class Acidic(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='acidic'
        self.strength=strength
        self.target.resistance['acid']*=1+self.strength/3
        self.acid=Fluids.Acid(None,strength=self.strength)

    def on_turn(self):
        super().on_turn()
        owner=None
        for i in self.target.equipped:
            Limb_Resistance_Modification(i,turns=2,strength=self.strength,res='acid')
            if owner==None:
                owner=i.owner
            if random.random()<(1/i.stats['luc'])**1.5:
                self.acid.add(i)
                self.attempt_identification(15)
        if owner!=None:
            Creature_Resistance_Modification(owner,turns=2,strength=self.strength/10,res='acid')
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

    def on_removal(self,**kwargs):
        self.target.resistance['acid']*=3/(self.strength+3)
        super().on_removal(**kwargs)

    def modify_strength(self,amount,**kwargs):
        oldstrength=self.strength
        super().modify_strength(amount,**kwargs)
        if self.strength<=0:
            self.on_removal(**kwargs)
            self.target.enchantments.remove(self)
            self.strength=oldstrength
            return
        if self in self.target.enchantments:
            self.target.resistance['acid']*=(1+self.strength/3)/(1+oldstrength/3)

class Burning(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='burning'
        self.classification=['magic','enchantment']
        self.strength=strength
        self.target.resistance['fire']*=1+self.strength/3

    def on_turn(self):
        super().on_turn()
        owner=None
        for i in self.target.equipped:
            Limb_Resistance_Modification(i,turns=2,strength=self.strength,res='fire')
            if owner==None:
                owner=i.owner
            if random.random()<(1/i.stats['luc'])**1.5:
                if random.random()<(1/i.stats['luc'])**1.5:
                    i.burn(random.gauss(self.strength*100,100),random.gauss(2,0.5),with_armor=False,source=self)
                    self.attempt_identification(20)
                else:
                    i.burn(random.gauss(self.strength*100,100),random.gauss(2,0.5),source=self)
                    if i.armor is None:
                        self.attempt_identification(20)
                    else:
                        self.attempt_identification(10)
        if owner!=None:
            Creature_Resistance_Modification(owner,turns=2,strength=self.strength/10,res='fire')

    def on_strike(self,attack):
        super().on_strike(attack)
        luc=attack.attacker.stats['luc']
        for i in attack.touchedobjects:
            if random.random()<luc/(10+luc):
                temp=random.gauss(self.strength*100,100)
                intensity=random.gauss(len(attack.touchedobjects)**0.5,0.1)
                if i.in_limb!=None:
                    temp=temp/i.in_limb.resistance['fire']
                    intensity=intensity/i.in_limb.resistance['fire']
                    if i.in_limb.owner!=None:
                        temp=temp/i.in_limb.owner.resistance['fire']
                        intensity=intensity/i.in_limb.owner.resistance['fire']
                        message=i.burn(temp,intensity,source=self,log=True,in_limb=True,limb=i.in_limb)
                        if i.in_limb.owner in Shell.shell.player.visible_creatures and i.in_limb.owner.alive and message[0]!='':
                            Shell.messages.append(message[0])
                else:
                    i.burn(temp,intensity,source=self)
                if attack.attacker==Shell.shell.player or attack.basetarget.owner==Shell.shell.player: self.attempt_identification(15)
                elif attack.basetarget.owner in Shell.shell.player.visible_creatures: self.attempt_identification(5)

    def on_struck(self,attack):
        super().on_struck(attack)
        if random.random()>0.3:
            try: attack.weapon.burn(random.gauss(self.strength*100,100),random.gauss(2,0.5))
            except AttributeError: attack.limb.burn(random.gauss(self.strength*100,100),random.gauss(2,0.5))
            if attack.basetarget.owner in Shell.shell.player.visible_creatures: self.attempt_identification(10)

    def on_destruction(self):
        if self.target.location==[None,None]:
            self.magma=Fluids.Magma(self.target.in_inventory,temp=random.gauss(self.strength*200,100))
            self.magma.splatter(intensity=3,volume=self.strength*2)
        else:
            self.magma=Fluids.Magma(self.target,temp=random.gauss(self.strength*200,100))
            self.magma.splatter(intensity=3,volume=self.strength*2)

    def on_removal(self,**kwargs):
        self.target.resistance['fire']*=3/(self.strength+3)
        super().on_removal(**kwargs)

    def modify_strength(self,amount,**kwargs):
        oldstrength=self.strength
        super().modify_strength(amount,**kwargs)
        if self.strength<=0:
            self.on_removal(**kwargs)
            self.target.enchantments.remove(self)
            self.strength=oldstrength
            return
        if self in self.target.enchantments:
            self.target.resistance['fire']*=(1+self.strength/3)/(1+oldstrength/3)

class Freezing(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='freezing'
        self.classification=['magic','enchantment']
        self.strength=strength
        self.target.resistance['ice']*=1+self.strength/3

    def on_turn(self):
        super().on_turn()
        owner=None
        for i in self.target.equipped:
            Limb_Resistance_Modification(i,turns=2,strength=self.strength,res='ice')
            if owner==None:
                owner=i.owner
            if random.random()<(1/i.stats['luc'])**1.5:
                if i.armor!=None and self.strength*random.random()>random.random()*(i.stats['luc']**0.5)/i.armor.heat_conduction:
                    Frozen_Limb(i,strength=self.strength/i.resistance['ice'])
                    if owner==Shell.shell.player:
                        Shell.messages.append("[color=C21D25]Your {} is frozen![/color]".format(i.name))
                    elif owner in Shell.shell.player.visible_creatures:
                        Shell.messages.append("[color=1F4CAD]{}'s {} is frozen![/color]".format(owner.name,i.name))
                    self.attempt_identification(20)
                elif i.armor==None:
                    Frozen_Limb(i,strength=self.strength/i.resistance['ice'])
                    if owner==Shell.shell.player:
                        Shell.messages.append("[color=C21D25]Your {} is frozen![/color]".format(i.name))
                    elif owner in Shell.shell.player.visible_creatures:
                        Shell.messages.append("[color=1F4CAD]{}'s {} is frozen![/color]".format(owner.name,i.name))
                    self.attempt_identification(20)
        if owner!=None:
            Creature_Resistance_Modification(owner,turns=2,strength=self.strength/10,res='ice')

    def on_strike(self,attack):
        super().on_strike(attack)
        message=None
        luc=attack.attacker.stats['luc']
        for i in attack.touchedobjects:
            if random.random()<luc/(10+luc):
                if i.in_limb!=None:
                    res=i.in_limb.resistance['ice']
                    if i.in_limb.owner!=None:
                        res*=i.in_limb.owner.resistance['ice']
                        chance=self.strength/res
                        chance=chance/(chance+i.in_limb.owner.stats['luc']**0.5)
                        if 0.2*chance**4>random.random():
                            Frozen_Creature(i.in_limb.owner,strength=self.strength/res)
                            if i.in_limb.owner==Shell.shell.player:
                                message="[color=C21D25]You are frozen solid![/color]"
                            elif i.in_limb.owner in Shell.shell.player.visible_creatures:
                                message="[color=1F4CAD]{} is frozen solid![/color]".format(i.in_limb.owner.name)
                        elif chance>random.random():
                            Frozen_Limb(i.in_limb,strength=self.strength/res)
                            if i.in_limb.owner==Shell.shell.player:
                                message="[color=C21D25]Your {} is frozen![/color]".format(i.in_limb.name)
                            elif i.in_limb.owner in Shell.shell.player.visible_creatures:
                                message="[color=1F4CAD]{}'s {} is frozen![/color]".format(i.in_limb.owner.name,i.in_limb.name)
                        if message!=None:
                            Shell.messages.append(message)
                if attack.attacker==Shell.shell.player or attack.basetarget.owner==Shell.shell.player: self.attempt_identification(15)
                elif attack.basetarget.owner in Shell.shell.player.visible_creatures: self.attempt_identification(5)

    def on_struck(self,attack):
        super().on_struck(attack)
        if 'melee' in attack.classification:
            chance=self.strength/attack.attacker.resistance['ice']
            chance=chance/(chance+attack.attacker.stats['luc']**0.5)
            if 0.2*chance**4>random.random():
                Frozen_Creature(attack.attacker,strength=self.strength/attack.attacker.resistance['ice'])
                if attack.attacker==Shell.shell.player:
                    Shell.messages.append("[color=C21D25]You are frozen solid![/color]".format(attack.limb.name))
                elif attack.attacker in Shell.shell.player.visible_creatures:
                    Shell.messages.append("[color=1F4CAD]{} is frozen solid![/color]".format(attack.attacker.name))
                return
            if 'weaponless' in attack.classification:
                chance=self.strength/(attack.limb.resistance['ice']*attack.attacker.resistance['ice'])
                if chance>random.random():
                    if attack.attacker==Shell.shell.player:
                        Shell.messages.append("[color=C21D25]Your {} is frozen![/color]".format(attack.limb.name))
                    elif attack.attacker in Shell.shell.player.visible_creatures:
                        Shell.messages.append("[color=1F4CAD]{}'s {} is frozen![/color]".format(attack.attacker.name,attack.limb.name))
                    Frozen_Limb(attack.limb,strength=self.strength/(attack.limb.resistance['ice']*attack.attacker.resistance['ice']))

    def on_destruction(self):
        location=[None,None]
        floor=None
        if self.target.location==[None,None]:
            try:
                location=self.target.in_inventory.location
                floor=self.target.in_inventory.floor
            except:
                location=[None,None]
        else:
            location=self.target.location
            floor=self.target.floor
        if location==[None,None]:
            return
        else:
            cell=floor.cells[location[0]][location[1]]
            frost=Shell.Abilities.Frost_Explosion(2*self.strength)
            frost.do(cell)

    def on_removal(self,**kwargs):
        self.target.resistance['ice']*=3/(self.strength+3)
        super().on_removal(**kwargs)

    def modify_strength(self,amount,**kwargs):
        oldstrength=self.strength
        super().modify_strength(amount,**kwargs)
        if self.strength<=0:
            self.on_removal(**kwargs)
            self.target.enchantments.remove(self)
            self.strength=oldstrength
            return
        if self in self.target.enchantments:
            self.target.resistance['ice']*=(1+self.strength/3)/(1+oldstrength/3)

class Vampiric(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='vampiric'
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
                if self.target in Shell.shell.player.visible_items or self.target.in_inventory==Shell.shell.player:
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
        if not 'melee' in attack.classification:
            return
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

    def on_removal(self,**kwargs):
        if self.has_edge:
            self.target.edge=self.base_edge
        if self.has_tip:
            self.target.tip=self.base_tip
        super().on_removal(**kwargs)

class Unstable(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='unstable'
        self.strength=strength


    def on_turn(self):
        super().on_turn()
        if random.random()<1/self.strength**2:
            self.target.on_destruction()
            self.target.damage['disintegrate']=1
            self.target.functioncheck()
            if self.target.in_inventory==Shell.shell.player or self.target in Shell.shell.player.visible_items:
                Shell.shell.log.addtext('The {} returns to the void'.format(self.target.name))
                #try: Shell.shell.player.inventory.remove(self.target)
                #except: pass
            try: self.target.in_inventory.inventory.remove(self.target)
            except: pass
            pass

class Bound(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='bound'
        self.strength=strength
        self.target=target
        self.limb=None

    def on_equip(self):
        if self.limb!=None: return
        attach=self.target.equipped[0]
        self.limb=Shell.Limbs.Bound_Item_Limb(item=self.target,owner=attach.owner)
        #if self.target.in_inventory!=None:
         #   self.target.in_inventory.inventory.remove(self.target)
          #  self.target.in_inventory=None
        if attach.owner==Shell.shell.player:
            Shell.shell.log.addtext('The {} fuses itself to your {}!'.format(self.target.name,attach.name))
        elif attach.owner in Shell.shell.player.visible_creatures:
            Shell.shell.log.addtext('The {} fuses itself to the {} of {}'.format(self.target.name,attach.name,attach.owner.name))

    def on_removal(self,**kwargs):
        try:
            self.limb.owner.limbs.remove(self.limb)
            self.limb.attachpoint.limbs.remove(self.limb)
            if self.target not in self.limb.owner.inventory:
                self.limb.owner.inventory_add(self.target)
        except:
            pass
        super().on_removal(**kwargs)

    def on_destruction(self):
        super().on_destruction()
        try:
            self.limb.owner.limbs.remove(self.limb)
            self.limb.attachpoint.limbs.remove(self.limb)
            self.target.in_inventory=self.limb.owner
            if self.limb.owner==Shell.shell.player:
                Shell.shell.log.addtext('The {} is no longer fused to your {}'.format(self.target.name,self.limb.attachpoint.name))
            elif self.limb.owner in Shell.shell.player.visible_creatures:
                Shell.shell.log.addtext("The {} is no longer fused to {}'s {}".format(self.target.name,self.limb.owner.name,self.limb.attachpoint.name))
        except:
            pass

class Indestructable(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='indestructable'
        self.strength=strength
        self.old_mode=self.target.mode
        self.old_mat_mode=self.target.material.mode
        self.target.mode='indestructable'
        self.target.material.mode='indestructable'
        self.old_acid_reaction=self.target.acid_reaction
        self.target.acid_reaction='indestructable'
        self.old_mat_acid_reaction=self.target.material.acid_reaction
        self.target.material.acid_reaction='indestructable'
        self.old_heat_reaction=self.target.heat_reaction
        self.target.heat_reaction='indestructable'
        self.old_mat_heat_reaction=self.target.material.heat_reaction
        self.target.material.heat_reaction='indestructable'

    def on_struck(self,attack):
        super().on_struck(attack)
        self.attempt_identification(5)

    def on_removal(self,**kwargs):
        self.target.mode=self.old_mode
        self.target.material.mode=self.old_mode
        self.target.acid_reaction=self.old_acid_reaction
        self.target.material.acid_reaction=self.old_mat_acid_reaction
        self.target.heat_reaction=self.old_heat_reaction
        self.target.material.heat_reaction=self.old_mat_heat_reaction
        super().on_removal(**kwargs)

class Shifting(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='shifting'
        self.strength=strength
        r={}
        if hasattr(self.target,'length'): r['length']=self.target.length
        else: r['length']=None
        if hasattr(self.target,'thickness'): r['thickness']=self.target.thickness
        else: r['thickness']=None
        if hasattr(self.target,'edge'): r['edge']=self.target.edge
        else: r['edge']=None
        if hasattr(self.target,'tip'): r['tip']=self.target.tip
        else: r['tip']=None
        if hasattr(self.target,'head'): r['head']=self.target.head
        else: r['head']=None
        if hasattr(self.target,'headvolume'): r['headvolume']=self.target.headvolume
        else: r['headvolume']=None
        if hasattr(self.target,'headsize'): r['headsize']=self.target.headsize
        else: r['headsize']=None
        if hasattr(self.target,'width'): r['width']=self.target.width
        else: r['width']=None
        if hasattr(self.target,'in_radius'):r['in radius']=self.target.in_radius
        else: r['in radius']=None
        if hasattr(self.target,'quality'): r['quality']=self.target.quality
        else: r['quality']=None
        self.base=r


    def on_turn(self):
        if random.random()>0.5:
            self.old_enchants=self.target.enchantments
            self.old_damage=self.target.damage
            self.old_index=self.target.inventory_index
            material=random.choice([Mats.Bone_Material,Mats.Aluminum,Mats.Basalt_Fiber,Mats.Brass,Mats.Bronze,Mats.Copper,Mats.Cotton,
                          Mats.Demonic_Material,Mats.Duraluminum,Mats.Iron,Mats.Steel,Mats.Fur,Mats.Hair_Material,
                          Mats.Keratin,Mats.Leather,Mats.Silk,Mats.Silver,Mats.Slime,Mats.Titanium,Mats.Wool,Mats.Spider_Silk,
                          Mats.Zicral,Mats.Wood,Mats.Flesh_Material])
            old_in_inventory=self.target.in_inventory
            old_inventory_index=self.target.inventory_index
            touched=self.target.touched_by_player
            seen=self.target.seen_by_player
            r={}
            if hasattr(self.target,'length'): r['length']=self.base['length']*random.triangular(4/5,5/4,1)
            else: r['length']=None
            if hasattr(self.target,'thickness'): r['thickness']=self.base['thickness']*random.triangular(4/5,5/4,1)
            else: r['thickness']=None
            if hasattr(self.target,'edge'): r['edge']=self.base['edge']*random.triangular(4/5,5/4,1)
            else: r['edge']=None
            if hasattr(self.target,'tip'): r['tip']=self.base['tip']*random.triangular(4/5,5/4,1)
            else: r['tip']=None
            if hasattr(self.target,'head'): r['head']=self.base['head']*random.triangular(4/5,5/4,1)
            else: r['head']=None
            if hasattr(self.target,'headvolume'): r['headvolume']=self.base['headvolume']*random.triangular(4/5,5/4,1)
            else: r['headvolume']=None
            if hasattr(self.target,'headsize'): r['headsize']=self.base['headsize']*random.triangular(4/5,5/4,1)
            else: r['headsize']=None
            if hasattr(self.target,'width'): r['width']=self.base['width']*random.triangular(4/5,5/4,1)
            else: r['width']=None
            if hasattr(self.target,'in_radius'):
                r['in radius']=self.base['in radius']*random.triangular(4/5,5/4,1)
                if self.target.equipped!=[]:
                    r['in radius']=max(self.target.equipped[0].radius,r['in radius'])
                    r['in radius']=min(self.target.equipped[0].radius*2,r['in radius'])
            else: r['in radius']=None
            if hasattr(self.target,'quality'): r['quality']=self.base['quality']*random.triangular(4/5,5/4,1)
            else: r['quality']=None
    
            equipped=self.target.equipped.copy()
            self.target.__init__(painfactor=self.target.painfactor,length=r['length'],thickness=r['thickness'],edge=r['edge'],tip=r['tip'],
                          head=r['head'],headvolume=r['headvolume'],headsize=r['headsize'],width=r['width'],in_radius=r['in radius'],
                          quality=r['quality'],material=material,power=self.target.power)
            self.target.equipped=equipped
            self.target.in_inventory=old_in_inventory
            self.target.inventory_index=old_inventory_index
            self.target.seen_by_player=seen
            self.target.touched_by_player=touched
            self.target.generate_descriptions(per=Shell.shell.player.stats['per'])
                
            self.target.enchantments=self.old_enchants
            self.target.damage=self.old_damage
            self.target.functioncheck()
            self.attempt_identification(30)

class Blinking(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='blinking'
        self.strength=strength

    def on_turn(self):
        player=Shell.shell.player
        super().on_turn()
        for i in self.target.equipped:
            if random.random()<(self.strength**0.5)/(i.stats['luc']*i.stats['luc']*i.resistance['teleport']):
                creature=i.owner
                equipped_items=0
                for j in i.equipment:
                    if i.equipment[j]!=None:
                        equipped_items+=1
                if i.armor!=None and i.armor!=self.target:
                    armor=i.armor
                    if armor.resistance['teleport']<random.random()*self.strength**0.5:
                        creature.unequip(armor,log=False)
                        creature.inventory.remove(armor)
                        armor.in_inventory=None
                        creature.floor.place_item(armor,location=None)
                        if creature==player:
                            Shell.messages.append("[color=1F4CAD]Your {} vanishes![/color]".format(armor.name))
                            self.attempt_identification(15)
                        elif creature in player.visible_creatures:
                            Shell.messages.append("[color=1F4CAD]{}'s {} vanishes![/color]".format(creature.name,armor.name))
                            self.attempt_identification(15)
                elif random.random()>0.5 and equipped_items>1:
                    for j in i.equipment:
                        if i.equipment[j]!=self.target:
                            item=i.equipment[j]
                            if item.resistance['teleport']<random.random()*self.strength**0.5:
                                creature.unequip(item)
                                creature.inventory.remove(item)
                                item.in_inventory=None
                                creature.floor.place_item(item)
                                if creature==player:
                                    Shell.messages.append("[color=1F4CAD]Your {} vanishes![/color]".format(item.name))
                                    self.attempt_identification(15)
                                elif creature in player.visible_creatures:
                                    Shell.messages.append("[color=1F4CAD]{}'s {} vanishes![/color]".format(creature.name,item.name))
                                    self.attempt_identification(15)
                elif creature.resistance['teleport']<random.random()*self.strength**0.5:
                    creature.floor.cells[creature.location[0]][creature.location[1]].contents.remove(creature)
                    creature.floor.place_creature(creature)
                    if creature==player:
                        Shell.messages.append("[color=1F4CAD]You feel disoriented.[/color]")
                        self.attempt_identification(10)
                    elif creature in player.visible_creatures:
                        Shell.messages.append("[color=1F4CAD]{} vanishes from sight![/color]".format(creature.name))
                        self.attempt_identification(5)

    def on_strike(self,attack):
        super().on_strike(attack)
        luc=attack.attacker.stats['luc']
        if hasattr(attack.target,'stats'):d_luc=attack.target.stats['luc']
        elif hasattr(attack.basetarget,'stats'):d_luc=attack.basetarget.stats['luc']
        else: d_luc=10
        defender=attack.basetarget.owner
        effect_chance=2*self.strength*luc/(d_luc*d_luc)
        for i in attack.touchedobjects:
            if random.random()<effect_chance/((1+effect_chance)*i.resistance['teleport']):
                if hasattr(i,'equipped') and any(isinstance(j,Shell.Limb) for j in i.equipped):
                    defender.unequip(i,log=False)
                    defender.inventory.remove(i)
                    i.in_inventory=None
                    defender.floor.place_item(i)
                    if defender==Shell.shell.player:
                        Shell.messages.append("[color=1F4CAD]Your {} vanishes![/color]".format(i.name))
                        self.attempt_identification(15)
                    elif defender in Shell.shell.player.visible_creatures:
                        Shell.messages.append("[color=1F4CAD]{}'s {} vanishes![/color]".format(defender.name,i.name))
                        self.attempt_identification(10)
                elif i in attack.basetarget.layers and defender.resistance['teleport']<random.random()*self.strength**0.5:
                    defender.floor.cells[defender.location[0]][defender.location[1]].contents.remove(defender)
                    defender.floor.place_creature(defender)
                    if defender==Shell.shell.player:
                        Shell.messages.append("[color=1F4CAD]You feel disoriented[/color]")
                        self.attempt_identification(10)
                    elif defender in Shell.shell.player.visible_creatures:
                        Shell.messages.append("[color=1F4CAD]{} vanishes from sight![/color]".format(defender.name))
                        self.attempt_identification(10)

    def on_struck(self,attack):
        super().on_struck(attack)
        if 'ranged' in attack.classification and 'weaponless' in attack.classification:
            return
        try: luc=self.target.stats['luc']
        except:
            try: luc=attack.basetarget.stats['luc']
            except: luc=self.strength
        try: d_luc=attack.weapon.stats['luc']
        except:
            try: d_luc=attack.armor.stats['luc']
            except: d_luc=attack.limb.stats['luc']
        effect_chance=3*self.strength*luc/(d_luc*d_luc)
        item=None
        if random.random()<effect_chance/(1+effect_chance):
            if attack.weapon!=None and not any(isinstance(i,Bound) for i in attack.weapon.enchantments) and 'weaponless' not in attack.classification:
                item=attack.weapon
            elif attack.limb.armor!=None and not any(isinstance(i,Bound) for i in attack.limb.armor.enchantments):
                item=attack.limb.armor
            if item!=None and item.resistance['teleport']<random.random()*self.strength**0.5:
                attack.attacker.unequip(item,log=False)
                try: attack.attacker.inventory.remove(item)
                except ValueError: pass
                item.in_inventory=None
                attack.attacker.floor.place_item(item)
                if attack.attacker==Shell.shell.player:
                    Shell.messages.append("[color=1F4CAD]Your {} vanishes![/color]".format(item.name))
                    self.attempt_identification(10)
                elif attack.attacker in Shell.shell.player.visible_creatures:
                    Shell.messages.append("[color=1F4CAD]{}'s {} vanishes![/color]".format(attack.attacker.name,item.name))
                    self.attempt_identification(10)
                return
            if attack.attacker.resistance['teleport']<random.random()*self.strength**0.5:
                attack.attacker.floor.cells[attack.attacker.location[0]][attack.attacker.location[1]].contents.remove(attack.attacker)
                attack.attacker.floor.place_creature(attack.attacker)
                if attack.attacker==Shell.shell.player:
                    Shell.messages.append("[color=1F4CAD]You feel disoriented[/color]")
                    self.attempt_identification(10)
                elif attack.attacker in Shell.shell.player.visible_creatures:
                    Shell.messages.append("[color=1F4CAD]{} vanishes from sight![/color]".format(attack.attacker.name))
                    self.attempt_identification(10)

    def on_destruction(self):
        pass

class Numbing(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='numbing'
        self.strength=strength
        self.oldpainfactors={}

    def on_equip(self):
        super().on_equip()
        self.oldpainfactors={}
        for i in self.target.equipped:
            self.oldpainfactors[i]=i.painfactor
            i.painfactor=i.painfactor/self.strength

    def on_turn(self):
        super().on_turn()
        for i in self.oldpainfactors.copy():
            if i not in self.target.equipped:
                i.painfactor=i.painfactor*self.strength
                del self.oldpainfactors[i]
        if self.target.equipped!=[] and self.strength>random.randint(0,self.target.equipped[0].owner.stats['luc']):
            for i in self.target.equipped:
                if hasattr(i,'dexterity'):
                    i.dexterity=i.dexterity/self.strength
                    i.ability=max(0,i.ability-0.01)
                if hasattr(i,'balance'):
                    i.balance=i.balance/self.strength
                    i.ability=max(0,i.ability-0.01)
                if hasattr(i,'vision'):
                    i.vision=i.vision/self.strength
                    i.ability=max(0,i.ability-0.01)
                if hasattr(i,'smell_sense'):
                    i.smell_sense=i.smell_sense/self.strength
                    i.ability=max(0,i.ability-0.01)
                if hasattr(i,'hearing'):
                    i.hearing=i.hearing/self.strength
                    i.ability=max(0,i.ability-0.01)

    def on_strike(self,attack):
        super().on_strike(attack)
        luc=attack.attacker.stats['luc']
        if not isinstance(attack.basetarget,BaseClasses.Limb):
            return
        numb=False
        for i in attack.touchedobjects:
            if i in attack.basetarget.layers and random.random()<luc/(10+luc):
                numb=True
        if numb==True:
            limb=attack.basetarget
            for i in limb.enchantments:
                if isinstance(i,Numb):
                    i.turns+=self.strength
                    return
            Numb(limb,turns=int(random.gauss(self.strength,1)),strength=self.strength)
            if limb.owner==Shell.shell.player:
                Shell.messages.append("[color=1F4CAD]Your {} goes numb[/color]".format(limb.name))
                self.attempt_identification(10)

    def on_struck(self,attack):
        try:
            if attack.basetarget.owner==Shell.shell.player:
                message=' '.join([Shell.messages.pop(),"[color=1F4CAD]You barely feel a thing.[/color]"])
                Shell.messages.append(message)
                self.attempt_identification(10)
        except:
            pass

    def on_removal(self,**kwargs):
        for i in self.oldpainfactors.copy():
            i.painfactor=i.painfactor*self.strength
            del self.oldpainfactors[i]
        super().on_removal(**kwargs)

class Bleeding(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        if target.fluid==None:
            return
        if target.in_limb==None:
            return
        if target.in_limb.owner==None or target.in_limb.owner.alive==False:
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='bleeding'
        self.strength=strength
        self.attempt_identification(10*strength)
        self.category="physical"
        self.classification=["physical","negative"]

    def on_turn(self):
        self.target.fluid.splatter(volume=self.strength,intensity=0.5)
        self.modify_strength(-random.random()*self.target.in_limb.owner.stats['luc']**0.5)
        if self.strength<=0:
            self.strength=0
            self.on_removal()
            self.target.enchantments.remove(self)

class Rot(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        if target.rottable==False:
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='rot'
        self.category='physical'
        self.strength=strength
        self.minimum_damage=target.damage.copy()
        self.attempt_identification(10*strength)
        self.loggable=True

    def on_turn(self):
        if self.target.in_limb!=None:
            luc=self.target.in_limb.stats['luc']
        elif self.target.in_inventory!=None:
            luc=self.target.in_inventory.stats['luc']
        else:
            luc=10
        luc*=(self.target.rot_resistance+1)
        if self.strength/((luc+self.strength)*self.target.resistance['rot'])>random.random():
            for i in self.minimum_damage:
                if self.target.damage[i]<self.minimum_damage[i]:
                    self.target.damage[i]+=(self.minimum_damage[i]-self.target.damage[i])*random.random()*random.random()/self.target.resistance['rot']
                    self.target.damage[i]=min(self.target.damage[i],self.minimum_damage[i])
                else:
                    self.minimum_damage[i]=self.target.damage[i]
            oldrot=self.target.damage['rot']
            self.target.damage['rot']+=(self.target.damage['cut']+self.target.damage['pierce']+self.target.damage['crack']*0.6+
                                        self.target.damage['burn']+self.target.damage['corrode']+self.target.damage['crush']
                                        )*random.random()*self.strength/(10*max(luc-self.strength,1))/self.target.resistance['rot']
            self.target.damage['rot']=min(1,self.target.damage['rot'])
            try:
                self.target.in_limb.owner.pain+=(1-self.target.damage['rot'])*self.target.damage['rot']*10/(
                    self.target.resistance['rot']*self.target.in_limb.owner.stats['wil']**0.5)
            except:
                pass
            if random.random()>0.75 and self.loggable==True and oldrot<1 and self.target.damage['rot']>oldrot:
                if self.target.in_limb!=None:
                    if self.target.in_limb.owner==Shell.shell.player:
                        Shell.messages.append("[color=C21D25]The {} on your {} rots![/color]".format(self.target.name,self.target.in_limb.name))
                    elif self.target.in_limb.owner in Shell.shell.player.visible_creatures:
                        Shell.messages.append("[color=1F4CAD]The {} on {}'s {} rots![/color]".format(self.target.name,self.target.in_limb.owner.name,self.target.in_limb.name))
                elif self.target.in_inventory==Shell.shell.player:
                    Shell.messages.append("[color=C21D25]Your {} decays[/color]".format(self.target.name))
        if random.random()*luc*(0.5)>random.random()*(self.strength+10*self.target.damage['rot']):
            self.modify_strength(-1)
        if self.strength<=0:
            self.on_removal()
            self.target.enchantments.remove(self)

class Magic_Eating(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='magic eating'
        self.strength=strength
        self.magic_consumed=target.magic_contamination.copy()
        target.magic_contamination={'dark':0,'elemental':0,'summoning':0,'transmutation':0,'arcane':0,'total':0}

    def on_turn(self):
        super().on_turn()
        if self.target.equipped!=[] and self.target.equipped[0].owner!=None:
            if self.strength/100>random.random():
                magic_drained=0
                eaten_magic=self.target.equipped[0].owner.magic_contamination.copy()
                for i in ('dark','elemental','summoning','transmutation','arcane'):
                    self.target.equipped[0].owner.magic_contamination[i]-=random.randint(0,self.strength)
                    if self.target.equipped[0].owner.magic_contamination[i]<0:
                        self.target.equipped[0].owner.magic_contamination[i]=0
                    eaten_magic[i]-=self.target.equipped[0].owner.magic_contamination[i]
                    self.magic_consumed[i]+=eaten_magic[i]
                    magic_drained+=eaten_magic[i]
                self.magic_consumed['total']=sum(self.magic_consumed[i] for i in ('dark','elemental','summoning','transmutation','arcane'))
                Spell_Failure(self.target.equipped[0].owner,turns=2,strength=magic_drained)
                if self.target.equipped[0].owner==Shell.shell.player:
                    self.attempt_identification(magic_drained)
        for i in ('dark','elemental','summoning','transmutation','arcane','total'):
            self.magic_consumed[i]+=self.target.magic_contamination[i]
            self.target.magic_contamination[i]=0
            if self.target.equipped!=[] and self.target.equipped[0].owner!=None:
                if i=='dark' and self.magic_consumed[i]/300>random.random():
                    power=random.randint(1,int(self.magic_consumed[i]+1))
                    self.magic_consumed[i]-=power
                    power=int(1.5*power**0.5+1)
                    Creature_Stat_Modification(self.target.equipped[0].owner,turns=self.strength,strength=power,stat='t')
                if i=='elemental' and self.magic_consumed[i]/300>random.random():
                    power=random.randint(1,int(self.magic_consumed[i]+1))
                    self.magic_consumed[i]-=power
                    power=int(1.5*power**0.5+1)
                    Creature_Stat_Modification(self.target.equipped[0].owner,turns=self.strength,strength=power,stat='s')
                if i=='summoning' and self.magic_consumed[i]/300>random.random():
                    power=random.randint(1,int(self.magic_consumed[i]+1))
                    self.magic_consumed[i]-=power
                    power=int(1.5*power**0.5+1)
                    Creature_Stat_Modification(self.target.equipped[0].owner,turns=self.strength,strength=power,stat='l')
                if i=='transmutation' and self.magic_consumed[i]/300>random.random():
                    power=random.randint(1,int(self.magic_consumed[i]+1))
                    self.magic_consumed[i]-=power
                    power=int(1.5*power**0.5+1)
                    Creature_Stat_Modification(self.target.equipped[0].owner,turns=self.strength,strength=power,stat='p')
                if i=='arcane' and self.magic_consumed[i]/300>random.random():
                    power=random.randint(1,int(self.magic_consumed[i]+1))
                    self.magic_consumed[i]-=power
                    power=int(1.5*power**0.5+1)
                    Creature_Stat_Modification(self.target.equipped[0].owner,turns=self.strength,strength=power,stat='w')

    def on_strike(self,attack):
        super().on_strike(attack)
        magic_drained=-self.magic_consumed.get('total')
        for i in attack.touchedobjects:
            if self.strength/(5+self.strength)<random.random(): continue
            if i.in_limb!=None and i.in_limb.owner!=None:
                eaten_magic=i.in_limb.owner.magic_contamination.copy()
                for j in ('dark','elemental','summoning','transmutation','arcane'):
                    i.in_limb.owner.magic_contamination[j]-=random.randint(0,int(self.strength*random.random()))
                    if i.in_limb.owner.magic_contamination[j]<0:
                        i.in_limb.owner.magic_contamination[j]=0
                    eaten_magic[j]-=i.in_limb.owner.magic_contamination[j]
                    self.magic_consumed[j]+=eaten_magic[j]
                    Spell_Failure(i.in_limb.owner,turns=2,strength=magic_drained)
            elif hasattr(i,'magic_contamination'):
                eaten_magic=i.magic_contamination.copy()
                for j in ('dark','elemental','summoning','transmutation','arcane'):
                    i.magic_contamination[j]-=random.randint(0,int(self.strength*random.random()))
                    if i.magic_contamination[j]<0:
                        i.magic_contamination[j]=0
                    eaten_magic[j]-=i.magic_contamination[j]
                    self.magic_consumed[j]+=eaten_magic[j]
        self.magic_consumed['total']=sum(self.magic_consumed[i] for i in ('dark','elemental','summoning','transmutation','arcane'))
        if attack.attacker==Shell.shell.player or attack.basetarget.owner==Shell.shell.player:
            self.attempt_identification((magic_drained+self.magic_consumed['total'])/2)

    def on_struck(self,attack):
        super().on_struck(attack)
        if self.strength/(5+self.strength)>random.random():
            if attack.weapon==None or attack.weapon==attack.limb:
                i=attack.limb.owner
            elif attack.weapon!=None:
                i=attack.weapon
            else:
                return
            magic_drained=0
            eaten_magic=i.magic_contamination.copy()
            for j in ('dark','elemental','summoning','transmutation','arcane'):
                i.magic_contamination[j]-=random.randint(0,int(self.strength*random.random()))
                if i.magic_contamination[j]<0:
                    i.magic_contamination[j]=0
                eaten_magic[j]-=i.magic_contamination[j]
                self.magic_consumed[j]+=eaten_magic[j]
                magic_drained+=eaten_magic[j]
            Spell_Failure(i,turns=2,strength=magic_drained)
            self.magic_consumed['total']=sum(self.magic_consumed[i] for i in ('dark','elemental','summoning','transmutation','arcane'))

            if attack.attacker==Shell.shell.player: self.attempt_identification(magic_drained)

    def on_destruction(self):
        if self.target.location==[None,None]:
            loc=self.target.in_inventory.location
            floor=self.target.in_inventory.floor
        else:
            loc=self.target.location
            floor=self.target.floor
        blast_radius=2*self.strength**0.5
        circle=floor.get_circle(loc,blast_radius,require_los=True)
        targets=[]
        for i in circle:
            d=i.distance_to(floor.cells[loc[0]][loc[1]])+1
            intensity=1/d**0.5
            shade=(1-intensity)/2
            Clock.schedule_once(functools.partial(i.animate_flash,(shade,shade,shade,intensity/(0.3+intensity)),(0.1,0.1,0.1,0.1),15),15/60)
            for j in i.creatures:
                targets.append(j)
                for k in j.inventory:
                    if self.strength/(self.strength+15)>random.random():
                        targets.append(k)
            for j in i.items:
                targets.append(j)

        for i in targets:
            for j in ('dark','elemental','summoning','transmutation','arcane'):
                i.magic_contamination[j]-=random.randint(0,self.strength)
                i.magic_contamination[j]=max(i.magic_contamination[j],0)

    def on_removal(self,**kwargs):
        pass



#Limb enchantments

class Numb(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Limb):
            return
        if not any(isinstance(i,Numb) for i in target.enchantments):
            new=True
        else: new=False
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='numb'
        self.strength=strength
        self.oldpainfactor=self.target.painfactor
        self.target.painfactor=0
        if self.target.owner==Shell.shell.player:
            self.attempt_identification(30)
            if new==True: Shell.messages.append("[color=1F4CAD]Your {} goes numb![/color]".format(self.target.name))
        elif self.target.owner in Shell.shell.player.visible_creatures:
            if random.random()*Shell.shell.player.stats['per']>random.random()*10 and new==True:
                Shell.messages.append("[color=1F4CAD]{}'s {} goes numb[/color]".format(self.target.owner.name,self.target.name))

    def on_turn(self):
        super().on_turn()
        self.target.ability-=(self.strength-0.9)/(self.strength+1)
        self.target.ability=max(self.target.ability,0)


    def on_dispel(self,**kwargs):
        self.target.painfactor=self.oldpainfactor

class Burning_Limb(BaseClasses.Enchantment):
    def __init__(self,target,turns=10,strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Limb):
            return
        if not any(isinstance(i,Numb) for i in target.enchantments):
            new=True
        else: new=False
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='on fire'
        self.strength=strength
        self.classification=['fire','negative']
        self.category='physical'
        self.oldpainfactor=self.target.painfactor
        self.target.painfactor=0
        if self.target.owner==Shell.shell.player:
            self.identified=True
            self.detected=True
            if new==True: Shell.messages.append("[color=C21D25][b]Your {} catches fire![/color][/b]".format(self.target.name))
        elif self.target.owner in Shell.shell.player.visible_creatures:
            Shell.messages.append("[color=1F4CAD]{}'s {} catches fire[/color]".format(self.target.owner.name,self.target.name))
        self.target.coatings=[]

    def on_turn(self):
        if self.target.owner==Shell.shell.player:
            Shell.messages.append("[color=C21D25]Your {} burns![/color]".format(self.target.name))
        elif self.target.owner in Shell.shell.player.visible_creatures:
            Shell.messages.append("[color=1F4CAD]{}'s {} burns![/color]".format(self.target.owner.name,self.target.name))
        Shell.messages.append(1)
        burning_layer=None
        burntemp=self.strength*100
        layers=list(self.target.layers)
        while layers!=[]:
            layer=layers.pop()
            for i in layer.coatings:
                if i.flammable:
                    self.turns+=random.randint(1,10)
                    self.strength+=random.randint(1,4)
                else:
                    i.burn(burntemp,1)
                    self.turns-=1
                    self.strength-=1
            if layer.damage['burn']>=1:
                continue
            if layer.heat_reaction not in ('burn','ignite'):
                break
            burning_layer=layer
            burntemp=max(burntemp,burning_layer.burn_temp)
            break
        self.target.burn(burntemp,3*random.random())
        if burning_layer==None:
            self.turns=0
        else:
            self.strength+=1
        Shell.messages.append(-1)
        super().on_turn()

class Magical_Grasp(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Limb):
            return
        if 'grasp' in target.equipment:
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='magical grasp'
        self.strength=strength
        if 'grasp' not in self.target.equipment:
            self.added_equipment_slot=True
            self.oldgrasp=self.target.grasp
            self.target.grasp=True
            self.target.equipment['grasp']=None
            self.target.primaryequip.append('grasp')
            self.target.dexterity=strength
        else:
            self.added_equipment_slot=False

    def on_turn(self):
        self.target.dexterity=self.strength*self.target.ability
        if self.target.dexterity<=0:
            self.target.grasp=False
            if self.target.equipment['grasp'] is not None and not any(isinstance(i,Bound) for i in self.target.equipment['grasp'].enchantments):
                if self.target.equipment['grasp'].equipped==[self]:
                    try: self.target.owner.unequip(self.target.equipment['grasp'],drop=True)
                    except: self.target.unequip('grasp',drop=True)

                else:
                    self.target.unequip('grasp',drop=False)
        else:
            self.target.grasp=True

    def on_dispel(self,**kwargs):
        if self.added_equipment_slot==True:
            if self.target.equipment['grasp']!=None:
                self.target.unequip('grasp',drop=True,log=False)
            del self.target.equipment['grasp']
            self.target.primaryequip.remove('grasp')
            self.target.grasp=self.oldgrasp

class Magical_Balance(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Limb):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='magical balance'
        self.strength=strength
        if not self.target.support:
            self.target.support=True
            self.target.balance=self.strength
            self.granted_support=True
        else:
            self.granted_support=False


    def on_turn(self):
        self.target.balance=self.strength*self.target.ability
        if self.target.balance>0:
            self.target.support=True
            self.target.movement['walk']+=self.target.balance
        else: self.target.support=False

    def on_dispel(self,**kwargs):
        if self.granted_support==True:
            self.target.support=False
            del self.target.balance

class Limb_Stat_Modification(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,stat='s',**kwargs):
        if not isinstance(target,BaseClasses.Limb):
            return
        super().__init__(target,turns=turns,strength=strength,combine=False,**kwargs)
        self.classname='limb stat modification'
        self.display=False
        self.stat_modified=stat
        self.strength=strength
        self.target.statmodifiers[stat]+=strength
        self.oldmodifier=strength

    def on_turn(self):
        if self.strength!=self.oldmodifier:
            self.target.statmodifiers[self.stat_modified]-=self.oldmodifier
            self.oldmodifier=self.strength
            self.target.statmodifiers[self.stat_modified]+=self.strength
        super().on_turn()

    def on_removal(self,**kwargs):
        self.target.statmodifiers[self.stat_modified]-=self.oldmodifier
        super().on_removal(**kwargs)

class Grasping(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Limb):
            return
        super().__init__(target,turns=turns,strength=strength,combination_type='max',**kwargs)
        self.classname='holding on'
        self.strength=strength
        self.category='physical'
        self.classification=["physical","grasp","movement impairing"]
        self.held=None

    def on_turn(self):
        self.target.ability=0

    def limb_function_modification(self):
        self.target.ability=0

class Held(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Limb):
            return
        super().__init__(target,turns=turns,strength=strength,combination_type='max',**kwargs)
        self.classname='held'
        self.strength=strength
        self.category='physical'
        self.classification=["physical","grasp","movement impairing"]
        self.grasping=None

    def on_turn(self):
        self.target.ability=0

    def limb_function_modification(self):
        self.target.ability=0

class Frozen_Limb(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Limb):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='frozen'
        self.classification=['incapacitate','magic','ice']
        self.display=False
        self.strength=strength
        if self.target==Shell.shell.player:
            self.removalmessage="[b][color=1FAD39]You can move your {} again[/b][/color]".format(self.target.name)
        else:
            self.removalmessage="[color=1F4CAD]{}'s {} is no longer frozen[/color]".format(self.target.owner.name,self.target.name)

    def on_turn(self):
        res=self.target.resistance['magic']*self.target.resistance['ice']*self.target.resistance['elemental']
        try:
            owner=self.target.owner
            res*=owner.resistance['magic']*owner.resistance['ice']*owner.resistance['elemental']
        except:
            pass
        self.target.ability=0
        if hasattr(self.target,'vision'):
            self.target.vision=0
        if hasattr(self.target,'smell_sense'):
            self.target.smell=0
        if hasattr(self.target,'hearing'):
            self.target.hearing=0
        if hasattr(self.target,'dexterity'):
            self.target.dexterity=0
        super().on_turn()
        if self.strength<=0:
            self.on_removal()
            if self in self.target.enchantments: self.target.enchantments.remove(self)
            return
        if res*self.target.stats['luc']*random.random()>self.strength*random.random():
            self.modify_strength(-random.random()*random.random()*self.target.stats['luc']*res)
            self.strength=int(self.strength)

class Limb_Resistance_Modification(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,res='random',**kwargs):
        if not isinstance(target,BaseClasses.Limb):
            return
        super().__init__(target,turns=turns,strength=strength,combine=False,**kwargs)
        self.classname='limb resistance modification'
        self.display=False
        if res!='random':
            self.res_modified=res
        else:
            self.res_modified=random.choice(['teleport','fire','ice','physical','acid','lightning','poison','pain',
                                             'psychic','divine','magic','dark','disable','rot','death','arcane',
                                             'elemental','transmutation'])
        self.strength=strength
        if self.strength>=0:
            self.target.resistance[self.res_modified]*=(1+self.strength/30)
        elif self.strength<=0:
            self.target.resistance[self.res_modified]*=1/(1-self.strength/30)

    def on_removal(self,**kwargs):
        if self.strength>0:
            self.target.resistance[self.res_modified]*=1/(1+self.strength/30)
        elif self.strength<0:
            self.target.resistance[self.res_modified]*=(1-self.strength/30)
        super().on_removal(**kwargs)

    def modify_strength(self,amount,**kwargs):
        oldstrength=self.strength
        self.strength+=amount
        if self.strength*oldstrength<=0:
            self.strength=oldstrength
            self.on_removal(**kwargs)
            self.target.enchantments.remove(self)
            return
        if self.strength>0:
            self.target.resistance[self.res_modified]*=(1+self.strength/30)/(1+oldstrength/30)
        elif self.strength<0:
            self.target.resistance[self.res_modified]*=(1-oldstrength/30)/(1-self.strength/30)

#Creature enchantments

class Psychic_Detection(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='psychic detection'
        self.strength=strength
        self.category="psychic"
        self.classification=["psychic","sensory"]
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def sense_modification(self):
        self.target.focus[0]=max(0,self.target.focus[0])
        if self.target.location==[None,None]: return
        testable_creatures=[Shell.shell.player]
        testable_creatures.extend(self.target.floor.creaturelist)
        radius=(self.strength*self.target.stats['per']*self.target.focus[0]/self.target.focus[1])**0.5
        for i in testable_creatures:
            if 'mindless' in i.classification or i.alive==False or i==self.target or i.location==[None,None]:
                continue
            distance=((self.target.location[0]-i.location[0])*(self.target.location[0]-i.location[0])+
            (self.target.location[1]-i.location[1])*(self.target.location[1]-i.location[1]))**0.5
            if radius*radius>distance:
                self.target.psychic_detected_creatures.append(i)
        if self.target==Shell.shell.player:
            for i in self.target.psychic_detected_creatures:
                i.floor.cells[i.location[0]][i.location[1]].update_graphics(show_items=False,show_dungeon=False)
        super().sense_modification()

    def sense_specific_creature(self,creature):
        if not isinstance(creature,BaseClasses.Creature):
            return False
        if 'mindless' in creature.classification or creature.alive==False or creature==self.target or creature.location==[None,None]:
            return False
        distance=((self.target.location[0]-creature.location[0])*(self.target.location[0]-creature.location[0])+
            (self.target.location[1]-creature.location[1])*(self.target.location[1]-creature.location[1]))**0.5
        radius=(self.strength*self.target.stats['per']*self.target.focus[0]/self.target.focus[1])**0.5
        if radius*radius>distance:
            return True

class Magical_Sense(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,vision=True,hearing=True,smell=True,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='magical sense'
        self.strength=strength
        self.vision=vision
        self.hearing=hearing
        self.smell=smell
        self.classification.append("sensory")
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def sense_modification(self):
        if self.vision==True:
            self.target.vision=max(self.target.vision,self.strength)
            self.target.can_see=True
        if self.hearing==True:
            self.target.hearing=max(self.target.hearing,self.strength)
            self.target.can_hear=True
        if self.smell==True:
            self.target.smell_sense=max(self.target.smell_sense,self.strength)
            self.target.can_smell=True

class Levitation(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='levitation'
        self.strength=strength
        self.identified=True
        self.detected=True


    def sense_modification(self):
        self.target.balance+=self.strength
        self.target.movement['float']+=self.strength

class Stealth(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='stealth'
        self.strength=strength
        self.detection_bonuses={}
        self.identified=True
        self.detected=True

    def on_turn(self):
        for i in self.detection_bonuses:
            if self.detection_bonuses[i]>=1:
                self.detection_bonuses[i]-=1
        super().on_turn()

    def get_bonus(self,detector):
        if detector not in self.detection_bonuses:
            self.detection_bonuses[detector]=0
        return self.detection_bonuses[detector]

    def on_strike(self,attack):
        super().on_strike(attack)
        if attack.basetarget.owner==None: return
        if attack.basetarget.owner not in self.detection_bonuses:
            self.detection_bonuses[attack.basetarget.owner]=0
        self.detection_bonuses[attack.basetarget.owner]+=2*int((attack.basetarget.owner.stats['per']**0.5)*(1+self.target.tension/100))

    def on_struck(self,attack):
        super().on_struck(attack)
        if attack.attacker not in self.detection_bonuses:
            self.detection_bonuses[attack.attacker]=0
        self.detection_bonuses[attack.attacker]+=int((attack.attacker.stats['per']**0.5)*(1+self.target.tension/100))

class Silenced(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='silenced'
        self.strength=strength
        self.attempt_identification()

    def magic_modification(self,magic,**kwargs):
        super().magic_modification(magic,**kwargs)
        magic.abort=True
        if self.target==Shell.shell.player:
            Shell.shell.log.addtext("Your magical abilities are sealed!")
            self.attempt_identification(15)

class Spell_Failure(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='magic disruption'
        self.strength=strength
        self.attempt_identification()

    def magic_modification(self,magic,**kwargs):
        super().magic_modification(magic,**kwargs)
        if self.strength>random.random()*self.target.stats['wil'] or magic.power<self.strength:
            magic.abort=True
            if self.target==Shell.shell.player:
                Shell.messages.append("[b][size=13][color=7B888C]Something disrupts your spell![/b][/size][/color]")
                self.attempt_identification(10)
                Shell.shell.turn+=1
            elif self.target in Shell.shell.detected_creatures:
                Shell.messages.append("[b][size=13][color=AD801F]{} attempts to cast a spell,[/color][color=7B888C] but something disrupts the magic![/b][/size][/color]".format(self.target.name))
                self.attempt_identification(5)
        magic.power-=self.strength

class Frozen_Creature(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='frozen'
        self.classification=['incapacitate','magic','ice','movement impairing','attack impairing']
        self.strength=strength
        self.identified=True
        self.detected=True
        if self.target==Shell.shell.player:
            self.removalmessage="[b][color=1FAD39]You are no longer frozen.[/b][/color]"
        else:
            self.removalmessage="[color=1F4CAD]{} is no longer frozen[/color]".format(self.target.name)

    def on_turn(self):
        res=self.target.resistance['ice']*self.target.resistance['magic']*self.target.resistance['elemental']
        super().on_turn()
        if self.strength<=0:
            self.on_removal()
            self.target.enchantments.remove(self)
        if res*self.target.stats['luc']*random.random()>self.strength*random.random():
            self.modify_strength(-random.random()*random.random()*self.target.stats['luc']*res)
            self.strength=int(self.strength)

    def attempt_attack(self):
        if self.target==Shell.shell.player:
            Shell.messages.append("You are frozen solid!")
        return False

    def attempt_movement(self):
        if self.target==Shell.shell.player:
            Shell.messages.append("You are frozen solid!")
        return False

    def attempt_ability_use(self,ability,**kwargs):
        if self.target==Shell.shell.player:
            Shell.messages.append("You are frozen solid!")
        ability.abort=True
        Shell.shell.turn+=1
        return False

class Impaired_Mobility(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='impaired mobility'
        self.classification=['incapacitate','physical','movement impairing']
        self.strength=strength
        self.identified=True
        self.detected=True



    def on_turn(self):
        super().on_turn()

    def attempt_movement(self):
        abil=self.target.balance*(self.target.stats['luc']*self.target.stats['str']*self.target.stats['wil']*self.target.stats['tec'])**0.25
        if abil/(abil+30)>random.random():
            return True
        if self.target==Shell.shell.player:
            Shell.messages.append("You stumble!")
        return False

    def attempt_ability_use(self,ability,**kwargs):
        if not 'movement' in ability.classification:
            return True
        abil=self.target.balance*(self.target.stats['luc']*self.target.stats['str']*self.target.stats['wil']*self.target.stats['tec'])**0.25
        if abil/(abil+30)>random.random:
            return True
        if self.target==Shell.shell.player:
            Shell.messages.append("You stumble!")
            Shell.shell.turn+=1
        return False

class Dazed(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='dazed'
        self.classification=['daze','psychic','ai_modifying','movement impairing','attack impairing']
        self.category='psychic'
        self.strength=strength
        self.old_ai=self.target.ai
        self.target.ai=ai.dazed_ai
        self.active=True
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True
        if self.target==Shell.shell.player:
            self.removalmessage="[b][color=1FAD39]You are no longer dazed.[/b][/color]"

    def on_turn(self):
        self.active=True
        super().on_turn()

    def on_removal(self,**kwargs):
        self.target.ai=self.old_ai
        super().on_removal(**kwargs)

    def attempt_movement(self):
        super().attempt_movement()
        if self.target!=Shell.shell.player:
            return True
        elif self.target.stats['luc']*random.random()>self.strength:
            return True
        elif self.active==True:
            self.active=False
            ai.dazed_ai(self.target)
            return False

    def attempt_attack(self):
        super().attempt_attack()
        if self.target!=Shell.shell.player:
            return True
        elif self.target.stats['luc']*random.random()>self.strength:
            return True
        elif self.active==True:
            self.active=False
            ai.dazed_ai(self.target)
            return False

    def attempt_ability_use(self,ability,**kwargs):
        super().attempt_ability_use(ability,**kwargs)
        if random.random()*2*self.target.stats['luc']<3*self.strength:
            ability.abort=True
            if self.target==Shell.shell.player:
                Shell.messages.append("[color=7B888C]You attempt to use an ability, but are unable to focus[/color]")
                Shell.shell.turn+=1
            elif self.target in Shell.shell.player.visible_creatures:
                Shell.messages.append("[color=7B888C]{} looks like it is trying to do something[/color]")

class Confused(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='confused'
        self.classification=['confused','psychic','attack impairing']
        self.category='psychic'
        self.strength=strength
        self.old_affinity=self.target.affinity.copy()
        if self.target==Shell.shell.player:
            self.removalmessage="[b][color=1FAD39]You are no longer confused.[/b][/color]"
        else:
            self.removalmessage="[color=1F4CAD]{} regains its wits[/color]".format(self.target.name)
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def on_turn(self):
        for i in self.target.affinity:
            if i not in self.old_affinity:
                self.old_affinity[i]=self.target.affinity[i]
            self.target.affinity[i]=random.randint(-10,11)
        self.target.target=None
        super().on_turn()


    def on_removal(self,**kwargs):
        self.target.affinity=self.old_affinity.copy()
        super().on_removal(**kwargs)


    def attempt_attack(self):
        super().attempt_attack()
        if self.target!=Shell.shell.player:
            return True
        else:
            if self.target.stats['luc']<random.random()*self.strength**2:
                creature=random.choice(["that harmless old lady!","that kindhearted child!","your own mother!","yourself!",
                                        "that poor beggar!","such a delicious sandwich!","your best friend!","the fabric of reality!",
                                        "such a brilliant idea!","yet another defenseless slime!","that... uhm... what were you doing again?",
                                        "the hopes of the future!","death itself!"])
                Shell.messages.append("[b][color=1F4CAD]You cannot bring yourself to attack {}[/color][/b[".format(creature))
                return False
            else: return True

    def attempt_ability_use(self,ability,**kwargs):
        super().attempt_ability_use(ability,**kwargs)

class Psychic_Shield(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,combine=False,**kwargs)
        self.classname='psychic shield'
        self.strength=strength
        self.focuscost=0
        self.attacks=[]
        self.active=True
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def on_turn(self):
        self.focuscost=0
        for i in self.attacks:
            self.focuscost+=int((10/self.strength)*i.energy**0.5)
        self.target.focus[0]-=self.focuscost+5
        self.attacks=[]
        super().on_turn()

    def evasion_modification(self,attack,**kwargs):
        if not self.active:
            return
        if random.random()<self.target.focus[0]/self.target.focus[1]:
            attack.abort=True
            if self.target==Shell.shell.player:
                Shell.messages.append(1)
                Shell.messages.append("[color=7B888C]You deflect the attack with your psychic shield![/color]")
                Shell.messages.append(-1)
            elif self.target in Shell.shell.player.visible_creatures:
                self.attempt_identification(10)
                Shell.messages.append(1)
                Shell.messages.append("[color=7B888C]The attack glances off of an invisible barrier![/color]")
                Shell.messages.append(-1)
            self.attacks.append(attack)
            return 'abort'
        elif random.random()*self.strength*self.strength*self.strength<random.random()*attack.energy:
            self.active=False
            self.turns=0
            if self.target==Shell.shell.player:
                Shell.messages.append(1)
                Shell.messages.append("[color=EB05B1]Your psychic shield shatters![/color]")
                Shell.messages.append(-1)
            elif self.target in Shell.shell.player.visible_creatures:
                Shell.messages.append(1)
                Shell.messages.append("[color=EB05B1]{}'s barrier collapses![/color]".format(self.target.name))
                Shell.messages.append(-1)
            self.target.focus[0]-=int(0.5*random.random()*random.random()*self.target.focus[0])+1
            pass

class Haste(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='haste'
        self.classification=['haste','physical','attack impairing','movement impairing']
        self.category='physical'
        self.strength=strength
        self.successive_turns=0
        if self.target==Shell.shell.player:
            self.removalmessage="[b][color=1FAD39]You slow down.[/b][/color]"
        else:
            self.removalmessage="[color=1F4CAD]{} slows down[/color]".format(self.target.name)
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def attempt_attack(self):
        super().attempt_attack()
        if random.random()>(self.strength/(3+self.strength))**(2+self.successive_turns):
            self.successive_turns=0
            return True
        else:
            self.successive_turns+=1
            return 'free'

    def attempt_movement(self):
        super().attempt_movement()
        if random.random()>(self.strength/(3+self.strength))**(2+self.successive_turns):
            self.successive_turns=0
            return True
        else:
            self.successive_turns+=1
            return 'free'

class Slow(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='slowed'
        self.classification=['slow','physical','attack impairing','movement impairing']
        self.category='physical'
        self.strength=strength
        self.successive_turns=0
        if self.target==Shell.shell.player:
            self.removalmessage="[b][color=1FAD39]You speed up![/b][/color]"
        else:
            self.removalmessage="[color=1F4CAD]{} speeds up![/color]".format(self.target.name)
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True


    def attempt_attack(self):
        super().attempt_attack()
        if random.random()>(self.strength/(3+self.strength))**(2+self.successive_turns):
            self.successive_turns=0
            return True
        else:
            self.successive_turns+=1
            if self.target==Shell.shell.player:
                Shell.shell.turn+=1
                self.attempt_attack()
            else:
                return False

    def attempt_movement(self):
        super().attempt_movement()
        if random.random()>(self.strength/(3+self.strength))**(2+self.successive_turns):
            self.successive_turns=0
            return True
        else:
            self.successive_turns+=1
            if self.target==Shell.shell.player:
                Shell.shell.turn+=1
                self.attempt_movement()
            else:
                return False

class Sprinting(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='sprinting'
        self.classification=['sprinting','physical','attack impairing','movement impairing']
        self.category='physical'
        self.strength=strength
        self.successive_turns=0
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def attempt_attack(self):
        super().attempt_attack()
        self.turns=0
        self.on_turn()

    def attempt_movement(self):
        super().attempt_movement()
        self.target.stamina[0]-=int((60+self.successive_turns*15)/self.strength)
        if self.target.stamina[0]<=0:
            self.target.stamina[0]=0
            self.turns=0
            self.on_turn()
            return True
        self.successive_turns+=1
        if self.target==Shell.shell.player:
            Shell.shell.playerstamina=self.target.stamina
        return 'free'

class Defenseless(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='defenseless'
        self.classification=['incapacitate']
        self.strength=strength
        self.identified=True
        self.detected=True

class Tormented(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature) or target.feels_pain==False:
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='tormented'
        self.classification=['tormented','magic','pain']
        self.category='magic'
        self.strength=strength
        self.old_affinity=self.target.affinity.copy()
        if self.target==Shell.shell.player:
            self.removalmessage="[b][color=1FAD39]The pain fades away.[/b][/color]"
        else:
            self.removalmessage="[color=1F4CAD]{} looks better.[/color]".format(self.target.name)
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def on_turn(self):
        self.target.pain+=2*int(self.strength/(self.target.resistance['pain']*self.target.resistance['magic']*self.target.resistance['dark']))
        if self.target==Shell.shell.player:
            Shell.messages.append("[color=1F4CAD]Your body is wracked with intense pain![/color]")
        elif self.target in Shell.shell.player.visible_creatures:
            Shell.messages.append("[color=1F4CAD]{} is in pain![/color]")
        super().on_turn()

class Blind(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='blind'
        self.strength=strength
        self.classification=["blind","sensory"]
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def sense_modification(self):
        self.target.vision_radius=0
        self.target.can_see=False
        super().sense_modification()

class Berserk(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='berserk'
        self.classification=['berserk','movement impairing','attack impairing']
        self.category='physical'
        self.strength=strength
        self.staminacost=50+self.target.stamina[1]-self.target.stamina[0]
        self.focuscost=10+self.target.focus[1]-self.target.focus[0]
        Creature_Stat_Modification(self.target,turns=1,strength=int(self.strength/2))
        for i in ('psychic','fear','pain','disable'):
            self.target.resistance[i]*=10000
        if self.target==Shell.shell.player:
            self.removalmessage="[b][color=1FAD39]You calm down.[/b][/color]"
        else:
            self.removalmessage="[color=1F4CAD]{} calms down[/color]".format(self.target.name)
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def on_turn(self):
        self.staminacost+=self.target.stamina[1]-self.target.stamina[0]
        self.focuscost+=self.target.focus[1]-self.target.focus[0]
        self.target.stamina[0]=self.target.stamina[1]
        self.target.focus[0]=self.target.focus[1]
        self.target.pain=0
        Creature_Stat_Modification(self.target,turns=1,strength=int(self.strength/2))
        self.strength-=1
        if self.strength<=0:
            self.turns=0
        super().on_turn()

    def on_removal(self,**kwargs):
        self.target.stamina[0]=max(self.target.stamina[0]-self.staminacost,0)
        self.target.focus[0]=max(self.target.focus[0]-self.focuscost,0)
        for i in ('psychic','fear','pain','disable'):
            self.target.resistance[i]=self.target.resistance[i]/10000
        super().on_removal(**kwargs)

    def attempt_attack(self):
        super().attempt_attack()
        return True

    def evasion_modification(self,attack,**kwargs):
        self.target.surprise=0
        self.target.exploit=0
        super().evasion_modification(attack,**kwargs)

    def attack_modification(self,attack,**kwargs):
        super().attack_modification(attack,**kwargs)
        self.strength+=2
        attack.damagefactor*=1+self.strength/10
        attack.time*=15/(15+self.strength)
        attack.energy*=1+self.strength/10

    def physical_ability_modification(self,ability,**kwargs):
        super().physical_ability_modification(ability,**kwargs)
        self.strength+=1

    def magic_modification(self,magic,**kwargs):
        super().magic_modification(magic,**kwargs)
        magic.abort=True
        if self.target==Shell.shell.player:
            Shell.shell.log.addtext("You cannot cast spells while berserk!")

    def technique_modification(self,technique,**kwargs):
        super().technique_modification(technique,**kwargs)
        technique.abort=True
        if self.target==Shell.shell.player:
            Shell.shell.log.addtext("You cannot use that while berserk!")

    def divine_modification(self,ability,**kwargs):
        super().divine_modification(ability,**kwargs)
        ability.abort=True
        if self.target==Shell.shell.player:
            Shell.shell.log.addtext("You cannot pray while berserk!")

    def psychic_modification(self,ability,**kwargs):
        super().psychic_modification(ability,**kwargs)
        ability.abort=True
        if self.target==Shell.shell.player:
            Shell.shell.log.addtext("You cannot focus your psychic abilities while berserk!")

class Invisible(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='invisible'
        self.strength=strength
        self.detection={}
        self.location=[self.target.location[0],self.target.location[1]]
        self.identified=True
        self.detected=True

    def on_turn(self):
        if self.location!=self.target.location:
            self.location=[self.target.location[0],self.target.location[1]]
            for i in self.detection:
                if self.detection[i]>0:
                    self.detection[i]-=1
        super().on_turn()

    def detect(self,detector):
        if detector in self.detection and self.detection[detector]>0:
            return True
        else:
            return False

    def on_strike(self,attack):
        super().on_strike(attack)
        if attack.basetarget.owner==None: return
        if attack.basetarget.owner not in self.detection:
            self.detection[attack.basetarget.owner]=0
        if ((attack.basetarget.owner.stats['per']*attack.basetarget.owner.stats['luc'])**0.5)*random.random()>10:
            self.detection[attack.basetarget.owner]+=random.randint(1,3)

    def on_struck(self,attack):
        super().on_struck(attack)
        if attack.attacker not in self.detection:
            self.detection[attack.attacker]=0
        if ((attack.basetarget.owner.stats['per']*attack.basetarget.owner.stats['luc'])**0.5)*random.random()>10:
            self.detection[attack.basetarget.owner]+=random.randint(1,3)



class Vision_Modification(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=1,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='vision modification'
        self.strength=strength
        self.display=False
        self.classification=["vision modification","sensory"]
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def sense_modification(self):
        self.target.vision_radius+=self.strength
        super().sense_modification()

class Creature_Resistance_Modification(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,res='random',**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,combine=False,**kwargs)
        self.classname='creature resistance modification'
        self.display=False
        if res!='random':
            self.res_modified=res
        else:
            self.res_modified=random.choice(['teleport','fire','ice','physical','acid','lightning','poison','pain',
                                             'psychic','divine','magic','dark','disable','rot','death','arcane',
                                             'elemental','transmutation'])
        self.strength=strength
        if self.strength>=0:
            self.target.resistance[self.res_modified]*=(1+self.strength/30)
        elif self.strength<=0:
            self.target.resistance[self.res_modified]*=1/(1-self.strength/30)

    def on_removal(self,**kwargs):
        if self.strength>0:
            self.target.resistance[self.res_modified]*=1/(1+self.strength/30)
        elif self.strength<0:
            self.target.resistance[self.res_modified]*=(1-self.strength/30)
        super().on_removal(**kwargs)

    def modify_strength(self,amount,**kwargs):
        oldstrength=self.strength
        self.strength+=amount
        if self.strength*oldstrength<=0:
            self.strength=oldstrength
            self.on_removal(**kwargs)
            self.target.enchantments.remove(self)
            return
        if self.strength>0:
            self.target.resistance[self.res_modified]*=(1+self.strength/30)/(1+oldstrength/30)
        elif self.strength<0:
            self.target.resistance[self.res_modified]*=(1-oldstrength/30)/(1-self.strength/30)

class Creature_Stat_Modification(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,stat='s',**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,combine=False,**kwargs)
        self.classname='creature stat modification'
        self.display=False
        self.stat_modified=stat
        self.strength=strength
        self.target.statmodifiers[stat]+=strength
        self.oldmodifier=strength

    def on_turn(self):
        if self.strength!=self.oldmodifier:
            self.target.statmodifiers[self.stat_modified]-=self.oldmodifier
            self.oldmodifier=self.strength
            self.target.statmodifiers[self.stat_modified]+=self.strength
        super().on_turn()

    def on_removal(self,**kwargs):
        self.target.statmodifiers[self.stat_modified]-=self.oldmodifier
        super().on_removal(**kwargs)

class Held_In_Grasp(BaseClasses.Enchantment):
    def __init__(self,target,turns="permanent",strength=6,holding_limb=None,held_limb=None,mobile_grabber=False,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        try:
            self.held_limb=held_limb
            self.holding_limb=holding_limb
            self.normal_balance=0
            self.mobile_grabber=mobile_grabber
            self.grabber_location=holding_limb.owner.location
        except:
            return
        super().__init__(target,turns=turns,strength=strength,combine=False,**kwargs)
        self.classname='held in grasp'
        self.category='physical'
        self.classification=['physical','grasp','root','movement impairing']
        self.strength=strength
        self.identified=True
        self.detected=True

    def on_turn(self):
        if self.held_limb not in self.target.limbs or self.holding_limb==None or self.target.alive==False or self.holding_limb.owner.alive==False:
            self.on_removal()
            self.target.enchantments.remove(self)
            return
        if self.mobile_grabber==False:
            if self.grabber_location!=self.holding_limb.owner.location:
                if self.holding_limb.owner==Shell.shell.player:
                    Shell.messages.append("[b][color=1F4CAD]You release your grip on {}'s {}[/color][/b]".format(self.target.name,self.held_limb.name))
                elif self.target==Shell.shell.player:
                    Shell.messages.append("[b][color=1F4CAD]{} releases its grip on your {}[/color][/b]".format(
                        self.holding_limb.owner.name,self.held_limb.name))
                elif self.target in Shell.shell.player.visible_creatures:
                    Shell.messages.append("[color=1F4CAD]{} releases its grip on {}'s {}[/color]".format(
                        self.holding_limb.owner.name,self.target.name,self.held_limb.name))
                self.on_removal()
                self.target.enchantments.remove(self)
                return
        self.grasping=Grasping(self.holding_limb)
        self.grasping.held=self.held_limb
        self.held=Held(self.held_limb)
        self.held.grasping=self.grasping

    def sense_modification(self):
        self.normal_balance=self.target.balance
        self.target.balance=0

    def attempt_movement(self):
        super().attempt_movement()
        if self.held_limb not in self.target.limbs or self.holding_limb==None:
            self.on_removal()
            self.target.enchantments.remove(self)
            return True
        self.holding_limb.updateability(include_enchantments=False)
        gripsize=self.holding_limb.length
        if hasattr(self.holding_limb,'dexterity'):
            for i in self.holding_limb.limbs:
                gripsize+=i.length
        chance=self.target.stats['str']*self.held_limb.radius/(
            self.holding_limb.stats['str']*self.holding_limb.ability*gripsize*self.held_limb.length+0.01)
        self.holding_limb.ability=0
        if chance>random.random():
            if self.target==Shell.shell.player:
                Shell.messages.append("[b][color=1FAD39]You wrest your {} free from {}'s {}[/b][/color]".format(
                    self.held_limb.name,self.holding_limb.owner.name,self.holding_limb.name))
            elif self.holding_limb.owner==Shell.shell.player:
                Shell.messages.append("[b][color=C21D25]{} struggles free of your {}'s grasp on its {}[/b][/color]".format(
                    self.target.name,self.holding_limb.name,self.held_limb.name))
            elif self.target in Shell.shell.player.visible_creatures:
                Shell.messages.append("[color=1F4CAD]{} breaks out of {}'s grasp![/color]".format(self.target.name,self.holding_limb.owner.name))
            self.on_removal()
            self.target.enchantments.remove(self)
            self.target.stamina[0]-=int(random.random()*random.random()*self.holding_limb.stats['str']+2)
            return True
        else:
            if self.target==Shell.shell.player:
                Shell.messages.append("[b][color=C21D25]You struggle, but are unable to break your {} free![/b][/color]".format(self.held_limb.name))
            elif self.target in Shell.shell.player.visible_creatures:
                Shell.messages.append("[color=1F4CAD]{} struggles to break free of the grasp on its {}[/color]".format(self.target.name,self.held_limb.name))
            self.target.stamina[0]-=int(random.random()*self.holding_limb.stats['str']+5)
            return False

    def on_removal(self,**kwargs):
        self.target.balance=self.normal_balance
        marked_for_removal=[]
        for i in self.held_limb.enchantments:
            if isinstance(i,Held):
                i.on_removal()
                marked_for_removal.append(i)
        for i in marked_for_removal:
            self.held_limb.enchantments.remove(i)
        marked_for_removal=[]
        for i in self.holding_limb.enchantments:
            if isinstance(i,Grasping):
                i.on_removal()
                marked_for_removal.append(i)
        for i in marked_for_removal:
            self.holding_limb.enchantments.remove(i)

class Familiar_Spirit(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=1,owner=None,**kwargs):
        import Abilities
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='familiar spirit'
        self.strength=strength
        self.category="magic"
        self.classification=["magic","summoning"]
        self.owner=owner
        self.companion_enchantment=Familiar_Guidance(self.owner,familiar=self.target)
        self.companion_enchantment.compantion_enchantment=self
        self.powergifts=[Abilities.Pain,Abilities.Psychic_Grab,Abilities.Fireball,Abilities.Controlled_Teleport]


    def on_turn(self):
        super().on_turn()
        if random.random()*random.random()*self.target.magic_contamination['total']>5+self.strength:
            self.grant_power()
            for i in range(0,int(5+self.strength)):
                magic_reduced=False
                tries=0
                while magic_reduced==False and tries<25:
                    key=random.choice(list(self.target.magic_contamination))
                    if self.target.magic_contamination[key]<=0 or key=='total':
                        pass
                    else:
                        self.target.magic_contamination[key]-=1
                        magic_reduced=True
                    tries+=1


    def add_graphical_instructions(self,cell,**kwargs):
        if self.owner==Shell.shell.player:
            cell.instructions.add(Color(1,0,0,0.9,group="creatures"))
            cell.instructions.add(Rectangle(size=[cell.size[0]*0.4,cell.size[1]*0.4],pos=[cell.pos[0]+cell.size[0]*0.6,
                                                                                  cell.pos[1]+cell.size[1]*0.6],
                                        source="./images/Heartoutline.png",group='creatures'))

    def grant_power(self):
        if random.random()>0.5:
            #About half the time, give an increases to stats
            self.target.stats['s']+=int(random.random()*random.random()*random.random()*self.target.stats['s'])
            self.target.stats['t']+=int(random.random()*random.random()*random.random()*self.target.stats['t'])
            self.target.stats['p']+=int(random.random()*random.random()*random.random()*self.target.stats['p'])
            self.target.stats['w']+=int(random.random()*random.random()*random.random()*self.target.stats['w'])
            self.target.stats['l']+=int(random.random()*random.random()*random.random()*self.target.stats['l'])
            if self.owner==Shell.shell.player:
                Shell.messages.append("[color=1F4CAD]{} has grown in power![/color]".format(self.target.name))
            elif self.target in Shell.shell.player.detected_creatures:
                Shell.messages.append("[color=1F4CAD]{} looks stronger![/color]".format(self.target.name))
        elif random.random()>0.5 and self.powergifts!=[]:
            #Sometimes, grant an ability
            ability=random.choice(self.powergifts)
            self.target.abilities.append(ability(self.target))
            self.powergifts.remove(ability)
            if self.owner==Shell.shell.player:
                Shell.messages.append("[color=1F4CAD]{} has gained mastery over new powers![/color]".format(self.target.name))
            elif self.target in Shell.shell.player.detected_creatures:
                Shell.messages.append("[color=1F4CAD]{} looks stronger![/color]".format(self.target.name))
        elif random.random()>0.5:
            #otherwise, cause mutations
            pass

class Familiar_Guidance(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=1,familiar=None,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='familiar guidance'
        self.strength=strength
        self.category="magic"
        self.classification=["magic","summoning"]
        self.familiar=familiar
        if self.target==Shell.shell.player:
            self.identified=True
            self.detected=True

    def on_turn(self):
        if self.familiar.alive==False:
            self.target.enchantments.remove(self)
        super().on_turn()
        if self.compantion_enchantment.strength*self.target.magic_contamination['total']>random.randint(0,200):
            key=random.choice(list(self.target.magic_contamination.keys()))
            if key!="total" and self.target.magic_contamination[key]>0:
                self.target.magic_contamination[key]-=1
                self.familiar.magic_contamination[key]+=1
                #print(self.target.magic_contamination,self.familiar.magic_contamination)

    def magic_modification(self,magic,**kwargs):
        super().magic_modification(magic,**kwargs)
        magic.power+=self.familiar.magic_contamination['total']

    def sense_modification(self):
        super().sense_modification()
        self.familiar.check_visible_cells(send_to=self.target)

class GeneralIncapacitation(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,strength=strength,**kwargs)
        self.classname='incapacitated'
        self.classification=['incapacitate','movement impairing','attack impairing']
        self.strength=strength
        self.identified=False
        self.detected=False

    def on_turn(self):
        super().on_turn()

    def attempt_attack(self):
        return False

    def attempt_movement(self):
        return False

    def attempt_ability_use(self,ability,**kwargs):
        return False










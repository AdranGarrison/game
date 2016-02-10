__author__ = 'Alan'

import BaseClasses
import Fluids
import random
import Shell
import Materials as Mats


#Item enchantments

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


    def on_dispel(self):
        if self.has_edge:
            self.target.edge=self.base_edge
        if self.has_tip:
            self.target.tip=self.base_tip

class Unstable(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,**kwargs)
        self.strength=strength


    def on_turn(self):
        super().on_turn()
        if random.random()<1/self.strength**2:
            self.target.on_destruction()
            self.target.damage['disintegrate']=1
            self.target.functioncheck()
            if self.target.in_inventory==Shell.shell.player or self.target in Shell.shell.player.visible_items:
                Shell.shell.log.addtext('The {} returns to the void'.format(self.target.name))
                try: Shell.shell.player.inventory.remove(self.target)
                except: pass
            pass

class Bound(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,**kwargs)
        self.strength=strength
        self.target=target
        self.limb=None

    def on_equip(self):
        attach=self.target.equipped[0]
        self.limb=Shell.Limbs.Bound_Item_Limb(item=self.target,owner=attach.owner)
        if self.target.in_inventory!=None:
            self.target.in_inventory.inventory.remove(self.target)
            self.target.in_inventory=None
        if attach.owner==Shell.shell.player:
            Shell.shell.log.addtext('The {} fuses itself to your {}!'.format(self.target.name,attach.name))
        elif attach.owner in Shell.shell.player.visible_creatures:
            Shell.shell.log.addtext('The {} fuses itself to the {} of {}'.format(self.target.name,attach.name,attach.owner.name))


    def on_dispel(self):
        try:
            self.limb.owner.limbs.remove(self.limb)
            self.limb.attachpoint.limbs.remove(self.limb)
            if self.target not in self.limb.owner.inventory:
                self.limb.owner.inventory_add(self.target)
        except:
            pass

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
        super().__init__(target,turns=turns,**kwargs)
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


    def on_dispel(self):
        self.target.mode=self.old_mode
        self.target.material.mode=self.old_mode
        self.target.acid_reaction=self.old_acid_reaction
        self.target.material.acid_reaction=self.old_mat_acid_reaction
        self.target.heat_reaction=self.old_heat_reaction
        self.target.material.heat_reaction=self.old_mat_heat_reaction

class Shifting(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Item):
            return
        super().__init__(target,turns=turns,**kwargs)
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
        super().__init__(target,turns=turns,**kwargs)
        self.strength=strength


    def on_turn(self):
        player=Shell.shell.player
        super().on_turn()
        for i in self.target.equipped:
            if random.random()<(self.strength**0.5)/(i.stats['luc']*i.stats['luc']):
                creature=i.owner
                equipped_items=0
                for j in i.equipment:
                    if i.equipment[j]!=None:
                        equipped_items+=1
                if i.armor!=None and i.armor!=self.target:
                    armor=i.armor
                    creature.unequip(armor,log=False)
                    creature.inventory.remove(armor)
                    armor.in_inventory=None
                    creature.floor.place_item(armor,location=None)
                    if creature==player:
                        Shell.messages.append("Your {} vanishes!".format(armor.name))
                        self.attempt_identification(15)
                    elif creature in player.visible_creatures:
                        Shell.messages.append("{}'s {} vanishes!".format(creature.name,armor.name))
                        self.attempt_identification(15)
                elif random.random()>0.5 and equipped_items>1:
                    for j in i.equipment:
                        if i.equipment[j]!=self.target:
                            item=i.equipment[j]
                            creature.unequip(item)
                            creature.inventory.remove(item)
                            item.in_inventory=None
                            creature.floor.place_item(item)
                        if creature==player:
                            Shell.messages.append("Your {} vanishes!".format(item.name))
                            self.attempt_identification(15)
                        elif creature in player.visible_creatures:
                            Shell.messages.append("{}'s {} vanishes!".format(creature.name,item.name))
                            self.attempt_identification(15)
                else:
                    creature.floor.cells[creature.location[0]][creature.location[1]].contents.remove(creature)
                    creature.floor.place_creature(creature)
                    if creature==player:
                        Shell.messages.append("You feel disoriented.")
                        self.attempt_identification(10)
                    elif creature in player.visible_creatures:
                        Shell.messages.append("{} vanishes from sight!".format(creature.name))
                        self.attempt_identification(5)

    def on_strike(self,attack):
        super().on_strike(attack)
        luc=attack.attacker.stats['luc']
        d_luc=attack.basetarget.stats['luc']
        defender=attack.basetarget.owner
        effect_chance=self.strength*luc/(d_luc*d_luc)
        for i in attack.touchedobjects:
            if random.random()<effect_chance/(1+effect_chance):
                if hasattr(i,'equipped') and any(isinstance(j,Shell.Limb) for j in i.equipped):
                    defender.unequip(i,log=False)
                    defender.inventory.remove(i)
                    i.in_inventory=None
                    defender.floor.place_item(i)
                    if defender==Shell.shell.player:
                        Shell.messages.append("Your {} vanishes!".format(i.name))
                        self.attempt_identification(15)
                    elif defender in Shell.shell.player.visible_creatures:
                        Shell.messages.append("{}'s {} vanishes!".format(defender.name,i.name))
                        self.attempt_identification(10)
                elif i in attack.basetarget.layers:
                    defender.floor.cells[defender.location[0]][defender.location[1]].contents.remove(defender)
                    defender.floor.place_creature(defender)
                    if defender==Shell.shell.player:
                        Shell.messages.append("You feel disoriented")
                        self.attempt_identification(10)
                    elif defender in Shell.shell.player.visible_creatures:
                        Shell.messages.append("{} vanishes from sight!".format(defender.name))
                        self.attempt_identification(10)

    def on_struck(self,attack):
        super().on_struck(attack)
        if 'ranged' in attack.classification and 'weaponless' in attack.classification:
            print('None of that here!')
            return
        try: luc=self.target.stats['luc']
        except:
            try: luc=attack.basetarget.stats['luc']
            except: luc=self.strength
        try: d_luc=attack.weapon.stats['luc']
        except:
            try: d_luc=attack.armor.stats['luc']
            except: d_luc=attack.limb.stats['luc']
        effect_chance=2*self.strength*luc/(d_luc*d_luc)
        item=None
        if random.random()<effect_chance/(1+effect_chance):
            if attack.weapon!=None and not any(isinstance(i,Bound) for i in attack.weapon.enchantments) and 'weaponless' not in attack.classification:
                item=attack.weapon
            elif attack.limb.armor!=None and not any(isinstance(i,Bound) for i in attack.limb.armor.enchantments):
                item=attack.limb.armor
            if item!=None:
                attack.attacker.unequip(item,log=False)
                try: attack.attacker.inventory.remove(item)
                except ValueError: pass
                item.in_inventory=None
                attack.attacker.floor.place_item(item)
                if attack.attacker==Shell.shell.player:
                    Shell.messages.append("Your {} vanishes!".format(item.name))
                    self.attempt_identification(10)
                elif attack.attacker in Shell.shell.player.visible_creatures:
                    Shell.messages.append("{}'s {} vanishes!".format(attack.attacker.name,item.name))
                    self.attempt_identification(10)
                return
            attack.attacker.floor.cells[attack.attacker.location[0]][attack.attacker.location[1]].contents.remove(attack.attacker)
            attack.attacker.floor.place_creature(attack.attacker)
            if attack.attacker==Shell.shell.player:
                Shell.messages.append("You feel disoriented")
                self.attempt_identification(10)
            elif attack.attacker in Shell.shell.player.visible_creatures:
                Shell.messages.append("{} vanishes from sight!".format(attack.attacker.name))
                self.attempt_identification(10)





    def on_destruction(self):
        pass



#Creature enchantments

class Psychic_Detection(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,**kwargs)
        self.strength=strength

class Magical_Sense(BaseClasses.Enchantment):
    def __init__(self,target,turns='permanent',strength=6,vision=True,hearing=True,smell=True,**kwargs):
        if not isinstance(target,BaseClasses.Creature):
            return
        super().__init__(target,turns=turns,**kwargs)
        self.strength=strength
        self.vision=vision
        self.hearing=hearing
        self.smell=smell

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

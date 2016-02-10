__author__ = 'Alan'

import Shell
import random
import Items
import Limbs
import Materials
import Enchantments
import Attacks


def Summon_Demonic_Weapon(summoner):
    #determine power
    will=summoner.stats['wil']
    magic=summoner.magic_contamination['total']
    luck=summoner.stats['luc']
    power=(will+magic)**0.5
    #determine type of weapon to create
    weighted_weapons=[(Items.LongSword,10),(Items.Gladius,5),(Items.Knife,7),(Items.Saber,4),(Items.Claymore,4),(Items.Mace,8),
                 (Items.WarHammer,3),(Items.Spear,5),(Items.Axe,6),(Items.QuarterStaff,3)]
    #most of the time
    if random.random()>0.03:
        #choose a weapon and continue with the process
        weapontype=Items.weighted_choice(weighted_weapons)
        weapon=weapontype(material=Materials.Demonic_Material,id=id,power=power)
        weapon.randomize()
        weapon.generate_descriptions(per=Shell.shell.player.stats['per'])
        summoner.inventory_add(weapon)
        if summoner.player:
            name,s='You',''
            weapon.seen_by_player=True
            weapon.touched_by_player=True
            for i in summoner.limbs:
                if 'grasp' in i.primaryequip and i.equipment['grasp']==None:
                    i.equip(weapon)
                    break
             #if you are lucky, the object will be fully identified
            if luck/(luck+30)>random.random():
                weapon.full_identify()
        else:
            name,s=summoner.name,'s'
            summoner.value_item(weapon)
            equipped_weapons=[]
            for i in summoner.limbs:
                if 'grasp' in i.primaryequip:
                    if i.equipment['grasp']!=None:
                        equipped_weapons.append(i.equipment['grasp'])
                    elif weapon.equipped==[]:
                        i.equip(weapon)
                        equipped_weapons.append(weapon)
            #If the summoner hates it, they will unequip it in favor of empty hands
            if summoner.item_values[weapon]<0 and weapon.equipped!=[]:
                summoner.action_queue.append(['unequip',weapon,weapon.equipped[0]])
            #If the summoner has too many weapons equipped, they will unequip the least desirable weapon
            elif len(equipped_weapons)>summoner.iprefs['desired weapons']:
                least_desired_weapon=equipped_weapons[0]
                for i in equipped_weapons:
                    if summoner.item_values[i]<summoner.item_values[least_desired_weapon]:
                        least_desired_weapon=i
                for i in least_desired_weapon.equipped:
                    summoner.action_queue.append(['unequip',least_desired_weapon,i])
            #If the summoned item went to the inventory, but the summoner WANTS to equip it
            elif weapon not in equipped_weapons:
                least_desired_weapon=weapon
                for i in equipped_weapons:
                    if summoner.item_values[i]<summoner.item_values[least_desired_weapon]:
                        least_desired_weapon=i
                if least_desired_weapon!=weapon:
                    for i in least_desired_weapon.equipped:
                        summoner.action_queue.append(['unequip',least_desired_weapon,i])
                        limb=i
                    summoner.action_queue.append(['equip',weapon,limb])




        if summoner in Shell.shell.player.visible_creatures:
            Shell.shell.log.addtext(message='{} summon{} a {}'.format(name,s,weapon.name))

        Enchantments.Unstable(weapon,strength=power+luck**0.5)
        Enchantments.Bound(weapon)
        if weapon.equipped!=[]:
            weapon.on_equip()


    #but sometimes you summon a limb instead
    elif random.random()>0.1:
        pass
    #and if you are unlucky, you'll summon a hostile horror
    else:
        pass
    summoner.magic_contamination['summoning']+=2

class Conjur_Weapon():
    def __init__(self,caster,**kwargs):
        self.caster=caster

    def select_target(self):
        self.do()

    def do(self,**kwargs):
        Summon_Demonic_Weapon(self.caster)

    def decide(self):
        value=0
        weapons=0
        limbs=0
        if self.caster.target==None or self.caster.iprefs['desired weapons']==0:
            return (0,self)
        for i in self.caster.equipped_items:
            if hasattr(i,'sortingtype') and i.sortingtype=='weapon':
                weapons+=1
        for i in self.caster.limbs:
            if 'grasp' in i.primaryequip and i.grasp==True and i.equipment['grasp']==None and i.ability>0:
                limbs+=1
        if weapons<self.caster.iprefs['desired weapons'] and limbs>0:
            value+=1
        value=(value+1)/(0.3*self.caster.magic_contamination['total']+1)
        return (value,self)

    def enemy_activation(self):
        self.do()




class Psychokinesis():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.weapon=None
        self.focuscost=20
        self.classification=['weaponless','physical','ranged']

    def select_target(self):
        if self.caster==Shell.shell.player:
            Shell.shell.reticule=Shell.Reticule(purpose=self)

    def do(self,location=None,**kwargs):
        try:
            distance=Shell.shell.dungeonmanager.current_screen.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)
            self.focuscost=5+distance
        except AttributeError:
            self.focuscost=10
        if self.caster.focus[0]<self.focuscost:
            if self.caster==Shell.shell.player:
                Shell.shell.log.addtext("You don't have the focus to do that")
            return
        self.caster.combataction=True
        self.touchedobjects=[]
        self.penetrate=False
        self.contact=True
        self.damage_dealt=0
        self.type='crush'
        self.oldtype='crush'
        self.results=[]
        self.damagedobjects=[]
        strikeables=[]
        for i in location.contents:
            if isinstance(i,Shell.Creature) and i.alive==True:
                target=Attacks.targetchoice(i)
                self.calculate_force(target)
                if self.caster==Shell.shell.player:
                    Shell.messages.append('You strike {} in the {} with a burst of telekenetic force'.format(i.name,target.name))
                elif i==Shell.shell.player:
                    Shell.messages.append('Something strikes you in the {}!'.format(target.name))
                target.damageresolve(self,self.caster)
                try:
                    Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                    Shell.shell.reticule=None
                    Shell.shell.keyboard_mode='play'
                except: pass
                self.caster.focus[0]-=self.focuscost
                if self.caster==Shell.shell.player: Shell.shell.turn+=1
                return
            elif isinstance(i,Shell.Item) or isinstance(i,Shell.Limb):
                strikeables.append(i)
        if strikeables!=[]:
            if self.caster==Shell.shell.player:
                Shell.messages.append('You unleash a wave of force!')
            for i in strikeables:
                self.calculate_force(i)
                i.damageresolve(self,self.caster)
        elif self.caster==Shell.shell.player:
            Shell.messages.append('You unleash a wave of force!')
        self.caster.focus[0]-=self.focuscost
        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

    def calculate_force(self,target):
        force=2*self.caster.stats['per']*self.caster.focus[0]
        self.weapon=None
        self.limb=None
        self.force=force
        self.area=0.1*(self.caster.focus[1]-self.caster.focus[0]+2)/self.caster.focus[1]
        self.pressure=force/self.area
        self.energy=self.caster.stats['per']*self.caster.stats['per']
        self.absolute_depth_limit=10
        self.target=target
        self.basetarget=target

    def energy_recalc(self):
        if self.energy<=0:
            self.force=0
            self.pressure=0
        else:
            self.force*=0.9*self.energy/(self.caster.stats['per']*self.caster.stats['per'])

    def decide(self):
        value=0
        if self.caster.target==None:
            return (0,self)
        targetcell=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]]
        castercell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        distance=targetcell.distance_to(castercell)
        if distance<5:
            value+=0.7*distance/5
        elif distance>=5:
            value=0.7*5/distance
        value*=self.caster.focus[0]/self.caster.focus[1]
        if 'psychic' in self.caster.classification: value*=1/0.7
        return (value,self)

    def enemy_activation(self):
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])
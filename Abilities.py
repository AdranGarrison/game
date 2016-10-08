__author__ = 'Alan'

import Shell
import random
import Items
import Limbs
import Materials
import Enchantments
import Attacks
import MapTiles
import BaseClasses
import Creatures
from kivy.clock import Clock
import functools
import NameGen


#generic abilities

class Look():
    def __init__(self,caster,**kwargs):
        self.classification=['generic']
        self.attacker=caster
        self.caster=Shell.shell.player

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self)
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        target=None
        for i in location.creatures:
            target=i
        if target!=None and target in Shell.shell.player.detected_creatures:
            Shell.shell.status_screen=Shell.StatusScreen(target)
            Shell.shell.status_screen.creature_status()
            Shell.shell.add_widget(Shell.shell.status_screen)
            Shell.shell.keyboard_mode='status screen'
        else:
            Shell.shell.keyboard_mode='play'
        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
        except: pass

#Magic abilities
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
        self.classification=['magic','summoning']
        self.contamination_cost={'summoning':2}
        self.name="Conjur Weapon"

    def select_target(self):
        self.do()

    def do(self,**kwargs):
        self.abort=False
        if self.test_usability()==False:
            return
        summoner=self.caster
        #determine power
        will=self.caster.stats['wil']
        magic=self.caster.magic_contamination['total']
        luck=summoner.stats['luc']
        self.power=(will**0.5+1.05**magic)**2+self.caster.magic_contamination['summoning']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.magic_modification(self)
        if self.abort:
            return
        #determine type of weapon to create
        weighted_weapons=[(Items.LongSword,10),(Items.Gladius,5),(Items.Knife,7),(Items.Saber,4),(Items.Claymore,4),(Items.Mace,8),
                     (Items.WarHammer,3),(Items.Spear,5),(Items.Axe,6),(Items.QuarterStaff,3)]
        #most of the time
        if random.random()>0.03:
            #choose a weapon and continue with the process
            weapontype=Items.weighted_choice(weighted_weapons)
            weapon=weapontype(material=Materials.Demonic_Material,id=id,power=self.power/5)
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
                Shell.messages.append('{} summon{} a {}'.format(name,s,weapon.name))

            Enchantments.Unstable(weapon,strength=self.power/5+luck**0.5)
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



        self.caster.on_ability_use(self)
        if self.caster==Shell.shell.player:
            Shell.shell.turn+=1

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
        value=(value)/(0.3*self.caster.magic_contamination['total']+1)
        return (value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do()

class Controlled_Teleport():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.classification=['magic','arcane','ranged']
        self.target_type='select'
        self.targets=[]
        self.contamination_cost={'arcane':5}
        self.name="Controlled Teleport"

    def select_target(self):
        if self.caster==Shell.shell.player:
            if self.target_type=='select':
                Shell.shell.log.addtext("What do you want to teleport?")
            elif self.target_type=='location':
                Shell.shell.log.addtext("Where do you want to teleport the target to?")
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self)
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        if self.test_usability()==False:
            return
        self.power=(self.caster.stats['wil']+1.05**self.caster.magic_contamination['total'])**2+self.caster.magic_contamination['arcane']
        for i in self.caster.enchantments:
            if self.target_type=="location":
                if not self.abort:
                    i.attempt_ability_use(self)
                if not self.abort:
                    i.magic_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        if self.target_type=='select' and self.caster==Shell.shell.player:
            self.startpos=location
            self.targets=location.creatures
            self.targets.extend(location.items)
            self.target_type='location'
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            self.select_target()
            return
        if location==None:
            location=random.choice(self.caster.floor.nonindexedcells)
        accuracy=self.power/4
        distance=location.distance_to(self.startpos)
        targetloc=location.location.copy()
        self.caster.on_ability_use(self)
        for i in self.targets:
            try:
                res=i.resistance['teleport']*i.resistance['magic']*i.resistance['arcane']
            except:
                res=1
            if random.random()*self.power<res*10:
                continue
            placed=False
            i.floor.cells[i.location[0]][i.location[1]].contents.remove(i)
            while placed==False:
                targetloc[0]=int(random.gauss(targetloc[0],distance/accuracy))
                targetloc[1]=int(random.gauss(targetloc[1],distance/accuracy))
                if targetloc[0] not in range(0,i.floor.dimensions[0]) or targetloc[1] not in range(0,i.floor.dimensions[1]):
                    continue
                i.location=[None,None]
                i.floor.place_creature(i,location=targetloc,retry='near')
                if i.location!=[None,None]:
                    placed=True
                    try: i.magic_contamination['arcane']+=1
                    except AttributeError: pass
        if self.targets!=[]:
            self.caster.magic_contamination['arcane']+=5
        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except:
            pass
        if self.caster==Shell.shell.player:
            Shell.shell.turn+=1

    def decide(self):
        #Use in a defensive way to teleport self away
        focusfactor=self.caster.focus[0]/self.caster.focus[1]
        staminafactor=self.caster.stamina[0]/self.caster.stamina[1]
        value=(focusfactor*focusfactor+staminafactor*staminafactor+self.caster.damage_level*self.caster.damage_level)**0.5
        value=(value+1)/(0.3*self.caster.magic_contamination['total']+1)
        self.target_type='location'
        self.enemytarget=self.caster
        #Use in mixed way to teleport hostile target away?
        if self.caster.target!=None and self.caster.hostilitycheck(self.caster.target):
            self.enemytarget=self.caster.target
        return (value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        location=self.enemytarget.floor.cells[self.enemytarget.location[0]][self.enemytarget.location[1]]
        self.startpos=location
        self.targets=location.creatures
        self.targets.extend(location.items)
        self.do()

class Pain():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.classification=['magic','dark','ranged']
        self.contamination_cost={'dark':1}
        self.name="Pain"

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self)
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        rootpower=self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total']
        self.power=rootpower*rootpower+self.caster.magic_contamination['dark']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.magic_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        startcell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        distance=location.distance_to(startcell)
        if distance>2*self.power**0.5:
            Shell.shell.log.addtext("That is too far away")
            return
        if location.creatures==[] or not any(i in Shell.shell.player.detected_creatures for i in location.creatures):
            Shell.shell.log.addtext("You sense no creature there")
            return
        if self.caster==Shell.shell.player:
            message="[b][size=13][color=1FAD39]You channel torment from the void. "
        elif self.caster in Shell.shell.player.visible_creatures:
            if Shell.shell.player in location.creatures:
                message="[b][size=13][color=C21D25]{} calls upon the power of the void. ".format(self.caster.name)
            else:
                message="[b][color=AD801F]{} calls upon the power of the void. ".format(self.caster.name)
        else: message=''
        for i in location.creatures:
            i.magic_contamination['dark']+=0.5
            res=i.resistance['dark']*i.resistance['magic']
            if i.feels_pain:
                i.pain+=abs(random.gauss(3*self.power*self.caster.stats['wil']/(i.stats['wil']*i.stats['luc'])**0.5,self.caster.magic_contamination['total']))/res
                if i==Shell.shell.player:
                    Shell.messages.append("".join([message,"Pain shoots through your body![/b][/size][/color]"]))
                elif i in Shell.shell.player.visible_creatures:
                    Shell.messages.append("".join([message,"{} convulses with pain![/b][/size][/color]".format(i.name.capitalize())]))
        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        self.caster.magic_contamination['dark']+=1
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

    def decide(self):
        value=0
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures or self.caster.target.feels_pain==False:
            return (0,self)
        targetcell=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]]
        castercell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        distance=targetcell.distance_to(castercell)
        rootpower=self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total']
        power=rootpower*rootpower+self.caster.magic_contamination['dark']
        if distance>2*power**0.5:
            return (0,self)
        else:
            value=1-1/(distance+1)
        value*=self.caster.stats['wil']*self.caster.ai_preferences['contamination comfort level']/\
               (3*self.caster.magic_contamination['total']+self.caster.stats['wil']*self.caster.ai_preferences['contamination comfort level'])
        pref=self.caster.ai_preferences['ranged']*self.caster.ai_preferences['magic']*self.caster.ai_preferences['debuff']
        value=pref*value/(pref+value)

        return (value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

class Fireball():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.classification=['magic','ranged','elemental']
        self.contamination_cost={'elemental':3}
        self.name="Fireball"

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self,highlight_type='los')
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        self.killingblow=False
        self.power=(self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total'])**2+self.caster.magic_contamination['elemental']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.magic_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        line=BaseClasses.get_line(self.caster.location,location.location)
        #if len(line)>1: line.pop(0)
        oldpos=line[0]
        for position in line:
            if position==line[0]: pass
            elif self.caster.floor.cells[position[0]][position[1]].passable:
                oldpos=position
                continue
            elif self.caster.floor.cells[position[0]][position[1]].creatures!=[]:
                location=self.caster.floor.cells[position[0]][position[1]]
                lineindex=line.index(position)
                for i in range(lineindex+1,len(line)):
                    line.pop(len(line)-1)
                break
            else:
                location=self.caster.floor.cells[oldpos[0]][oldpos[1]]
                lineindex=line.index(position)
                for i in range(lineindex+1,len(line)):
                    line.pop(len(line)-1)
                break


        distance_to=location.distance_to(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]])
        blast_radius=self.power**(1/3)
        circle=self.caster.floor.get_circle(location.location,blast_radius,require_los=True)
        temperature=(400*(self.power)**0.5)*abs(random.gauss(self.caster.stats['wil'],self.caster.magic_contamination['total']**0.5)/(self.caster.stats['wil']+distance_to))
        heat=(self.power**0.5)/(random.triangular(1,1+distance_to,1))

        travel_line=BaseClasses.get_line(self.caster.location,location.location)
        if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in travel_line):
            fireball=BaseClasses.Item()
            fireball.image='./images/droplet.png'
            fireball.color=(1,0,0,1)
            self.caster.floor.animate_travel(fireball,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location,slowness=15)

        indent=0
        if self.caster==Shell.shell.player:
            Shell.messages.append("[b][size=13][color=1FAD39]You conjur an explosive ball of flame![/b][/size][/color]")
            Shell.messages.append(1)
            indent=1
        elif self.caster in Shell.shell.player.visible_creatures:
            if any(Shell.shell.player.location==i.location for i in circle):
                Shell.messages.append("[b][size=13][color=C21D25]{} summons a fireball![/b][/color][/size]".format(self.caster.name))
            else:
                Shell.messages.append("[b][color=AD801F]{} summons a fireball![/b][/color]".format(self.caster.name))
            Shell.messages.append(1)
            indent=1
        elif location in Shell.shell.player.visible_cells:
            if any(Shell.shell.player.location==i.location for i in circle):
                Shell.messages.append("[b][size=13][color=C21D25]A ball of flames strikes nearby![/b][/color][/size]")
            else:
                Shell.messages.append("[b][color=AD801F]A ball of flames strikes nearby![/b][/color]")
            Shell.messages.append(1)
            indent=1

        for i in circle:
            d=i.distance_to(location)+1
            intensity=heat/d
            temp=temperature/d**0.5
            red=0.8
            green=max((temp-800*d**0.5)/temp,0)
            blue=max((temp-1100*d)/temp,0)
            if temp>2000:
                green=green*1500/temp
                red=red*2000/temp
            Clock.schedule_once(functools.partial(i.animate_flash,(red,green,blue,(intensity-0.5)/intensity),(0.1,0.1,0.1,0.1),15),15/60)
            for j in i.creatures:
                res=j.resistance['magic']*j.resistance['elemental']
                indents=0
                if j==Shell.shell.player:
                    Shell.messages.append("[b][size=13][color=C21D25]You are caught in the blast![/color][/b][/size]")
                    Shell.messages.append(1)
                    indents=1
                elif j in Shell.shell.player.visible_creatures:
                    Shell.messages.append("[b][size=13][color=AD801F]{} is caught in the blast![/color][/b][/size]".format(j.name))
                    Shell.messages.append(1)
                    indents=1
                j.magic_contamination['elemental']+=1
                limbs_to_burn=[]
                number_of_burns=random.randrange(1,len(j.limbs)+1)
                number_of_burns=max(int(number_of_burns/random.triangular(1,d,1)),1)
                for k in range(0,number_of_burns):
                    newlimb=BaseClasses.targetchoice(j)
                    if newlimb not in limbs_to_burn:
                        limbs_to_burn.append(newlimb)
                for k in limbs_to_burn:
                    k.burn(temp/res,intensity/res,source=self)
                if indents==1:
                    Shell.messages.append(-1)
            for j in i.items:
                j.burn(temp,intensity,source=self)
                j.magic_contamination['elemental']+=1
            for j in i.dungeon:
                j.burn(temp,intensity,source=self)


        self.caster.on_ability_use(self)
        self.caster.magic_contamination['elemental']+=3
        if indent==1:
            Shell.messages.append(-1)


        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

    def decide(self):
        value=0
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures:
            return (0,self)
        targetcell=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]]
        castercell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        distance=targetcell.distance_to(castercell)
        power=(self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total'])**2+self.caster.magic_contamination['elemental']
        line=BaseClasses.get_line(self.caster.location,self.caster.target.location)
        for position in line:
            if position==line[0]: pass
            elif self.caster.floor.cells[position[0]][position[1]].passable:
                continue
            elif self.caster.target in self.caster.floor.cells[position[0]][position[1]].contents:
                break
            else:
                return (0,self)
        #we've established that the target can be hit. Now we'll look at collateral damage
        blast_radius=power**(1/3)
        circle=self.caster.floor.get_circle(self.caster.target.location,blast_radius,require_los=True)
        desirability=0
        for i in circle:
            d=i.distance_to(self.caster.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])+1
            for j in i.creatures:
                try:
                    desirability-=self.caster.affinity[j]/d
                except:
                    pass
        if desirability<=0:
            return (0,self)

        value=desirability/(1+desirability)
        value*=(-(distance-blast_radius)**2+2*distance)/(distance+1)
        value*=self.caster.stats['wil']*self.caster.ai_preferences['contamination comfort level']/\
               (3*self.caster.magic_contamination['total']+self.caster.stats['wil']*self.caster.ai_preferences['contamination comfort level'])
        pref=self.caster.ai_preferences['ranged']*self.caster.ai_preferences['magic']
        value=pref*value/(pref+value)

        return (value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

class Frostbolt():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.classification=['magic','ranged','elemental','debuff']
        self.contamination_cost={'elemental':2}
        self.name="Frost Bolt"

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self,highlight_type='los')
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        self.killingblow=False
        self.power=(self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total'])**2+self.caster.magic_contamination['elemental']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.magic_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        line=BaseClasses.get_line(self.caster.location,location.location)
        #if len(line)>1: line.pop(0)
        oldpos=line[0]
        for position in line:
            if position==line[0]: pass
            elif self.caster.floor.cells[position[0]][position[1]].passable:
                oldpos=position
                continue
            elif self.caster.floor.cells[position[0]][position[1]].creatures!=[]:
                location=self.caster.floor.cells[position[0]][position[1]]
                lineindex=line.index(position)
                for i in range(lineindex+1,len(line)):
                    line.pop(len(line)-1)
                break
            else:
                location=self.caster.floor.cells[oldpos[0]][oldpos[1]]
                lineindex=line.index(position)
                for i in range(lineindex+1,len(line)):
                    line.pop(len(line)-1)
                break


        distance_to=location.distance_to(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]])
        frosted_cells=[location]
        nextset=location.immediate_neighbors
        tested_cells=[]
        attempts=0
        probability=(1-1/self.power**0.5)**2
        ordered_frost={}
        creatures=[]

        travel_line=BaseClasses.get_line(self.caster.location,location.location)
        if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in travel_line):
            frost=BaseClasses.Item()
            frost.image='./images/droplet.png'
            frost.color=(0,0.3,1,1)
            self.caster.floor.animate_travel(frost,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location,slowness=15)
        while attempts<self.power**0.5+1:
            attempts+=1
            ordered_frost[attempts]=[]
            for i in nextset:
                if random.random()<probability**attempts:
                    if i.passable:
                        frosted_cells.append(i)
                        ordered_frost[attempts].append(i)
                        i.passable=False
                    elif i.creatures!=[]:
                        creatures.extend(i.creatures)
                elif not any(j.location==i.location for j in tested_cells):
                    tested_cells.append(i)
            nextset=[]
            for i in ordered_frost[attempts]:
                for j in i.immediate_neighbors:
                    if not any(j.location==k.location for k in tested_cells):
                        nextset.append(j)
            if nextset==[]:
                break

        for i in range(1,attempts+1):
            for j in ordered_frost[i]:
                Clock.schedule_once(functools.partial(self.add_frostwall,j,probability**0.5),15/60+i/15)





        indent=0
        if self.caster==Shell.shell.player:
            Shell.messages.append("[b][size=13][color=1FAD39]You conjur a bolt of frost![/b][/size][/color]")
            Shell.messages.append(1)
            indent=1
        elif self.caster in Shell.shell.player.visible_creatures:
            if any(Shell.shell.player.location==i.location for i in frosted_cells):
                Shell.messages.append("[b][size=13][color=C21D25]{} summons a frost bolt![/b][/color][/size]".format(self.caster.name))
            else:
                Shell.messages.append("[b][color=AD801F]{} summons a frost bolt![/b][/color]".format(self.caster.name))
            Shell.messages.append(1)
            indent=1
        elif location in Shell.shell.player.visible_cells:
            if any(Shell.shell.player.location==i.location for i in frosted_cells):
                Shell.messages.append("[b][size=13][color=C21D25]A bolt of frost strikes nearby![/b][/color][/size]")
            else:
                Shell.messages.append("[b][color=AD801F]A bolt of frost strikes nearby![/b][/color]")
            Shell.messages.append(1)
            indent=1


        for i in set(creatures):
            res=i.resistance['magic']*i.resistance['ice']*i.resistance['elemental']
            i.magic_contamination['elemental']+=1
            if self.power*random.random()>res*i.stats['luc']*random.random():
                Enchantments.Frozen_Creature(i,strength=int((1/res)*max(self.power-i.stats['luc'],0)**0.7+1))
                if i==Shell.shell.player:
                    Shell.messages.append("[color=C21D25]You are frozen solid![/color]")
                elif i in Shell.shell.player.visible_creatures:
                    Shell.messages.append("[color=1F4CAD]{} is frozen solid![/color]".format(i.name))
            else:
                limbs=[]
                creature_res=res
                for j in range(0,int(self.power**0.5+1)):
                    if self.power*random.random()<creature_res*i.stats['luc']*random.random():continue
                    newlimb=random.choice(i.limbs)
                    if newlimb not in limbs:
                        limbs.append(newlimb)
                for j in limbs:
                    res=creature_res*j.resistance['magic']*j.resistance['ice']*j.resistance['elemental']
                    Enchantments.Frozen_Limb(j,strength=int((1/res)*max(self.power-i.stats['luc'],0)**0.7+1))
                    if i==Shell.shell.player:
                        Shell.messages.append("[color=C21D25]Your {} is frozen![/color]".format(j.name))
                    elif i in Shell.shell.player.visible_creatures:
                        Shell.messages.append("[color=1F4CAD]{}'s {} is frozen solid![/color]".format(i.name,j.name))




        self.caster.on_ability_use(self)
        self.caster.magic_contamination['elemental']+=2
        if indent==1:
            Shell.messages.append(-1)


        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

    def decide(self):
        value=0
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures:
            return (0,self)
        targetcell=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]]
        castercell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        distance=targetcell.distance_to(castercell)
        power=(self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total'])**2+self.caster.magic_contamination['elemental']
        line=BaseClasses.get_line(self.caster.location,self.caster.target.location)
        for position in line:
            if position==line[0]: pass
            elif self.caster.floor.cells[position[0]][position[1]].passable:
                continue
            elif self.caster.target in self.caster.floor.cells[position[0]][position[1]].contents:
                break
            else:
                return (0,self)
        #we've established that the target can be hit. Now we'll look at collateral damage
        blast_radius=power**(1/3)
        circle=self.caster.floor.get_circle(self.caster.target.location,blast_radius,require_los=True)
        desirability=0
        for i in circle:
            d=i.distance_to(self.caster.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])+1
            for j in i.creatures:
                try:
                    desirability-=self.caster.affinity[j]/d
                except:
                    pass
        if desirability<=0:
            return (0,self)

        value=desirability/(1+desirability)
        value*=(-(distance-blast_radius)**2+2*distance)/(distance+1)
        value*=self.caster.stats['wil']*self.caster.ai_preferences['contamination comfort level']/\
               (3*self.caster.magic_contamination['total']+self.caster.stats['wil']*self.caster.ai_preferences['contamination comfort level'])
        pref=self.caster.ai_preferences['ranged']*self.caster.ai_preferences['magic']*self.caster.ai_preferences['debuff']/self.caster.ai_preferences['melee']
        value=pref*value/(pref+value)

        return (value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

    def add_frostwall(self,location=None,melt=0.9,*args,**kwargs):
        icewall=MapTiles.IceWall()
        icewall.melt_resistance=melt
        location.contents.append(icewall)

class Summon_Familiar():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.classification=['magic','summoning']
        self.contamination_cost={'summoning':5}
        self.name="Summon Familiar"

    def select_target(self):
        if any(isinstance(i,Enchantments.Familiar_Guidance) for i in self.caster.enchantments):
            if self.caster==Shell.shell.player:
                Shell.shell.log.addtext("You already have a familiar!")
            return
        self.do()

    def do(self,location=None,**kwargs):
        self.abort=False
        self.killingblow=False
        self.power=(self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total'])**2+self.caster.magic_contamination['summoning']

        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.magic_modification(self)
        if self.abort:
            return

        possible_familiars={Creatures.Owl:25,Creatures.Rat:5,Creatures.Falcon:15,Creatures.Hawk:15,Creatures.Cat:20,
                            Creatures.Dog:25,Creatures.Giant_Rat:30,Creatures.Giant_Ant:30,Creatures.Wolf:35,
                            Creatures.Giant_Spider:45, Creatures.Dire_Wolf:50,Creatures.Ostrich:60,
                            Creatures.Elephant_Bird:80}
        familiar=None
        while familiar==None:
            n=random.randint(0,int(self.power))
            f=random.choice(list(possible_familiars.keys()))
            if possible_familiars[f]<n:
                if self.caster==Shell.shell.player:
                    familiar=f(name=NameGen.namegen(random.choice(['m','f'])))
                    familiar.true_name=familiar.name
                    familiar.true_name_known=True
                else: familiar=f()
        familiar.master=self.caster
        self.caster.minions.append(familiar)
        self.caster.floor.place_creature(familiar,location=self.caster.location,retry='near')
        self.caster.floor.creaturelist.append(familiar)
        Enchantments.Familiar_Spirit(familiar,owner=self.caster)

        self.caster.on_ability_use(self)
        self.caster.magic_contamination['summoning']+=5

        if self.caster==Shell.shell.player:
            Shell.messages.append("[b][size=13][color=1FAD39]You summon {}, the {} from the void![/b][/size][/color]".format(familiar.name,familiar.basicname))
        elif self.caster in Shell.shell.player.visible_creatures:
            Shell.messages.append("[b][color=AD801F]{} summons a companion from the void![/color][/b]".format(self.caster.name))
        if familiar in Shell.shell.player.visible_creatures and self.caster!=Shell.shell.player:
            Shell.messages.append("[b][color=AD801F]{} suddenly appears![/color][/b]".format(familiar.name))


        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

class Starstorm():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.weapon=None
        self.classification=['magic','arcane','ranged']
        self.attacker=caster
        self.name="Starstorm"
        self.contamination_cost={'arcane':3}

    def select_target(self,**kwargs):
        self.do(**kwargs)

    def do(self,location=None,**kwargs):
        location=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        indent=0
        self.surprise=False
        self.abort=False
        self.killingblow=False
        self.damage_severity=0
        self.power=(self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total'])**2+self.caster.magic_contamination['arcane']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.magic_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        circle=self.caster.floor.get_circle(self.caster.location,2*self.power**(1/3)+2)
        projectiles=int(random.random()*self.power**0.7)+2

        if self.caster==Shell.shell.player:
            Shell.messages.append("[b][size=13][color=1FAD39]You create an explosion of magical shards![/b][/size][/color]")
            Shell.messages.append(1)
            indent=1
        elif self.caster in Shell.shell.visible_creatures:
            if any(Shell.shell.player.location==i.location for i in circle):
                Shell.messages.append("[b][size=13][color=C21D25]{} creates a shower of magical shards![/b][/color][/size]".format(self.caster.name))
            else:
                Shell.messages.append("[b][color=AD801F]{} creates a shower of magical shards![/b][/color]".format(self.caster.name))
            Shell.messages.append(1)
            indent=1

        for i in range(0,projectiles):
            child_indent=0
            projectile=Items.Stone(length=0.4*random.random()*random.random(),out_radius=0.4*random.random()*random.random(),
                                   material=Materials.Magic_Projectile_Material,power=random.random()*self.power)
            loc=random.choice(circle)
            if loc.location==self.caster.location:
                continue
            line=BaseClasses.get_line(self.caster.location,loc.location)
            for position in line:
                if position==line[0]: pass
                elif self.caster.floor.cells[position[0]][position[1]].passable:
                    location=self.caster.floor.cells[position[0]][position[1]]
                    continue
                else:
                    location=self.caster.floor.cells[position[0]][position[1]]
                    lineindex=line.index(position)
                    for i in range(lineindex+1,len(line)):
                        line.pop(len(line)-1)
                    break
            strikeables=[]
            target=None
            alive=False
            for i in location.contents:
                if isinstance(i,BaseClasses.Creature) and i.alive==True:
                    target=BaseClasses.targetchoice(i)
                    alive=True
                    break
                elif isinstance(i,BaseClasses.Item) or isinstance(i,BaseClasses.Limb):
                    strikeables.append(i)
                elif isinstance(i,BaseClasses.Creature):
                    strikeables.append(BaseClasses.targetchoice(i))
            if target==None and strikeables!=[]:
                target=random.choice(strikeables)


            if hasattr(target,'stats'): luc=target.stats['luc']
            else: luc=10
            self.weapon=projectile
            self.speed=random.random()*3*self.power
            self.energy=0.5*projectile.mass*self.speed*self.speed
            distance=Shell.shell.dungeonmanager.current_screen.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)
            self.time=distance/self.speed
            for i in range(0,int(distance)):
                self.energy-=1.3*self.speed**2*self.weapon.length*self.weapon.radius*0.4
                if self.energy<0:
                    self.energy=0
                self.speed=(2*self.energy/self.weapon.mass)**0.5
            #If we hit a wall or similar feature, land in front of it
            if any(isinstance(i,MapTiles.DungeonFeature) and i.passable==False for i in location.dungeon):
                xy=line[lineindex-1]
                self.landingcell=self.caster.floor.cells[xy[0]][xy[1]]
                line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
                if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                    self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
                #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)
                continue


            elif target==None:
                self.landingcell=location
                line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
                if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                    self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
                #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)
                continue

            #We can hit the target! Now let's process the damage
            self.target=target
            self.basetarget=target
            self.touchedobjects=[]
            self.penetrate=False
            self.contact=True
            self.blocked=False
            self.dodged=False
            self.parried=False
            self.damage_dealt=0
            self.type='crush'
            self.oldtype=self.type
            self.results=[]
            self.damagedobjects=[]
            self.absolute_depth_limit=self.weapon.length
            self.damagefactor=1
            self.attacker=self.caster
            self.accuracy=1
            self.arpen=-0.1
            self.area=random.random()*self.weapon.radius*self.weapon.length

            if hasattr(self.target,'owner') and self.target.owner!=None:
                Shell.messages.append("[b][color=AD801F]{} is struck in the {} with a magic bolt![/b][/color]".format(self.target.owner.name,self.target.name))
            else:
                Shell.messages.append("[b][color=AD801F]The {} is struck with a magic bolt![/b][/color]".format(self.target.name))
            try:
                self.blockable=1
                self.parryable=0
                self.dodgeable=1
                self.target.owner.evasion(self)
            except: pass
            if self.blocked==True:
                Shell.messages.pop()
                Shell.messages.append("[color=7B888C]The {} was blocked with the {}[/color]".format(self.weapon.name,self.target.name))
            elif self.dodged==True:
                Shell.messages.pop()
                Shell.messages.append("[color=7B888C]The {} was dodged![/color]".format(self.weapon.name))

            self.reducedmass = self.weapon.mass * self.target.mass / (self.weapon.mass + self.target.mass)
            thickness,density=self.armor_penetration()
            self.force = self.damagefactor* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
                self.weapon.thickness / self.weapon.youngs + thickness / self.youngs)**0.25))
            try:
                res=self.target.resistance['physical']*self.target.resistance['magic']*self.target.resistance['arcane']
            except:
                res=1
            self.force=self.force/res
            self.energ=self.energy/res
            self.pressure = self.force / self.area
            self.landingcell=location
            self.target.damageresolve(self,self.caster)
            line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
            if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
            limb_processed=False
            for i in self.touchedobjects:
                i.on_struck(self)
                try:
                    if i in self.basetarget.layers and limb_processed==False:
                        self.basetarget.on_struck(self)
                        limb_processed=True
                except:
                    self.target.on_struck(self)
            self.weapon.on_strike(self)

            if alive:
                self.basetarget.owner.survivalcheck()
                if self.basetarget.owner.alive==False:
                    self.caster.on_kill(self.basetarget.owner)
            try:
                self.basetarget.owner.magic_contamination['arcane']+=1
            except:
                pass
            if self.surprise:
                Shell.messages.append(-1)
                self.surprise=False




        self.caster.magic_contamination['arcane']+=3

        self.caster.on_ability_use(self)
        if self.caster==Shell.shell.player:
            Shell.shell.turn+=1
            pass
        if indent==1:
            Shell.messages.append(-1)

    def test_usability(self):
        return True

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.speed = (2 * self.energy / self.weapon.mass) ** 0.5
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25))
        self.force = min(new, 0.9 * self.force)

    def decide(self):
        value=0
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures:
            return (0,self)
        power=(self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total'])**2+self.caster.magic_contamination['arcane']
        circle=self.caster.floor.get_circle(self.caster.location,2*power**(1/3)+2,require_los=True)
        desirability=0
        targets=0
        castercell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        for i in circle:
            for j in i.creatures:
                if j==self.caster: continue
                d=i.distance_to(castercell)+1
                try:
                    desirability-=self.caster.affinity[j]/d
                    if self.caster.affinity[j]<0:
                        targets+=1
                except KeyError:
                    pass
        if targets<=0:
            return (0,self)
        value=desirability/(8/targets+desirability)
        value*=self.caster.stats['wil']*self.caster.ai_preferences['contamination comfort level']/\
               (3*self.caster.magic_contamination['total']+self.caster.stats['wil']*self.caster.ai_preferences['contamination comfort level'])
        pref=self.caster.ai_preferences['ranged']*self.caster.ai_preferences['magic']
        value=pref*value/(pref+value)

        return (value,self)

    def enemy_activation(self):
        self.do()

    def armor_penetration(self):
        tec=self.caster.stats['tec']
        luc=self.caster.stats['luc']
        if hasattr(self.target,'stats'):
            dluc=self.target.stats['luc']
            dper=self.target.stats['per']
        else:
            dluc=10
            dper=10
        if hasattr(self.target,"armor") and self.target.armor is not None:
            thickness=self.target.thickness+self.target.armor.thickness
            density=self.target.armor.density
            coverage=self.target.armor.coverage-self.arpen
                #mode shifts down for higher defender luck or per. Shifts up for higher attacker tec or luck.
            mode=(tec+0.5*luc)/(2*dluc+dper)
            mode=min(mode,1)
            if random.triangular(0,1,mode)>coverage:
                #if self.target.armor.coverage*abs(random.gauss(self.target.stats['luc'],1))<random.random()*(self.limb.stats['luc']+2*self.limb.stats['tec'])/3+self.arpen:
                self.youngs=self.target.arpen_youngs
                self.shear=self.target.arpen_shear
                thickness=self.target.thickness
                density=self.target.layers[len(self.target.layers)-1].density
                self.penetrate=True
            else:
                self.youngs=self.target.youngs
                self.shear=self.target.shear
        else:
            thickness=self.target.thickness
            self.youngs=self.target.youngs
            self.shear=self.target.shear
            if hasattr(self.target,'density'):
                density=self.target.density
            elif hasattr(self.target,'layers') and self.target.layers!=[]:
                density=self.target.layers[len(self.target.layers)-1].density
            else:
                density=5000
        return (thickness,density)

class Lightning_Strike():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.classification=['magic','ranged','elemental']

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self,highlight_type='los')
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        self.killingblow=False
        self.power=(self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total'])**2+self.caster.magic_contamination['elemental']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.magic_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        line=BaseClasses.get_line(self.caster.location,location.location)
        #if len(line)>1: line.pop(0)
        for position in line:
            if position==line[0]: pass
            elif self.caster.floor.cells[position[0]][position[1]].passable:
                continue
            else:
                location=self.caster.floor.cells[position[0]][position[1]]
                lineindex=line.index(position)
                for i in range(lineindex+1,len(line)):
                    line.pop(len(line)-1)
                break

        distance_to=location.distance_to(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]])
        blast_radius=self.power**(1/3)
        circle=self.caster.floor.get_circle(location.location,blast_radius,require_los=True)
        temperature=(400*(self.power)**0.5)*abs(random.gauss(self.caster.stats['wil'],self.caster.magic_contamination['total']**0.5)/(self.caster.stats['wil']+distance_to))
        heat=(self.power**0.5)/(random.triangular(1,1+distance_to,1))

        travel_line=BaseClasses.get_line(self.caster.location,location.location)
        if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in travel_line):
            fireball=BaseClasses.Item()
            fireball.image='./images/droplet.png'
            fireball.color=(1,0,0,1)
            self.caster.floor.animate_travel(fireball,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location,slowness=15)



        for i in circle:
            d=i.distance_to(location)+1
            intensity=heat/d
            temp=temperature/d**0.5
            red=0.8
            green=max((temp-800*d**0.5)/temp,0)
            blue=max((temp-1100*d)/temp,0)
            if temp>2000:
                green=green*1500/temp
                red=red*2000/temp
            Clock.schedule_once(functools.partial(i.animate_flash,(red,green,blue,(intensity-0.5)/intensity),(0.1,0.1,0.1,0.1),15),15/60)
            for j in i.creatures:
                j.magic_contamination['elemental']+=1
                limbs_to_burn=[]
                number_of_burns=random.randrange(1,len(j.limbs)+1)
                number_of_burns=max(int(number_of_burns/random.triangular(1,d,1)),1)
                for k in range(0,number_of_burns):
                    newlimb=BaseClasses.targetchoice(j)
                    if newlimb not in limbs_to_burn:
                        limbs_to_burn.append(newlimb)
                for k in limbs_to_burn:
                    k.burn(temp,intensity)
            for j in i.items:
                j.burn(temp,intensity)
                j.magic_contamination['elemental']+=1


        self.caster.on_ability_use(self)
        self.caster.magic_contamination['elemental']+=3



        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

    def decide(self):
        value=0
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures:
            return (0,self)
        targetcell=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]]
        castercell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        distance=targetcell.distance_to(castercell)
        power=(self.caster.stats['wil']**0.5+1.05**self.caster.magic_contamination['total'])**2+self.caster.magic_contamination['elemental']
        line=BaseClasses.get_line(self.caster.location,self.caster.target.location)
        for position in line:
            if position==line[0]: pass
            elif self.caster.floor.cells[position[0]][position[1]].passable:
                continue
            elif self.caster.target in self.caster.floor.cells[position[0]][position[1]].contents:
                break
            else:
                return (0,self)
        #we've established that the target can be hit. Now we'll look at collateral damage
        blast_radius=power**(1/3)
        circle=self.caster.floor.get_circle(self.caster.target.location,blast_radius,require_los=True)
        desirability=0
        for i in circle:
            d=i.distance_to(self.caster.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])+1
            for j in i.creatures:
                try:
                    desirability-=self.caster.affinity[j]/d
                except:
                    pass
        if desirability<=0:
            return (0,self)

        value=desirability/(1+desirability)
        value*=(-(distance-blast_radius)**2+2*distance)/(distance+1)
        value*=self.caster.stats['wil']*self.caster.ai_preferences['contamination comfort level']/\
               (3*self.caster.magic_contamination['total']+self.caster.stats['wil']*self.caster.ai_preferences['contamination comfort level'])
        pref=self.caster.ai_preferences['ranged']*self.caster.ai_preferences['magic']
        value=pref*value/(pref+value)

        return (value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

#Psychic Abilities
class Psychokinesis():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.weapon=None
        self.focuscost=20
        self.classification=['weaponless','physical','ranged']
        self.attacker=caster
        self.name="Psychokinesis"

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self)
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        self.damage_severity=0
        self.killingblow=False
        try:
            distance=Shell.shell.dungeonmanager.current_screen.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)
            self.focuscost=5+distance
        except AttributeError:
            self.focuscost=10
        if not any(location.location==i.location for i in self.caster.visible_cells):
            self.focuscost*=2
        if self.caster.focus[0]<self.focuscost:
            if self.caster==Shell.shell.player:
                Shell.shell.log.addtext("You don't have the focus to do that")
            return
        if self.test_usability()==False:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        self.damagefactor=1
        self.power=self.caster.stats['per']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.psychic_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return

        self.caster.on_ability_use(self)
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
        self.time=0
        self.arpen=-1
        indent=0
        for i in location.contents:
            if isinstance(i,BaseClasses.Creature) and i.alive==True:
                target=BaseClasses.targetchoice(i)
                self.calculate_force(target)
                if self.caster==Shell.shell.player:
                    Shell.messages.append('[b][size=13][color=1FAD39]You strike {} in the {} with a burst of telekenetic force![/b][/size][/color]'.format(i.name,target.name))
                    indent+=1
                elif i==Shell.shell.player:
                    Shell.messages.append('[b][size=13][color=C21D25]Something strikes you in the {}![/b][/size][/color]'.format(target.name))
                    indent+=1
                elif i in Shell.shell.player.visible_creatures:
                    Shell.messages.append("[b][color=AD801F]Something strikes {} in the {}[/b][/color]".format(i.name,target.name))
                    indent+=1
                target.owner.evasion(self,blockable=0,dodgeable=0,parryable=0,suprisable=0)
                if indent>0:
                    Shell.messages.append(1)
                target.damageresolve(self,self.caster)
                i.survivalcheck()
                if i.alive==False:
                    self.killingblow=True
                    self.caster.on_kill(i)
                try:
                    Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                    Shell.shell.reticule=None
                    Shell.shell.keyboard_mode='play'
                except: pass
                self.caster.focus[0]-=self.focuscost
                if self.caster==Shell.shell.player: Shell.shell.turn+=1
                if indent>0:
                    Shell.messages.append(-1)
                return
            elif isinstance(i,BaseClasses.Item) or isinstance(i,BaseClasses.Limb):
                strikeables.append(i)
            elif isinstance(i,BaseClasses.Creature):
                strikeables.append(BaseClasses.targetchoice(i))
        if strikeables!=[]:
            if self.caster==Shell.shell.player:
                Shell.messages.append('[b][size=13][color=1FAD39]You unleash a wave of force![/b][/size][/color]')
                Shell.messages.append(1)
                indent+=1
            for i in strikeables:
                self.calculate_force(i)
                i.damageresolve(self,self.caster)
        elif self.caster==Shell.shell.player:
            Shell.messages.append('[b][size=13][color=1FAD39]You unleash a wave of force![/b][/size][/color]')
        self.caster.focus[0]-=self.focuscost
        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1
        if indent>0:
            Shell.messages.append(-1)

    def calculate_force(self,target):
        res=target.resistance['psychic']*target.resistance['physical']
        if hasattr(target,'owner') and target.owner is not None:
            res*=target.owner.resistance['psychic']*target.owner.resistance['physical']
        force=self.damagefactor*2*self.power*self.caster.focus[0]
        self.weapon=None
        self.limb=None
        self.force=force/res
        self.area=0.1*(self.caster.focus[1]-self.caster.focus[0]+2)/self.caster.focus[1]
        self.pressure=force/self.area
        self.energy=self.power*self.power/res
        self.absolute_depth_limit=10
        self.speed=5
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
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures:
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
        pref=self.caster.ai_preferences['psychic']*self.caster.ai_preferences['ranged']
        value=value*pref/(value+pref)
        return (value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

class Psychic_Grab():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.classification=['physical']
        self.name="Psychic Grab"

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self)
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        self.damagefactor=1
        self.power=self.caster.stats['per']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.psychic_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        stats=self.caster.stats.copy()
        stats['per']=self.power
        self.holding_limb=Limbs.Psychic_Grasp(self.caster.stats,name="mind",owner=self.caster,natural=False)
        if location.creatures!=[]:
            target=location.creatures[0]
            attempts=0
            limb_to_grab=BaseClasses.targetchoice(target)
            while attempts<self.caster.stats['tec'] and 'graspable' not in limb_to_grab.target_class:
                limb_to_grab=BaseClasses.targetchoice(target)
            self.target=limb_to_grab.owner
            self.held_limb=limb_to_grab
            gripsize=self.holding_limb.stats['tec']/10
            chance=self.target.stats['str']*self.held_limb.radius/(self.damagefactor*
                self.holding_limb.stats['str']*self.holding_limb.ability*gripsize*self.held_limb.length+0.01)
            if chance<random.random():
                grasp=Enchantments.Held_In_Grasp(self.target,holding_limb=self.holding_limb,held_limb=self.held_limb,mobile_grabber=True)
                grasp.on_turn()
                self.holding_limb.vanish_case=grasp.grasping
                if self.caster==Shell.shell.player:
                    Shell.messages.append("[b][size=13][color=1FAD39]You grab {}'s {} with your {}[/b][/size][/color]".format(
                        self.target.name,self.held_limb.name,self.holding_limb.name))
                elif self.target==Shell.shell.player:
                    Shell.messages.append("[b][size=13][color=C21D25]{} grabs your {} with its {}[/b][/size][/color]".format(
                        self.caster.name,self.held_limb.name,self.holding_limb.name))
                elif self.caster in Shell.shell.player.visible_creatures and self.target in Shell.shell.player.visible_creatures:
                    Shell.messages.apend("[b][color=AD801F]{} grabs {}'s {} with its {}[/b][/color]".format(self.caster.name,self.target.name,
                                                                               self.held_limb.name,self.holding_limb.name))
            else:
                if self.caster==Shell.shell.player:
                    Shell.messages.append(
                        "[b][size=13][color=1FAD39]You attempt to grab {}'s {} with your {},[color=7B888C] but {} struggles free![/b][/size][/color][/color]".format(
                        self.target.name,self.held_limb.name,self.holding_limb.name,self.target.name))
                elif self.target==Shell.shell.player:
                    Shell.messages.append(
                        "[b][size=13][color=C21D25]{} attempts to grab your {} with its {},[color=7B888C] but you break free![/b][/size][/color][/color]".format(
                        self.caster.name,self.held_limb.name,self.holding_limb.name))
                elif self.caster in Shell.shell.player.visible_creatures and self.target in Shell.shell.player.visible_creatures:
                    Shell.messages.apend(
                        "[b][color=AD801F]{} attempts to grab {}'s {} with its {},[color=7B888C] but cannot hold fast![/b][/color][/color]".format(
                        self.caster.name,self.target.name,self.held_limb.name,self.holding_limb.name))

        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        self.target.hostilitycheck(self.caster)
        self.target.affinity[self.caster]-=1
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

    def decide(self):
        if self.test_usability()==False:
            return (0,self)
        value=0
        if not isinstance(self.caster.target,BaseClasses.Creature) or self.caster.hostilitycheck(self.caster.target)==False:
            return (value,self)
        s_adv=self.caster.stats['per']/self.caster.target.stats['str']
        value=s_adv/(2+s_adv)
        for i in self.caster.target.enchantments:
            if isinstance(i,Enchantments.Held_In_Grasp) and i.holding_limb in self.caster.limbs:
                value=value/5
        value=value*self.caster.ai_preferences['psychic']/(value+self.caster.ai_preferences['psychic'])
        return (value,self)

    def test_usability(self):
        if self.caster.focus[0]<30:
            return False
        else:
            return True

    def enemy_activation(self):
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

class Addle():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.weapon=None
        self.focuscost=30
        self.classification=['weaponless','psychic','ranged']
        self.attacker=caster
        self.name="Addle"

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self)
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        self.damage_severity=0
        self.killingblow=False
        try:
            distance=Shell.shell.dungeonmanager.current_screen.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)
            self.focuscost=5+distance
        except AttributeError:
            self.focuscost=5
        if self.caster.focus[0]<self.focuscost:
            if self.caster==Shell.shell.player:
                Shell.shell.log.addtext("You don't have the focus to do that")
            return
        if self.test_usability()==False:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        self.damagefactor=1
        self.power=self.caster.stats['per']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.psychic_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return

        self.caster.on_ability_use(self)
        self.caster.combataction=True
        indent=0
        creatures=location.creatures
        if creatures==[] and location.items==[]:
            if self.caster==Shell.shell.player:
                self.caster.focus[0]-=self.focuscost
                Shell.messages.append("[color=7B888C]Your attempts to addle the dungeon are amusing, but not fruitful[/color]")
                Shell.shell.turn+=1
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        if creatures!=[]:
            for i in creatures:
                if 'mindless' in i.classification:
                    if self.caster==Shell.shell.player and i!=self.caster:
                        Shell.messages.append("[color=7B888C]{} doesn't seem to have any thoughts which can be manipulated[/color]".format(i.name))
                    elif i==Shell.shell.player:
                        Shell.messages.append("[color=7B888C]Your mind is empty[/color]")
                    continue
                addlepower=self.power*self.caster.focus[0]/(i.stats['wil']*i.focus[0])
                addlepower=addlepower/i.resistance['psychic']
                if random.random()*addlepower>random.random()*random.random():
                    turns=2*int((10*addlepower)**0.5)+random.randint(1,5)
                    Enchantments.Confused(i,power=int(2*addlepower)+1,turns=turns)
                    if i==Shell.shell.player:
                        Shell.messages.append("[color=1F4CAD]Wait... what were you doing again?[/color]")
                    elif self.caster in Shell.shell.player.visible_creatures or (self.caster==Shell.shell.player and i in self.caster.detected_creatures):
                        Shell.messages.append("[color=1F4CAD]{} has no idea what is going on![/color]".format(i.name))
                elif random.random()*addlepower>random.random():
                    turns=2*int((10*addlepower)**0.5)+random.randint(1,5)
                    Enchantments.Dazed(i,power=int(2*addlepower)+1,turns=turns)
                    if i==Shell.shell.player:
                        Shell.messages.append("[color=1F4CAD]You feel as if the world is spinning![/color]")
                    elif self.caster in Shell.shell.player.visible_creatures or (self.caster==Shell.shell.player and i in self.caster.detected_creatures):
                        Shell.messages.append("[color=1F4CAD]{} is dazed![/color]".format(i.name))
                else:
                    if i==Shell.shell.player:
                        Shell.messages.append("[color=1F4CAD]You struggle to keep your thoughts together![/color]")
                    elif self.caster in Shell.shell.player.visible_creatures or (self.caster==Shell.shell.player and i in self.caster.detected_creatures):
                        Shell.messages.append("[color=1F4CAD]{} struggles to keep focus![/color]".format(i.name))
                i.focus[0]-=int(1.5*self.power*addlepower)+1
                i.focus[0]=max(0,i.focus[0])

        if location.items!=[]:
            if self.caster==Shell.shell.player:
                addled=[]
                for i in location.items:
                    for j in i.enchantments:
                        if j.category=='magic':
                            j.attempt_identification(self.power/i.resistance['psychic'])
                            addled.append(j)
                if len(addled)>0:
                    Shell.messages.append("You detect a presence!")
                    for i in addled:
                        i.on_psychic_contact(self.caster)
                elif len(location.items)==1 and creatures==[] and any(location.location==i.location for i in Shell.shell.player.visible_cells):
                    Shell.messages.append("[color=7B888C]The {} doesn't seem particularly disoriented[/color]".format(location.items[0].name))
                elif creatures==[] and any(location.location==i.location for i in Shell.shell.player.visible_cells):
                    Shell.messages.append("[color=7B888C]Those things don't seem to be bothered by you[/color]")


        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1
        if indent>0:
            Shell.messages.append(-1)
        self.caster.focus[0]-=self.focuscost

    def decide(self):
        value=0
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures:
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
        pref=self.caster.ai_preferences['psychic']*self.caster.ai_preferences['ranged']
        value=value*pref/(value+pref)
        return (value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

class Telekinetic_Barrier():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.weapon=None
        self.focuscost=50
        self.classification=['defensive','psychic']
        self.attacker=caster
        self.name="Telekinetic Barrier"

    def select_target(self):
        self.do()

    def do(self,location=None,**kwargs):
        self.abort=False
        if self.caster.focus[0]<self.focuscost:
            if self.caster==Shell.shell.player:
                Shell.shell.log.addtext("You don't have the focus to do that")
            return
        if any(isinstance(i,Enchantments.Psychic_Shield) for i in self.caster.enchantments):
            if self.caster==Shell.shell.player:
                Shell.shell.log.addtext("You already have a psychic shield!")
            return
        if self.test_usability()==False:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        self.damagefactor=1
        self.power=self.caster.stats['per']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.psychic_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        Enchantments.Psychic_Shield(self.caster,strength=self.power/2)
        if self.caster==Shell.shell.player:
            Shell.messages.append("[color=1FAD39]You shield yourself with a telekinetic barrier![/color]")

        self.caster.on_ability_use(self)
        self.caster.combataction=True

        if self.caster==Shell.shell.player: Shell.shell.turn+=1


    def decide(self):
        if self.caster.focus[0]<=50:
            return (0,self)
        value=0.7*(self.caster.focus[0]/self.caster.focus[1])**2
        if 'psychic' in self.caster.classification: value*=1/0.7
        pref=self.caster.ai_preferences['psychic']*self.caster.ai_preferences['ranged']
        value=value*pref/(value+pref)
        return (value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do()

#Physical skills are handled just like attacks. They must have basetarget and target attributes, force, pressure, etc
class Throw():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.weapon=None
        self.can_tear=False
        self.classification=['physical','ranged']
        self.attacker=caster
        self.name="Throw"

    def select_target(self):
        if self.caster==Shell.shell.player:
            self.throwing_limbs=[]
            self.throwables=[]
            for i in self.caster.limbs:
                if i.grasp==True and i.equipment['grasp']==None:
                    self.throwing_limbs.append(i)
                elif i.grasp==True and not any(isinstance(j,Enchantments.Bound) for j in i.equipment['grasp'].enchantments):
                    self.throwables.append(i.equipment['grasp'])
            if self.throwing_limbs!=[]:
                for i in self.caster.inventory:
                    if i not in self.caster.equipped_items:
                        self.throwables.append(i)
            if self.throwables==[]:
                Shell.shell.log.addtext("You have nothing which can be thrown")
            else:
                Shell.shell.inventory.show_player_inventory(show_only=self.throwables)
                Shell.shell.keyboard_mode='item select'
                Shell.shell.keyboard_send_to=self

    def do(self,location=None,remove_item=True,**kwargs):
        self.abort=False
        self.damagefactor=1
        self.power=self.caster.stats['str']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.physical_ability_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        bonus=self.power/self.caster.stats['str']
        self.damage_severity=0
        self.surprise=False
        indent=0
        self.remove_item=remove_item
        self.killingblow=False
        resolved=False
        throw_accuracy=1+(self.caster.focus[0]*1.12**self.caster.stats['tec'])/self.caster.focus[1]
        while resolved==False:
            if throw_accuracy<self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)*random.random():
                location=random.choice(location.immediate_neighbors)
            else:
                resolved=True



        line=BaseClasses.get_line(self.caster.location,location.location)
        #if len(line)>1: line.pop(0)
        for position in line:
            if position==line[0]: pass
            elif self.caster.floor.cells[position[0]][position[1]].passable:
                continue
            else:
                location=self.caster.floor.cells[position[0]][position[1]]
                lineindex=line.index(position)
                for i in range(lineindex+1,len(line)):
                    line.pop(len(line)-1)
                break


        strikeables=[]
        target=None
        alive=False
        for i in location.contents:
            if isinstance(i,BaseClasses.Creature) and i.alive==True:
                target=BaseClasses.targetchoice(i)
                alive=True
                break
            elif isinstance(i,BaseClasses.Item) or isinstance(i,BaseClasses.Limb):
                strikeables.append(i)
            elif isinstance(i,BaseClasses.Creature):
                strikeables.append(BaseClasses.targetchoice(i))
        if target==None and strikeables!=[]:
            target=random.choice(strikeables)


        if hasattr(target,'stats'): luc=target.stats['luc']
        else: luc=10

        throwcosts={}
        throwspeeds={}
        if self.weapon.equipped!=[]:
            self.throwing_limbs=self.weapon.equipped
        for i in self.throwing_limbs:
            if i.attachpoint!=None:
                moment=i.attachpoint.I+i.attachpoint.length*i.attachpoint.length*i.movemass
                if i.equipment['grasp']==None: moment+=i.attachpoint.length*i.attachpoint.length*self.weapon.mass
                throwstrength=i.attachpoint.stats['str']*i.attachpoint.ability+0.2*i.stats['str']*i.ability
                throwstrength*=bonus
                armlength=i.attachpoint.length
            else:
                moment=i.I
                throwstrength=i.stats['str']*i.ability*bonus
                armlength=i.length
            torque=10*throwstrength*moment**0.5
            swingangle = random.triangular(low=2, high=4.5, mode=min(max(2 * i.stats['tec'] / luc,2),4.5))
            throwspeeds[i]=armlength*((2 * torque * swingangle / moment) ** 0.5)
            throwcosts[i]=1+int(4*moment/throwstrength)

        self.limb=None
        current_speed=0
        for i in throwspeeds:
            if throwspeeds[i]>current_speed and throwcosts[i]<self.caster.stamina[0]:
                self.limb=i
        if self.limb==None:
            Shell.shell.log.addtext("You don't have the stamina to throw that right now")
            return

        self.caster.on_ability_use(self)

        self.speed=throwspeeds[self.limb]
        self.caster.stamina[0]-=throwcosts[self.limb]
        self.caster.focus[0]-=3
        self.caster.combataction=True
        self.caster.attacked=True
        self.energy=0.5*self.weapon.mass*self.speed**2

        #Make sure we can actually throw far enough to reach our target
        maxdistance=max(self.speed*self.speed/20-3,1)
        distance=Shell.shell.dungeonmanager.current_screen.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)
        self.time=distance/self.speed
        for i in range(0,int(distance)):
            self.energy-=1.3*self.speed**2*self.weapon.length*self.weapon.radius*0.4
            self.speed=(2*self.energy/self.weapon.mass)**0.5
            if self.speed<1:
                maxdistance=min(i,maxdistance)
                self.speed=0
                self.energy=0
                break
        if maxdistance<distance:
            xy=line[min(int(maxdistance*(len(line)-1)/distance),len(line)-1)]
            self.landingcell=self.caster.floor.cells[xy[0]][xy[1]]
            line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
            if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
            #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)
            try:
                self.caster.unequip(self.weapon,log=False)
                self.caster.inventory.remove(self.weapon)
                self.weapon.in_inventory=None
            except ValueError: pass
            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            if self.caster==Shell.shell.player: Shell.shell.turn+=1
            return
        #If we hit a wall or similar feature, land in front of it
        if any(isinstance(i,MapTiles.DungeonFeature) and i.passable==False for i in location.dungeon):
            xy=line[lineindex-1]
            self.landingcell=self.caster.floor.cells[xy[0]][xy[1]]
            line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
            if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
            #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)
            try:
                self.caster.unequip(self.weapon,log=False)
                self.caster.inventory.remove(self.weapon)
                self.weapon.in_inventory=None
            except ValueError: pass
            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            if self.caster==Shell.shell.player: Shell.shell.turn+=1
            return
        elif target==None:
            self.landingcell=location
            line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
            if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
            #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)
            try:
                self.caster.unequip(self.weapon,log=False)
                self.caster.inventory.remove(self.weapon)
                self.weapon.in_inventory=None
            except ValueError: pass
            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            if self.caster==Shell.shell.player: Shell.shell.turn+=1
            return
        #We can hit the target! Now let's process the damage
        self.target=target
        self.basetarget=target
        self.touchedobjects=[]
        self.penetrate=False
        self.contact=True
        self.blocked=False
        self.dodged=False
        self.parried=False
        self.damage_dealt=0
        possible_types=['crush']
        if hasattr(self.weapon,'edge'):
            possible_types.append('cut')
        if hasattr(self.weapon,'tip'):
            possible_types.append('pierce')
        self.type=random.choice(possible_types)
        self.oldtype=self.type
        self.results=[]
        self.damagedobjects=[]
        self.absolute_depth_limit=self.weapon.length
        self.attacker=self.caster
        self.accuracy=(self.caster.focus[0]*self.caster.stats['tec']**0.6)/self.caster.focus[1]
        if self.type=='crush':
            self.arpen=-0.1*max(self.weapon.length,self.weapon.thickness)
            self.area=random.random()*self.weapon.radius*self.weapon.length
        elif self.type=='cut':
            self.arpen=0.05
            self.area=self.weapon.edge
        elif self.type=='pierce':
            self.arpen=0.1
            self.area=self.weapon.tip

        if self.caster==Shell.shell.player:
            if self.target.owner!=None:
                Shell.messages.append(
                "[b][size=13][color=1FAD39]You throw your {} at {}'s {}[/b][/size][/color]".format(self.weapon.name,self.target.owner.name,self.target.name))
                indent+=1
            else:
                Shell.messages.append(
                "[b][size=13][color=1FAD39]You throw your {} at the {}[/b][/size][/color]".format(self.weapon.name,self.target.name))
                indent+=1
        elif self.caster in Shell.shell.player.visible_creatures:
            if self.basetarget.owner==Shell.shell.player:
                Shell.messages.append(
                "[b][size=13][color=C21D25]{} throws its {} at your {}[/b][/size][/color]".format(self.caster.name,self.weapon.name,self.target.name))
                indent+=1
            elif self.target.owner!=None:
                Shell.messages.append("{} throws its {} at {}'s {}".format(self.caster.name,self.weapon.name,self.target.owner.name,self.target.name))
                indent+=1
            else:
                Shell.messages.append("[b][color=AD801F]{} throws its {} at {}[/b][/color]".format(self.caster.name,self.weapon.name,self.target.name))
                indent+=1

        try:
            self.blockable=1
            self.parryable=0
            self.dodgeable=1
            self.target.owner.evasion(self)
        except: pass
        if indent>0:
            Shell.messages.append(1)

        if self.blocked==True:
            Shell.messages.append("[color=7B888C]The {} was blocked with the {}[/color]".format(self.weapon.name,self.target.name))
        elif self.dodged==True:
            Shell.messages.append("[color=7B888C]The {} was dodged![/color]".format(self.weapon.name))

        self.reducedmass = self.weapon.mass * self.target.mass / (self.weapon.mass + self.target.mass)
        thickness,density=self.armor_penetration()
        self.force = self.damagefactor* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + thickness / self.youngs)**0.25))
        self.pressure = self.force / self.area

        self.landingcell=location
        if not self.abort: self.target.damageresolve(self,self.caster)
        line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
        if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
            self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
        #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)
        try:
            self.caster.unequip(self.weapon,log=False)
            self.caster.inventory.remove(self.weapon)
            self.weapon.in_inventory=None
        except ValueError: pass
        Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)

        limb_processed=False
        if not self.abort:
            for i in self.touchedobjects:
                i.on_struck(self)
                try:
                    if i in self.basetarget.layers and limb_processed==False:
                        self.basetarget.on_struck(self)
                        limb_processed=True
                except:
                    self.target.on_struck(self)
            self.weapon.on_strike(self)

        if alive:
            self.basetarget.owner.survivalcheck()
            if self.basetarget.owner.alive==False:
                self.caster.on_kill(self.basetarget.owner)

        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1
        if indent>0:
            Shell.messages.append(-1)
        if self.surprise:
            Shell.messages.append(-1)

    def test_usability(self):
        return True

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.speed = (2 * self.energy / self.weapon.mass) ** 0.5
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25))
        self.force = min(new, 0.9 * self.force)

    def decide(self):
        value=0
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures:
            return (0,self)
        if not any(i.grasp==True and i.equipment['grasp']==None for i in self.caster.limbs):
            return(0,self)
        if len(self.caster.equipped_items)>=len(self.caster.inventory):
            return(0,self)
        try:
            line=BaseClasses.get_line(self.caster.location,self.caster.target.location)
            line.pop(0)
            line.pop(len(line)-1)
        except:
            return(0,self)
        if any(self.caster.floor.cells[i[0]][i[1]].passable==False for i in line):
            return(0,self)
        #We have established that we have unequipped items and the means to throw them
        targetcell=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]]
        castercell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        distance=targetcell.distance_to(castercell)
        rootstrength=self.caster.stats['str']**0.5
        if distance<1.42:
            value+=0.1
        elif distance<=self.caster.stats['str']:
            value+=2*rootstrength/distance
        item_idealness=-50
        for i in self.caster.inventory:
            if i not in self.caster.equipped_items:
                new_idealness=0
                if hasattr(i,'edge'): new_idealness+=1
                if hasattr(i,'tip'): new_idealness+=1
                new_idealness+=max(1-abs(rootstrength-i.mass/2),-2)
                item_idealness=max(item_idealness,new_idealness)
                if new_idealness==item_idealness:
                    self.enemyweapon=i
        value+=item_idealness
        pref=self.caster.ai_preferences['throw']*self.caster.ai_preferences['ranged']
        value=value*pref/(value+pref)
        if 'thrower' in self.caster.classification: value*=2
        #print('throwing likelihood is ',value)
        return (value,self)

    def enemy_activation(self):
        self.throwing_limbs=[]

        for i in self.caster.limbs:
            if i.grasp==True and i.equipment['grasp']==None:
                self.throwing_limbs.append(i)
        self.weapon=self.enemyweapon
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

    def recieve_input(self,item):
        if item=='abort':
            Shell.shell.inventory.close()
            Shell.shell.keyboard_mode='play'
            Shell.shell.mouselistener(None,[0,0])
        if hasattr(item,'mass'):
            Shell.shell.inventory.close()
            Shell.shell.keyboard_mode='targeting'
            self.weapon=item
            Shell.shell.reticule=Shell.Reticule(purpose=self,highlight_type='los')
            Shell.shell.player.floor.cells[Shell.shell.player.location[0]][Shell.shell.player.location[1]].contents.append(Shell.shell.reticule)

    def armor_penetration(self):
        tec=self.caster.stats['tec']
        luc=self.caster.stats['luc']
        if hasattr(self.target,'stats'):
            dluc=self.target.stats['luc']
            dper=self.target.stats['per']
        else:
            dluc=10
            dper=10
        if hasattr(self.target,"armor") and self.target.armor is not None:
            thickness=self.target.thickness+self.target.armor.thickness
            density=self.target.armor.density
            coverage=self.target.armor.coverage-self.arpen
                #mode shifts down for higher defender luck or per. Shifts up for higher attacker tec or luck.
            mode=(tec+0.5*luc)/(2*dluc+dper)
            mode=min(mode,1)
            if random.triangular(0,1,mode)>coverage:
                #if self.target.armor.coverage*abs(random.gauss(self.target.stats['luc'],1))<random.random()*(self.limb.stats['luc']+2*self.limb.stats['tec'])/3+self.arpen:
                self.youngs=self.target.arpen_youngs
                self.shear=self.target.arpen_shear
                thickness=self.target.thickness
                density=self.target.layers[len(self.target.layers)-1].density
                self.penetrate=True
            else:
                self.youngs=self.target.youngs
                self.shear=self.target.shear
        else:
            thickness=self.target.thickness
            self.youngs=self.target.youngs
            self.shear=self.target.shear
            if hasattr(self.target,'density'):
                density=self.target.density
            elif hasattr(self.target,'layers'):
                density=self.target.layers[len(self.target.layers)-1].density
            else:
                density=5000
        return (thickness,density)

class Fire_Bow():
    def __init__(self,caster,bow,**kwargs):
        self.caster=caster
        self.bow=bow
        self.weapon=None
        self.can_tear=False
        self.classification=['physical','ranged']
        self.attacker=caster
        self.name="Fire Bow"

    def select_target(self):
        if self.caster==Shell.shell.player:
            self.arrows=[]
            limbs=[]
            for i in self.caster.limbs:
                if i.grasp==True and i.equipment['grasp']==None:
                    limbs.append(i)
            if limbs==[]:
                Shell.shell.log.addtext("You do not have a free hand with which to fire the bow!")
                return
            if self.caster.quiver!=[]:
                for i in self.caster.quiver:
                    if isinstance(i,Items.Arrow):
                        self.arrows.append(i)
                if self.arrows!=[]:
                    self.weapon=random.choice(self.arrows)
                    Shell.shell.keyboard_mode='targeting'
                    Shell.shell.reticule=Shell.Reticule(purpose=self,highlight_type='los')
                    Shell.shell.player.floor.cells[Shell.shell.player.location[0]][Shell.shell.player.location[1]].contents.append(Shell.shell.reticule)
                    return
            else:
                for i in self.caster.inventory:
                    if isinstance(i,Items.Arrow):
                        self.arrows.append(i)
            if self.arrows==[]:
                Shell.shell.log.addtext("You have no arrows")
            else:
                Shell.shell.inventory.show_player_inventory(show_only=self.arrows)
                Shell.shell.keyboard_mode='item select'
                Shell.shell.keyboard_send_to=self

    def do(self,location=None,remove_item=True,**kwargs):
        self.abort=False
        self.damagefactor=1
        self.power=self.bow.equipped[0].stats['str']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.physical_ability_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        bonus=self.power/self.bow.equipped[0].stats['str']
        self.damage_severity=0
        self.surprise=False
        indent=0
        self.remove_item=remove_item
        self.killingblow=False
        resolved=False
        accuracy=(1+(self.caster.focus[0]*1.16**self.caster.stats['tec'])/self.caster.focus[1])*(1+(50-self.caster.tension)/200)*self.bow.brace**0.2
        while resolved==False and self.caster.passives['sharpshooter']<1:
            if accuracy<self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)*random.random():
                location=random.choice(location.immediate_neighbors)
            else:
                resolved=True



        line=BaseClasses.get_line(self.caster.location,location.location)
        #if len(line)>1: line.pop(0)
        for position in line:
            if position==line[0]: pass
            elif self.caster.floor.cells[position[0]][position[1]].passable:
                continue
            else:
                location=self.caster.floor.cells[position[0]][position[1]]
                lineindex=line.index(position)
                for i in range(lineindex+1,len(line)):
                    line.pop(len(line)-1)
                break

        Enchantments.Defenseless(self.caster,turns=1)
        strikeables=[]
        target=None
        alive=False
        for i in location.contents:
            if isinstance(i,BaseClasses.Creature) and i.alive==True:
                target=BaseClasses.targetchoice(i)
                alive=True
                break
            elif isinstance(i,BaseClasses.Item) or isinstance(i,BaseClasses.Limb):
                strikeables.append(i)
            elif isinstance(i,BaseClasses.Creature):
                strikeables.append(BaseClasses.targetchoice(i))
        if target==None and strikeables!=[]:
            target=random.choice(strikeables)


        if hasattr(target,'stats'): luc=target.stats['luc']
        else: luc=10
        k=(48*3.14159*1000000000*self.bow.youngs*self.bow.radius**4)/(4*self.bow.height**3)

        self.weapon=self.weapon.get_from_stack()
        self.limb=self.bow.equipped[0]

        countedlimbs=[self.bow.equipped[0]]
        limblength=self.bow.equipped[0].length
        currentlimb=self.bow.equipped[0].attachpoint
        while currentlimb is not None and currentlimb not in countedlimbs:
            limblength+=currentlimb.length
            currentlimb=currentlimb.attachpoint

        max_draw_distance=min(self.bow.height*0.4,self.weapon.length-self.bow.brace,
                              60*self.power/k,limblength-self.bow.brace)
        virtual_mass=self.bow.mass/(100*self.bow.quality)
        self.energy=0.5*k*max_draw_distance*max_draw_distance
        self.caster.stamina[0]-=int(self.energy/25)+1
        self.speed=(2*self.energy/(self.weapon.mass+virtual_mass))**0.5
        self.energy=0.5*self.weapon.mass*self.speed*self.speed

        self.caster.on_ability_use(self)
        self.caster.focus[0]-=3
        self.caster.combataction=True
        self.caster.attacked=True


        #Make sure we can actually throw far enough to reach our target
        maxdistance=max(self.speed*self.speed/20-3,1)
        distance=Shell.shell.dungeonmanager.current_screen.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)
        self.time=distance/self.speed
        for i in range(0,int(distance)):
            self.energy-=0.4*self.speed**2*self.weapon.radius**2
            self.speed=(2*self.energy/self.weapon.mass)**0.5
            if self.speed<1:
                maxdistance=min(i,maxdistance)
                self.speed=0
                self.energy=0
                break
        self.time+=0.6/distance
        if maxdistance<distance:
            xy=line[min(int(maxdistance*(len(line)-1)/distance),len(line)-1)]
            self.landingcell=self.caster.floor.cells[xy[0]][xy[1]]
            line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
            if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
            #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)
            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            if self.caster==Shell.shell.player: Shell.shell.turn+=1
            return
        #If we hit a wall or similar feature, land in front of it
        if any(isinstance(i,MapTiles.DungeonFeature) and i.passable==False for i in location.dungeon):
            xy=line[lineindex-1]
            self.landingcell=self.caster.floor.cells[xy[0]][xy[1]]
            line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
            if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
            #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)

            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            if self.caster==Shell.shell.player: Shell.shell.turn+=1
            return
        elif target==None:
            self.landingcell=location
            line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
            if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
            #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)

            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            if self.caster==Shell.shell.player: Shell.shell.turn+=1
            return
        #We can hit the target! Now let's process the damage
        self.target=target
        self.basetarget=target
        self.touchedobjects=[]
        self.penetrate=False
        self.contact=True
        self.blocked=False
        self.dodged=False
        self.parried=False
        self.damage_dealt=0
        self.type='pierce'
        self.oldtype=self.type
        self.results=[]
        self.damagedobjects=[]
        self.absolute_depth_limit=self.weapon.length
        self.attacker=self.caster
        self.accuracy=accuracy
        self.arpen=0.01*self.caster.stats['tec']
        self.area=self.weapon.tip

        if self.caster==Shell.shell.player:
            if self.target.owner!=None:
                Shell.messages.append(
                "[b][size=13][color=1FAD39]You fire the {} at {}'s {}[/b][/size][/color]".format(self.weapon.name,self.target.owner.name,self.target.name))
                indent+=1
            else:
                Shell.messages.append(
                "[b][size=13][color=1FAD39]You fire the {} at the {}[/b][/size][/color]".format(self.weapon.name,self.target.name))
                indent+=1
        elif self.caster in Shell.shell.player.visible_creatures:
            if self.basetarget.owner==Shell.shell.player:
                Shell.messages.append(
                "[b][size=13][color=C21D25]{} fires a {} at your {}[/b][/size][/color]".format(self.caster.name,self.weapon.name,self.target.name))
                indent+=1
            elif self.target.owner!=None:
                Shell.messages.append("{} fires a {} at {}'s {}".format(self.caster.name,self.weapon.name,self.target.owner.name,self.target.name))
                indent+=1
            else:
                Shell.messages.append("[b][color=AD801F]{} fires a {} at {}[/b][/color]".format(self.caster.name,self.weapon.name,self.target.name))
                indent+=1

        try:
            self.blockable=1
            self.parryable=0
            self.dodgeable=1
            self.target.owner.evasion(self)
        except: pass
        if indent>0:
            Shell.messages.append(1)

        if self.blocked==True:
            Shell.messages.append("[color=7B888C]The {} was blocked with the {}[/color]".format(self.weapon.name,self.target.name))
            self.abort=True
        elif self.dodged==True:
            Shell.messages.append("[color=7B888C]The {} was dodged![/color]".format(self.weapon.name))
            self.abort=True
        else:
            self.reducedmass = self.weapon.mass * self.target.mass / (self.weapon.mass + self.target.mass)
            thickness,density=self.armor_penetration()
            self.force = self.damagefactor* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
                self.weapon.thickness / self.weapon.youngs + thickness / self.youngs)**0.25))
            self.pressure = self.force / self.area

            print("Firing bow! Force: {} N, Pressure: {} Pa, Speed: {} m/s, Energy: {} J, Time: {} s, Stiffness: {} N/m, Draw: {} m".format(
                self.force,self.pressure,self.speed,self.energy,self.time,k,max_draw_distance
            ))

        self.landingcell=location
        if not self.abort: self.target.damageresolve(self,self.caster)
        line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
        if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
            self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
        #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)

        limb_processed=False
        if not self.abort:
            for i in self.touchedobjects:
                i.on_struck(self)
                try:
                    if i in self.basetarget.layers and limb_processed==False:
                        self.basetarget.on_struck(self)
                        limb_processed=True
                except:
                    self.target.on_struck(self)
            self.weapon.on_strike(self)

        if self.caster.stats['luc']*random.random()>3:
            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
        else:
            self.landingcell.contents.append(self.weapon)
            self.weapon.in_inventory=None
            self.weapon.location=self.landingcell.location
            self.weapon.on_destruction()
            #self.landingcell.contents.remove(self.weapon)

        if alive:
            self.basetarget.owner.survivalcheck()
            if self.basetarget.owner.alive==False:
                self.caster.on_kill(self.basetarget.owner)

        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1
        if indent>0:
            Shell.messages.append(-1)
        if self.surprise:
            Shell.messages.append(-1)

    def test_usability(self):
        return True

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.speed = (2 * self.energy / self.weapon.mass) ** 0.5
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25))
        self.force = min(new, 0.9 * self.force)

    def decide(self):
        value=0
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures:
            return (0,self)
        if not any(i.grasp==True and i.equipment['grasp']==None for i in self.caster.limbs):
            return(0,self)
        if len(self.caster.equipped_items)>=len(self.caster.inventory):
            return(0,self)
        try:
            line=BaseClasses.get_line(self.caster.location,self.caster.target.location)
            line.pop(0)
            line.pop(len(line)-1)
        except:
            return(0,self)
        if any(self.caster.floor.cells[i[0]][i[1]].passable==False for i in line):
            return(0,self)
        #We have established that we have unequipped items and the means to throw them
        targetcell=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]]
        castercell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        distance=targetcell.distance_to(castercell)
        rootstrength=self.caster.stats['str']**0.5
        if distance<1.42:
            value+=0.1
        elif distance<=self.caster.stats['str']:
            value+=2*rootstrength/distance
        item_idealness=-50
        for i in self.caster.inventory:
            if i not in self.caster.equipped_items:
                new_idealness=0
                if hasattr(i,'edge'): new_idealness+=1
                if hasattr(i,'tip'): new_idealness+=1
                new_idealness+=max(1-abs(rootstrength-i.mass/2),-2)
                item_idealness=max(item_idealness,new_idealness)
                if new_idealness==item_idealness:
                    self.enemyweapon=i
        value+=item_idealness
        pref=self.caster.ai_preferences['throw']*self.caster.ai_preferences['ranged']
        value=value*pref/(value+pref)
        if 'thrower' in self.caster.classification: value*=2
        #print('throwing likelihood is ',value)
        return (value,self)

    def enemy_activation(self):
        self.throwing_limbs=[]

        for i in self.caster.limbs:
            if i.grasp==True and i.equipment['grasp']==None:
                self.throwing_limbs.append(i)
        self.weapon=self.enemyweapon
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

    def recieve_input(self,item):
        if item=='abort':
            Shell.shell.inventory.close()
            Shell.shell.keyboard_mode='play'
            Shell.shell.mouselistener(None,[0,0])
        if hasattr(item,'mass'):
            Shell.shell.inventory.close()
            Shell.shell.keyboard_mode='targeting'
            self.weapon=item
            Shell.shell.reticule=Shell.Reticule(purpose=self,highlight_type='los')
            Shell.shell.player.floor.cells[Shell.shell.player.location[0]][Shell.shell.player.location[1]].contents.append(Shell.shell.reticule)

    def armor_penetration(self):
        tec=self.caster.stats['tec']
        luc=self.caster.stats['luc']
        if hasattr(self.target,'stats'):
            dluc=self.target.stats['luc']
            dper=self.target.stats['per']
        else:
            dluc=10
            dper=10
        if hasattr(self.target,"armor") and self.target.armor is not None:
            thickness=self.target.thickness+self.target.armor.thickness
            density=self.target.armor.density
            coverage=self.target.armor.coverage-self.arpen
                #mode shifts down for higher defender luck or per. Shifts up for higher attacker tec or luck.
            mode=(tec+0.5*luc)/(2*dluc+dper)
            mode=min(mode,1)
            if random.triangular(0,1,mode)>coverage:
                #if self.target.armor.coverage*abs(random.gauss(self.target.stats['luc'],1))<random.random()*(self.limb.stats['luc']+2*self.limb.stats['tec'])/3+self.arpen:
                self.youngs=self.target.arpen_youngs
                self.shear=self.target.arpen_shear
                thickness=self.target.thickness
                density=self.target.layers[len(self.target.layers)-1].density
                self.penetrate=True
            else:
                self.youngs=self.target.youngs
                self.shear=self.target.shear
        else:
            thickness=self.target.thickness
            self.youngs=self.target.youngs
            self.shear=self.target.shear
            if hasattr(self.target,'density'):
                density=self.target.density
            elif hasattr(self.target,'layers') and self.target.layers!=[]:
                density=self.target.layers[len(self.target.layers)-1].density
            else:
                density=5000
        return (thickness,density)

class Fire_Crossbow():
    def __init__(self,caster,bow,**kwargs):
        self.caster=caster
        self.bow=bow
        self.weapon=None
        self.can_tear=False
        self.classification=['physical','ranged']
        self.attacker=caster
        self.name="Load/Fire Crossbow"

    def select_target(self):
        if self.caster==Shell.shell.player:
            if self.bow.ammo==None:
                load=Load_Crossbow(self.caster,self.bow)
                load.select_target()
                return

            Shell.shell.keyboard_mode='targeting'
            Shell.shell.reticule=Shell.Reticule(purpose=self,highlight_type='los')
            Shell.shell.player.floor.cells[Shell.shell.player.location[0]][Shell.shell.player.location[1]].contents.append(Shell.shell.reticule)


    def do(self,location=None,remove_item=True,**kwargs):
        self.abort=False
        self.damagefactor=1
        self.power=self.caster.stats['tec']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.physical_ability_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        bonus=self.power/self.caster.stats['tec']
        self.damage_severity=0
        self.surprise=False
        indent=0
        self.remove_item=remove_item
        self.killingblow=False
        resolved=False
        accuracy=2*(1+(self.caster.focus[0]*1.09**self.power)/self.caster.focus[1])*(1+(50-self.caster.tension)/200)
        while resolved==False and self.caster.passives['sharpshooter']<1:
            if accuracy<self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)*random.random():
                location=random.choice(location.immediate_neighbors)
            else:
                resolved=True



        line=BaseClasses.get_line(self.caster.location,location.location)
        #if len(line)>1: line.pop(0)
        for position in line:
            if position==line[0]: pass
            elif self.caster.floor.cells[position[0]][position[1]].passable:
                continue
            else:
                location=self.caster.floor.cells[position[0]][position[1]]
                lineindex=line.index(position)
                for i in range(lineindex+1,len(line)):
                    line.pop(len(line)-1)
                break
        strikeables=[]
        target=None
        alive=False
        for i in location.contents:
            if isinstance(i,BaseClasses.Creature) and i.alive==True:
                target=BaseClasses.targetchoice(i)
                alive=True
                break
            elif isinstance(i,BaseClasses.Item) or isinstance(i,BaseClasses.Limb):
                strikeables.append(i)
            elif isinstance(i,BaseClasses.Creature):
                strikeables.append(BaseClasses.targetchoice(i))
        if target==None and strikeables!=[]:
            target=random.choice(strikeables)


        if hasattr(target,'stats'): luc=target.stats['luc']
        else: luc=10
        k=self.bow.stiffness

        self.weapon=self.bow.ammo
        self.limb=self.bow.equipped[0]
        self.bow.ammo=None

        max_draw_distance=self.bow.length-self.bow.brace
        virtual_mass=self.bow.mass/(100*self.bow.quality)
        self.energy=0.5*k*max_draw_distance*max_draw_distance
        self.speed=(2*self.energy/(self.weapon.mass+virtual_mass))**0.5
        self.energy=0.5*self.weapon.mass*self.speed*self.speed

        self.caster.on_ability_use(self)
        self.caster.focus[0]-=3
        self.caster.combataction=True
        self.caster.attacked=True


        #Make sure we can actually throw far enough to reach our target
        maxdistance=max(self.speed*self.speed/20-3,1)
        distance=Shell.shell.dungeonmanager.current_screen.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)
        self.time=distance/self.speed
        for i in range(0,int(distance)):
            self.energy-=0.4*self.speed**2*self.weapon.radius**2
            self.speed=(2*self.energy/self.weapon.mass)**0.5
            if self.speed<1:
                maxdistance=min(i,maxdistance)
                self.speed=0
                self.energy=0
                break
        self.time+=0.5/distance
        if maxdistance<distance:
            xy=line[min(int(maxdistance*(len(line)-1)/distance),len(line)-1)]
            self.landingcell=self.caster.floor.cells[xy[0]][xy[1]]
            line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
            if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
            #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)
            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            if self.caster==Shell.shell.player: Shell.shell.turn+=1
            return
        #If we hit a wall or similar feature, land in front of it
        if any(isinstance(i,MapTiles.DungeonFeature) and i.passable==False for i in location.dungeon):
            xy=line[lineindex-1]
            self.landingcell=self.caster.floor.cells[xy[0]][xy[1]]
            line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
            if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
            #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)

            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            if self.caster==Shell.shell.player: Shell.shell.turn+=1
            return
        elif target==None:
            self.landingcell=location
            line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
            if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
                self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
            #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)

            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            if self.caster==Shell.shell.player: Shell.shell.turn+=1
            return
        #We can hit the target! Now let's process the damage
        self.target=target
        self.basetarget=target
        self.touchedobjects=[]
        self.penetrate=False
        self.contact=True
        self.blocked=False
        self.dodged=False
        self.parried=False
        self.damage_dealt=0
        self.type='pierce'
        self.oldtype=self.type
        self.results=[]
        self.damagedobjects=[]
        self.absolute_depth_limit=self.weapon.length
        self.attacker=self.caster
        self.accuracy=accuracy
        self.arpen=0.1
        self.area=self.weapon.tip

        if self.caster==Shell.shell.player:
            if self.target.owner!=None:
                Shell.messages.append(
                "[b][size=13][color=1FAD39]You fire the {} at {}'s {}[/b][/size][/color]".format(self.weapon.name,self.target.owner.name,self.target.name))
                indent+=1
            else:
                Shell.messages.append(
                "[b][size=13][color=1FAD39]You fire the {} at the {}[/b][/size][/color]".format(self.weapon.name,self.target.name))
                indent+=1
        elif self.caster in Shell.shell.player.visible_creatures:
            if self.basetarget.owner==Shell.shell.player:
                Shell.messages.append(
                "[b][size=13][color=C21D25]{} fires a {} at your {}[/b][/size][/color]".format(self.caster.name,self.weapon.name,self.target.name))
                indent+=1
            elif self.target.owner!=None:
                Shell.messages.append("{} fires a {} at {}'s {}".format(self.caster.name,self.weapon.name,self.target.owner.name,self.target.name))
                indent+=1
            else:
                Shell.messages.append("[b][color=AD801F]{} fires a {} at {}[/b][/color]".format(self.caster.name,self.weapon.name,self.target.name))
                indent+=1

        try:
            self.blockable=1
            self.parryable=0
            self.dodgeable=1
            self.target.owner.evasion(self)
        except: pass
        if indent>0:
            Shell.messages.append(1)

        if self.blocked==True:
            Shell.messages.append("[color=7B888C]The {} was blocked with the {}[/color]".format(self.weapon.name,self.target.name))
        elif self.dodged==True:
            Shell.messages.append("[color=7B888C]The {} was dodged![/color]".format(self.weapon.name))

        self.reducedmass = self.weapon.mass * self.target.mass / (self.weapon.mass + self.target.mass)
        thickness,density=self.armor_penetration()
        self.force = self.damagefactor* (self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + thickness / self.youngs)**0.25))
        self.pressure = self.force / self.area

        print("Firing bow! Force: {} N, Pressure: {} Pa, Speed: {} m/s, Energy: {} J, Time: {} s, Stiffness: {} N/m, Draw: {} m".format(
            self.force,self.pressure,self.speed,self.energy,self.time,k,max_draw_distance
        ))

        self.landingcell=location
        if not self.abort: self.target.damageresolve(self,self.caster)
        line=BaseClasses.get_line(self.caster.location,self.landingcell.location)
        if any(self.caster.floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
            self.caster.floor.animate_travel(self.weapon,self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],self.landingcell,slowness=15)
        #self.animate(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]],location)

        limb_processed=False
        if not self.abort:
            for i in self.touchedobjects:
                i.on_struck(self)
                try:
                    if i in self.basetarget.layers and limb_processed==False:
                        self.basetarget.on_struck(self)
                        limb_processed=True
                except:
                    self.target.on_struck(self)
            self.weapon.on_strike(self)

        if self.caster.stats['luc']*random.random()>3:
            Clock.schedule_once(lambda dx: self.landingcell.contents.append(self.weapon),1/6)
        else:
            self.landingcell.contents.append(self.weapon)
            self.weapon.in_inventory=None
            self.weapon.location=self.landingcell.location
            self.weapon.on_destruction()
            self.landingcell.contents.remove(self.weapon)

        if alive:
            self.basetarget.owner.survivalcheck()
            if self.basetarget.owner.alive==False:
                self.caster.on_kill(self.basetarget.owner)

        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1
        if indent>0:
            Shell.messages.append(-1)
        if self.surprise:
            Shell.messages.append(-1)

    def test_usability(self):
        return True

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.speed = (2 * self.energy / self.weapon.mass) ** 0.5
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.youngs + self.basetarget.thickness / self.youngs)**0.25))
        self.force = min(new, 0.9 * self.force)

    def decide(self):
        value=0
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures:
            return (0,self)
        if not any(i.grasp==True and i.equipment['grasp']==None for i in self.caster.limbs):
            return(0,self)
        if len(self.caster.equipped_items)>=len(self.caster.inventory):
            return(0,self)
        try:
            line=BaseClasses.get_line(self.caster.location,self.caster.target.location)
            line.pop(0)
            line.pop(len(line)-1)
        except:
            return(0,self)
        if any(self.caster.floor.cells[i[0]][i[1]].passable==False for i in line):
            return(0,self)
        #We have established that we have unequipped items and the means to throw them
        targetcell=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]]
        castercell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        distance=targetcell.distance_to(castercell)
        rootstrength=self.caster.stats['str']**0.5
        if distance<1.42:
            value+=0.1
        elif distance<=self.caster.stats['str']:
            value+=2*rootstrength/distance
        item_idealness=-50
        for i in self.caster.inventory:
            if i not in self.caster.equipped_items:
                new_idealness=0
                if hasattr(i,'edge'): new_idealness+=1
                if hasattr(i,'tip'): new_idealness+=1
                new_idealness+=max(1-abs(rootstrength-i.mass/2),-2)
                item_idealness=max(item_idealness,new_idealness)
                if new_idealness==item_idealness:
                    self.enemyweapon=i
        value+=item_idealness
        pref=self.caster.ai_preferences['throw']*self.caster.ai_preferences['ranged']
        value=value*pref/(value+pref)
        if 'thrower' in self.caster.classification: value*=2
        #print('throwing likelihood is ',value)
        return (value,self)

    def enemy_activation(self):
        self.throwing_limbs=[]

        for i in self.caster.limbs:
            if i.grasp==True and i.equipment['grasp']==None:
                self.throwing_limbs.append(i)
        self.weapon=self.enemyweapon
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

    def recieve_input(self,item):
        if item=='abort':
            Shell.shell.inventory.close()
            Shell.shell.keyboard_mode='play'
            Shell.shell.mouselistener(None,[0,0])
        if hasattr(item,'mass'):
            Shell.shell.inventory.close()
            Shell.shell.keyboard_mode='targeting'
            self.weapon=item
            Shell.shell.reticule=Shell.Reticule(purpose=self,highlight_type='los')
            Shell.shell.player.floor.cells[Shell.shell.player.location[0]][Shell.shell.player.location[1]].contents.append(Shell.shell.reticule)

    def armor_penetration(self):
        tec=self.caster.stats['tec']
        luc=self.caster.stats['luc']
        if hasattr(self.target,'stats'):
            dluc=self.target.stats['luc']
            dper=self.target.stats['per']
        else:
            dluc=10
            dper=10
        if hasattr(self.target,"armor") and self.target.armor is not None:
            thickness=self.target.thickness+self.target.armor.thickness
            density=self.target.armor.density
            coverage=self.target.armor.coverage-self.arpen
                #mode shifts down for higher defender luck or per. Shifts up for higher attacker tec or luck.
            mode=(tec+0.5*luc)/(2*dluc+dper)
            mode=min(mode,1)
            if random.triangular(0,1,mode)>coverage:
                #if self.target.armor.coverage*abs(random.gauss(self.target.stats['luc'],1))<random.random()*(self.limb.stats['luc']+2*self.limb.stats['tec'])/3+self.arpen:
                self.youngs=self.target.arpen_youngs
                self.shear=self.target.arpen_shear
                thickness=self.target.thickness
                density=self.target.layers[len(self.target.layers)-1].density
                self.penetrate=True
            else:
                self.youngs=self.target.youngs
                self.shear=self.target.shear
        else:
            thickness=self.target.thickness
            self.youngs=self.target.youngs
            self.shear=self.target.shear
            if hasattr(self.target,'density'):
                density=self.target.density
            elif hasattr(self.target,'layers') and self.target.layers!=[]:
                density=self.target.layers[len(self.target.layers)-1].density
            else:
                density=5000
        return (thickness,density)

class Load_Crossbow():
    def __init__(self,caster,bow,**kwargs):
        self.caster=caster
        self.bow=bow
        self.weapon=None
        self.can_tear=False
        self.classification=['physical','ranged']
        self.attacker=caster
        self.name="Load/Fire Crossbow"

    def select_target(self):
        if self.caster==Shell.shell.player:
            self.arrows=[]
            if self.caster.quiver!=[]:
                for i in self.caster.quiver:
                    if isinstance(i,Items.Bolt):
                        self.arrows.append(i)
                if self.arrows!=[]:
                    self.weapon=random.choice(self.arrows)
                    self.do()
                    return
            else:
                for i in self.caster.inventory:
                    if isinstance(i,Items.Bolt):
                        self.arrows.append(i)
            if self.arrows==[]:
                Shell.shell.log.addtext("You have no crossbow bolts!")
            else:
                Shell.shell.inventory.show_player_inventory(show_only=self.arrows)
                Shell.shell.keyboard_mode='item select'
                Shell.shell.keyboard_send_to=self

    def do(self,location=None,remove_item=True,**kwargs):
        self.abort=False
        self.damagefactor=1
        self.power=1
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.physical_ability_modification(self)
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        Enchantments.Defenseless(self.caster,turns=1)
        arrow=self.weapon.get_from_stack()
        self.bow.ammo=arrow
        if self.caster==Shell.shell.player:
            Shell.messages.append("[color=EB05B1][b]You load the {} in your {}[/color][/b]".format(arrow.name,self.bow.name))
        elif self.caster in Shell.shell.player.visible_creatures:
            Shell.messages.append("[color=EB05B1]{} readies its {}[/color]".format(self.caster.name,self.bow.name))
        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

    def test_usability(self):
        return True

    def decide(self):
        return (0,self)

    def enemy_activation(self):
        bolts=[]
        for i in self.caster.inventory:
            if isinstance(i,Items.Bolt):
                bolts.append(i)
        if bolts==[]:
            return
        else:
            self.weapon=random.choice(bolts)
        self.do()

    def recieve_input(self,item):
        if item=='abort':
            Shell.shell.inventory.close()
            Shell.shell.keyboard_mode='play'
            Shell.shell.mouselistener(None,[0,0])
        if hasattr(item,'mass'):
            Shell.shell.inventory.close()
            Shell.shell.keyboard_mode='targeting'
            self.weapon=item
            Shell.shell.reticule=Shell.Reticule(purpose=self,highlight_type='los')
            Shell.shell.player.floor.cells[Shell.shell.player.location[0]][Shell.shell.player.location[1]].contents.append(Shell.shell.reticule)


class Charge():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.weapon=None
        self.classification=['physical','melee','movement']
        self.name="Charge"

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self,highlight_type='los')
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        self.damagefactor=1
        self.power=self.caster.stats['str']

        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.physical_ability_modification(self)

        self.bonus=self.power/self.caster.stats['str']

        animate=False
        line=BaseClasses.get_line(self.caster.location,location.location)
        #if len(line)>1: line.pop(0)
        for position in line:
            if position==line[0]: pass
            elif self.caster.floor.cells[position[0]][position[1]].passable:
                lineindex=line.index(position)
                continue
            else:
                location=self.caster.floor.cells[position[0]][position[1]]
                lineindex=line.index(position)
                for i in range(lineindex+1,len(line)):
                    line.pop(len(line)-1)
                break
        floor=self.caster.floor
        if any(floor.cells[i[0]][i[1]] in Shell.shell.player.visible_cells for i in line):
            animate=True

        strikeables=[]
        target=None
        for i in location.contents:
            if isinstance(i,BaseClasses.Creature) and i.alive==True:
                target=i
                break
            elif isinstance(i,BaseClasses.Item) or isinstance(i,BaseClasses.Limb):
                strikeables.append(i)
        if target==None and strikeables!=[]:
            target=random.choice(strikeables)

        distance=Shell.shell.dungeonmanager.current_screen.cells[self.caster.location[0]][self.caster.location[1]].distance_to(location)
        staminacost=distance*self.caster.movemass/self.power+distance*distance
        if staminacost>self.caster.stamina[0]:
            Shell.shell.log.addtext("You don't have the stamina to make that charge")
            self.abort=True
        self.caster.updateattacks()
        if len(line)<=2:
            Shell.shell.log.addtext("You cannot charge from this close")
            self.abort=True
        elif self.caster.attacks==[]:
            Shell.shell.log.addtext("You have no enabled attacks")
            self.abort=True
        elif not any("chargeable" in i.classification for i in self.caster.attacks):
            self.abort=True
            Shell.shell.log.addtext("You have no attacks which you can charge with")

        if self.abort==False:
            if self.test_usability()==False:
                self.abort=True

        valid_attacks=[]
        for i in self.caster.attacks:
            if "chargeable" in i.classification:
                valid_attacks.append(i)
        if valid_attacks==[]: self.abort=True
        if self.abort==True:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
                return
            except:
                return
        self.caster.on_ability_use(self)
        attack=random.choice(valid_attacks)
        target_preference=self.caster.target_preference

        if target_preference=='random':
            pref='limb'
        elif target_preference=='vital organs':
            pref='vital'
        elif target_preference=='nonvital organs':
            pref='nonvital'
        elif target_preference=='attacking limbs':
            pref='attacking'
        elif target_preference=='ambulatory limbs':
            pref='moving'
        elif target_preference=='grasping limbs':
            pref='grasping'
        elif target_preference=='sensory organs':
            pref='sensory'
        elif target_preference=='balancing limbs':
            pref='balancing'

        self.chargespeed=(distance*2*self.caster.balance*self.caster.stats['str']/self.caster.movemass)**0.5

        if isinstance(target,BaseClasses.Creature):
            for i in range(0,3):
                newtarget=BaseClasses.targetchoice(target)
                if pref in newtarget.target_class:
                    break
            target=newtarget
            if self.caster.preference_enforcement==True and pref not in target.target_class:
                if not any(pref in i.target_class for i in target.limbs) and self.caster.player==True:
                    Shell.messages.append(
                        '[b][size=13][color=1FAD39]You charge in to attack,[color=7B888C] but the target does not have any limbs matching your targeting preference[/b][/size][/color][/color]')
                elif self.caster.player==True:
                    Shell.messages.append('[b][size=13][color=1FAD39]You charge in to attack,[color=7B888C] but you cannot find an opening to attack your preferred target[/b][/size][/color][/color]')
            else:
                if self.caster.player:
                    Shell.messages.append(
                        "[b][size=13][color=1FAD39]You charge {} and attack it in the {} with {}[/b][/size][/color]".format(target.owner.name,target.name,attack.name))
                elif self.caster in Shell.shell.player.visible_creatures and target.owner==Shell.shell.player:
                    Shell.messages.append(
                        "[b][size=13][color=C21D25]{} charges you and attacks your {} with {}[/b][/size][/color]".format(self.caster.name,target.name,attack.name))
                elif self.caster in Shell.shell.player.visible_creatures:
                    Shell.messages.append(
                        "[b][color=AD801F]{} charges {} and attacks the {} with {}[/b][/color]".format(self.caster.name,target.owner.name,target.name,attack.name))
                attack.do(target,parryable=0,blockable=0,call_before_evasion=self.call_before_evasion)
                if attack.initialforce>target.owner.movemass*target.owner.balance*random.random() and attack.dodged==False:
                    if 'off_balance' not in target.owner.conditions:
                        target.owner.conditions.append('off_balance')
                        Shell.messages.append("[color=1F4CAD]{} is knocked off balance![/color]".format(target.owner.name))
                elif attack.dodged==True:
                    if "off_balance" not in self.caster.conditions: self.caster.conditions.append("off_balance")
                    if self.caster==Shell.shell.player: Shell.messages.append("[color=1F4CAD]You stumble[color=7B888C] as your attack misses the target[/color][/color]")
                    elif self.caster in Shell.shell.player.visible_creatures: Shell.messages.append("[color=1F4CAD]{} stumbles as its attack misses[/color]".format(self.caster.name))
        elif target!=None:
            if self.caster.player: Shell.messages.append("[b][size=13][color=1FAD39]You rush the {} and attack with {}[/b][/size][/color]".format(target.name,attack.name))
            elif self.caster in Shell.shell.player.visible_creatures: Shell.messages.append("[b][color=AD801F]{} rushes the {} and attacks with {}[/b][/color]".format(self.caster.name,target.name,attack.name))
            attack.do(target,parryable=0,blockable=0,call_before_evasion=self.call_before_evasion)

        if self.caster in Shell.shell.player.detected_creatures:
            self.old_detected=True
        else:
            self.old_detected=False
        self.caster.stamina[0]-=staminacost
        self.caster.focus[0]-=3
        self.caster.combataction=True
        self.caster.attacked=True
        startcell=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]]
        self.startcell=startcell
        if self.caster in startcell.contents: startcell.contents.remove(self.caster)
        endcell=self.caster.floor.cells[line[lineindex-1][0]][line[lineindex-1][1]]
        self.endcell=endcell
        endcell.passable=False
        if animate==True:
            self.caster.floor.animate_travel(self.caster,startcell,endcell,slowness=15)
            Clock.schedule_once(lambda dx: endcell.contents.append(self.caster),1/5)
            self.caster.location=endcell.location
            Clock.schedule_once(lambda dx: self.wrapup(),13/60)
        else:
            endcell.contents.append(self.caster)
            self.caster.location=endcell.location
            self.wrapup()



        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode=None
        except: pass

    def test_usability(self):
        return True

    def energy_recalc(self):
        if self.energy < 0:
            self.force = 0
            self.pressure = 0
            self.energy=0
            return
        self.speed = (2 * self.energy / self.weapon.mass) ** 0.5
        if hasattr(self.basetarget,'layers'):
            density=self.basetarget.layers[len(self.basetarget.layers)-1].density
        elif hasattr(self.basetarget,'density'):
            density=self.basetarget.density
        else:
            density=5000
        new = self.damagefactor*(self.speed * (10**3) * (self.shear**0.25) * (self.reducedmass**0.75) / ((density**0.25)*(
            self.weapon.thickness / self.weapon.material.youngs + self.basetarget.thickness / self.youngs)**0.25))
        self.force = min(new, 0.9 * self.force)

    def decide(self):
        value=0
        self.caster.updateattacks()
        if self.caster.target==None or self.caster.target not in self.caster.detected_creatures:
            return (0,self)
        if not self.caster.target.alive:
            return(0,self)
        if not any('chargeable' in i.classification for i in self.caster.attacks):
            return (0,self)
        if any(self.caster.target in i.contents for i in self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]].immediate_neighbors):
            return (0,self)
        if self.caster.location==self.caster.target.location:
            return (0,self)
        distance=self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]].distance_to(
            self.caster.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])
        staminacost=distance*self.caster.movemass/self.caster.stats['str']+distance*distance
        if staminacost>self.caster.stamina[0]:
            return(0,self)
        line=BaseClasses.get_line(self.caster.location,self.caster.target.location)
        line.pop(0)
        line.pop(len(line)-1)
        if any(self.caster.floor.cells[i[0]][i[1]].passable==False for i in line):
            return (0,self)
        #We have established that we are able to charge the target
        value=1
        value-=staminacost/self.caster.stamina[0]
        pref=self.caster.ai_preferences['melee']*self.caster.ai_preferences['approach']
        value=value*pref/(value+pref)
        return (value, self)

        return (value,self)

    def enemy_activation(self):
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

    def wrapup(self,*args):
        if self.caster in self.startcell.contents: self.startcell.contents.remove(self.caster)
        self.startcell.on_contents(None,None)
        Shell.shell.player.sense_awareness()
        self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]].on_contents(None,None)
        if self.caster==Shell.shell.player:
            Shell.shell.keyboard_mode='play'
            Shell.shell.turn+=1

    def call_before_evasion(self,attack):
        if hasattr(attack,'I'):
            bodyradius=2*max(i.radius for i in self.caster.limbs)
            attack.I+=bodyradius*bodyradius*self.caster.movemass*self.bonus
        if hasattr(attack,'w'):
            attack.w+=self.chargespeed/attack.collidepoint*self.bonus
        if hasattr(attack,'speed'):
            attack.speed+=self.chargespeed*self.bonus
        if hasattr(attack,'strikemass'):
            attack.strikemass+=self.caster.movemass*self.bonus
        attack.energy+=0.5*self.caster.movemass*self.chargespeed*self.chargespeed*self.bonus
        attack.time*=0.5/self.bonus

class Grab():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.classification=['physical']
        self.name="Grab"

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self)
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        possible_limbs=[]
        self.damagefactor=1
        self.energy=10
        self.power=self.caster.stats['str']

        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.physical_ability_modification(self)
        self.bonus=self.power/self.caster.stats['str']
        if self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        for i in self.caster.limbs:
            if i.grasp==True and i.equipment['grasp']==None and i.ability>0:
                possible_limbs.append(i)
            elif 'grasping' in i.target_class and i.ability>0:
                possible_limbs.append(i)
        if location.creatures!=[] and possible_limbs!=[]:
            self.holding_limb=random.choice(possible_limbs)
            target=location.creatures[0]
            attempts=0
            limb_to_grab=BaseClasses.targetchoice(target)
            while attempts<self.caster.stats['tec'] and 'graspable' not in limb_to_grab.target_class:
                limb_to_grab=BaseClasses.targetchoice(target)
            self.target=limb_to_grab.owner
            self.held_limb=limb_to_grab
            gripsize=self.holding_limb.length
            if hasattr(self.holding_limb,'dexterity'):
                gripsize*=gripsize*self.bonus
                for i in self.holding_limb.limbs:
                    gripsize+=i.length*i.length
                gripsize=gripsize**0.5
            self.caster.stamina[0]-=self.caster.movemass/self.power
            self.time=self.caster.movemass/(self.caster.balance*self.power+0.000001)
            self.attacker=self.caster
            self.arpen=-1
            self.basetarget=self.held_limb
            self.accuracy=self.caster.stats['tec']
            self.dodged=False
            self.target.evasion(self,blockable=0,parryable=0,surprisable=0,exploitable=0)
            chance=self.target.stats['str']*self.held_limb.radius/(self.damagefactor*
                self.bonus*self.holding_limb.stats['str']*self.holding_limb.ability*gripsize*self.held_limb.length+0.01)
            if self.dodged==True:
                if self.caster==Shell.shell.player:
                    Shell.messages.append("[b][size=13][color=1FAD39]You attempt to grab {} with your {},[color=7B888C] but {} avoids the grab![/b][/size][/color][/color]".format(
                        self.target.name,self.holding_limb.name,self.target.name))
                elif self.target==Shell.shell.player:
                    Shell.messages.append("[b][size=13][color=C21D25]{} attempts to grab you with its {},[color=7B888C] but you dodge![/b][/size][/color][/color]".format(
                        self.caster.name,self.holding_limb.name))
                elif self.caster in Shell.shell.player.visible_creatures and self.target in Shell.shell.player.visible_creatures:
                    Shell.messages.apend("[b][color=AD801F]{} attempts to grab {} with its {},[color=7B888C] but the grab is avoided![/b][/color][/color]".format(
                        self.caster.name,self.target.name,self.holding_limb.name))
            elif chance<random.random():
                grasp=Enchantments.Held_In_Grasp(self.target,holding_limb=self.holding_limb,held_limb=self.held_limb)
                grasp.on_turn()
                if self.caster==Shell.shell.player:
                    Shell.messages.append("[b][size=13][color=1FAD39]You grab {}'s {} with your {}[/b][/size][/color]".format(
                        self.target.name,self.held_limb.name,self.holding_limb.name))
                elif self.target==Shell.shell.player:
                    Shell.messages.append("[b][size=13][color=C21D25]{} grabs your {} with its {}[/b][/size][/color]".format(self.caster.name,self.held_limb.name,self.holding_limb.name))
                elif self.caster in Shell.shell.player.visible_creatures and self.target in Shell.shell.player.visible_creatures:
                    Shell.messages.apend("[b][color=AD801F]{} grabs {}'s {} with its {}[/b][/color]".format(self.caster.name,self.target.name,
                                                                               self.held_limb.name,self.holding_limb.name))
            else:
                if self.caster==Shell.shell.player:
                    Shell.messages.append("[b][size=13][color=1FAD39]You attempt to grab {}'s {} with your {},[color=7B888C] but {} struggles free![/b][/size][/color][/color]".format(
                        self.target.name,self.held_limb.name,self.holding_limb.name,self.target.name))
                elif self.target==Shell.shell.player:
                    Shell.messages.append("[b][size=13][color=C21D25]{} attempts to grab your {} with its {},[color=7B888C] but you break free![/b][/size][/color][/color]".format(
                        self.caster.name,self.held_limb.name,self.holding_limb.name))
                elif self.caster in Shell.shell.player.visible_creatures and self.target in Shell.shell.player.visible_creatures:
                    Shell.messages.apend("[b][color=AD801F]{} attempts to grab {}'s {} with its {},[color=7B888C] but cannot hold fast![/b][/size][/color]".format(
                        self.caster.name,self.target.name,self.held_limb.name,self.holding_limb.name))

        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        try:
            self.target.hostilitycheck(self.caster)
            self.target.affinity[self.caster]-=1
        except:
            pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

    def decide(self):
        if self.test_usability()==False:
            return (0,self)
        value=0
        if not isinstance(self.caster.target,BaseClasses.Creature) or self.caster.hostilitycheck(self.caster.target)==False:
            return (value,self)
        if self.caster.location[0]-self.caster.target.location[0] not in [-1,0,1]:
            return (value,self)
        if self.caster.location[1]-self.caster.target.location[1] not in [-1,0,1]:
            return (value,self)
        s_adv=self.caster.stats['str']/self.caster.target.stats['str']
        value=s_adv/(2+s_adv)
        for i in self.caster.target.enchantments:
            if isinstance(i,Enchantments.Held_In_Grasp) and i.holding_limb in self.caster.limbs:
                value=value/5
        value=value*self.caster.ai_preferences['grapple']/(value+self.caster.ai_preferences['grapple'])
        return (value,self)

    def test_usability(self):
        possible_limbs=[]
        for i in self.caster.limbs:
            if i.grasp==True and i.equipment['grasp']==None and i.ability>0:
                possible_limbs.append(i)
            elif 'grasping' in i.target_class and i.ability>0:
                possible_limbs.append(i)
        if possible_limbs==[]:
            return False
        else:
            return True

    def enemy_activation(self):
        self.do(location=self.caster.target.floor.cells[self.caster.target.location[0]][self.caster.target.location[1]])

#Techniques

class Sprint():
    def __init__(self,caster,**kwargs):
        self.caster=caster
        self.classification=['physical','technique','movement']
        self.name="Sprint"

    def select_target(self):
        self.do()

    def do(self,*args,**kwargs):
        self.abort=False
        self.power=self.caster.stats['tec']
        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.technique_ability_modification(self)
        Enchantments.Sprinting(self.caster,turns=1,strength=int(self.power**0.8))

    def decide(self):
        return (0,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do()

#Divine skills must have a targetcreature attribute and have a type attribute which is 'offensive' 'defensive' or 'mixed
#Must also have a 'difficulty' attribute, with higher difficulties corresponding to greater failure rates and/or costs

class Divine_Healing():
    def __init__(self,caster):
        self.caster=caster
        self.classification=['divine','defensive','healing']
        self.type='defensive'
        self.difficulty=2
        self.alignment='L'
        self.name="Divine Healing"

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self,highlight_type='cell')
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        self.damagefactor=1
        self.power=self.caster.stats['luc']
        self.killingblow=False
        targetcell=location
        creatures=[]
        for i in location.contents:
            if isinstance(i,BaseClasses.Creature):
                creatures.append(i)
        if creatures==[]:
            Shell.shell.log.addtext("There are no creatures there to heal")
            return
        elif not any(i.alive for i in creatures):
            Shell.shell.log.addtext("It's too late for that one")
            return
        else:
            new=[]
            for i in creatures:
                if i.alive: new.append(i)
            creatures=new
        self.targetcreature=creatures[0]

        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.divine_modification(self)


        if self.test_usability()==False or self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        if self.caster==Shell.shell.player:
            if self.targetcreature==Shell.shell.player: message="[b][size=13][color=1FAD39]You beseech the gods for healing"
            else: message="[b][size=13][color=1FAD39]You ask the gods that {} be healed".format(self.targetcreature.name)
        else:
            message="[b][color=AD801F]{} mutters a prayer".format(self.caster.name)

        gods=self.caster.gods
        random.shuffle(gods)
        self.god=None
        for i in gods:
            if i.invoke(self):
                self.god=i
                break
        if self.god==None:
            if self.caster==Shell.shell.player:
                message=''.join([message,',[color=7B888C] but your prayers go unanswered.[/b][/size][/color][/color]'])
                Shell.messages.append(message)
                Shell.messages.append(1)
            elif self.caster in Shell.shell.player.visible_creatures:
                message=''.join([message,',[color=7B888C] but nothing seems to happen.[/b][/size][/color][/color]'])
                Shell.messages.append(message)
                Shell.messages.append(1)
        else:
            if self.caster==Shell.shell.player:
                message=''.join([message,'. {} answers your prayer![/b][/size][/color]'.format(self.god.name)])
                Shell.messages.append(message)
                Shell.messages.append(1)
            elif self.caster in Shell.shell.player.visible_creatures:
                message=''.join([message, ' to {}![/b][/size][/color]'.format(self.god.name)])
                Shell.messages.append(message)
                Shell.messages.append(1)

        if self.targetcreature==Shell.shell.player and self.god!=None:
            Shell.messages.append("[color=1ED6E3]You feel much better![/color]")
        elif self.targetcreature in Shell.shell.player.visible_creatures and self.god!=None:
            Shell.messages.append("[color=1ED6E3]{} looks much better![/color]".format(self.targetcreature.name))

        Shell.messages.append(0)
        self.caster.on_ability_use(self)
        fullheals=0
        if self.god!=None:
            for i in self.targetcreature.limbs:
                if i.ability<=random.random() and fullheals<=random.randint(0,self.power):
                    i.recover(fullheal=True)
                    fullheals+=1
                else: i.recover(turns=int(self.power**(1+random.random())),divine_healing=True)

        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

    def decide(self):
        if self.test_usability()==False:
            return (0,self)
        value=0
        backupfavor={}
        for i in self.caster.gods:
            backupfavor[i]=i.favor[self.caster]
        test=False
        value=self.caster.damage_level
        self.enemytarget=self.caster
        for i in self.caster.visible_creatures:
            if self.caster.hostilitycheck(i)==True:
                continue
            if self.caster.affinity[i]>0 and i.alive:
                if i.damage_level>value:
                    self.enemytarget=i
                    value=i.damage_level
        self.targetcreature=self.enemytarget
        #Test invocation. If successful, there is a good chance that this can be cast
        for i in self.caster.gods:
            test=i.invoke(self)
            if test==True: break
        for i in self.caster.gods:
            i.favor[self.caster]=backupfavor[i]
        if test==False:
            return (0,self)
        pref=self.caster.ai_preferences['heal']*self.caster.ai_preferences['divine']
        value=value*pref/(value+pref)
        return (2*value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do(location=self.caster.floor.cells[self.enemytarget.location[0]][self.enemytarget.location[1]])

class Smite():
    def __init__(self,caster):
        self.caster=caster
        self.classification=['divine','defensive','healing']
        self.type='defensive'
        self.difficulty=2
        self.alignment='L'
        self.name="Smite"

    def select_target(self):
        if self.caster==Shell.shell.player:
            shell=Shell.shell
            player=Shell.shell.player
            shell.reticule=Shell.Reticule(purpose=self,highlight_type='cell')
            shell.reticule.floor=player.floor
            shell.reticule.location=player.location
            player.floor.cells[player.location[0]][player.location[1]].contents.append(shell.reticule)
            shell.keyboard_mode='targeting'

    def do(self,location=None,**kwargs):
        self.abort=False
        self.damagefactor=1
        self.power=self.caster.stats['luc']
        indent=0
        if location.distance_to(self.caster.floor.cells[self.caster.location[0]][self.caster.location[1]])>1.5:
            Shell.shell.log.addtext("You cannot reach that target.")
            return
        elif self.caster.attacks==[]:
            Shell.shell.log.addtext("You have no enabled attacks.")
            return
        self.killingblow=False
        targetcell=location
        creatures=[]
        objects=[]
        for i in location.creatures:
            creatures.append(i)
        for i in location.items:
            objects.append(i)
        if creatures==[]:
            if objects==[]:
                Shell.shell.log.addtext("There is nothing there to strike!")
                return
            else:
                self.basetarget=random.choice(objects)
                article='the '
        else:
            self.basetarget=random.choice(creatures)
            article=''

        for i in self.caster.enchantments:
            if not self.abort:
                i.attempt_ability_use(self)
            if not self.abort:
                i.divine_modification(self)

        if self.test_usability()==False or self.abort:
            try:
                Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
                Shell.shell.reticule=None
                Shell.shell.keyboard_mode='play'
            except: pass
            return
        if self.caster==Shell.shell.player:
            message="[b][size=13][color=1FAD39]You call down divine wrath on {}{}".format(article,self.basetarget.name)
        self.targetcreature=self.basetarget


        gods=self.caster.gods
        random.shuffle(gods)
        self.god=None
        for i in gods:
            if i.invoke(self):
                self.god=i
                break
        if self.god==None:
            if self.caster==Shell.shell.player: message=''.join([message,',[/color][color=7B888C] but your prayers go unanswered.[/b][/color][/size]'])
            else: message="[color=7B888C]{} seems angry.[/color]".format(self.caster.name)
            Shell.messages.append(message)
            Shell.messages.append(1)
            indent=1
            self.caster.attack(self.basetarget)
            if self.caster==Shell.shell.player: Shell.shell.turn+=1
            return
        else:
            if self.caster==Shell.shell.player: message=''.join([message,'. You feel strengthened by the wrath of {}![/b][/color][/size]'.format(self.god.name)])
            else: message="[b][color=AD801F]{} channels the wrath of {}[/b][/color]".format(self.caster.name,self.god.name)
            Shell.messages.append(message)
            Shell.messages.append(1)
            indent=1

        weaponattacks=[]
        forces={}
        attack=None
        force=0
        for i in self.caster.attacks:
            forces[i]=i.average_values()["Average Force"]
            if "weaponless" not in i.classification:
                weaponattacks.append(i)
        for i in weaponattacks:
            if forces[i]>force:
                force=forces[i]
                attack=i
        if attack==None:
            for i in self.caster.attacks:
                if forces[i]>force:
                    force=forces[i]
                    attack=i

        self.caster.on_ability_use(self)
        target_preference=self.caster.target_preference

        if target_preference=='random':
            pref='limb'
        elif target_preference=='vital organs':
            pref='vital'
        elif target_preference=='nonvital organs':
            pref='nonvital'
        elif target_preference=='attacking limbs':
            pref='attacking'
        elif target_preference=='ambulatory limbs':
            pref='moving'
        elif target_preference=='grasping limbs':
            pref='grasping'
        elif target_preference=='sensory organs':
            pref='sensory'
        elif target_preference=='balancing limbs':
            pref='balancing'
        if isinstance(self.basetarget,BaseClasses.Creature):
            for i in range(0,self.power):
                newtarget=BaseClasses.targetchoice(self.basetarget)
                if pref in newtarget.target_class:
                    break
            target=newtarget
            if self.caster.preference_enforcement==True and pref not in target.target_class:
                if not any(pref in i.target_class for i in target.limbs) and self.caster.player==True:
                    Shell.messages.append('[color=7B888C]The target does not have any limbs matching your targeting preference[/color]')
                elif self.caster.player==True:
                    Shell.messages.append('[color=7B888C]You cannot find an opening to attack your preferred target[/color]')
            else:
                self.caster.attacked=True
                if self.caster==Shell.shell.player:
                    Shell.messages.append('[b][size=13][color=1FAD39]You attack {} in the {} with {}[/b][/color][/size]'.format(self.basetarget.name,target.name,attack.name))
                elif self.basetarget==Shell.shell.player:
                    if self.caster in self.basetarget.detected_creatures:
                        Shell.messages.append('[b][size=13][color=C21D25]{} attacks your {} with {}[/b][/color][/size]'.format(self.caster.name,target.name,attack.name))
                    else:
                        Shell.messages.append('[b][size=13][color=C21D25]Something strikes you in the {}![/b][/color][/size]'.format(target.name))
                elif self.caster in Shell.shell.player.visible_creatures:
                    if self.basetarget in Shell.shell.player.detected_creatures:
                        Shell.messages.append('[b][color=AD801F]{} attacks {} in the {} with {}[/b][/color]'.format(self.caster.name,self.basetarget.name,target.name,attack.name))
                    else:
                        Shell.messages.append('[b][color=AD801F]{} attacks something with {}[/b][/color]'.format(self.caster.name,attack.name))

        else:
            target=self.basetarget
            if self.caster==Shell.shell.player:
                Shell.messages.append("[b][size=13][color=1FAD39]You attack the {} with {}[/b][/color][/size]".format(target.name,attack.name))
            elif self.caster in Shell.shell.player.visible_creatures:
                if target in Shell.shell.player.visible_items:
                    Shell.messages.append("[b][color=AD801F]{} attacks the {} with {}[/b][/color]".format(self.caster.name,target.name,attack.name))
                else:
                    Shell.messages.append("[b][color=AD801F]{} attacks something with {}[/b][/color]".format(self.caster.name,attack.name))

        attack.do(target,parryable=0,blockable=0,dodgeable=0,call_before_evasion=self.call_before_evasion)
        if indent>0:
            Shell.messages.append(-1)

        try:
            Shell.dungeonmanager.current_screen.cells[Shell.shell.reticule.location[0]][Shell.shell.reticule.location[1]].contents.remove(Shell.shell.reticule)
            Shell.shell.reticule=None
            Shell.shell.keyboard_mode='play'
        except: pass
        if self.caster==Shell.shell.player: Shell.shell.turn+=1

    def decide(self):
        if self.test_usability()==False:
            return (0,self)
        value=0
        backupfavor={}
        for i in self.caster.gods:
            backupfavor[i]=i.favor[self.caster]
        test=False
        value=self.caster.damage_level
        self.enemytarget=self.caster
        for i in self.caster.visible_creatures:
            if self.caster.hostilitycheck(i)==True:
                continue
            if self.caster.affinity[i]>0 and i.alive:
                if i.damage_level>value:
                    self.enemytarget=i
                    value=i.damage_level
        self.targetcreature=self.enemytarget
        #Test invocation. If successful, there is a good chance that this can be cast
        for i in self.caster.gods:
            test=i.invoke(self)
            if test==True: break
        for i in self.caster.gods:
            i.favor[self.caster]=backupfavor[i]
        if test==False:
            return (0,self)
        pref=self.caster.ai_preferences['heal']*self.caster.ai_preferences['divine']
        value=value*pref/(value+pref)
        return (2*value,self)

    def test_usability(self):
        return True

    def enemy_activation(self):
        self.do(location=self.caster.floor.cells[self.enemytarget.location[0]][self.enemytarget.location[1]])

    def call_before_evasion(self,attack):
        self.god.smite_effects(self.caster,attack,self)

#Abilities not activated by creatures under normal circumstances

class Frost_Explosion():
    def __init__(self,power,**kwargs):
        self.power=power
        self.classification=['magic','ranged','elemental','debuff']
        self.name="Frost Explosion"

    def do(self,location=None,**kwargs):
        self.abort=False
        self.killingblow=False

        frosted_cells=[location]
        nextset=location.immediate_neighbors
        tested_cells=[]
        attempts=0
        probability=(1-1/self.power**0.5)**2
        ordered_frost={}
        creatures=[]
        while attempts<self.power**0.5+1:
            attempts+=1
            ordered_frost[attempts]=[]
            for i in nextset:
                if random.random()<probability**attempts:
                    if i.passable:
                        frosted_cells.append(i)
                        ordered_frost[attempts].append(i)
                        i.passable=False
                    elif i.creatures!=[]:
                        creatures.extend(i.creatures)
                elif not any(j.location==i.location for j in tested_cells):
                    tested_cells.append(i)
            nextset=[]
            for i in ordered_frost[attempts]:
                for j in i.immediate_neighbors:
                    if not any(j.location==k.location for k in tested_cells):
                        nextset.append(j)
            if nextset==[]:
                break

        for i in range(1,attempts+1):
            for j in ordered_frost[i]:
                Clock.schedule_once(functools.partial(self.add_frostwall,j,probability**0.5),15/60+i/15)

        indent=0

        for i in set(creatures):
            res=i.resistance['magic']*i.resistance['ice']*i.resistance['elemental']
            i.magic_contamination['elemental']+=1
            if self.power*random.random()>res*i.stats['luc']*random.random():
                Enchantments.Frozen_Creature(i,strength=int((1/res)*max(self.power-i.stats['luc'],0)**0.7+1))
                if i==Shell.shell.player:
                    Shell.messages.append("[color=C21D25]You are frozen solid![/color]")
                elif i in Shell.shell.player.visible_creatures:
                    Shell.messages.append("[color=1F4CAD]{} is frozen solid![/color]".format(i.name))
            else:
                limbs=[]
                creature_res=res
                for j in range(0,int(self.power**0.5+1)):
                    if self.power*random.random()<creature_res*i.stats['luc']*random.random():continue
                    newlimb=random.choice(i.limbs)
                    if newlimb not in limbs:
                        limbs.append(newlimb)
                for j in limbs:
                    res=creature_res*j.resistance['magic']*j.resistance['ice']*j.resistance['elemental']
                    Enchantments.Frozen_Limb(j,strength=int((1/res)*max(self.power-i.stats['luc'],0)**0.7+1))
                    if i==Shell.shell.player:
                        Shell.messages.append("[color=C21D25]Your {} is frozen![/color]".format(j.name))
                    elif i in Shell.shell.player.visible_creatures:
                        Shell.messages.append("[color=1F4CAD]{}'s {} is frozen solid![/color]".format(i.name,j.name))
        if indent==1:
            Shell.messages.append(-1)

    def add_frostwall(self,location=None,melt=0.9,*args,**kwargs):
        icewall=MapTiles.IceWall()
        icewall.melt_resistance=melt
        location.contents.append(icewall)



'''
    def animate(self,start,finish):
        self.animation=Shell.Widget(pos=start.pos,size=start.size)
        self.removal_point=start
        start.add_widget(self.animation)
        with self.animation.canvas.after:
            Shell.Color(self.weapon.color[0],self.weapon.color[1],self.weapon.color[2],self.weapon.color[3])
            Shell.Rectangle(pos=self.animation.pos,size=self.animation.size)
        self.k=0
        self.x_distance=finish.pos[0]-start.pos[0]
        self.y_distance=finish.pos[1]-start.pos[1]
        Clock.schedule_interval(self.travel,1/60)

    def travel(self,instance):
        self.k+=1
        self.animation.canvas.after.clear()
        with self.animation.canvas.after:
            Shell.Color(self.weapon.color[0],self.weapon.color[1],self.weapon.color[2],self.weapon.color[3])
            Shell.Rectangle(pos=[self.animation.pos[0]+self.k*self.x_distance/10,self.animation.pos[1]+self.k*self.y_distance/10],size=self.animation.size,source=self.weapon.image)
        if self.k>=10:
            self.animation.canvas.after.clear()
            Clock.unschedule(self.travel)
            self.removal_point.remove_widget(self.animation)
            if self.remove_item==True:
                try:
                    self.caster.unequip(self.weapon,log=False)
                    self.caster.inventory.remove(self.weapon)
                    self.weapon.in_inventory=None
                    self.landingcell.contents.append(self.weapon)
                except ValueError: pass
'''
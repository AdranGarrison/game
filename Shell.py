__author__ = 'Alan'

import os
import sys

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty,StringProperty,NumericProperty
import dill
import pickle
import json
import Limbs
import shelve
import Creatures
import Attacks
import Abilities
import Enchantments
import Deities
import Items
import Fluids
from Materials import *
from UI_Elements import *
from BaseClasses import Floor
from kivy.storage.jsonstore import JsonStore




os.environ['KIVY_NO_FILELOG']='true'
sys.setrecursionlimit(5000)



def picklecopy(object):
    print(object)
    try:
        return dill.loads(dill.dumps(object))
    except:
    #    print('Pickling failed!')
        return copy.deepcopy(object)





floornames=["Floor {}".format(i) for i in range(1,100)]

player=Creatures.Human(player=True,stats={'s':15,'t':15,'p':15,'w':15,'l':15},name="Sir Bugsmasher")

#This class is the total game, all the pieces put together, complete with listeners for keyboard and mouse inputs
class Shell(FloatLayout):
    playerfocus=ListProperty((0,100))
    playerstamina=ListProperty((0,100))
    exp=ListProperty((0,100))
    name=StringProperty('Sir Face')
    charlevel=NumericProperty(1)
    turn=NumericProperty(-1)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        #set up a screen manager
        self.manager=manager
        self.dungeonmanager=dungeonmanager

        self.add_widget(self.manager)
        #setting up the viewport. self.viewport is the port and self.dungeonmanager holds all the floors


        #this is the dummy floor, to be replaced by a set of real floors later
        self.floors=floors
        #floormaker(None,'dummy')
        Floor(floornames[0])
        self.dungeonmanager.current=floornames[0]
        self.playscreen=playscreen


        #placing all widgets in the playscreen
        #action bar
        self.actionbar=Buttonbar()
        playscreen.add_widget(self.actionbar)
        #minimap
        self.minimap=Minimap(pos_hint={'right':0.97,'y':0.13})
        self.playscreen.add_widget(self.minimap)
        #combat log
        #self.combatlog=Combatlog(pos_hint={'right':self.right,'top':self.top})
        self.combatlog=Combatlog(pos_hint={'right':1,'top':1})
        playscreen.add_widget(self.combatlog)
        self.log=Log()
        self.log.height=self.combatlog.height
        self.combatlog.add_widget(self.log)
        #border
        self.bottomborder=Border(pos_hint={'x':0,'y':0.1},size_hint=(1,0.03))
        playscreen.add_widget(self.bottomborder)
        self.sideborder=Border(pos_hint={'x':0.65,'y':0.13},size_hint=(0.02,0.87))
        self.playscreen.add_widget(self.sideborder)
        #focus bar
        self.focusbar=FocusBar(focus=self.playerfocus[0],maxfocus=self.playerfocus[1],size_hint=(0.12,0.02),pos_hint={'x':0.07,'y':0.14})
        self.playscreen.add_widget(self.focusbar)
        #dummy values for focus bar here
        self.playerfocus[0]=75
        self.playerfocus[1]=100
        #stamina bar
        self.staminabar=StaminaBar(stamina=self.playerstamina[0],maxstamina=self.playerstamina[1],size_hint=(0.12,0.02),pos_hint={'x':0.07,'y':0.17})
        self.playscreen.add_widget(self.staminabar)
        #dummy values for stamina bar here
        self.playerstamina[0]=110
        self.playerstamina[1]=120
        #experience bar
        self.experiencebar=ExpBar(exp=self.exp[0],nextlevel=self.exp[1],size_hint=(0.65,0.02),pos_hint={'x':0,'y':0.11})
        self.add_widget(self.experiencebar)
        #dummy values for experience bar here
        self.exp[0]+=10
        #character portrait
        self.portrait=Portrait(size_hint=(0.05,0.05),pos_hint={'x':0.01,'y':0.15})
        self.playscreen.add_widget(self.portrait)
        self.portrait.source='C:/Project/Untitled.jpg'
        self.nametag=Label(text=self.name,pos_hint={'center_x':0.1,'y':0.2},size_hint=(0.07,0.05))
        self.playscreen.add_widget(self.nametag)
        self.leveltag=Label(text='Lvl. {}'.format(self.charlevel),font_size=12,pos_hint={'center_x':0.03,'y':0.115},size_hint=(0.05,0.05))
        self.playscreen.add_widget(self.leveltag)
        #turn counter
        self.turncounter=Label(text='Turn: {}'.format(self.turn),size_hint=(0.15,0.17),pos_hint={'x':0.64,'y':0.465},
                               halign='left',valign='bottom')
        self.playscreen.add_widget(self.turncounter)
        #effect list
        self.effect_list=GridLayout(size_hint=(0.15,0.2),pos_hint={'right':0.65,'top':1},cols=1)
        self.playscreen.add_widget(self.effect_list)
        #inventory sidebar
        self.inventory=InventorySidebar(self)



        #Below are mouse and keyboard listening devices
        #setting up listener for mouse position, to correctly identify the cell to which the mouse points.
        self.mousemode='cell'
        self.mouse_circle_radius=5
        self.mouse_cone_radius=5
        Window.bind(mouse_pos=self.mouselistener)

        #setting up listener for keyboard inputs. Must have different settings for different screens.
        self.keyboard=Window.request_keyboard(self.kbclosed,self,'text')
        self.keyboard.bind(on_key_down=self.on_key_down)
        self.keyboard.bind(on_key_up=self.on_key_up)
        self.shift=False
        self.recent_shift=False
        self.keyboard_mode='play'
        self.keyboard_send_to=None

        #This MUST be set before any items can be created
        #self.playerstats={'s':15,'str':15,'t':15,'tec':15,'p':15,'per':15,'w':15,'wil':15,'l':15,'luc':15}



        player=Creatures.Human(color=(0,1,0,0.8),player=True,stats={'s':15,'t':15,'p':15,'w':15,'l':15},name="Sir Bugsmasher")
        #player=Creatures.Giant(color=(0,1,0,0.8),player=True,name="Sir Bugsmasher")
        #placing a player character
        self.player=player

        #combat log additions. For testing purposes only.

        #this is the end of the initialization

    #These functions are simple updates to focus, stamina, exp, etc.
    def on_playerfocus(self,*args,**kwargs):
        self.focusbar.max=self.playerfocus[1]
        self.focusbar.value=self.playerfocus[0]

    def on_playerstamina(self,*args,**kwargs):
        self.staminabar.max=self.playerstamina[1]
        self.staminabar.value=self.playerstamina[0]

    def on_exp(self,*args,**kwargs):
        if self.exp[0]>=self.exp[1]:
            self.charlevel+=1
            self.exp[0]-=self.exp[1]
            self.exp[1]+=50*self.charlevel
        self.experiencebar.max=self.exp[1]
        self.experiencebar.value=self.exp[0]

    def on_name(self,*args,**kwargs):
        self.nametag.text=self.name

    def on_charlevel(self,*args,**kwargs):
        self.leveltag.text='Lvl. {}'.format(self.charlevel)

    def on_turn(self,*args,**kwargs):
        oldkb=self.keyboard_mode
        #self.keyboard_mode=None
        self.playerstats=self.player.stats
        self.turncounter.text='Turn: {}'.format(self.turn)
        self.playerstamina=self.player.stamina
        self.playerfocus=self.player.focus
        for i in self.dungeonmanager.current_screen.creaturelist:
            i.on_turn()
        self.player.on_turn()
        self.post_messages()
        self.dungeonmanager.current_screen.itemlist=[]
        for i in self.dungeonmanager.current_screen.nonindexedcells:
            i.on_turn()
        self.playerstamina=self.player.stamina
        self.playerfocus=self.player.focus

        if any(isinstance(i,Creatures.Target_Dummy) for i in self.dungeonmanager.current_screen.creaturelist):
            self.player.stamina[0]=self.player.stamina[1]
            self.player.focus[0]=self.player.focus[1]

        elif random.random()>0.98:
            newcreaturetype=random.choice([Creatures.Human,Creatures.Amorphous_Horror,Creatures.Giant,
                                           Creatures.Halfling,Creatures.Fairy,Creatures.Goblin,Creatures.Blob,
                                           Creatures.Acid_Blob,Creatures.Wolf,Creatures.Dog,Creatures.Cat,Creatures.Animated_Weapon])
            creature=newcreaturetype(color=(random.random(),random.random(),random.random(),0.8))
            creature.abilities.extend([Abilities.Conjur_Weapon(creature),Abilities.Psychokinesis(creature),Abilities.Throw(creature),
                                       Abilities.Charge(creature),Abilities.Divine_Healing(creature),Abilities.Grab(creature),
                                       Abilities.Fireball(creature),Abilities.Pain(creature),Abilities.Telekinetic_Barrier(creature)])
            for i in creature.inventory:
                creature.value_item(i)
            self.dungeonmanager.current_screen.place_creature(creature)
            self.dungeonmanager.current_screen.creaturelist.append(creature)
            self.dungeonmanager.current_screen.itemlist=[]
        for i in Deities.pantheon:
            i.on_turn()
        for i in self.player.gods:
            if self.player.alive:
                pass
                #print(i.name,i.favor[self.player])
        self.dungeonmanager.current_screen.on_turn()
        self.effect_list.clear_widgets()
        enchants=[]
        for i in self.player.enchantments:
            if i.display and i.detected:
                enchants.append(i)
        self.effect_list.size_hint_y=0.03*(len(enchants)+1)
        self.effect_list.add_widget(OutlinedTextBox(text='Active Effects:'))
        for i in enchants:
            if not i.identified:
                self.effect_list.add_widget(Label(text="Unknown effect",text_size=[self.effect_list.width,0]))
            elif i.turns!='permanent':
                self.effect_list.add_widget(Label(text="{} ({})".format(i.classname,i.turns),text_size=[self.effect_list.width,0]))
            else:
                self.effect_list.add_widget(Label(text=i.classname,text_size=[self.effect_list.width,0]))
        self.keyboard_mode=oldkb

    def post_messages(self):
        message_posted=False
        while len(messages)>0:
            message=messages.pop(0)
            #print(message)
            if message==1:
                self.log.indentation_level+=1
            elif message==-1:
                self.log.indentation_level-=1
                self.log.indentation_level=max(self.log.indentation_level,0)
            elif message==0:
                self.log.indentation_level=0
            else:
                if message_posted==False:
                    self.log.addtext("[b]Turn {}:[/b]".format(self.turn),newturn=True)
                    message_posted=True

                self.log.addtext(message)
        self.log.indentation_level=0


    #These functions are related to listening devices (mouse and keyboard inputs)

    def mouselistener(self,instance,pos):
        newpos=self.dungeonmanager.to_widget(pos[0],pos[1])
        floor=self.dungeonmanager.current_screen
        targetedcell=None
        for i in range(0,floor.dimensions[0]):
            for j in range(0,floor.dimensions[1]):
                if floor.cells[i][j].collide_point(newpos[0],newpos[1]):
                    #floor.cells[i][j].highlight()
                    targetedcell=floor.cells[i][j]
                else:
                    floor.cells[i][j].unhighlight()
        if targetedcell==None:
            return
        if self.mousemode=='cell':
            targetedcell.highlight()
        if self.mousemode=='line':
            line=BaseClasses.get_line(self.player.location,targetedcell.location)
            for position in line:
                floor.cells[position[0]][position[1]].highlight()
        if self.mousemode=='los':
            color=(1,1,1,0.1)
            line=BaseClasses.get_line(self.player.location,targetedcell.location)
            if len(line)>0:line.pop(0)
            known_blockage=False
            for position in line:
                if floor.cells[position[0]][position[1]].seen_by_player==False and known_blockage==False:
                    color=(0.5,1,0,0.2)
                elif floor.cells[position[0]][position[1]].passable==False:
                    color=(1,0,0,0.1)
                    known_blockage=True
                floor.cells[position[0]][position[1]].highlight(color=color)
        if self.mousemode=='los from':
            color=(1,1,1,0.1)
            line=BaseClasses.get_line(self.highlight_start_location,targetedcell.location)
            if len(line)>0:line.pop(0)
            known_blockage=False
            for position in line:
                if floor.cells[position[0]][position[1]].seen_by_player==False and known_blockage==False:
                    color=(0.5,1,0,0.2)
                elif floor.cells[position[0]][position[1]].passable==False:
                    color=(1,0,0,0.1)
                    known_blockage=True
                floor.cells[position[0]][position[1]].highlight(color=color)
        if self.mousemode=='circle':
            color=(1,1,1,0.1)
            circle=floor.get_circle(targetedcell.location,self.mouse_circle_radius)
            for i in circle:
                i.highlight(color=color)
        if self.mousemode=='los circle':
            color=(1,1,1,0.1)
            circle=floor.get_circle(targetedcell.location,self.mouse_circle_radius,require_los=True)
            for i in circle:
                i.highlight(color=color)
        if self.mousemode=='cone':
            color=(1,1,1,0.1)
            cone=floor.get_cone(self.player.location,targetedcell.location,maxradius=self.mouse_cone_radius,require_los=False)
            for i in cone:
                i.highlight(color=color)
        if self.mousemode=='los cone':
            color=(1,1,1,0.1)
            cone=floor.get_cone(self.player.location,targetedcell.location,maxradius=self.mouse_cone_radius,require_los=True)
            for i in cone:
                i.highlight(color=color)

    def on_key_down(self,keyboard,keycode,text,modifiers):
        floor=self.dungeonmanager.current_screen
        if keycode[0]==303 or keycode[0]==304:
            self.shift=True
            self.recent_shift=True
        if self.keyboard_mode=='play':
            #The below bindings are for test/debugging purposes only, to increase or decrease important attributes
            #print('play',keycode)
            #if keycode[1]=='g' and self.shift==True:
            #    Floor(self.dungeonmanager.current+'new')
            #    self.dungeonmanager.current=self.dungeonmanager.current+'new'
            #if keycode[1]=='t' and self.shift==True:
            #    print("UNARMORED")
            #    unittestone(Items.Spear,enemy_armor=False,twohand=False)
            #
            #
            #    print("ARMORED")
            #    unittestone(Items.Spear,enemy_armor=True,twohand=True)
            #if keycode[1]=='b' and self.shift==True:
            #    for i in self.player.limbs:
            #        i.burn(1000,5)

            #The below bindings are for real
            movement=None
            if keycode[1]=='numpad7':
                movement=[-1,1]
                #self.move(self.player,[-1,1])
            elif keycode[1]=='numpad8' or keycode[1]=='up':
                movement=[0,1]
                #self.move(self.player,[0,1])
            elif keycode[1]=='numpad9':
                movement=[1,1]
                #self.move(self.player,[1,1])
            elif keycode[1]=='numpad4' or keycode[1]=='left':
                movement=[-1,0]
                #self.move(self.player,[-1,0])
            elif keycode[1]=='numpad6' or keycode[1]=='right':
                movement=[1,0]
                #self.move(self.player,[1,0])
            elif keycode[1]=='numpad1':
                movement=[-1,-1]
                #self.move(self.player,[-1,-1])
            elif keycode[1]=='numpad2' or keycode[1]=='down':
                movement=[0,-1]
                #self.move(self.player,[0,-1])
            elif keycode[1]=='numpad3':
                movement=[1,-1]
                #self.move(self.player,[1,-1])
            elif keycode[1]=='numpad5':
                movement=[0,0]
            if movement!=None:
                if self.recent_shift==False:
                    if movement==[0,0]:
                        self.turn+=1
                    else:
                        self.player.move(movement)
                else:
                    self.status_screen=AdvancedTargetingScreen(self.player,cell=self.player.floor.cells[self.player.location[0]+movement[0]][self.player.location[1]+movement[1]])
                    self.add_widget(self.status_screen)
                    self.keyboard_mode='status screen'
            if keycode[1]=='1':
                self.actionbar.button1.on_release()
            elif keycode[1]=='2':
                self.actionbar.button2.on_release()
            elif keycode[1]=='3':
                self.actionbar.button3.on_release()
            elif keycode[1]=='4':
                self.actionbar.button4.on_release()
            elif keycode[1]=='5':
                self.actionbar.button5.on_release()
            elif keycode[1]=='6':
                self.actionbar.button6.on_release()
            elif keycode[1]=='7':
                self.actionbar.button7.on_release()
            elif keycode[1]=='8':
                self.actionbar.button8.on_release()
            elif keycode[1]=='9':
                self.actionbar.button9.on_release()
            elif keycode[1]=='0':
                self.actionbar.button10.on_release()
            elif keycode[1]=='-':
                self.actionbar.button11.on_release()
            elif keycode[1]=='=':
                self.actionbar.button12.on_release()
            elif keycode[1]=='.' and self.shift==False:
                self.turn+=1
            elif keycode[1]=='.' and self.shift==True:
                for i in self.dungeonmanager.current_screen.cells[self.player.location[0]][self.player.location[1]].contents:
                    if isinstance(i,MapTiles.Downstair):
                        i.go_down(self.player)
                        self.turn+=1
                        return
            elif keycode[1]==',' and self.shift==True:
                for i in self.dungeonmanager.current_screen.cells[self.player.location[0]][self.player.location[1]].contents:
                    if isinstance(i,MapTiles.Upstair):
                        i.go_up(self.player)
                        self.turn+=1
                        return
            elif keycode[1]=='i' and self.shift==False:
                self.inventory.show_player_inventory()
                self.keyboard_mode='inventory sidebar'
                return
            elif keycode[1]==',' and self.shift==False:
                self.inventory.show_items_on_ground(self.dungeonmanager.current_screen.cells[self.player.location[0]][self.player.location[1]])
                self.keyboard_mode='item pickup'
                return
            elif keycode[1]=='d' and self.shift==False:
                self.inventory.show_player_inventory()
                self.keyboard_mode='drop'
                return
            elif keycode[1]=='w' and self.shift==False:
                self.inventory.show_player_inventory()
                self.keyboard_mode='equip'
                return
            elif keycode[1]=='r' and self.shift==False:
                self.inventory.show_player_inventory()
                self.keyboard_mode='unequip'
                return
            elif keycode[1]=='a' and self.shift==False:
                self.status_screen=StatusScreen(self.player)
                self.status_screen.attack_screen()
                self.add_widget(self.status_screen)
                self.keyboard_mode='status screen'
                return
            elif keycode[1]=='s' and self.shift==False:
                self.status_screen=StatusScreen(self.player)
                self.status_screen.creature_status()
                self.add_widget(self.status_screen)
                self.keyboard_mode='status screen'
                return
            elif keycode[1]=='l' and self.shift==False:
                Abilities.Look(self.player).select_target()
                return
            elif keycode[1]=='p' and self.shift==False:
                psychokenesis=Abilities.Psychokinesis(self.player)
                psychokenesis.select_target()
                return
            elif keycode[1]=='t' and self.shift==False:
                throw=Abilities.Throw(self.player)
                throw.select_target()
                return
            elif keycode[1]=='s' and self.shift==True:
                conjur_weapon=Abilities.Conjur_Weapon(self.player)
                conjur_weapon.select_target()
            elif keycode[1]=='c' and self.shift==False:
                charge=Abilities.Charge(self.player)
                charge.select_target()
            elif keycode[1]=='h' and self.shift==False:
                heal=Abilities.Divine_Healing(self.player)
                heal.select_target()
            elif keycode[1]=='t' and self.shift==True:
                teleport=Abilities.Controlled_Teleport(self.player)
                teleport.select_target()
            elif keycode[1]=='p' and self.shift==True:
                teleport=Abilities.Pain(self.player)
                teleport.select_target()
            elif keycode[1]=='f' and self.shift==False:
                fireball=Abilities.Fireburst(self.player,power=25)
                fireball.select_target()
            elif keycode[1]=='f' and self.shift==True:
                summon=Abilities.Summon_Familiar(self.player)
                summon.select_target()
            elif keycode[1]=='m' and self.shift==False:
                print(self.player.magic_contamination)
            elif keycode[1]=='g' and self.shift==False:
                grasp=Abilities.Psychic_Grab(self.player)
                grasp.select_target()
            elif keycode[1]=='k' and self.shift==False:
                starstorm=Abilities.Starstorm(self.player)
                starstorm.select_target()
            elif keycode[1]=='m' and self.shift==True:
                smite=Abilities.Smite(self.player)
                smite.select_target()
            elif keycode[1]=='x' and self.shift==False:
                blood=Fluids.Blood(self.player)
                blood.splatter(5,99)
                self.player.blood=[100,100]
            elif keycode[1]=='b' and self.shift==False:
                Enchantments.Berserk(self.player,turns=10)
            elif keycode[1]=='d' and self.shift==True:
                addle=Abilities.Addle(self.player)
                addle.select_target()
            elif keycode[1]=='z' and self.shift==False:
                thing=BaseClasses.Creature()
                attempt=dill.dump(thing,open('testfile.grp','wb'),protocol=4)
                pass
            elif keycode[1]=='v' and self.shift==False:
                for i in self.player.item_abilities:
                    if isinstance(i,Abilities.Fire_Bow):
                        i.select_target()
                        return
                    if isinstance(i,Abilities.Fire_Crossbow):
                        i.select_target()
                        return
            elif keycode[1]=='z' and self.shift==True:
                self.status_screen=AbilityScreen(self.player)
                self.keyboard_mode='status screen'
                self.add_widget(self.status_screen)
            elif keycode[1]=='g' and self.shift==True:
                if self.player.missing_limbs!=[]:
                    limb=random.choice(self.player.missing_limbs)
                    self.player.regrow_limb(limb)



        if self.keyboard_mode=='inventory sidebar':
            if keycode[1]=='escape':
                self.inventory.close()
                self.keyboard_mode='play'
            elif keycode[1] in 'abcdefghijklmnopqrstuvwxyz1234567890-=':
                if self.shift==False:
                    self.inventory.inspect(keycode[1])
                elif self.shift==True:
                    self.inventory.inspect(keycode[1].upper())
            elif keycode[1]==',':
                if self.inventory.showing=='inventory':
                    self.inventory.close()
                    self.inventory.show_items_on_ground(self.dungeonmanager.current_screen.cells[self.player.location[0]][self.player.location[1]])
                elif self.inventory.showing=='ground':
                    self.inventory.close()
                    self.inventory.show_player_inventory()
            elif keycode[1]=='enter':
                if self.inventory.inspected_item is not None:
                    self.inventory.inspect('enter')

        if self.keyboard_mode=='close inspect':
            self.inventory.inspectionscreen.open_submenu(keycode[1])

        if self.keyboard_mode=='item select':
            if self.keyboard_send_to==None:
                if self.shift==False: self.inventory.return_item(keycode[1])
                else: self.inventory.return_item(keycode[1].upper())
            else:
                if keycode[1]=='escape':
                    self.keyboard_send_to.recieve_input('abort')
                elif self.shift==False:
                    self.keyboard_send_to.recieve_input(self.inventory.return_item(keycode[1]))
                else:
                    self.keyboard_send_to.recieve_input(self.inventory.return_item(keycode[1].upper()))

        if self.keyboard_mode=='item pickup':
            if keycode[1]=='escape':
                self.inventory.close()
                self.keyboard_mode='play'
            elif keycode[1] in 'abcdefghijklmnopqrstuvwxyz1234567890-=':
                if self.shift==False:
                    self.inventory.select(keycode[1])
                elif self.shift==True:
                    self.inventory.select(keycode[1].upper())
            elif keycode[1]=='enter':
                self.inventory.pickup_selected(self.dungeonmanager.current_screen.cells[self.player.location[0]][self.player.location[1]])
                self.keyboard_mode='play'

        if self.keyboard_mode=='drop':
            if keycode[1]=='escape':
                self.inventory.close()
                self.keyboard_mode='play'
            elif keycode[1] in 'abcdefghijklmnopqrstuvwxyz1234567890-=':
                if self.shift==False:
                    self.inventory.select(keycode[1])
                elif self.shift==True:
                    self.inventory.select(keycode[1].upper())
            elif keycode[1]=='enter':
                self.inventory.drop_selected(self.dungeonmanager.current_screen.cells[self.player.location[0]][self.player.location[1]])
                self.keyboard_mode='play'

        if self.keyboard_mode=='equip':
            if keycode[1]=='escape':
                self.inventory.close()
                self.keyboard_mode='play'
            elif keycode[1] in 'abcdefghijklmnopqrstuvwxyz1234567890-=':
                if self.shift==False:
                    self.inventory.select(keycode[1])
                elif self.shift==True:
                    self.inventory.select(keycode[1].upper())
            elif keycode[1]=='enter':
                self.inventory.equip_selected()
                self.keyboard_mode='play'

        if self.keyboard_mode=='unequip':
            if keycode[1]=='escape':
                self.inventory.close()
                self.keyboard_mode='play'
            elif keycode[1] in 'abcdefghijklmnopqrstuvwxyz1234567890-=':
                if self.shift==False:
                    self.inventory.select(keycode[1])
                elif self.shift==True:
                    self.inventory.select(keycode[1].upper())
            elif keycode[1]=='enter':
                self.inventory.unequip_selected()
                self.keyboard_mode='play'

        if self.keyboard_mode=='status screen':
            self.status_screen.keyboard_input(keycode[1],shift=self.shift)

        if self.keyboard_mode=='pass':
            pass

        if self.keyboard_mode=='targeting':
            if keycode[1]=='escape':
                try:
                    self.reticule.purpose.cleanup()
                except:
                    pass
                try:
                    floor.cells[self.reticule.location[0]][self.reticule.location[1]].contents.remove(self.reticule)
                    self.reticule=None
                except: pass
                self.mouselistener(None,[0,0])
                self.keyboard_mode='play'
            elif keycode[1]=='numpad7':
                self.move(self.reticule,[-1,1],track=True,phasing=True)
            elif keycode[1]=='numpad8' or keycode[1]=='up':
                self.move(self.reticule,[0,1],track=True,phasing=True)
            elif keycode[1]=='numpad9':
                self.move(self.reticule,[1,1],track=True,phasing=True)
            elif keycode[1]=='numpad4' or keycode[1]=='left':
                self.move(self.reticule,[-1,0],track=True,phasing=True)
            elif keycode[1]=='numpad6' or keycode[1]=='right':
                self.move(self.reticule,[1,0],track=True,phasing=True)
            elif keycode[1]=='numpad1':
                self.move(self.reticule,[-1,-1],track=True,phasing=True)
            elif keycode[1]=='numpad2' or keycode[1]=='down':
                self.move(self.reticule,[0,-1],track=True,phasing=True)
            elif keycode[1]=='numpad3':
                self.move(self.reticule,[1,-1],track=True,phasing=True)
            elif keycode[1]=='numpad5' or keycode[1]=='.':
                self.move(self.reticule,[0,0],track=True,phasing=True)
            elif keycode[1]=='enter':
                self.reticule.do()



    def on_key_up(self,keyboard,keycode):
        if keycode[0]==303 or keycode[0]==304:
            self.shift=False
            self.recent_shift=True
            Clock.schedule_once(self.kill_shift,1/60)

    def kill_shift(self,*args,**kwargs):
        self.recent_shift=False

    #kbclosed should never be called in normal operation
    def kbclosed(self):
        #print('Uhhhh... guys... the keyboard just closed')
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard=None

    def on_keyboard_down(self,**kwargs):
        pass

    #This function handles movement of objects from cell to cell and calls for bump attacks
    def move(self,target,distance,teleport=False,mobile=True,free=False,track=False,phasing=False,force_attack=False,*args,**kwargs):
        if target==None: return
        #Make sure the cell we are trying to move to exists and is passable
        if target.location[0]+distance[0] in range(0,self.dungeonmanager.current_screen.dimensions[0]) and target.location[1]+distance[1] in range(0,self.dungeonmanager.current_screen.dimensions[1]):
            #if target==self.player: self.dungeonmanager.current_screen.cells[target.location[0]+distance[0]][target.location[1]+distance[1]].on_contents(None,None)
            cell=self.dungeonmanager.current_screen.cells[target.location[0]+distance[0]][target.location[1]+distance[1]]
            if cell.passable==True or (phasing==True and cell.creatures==[]) or isinstance(target,Reticule):

                if target in self.dungeonmanager.current_screen.cells[target.location[0]][target.location[1]].contents:
                    #print(target.location,distance)
                    if mobile==True:
                        self.dungeonmanager.current_screen.cells[target.location[0]][target.location[1]].contents.remove(target)
                        self.dungeonmanager.current_screen.cells[target.location[0]+distance[0]][target.location[1]+distance[1]].contents.append(target)
                    #print(target.location)


                    #Ensuring that the viewport tracks the player-controlled character
                    if target==self.player and free==False:
                        self.turn+=1
                    elif target==self.player:
                        self.post_messages()
                    if target==self.player or track:
                        scrollamount=viewport.convert_distance_to_scroll(cellsize,cellsize)
                        cell=self.dungeonmanager.current_screen.cells[target.location[0]][target.location[1]]
                        if viewport.width-cell.to_window(cell.pos[0],cell.pos[1])[0]<110:
                            viewport.scroll_x+=scrollamount[0]
                        if viewport.height-cell.to_window(cell.pos[0],cell.pos[1])[1]<60:
                            viewport.scroll_y+=scrollamount[1]
                        if viewport.pos[0]-cell.to_window(cell.pos[0],cell.pos[1])[0]>-80:
                            viewport.scroll_x-=scrollamount[0]
                        if viewport.pos[1]-cell.to_window(cell.pos[0],cell.pos[1])[1]>-80:
                            viewport.scroll_y-=scrollamount[1]





                elif mobile==True:
                    print('target is not where it is supposed to be')
            else:

#check to see if target is attackable and hostile. If so, attack

                attacked=False
                for i in self.dungeonmanager.current_screen.cells[target.location[0]+distance[0]][target.location[1]+distance[1]].contents:
                    if i.targetable==True and (target.hostilitycheck(i)==True or force_attack==True):
                        target.attack(i)
                        if target.player==True and free==False:
                            self.turn+=1
                        elif target.player:
                            self.post_messages()
                        attacked=True
                        break
                    elif i.targetable==True and target.hostilitycheck(i)==False and target==self.player:
                        if self.shift or force_attack:
                            target.attack(i)
                            if free:
                                self.post_messages()
                            else: self.turn+=1
                        else:
                            self.log.addtext('Do you want to attack {}?'.format(i.name))
                if attacked==False and target.player:
                    self.log.addtext('You cannot pass through here')
                    print('not passable')

        elif target==self.player:
            print("There is no cell where you are trying to move")
            self.log.addtext('Trust me, you don\'t want to go that way')

        if hasattr(self,'reticule') and target==self.reticule:
            self.highlight_start_location=self.reticule.hsl
            cell=self.dungeonmanager.current_screen.cells[target.location[0]][target.location[1]]
            self.oldmousemode=self.mousemode
            self.mousemode=self.reticule.highlight_type
            pos=cell.to_window(cell.pos[0],cell.pos[1])
            pos=[pos[0]+1,pos[1]+1]
            self.mouselistener(None,pos)
            self.mousemode=self.oldmousemode

        pass

    def populate(self):
        initialinventory=[]

        initialinventory.append(Items.Longbow(id=True))
        initialinventory.append(Items.Arrow(material=Aluminum,id=True))
        initialinventory.append(Items.Flail(material=Steel,id=True))
        initialinventory.append(Items.LongSword(material=Steel,id=True))
        initialinventory.append(Items.WarHammer(material=Steel,id=True))
        initialinventory.append(Items.Axe(material=Steel,id=True))
        initialinventory.append(Items.Spear(material=Steel,id=True))
        initialinventory.append(Items.Glove(material=Steel,id=True))
        initialinventory.append(Items.Glove(material=Steel,id=True))
        initialinventory.append(Items.Chainmail(material=Steel,id=True))
        initialinventory.append(Items.Chain_Armlet(material=Steel,id=True))
        initialinventory.append(Items.Chain_Armlet(material=Steel,id=True))
        initialinventory.append(Items.Boot(material=Steel,id=True))
        initialinventory.append(Items.Boot(material=Steel,id=True))
        initialinventory.append(Items.Helm(material=Steel,id=True))
        initialinventory.append(Items.Chain_Legging(material=Steel,id=True))
        initialinventory.append(Items.Chain_Legging(material=Steel,id=True))
        #self.player.equip(LongSword(material=Steel,id=True),log=False)
        #self.player.equip(Glove(material=Steel,id=True),log=False)
        #self.player.equip(Glove(material=Steel,id=True),log=False)
        #self.player.equip(Chest(material=Steel,id=True),log=False)
        #self.player.equip(Armlet(material=Steel,id=True),log=False)
        #self.player.equip(Armlet(material=Steel,id=True),log=False)
        #self.player.equip(Boot(material=Steel,id=True),log=False)
        #self.player.equip(Boot(material=Steel,id=True),log=False)
        #self.player.equip(Helm(material=Steel,id=True),log=False)
        #self.player.equip(Legging(material=Steel,id=True),log=False)
        #self.player.equip(Legging(material=Steel,id=True),log=False)
        self.dungeonmanager.current_screen.cells[3][3].contents.append(self.player)

        self.player.inventory.extend(initialinventory)
        self.player.inventory.extend([Items.Mace(material=Steel,id=True),Items.Knife(material=Steel,id=True)])
        self.player.inventory.extend(self.player.equipped_items)
        self.player.inventory.extend([Items.QuarterStaff()])

        self.player.disabled_attack_types.append(Attacks.Kick)
        #self.player.disabled_attack_types.append(Stab_1H)

        while any(isinstance(x,MapTiles.Wall) for x in self.dungeonmanager.current_screen.cells[self.player.location[0]][self.player.location[1]].contents):
            self.dungeonmanager.current_screen.cells[self.player.location[0]][self.player.location[1]].contents.remove(self.player)
            self.dungeonmanager.current_screen.cells[random.randint(0,self.dungeonmanager.current_screen.dimensions[0]-1)][random.randint(0,self.dungeonmanager.current_screen.dimensions[1]-1)].contents.append(self.player)
        self.player.mass_calc()

        self.playerstamina=self.player.stamina
        self.playerfocus=self.player.focus

        currentscreen=self.dungeonmanager.current_screen

        #Some objects to play around with
        currentscreen.creaturelist=[Creatures.Human(color=(1,0,0,0.8),stats={'s':15,'t':15,'p':15,'w':15,'l':15})]
        adversarymaterial=Steel

        foe=Creatures.Human(color=(0,1,0,0.8))
        #currentscreen.creaturelist.append(foe)
        adversary=currentscreen.creaturelist[0]
        adversary.disabled_attack_types=[Attacks.Slash_1H,Attacks.Stab_1H,Attacks.Kick,Attacks.Punch,Attacks.Bludgeon_1H,Attacks.Bite]

        dummyarmor=Items.Chainmail(material=adversarymaterial)

        currentscreen.creaturelist[0].equip(dummyarmor,log=False)
        currentscreen.creaturelist[0].equip(Items.Glove(material=adversarymaterial),log=False)
        currentscreen.creaturelist[0].equip(Items.Glove(material=adversarymaterial),log=False)
        currentscreen.creaturelist[0].equip(Items.Chain_Armlet(material=adversarymaterial),log=False)
        currentscreen.creaturelist[0].equip(Items.Chain_Armlet(material=adversarymaterial),log=False)
        currentscreen.creaturelist[0].equip(Items.Boot(material=adversarymaterial),log=False)
        currentscreen.creaturelist[0].equip(Items.Boot(material=adversarymaterial),log=False)
        currentscreen.creaturelist[0].equip(Items.Helm(material=adversarymaterial),log=False)
        adversary.equip(Items.LongSword(material=adversarymaterial),log=False)
        adversary.equip(Items.Mace(material=adversarymaterial),log=False)
        adversary.equip(Items.Shield(material=adversarymaterial),log=False)
        adversary.equip(Items.Buckler(material=adversarymaterial),log=False)
        adversary.equip(Items.Chain_Legging(material=adversarymaterial),log=False)
        adversary.equip(Items.Chain_Legging(material=adversarymaterial),log=False)

        for i in adversary.equipped_items:
            if i not in adversary.inventory:
                adversary.inventory.append(i)


        for i in adversary.inventory:
            i.randomize(1)
            adversary.value_item(i)


        '''
        for i in adversary.limbs:
            i.change_material(Flesh_Material,Wood)
            i.change_material(Bone_Material,Wood)
        '''


        adversary.mass_calc()
        adversary.updateattacks()


        self.dungeonmanager.current_screen.place_creature(adversary,[6,6])
        #self.dungeonmanager.current_screen.cells[6][6].contents.append(currentscreen.creaturelist[0])
        #self.dungeonmanager.current_screen.cells[8][9].contents.append(foe)
        self.dungeonmanager.current_screen.cells[7][7].contents.append(Items.LongSword())
        self.dungeonmanager.current_screen.cells[8][7].contents.append(Items.Shield())
        self.player.inventory_setup()

        wolf=Creatures.Wolf()
        currentscreen.creaturelist.append(wolf)
        currentscreen.place_creature(wolf,[10,10])

        golem=Creatures.Golem(power=10)
        currentscreen.creaturelist.append(golem)
        currentscreen.place_creature(golem,[15,15])

        animated_armor=Creatures.Phoenix()
        currentscreen.creaturelist.append(animated_armor)
        currentscreen.place_creature(animated_armor,[20,20])


        self.player.inventory_setup()
        for i in currentscreen.creaturelist:
            for j in i.inventory:
                j.generate_descriptions(per=self.player.stats['per'])
            for j in i.limbs:
                for k in j.layers:
                    k.generate_descriptions(per=self.player.stats['per'])
        for i in self.player.inventory:
            i.generate_descriptions(per=100)
        for i in self.player.limbs:
            for j in i.layers:
                j.generate_descriptions(per=100)
        for i in range(0,30):
            item=Items.weighted_generation()
            self.dungeonmanager.current_screen.place_creature(item)

        Enchantments.Psychic_Shield(self.player)


        #for i in adversary.limbs:
        #    i.add_outer_layer(Hair,Hair_Material,0.01)

        for i in self.player.inventory:
            #Enchantments.Acidic(i)
            #Enchantments.Burning(i)
            #Enchantments.Vampiric(i)
            #Enchantments.Indestructable(i)
            #Enchantments.Shifting(i)
            #Enchantments.Blinking(i)
            #Enchantments.Numbing(i)
            #Enchantments.Freezing(i)
            #Enchantments.Magic_Eating(i)
            #Fluids.Numbing_Poison(None,applied=True).add(i)
            pass
        for i in self.player.limbs:
            #Enchantments.Magical_Grasp(i)
            #Enchantments.Magical_Balance(i)
            #Enchantments.Frozen_Limb(i)
            pass
        #Enchantments.Psychic_Detection(self.player,strength=30)
        for i in currentscreen.creaturelist:
            #Enchantments.Stealth(i)
            pass
        #Enchantments.Stealth(self.player)
        #Enchantments.Psychic_Detection(self.player)
        #Enchantments.Haste(self.player)
        #Enchantments.Slow(self.player)
        #Enchantments.Sprinting(self.player,turns=3)
        self.player.abilities.extend([Abilities.Fireball(self.player),Abilities.Pain(self.player),
                                      Abilities.Charge(self.player),Abilities.Grab(self.player),
                                      Abilities.Sprint(self.player),Abilities.Divine_Healing(self.player),
                                      Abilities.Throw(self.player),Abilities.Addle(self.player),Abilities.Regrowth(self.player),
                                      Abilities.Throw_Creature(self.player),Abilities.Psychic_Throw(self.player),
                                      Abilities.Firebreath(self.player),Abilities.Frostbolt(self.player),
                                      Abilities.Invisibility(self.player)])











shell=Shell()

shell.populate()





def unittestone(weapon,armored=False,enemy_armor=False,twohand=False):
    attacker1=Creatures.Human(stats={'s':15,'t':15,'p':15,'w':15,'l':15})
    defender1=Creatures.Target_Dummy(stats={'s':15,'t':15,'p':15,'w':15,'l':15})
    attacker1.location=None
    defender1.location=None
    theweapon=weapon(material=Steel)

    if weapon!=None and twohand==False:
        attacker1.equip(weapon(material=Steel),log=False)
        attacker1.equip(weapon(material=Steel),log=False)
    elif weapon!=None and twohand==True:
        attacker1.equip(theweapon,log=False)
        attacker1.equip(theweapon,log=False)
    if armored==True:
        attacker1.equip(Items.Glove(material=Steel))
        attacker1.equip(Items.Glove(material=Steel))
        attacker1.equip(Items.Armlet(material=Steel))
        attacker1.equip(Items.Armlet(material=Steel))
        attacker1.equip(Items.Legging(material=Steel))
        attacker1.equip(Items.Legging(material=Steel))
        attacker1.equip(Items.Chest(material=Steel))
        attacker1.equip(Items.Helm(material=Steel))
        attacker1.equip(Items.Boot(material=Steel))
        attacker1.equip(Items.Boot(material=Steel))


    attacker1.disabled_attack_types=[Attacks.Kick,Attacks.Bite]
    bruising=0
    bruising_events=0
    breaking=0
    breaking_events=0
    cutting=0
    cutting_events=0
    cracking=0
    cracking_events=0
    piercing=0
    piercing_events=0
    crushing=0
    crushing_events=0
    for i in range (0,1000):
        if enemy_armor==True:
            defender1.equip(Items.Glove(material=Steel),log=False)
            defender1.equip(Items.Glove(material=Steel),log=False)
            defender1.equip(Items.Armlet(material=Steel),log=False)
            defender1.equip(Items.Armlet(material=Steel),log=False)
            defender1.equip(Items.Legging(material=Steel),log=False)
            defender1.equip(Items.Legging(material=Steel),log=False)
            defender1.equip(Items.Chest(material=Steel),log=False)
            defender1.equip(Items.Helm(material=Steel),log=False)
            defender1.equip(Items.Boot(material=Steel),log=False)
            defender1.equip(Items.Boot(material=Steel),log=False)
        if weapon!=None:
            attacker1.equip(weapon(material=Steel),log=False)
            attacker1.equip(weapon(material=Steel),log=False)
        attacker1.recover(fullheal=True)
        attacker1.attack(defender1)
        attacker1.stamina[0]=attacker1.stamina[1]
        attacker1.focus[0]=attacker1.focus[1]
        for j in defender1.limbs:
            for k in j.layers:
                if k.damage['bruise']>0:
                    bruising+=k.damage['bruise']
                    bruising_events+=1
                if k.damage['break']>0:
                    breaking+=k.damage['break']
                    breaking_events+=1
                if k.damage['cut']>0:
                    cutting+=k.damage['cut']
                    cutting_events+=1
                if k.damage['crack']>0:
                    cracking+=k.damage['crack']
                    cracking_events+=1
                if k.damage['pierce']>0:
                    piercing+=k.damage['pierce']
                    piercing_events+=1
                if k.damage['crush']>0:
                    crushing+=k.damage['crush']
                    crushing_events+=1
        defender1.reform()
    print('attacking with',weapon)
    defender1.report()
    print('total bruising:',bruising,' ({}) events'.format(bruising_events))
    print('total breaking:',breaking,' ({}) events'.format(breaking_events))
    print('total cutting:',cutting,' ({}) events'.format(cutting_events))
    print('total cracking:',cracking,' ({}) events'.format(cracking_events))
    print('total piercing:',piercing,' ({}) events'.format(piercing_events))
    print('total crushing:',crushing,' ({}) events'.format(crushing_events))



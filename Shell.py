__author__ = 'Alan'

import os
from Creatures import *
from Attacks import *
from Items import *
from Materials import *
from Limbs import *


os.environ['KIVY_NO_FILELOG']='true'

#Contained in this space are the objects which can be contained in cells


class Sword():
    def __init__(self,color=(1,1,1,1)):
        self.name='dummysword'
        self.image='C:/Project/sword.png'
        self.location=[None,None]
        self.passable=True
        self.color=color
        self.targetable=False
        self.hostile=False

        pass

class Shield():
    def __init__(self,color=(1,1,1,1)):
        self.name='dummyshield'
        self.image='c:/Project/shield.png'
        self.location=[None,None]
        self.passable=True
        self.color=color
        self.targetable=False
        self.hostile=False






player=Human(player=True,stats={'s':15,'t':15,'p':15,'w':15,'l':15},name="Sir Bugsmasher")

#This class is the total game, all the pieces put together, complete with listeners for keyboard and mouse inputs
class Shell(FloatLayout):
    playerfocus=ListProperty((0,100))
    playerstamina=ListProperty((0,100))
    exp=ListProperty((0,100))
    name=StringProperty('Sir Face')
    charlevel=NumericProperty(1)
    turn=NumericProperty(turn)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        #set up a screen manager
        self.manager=manager
        self.dungeonmanager=dungeonmanager

        self.add_widget(self.manager)
        #setting up the viewport. self.viewport is the port and self.dungeonmanager holds all the floors


        #this is the dummy floor, to be replaced by a set of real floors later
        self.floors=floors
        floormaker(None,'dummy')
        self.dungeonmanager.current='dummy'
        self.playscreen=playscreen


        #placing all widgets in the playscreen
        #action bar
        self.actionbar=Buttonbar()
        playscreen.add_widget(self.actionbar)
        #minimap
        self.minimap=Minimap(pos_hint={'right':0.97,'y':0.13})
        self.playscreen.add_widget(self.minimap)
        #combat log
        self.combatlog=Combatlog(pos_hint={'right':self.right,'top':self.top})
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




        #Below are mouse and keyboard listening devices
        #setting up listener for mouse position, to correctly identify the cell to which the mouse points.
        Window.bind(mouse_pos=self.mouselistener)

        #setting up listener for keyboard inputs. Must have different settings for different screens.
        self.keyboard=Window.request_keyboard(self.kbclosed,self,'text')
        self.keyboard.bind(on_key_down=self.on_key_down)
        self.keyboard.bind(on_key_up=self.on_key_up)
        self.shift=False



        #placing a player character
        self.player=player
        print(self.player.mass)
        self.player.equip(Mace())
        self.player.equip(LongSword())
        self.player.equip(Glove())
        self.player.equip(Glove())
        self.player.equip(Chest())
        self.player.equip(Armlet())
        self.player.equip(Armlet())
        self.player.equip(Boot())
        self.player.equip(Boot())
        self.player.equip(Helm())
        self.dungeonmanager.current_screen.cells[3][3].contents.append(self.player)




        self.playerstamina=self.player.stamina
        self.playerfocus=self.player.focus

        currentscreen=self.dungeonmanager.current_screen

        #Some objects to play around with
        currentscreen.creaturelist=[Human(color=(1,0,0,0.8),stats={'s':15,'t':15,'p':15,'w':15,'l':15})]

        dummyarmor=Chest()
        currentscreen.creaturelist[0].equip(dummyarmor)
        currentscreen.creaturelist[0].equip(Glove())
        currentscreen.creaturelist[0].equip(Glove())
        currentscreen.creaturelist[0].equip(Armlet())
        currentscreen.creaturelist[0].equip(Armlet())
        currentscreen.creaturelist[0].equip(Boot())
        currentscreen.creaturelist[0].equip(Boot())
        currentscreen.creaturelist[0].equip(Helm())


        self.dungeonmanager.current_screen.cells[6][6].contents.append(currentscreen.creaturelist[0])
        self.dungeonmanager.current_screen.cells[7][7].contents.append(Sword())
        self.dungeonmanager.current_screen.cells[8][7].contents.append(Shield())





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
        self.turncounter.text='Turn: {}'.format(self.turn)
        self.playerstamina=self.player.stamina
        self.playerfocus=self.player.focus
        for i in self.dungeonmanager.current_screen.creaturelist:
            i.on_turn()
        if len(messages)>0:
            self.log.addtext("[b]Turn {}:[/b]".format(self.turn),newturn=True)
        while len(messages)>0:
            self.log.addtext(messages.pop(0))
        for i in self.dungeonmanager.current_screen.cells:
            for j in self.dungeonmanager.current_screen.cells[i]:
                self.dungeonmanager.current_screen.cells[i][j].on_contents(None,None)
        self.player.on_turn()
        self.playerstamina=self.player.stamina
        self.playerfocus=self.player.focus




    #These functions are related to listening devices (mouse and keyboard inputs)

    def mouselistener(self,instance,pos):
        newpos=self.dungeonmanager.to_widget(pos[0],pos[1])
        floor=self.dungeonmanager.current_screen
        for i in range(0,50):
            for j in range(0,50):
                if floor.cells[i][j].collide_point(newpos[0],newpos[1]):
                    floor.cells[i][j].highlight()
                else:
                    floor.cells[i][j].unhighlight()

    def on_key_down(self,keyboard,keycode,text,modifiers):
        if keycode[0]==303 or keycode[0]==304:
            self.shift=True
        if self.manager.current=='play':
            #The below bindings are for test/debugging purposes only, to increase or decrease important attributes
            #print('play',keycode)
            if keycode[1]=='e' and self.shift==False:
                self.exp[0]+=1
            if keycode[1]=='e' and self.shift==True:
                self.exp[0]-=1
            if keycode[1]=='s' and self.shift==False:
                self.playerstamina[0]+=1
            if keycode[1]=='s' and self.shift==True:
                self.playerstamina[0]-=1
            if keycode[1]=='f' and self.shift==False:
                self.playerfocus[0]+=1
            if keycode[1]=='f' and self.shift==True:
                self.playerfocus[0]-=1
            #The below bindings are for real
            if keycode[1]=='numpad7':
                self.move(self.player,[-1,1])
            elif keycode[1]=='numpad8' or keycode[1]=='up':
                self.move(self.player,[0,1])
            elif keycode[1]=='numpad9':
                self.move(self.player,[1,1])
            elif keycode[1]=='numpad4' or keycode[1]=='left':
                self.move(self.player,[-1,0])
            elif keycode[1]=='numpad6' or keycode[1]=='right':
                self.move(self.player,[1,0])
            elif keycode[1]=='numpad1':
                self.move(self.player,[-1,-1])
            elif keycode[1]=='numpad2' or keycode[1]=='down':
                self.move(self.player,[0,-1])
            elif keycode[1]=='numpad3':
                self.move(self.player,[1,-1])
            elif keycode[1]=='numpad5' or keycode[1]=='.':
                self.turn+=1

    def on_key_up(self,keyboard,keycode):
        if keycode[0]==303 or keycode[0]==304:
            self.shift=False
    #kbclosed should never be called in normal operation
    def kbclosed(self):
        print('Uhhhh... guys... the keyboard just closed')
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard=None





    #This function handles movement of objects from cell to cell and calls for bump attacks
    def move(self,target,distance,teleport=False,mobile=True,*args,**kwargs):
        #Make sure the cell we are trying to move to exists and is passable
        if target.location[0]+distance[0] in range(0,50) and target.location[1]+distance[1] in range(0,50):

            if self.dungeonmanager.current_screen.cells[target.location[0]+distance[0]][target.location[1]+distance[1]].passable==True:

                if target in self.dungeonmanager.current_screen.cells[target.location[0]][target.location[1]].contents:
                    #print(target.location,distance)
                    if mobile==True:
                        self.dungeonmanager.current_screen.cells[target.location[0]][target.location[1]].contents.remove(target)
                        self.dungeonmanager.current_screen.cells[target.location[0]+distance[0]][target.location[1]+distance[1]].contents.append(target)
                    #print(target.location)


                    #Ensuring that the viewport tracks the player-controlled character
                    if target==self.player:
                        self.turn+=1
                        scrollamount=viewport.convert_distance_to_scroll(30,30)
                        cell=self.dungeonmanager.current_screen.cells[target.location[0]][target.location[1]]
                        if viewport.width-cell.to_window(cell.pos[0],cell.pos[1])[0]<110:
                            viewport.scroll_x+=scrollamount[0]
                        if viewport.width-cell.to_window(cell.pos[0],cell.pos[1])[1]<60:
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
                    if i.targetable==True and i.hostile==True:
                        if target.player==True:
                            target.attack(i)
                            self.turn+=1
                        else:
                            target.attack(i)
                        attacked=True
                        break
                    elif i.targetable==True and i.hostile==False:
                        self.log.addtext('Do you want to attack {}?'.format(i.name))
                if attacked==False:
                    self.log.addtext('You cannot pass through here')
                    print('not passable')

        else:
            print("There is no cell where you are trying to move")
            self.log.addtext('Trust me, you don\'t want to go that way')


        pass


shell=Shell()
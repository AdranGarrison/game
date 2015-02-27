__author__ = 'Alan'

import os


os.environ['KIVY_NO_FILELOG']='true'

import kivy
import operator
import functools
import random
kivy.require('1.8.0')
from kivy.app import EventDispatcher
from kivy.app import App
from kivy.uix.label import Label
from kivy.core.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.uix.button import Button
from kivy.effects.scroll import ScrollEffect
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty, NumericProperty,StringProperty
from kivy.graphics import Color,Rectangle,Line,ChangeState,BorderImage
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.progressbar import ProgressBar

def flatten(l,ltypes=(list,tuple)):
    ltype=type(l)
    l=list(l)
    i=0
    while i<len(l):
        while isinstance(l[i],ltypes):
            if not l[i]:
                l.pop(i)
                i-=1
                break
            else:
                l[i:i+1]=l[i]
        i+=1
    return ltype(l)


Builder.load_string('''
<Minimap@FloatLayout>:
    canvas:
        Color:
            rgba:0,0,1,0.8
        Rectangle:
            size:self.size
            pos:self.pos
    Label:
        text:'This is where the minimap goes'
        pos:root.pos

<Log@BoxLayout>
    canvas.before:
        Color:
            rgba:1,1,1,0.1
        Rectangle:
            size:self.size
            pos:self.pos


<Border@FloatLayout>
    canvas:
        Color:
            rgba:0.5,0,0.5,0.7
        Rectangle:
            size:self.size
            pos:self.pos

<FocusBar@ProgressBar>
    id:bar
    canvas:
        Color:
            rgba:0.5,0.5,0,0.4
        BorderImage:
            border:(12,1,12,1)
            pos:self.x,self.center_y
            size:self.width,10
        Color:
            rgba:1,1,0,0.8
        BorderImage:
            border:(12,1,12,1)
            pos:self.x,self.center_y
            size: self.width * (self.value/float(self.max)),10
    Label:
        markup:True
        font_size:10
        text:'[color=000000]Focus:{}/{}[/color]'.format(int(bar.value),int(bar.max))
        pos:bar.x,bar.center_y-1
        size:bar.size


<StaminaBar@ProgressBar>
    id:bar
    canvas:
        Color:
            rgba:0.5,0,0,0.4
        BorderImage:
            border:(12,1,12,1)
            pos:self.x,self.center_y
            size:self.width,10
        Color:
            rgba:1,0,0,0.8
        BorderImage:
            border:(12,1,12,1)
            pos:self.x,self.center_y
            size: self.width * (self.value/float(self.max)),10
    Label:
        markup:True
        font_size:10
        text:'[color=000000]Stamina:{}/{}[/color]'.format(int(bar.value),int(bar.max))
        pos:bar.x,bar.center_y-1
        size:bar.size

<ExpBar@ProgressBar>
    id:bar
    Label:
        markup:True
        font_size:10
        text:'[color=ffffff]Exp:{}/{}[/color]'.format(int(bar.value),int(bar.max))
        pos:(bar.x+bar.right)/2-self.width/2,(bar.y+bar.top)/2-self.height/2-5


<Portrait@Widget>
    canvas:
        Color:
            rgba:0.2,0.2,0.2,0.7
        Rectangle:
            id:graphics
            size:self.size
            pos:self.pos
            source:'C:/Project/Untitled.jpg'

<Cell@Widget>
    id:cell
    size_hint:None,None
    size:30,30
    canvas:
        Color:
            rgba:0.5,0.5,0.5,1
        Rectangle:
            id:backdrop
            size:self.size
            pos:cell.pos
        Color:
            rgba:0.1,0.1,0.1,1
        Rectangle:
            id:graphics
            size:self.width-2,self.height-2
            pos:self.x+1,self.y+1



''')

#Below are UI elements which are fixed on the screen (bars, combat log, buttons, etc)
class Buttonbar(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation='horizontal'
        self.size_hint=(1,0.1)
        self.button1=Button(text='1')
        self.button2=Button(text='2')
        self.button3=Button(text='3')
        self.button4=Button(text='4')
        self.button5=Button(text='5')
        self.button6=Button(text='6')
        self.button7=Button(text='7')
        self.button8=Button(text='8')
        self.button9=Button(text='9')
        self.button10=Button(text='10')
        self.button11=Button(text='11')
        self.button12=Button(text='12')
        self.add_widget(self.button1)
        self.add_widget(self.button2)
        self.add_widget(self.button3)
        self.add_widget(self.button4)
        self.add_widget(self.button5)
        self.add_widget(self.button6)
        self.add_widget(self.button7)
        self.add_widget(self.button8)
        self.add_widget(self.button9)
        self.add_widget(self.button10)
        self.add_widget(self.button11)
        self.add_widget(self.button12)

class Minimap(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint=(0.3,0.4)

class Combatlog(ScrollView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint=(0.33,0.43)
        self.scroll_y=0

class Log(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation='vertical'
        self.size_hint=(1,None)
        self.words=Label(text='',size_hint=(1,None),font_size=14,halign='left',valign='bottom',text_size=(self.width,None))
        self.add_widget(self.words)
        self.words.texture_update()



    def addtext(self,message,**kwargs):

        self.words.text+='\n   -'+message
        self.words.texture_update()
        self.height=self.words.texture_size[1]
        self.words.height=self.height
        self.words.texture_update()
        print(self.height,self.words.height,self.words.texture_size)
        self.bind(size=self.words.setter('text_size'))
        self.words.bind(size=self.words.setter('text_size'))

'''
    def addtext(self,message,**kwargs):
        newtext=Label(text=message,**kwargs)
        newtext.size_hint=(1,None)
        newtext.bind(size=newtext.setter('text_size'))
        newtext.font_size=14
        newtext.padding=(0,8)
        newtext.halign='left'
        newtext.valign='middle'
        newtext.text_size=(newtext.width,None)
        newtext.texture_update()
        newtext.width=newtext.texture_size[0]
        newtext.texture_size[1]=newtext.height
        newtext.texture_update()
        newtext.height=newtext.texture_size[1]/3
        #newtext.bind(size=self.resize)
        self.height+=newtext.height
        self.add_widget(newtext)
        print(newtext.height,newtext.texture_size,newtext.text_size)
'''

class Border(FloatLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

class FocusBar(ProgressBar):
    def __init__(self,focus=0,maxfocus=100,**kwargs):
        super().__init__(**kwargs)
        self.value=focus
        self.max=maxfocus

class StaminaBar(ProgressBar):
    def __init__(self,stamina=0,maxstamina=100,**kwargs):
        super().__init__(**kwargs)
        self.value=stamina
        self.max=maxstamina

class ExpBar(ProgressBar):
    def __init__(self,exp=0,nextlevel=100,**kwargs):
        super().__init__(**kwargs)
        self.max=nextlevel
        self.value=exp

class Portrait(Widget):
    source=StringProperty('C:/Project/Untitled.jpg')
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def on_source(self,*args,**kwargs):
        with self.canvas:
            Color(0.2,0.2,0.2,0.7)
            self.canvas.clear()
            self.graphics=Rectangle(source=self.source,size=self.size,pos=self.pos)


#The intention is that the Cell class will serve as a container for all creatures and items to be displayed on the screen.
#I expect to be tinkering with it quite a bit to make everything work just right.
class Cell(Widget):
    contents=ListProperty([])
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size=(30,30)
        self.passable=True
        self.highlighted=False
        self.location=[None,None]

    def highlight(self):
        if self.highlighted==False:
            self.glow=Widget(pos=self.pos,size=self.size)
            self.add_widget(self.glow)
            with self.glow.canvas:
                Color(1,1,1,0.1)
                Rectangle(size=self.glow.size,pos=self.glow.pos)
        self.highlighted=True

    def unhighlight(self):
        if self.highlighted==True:
            self.glow.canvas.clear()
            del self.glow
            self.highlighted=False

    def on_contents(self,instance,content):
        #print('Ah!!',instance,content)
        self.canvas.after.clear()
        self.passable=True
        for i in self.contents:
            i.location=self.location
            with self.canvas.after:
                if not i.color:
                    pass
                else:
                    Color(i.color[0],i.color[1],i.color[2],i.color[3])
                Rectangle(size=self.size,pos=self.pos,source=i.image)
            if i.passable==False:
                self.passable=False





#Contained in this space are the objects which can be contained in cells

class Human(Widget):
    def __init__(self,color=(1,1,1,1),name='the human',job='',named=False,hostile=True,player=False):
        self.image='C:/Project/Untitled.jpg'
        self.location=[None,None]
        self.passable=False
        self.color=color
        self.name=name+' '+job
        self.indefinitename=name.replace('the ', 'a ',1)
        self.targetable=True
        self.hostile=hostile
        self.player=player

        pass

class Sword():
    def __init__(self,color=(1,1,1,1)):
        self.image='C:/Project/sword.png'
        self.location=[None,None]
        self.passable=True
        self.color=color

        pass

class Shield():
    def __init__(self,color=(1,1,1,1)):
        self.image='c:/Project/shield.png'
        self.location=[None,None]
        self.passable=True
        self.color=color





#This class is the total game, all the pieces put together, complete with listeners for keyboard and mouse inputs
class Shell(FloatLayout):
    playerfocus=ListProperty((0,100))
    playerstamina=ListProperty((0,100))
    exp=ListProperty((0,100))
    name=StringProperty('Sir Face')
    charlevel=NumericProperty(1)
    turn=NumericProperty(0)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        #set up a screen manager
        self.manager=ScreenManager()
        self.playscreen=Screen(name='play')
        self.inventory=Screen(name='inv')
        self.talentscreen=Screen(name='talentscreen')
        self.startscreen=Screen(name='startscreen')
        self.manager.add_widget(self.playscreen)
        self.manager.add_widget(self.inventory)
        self.manager.add_widget(self.talentscreen)
        self.manager.add_widget(self.startscreen)
        self.manager.current='play'
        self.add_widget(self.manager)
        #setting up the viewport. self.viewport is the port and self.dungeonmanager holds all the floors
        self.viewport=ScrollView(size_hint=(0.65,0.87),pos_hint={'x':0,'y':0.13},scroll_x=0,scroll_y=0)
        self.viewport.effect_cls=ScrollEffect
        self.playscreen.add_widget(self.viewport)
        self.dungeonmanager=ScreenManager(size_hint=(None,None),size=(1500,1500))
        self.viewport.add_widget(self.dungeonmanager)
        #this is the dummy floor, to be replaced by a set of real floors later
        self.floors={}
        self.floormaker(self,'dummy')
        self.dungeonmanager.current='dummy'


        #placing all widgets in the playscreen
        #action bar
        self.actionbar=Buttonbar()
        self.playscreen.add_widget(self.actionbar)
        #minimap
        self.minimap=Minimap(pos_hint={'right':0.97,'y':0.13})
        self.playscreen.add_widget(self.minimap)
        #combat log
        self.combatlog=Combatlog(pos_hint={'right':self.right,'top':self.top})
        self.playscreen.add_widget(self.combatlog)
        self.log=Log()
        self.log.height=self.combatlog.height
        self.combatlog.add_widget(self.log)
        #border
        self.bottomborder=Border(pos_hint={'x':0,'y':0.1},size_hint=(1,0.03))
        self.playscreen.add_widget(self.bottomborder)
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
        self.turncounter=Label(text='Turn: {}'.format(self.turn),size_hint=(None,None),pos_hint={'x':0.64,'y':0.465})
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
        self.player=Human(player=True)
        self.dungeonmanager.current_screen.cells[3][3].contents.append(self.player)


        #Some objects to play around with
        self.dungeonmanager.current_screen.cells[6][6].contents.append(Human(color=(1,0,0,0.8)))
        self.dungeonmanager.current_screen.cells[7][7].contents.append(Sword())
        self.dungeonmanager.current_screen.cells[8][7].contents.append(Shield())





        #combat log additions. For testing purposes only.
        self.log.addtext('This is the combat log')
        self.log.addtext('This is the combat log. It is so combat-oriented, and logs a bunch of stuff! It does, however,'
                    'appear to run into itself. So I\'m making a nice long bit of text here to ensure that it works'
                    'and continues to work no matter how long I make this string. So let me tell you what I am doing.'
                    ' I\'m making a combat log. It\'s pretty cool, I suppose. Still, I have to write more to be '
                    'sure that it continues to work no matter how long the input text. I will probably never have'
                    'a single string that is as long as this in the actual game, but still, I am going for it!')
        self.log.addtext('This is the combat log')
        self.log.addtext('This is the combat log')
        self.log.addtext('This is the combat log')
        self.log.addtext('This is the combat log')
        self.log.addtext('The superman attacks you. You block! You die anyways!')
        self.log.addtext('This is the combat log')

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

    def on_key_up(self,keyboard,keycode):
        if keycode[0]==303 or keycode[0]==304:
            self.shift=False
    #kbclosed should never be called in normal operation
    def kbclosed(self):
        print('Uhhhh... guys... the keyboard just closed')
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard=None



    #This function constructs floors
    def floormaker(self,instance,inputname,*args,**kwargs):
        print('name is {}'.format(inputname))
        newfloor=Screen(name=str(inputname))
        self.floors[str(inputname)]=newfloor
        newfloor.cells={}
        for i in range(0,50):
            newfloor.cells[i]={}
            for j in range(0,50):
                newfloor.cells[i][j]=Cell(size=(30,30),pos=(i*30,j*30))
                newfloor.cells[i][j].location=[i,j]
                newfloor.add_widget(newfloor.cells[i][j])
        self.dungeonmanager.add_widget(newfloor)

    #This function handles movement of objects from cell to cell and calls for bump attacks
    def move(self,target,distance,teleport=False,*args,**kwargs):
        #Make sure the cell we are trying to move to exists and is passable
        if target.location[0]+distance[0] in range(0,50) and target.location[1]+distance[1] in range(0,50):

            if self.dungeonmanager.current_screen.cells[target.location[0]+distance[0]][target.location[1]+distance[1]].passable==True:

                if target in self.dungeonmanager.current_screen.cells[target.location[0]][target.location[1]].contents:
                    #print(target.location,distance)
                    self.dungeonmanager.current_screen.cells[target.location[0]][target.location[1]].contents.remove(target)
                    self.dungeonmanager.current_screen.cells[target.location[0]+distance[0]][target.location[1]+distance[1]].contents.append(target)
                    #print(target.location)


                    #Ensuring that the viewport tracks the player-controlled character
                    if target==self.player:
                        self.turn+=1
                        scrollamount=self.viewport.convert_distance_to_scroll(30,30)
                        cell=self.dungeonmanager.current_screen.cells[target.location[0]][target.location[1]]
                        if self.viewport.width-cell.to_window(cell.pos[0],cell.pos[1])[0]<110:
                            self.viewport.scroll_x+=scrollamount[0]
                        if self.viewport.width-cell.to_window(cell.pos[0],cell.pos[1])[1]<60:
                            self.viewport.scroll_y+=scrollamount[1]
                        if self.viewport.pos[0]-cell.to_window(cell.pos[0],cell.pos[1])[0]>-80:
                            self.viewport.scroll_x-=scrollamount[0]
                        if self.viewport.pos[1]-cell.to_window(cell.pos[0],cell.pos[1])[1]>-80:
                            self.viewport.scroll_y-=scrollamount[1]





                else:
                    print('target is not where it is supposed to be')
            else:

#check to see if target is attackable and hostile. If so, attack

                attacked=False
                for i in self.dungeonmanager.current_screen.cells[target.location[0]+distance[0]][target.location[1]+distance[1]].contents:
                    if i.targetable==True and i.hostile==True:
                        self.log.addtext('You attack {}'.format(i.name))
                        if target==self.player:
                            self.turn+=1
                        attacked=True
                        break
                    elif i.targetable==True and i.hostile==False:
                        self.log.addtext('Do you want to attack {}'.format(i.name))
                if attacked==False:
                    self.log.addtext('You cannot pass through here')
                    print('not passable')

        else:
            print("There is no cell where you are trying to move")
            self.log.addtext('Trust me, you don\'t want to go that way')


        pass





























shell=Shell()

class ActualGame(App):
    def build(self):
        return shell

if __name__=='__main__':
    ActualGame().run()

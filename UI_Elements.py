__author__ = 'Alan'

import os
import Shell

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
from kivy.config import Config

import BaseClasses
import MapTiles
import FloorGen

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

Config.set('modules','monitor','1')
Config.write()

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
    size:16,16
    ''')
'''
    canvas:
        Color:
            rgba:0.5,0.5,0.5,0.3
        Rectangle:
            id:backdrop
            size:self.size
            pos:cell.pos
        Color:
            rgba:0.1,0.1,0.1,1
        Rectangle:
            id:graphics
            size:self.width-1,self.height-1
            pos:self.x+1,self.y+1



'''

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

#TODO: Combat log needs to be more readable. Format needs to be implemented for ease of scanning to draw the eyes quickly to important pieces of information

class Log(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation='vertical'
        self.size_hint=(1,None)
        self.words=Label(text='',size_hint=(1,None),font_size=12,halign='left',valign='bottom',text_size=(self.width,None),markup=True,shorten=True,strip=True)
        self.add_widget(self.words)
        self.words.texture_update()
        self.bind(size=self.words.setter('text_size'))
        self.words.bind(size=self.words.setter('text_size'))



    def addtext(self,message,newturn=False,**kwargs):
        if len(self.words.text)>8000:
            truncatelength=len(self.words.text)-8000
            self.words.text=self.words.text[truncatelength:]
        if newturn==False:
            self.words.text="".join([self.words.text,'\n   -'+message])
  #          self.words.texture_update()
            self.height=max(self.words.texture_size[1],2000)
            self.words.height=self.height
  #          self.words.texture_update()
  #          self.bind(size=self.words.setter('text_size'))
  #          self.words.bind(size=self.words.setter('text_size'))
        else:
            self.words.text+='\n  '+message
    #        self.words.texture_update()
            self.height=max(self.words.texture_size[1],2000)
            self.words.height=self.height
   #         self.words.texture_update()
  #          self.bind(size=self.words.setter('text_size'))
   #         self.words.bind(size=self.words.setter('text_size'))


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

#TODO: Need to ensure updates to graphics only occur when the cell is visible to the player. Much work to be done.

class Cell(Widget):
    contents=ListProperty([])
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.size_hint=(None,None)
        self.size=(cellsize,cellsize)
        self.passable=True
        self.highlighted=False
        self.location=[None,None]
        self.immediate_neighbors=[]

        '''
        with self.canvas:
            Color(0.5,0.5,0.5,0.3)
            Rectangle(size=self.size,pos=self.pos)
            Color(0.1,0.1,0.1,1)
            Rectangle(size=(cellsize-1,cellsize-1),pos=(self.pos[0]+1,self.pos[1]+1))
'''


    def highlight(self):
        if self.highlighted==False:
            self.glow=Widget(pos=self.pos,size=self.size)
            self.add_widget(self.glow)
            with self.glow.canvas:
                Color(1,1,1,0.1)
                Rectangle(size=self.glow.size,pos=self.glow.pos)
        self.highlighted=True
        if self.contents!=[]: print(self.contents)
        for i in self.contents:
            if hasattr(i,'name'):
                print(i.name)
            if hasattr(i,'focus'):
                print('focus:',i.focus)
            if hasattr(i,'stamina'):
                print('stamina:',i.stamina)
            if hasattr(i,'pain'):
                print('pain:',i.pain)
            if hasattr(i,'stats'):
                print('stats:',i.stats)

    def unhighlight(self):
        if self.highlighted==True:
            self.glow.canvas.clear()
            del self.glow
            self.highlighted=False

    def on_contents(self,instance,content):
        #print('Ah!!',instance,content)
        creatures=[]
        self.canvas.after.clear()
        self.passable=True
        for i in self.contents:
            if isinstance(i,BaseClasses.Creature)==False:
                i.location=self.location
                with self.canvas.after:
                    if hasattr(i,'color')==False:
                        Color(1,1,1,1)
                    else:
                        Color(i.color[0],i.color[1],i.color[2],i.color[3])
                    Rectangle(size=self.size,pos=self.pos,source=i.image)
            else:
                creatures.append(i)
            if i.passable==False:
                self.passable=False
        for i in creatures:
            i.location=self.location
            with self.canvas.after:
                if not i.color:
                    pass
                else:
                    Color(i.color[0],i.color[1],i.color[2],i.color[3])
                Rectangle(size=self.size,pos=self.pos,source=i.image)
            if i.passable==False:
                self.passable=False

    def on_turn(self):
        pass


cellsize=16


#Screen Manager
manager=ScreenManager()
playscreen=Screen(name='play')
inventory=Screen(name='inv')
talentscreen=Screen(name='talentscreen')
startscreen=Screen(name='startscreen')
manager.add_widget(playscreen)
manager.add_widget(inventory)
manager.add_widget(talentscreen)
manager.add_widget(startscreen)
manager.current='play'


#setting up the viewport. viewport is the port and dungeonmanager holds all the floors
viewport=ScrollView(size_hint=(0.65,0.87),pos_hint={'x':0,'y':0.13},scroll_x=0,scroll_y=0)
viewport.effect_cls=ScrollEffect
playscreen.add_widget(viewport)
dungeonmanager=ScreenManager(size_hint=(None,None),size=(2000,2000))
viewport.add_widget(dungeonmanager)
turn=0


#Dictionary of floors
floors={}

#messanger list
messages=[]

'''This function constructs floors
def floormaker(instance,inputname,max_x=60,max_y=60,*args,**kwargs):
    print('name is {}'.format(inputname))
    newfloor=Screen(name=str(inputname))
    floors[str(inputname)]=newfloor
    newfloor.cells={}
    newfloor.dimensions=[max_x,max_y]
    newfloor.nonindexedcells=[]
    newfloor.creaturelist=[]
    for i in range(0,max_x):
        newfloor.cells[i]={}
        for j in range(0,max_y):
            newfloor.cells[i][j]=Cell(size=(cellsize,cellsize),pos=(i*cellsize,j*cellsize))
            newfloor.cells[i][j].location=[i,j]
            newfloor.cells[i][j].open=False
            newfloor.cells[i][j].probability=0
            newfloor.add_widget(newfloor.cells[i][j])
            newfloor.nonindexedcells.append(newfloor.cells[i][j])
    dungeonmanager.add_widget(newfloor)
    dungeonmanager.size=(max_x*cellsize+1,max_y*cellsize+1)
    for i in range(0,max_x):
        for j in range(0,max_y):
            newfloor.cells[i][j].immediate_neighbors=[]

#stuff to the right
            if i+1 in range (0,max_x):
                if j+1 in range (0,max_y):
                    newfloor.cells[i][j].immediate_neighbors.append(newfloor.cells[i+1][j+1])
                newfloor.cells[i][j].immediate_neighbors.append(newfloor.cells[i+1][j])
                if j-1 in range(0,max_y):
                    newfloor.cells[i][j].immediate_neighbors.append(newfloor.cells[i+1][j-1])
#stuff to the left
            if i-1 in range(0,max_x):
                newfloor.cells[i][j].immediate_neighbors.append(newfloor.cells[i-1][j])
                if j+1 in range (0,max_y):
                    newfloor.cells[i][j].immediate_neighbors.append(newfloor.cells[i-1][j+1])
                if j-1 in range(0,max_y):
                    newfloor.cells[i][j].immediate_neighbors.append(newfloor.cells[i-1][j-1])
#straight above
            if j+1 in range(0,max_y):
                newfloor.cells[i][j].immediate_neighbors.append(newfloor.cells[i][j+1])
#and straight below
            if j-1 in range(0,max_y):
                newfloor.cells[i][j].immediate_neighbors.append(newfloor.cells[i][j-1])
#And now next-nearest neighbors (with corners. May want to remove)
    for i in newfloor.nonindexedcells:
        i.second_order_neighbors=[]
        for j in i.immediate_neighbors:
            i.second_order_neighbors.extend(j.immediate_neighbors)
        i.second_order_neighbors=set(i.second_order_neighbors)-set(i.immediate_neighbors)- {i}

    FloorGen.experimental_automaton(newfloor)
    for i in newfloor.nonindexedcells:
        i.on_contents(None,None)
'''





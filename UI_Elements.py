__author__ = 'Alan'

import os
import Shell

os.environ['KIVY_NO_FILELOG']='true'

import kivy
import operator
import functools
import random
import copy
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
from kivy.uix.behaviors import ButtonBehavior

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
Config.set('kivy', 'exit_on_escape', 0)
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


<ItemGraphic@Widget>
    canvas:
        Color:
            rgba:self.color[0],self.color[1],self.color[2],self.color[3]
        Rectangle:
            id:graphics
            size:self.height*0.8,self.height*0.8
            pos:self.center_x-self.height*0.4,self.y
            source:self.source


<OutlinedTextBox@Label>
    background:(0,0,0,1)
    outline:(0,0,0,1)
    text_size:self.size
    shorten:True
    halign:'center'
    valign:'middle'
    markup:True
    canvas.before:
        Color:
            rgba:self.outline[0],self.outline[1],self.outline[2],self.outline[3]
        Rectangle:
            pos:self.x,self.y
            size:self.width,self.height
        Color:
            rgba: self.background[0],self.background[1],self.background[2],self.background[3]
        Rectangle:
            pos:self.x+1,self.y+1
            size:self.width-2,self.height-2

<DisplayBox@FloatLayout>
    background:(0,0,0,1)
    outline:(0,0,0,1)
    canvas.before:
        Color:
            rgba:self.outline[0],self.outline[1],self.outline[2],self.outline[3]
        Rectangle:
            pos:self.x,self.y
            size:self.width,self.height
        Color:
            rgba: self.background[0],self.background[1],self.background[2],self.background[3]
        Rectangle:
            pos:self.x+1,self.y+1
            size:self.width-2,self.height-2
    Label:
        id:title
        font_size:12
        bold:True
        color:.6,.6,.6,.6
        text:root.titletext
        text_size:self.size
        shorten:True
        halign:'left'
        valign:'top'
        markup:True
        pos:root.x+1,root.y+root.height-self.height+1
    Label:
        id:information
        text:root.info
        text_size:self.size
        shorten:True
        halign:'right'
        valign:'middle'
        markup:True
        pos:root.x-2,root.y-2


<NoteBox@FloatLayout>
    background:(0,0,0,1)
    outline:(0,0,0,1)
    canvas.before:
        Color:
            rgba:self.outline[0],self.outline[1],self.outline[2],self.outline[3]
        Rectangle:
            pos:self.x,self.y
            size:self.width,self.height
        Color:
            rgba: self.background[0],self.background[1],self.background[2],self.background[3]
        Rectangle:
            pos:self.x+1,self.y+1
            size:self.width-2,self.height-2
    TextInput:
        id:information
        multiline:False
        text:root.info
        text_size:self.size
        foreground_color: 1,1,1,1
        shorten:True
        halign:'right'
        valign:'middle'
        markup:True
        pos:root.x,root.y
        padding:3,10,0,0
    Label:
        id:title
        font_size:12
        bold:True
        color:.6,.6,.6,.6
        text:root.titletext
        text_size:self.size
        shorten:True
        halign:'left'
        valign:'top'
        markup:True
        pos:root.x+1,root.y+root.height-self.height+1


<ItemDescription@FloatLayout>
    damage:''
    canvas.before:
        Color:
            rgba: 0.2,0.2,0.2,0.95
        Rectangle:
            id: backdrop
            size:self.width,self.height
            pos:self.pos
        Color:
            rgba: 0,0,0,1
        Rectangle:
            size:0.05*self.width,0.05*self.height
            pos: self.x+10,self.y+0.95*self.height-10
        Color:
            rgba: 0,0,0,1
        Rectangle:
            size:0.05*self.width-2,0.05*self.height-2
            pos: self.x+11,self.y+0.95*self.height-9
        Color:
            rgba: self.item.color[0],self.item.color[1],self.item.color[2],self.item.color[3]
        Rectangle:
            size:0.05*self.width,0.05*self.height
            pos: self.x+10,self.y+0.95*self.height-10
            source:self.item.image
    OutlinedTextBox:
        shorten:True
        halign:'left'
        font_size:18
        text: '[b]      '+root.item.name+': '
        size_hint:(root.width*0.95-30)/root.width,(root.height*0.05+10)/root.height
        text_size: root.width*0.9,root.height*0.05
        size: self.texture_size
        pos:root.x+0.08*root.width,root.y+0.95*root.height-20
    OutlinedTextBox:
        text:root.item.descriptor
        text_size:root.width-20,root.height*0.05
        size:self.texture_size
        size_hint:(root.width-20)/root.width,0.1
        pos:root.x+10,root.y+0.85*root.height-20
    OutlinedTextBox:
        id:damagebox
        text:root.damage
        text_size:root.width-20,root.height*0.1
        size:self.texture_size
        size_hint: (root.width-20)/root.width,0.2
        pos:root.x+10,root.y+0.65*root.height-30
        Label:
            color:.6,.6,.6,.6
            markup:True
            halign:'left'
            valign:'top'
            size:self.texture_size
            font_size:18
            text:'[b]Damage:[/b]'
            pos:damagebox.x,damagebox.y+damagebox.height-self.height
    GridLayout:
        id:infobox1
        cols:1
        pos:root.x+10,root.y+10+0.1*root.height
        size_hint:(0.5*root.width-15)/root.width,(root.height*0.55-50)/root.height
        canvas.before:
            Color:
                rgba:0,0,0,1
            Rectangle:
                pos:self.pos
                size:self.size
    GridLayout:
        id:infobox2
        cols:1
        pos:root.x+0.5*root.width+5,root.y+10+0.1*root.height
        size_hint:(0.5*root.width-15)/root.width,(root.height*0.55-50)/root.height
        canvas.before:
            Color:
                rgba:0,0,0,1
            Rectangle:
                pos:self.pos
                size:self.size
    OutlinedTextBox:
        id:instructions
        pos:root.x+10,root.y+10
        size_hint:(root.width-20)/root.width,(root.height*0.1-10)/root.height
        text:'Press[b][color=ffff00] Enter[/color][/b] for further options'

<AttackDescription@FloatLayout>
    canvas.before:
        Color:
            rgba: 0.2,0.2,0.2,0.95
        Rectangle:
            id: backdrop
            size: self.width,self.height
            pos: self.pos
    GridLayout:
        cols: 7
        id: titles
        size_hint: (root.width-20)/root.width,(0.2*root.height-10)/root.height
        pos: root.x+10,root.y+root.height-self.height-15
        OutlinedTextBox:
            outline:1,0,0,1
            text:'Attack Name'
        OutlinedTextBox:
            outline:1,0,0,1
            text:'Damage Type'
            size: self.texture_size
        OutlinedTextBox:
            outline:1,0,0,1
            text:'Execution Time'
            size: self.texture_size
        OutlinedTextBox:
            outline:1,0,0,1
            text:'Strike Length'
            size: self.texture_size
        OutlinedTextBox:
            outline:1,0,0,1
            text:'Average Force'
            size: self.texture_size
        OutlinedTextBox:
            outline:1,0,0,1
            text:'Average Pressure'
            size: self.texture_size
        OutlinedTextBox:
            outline:1,0,0,1
            text:'Stamina Cost'
            size: self.texture_size
    ScrollView:
        size_hint:(root.width-20)/root.width,(0.8*root.height-20)/root.height
        pos:root.x+10,root.y+10
        GridLayout:
            cols:7
            id:attackinfo
            size_hint:1,50*len(self.children)/(7*root.height)
            pos:root.x+10,root.y+10
            row_default_height:50

<AttackManagementScreen@FloatLayout>
    size_hint:0.65,0.87
    pos_hint_x:0
    pos_hint_y:0.13
    canvas.before:
        Color:
            rgba: 0.2,0.2,0.2,0.95
        Rectangle:
            id: backdrop
            size: self.width,self.height
            pos: self.pos
    FloatLayout:
        id:attackwindow
        pos:root.x,root.y
        size_hint:1,0.5
        GridLayout:
            cols: 9
            id: titles
            size_hint: (attackwindow.width-20)/attackwindow.width,(0.1*attackwindow.height-10)/attackwindow.height
            pos: attackwindow.x+10,attackwindow.y+attackwindow.height-self.height-10
            OutlinedTextBox:
                outline:1,0,0,1
                text:'index'
            OutlinedTextBox:
                outline:1,0,0,1
                text:'Attack Name'
                size_hint_y:0.5
            OutlinedTextBox:
                outline:1,0,0,1
                text:'Weapon'
            OutlinedTextBox:
                outline:1,0,0,1
                text:'Damage Type'
                size: self.texture_size
            OutlinedTextBox:
                outline:1,0,0,1
                text:'Execution Time'
                size: self.texture_size
            OutlinedTextBox:
                outline:1,0,0,1
                text:'Strike Length'
                size: self.texture_size
            OutlinedTextBox:
                outline:1,0,0,1
                text:'Average Force'
                size: self.texture_size
            OutlinedTextBox:
                outline:1,0,0,1
                text:'Average Pressure'
                size: self.texture_size
            OutlinedTextBox:
                outline:1,0,0,1
                text:'Stamina Cost'
                size: self.texture_size
        ScrollView:
            id:attackscroll
            size_hint:1,(0.9*attackwindow.height-20)/attackwindow.height
            pos:attackwindow.x,attackwindow.y
            GridLayout:
                id:attacks
                cols:1
                size_hint:1,50*len(self.children)/(attackscroll.height)
                row_default_height:50
    FloatLayout:
        id:typewindow
        pos:root.x,root.y+0.5*root.height
        size_hint:0.5,0.5
        OutlinedTextBox:
            outline:1,0,0,1
            text:'Disable/Enable attacks by type'
            size_hint:(typewindow.width-20)/typewindow.width,(0.2*typewindow.height-20)/typewindow.height
            pos:typewindow.x+10,typewindow.y+typewindow.height-self.height-10
        ScrollView:
            id:typescroll
            size_hint:(typewindow.width-20)/typewindow.width,(0.8*typewindow.height-20)/typewindow.height
            pos:typewindow.x+10,typewindow.y+10
            GridLayout:
                id:types
                cols:1
                size_hint:1,50*len(self.children)/typescroll.height
    FloatLayout:
        id:prefwindow
        pos:root.x+0.5*root.width,root.y+0.5*root.height
        size_hint:0.5,0.5
        OutlinedTextBox:
            outline:1,0,0,1
            text:'Target Preference'
            size_hint:(prefwindow.width-20)/prefwindow.width,(0.2*prefwindow.height-20)/prefwindow.height
            pos:prefwindow.x+10,prefwindow.y+prefwindow.height-self.height-10
        ScrollView:
            id:prefscroll
            size_hint:(prefwindow.width-20)/prefwindow.width,(0.75*prefwindow.height-20)/prefwindow.height
            pos:prefwindow.x+10,prefwindow.y+10+0.05*prefwindow.height
            GridLayout:
                id:prefs
                cols:1
                row_default_height:35
                size_hint:1,35*len(self.children)/prefscroll.height
        OutlinedTextBox:
            outline:1,0,0,1
            text:'Strictly enforce targeting preference [b][color=ffff00](Enter)[/color][/b]'
            pos:prefwindow.x+10,prefwindow.y
            size_hint: (prefwindow.width-20)/prefwindow.width,(0.1*prefwindow.height-20)/prefwindow.height
        CheckBox:
            id:targetenforcement
            pos:prefwindow.x+10,prefwindow.y+1
            size_hint: (0.1*prefwindow.width-20)/prefwindow.width,(0.1*prefwindow.height-20)/prefwindow.height


<AttackInfo@GridLayout>
    cols:9
    size_hint:1,1
    OutlinedTextBox:
        text:str(root.information['Index'])
        color:root.color
    OutlinedTextBox:
        text:str(root.information['Attack Name'])
        color:root.color
    OutlinedTextBox:
        text:str(root.information['Weapon'])
        color:root.color
    OutlinedTextBox:
        text:str(root.information['Damage Type'])
        color:root.color
    OutlinedTextBox:
        text:str(root.information['Execution Time'])
        color:root.color
    OutlinedTextBox:
        text:str(root.information['Strike Length'])
        color:root.color
    OutlinedTextBox:
        text:str(root.information['Average Force'])
        color:root.color
    OutlinedTextBox:
        text:str(root.information['Average Pressure'])
        color:root.color
    OutlinedTextBox:
        text:str(root.information['Stamina Cost'])
        color:root.color

<AttackType@GridLayout>
    cols:2
    size_hint:1,1
    OutlinedTextBox:
        text:str(root.information['Index'])
        color:root.color
        size_hint:None,1
        width:0.2*root.width
    OutlinedTextBox:
        text:str(root.information['Type Name'])
        color:root.color

<CreatureStatusScreen@FloatLayout>
    size_hint:0.65,0.87
    pos_hint_x:0
    pos_hint_y:0.13
    canvas.before:
        Color:
            rgba:0.2,0.2,0.2,0.95
        Rectangle:
            id:backdrop
            size:self.width,self.height
            pos:self.pos
    OutlinedTextBox:
        size_hint:1,0.1
        pos:root.x,root.y+root.height-self.height
        text:'Status'
        outline:(1,0,0,1)
        font_size:30
    GridLayout:
        cols:1
        size_hint:0.2,0.05
        pos:root.x+10,root.y+0.9*root.height-self.height-10
        id:nametag
    GridLayout:
        cols:1
        size_hint:0.2,0.25
        pos:root.x+10,root.y+0.5*root.height-self.height-10
        id:attributes
    GridLayout:
        cols:1
        size_hint:0.2,0.05
        pos:root.x+10,root.y+0.85*root.height-self.height-10
        id:race
    GridLayout:
        cols:1
        size_hint:0.2,0.05
        pos:root.x+10,root.y+0.8*root.height-self.height-10
        id:level
    GridLayout:
        cols:1
        size_hint:0.2,0.05
        pos:root.x+10,root.y+0.75*root.height-self.height-10
        id:focus
    GridLayout:
        cols:1
        size_hint:0.2,0.05
        pos:root.x+10,root.y+0.7*root.height-self.height-10
        id:stamina
    GridLayout:
        cols:1
        size_hint:0.2,0.05
        pos:root.x+10,root.y+0.65*root.height-self.height-10
        id:tension
    GridLayout:
        cols:1
        size_hint:0.2,0.05
        pos:root.x+10,root.y+0.6*root.height-self.height-10
        id:pain

    OutlinedTextBox:
        size_hint: 0.25,0.05
        pos: root.x+0.2*root.width+20,root.y+0.9*root.height-self.height-10
        outline:(1,0,0,1)
        text:'Limbs'

    OutlinedTextBox:
        size_hint: 0.25,0.05
        pos: root.x+0.45*root.width+30,root.y+0.9*root.height-self.height-10
        outline:(1,0,0,1)
        text:'Injuries'

    OutlinedTextBox:
        size_hint: 0.25,0.05
        pos: root.x+0.7*root.width+40,root.y+0.9*root.height-self.height-10
        outline:(1,0,0,1)
        text:'Missing Limbs'

    ScrollView:
        size_hint:0.25,0.6-10/root.height
        pos: root.x+0.2*root.width+20,root.y+0.85*root.height-self.height-20
        canvas.before:
            Color:
                rgba:0,0,0,0.95
            Rectangle:
                size:self.width,self.height
                pos:self.pos
        GridLayout:
            cols:1
            id:limbs
            size_hint:1,0

    ScrollView:
        size_hint:0.25,0.6-10/root.height
        pos: root.x+0.45*root.width+30,root.y+0.85*root.height-self.height-20
        canvas.before:
            Color:
                rgba:0,0,0,0.95
            Rectangle:
                size:self.width,self.height
                pos:self.pos
        GridLayout:
            cols:1
            id:injuries
            size_hint:1,0

    ScrollView:
        size_hint:0.25,0.6-10/root.height
        pos: root.x+0.7*root.width+40,root.y+0.85*root.height-self.height-20
        canvas.before:
            Color:
                rgba:0,0,0,0.95
            Rectangle:
                size:self.width,self.height
                pos:self.pos
        GridLayout:
            cols:1
            id:missinglimbs
            size_hint:1,0

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

#The classes below deal with inventory screens
class OutlinedTextBox(Label):
    def __init__(self,color=(0,0,0,1),background=(0,0,0,1),**kwargs):
        self.outline=color
        self.background=background
        super().__init__(**kwargs)

class DisplayBox(FloatLayout):
    def __init__(self,titletext='',info='',color=(0,0,0,1),background=(0,0,0,1),**kwargs):
        self.titletext=titletext
        self.info=info
        self.outline=color
        self.background=background
        super().__init__(**kwargs)

class NoteBox(FloatLayout):
    def __init__(self,titletext,info,color=(0,0,0,1),background=(0,0,0,1),**kwargs):
        self.titletext=titletext
        self.info=info
        self.outline=color
        self.background=background
        super().__init__(**kwargs)
        self.ids['information'].bind(focus=self.on_focus)
        self.ids['information'].background_color=[self.background[0],self.background[1],self.background[2],0]

    def on_focus(self,instance,value):
        if value==True:
            self.past_keyboard_mode=Shell.shell.keyboard_mode
            Shell.shell.keyboard_mode='pass'
        else:
            Shell.shell.keyboard_mode=self.past_keyboard_mode

class ItemGraphic(Widget):
    def __init__(self,item,**kwargs):
        self.source=item.image
        if hasattr(item,'color'):
            self.color=item.color
        else:
            self.color=(1,1,1,1)
        super().__init__(**kwargs)

class AttackDescription(FloatLayout):
    def __init__(self,mode='item',item=None,player=None,**kwargs):
        self.size_hint=(0.4,0.3)
        self.pos_hint={'x':0.1,'top':0.4}
        super().__init__(**kwargs)
        if mode=='item':
            attackinfo=[]
            copyplayer=Shell.picklecopy(player)
            for i in copy.copy(copyplayer.equipped_items):
                if i.wield==item.wield:
                    while i.equipped!=[]:
                        copyplayer.unequip(i,log=False)
            item=Shell.picklecopy(item)
            item.equipped=[]
            copyplayer.equip(item=item,log=False)
            for i in copyplayer.attacks:
                if i.weapon==item and i.hands==1:
                    attackinfo.append(i.average_values())
            copyplayer.equip(item,log=False)
            for i in copyplayer.attacks:
                if i.weapon==item and i.hands==2 and len(i.limbs)==2:
                    i.__init__(i.weapon,i.limb)
                    newinfo=i.average_values()
                    if newinfo not in attackinfo:
                        attackinfo.append(newinfo)

        elif mode=='character':
            attackinfo=[]
            self.size_hint=(0.65,0.87)
            self.pos_hint={'x':0,'y':0.13}
            for i in player.attacks:
                newinfo=None
                if i.disabled==True:
                    pass
                elif i.weapon==None:
                    i.__init__(limb=i.limb)
                    newinfo=i.average_values()
                elif not hasattr(i.weapon,'equipped'):
                    i.__init__(weapon=i.weapon,limb=i.limb)
                    newinfo=i.average_values()
                elif i.hands==1 and len(i.weapon.equipped)==1:
                    i.__init__(weapon=i.weapon,limb=i.limb)
                    newinfo=i.average_values()
                elif i.hands==2 and len(i.weapon.equipped)>1:
                    i.__init__(weapon=i.weapon,limb=i.limb)
                    newinfo=i.average_values()
                if newinfo is not None and newinfo not in attackinfo:
                    attackinfo.append(newinfo)

        for i in attackinfo:
            self.ids['attackinfo'].add_widget(OutlinedTextBox(text=str(i['Attack Name']),halign='left'))
            self.ids['attackinfo'].add_widget(OutlinedTextBox(text=str(i['Damage Type']),halifn='left'))
            self.ids['attackinfo'].add_widget(OutlinedTextBox(text=''.join((str(int(100*i['Execution Time'])/100),' sec'))))
            self.ids['attackinfo'].add_widget(OutlinedTextBox(text=''.join((str(int(100*i['Strike Length'])/100),' m'))))
            self.ids['attackinfo'].add_widget(OutlinedTextBox(text=''.join((str(int(i['Average Force'])),' N'))))
            self.ids['attackinfo'].add_widget(OutlinedTextBox(text=''.join((str(int(i['Average Pressure']/100000)/10),' MPa'))))
            self.ids['attackinfo'].add_widget(OutlinedTextBox(text=str(i['Stamina Cost']),halign='left'))

class ItemDescription(FloatLayout):
    def __init__(self,item,player,pos_hint={'x':0.1,'y':0.4},**kwargs):
        self.item=item
        self.size_hint=(0.4,0.5)
        self.pos_hint=pos_hint
        self.player=player
        self.standard_inspection_screen(**kwargs)
        self.extrascreen=None

    def standard_inspection_screen(self,**kwargs):
        super().__init__(pos_hint=self.pos_hint,**kwargs)
        self.item.generate_descriptions(per=self.player.stats['per'])
        self.item_description=self.item.descriptor
        self.damage=self.item.describe_damage()
        if self.damage=='':
            self.damage='No damage'
        self.ids['infobox1'].add_widget(DisplayBox('material: ',self.item.info['material'],color=(1,0,0,1)))
        self.ids['infobox1'].add_widget(DisplayBox('mass: ',self.item.info['mass'],color=(1,0,0,1)))
        self.ids['infobox1'].add_widget(DisplayBox('magic: ',self.item.info['magic'],color=(1,0,0,1)))
        self.ids['infobox1'].add_widget(DisplayBox('quality: ',self.item.info['quality'],color=(1,0,0,1)))
        self.ids['infobox1'].add_widget(DisplayBox('equippable by player: ',self.item.info['equippable by player'],color=(1,0,0,1)))

        boxes=0
        try:
            self.ids['infobox2'].add_widget(DisplayBox('length: ',self.item.info['length'],color=(1,0,0,1)))
            boxes+=1
        except: pass
        try:
            self.ids['infobox2'].add_widget(DisplayBox('thickness: ',self.item.info['thickness'],color=(1,0,0,1)))
            boxes+=1
        except: pass
        try:
            self.ids['infobox2'].add_widget(DisplayBox('radius: ',self.item.info['radius'],color=(1,0,0,1)))
            boxes+=1
        except: pass
        try:
            self.ids['infobox2'].add_widget(DisplayBox('edge sharpness: ',self.item.info['edge sharpness'],color=(1,0,0,1)))
            boxes+=1
        except: pass
        try:
            self.ids['infobox2'].add_widget(DisplayBox('tip sharpness: ',self.item.info['tip sharpness'],color=(1,0,0,1)))
            boxes+=1
        except: pass
        try:
            self.ids['infobox2'].add_widget(DisplayBox('moment of inertia: ',self.item.info['moment of inertia'],color=(1,0,0,1)))
            boxes+=1
        except: pass
        self.note=NoteBox('Note: ',self.item.note,color=(1,0,0,1))
        self.ids['infobox2'].add_widget(self.note)
        boxes+=1

        self.note.ids['information'].bind(on_text_validate=self.note_update)

        while boxes<5:
            self.ids['infobox2'].add_widget(DisplayBox('',''))
            boxes+=1
        #for i in self.item.info:
         #   self.ids['infobox1'].add_widget(DisplayBox(''.join((i,': ')),self.item.info[i],color=(1,0,0,1)))

    def note_update(self,instance):
        self.item.note=instance.text

    def close_inspect(self):
        self.valid_commands=[]
        instructions=['']
        if self.item.attacks!=[]:
            instructions.append('[color=ffff00][b]A[/color][/b]ttacks({})   '.format(len(self.item.attacks)))
            self.valid_commands.append('a')
        if self.item.kills!=[]:
            instructions.append('[color=ffff00][b]K[/color][/b]ills({})   '.format(len(self.item.kills)))
            self.valid_commands.append('k')
        if self.item.enchantments!=[]:
            detected_enchantments=[]
            for i in self.item.enchantments:
                if i.detected==True:
                    detected_enchantments.append(i)
            if detected_enchantments!=[]:
                instructions.append('[color=ffff00][b]E[/color][/b]ffects({})   '.format(len(detected_enchantments)))
                self.valid_commands.append('e')
        if self.item.useable==True and self.item.in_inventory==Shell.shell.player:
            instructions.append('[color=ffff00][b]U[/color][/b]se   ')
            self.valid_commands.append('u')
        self.ids['instructions'].text=''.join(instructions)

    def open_submenu(self,keycode):
        if keycode=='escape':
            self.remove_extra()
            self.close_inspect()
            self.ids['instructions'].text='Press[b][color=ffff00] Enter[/color][/b] for further options'
            Shell.shell.keyboard_mode='inventory sidebar'
        if keycode in self.valid_commands:
            if keycode=='a':
                if isinstance(self.extrascreen,AttackDescription):
                    pass
                else:
                    self.extrascreen=AttackDescription(player=Shell.shell.player,item=self.item)
                    Shell.shell.add_widget(self.extrascreen)

    def remove_extra(self):
        if self.extrascreen!=None:
            Shell.shell.remove_widget(self.extrascreen)
            self.extrascreen=None

class InventoryItem(ButtonBehavior,GridLayout):
    def __init__(self,item,letter='playerinventory',**kwargs):
        super().__init__(cols=4,**kwargs)
        self.item=item
        self.letter=letter
        self.graphicsbox=ItemGraphic(item,size_hint=(0.1,None),height=self.height)
        mass=int(item.mass*100)/100
        text='[color=333300][b] {} [/b]({} kg) [/color]'.format(item.name,mass)
        if hasattr(item,'equipped') and item.equipped!=[]:
            print(item.equipped)
            text=' '.join((text,' [color=ff33ff](equipped on {})[/color]'.format(' '.join((i.name for i in item.equipped)))))
        self.text=Label(markup=True,text=text,halign='left',text_size=(500,None),shorten=True)
        if letter=='playerinventory':
            self.index=Label(markup=True, text='[b][color=333300]     {}: [/color][/b]'.format(item.inventory_index),shorten=True,size_hint=(0.1,1))
        else:
            self.index=Label(markup=True, text='[b][color=333300]     {}: [/color][/b]'.format(letter),shorten=True,size_hint=(0.1,1))
        self.add_widget(self.index)
        self.add_widget(self.graphicsbox)
        self.add_widget(self.text)
        self.index.bind(size=self.index.setter('text_size'))
        self.text.bind(size=self.text.setter('text_size'))

    def highlight(self):
        with self.canvas.before:
            Color(1,0,0,0.1)
            Rectangle(size=self.size,pos=self.pos)
        pass

    def unhighlight(self):
        self.canvas.before.clear()
        pass

    def inspect(self):
        pass

class InventorySidebar(ScrollView):
    def __init__(self,shell,**kwargs):
        super().__init__(**kwargs)
        self.inspection_open=False
        self.size_hint=(0.35,0.9)
        self.pos_hint={'right':1,'top':1}
        self.shell=shell
        self.showing=''
        self.inspected_item=None

    def show_player_inventory(self):
        self.showing='inventory'
        self.shell.player.inventory_order()
        self.shell.player.mass_calc()
        self.selected_items=[]
        letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-='
        self.selectionindex={}
        self.list=BoxLayout(orientation='vertical',size_hint=(1,None))
        self.list.size[1]=len(self.shell.player.inventory)*30+120
        self.add_widget(self.list)
        with self.canvas.before:
            Color(0.7,0.7,0.7)
            self.graphics=Rectangle(size=(10000,10000),pos_hint=self.pos_hint)

        weaponlabel=Label(markup=True,text="[color=333300]  Weapons:[/color]",halign='left',text_size=(500,None),shorten=True)
        self.list.add_widget(weaponlabel)
        weaponlabel.bind(size=weaponlabel.setter('text_size'))
        weapons=0
        for i in self.shell.player.inventory:
            if i.sortingtype=='weapon':
                new=InventoryItem(i,size_hint=(1,None),height=30)
                self.selectionindex[new.item.inventory_index]=new
                self.list.add_widget(new)
                weapons+=1
        if weapons==0:
            self.list.remove_widget(weaponlabel)


        armorlabel=Label(markup=True,text="[color=333300]  Armor:[/color]",halign='left',text_size=(500,None),shorten=True)
        armorlabel.bind(size=armorlabel.setter('text_size'))
        self.list.add_widget(armorlabel)
        armor=0
        for i in self.shell.player.inventory:
            if i.sortingtype=='armor':
                new=InventoryItem(i,size_hint=(1,None),height=30)
                self.selectionindex[new.item.inventory_index]=new
                self.list.add_widget(new)
                armor+=1
        if armor==0:
            self.list.remove_widget(armorlabel)

        misclabel=Label(markup=True,text="[color=333300]  Miscellaneous:[/color]",halign='left',text_size=(500,None),shorten=True)
        misclabel.bind(size=misclabel.setter('text_size'))
        self.list.add_widget(misclabel)
        misc=0
        for i in self.shell.player.inventory:
            if i.sortingtype=='misc':
                new=InventoryItem(i,size_hint=(1,None),height=30)
                self.selectionindex[new.item.inventory_index]=new
                self.list.add_widget(new)
                misc+=1
        if misc==0:
            self.list.remove_widget(misclabel)
        
        item_mass=0
        for i in self.shell.player.inventory:
            item_mass+=i.mass
        item_mass=int(item_mass*100)/100
        
        carryweight=Label(markup=True,text="[b][color=333300]Carried Weight:[/b] {}[/color]".format(item_mass),halign='right',text_size=(500,None),shorten=True)
        carryweight.bind(size=carryweight.setter('text_size'))
        self.list.add_widget(carryweight)

        body_mass=int(100*self.shell.player.mass)/100
        bodyweight=Label(markup=True,text="[b][color=333300]Body Weight:[/b] {}[/color]".format(body_mass),halign='right',text_size=(500,None),shorten=True)
        bodyweight.bind(size=bodyweight.setter('text_size'))
        self.list.add_widget(bodyweight)

        total_mass=int(self.shell.player.movemass*100)/100
        totalweight=Label(markup=True,text="[b][color=333300]Total Weight: [/b] {}[/color]".format(total_mass),halign='right',text_size=(500,None),shorten=True)
        totalweight.bind(size=totalweight.setter('text_size'))
        self.list.add_widget(totalweight)

        encumbrance_factor=int(total_mass/self.shell.player.stats['str']*100)/100
        encumbrance=Label(markup=True,text="[b][color=333300]Encumbrance Factor: [/b] {}[/color]".format(encumbrance_factor),halign='right',text_size=(500,None),shorten=True)
        encumbrance.bind(size=encumbrance.setter('text_size'))
        self.list.add_widget(encumbrance)

        self.shell.add_widget(self)

        for i in self.list.children:
            try: i.bind(on_press=self.mouse_select)
            except: pass

    def show_items_on_ground(self,cell):
        self.showing='ground'
        self.selected_items=[]
        self.selectionindex={}
        letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-='
        letterpos=0
        self.list=BoxLayout(orientation='vertical',size_hint=(1,None))
        self.list.size[1]=len(cell.contents)*30+60
        self.add_widget(self.list)
        with self.canvas.before:
            Color(0.7,0.7,0.7)
            self.graphics=Rectangle(size=(10000,10000),pos_hint=self.pos_hint)

        weaponlabel=Label(markup=True,text="[color=333300]  Weapons:[/color]",halign='left',text_size=(500,None),shorten=True)
        weaponlabel.bind(size=weaponlabel.setter('text_size'))
        self.list.add_widget(weaponlabel)
        weapons=0
        for i in cell.contents:
            if hasattr(i,'sortingtype') and i.sortingtype=='weapon':
                try: letter=letters[letterpos]
                except KeyError: letter=''
                i.touched_by_player=True
                if self.shell.player.can_see==True:
                    i.seen_by_player=True
                i.generate_descriptions(self.shell.player.stats['per'])
                new=InventoryItem(i,size_hint=(1,None),letter=letter,height=30)
                self.selectionindex[letter]=new
                self.list.add_widget(new)
                letterpos+=1
                weapons+=1
        if weapons==0:
            self.list.remove_widget(weaponlabel)

        armorlabel=Label(markup=True,text="[color=333300]  Armor:[/color]",halign='left',text_size=(500,None),shorten=True)
        armorlabel.bind(size=armorlabel.setter('text_size'))
        self.list.add_widget(armorlabel)
        armor=0
        for i in cell.contents:
            if hasattr(i,'sortingtype') and i.sortingtype=='armor':
                try: letter=letters[letterpos]
                except KeyError: letter=''
                i.touched_by_player=True
                if self.shell.player.can_see==True:
                    i.seen_by_player=True
                i.generate_descriptions(self.shell.player.stats['per'])
                new=InventoryItem(i,size_hint=(1,None),letter=letter,height=30)
                self.selectionindex[letter]=new
                self.list.add_widget(new)
                letterpos+=1
                armor+=1
        if armor==0:
            self.list.remove_widget(armorlabel)

        misclabel=Label(markup=True,text="[color=333300]  Miscellaneous:[/color]",halign='left',text_size=(500,None),shorten=True)
        misclabel.bind(size=misclabel.setter('text_size'))
        self.list.add_widget(misclabel)
        misc=0
        for i in cell.contents:
            if hasattr(i,'sortingtype') and i.sortingtype=='misc':
                try: letter=letters[letterpos]
                except KeyError: letter=''
                i.touched_by_player=True
                if self.shell.player.can_see==True:
                    i.seen_by_player=True
                i.generate_descriptions(self.shell.player.stats['per'])
                new=InventoryItem(i,size_hint=(1,None),letter=letter,height=30)
                self.selectionindex[letter]=new
                self.list.add_widget(new)
                letterpos+=1
                misc+=1
        if misc==0:
            self.list.remove_widget(misclabel)


        self.shell.add_widget(self)

        for i in self.list.children:
            try: i.bind(on_press=self.mouse_select)
            except: pass

    def mouse_select(self,inventoryitem):
        if Shell.shell.keyboard_mode=='inventory sidebar':
            if self.showing=='inventory':
                if inventoryitem.item.inventory_index not in ('',None):
                    self.inspect(inventoryitem.item.inventory_index)
                else:
                    self.selectionindex['mouse']=inventoryitem
                    inventoryitem.item.inventory_index='mouse'
                    self.inspect('mouse')
                    self.selectionindex['mouse']=None
                    inventoryitem.item.inventory_index=None
            elif self.showing=='ground':
                if inventoryitem.letter not in ('',None):
                    self.inspect(inventoryitem.letter)
                else:
                    self.selectionindex['mouse']=inventoryitem
                    inventoryitem.item.inventory_index='mouse'
                    self.inspect('mouse')
                    self.selectionindex['mouse']=None
                    inventoryitem.item.inventory_index=None
        else:
            if self.showing=='inventory':
                if inventoryitem.item.inventory_index not in (None,''):
                    self.select(inventoryitem.item.inventory_index)
                else:
                    self.selectionindex['mouse']=inventoryitem
                    inventoryitem.item.inventory_index='mouse'
                    self.select('mouse')
                    self.selectionindex['mouse']=None
                    inventoryitem.item.inventory_index=None
            if self.showing=='ground':
                if inventoryitem.letter not in (None,''):
                    self.select(inventoryitem.letter)
                else:
                    self.selectionindex['mouse']=inventoryitem
                    inventoryitem.item.inventory_index='mouse'
                    self.select('mouse')
                    self.selectionindex['mouse']=None
                    inventoryitem.item.inventory_index=None

    def select(self,index):
        for i in self.selectionindex:
            if index==i:
                if self.selectionindex[i] not in self.selected_items:
                    self.selected_items.append(self.selectionindex[i])
                    self.selectionindex[i].highlight()
                else:
                    self.selected_items.remove(self.selectionindex[i])
                    self.selectionindex[i].unhighlight()

    def inspect(self,index):
        if index=='enter':
            self.inspectionscreen.close_inspect()
            Shell.shell.keyboard_mode='close inspect'
            return
        if self.inspection_open==True:
            self.shell.remove_widget(self.inspectionscreen)
            self.inspection_open=False
        ok=False
        for i in self.selectionindex:
            if index==i:
                self.inspectionscreen=ItemDescription(self.selectionindex[i].item,self.shell.player)
                ok=True
        if ok==True:
            self.shell.add_widget(self.inspectionscreen)
            self.inspection_open=True
            self.inspected_item=self.selectionindex[i]
        else:
            self.inspected_item=None

    def pickup_selected(self,cell):
        pickedup=0
        for i in self.selected_items:
            self.shell.player.inventory_add(i.item)
            cell.contents.remove(i.item)
            messages.append("You pick up the {}".format(i.item.name))
            pickedup+=1
        if pickedup>0:
            self.shell.turn+=1
        self.close()

    def drop_selected(self,cell):
        dropped_items=0
        for i in self.selected_items:
            if hasattr(i.item,'equipped') and i.item.equipped!=[]:
                if i.item.wield is not 'grasp':
                    self.shell.log.addtext('You must unequip your {} before dropping it'.format(i.item.name))
                else:
                    self.shell.player.unequip(i.item,log=False)
                    self.shell.player.inventory.remove(i.item)
                    cell.contents.append(i.item)
                    self.shell.log.addtext('You drop the {}'.format(i.item.name))
                    #dropped_items+=1
            else:
                self.shell.player.inventory.remove(i.item)
                cell.contents.append(i.item)
                self.shell.log.addtext('You drop the {}'.format(i.item.name))
                dropped_items+=1
        if dropped_items>0:
            self.shell.turn+=1
        self.close()

    def equip_selected(self):
        for i in self.selected_items:
            if not hasattr(i.item,'wield'):
                self.shell.log.addtext('{} cannot be wielded as a weapon or armor'.format(i.item.name))
            if hasattr(i.item,'equipped') and i.item.equipped!=[] and i.item.wield!='grasp':
                self.shell.log.addtext('The {} is already equipped!'.format(i.item.name))
            elif hasattr(i.item,'equipped') and i.item.equipped!=[] and i.item.wield=='grasp':
                wieldingnumber=len(i.item.equipped)
                self.shell.player.equip(i.item)
                if len(i.item.equipped)>wieldingnumber:
                    pass
                    #self.shell.turn+=1
                else:
                    self.shell.log.addtext('You have no additional limbs which can grasp the {}'.format(i.item.name))
            if hasattr(i.item,'equipped') and i.item.equipped==[]:
                self.shell.player.equip(i.item)
                if i.item.equipped!=[]:
                    self.shell.turn+=1
                else:
                    self.shell.log.addtext('You have no body parts available which can wield the {}'.format(i.item.name))
        self.close()

    def unequip_selected(self):
        for i in self.selected_items:
            if not hasattr(i.item,'wield'):
                self.shell.log.addtext('{} cannot be wielded as a weapon or armor'.format(i.item.name))
            if hasattr(i.item,'equipped') and i.item.equipped==[]:
                self.shell.log.addtext('The {} is not equipped!'.format(i.item.name))
            if hasattr(i.item,'equipped') and i.item.equipped!=[]:
                self.shell.player.unequip(i.item)
                if i.item.equipped==[]:
                    if i.item.wield=='grasp':
                        messages.append('You put away the {}'.format(i.item.name))
                        self.shell.turn+=1
                    else:
                        messages.append('You remove the {}'.format(i.item.name))
                        self.shell.turn+=1

        self.close()

    def close(self):
        if self.inspection_open==True:
            self.inspected_item=None
            self.shell.remove_widget(self.inspectionscreen)
            self.inspection_open==False
        self.list.canvas.clear()
        self.shell.remove_widget(self)
        self.clear_widgets()


#The classes below deal with creature status screens

class CreatureStatusScreen(FloatLayout):
    #TODO: Make limbs collapsible
    def __init__(self,creature=None,**kwargs):
        self.creature=creature
        super().__init__(**kwargs)
        self.pos_hint={'x':0,'y':0.13}
        self.nametag=DisplayBox(titletext='Name:',info=self.creature.name)
        self.ids['nametag'].add_widget(self.nametag)
        if creature.stats['str']==creature.stats['s']:
            self.strength=DisplayBox(titletext='Strength',info=str(creature.stats['str']))
        else:
            self.strength=DisplayBox(titletext='Strength',info='{} ({})'.format(creature.stats['str'],creature.stats['s']))
        if creature.stats['tec']==creature.stats['t']:
            self.technique=DisplayBox(titletext='Technique',info=str(creature.stats['tec']))
        else:
            self.technique=DisplayBox(titletext='Technique',info='{} ({})'.format(creature.stats['tec'],creature.stats['t']))
        if creature.stats['per']==creature.stats['p']:
            self.perception=DisplayBox(titletext='Perception',info=str(creature.stats['per']))
        else:
            self.perception=DisplayBox(titletext='Perception',info='{} ({})'.format(creature.stats['per'],creature.stats['p']))
        if creature.stats['wil']==creature.stats['w']:
            self.will=DisplayBox(titletext='Will',info=str(creature.stats['wil']))
        else:
            self.will=DisplayBox(titletext='Will',info='{} ({})'.format(creature.stats['wil'],creature.stats['w']))
        if creature.stats['luc']==creature.stats['l']:
            self.luck=DisplayBox(titletext='Luck',info=str(creature.stats['luc']))
        else:
            self.will=DisplayBox(titletext='Luck',info='{} ({})'.format(creature.stats['luc'],creature.stats['l']))
        self.ids['attributes'].add_widget(self.strength)
        self.ids['attributes'].add_widget(self.technique)
        self.ids['attributes'].add_widget(self.perception)
        self.ids['attributes'].add_widget(self.will)
        self.ids['attributes'].add_widget(self.luck)

        self.race=DisplayBox(titletext='Race',info='Human')
        self.ids['race'].add_widget(self.race)

        self.level=DisplayBox(titletext='Level',info=str(creature.level))
        self.ids['level'].add_widget(self.level)

        self.focus=DisplayBox(titletext='Focus',info="{}/{}".format(int(creature.focus[0]),int(creature.focus[1])))
        self.ids['focus'].add_widget(self.focus)

        self.stamina=DisplayBox(titletext='Stamina',info="{}/{}".format(int(creature.stamina[0]),int(creature.stamina[1])))
        self.ids['stamina'].add_widget(self.stamina)

        self.pain=DisplayBox(titletext='Pain',info=str(int(creature.pain)))
        self.ids['pain'].add_widget(self.pain)

        self.tension=DisplayBox(titletext='Tension',info="{} %".format(int(100*creature.tension)))
        self.ids['tension'].add_widget(self.tension)

        for i in creature.limbs:
            self.ids['limbs'].size_hint[1]+=0.05
            self.ids['limbs'].add_widget(OutlinedTextBox(text=i.name))
            if i.ability<1:
                self.ids['injuries'].size_hint[1]+=0.05
                self.ids['injuries'].add_widget(OutlinedTextBox(text=i.name))
        for i in creature.missing_limbs:
            self.ids['missinglimbs'].size_hint[1]+=0.05
            self.ids['missinglimbs'].add_widget(OutlinedTextBox(text=i.name))

class AttackManagementScreen(FloatLayout):
    def __init__(self,creature=None,**kwargs):
        self.creature=creature
        limbs=self.creature.limbs
        attacklist=[]
        typelist=[]
        super().__init__(**kwargs)
        self.pos_hint={'x':0,'y':0.13}
        for k in limbs:
            if k.ability>0 and k.owner is not None:
                for i in k.attacks:
                    if type(i) not in typelist:
                        typelist.append(type(i))
                    if i.weapon==None:
                        attacklist.append(i)
                    elif not hasattr(i.weapon,'equipped'):
                        attacklist.append(i)
                    elif len(i.weapon.equipped)==1 and i.hands==1:
                        attacklist.append(i)
                    elif len(i.weapon.equipped)>1 and i.hands>1:
                        if not any((i.weapon.equipped,i.name)==(j.weapon.equipped,j.name) for j in attacklist):
                            attacklist.append(i)
        letters='abcdefghijklmnopqrstuvwxyz'
        assigned_indices=[]
        for i in attacklist:
            try:
                index=letters[len(assigned_indices)]
                assigned_indices.append(index)
            except KeyError:
                index=None
            self.ids['attacks'].add_widget(AttackInfo(attack=i,creature=creature,index=index))
        assigned_indices=[]
        for i in typelist:
            try:
                index=letters[len(assigned_indices)]
                assigned_indices.append(index)
            except KeyError:
                index=None
            self.ids['types'].add_widget(AttackType(attacktype=i,creature=creature,index=index))
        for i in self.ids['types'].children:
            i.screen=self
        number=1
        for i in ('random','vital organs','nonvital organs','attacking limbs','ambulatory limbs','grasping limbs','sensory organs','balancing limbs'):
            pref=AttackPref(creature=self.creature,pref=i,index=str(number))
            self.ids['prefs'].add_widget(pref)
            number+=1
            pref.screen=self
        self.ids['targetenforcement'].bind(active=self.check_uncheck)
        self.ids['targetenforcement'].active=creature.preference_enforcement

    def keyboard_input(self,input,shift):
        if input=='enter':
            self.ids['targetenforcement']._toggle_active()
        if shift==False:
            for i in self.ids['prefs'].children:
                if i.index==input:
                    i.on_press()
            for i in self.ids['attacks'].children:
                if i.information['Index']==input:
                    i.on_press()
        if shift==True:
            for i in self.ids['types'].children:
                if i.index==input:
                    i.on_press()

    def check_uncheck(self,instance,state):
        self.creature.preference_enforcement=state

    def refresh(self):
        self.clear_widgets()
        self.__init__(creature=self.creature)

class AttackInfo(ButtonBehavior,GridLayout):
    def __init__(self,attack=None,creature=None,index=None,**kwargs):
        self.attack=attack
        self.creature=creature
        self.index=index
        if self.attack.disabled==True or type(attack) in creature.disabled_attack_types:
            self.color=[0.6,0.6,0.6,0.6]
        else:
            self.color=[1,1,1,1]
        self.attack.__init__(weapon=attack.weapon,limb=attack.limb)
        self.information=attack.average_values()
        self.information['Index']=index
        try: self.information['Weapon']=self.attack.weapon.name
        except AttributeError: self.information['Weapon']=None
        self.information['Execution Time']=''.join((str(int(100*self.information['Execution Time'])/100),' sec'))
        self.information['Strike Length']=''.join((str(int(100*self.information['Strike Length'])/100),' m'))
        self.information['Average Force']=''.join((str(int(self.information['Average Force'])),' N'))
        self.information['Average Pressure']=''.join((str(int(self.information['Average Pressure']/100000)/10),' MPa'))
        super().__init__(**kwargs)

    def on_press(self):
        if type(self.attack) in self.creature.disabled_attack_types:
            return
        if self.attack.disabled==True:
            self.attack.disabled=False
            self.color=[1,1,1,1]
            self.clear_widgets()
            self.__init__(attack=self.attack,creature=self.creature,index=self.information['Index'])
            if self.attack.sig in self.creature.disabled_attacks:
                self.creature.disabled_attacks.remove(self.attack.sig)
            return
        if self.attack.disabled==False:
            self.attack.disabled=True
            self.color=[0.6,0.6,0.6,0.6]
            self.clear_widgets()
            self.__init__(attack=self.attack,creature=self.creature,index=self.information['Index'])
            if self.attack.sig not in self.creature.disabled_attacks:
                self.creature.disabled_attacks.append(self.attack.sig)
            return

class AttackType(ButtonBehavior,GridLayout):
    def __init__(self,attacktype=None,creature=None,index=None,**kwargs):
        self.index=index
        self.creature=creature
        self.attacktype=attacktype
        self.information={'Index':index.capitalize(),'Type Name':str(attacktype).strip("<class 'Attacks.").strip(">'")}
        if attacktype in creature.disabled_attack_types:
            self.color=[0.6,0.6,0.6,0.6]
        else:
            self.color=[1,1,1,1]
        super().__init__(**kwargs)

    def on_press(self):
        if self.attacktype in self.creature.disabled_attack_types:
            self.creature.disabled_attack_types.remove(self.attacktype)
            self.color=[1,1,1,1]
            self.clear_widgets()
            self.__init__(attacktype=self.attacktype,creature=self.creature,index=self.index)
        else:
            self.creature.disabled_attack_types.append(self.attacktype)
            self.color=[0.6,0.6,0.6,0.6]
            self.clear_widgets()
            self.__init__(attacktype=self.attacktype,creature=self.creature,index=self.index)
        for i in self.screen.ids['attacks'].children:
            i.clear_widgets()
            i.__init__(attack=i.attack,creature=i.creature,index=i.index)

class AttackPref(ButtonBehavior,GridLayout):
    def __init__(self,creature=None,pref=None,index=None,**kwargs):
        super().__init__(**kwargs)
        self.creature=creature
        self.cols=2
        self.pref=pref
        self.index=index
        indexbox=OutlinedTextBox(text=str(index),size_hint=(None,1))
        indexbox.width=40
        self.add_widget(indexbox)
        prefbox=OutlinedTextBox(text=str(pref))
        self.add_widget(prefbox)
        if creature.target_preference==pref:
            color=(1,1,1,1)
        else:
            color=(0.6,0.6,0.6,0.6)
        indexbox.color=color
        prefbox.color=color

    def on_press(self):
        self.creature.target_preference=self.pref
        for i in self.screen.ids['prefs'].children:
            i.clear_widgets()
            i.__init__(pref=i.pref,creature=i.creature,index=i.index)


class LimbIndicator(ButtonBehavior,GridLayout):
    def __init__(self,limb,**kwargs):
        pass


class StatusScreen(FloatLayout):
    def __init__(self,character,**kwargs):
        super().__init__(**kwargs)
        self.character=character
        self.screen=None

    def keyboard_input(self,input,shift):
        if input=='escape':
            self.screen=None
            Shell.shell.keyboard_mode='play'
            Shell.shell.remove_widget(self)
        elif self.screen is not None:
            self.screen.keyboard_input(input,shift)


    def attack_screen(self):
        #self.add_widget(AttackDescription(mode='character',player=self.character))
        self.screen=AttackManagementScreen(self.character)
        self.add_widget(self.screen)

    def creature_status(self):
        self.screen=CreatureStatusScreen(self.character)
        self.add_widget(self.screen)

#The intention is that the Cell class will serve as a container for all creatures and items to be displayed on the screen.
#I expect to be tinkering with it quite a bit to make everything work just right.

#TODO: Need to ensure updates to graphics only occur when the cell is visible to the player. Much work to be done.

class Cell(Widget):
    contents=ListProperty([])
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.alignment=0
        self.size_hint=(None,None)
        self.size=(cellsize,cellsize)
        self.passable=True
        self.highlighted=False
        self.location=[None,None]
        self.immediate_neighbors=[]


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
        for i in self.contents:
            if isinstance(i,BaseClasses.Item) or isinstance(i,MapTiles.DungeonFeature) or isinstance(i,BaseClasses.Fluid):
                i.on_turn()
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





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
            rgba:1,1,1,1
        Rectangle:
            id:graphics
            size:self.height*0.8,self.height*0.8
            pos:self.center_x-self.height*0.4,self.y
            source:self.source


<OutlinedTextBox@Label>
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
            rgba: 0,0,0,1
        Rectangle:
            pos:self.x+1,self.y+1
            size:self.width-2,self.height-2



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
            rgba: 1,1,1,1
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
        id:infobox
        cols:2
        rows:len(root.item.info)
        pos:root.x+10,root.y+10+0.1*root.height
        size_hint:(root.width-20)/root.width,(root.height*0.55-50)/root.height
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

class OutlinedTextBox(Label):
    def __init__(self,color=(0,0,0,1),**kwargs):
        self.outline=color
        super().__init__(**kwargs)

class ItemGraphic(Widget):
    def __init__(self,item,**kwargs):
        self.source=item.image
        super().__init__(**kwargs)

class ItemDescription(FloatLayout):
    def __init__(self,item,player,pos_hint={'x':0.1,'y':0.3},**kwargs):
        self.item=item
        self.size_hint=(0.4,0.5)
        self.pos_hint=pos_hint
        super().__init__(pos_hint=pos_hint,**kwargs)
        self.item.generate_descriptions(per=player.stats['per'])
        self.item_description=item.descriptor
        self.damage=item.describe_damage()
        if self.damage=='':
            self.damage='No damage'
        for i in self.item.info:
            self.ids['infobox'].add_widget(OutlinedTextBox(text='{}:'.format(i),color=(1,0,0,1),halign='left'))
            self.ids['infobox'].add_widget(OutlinedTextBox(text=self.item.info[i],color=(1,0,0,1),halign='right'))





class InventoryItem(GridLayout):
    def __init__(self,item,letter='playerinventory',**kwargs):
        super().__init__(cols=4,**kwargs)
        self.item=item
        self.graphicsbox=ItemGraphic(item,size_hint=(0.1,None),height=self.height)
        mass=int(item.mass*100)/100
        text='[color=333300][b] {} [/b]({} kg) [/color]'.format(item.name,mass)
        if hasattr(item,'equipped') and item.equipped is not None:
            text=' '.join((text,' [color=ff33ff](equipped on {})[/color]'.format(item.equipped.name)))
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

    def show_player_inventory(self):
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

    def show_items_on_ground(self,cell):
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
                new=InventoryItem(i,size_hint=(1,None),letter=letters[letterpos],height=30)
                self.selectionindex[letters[letterpos]]=new
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
                new=InventoryItem(i,size_hint=(1,None),letter=letters[letterpos],height=30)
                self.selectionindex[letters[letterpos]]=new
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
                new=InventoryItem(i,size_hint=(1,None),letter=letters[letterpos],height=30)
                self.selectionindex[letters[letterpos]]=new
                self.list.add_widget(new)
                letterpos+=1
                misc+=1
        if misc==0:
            self.list.remove_widget(misclabel)


        self.shell.add_widget(self)

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
            if hasattr(i.item,'equipped') and i.item.equipped is not None:
                if i.item.wield is not 'grasp':
                    self.shell.log.addtext('You must unequip your {} before dropping it'.format(i.item.name))
                else:
                    self.shell.player.unequip(i.item,log=False)
                    self.shell.player.inventory.remove(i.item)
                    cell.contents.append(i.item)
                    self.shell.log.addtext('You drop the {}'.format(i.item.name))
                    dropped_items+=1
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
            if hasattr(i.item,'equipped') and i.item.equipped!=None:
                self.shell.log.addtext('The {} is already equipped!'.format(i.item.name))
            if hasattr(i.item,'equipped') and i.item.equipped==None:
                self.shell.player.equip(i.item)
                if i.item.equipped!=None:
                    self.shell.turn+=1
                else:
                    self.shell.log.addtext('You have no body parts available which can wield the {}'.format(i.item.name))
        self.close()

    def unequip_selected(self):
        for i in self.selected_items:
            if not hasattr(i.item,'wield'):
                self.shell.log.addtext('{} cannot be wielded as a weapon or armor'.format(i.item.name))
            if hasattr(i.item,'equipped') and i.item.equipped==None:
                self.shell.log.addtext('The {} is not equipped!'.format(i.item.name))
            if hasattr(i.item,'equipped') and i.item.equipped!=None:
                self.shell.player.unequip(i.item)
                if i.item.equipped==None:
                    if i.item.wield=='grasp':
                        messages.append('You put away the {}'.format(i.item.name))
                        self.shell.turn+=1
                    else:
                        messages.append('You remove the {}'.format(i.item.name))
                        self.shell.turn+=1

        self.close()



    def close(self):
        if self.inspection_open==True:
            self.shell.remove_widget(self.inspectionscreen)
            self.inspection_open==False
        self.list.canvas.clear()
        self.shell.remove_widget(self)
        self.clear_widgets()




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





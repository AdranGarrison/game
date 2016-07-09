__author__ = 'Alan'



import BaseClasses
import Shell



class DungeonFeature():
    def __init__(self,screen=None,x=None,y=None,image='./images/BlankTile.png'):
        self.location=[None,None]
        self.passable=True
        self.passage={'walk':1,'crawl':1,'fly':1,'swim':0,'float':1,'phase':1,'climb':0}
        self.vision_blocking=False
        self.hostile=[]
        self.targetable=False
        self.image=image
        self.color=[1,1,1,1]
        self.name=''
        if screen:
            self.place(screen,x,y)

    def place(self,screen,x,y):
        screen.cells[x][y].contents.append(self)
        self.location=[x,y]
        self.floor=screen

    def on_turn(self):
        pass

    def go_down(self,creature):
        pass

    def go_up(self,creature):
        pass

class DungeonFloor(DungeonFeature):
    def __init__(self,screen=None,x=None,y=None):
        super().__init__(screen,x,y,image='./images/Floor.png')
        self.name='dungeon floor'


class Wall(DungeonFeature):
    def __init__(self,screen=None,x=None,y=None):
        super().__init__(screen,x,y,image='./images/Wall.png')
        self.passable=False
        self.passage={'walk':0,'crawl':0,'fly':0,'float':0,'climb':0,'phase':1,'swim':0}
        self.vision_blocking=True
        self.name='wall'

class Upstair(DungeonFeature):
    def __init__(self,screen=None,x=None,y=None,goto=None):
        super().__init__(screen,x,y,image='./images/upstair.png')
        self.goto=goto
        if screen:
            screen.upstair=self

    def go_up(self,creature):
        if self.goto==None:
            return
        creature.floor.cells[creature.location[0]][creature.location[1]].contents.remove(creature)
        self.goto.floor.cells[self.goto.location[0]][self.goto.location[1]].contents.append(creature)
        if creature.player:
            Shell.shell.dungeonmanager.current=self.goto.floor.name


class Downstair(DungeonFeature):
    def __init__(self,screen=None,x=None,y=None,goto=None):
        super().__init__(screen,x,y,image='./images/downstair.png')
        self.goto=goto
        if screen:
            screen.downstair=self

    def go_down(self,creature):
        if self.goto==None:
            floorname=Shell.floornames[Shell.floornames.index(self.floor.name)+1]
            gotofloor=BaseClasses.Floor(floorname)
            self.goto=gotofloor.upstair
            gotofloor.upstair.goto=self
        creature.floor.cells[creature.location[0]][creature.location[1]].contents.remove(creature)
        self.goto.floor.cells[self.goto.location[0]][self.goto.location[1]].contents.append(creature)
        if creature.player:
            Shell.shell.dungeonmanager.current=self.goto.floor.name




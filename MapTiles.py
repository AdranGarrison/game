__author__ = 'Alan'



from BaseClasses import *


class DungeonFeature():
    def __init__(self,screen=None,x=None,y=None,image='./images/BlankTile.png'):
        self.location=[None,None]
        self.passable=True
        self.hostile=[]
        self.targetable=False
        self.image=image
        if screen:
            self.place(screen,x,y)

    def place(self,screen,x,y):
        screen.cells[x][y].contents.append(self)
        self.location=[x,y]

    def on_turn(self):
        pass

class DungeonFloor(DungeonFeature):
    def __init__(self,screen=None,x=None,y=None):
        super().__init__(screen,x,y)


class Wall(DungeonFeature):
    def __init__(self,screen=None,x=None,y=None):
        super().__init__(screen,x,y,image='./images/Wall.png')
        self.passable=False
__author__ = 'Alan'


from MapTiles import *
from UI_Elements import *


def probabilistic_automaton(floor, complete=True):
    max_x=floor.dimensions[0]
    max_y=floor.dimensions[1]
    newfloor=floor
    for h in range (0,int(2*max_x)):
        newfloor.cells[random.randint(0,max_x-1)][random.randint(0,max_y-1)].open=True

    for h in range(0,8):
        for i in range(0,max_x):
            for j in range(0,max_y):
                for x in newfloor.cells[i][j].immediate_neighbors:
                    if x.open==True:
                        newfloor.cells[i][j].probability+=3
                    else:
                        newfloor.cells[i][j].probability-=0.29
                if i in [0,max_x-1] or j in [0,max_y-1]:
                    newfloor.cells[i][j].probability=0
                    newfloor.cells[i][j].open=False
        for i in range(0,max_x):
            for j in range(0,max_y):
                if newfloor.cells[i][j].probability/8>=random.gauss(0.4,0.2):
                    newfloor.cells[i][j].open=True
                else:
                    newfloor.cells[i][j].open=False
                newfloor.cells[i][j].probability=random.choice([0,newfloor.cells[i][j].probability/2])
                newfloor.cells[i][j].probability=random.choice([0,newfloor.cells[i][j].probability/3])

    if complete==True:
        for i in range(0,max_x):
            for j in range(0,max_y):
                if newfloor.cells[i][j].open==False:
                    MapTiles.Wall(newfloor,i,j)

def second_order_automaton(floor, complete=True):
    max_x=floor.dimensions[0]
    max_y=floor.dimensions[1]
    newfloor=floor
    for h in range (0,int(5*max_x)):
        newfloor.cells[random.randint(0,max_x-1)][random.randint(0,max_y-1)].open=True

    for h in range(0,9):
        for i in range(0,max_x):
            for j in range(0,max_y):
                for x in newfloor.cells[i][j].second_order_neighbors:
                    if x.open==True:
                        newfloor.cells[i][j].probability+=3
                    else:
                        newfloor.cells[i][j].probability-=0.55
                if i in [0,max_x-1] or j in [0,max_y-1]:
                    newfloor.cells[i][j].probability=0
                    newfloor.cells[i][j].open=False
        for i in range(0,max_x):
            for j in range(0,max_y):
                if newfloor.cells[i][j].probability/8>=random.gauss(0.4,0.2):
                    newfloor.cells[i][j].open=True
                else:
                    newfloor.cells[i][j].open=False
                newfloor.cells[i][j].probability=random.choice([0,newfloor.cells[i][j].probability/2])
                newfloor.cells[i][j].probability=random.choice([0,newfloor.cells[i][j].probability/3])

    if complete==True:
        for i in range(0,max_x):
            for j in range(0,max_y):
                if newfloor.cells[i][j].open==False:
                    MapTiles.Wall(newfloor,i,j)

def experimental_automaton(floor, complete=True,placements=1000):
    max_x=floor.dimensions[0]
    max_y=floor.dimensions[1]
    newfloor=floor

    golden_seed(floor,placements=placements)

    for passes in ((2,9),(3,8),(3,7),(2,8),(3,8),(6,8)):
        primary_automaton_step(floor,passes)

    for passes in ([3,12],[8,14],[7,15]):
        secondary_automaton_step(floor,passes)

    for passes in ((7,8),(4,8)):
        primary_automaton_step(floor,passes)

    opener(floor)
    opener(floor)
    primary_automaton_step(floor,(5,8))
    secondary_automaton_step(floor,(5,14))
    opener(floor)
    edger(floor)




    if complete==True:
        for i in range(0,max_x):
            for j in range(0,max_y):
                if newfloor.cells[i][j].open==False:
                    MapTiles.Wall(newfloor,i,j)

def golden_seed(floor,placements=1000):
    max_x=floor.dimensions[0]
    max_y=floor.dimensions[1]
    newfloor=floor

    seedling=floor.cells[random.randint(2,max_x-3)][random.randint(2,max_x-3)]

    seedling.open=True
    opened_cells=[seedling]

    for i in range(0,placements):
        edgepiece=random.choice([floor.cells[0][random.randint(0,max_y-1)],floor.cells[max_x-1]
        [random.randint(0,max_y-1)],floor.cells[random.randint(0,max_x-1)][0],floor.cells[random.randint(0,max_x-1)][max_y-1],random.choice(opened_cells)]) #random.choice(opened_cells)
        startpos=random.choice(opened_cells)
        newcell=floor.cells[startpos.location[0]-(int((startpos.location[0]-edgepiece.location[0])/1.618))][startpos.location[1]-(int((startpos.location[1]-edgepiece.location[1])/1.618))]
        newcell.open=True
        opened_cells.append(newcell)

def primary_automaton_step(floor,rule):
    for i in floor.nonindexedcells:
        i.probability=0
        for j in i.immediate_neighbors:
            if j.open==True:
                i.probability+=1

    for i in floor.nonindexedcells:
        if i.probability>=rule[0] and i.probability<=rule[1]:
            i.open=True
        else:
            i.open=False
        i.probability=0

def secondary_automaton_step(floor,rule):
    for i in floor.nonindexedcells:
        i.probability=0
        for j in i.second_order_neighbors:
            if j.open==True:
                i.probability+=1

    for i in floor.nonindexedcells:
        if i.probability>=rule[0] and i.probability<=rule[1]:
            i.open=True
        else:
            i.open=False
        i.probability=0

def opener(floor):
    for i in floor.nonindexedcells:
        i.probability=0
        for j in i.immediate_neighbors:
            if j.open:
                i.probability+=1

    for i in floor.nonindexedcells:
        neighboragreement=0
        for j in i.immediate_neighbors:
            if j.open==False and j.probability==2:
                neighboragreement+=1
        if i.probability==2 and neighboragreement==2:
            i.open=True

def edger(floor):
    for i in range(0,floor.dimensions[0]):
        for j in range(0,floor.dimensions[1]):
            if i in [0,floor.dimensions[0]-1] or j in [0,floor.dimensions[1]-1]:
                floor.cells[i][j].probability=0
                floor.cells[i][j].open=False



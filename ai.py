__author__ = 'Alan'
import Shell
import BaseClasses
import random

def standard_ai(self):
    #start with non-turn-consuming actions
        for i in self.equipped_items:
            if hasattr(i,'sortingtype') and i.sortingtype=='weapon':
                if len(i.equipped)<self.iprefs['wield preference']:
                    self.equip(i)

        #decide if any abilities should be used
        random.shuffle(self.abilities)
        for i in self.abilities:
            chance=i.decide()
            if random.random()<chance[0]:
                i.enemy_activation()
                return

        #If no target, choose a target
        if self.target!=None and self.target not in self.detected_creatures:
            if random.random()>0.9:
                self.target=None
            elif len(self.path)>1:
                self.follow_path()
                return
            else: self.target=None
        if self.target!=None and self.target.alive==False:
            self.target=None
            self.path=[]
        if self.target==None:
            targetvalue=0
            for i in self.detected_creatures:
                if self.hostilitycheck(i) and i.alive:
                    if self.affinity[i]<targetvalue:
                        targetvalue=self.affinity[i]
                        self.target=i
        #If we have a target and it is visible, chase and kill
        if self.target!=None and self.target in self.detected_creatures:
            if self.path==[] or self.target not in self.path[0].contents:
                self.get_path(self.target.floor.cells[self.target.location[0]][self.target.location[1]])

            self.follow_path()
            return
        #Follow steps in the action queue if they exist
        if self.action_queue!=[]:
            instructions=self.action_queue.pop(0)
            if instructions[0]=='unequip':
                #format is command, item, current equipment location
                if self in Shell.shell.player.visible_creatures:
                    self.unequip(instructions[1],log=True)
                else:
                    self.unequip(instructions[1],log=False)
            elif instructions[0]=='equip':
                #format is command, item, limb
                instructions[2].equip(instructions[1])
                if self in Shell.shell.player.visible_creatures:
                    Shell.messages.append("{} equips {}".format(self.name,instructions[1].name))

        #If we are not in combat, maybe we should pick up some items
        #How many weapons are we currently wielding?
        equipped_weapons=0
        for i in self.equipped_items:
            if hasattr(i,'sortingtype') and i.sortingtype=='weapon':
                equipped_weapons+=1
        #take inventory of surrounding items
        for i in self.visible_items:
            if isinstance(i,BaseClasses.Item) or isinstance(i,BaseClasses.Limb): pass
            else: continue
            self.value_item(i)
            if hasattr(i,'wield') and self.movemass+i.mass<self.iprefs['weight threshold']:
                #See if it outvalues what we currently have equipped
                for j in self.limbs:
                    if i.wield in j.primaryequip:
                        if j.equipment[i.wield]==None and i.wield=='grasp':
                            #don't wield more weapons than you want
                            if hasattr(i,'sortingtype') and i.sortingtype=='weapon' and equipped_weapons>=self.iprefs['desired weapons']:
                                continue
                            #don't wield shields until you have the number of weapons you desire
                            elif hasattr(i,'sortingtype') and i.sortingtype=='armor' and equipped_weapons<self.iprefs['desired weapons']:
                                continue
                        if j.equipment[i.wield]==None or self.item_values[i]>self.item_values[j.equipment[i.wield]]:
                            #If we are standing on it, pick it up
                            if i.location==self.location:
                                self.inventory_add(i)
                                try: self.floor.cells[self.location[0]][self.location[1]].contents.remove(i)
                                except ValueError: pass
                                i.location=[None,None]
                                if j.equipment[i.wield]!=None:
                                    self.action_queue.append(['unequip',j.equipment[i.wield],j])
                                self.action_queue.append(['equip',i,j])
                            else:
                                self.get_path(self.floor.cells[i.location[0]][i.location[1]])
                                self.target=i
                                self.follow_path()
                                self.target=None
                            #self.chase(i)
                            return

        #Even if it's useless for us, take it if it is above collection threshold but won't put us over weight
            if self.movemass+i.mass<self.iprefs['weight threshold'] and self.item_values[i]>self.iprefs['collection threshold']:
                if i.location==self.location:
                    self.inventory_add(i)
                    try: self.floor.cells[self.location[0]][self.location[1]].contents.remove(i)
                    except: pass
                    i.location=[None,None]
                else: self.chase(i)
                return


        if self.master==None:
            self.wander()
        elif random.random()*7>self.floor.cells[self.location[0]][self.location[1]].distance_to(
                self.master.floor.cells[self.master.location[0]][self.master.location[1]]): self.wander()
        else:
            self.get_path(self.master.floor.cells[self.master.location[0]][self.master.location[1]])
            self.follow_path()

def dazed_ai(self):
    movement=[random.choice([-1,0,1]),random.choice([-1,0,1])]
    self.move(movement,force_attack=True,free=True)


__author__ = 'Alan'


from Materials import *
from BaseClasses import *
from Attacks import *



import BaseClasses as B







#Attacktype can be None, stab, slash, bludgeon, or whip
#damagetype indicates damage types the object can sustain in addition to material damage


##############################################ITEMS###################################################################


############################################BodyParts#######################################
#TODO: Vital organs should have a separate entry here, with different effects for being damaged (eg. bruising the brain should greatly reduce focus or cause loss of conciousness. Lung damage should greatly increase stamina costs, etc)

class Bone(Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.5,radius=0.03,in_radius=0,material=Bone_Material,name='bone',plural=False,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.plural=plural
        self.material=material(quality=quality)
        if isinstance(self.material,Bone_Material):
            self.name=name
        else:
            self.name=self.material.name+" "+name
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=True
        self.wield='grasp'
        self.curvature=0
        self.attacktype=['bludgeon']
        self.function=1
        self.recalc()







class Flesh(Item):
    #length is limb length in meters
    #in_radius is the inner radius of the flesh
    #out_radius is the radius of the skin
    def __init__(self,length=0.5,in_radius=0.03,out_radius=0.05,material=Flesh_Material,name='flesh',plural=False,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.plural=plural
        self.material=material(quality=quality)
        if isinstance(self.material,Flesh_Material):
            self.name=name
        else:
            self.name=self.material.name+' '+name
        self.length=length
        self.radius=out_radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='grasp'
        self.curvature=0
        self.attacktype=None
        self.function=1
        self.recalc()





############################################Weapons#########################################
#TODO: Blade edge should wear with use, especially upon striking hard targets. Needs to be sharpenable as well.

#TODO: Stab attacks still require implementation. Need to be sure that both stab and slash attacks can be used.

class LongSword(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1,edge=0.00001,tip=0.0000001,width=0.035,thickness=0.007,material=Iron,quality=1):
        super().__init__()
        self.material=material(quality=quality)
        self.plural=False
        self.name=self.material.name+' long sword'
        self.length=length
        self.edge=edge
        self.tip=tip
        self.width=width
        self.thickness=thickness
        self.radius=self.thickness
        self.parry=True
        self.wield='grasp'
        self.curvature=0
        self.attacktype=['stab','slash']
        self.function=1
        self.attacks=[Slash_1H,Stab_1H]
        self.recalc()
        self.damagetype.append('blunt')

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*self.width*self.thickness)
        self.movemass=self.mass
        self.centermass=self.length*0.1
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.r=self.width


class Gladius(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=0.6,edge=0.00001,tip=0.0000001,width=0.035,thickness=0.007,material=Iron,quality=1):
        self.material=material(quality=quality)
        self.length=length
        self.edge=edge
        self.tip=tip
        self.width=width
        self.thickness=thickness
        self.parry=True
        self.mass=self.material.density*(self.length*self.width*self.thickness)
        self.wield='grasp'
        self.centermass=length*0.2
        self.curvature=0
        self.attacktype=['stab','slash']
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.damagetype=self.material.damagetype
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.damagetype.append('blunt')
        self.movemass=self.mass


class Knife(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=0.3,edge=0.000005,tip=0.000000025,width=0.035,thickness=0.01,material=Iron,quality=1):
        self.material=material(quality=quality)
        self.length=length
        self.edge=edge
        self.tip=tip
        self.width=width
        self.thickness=thickness
        self.parry=True
        self.mass=self.material.density*(self.length*self.width*self.thickness)
        self.wield='grasp'
        self.centermass=length*0.4
        self.curvature=0
        self.attacktype=['stab','slash']
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.damagetype=self.material.damagetype
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.damagetype.append('blunt')
        self.movemass=self.mass


class Saber(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1,edge=0.000005,tip=0.0000002,width=0.035,thickness=0.006,material=Iron,quality=1):
        self.material=material(quality=quality)
        self.length=length
        self.edge=edge
        self.tip=tip
        self.width=width
        self.thickness=thickness
        self.parry=True
        self.mass=self.material.density*(self.length*self.width*self.thickness)
        self.wield='grasp'
        self.centermass=length*0.3
        self.curvature=0.2
        self.attacktype=['stab','slash']
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.damagetype=self.material.damagetype
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.damagetype.append('blunt')
        self.movemass=self.mass


class Claymore(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1.3,edge=0.00001,tip=0.0000001,width=0.04,thickness=0.008,material=Iron,quality=1):
        self.material=material(quality=quality)
        self.length=length
        self.edge=edge
        self.tip=tip
        self.width=width
        self.thickness=thickness
        self.parry=True
        self.mass=self.material.density*(self.length*self.width*self.thickness)
        self.wield='grasp'
        self.centermass=length*0.1
        self.curvature=0
        self.attacktype=['stab','slash']
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.damagetype=self.material.damagetype
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.damagetype.append('blunt')
        self.movemass=self.mass


class Mace(Item):
    #length is length of mace in meters
    #head is head radius in meters
    def __init__(self,length=0.8,head=0.055,material=Iron,quality=1):
        super().__init__()
        self.material=material(quality=quality)
        self.length=length
        self.head=head
        self.parry=True
        self.name=self.material.name+' mace'
        self.wield='grasp'
        self.curvature=0.5
        self.attacktype=['bludgeon']
        self.function=1
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.attacks=[Bludgeon_1H]
        self.recalc()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*3.14*0.005**2+1.33*3.14*self.head**3)
        self.centermass=self.length*0.8
        self.I=self.mass*self.centermass**2
        self.contactarea=0.5*(1-self.curvature)*3.14*self.head**2
        self.radius=self.head
        self.thickness=0.02
        self.r=0.015
        self.movemass=self.mass


class FlangedMace(Item):
    #length is length of mace in meters
    #head is head radius in meters
    #contactarea is the contact area of a flange or spike in square meters
    def __init__(self,length=0.8,head=0.06,contactarea=.0008,material=Iron,quality=1):
        self.material=material(quality=quality)
        self.length=length
        self.head=head
        self.contactarea=contactarea
        self.parry=True
        self.mass=self.material.density*(self.length*3.14*0.005**2+1.33*3.14*self.head**3)
        self.wield='grasp'
        self.centermass=length*0.8
        self.attacktype=['bludgeon']
        self.I=self.mass*self.centermass**2
        self.damagetype=self.material.damagetype
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.damagetype.append('blunt')
        self.movemass=self.mass

class WarHammer(Item):
    #length is length of war hammer in meters
    #headsize is the volume of the head in cubic meters
    #contactarea is the contact area of the spike in square meters
    def __init__(self,length=1.1,headsize=0.001,contactarea=.00005,material=Iron,quality=1):
        self.material=material(quality=quality)
        self.length=length
        self.headsize=headsize
        self.contactarea=contactarea
        self.parry=True
        self.mass=self.material.density* self.headsize
        self.wield='grasp'
        self.centermass=length*0.8
        self.attacktype=['bludgeon']
        self.I=self.mass*self.centermass**2
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.damagetype=self.material.damagetype
        self.movemass=self.mass

class Spear(Item):
    #length is spear length in meters
    #tip is tip surface area in square meters
    #thickness is shaft thickness in meters
    def __init__(self,length=2,tip=0.000000025,thickness=0.01,material=Iron,quality=1):
        super().__init__()
        self.material=material(quality=quality)
        self.plural=False
        self.name=self.material.name+' spear'
        self.length=length
        self.tip=tip
        self.thickness=thickness
        self.radius=self.thickness
        self.parry=True
        self.wield='grasp'
        self.curvature=0
        self.attacktype=['stab','slash']
        self.function=1
        self.attacks=[Stab_1H]
        self.recalc()
        self.damagetype.append('blunt')

    def recalc(self):
        self.material_import()
        self.mass=0.5*self.density*(3.14*self.length*self.thickness**2)
        self.movemass=self.mass
        self.centermass=self.length*0.5
        self.I=(1/12)*self.mass*self.length**2
        self.r=self.thickness
        print(self.mass)


class Axe(Item):
    def __init__(self):
        pass







############################################Armor####################################################################

class Chest(Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.9,radius=0.102,in_radius=0.1,material=Iron,plural=False,quality=1):
        super().__init__()
        self.plural=plural
        self.material=material(quality=quality)
        self.name=self.material.name+' plate armor'
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='chest'
        self.curvature=0
        self.attacktype=[]
        self.coverage=0.95
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.function=1
        self.recalc()

    def recalc(self):
        self.material_import()
        self.mass=self.material.density*(self.length*(self.radius**2-self.in_radius**2))*3.14
        self.centermass=self.length*0.5
        self.thickness=self.radius-self.in_radius
        self.r=self.radius
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.movemass=self.mass

class Glove(Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.4,radius=0.025,in_radius=0.022,material=Iron,plural=False,quality=1):
        super().__init__()
        self.plural=plural
        self.material=material(quality=quality)
        self.name=self.material.name+' gauntlet'
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='glove'
        self.curvature=0.2
        self.attacktype=[]
        self.coverage=0.95
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.function=1
        self.recalc()

    def recalc(self):
        super().recalc()
        self.r=self.length/2

class Legging(Item):
    def __init__(self,length=0.8,radius=0.087,in_radius=0.085,material=Iron,plural=False,quality=1):
        super().__init__()
        self.plural=plural
        self.material=material(quality=quality)
        self.name=self.material.name+' greave'
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='legging'
        self.curvature=0.1
        self.attacktype=[]
        self.coverage=0.75
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.function=1
        self.recalc()

    def recalc(self):
        super().recalc()
        self.r=self.radius

class Armlet(Item):
    def __init__(self,length=0.375,radius=0.0548,in_radius=0.052,material=Iron,plural=False,quality=1):
        super().__init__()
        self.plural=plural
        self.material=material(quality=quality)
        self.name=self.material.name+' armlet'
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.thickness=self.radius-in_radius
        self.r=self.radius
        self.parry=False
        self.wield='armlet'
        self.curvature=0.1
        self.attacktype=[]
        self.coverage=0.75
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.function=1
        self.recalc()

    def recalc(self):
        super().recalc()
        self.mass=2*self.mass
        self.movemass=self.mass
        self.r=self.radius

class Boot(Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.35,radius=0.038,in_radius=0.035,material=Iron,plural=False,quality=1):
        super().__init__()
        self.plural=plural
        self.material=material(quality=quality)
        self.name=self.material.name+' boot'
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='boot'
        self.curvature=0.2
        self.attacktype=[]
        self.coverage=0.95
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.function=1
        self.recalc()

    def recalc(self):
        super().recalc()
        self.r=self.length

class Helm(Item):
    def __init__(self,length=0.1,radius=0.082,in_radius=0.08,material=Iron,plural=False,quality=1):
        super().__init__()
        self.plural=plural
        self.material=material(quality=quality)
        self.name=self.material.name+' helm'
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='helmet'
        self.curvature=0
        self.attacktype=[]
        self.coverage=0.55
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.function=1
        self.recalc()

    def recalc(self):
        super().recalc()
        self.r=self.length

class GreatHelm(Item):
    def __init__(self,length=0.2,radius=0.082,in_radius=0.08,material=Iron,plural=False,quality=1):
        super().__init__()
        self.plural=plural
        self.material=material(quality=quality)
        self.name=self.material.name+' greathelm'
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='helmet'
        self.vision_blocking=0.6
        self.sound_blocking=0.5
        self.smell_blocking=0.8
        self.curvature=0
        self.attacktype=[]
        self.coverage=1
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.function=1
        self.recalc()

    def recalc(self):
        super().recalc()
        self.r=self.length

class Shield(Item):
    def __init__(self,length=0.02,radius=0.36,in_radius=0,material=Iron,plural=False,quality=1):
        super().__init__()
        self.image='c:/Project/shield.png'
        self.plural=plural
        self.material=material(quality=quality)
        self.name=self.material.name+' shield'
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.block=True
        self.wield='grasp'
        self.curvature=0
        self.coverage=0.95
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.function=1
        self.material.youngs=self.material.youngs/100
        self.defaultmaterial=material
        self.attacks=[Shield_Bash]
        self.recalc()

    def recalc(self):
        if isinstance(self.material,self.defaultmaterial):
            pass
        else:
            self.material.youngs=self.material.youngs/100
            self.defaultmaterial=type(self.material)
        self.material_import()
        self.thickness=self.length
        self.r=self.radius
        self.mass=0.25*self.material.density*(self.length*(self.radius**2-self.in_radius**2))*3.14
        self.centermass=self.length*0.5
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.contactarea=3.14*self.radius**2

class Buckler(Item):
    def __init__(self,length=0.02,radius=0.1,in_radius=0,material=Iron,plural=False,quality=1):
        super().__init__()
        self.image='c:/Project/shield.png'
        self.plural=plural
        self.material=material(quality=quality)
        self.defaultmaterial=material
        self.name=self.material.name+' buckler'
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.block=True
        self.wield='grasp'
        self.centermass=length*0.5
        self.curvature=0
        self.coverage=0.95
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0,'pierce':0}
        self.function=1
        self.material.youngs=self.material.youngs/100
        self.attacks=[Shield_Bash]
        self.recalc()

    def recalc(self):
        if isinstance(self.material,self.defaultmaterial):
            pass
        else:
            self.material.youngs=self.material.youngs/100
            self.defaultmaterial=type(self.material)
        self.material_import()
        self.thickness=self.length
        self.r=self.radius
        self.mass=0.25*self.material.density*(self.length*(self.radius**2-self.in_radius**2))*3.14
        self.centermass=self.length*0.5
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.contactarea=3.14*self.radius**2
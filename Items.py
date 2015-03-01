__author__ = 'Alan'

from Materials import *
from BaseClasses import *
from Attacks import *





#Attacktype can be None, stab, slash, bludgeon, or whip
#damagetype indicates damage types the object can sustain in addition to material damage


##############################################ITEMS###################################################################


############################################BodyParts#######################################
class Bone(Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.5,radius=0.03,in_radius=0,material=Bone_Material,name='bone',plural=False):
        self.plural=plural
        self.material=material()
        if isinstance(self.material,Bone_Material):
            self.name=name
        else:
            self.name=self.material.name+" "+name
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.thickness=self.radius-in_radius
        self.parry=True
        self.mass=self.material.density*(self.length*(self.radius**2-in_radius**2))*3.14
        self.wield='grasp'
        self.centermass=length*0.5
        self.curvature=0
        self.attacktype=['bludgeon']
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.damagetype=self.material.damagetype
        self.dissipationfactor=self.material.dissipationfactor
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0}
        self.function=1







class Flesh(Item):
    #length is limb length in meters
    #in_radius is the inner radius of the flesh
    #out_radius is the radius of the skin
    def __init__(self,length=0.5,in_radius=0.03,out_radius=0.05,material=Flesh_Material,name='flesh',plural=False):
        self.plural=plural
        self.material=material()
        if isinstance(self.material,Flesh_Material):
            self.name=name
        else:
            self.name=self.material.name+' '+name
        self.length=length
        self.radius=out_radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.thickness=self.radius-self.in_radius
        self.parry=False
        self.mass=self.material.density*(self.length*self.radius**2-self.length*self.in_radius**2)*3.14
        self.wield='grasp'
        self.centermass=length*0.5
        self.curvature=0
        self.attacktype=None
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.damagetype=self.material.damagetype
        self.damage={'bruise':0,'crack':0,'dent':0,'bend':0,'deform':0,'break':0,'cut':0,'shatter':0,'crush':0,'burn':0}
        self.dissipationfactor=self.material.dissipationfactor
        self.function=1





############################################Weapons#########################################
class LongSword(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1,edge=0.00001,tip=0.0000001,width=0.035,thickness=0.007,material=Iron):
        self.material=material()
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
        self.damagetype.append('blunt')

class Gladius(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=0.6,edge=0.00001,tip=0.0000001,width=0.035,thickness=0.007,material=Iron):
        self.material=material()
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
        self.damagetype.append('blunt')


class Knife(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=0.3,edge=0.000005,tip=0.000000025,width=0.035,thickness=0.01,material=Iron):
        self.material=material()
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
        self.damagetype.append('blunt')


class Saber(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1,edge=0.000005,tip=0.0000002,width=0.035,thickness=0.006,material=Iron):
        self.material=material()
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
        self.damagetype.append('blunt')


class Claymore(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1.3,edge=0.00001,tip=0.0000001,width=0.04,thickness=0.008,material=Iron):
        self.material=material()
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
        self.damagetype.append('blunt')


class Mace(Item):
    #length is length of mace in meters
    #head is head radius in meters
    def __init__(self,length=0.8,head=0.06,material=Iron):
        self.material=material()
        self.length=length
        self.head=head
        self.parry=True
        self.mass=self.material.density*(self.length*3.14*0.005**2+1.33*3.14*self.head**3)
        self.wield='grasp'
        self.centermass=length*0.8
        self.curvature=0.3
        self.contactarea=0.5(1-self.curvature)*3.14*self.head**2
        self.attacktype=['bludgeon']
        self.I=self.mass*self.centermass**2


class FlangedMace(Item):
    #length is length of mace in meters
    #head is head radius in meters
    #contactarea is the contact area of a flange or spike in square meters
    def __init__(self,length=0.8,head=0.06,contactarea=.0008,material=Iron):
        self.material=material()
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
        self.damagetype.append('blunt')

class WarHammer(Item):
    #length is length of war hammer in meters
    #headsize is the volume of the head in cubic meters
    #contactarea is the contact area of the spike in square meters
    def __init__(self,length=1.1,headsize=0.001,contactarea=.00005,material=Iron):
        self.material=material()
        self.length=length
        self.headsize=headsize
        self.contactarea=contactarea
        self.parry=True
        self.mass=self.material.density*(self.headsize)
        self.wield='grasp'
        self.centermass=length*0.8
        self.attacktype=['bludgeon']
        self.I=self.mass*self.centermass**2
        self.damagetype=self.material.damagetype


class Spear(Item):
    #length is length of the spear in meters
    #tip is area of tip in square meters
    def __init__(self,length=1.5,tip=0.000000025,material=Iron):
        self.material=material()
        self.length=length
        self.tip=tip
        self.parry=True
        self.mass=self.material.density*(0.0001)+self.length
        self.wield='grasp'
        self.centermass=length*0.5
        self.curvature=0
        self.attacktype=['stab']
        self.I=(1/12)*self.length**3+self.mass*self.centermass**2
        self.damagetype=self.material.damagetype
        self.damagetype.append('blunt')


class Axe(Item):
    def __init__(self):
        pass




weapon=Spear()

print(weapon.mass,weapon.I)



######################################################################################################################


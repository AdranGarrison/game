__author__ = 'Alan'


from Materials import *
from BaseClasses import *
from Attacks import *



import BaseClasses as B
import Enchantments







#Attacktype can be None, stab, slash, bludgeon, or whip
#damagetype indicates damage types the object can sustain in addition to material damage


##############################################ITEMS###################################################################


############################################BodyParts#######################################
#TODO: Vital organs should have a separate entry here, with different effects for being damaged (eg. bruising the brain should greatly reduce focus or cause loss of conciousness. Lung damage should greatly increase stamina costs, etc)

class Bone(Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.5,radius=0.03,in_radius=0,material=Bone_Material,name='bone',plural=False,quality=1,threshold=0,**kwargs):
        super().__init__(**kwargs)
        self.base_descriptor='A bone from some creature or another'
        self.plural=plural
        self.material=material(quality=quality)
        self.names=['bone']
        self.knowledge_level['truename']=1
        if isinstance(self.material,Bone_Material):
            self.truename=name
            self.name=name
        else:
            self.truename=self.material.name+" "+name
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
        self.threshold=threshold
        self.recalc()

class Flesh(Item):
    #length is limb length in meters
    #in_radius is the inner radius of the flesh
    #out_radius is the radius of the skin
    def __init__(self,length=0.5,in_radius=0.03,out_radius=0.05,material=Flesh_Material,name='flesh',plural=False,quality=1,threshold=0,**kwargs):
        super().__init__(**kwargs)
        self.base_descriptor='Flesh carved from some creature or another'
        self.plural=plural
        self.material=material(quality=quality)
        self.names=['flesh']
        self.knowledge_level['truename']=1
        if isinstance(self.material,Flesh_Material):
            self.name=name
            self.truename=name
        else:
            self.truename=self.material.name+' '+name
            self.name=self.material.name+' '+name
        self.length=length
        self.radius=out_radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='grasp'
        self.curvature=0
        self.attacktype=None
        self.threshold=threshold
        self.function=1
        self.recalc()

class Hair(Item):
    #length is limb length in meters
    #in_radius is the inner radius of the flesh
    #out_radius is the radius of the skin
    def __init__(self,length=0.5,in_radius=0.03,out_radius=0.05,material=Hair_Material,name='hair',plural=False,quality=1,threshold=0,**kwargs):
        super().__init__(painfactor=0,**kwargs)
        self.base_descriptor='Hair from some creature or another'
        self.coverage=0.1
        self.plural=plural
        self.material=material(quality=quality)
        self.names=['hair']
        self.knowledge_level['truename']=1
        if isinstance(self.material,Hair_Material) or isinstance(self.material,Fur):
            self.name=name
            self.truename=name
        else:
            self.name=name
            self.truename=''.join((self.material.name,' ',self.name))
        self.length=length
        self.radius=out_radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='grasp'
        self.curvature=0
        self.attacktype=None
        self.threshold=threshold
        self.function=1
        self.recalc()




############################################Weapons#########################################
#TODO: Blade edge should wear with use, especially upon striking hard targets. Needs to be sharpenable as well.


class LongSword(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1,edge=0.00001,tip=0.0000001,width=0.035,thickness=0.007,material=Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','sword','long sword']
        self.base_descriptor='A straight, double-edged sword with a long blade. A well-balanced and versatile weapon for cutting and thrusting'
        self.sortingtype='weapon'
        self.material=material(quality=quality)
        self.plural=False
        self.truename=self.material.name+' long sword'
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
        self.attacks=[Slash_1H,Stab_1H,Slash_2H,Stab_2H]
        self.recalc()
        self.damagetype.append('blunt')
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*self.width*self.thickness)
        self.movemass=self.mass
        self.centermass=self.length*0.2
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.r=self.width
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class Gladius(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=0.6,edge=0.00001,tip=0.0000001,width=0.035,thickness=0.007,material=Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','sword','gladius']
        self.base_descriptor='A two-edged short sword balanced for cutting, chopping, or thrusting'
        self.sortingtype='weapon'
        self.material=material(quality=quality)
        self.plural=False
        self.truename=self.material.name+' gladius'
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
        self.attacks=[Slash_1H,Stab_1H,Slash_2H,Stab_2H]
        self.recalc()
        self.damagetype.append('blunt')
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*self.width*self.thickness)
        self.movemass=self.mass
        self.centermass=self.length*0.3
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.r=self.width
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class Knife(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=0.3,edge=0.000005,tip=0.000000025,width=0.035,thickness=0.01,material=Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','dagger']
        self.base_descriptor='A short, bladed weapon with a very sharp point. Suitable for throwing, slashing, or stabbing'
        self.sortingtype='weapon'
        self.material=material(quality=quality)
        self.plural=False
        self.truename=self.material.name+' dagger'
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
        self.attacks=[Slash_1H,Stab_1H,Slash_2H,Stab_2H]
        self.recalc()
        self.damagetype.append('blunt')
        self.generate_descriptions()


    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*self.width*self.thickness)
        self.movemass=self.mass
        self.centermass=self.length*0.4
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.r=self.width
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class Saber(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1,edge=0.000005,tip=0.0000002,width=0.035,thickness=0.006,material=Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','sword','saber']
        self.base_descriptor='A curved, single-edge sword optimized for cutting'
        self.sortingtype='weapon'
        self.material=material(quality=quality)
        self.plural=False
        self.truename=self.material.name+' saber'
        self.length=length
        self.edge=edge
        self.tip=tip
        self.width=width
        self.thickness=thickness
        self.radius=self.thickness
        self.parry=True
        self.wield='grasp'
        self.curvature=0.2
        self.attacktype=['stab','slash']
        self.function=1
        self.attacks=[Slash_1H,Stab_1H,Stab_2H,Slash_2H]
        self.recalc()
        self.damagetype.append('blunt')
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*self.width*self.thickness)
        self.movemass=self.mass
        self.centermass=self.length*0.3
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.r=self.width
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class Claymore(Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1.3,edge=0.00001,tip=0.0000001,width=0.04,thickness=0.008,material=Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','sword','claymore']
        self.base_descriptor='A broad, heavy longsword suitable only for those strong enough to effectively wield it'
        self.sortingtype='weapon'
        self.material=material(quality=quality)
        self.plural=False
        self.truename=self.material.name+' claymore'
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
        self.attacks=[Slash_1H,Stab_1H,Slash_2H,Stab_2H]
        self.recalc()
        self.damagetype.append('blunt')
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*self.width*self.thickness)
        self.movemass=self.mass
        self.centermass=self.length*0.2
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.r=self.width
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class Mace(Item):
    #length is length of mace in meters
    #head is head radius in meters
    def __init__(self,length=0.8,head=0.06,material=Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','club','mace']
        self.base_descriptor='A heavy, blunt weapon for delivering powerful blows'
        self.sortingtype='weapon'
        self.material=material(quality=quality)
        self.length=length
        self.head=head
        self.parry=True
        self.truename=self.material.name+' mace'
        self.wield='grasp'
        self.curvature=0.5
        self.attacktype=['bludgeon']
        self.function=1
        self.attacks=[Bludgeon_1H,Bludgeon_2H]
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*3.14*0.005**2+1.33*3.14*self.head**3)
        self.centermass=self.length*0.8
        self.I=self.mass*self.centermass**2
        self.contactarea=0.25*(1-self.curvature)*3.14*self.head**2
        self.radius=self.head
        self.thickness=0.02
        self.r=0.015
        self.movemass=self.mass
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class FlangedMace(Item):
    #length is length of mace in meters
    #head is head radius in meters
    #contactarea is the contact area of a flange or spike in square meters
    def __init__(self,length=0.8,head=0.06,contactarea=.0008,material=Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','club','flanged mace']
        self.sortingtype='weapon'
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
        self.damagetype.append('blunt')
        self.movemass=self.mass

class WarHammer(Item):
    #length is length of war hammer in meters
    #headvolume is the volume of the head of the warhammer
    #headsize is the area of the head in square meters
    #tip is the contact area of the spike in square meters
    #contactarea is the contact area of the hammer in square meters
    def __init__(self,length=1.1,headvolume=.0002,headsize=0.0005,tip=0.00005,material=Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','club','war hammer']
        self.base_descriptor='A long, heavy hammer with a head for bashing attacks and a spike for piercing through armor'
        self.sortingtype='weapon'
        self.material=material(quality=quality)
        self.length=length
        self.headvolume=headvolume
        self.headsize=headsize
        self.tip=tip
        self.parry=True
        self.truename=self.material.name+' war hammer'
        self.wield='grasp'
        self.curvature=0
        self.function=1
        self.attacks=[Bludgeon_1H,Swing_Pierce_1H,Bludgeon_2H,Swing_Pierce_2H]
        self.attacktype=['bludgeon']
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*3.14*0.005**2+self.headvolume)
        self.centermass=self.length*0.85
        self.I=self.mass*self.centermass**2
        self.contactarea=self.headsize
        self.radius=self.headsize**0.5
        self.thickness=0.02
        self.r=0.015
        self.movemass=self.mass
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius
        #print('warhammer mass, I',self.mass,self.I)

class Spear(Item):
    #length is spear length in meters
    #tip is tip surface area in square meters
    #thickness is shaft thickness in meters
    def __init__(self,length=2,tip=0.000000025,thickness=0.01,material=Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','polearm','spear']
        self.base_descriptor='A long pole weapon with a sharp tip for piercing attacks.'
        self.sortingtype='weapon'
        self.material=material(quality=quality)
        self.plural=False
        self.truename=self.material.name+' spear'
        self.length=length
        self.tip=tip
        self.thickness=thickness
        self.radius=self.thickness
        self.parry=True
        self.wield='grasp'
        self.curvature=0
        self.attacktype=['stab','slash']
        self.function=1
        self.attacks=[Stab_1H,Stab_2H]
        self.recalc()
        self.damagetype.append('blunt')
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=0.5*self.density*(3.14*self.length*self.thickness**2)
        self.movemass=self.mass
        self.centermass=self.length*0.5
        self.I=(1/12)*self.mass*self.length**2
        self.r=self.thickness
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius
        #print(self.mass)

class Axe(Item):
    def __init__(self,length=0.8,edge=0.00004,width=0.2,thickness=0.01,material=Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','axe']
        self.base_descriptor='A heavy, broad-headed bladed weapon. Somewhat clumsier than a sword but capable of delivering considerably more force.'
        self.sortingtype='weapon'
        self.material=material(quality=quality)
        self.plural=False
        self.truename=self.material.name+' axe'
        self.length=length
        self.edge=edge
        self.width=width
        self.thickness=thickness
        self.radius=self.thickness
        self.parry=True
        self.wield='grasp'
        self.curvature=0
        self.attacktype=['slash']
        self.function=1
        self.attacks=[Slash_1H,Slash_2H]
        self.recalc()
        self.damagetype.append('blunt')
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*(3.14*0.005**2+self.width*self.thickness*0.2))
        self.movemass=self.mass
        self.centermass=self.length*0.8
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.r=self.width
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class QuarterStaff(Item):
    def __init__(self,length=2,thickness=0.02,material=Wood,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','polearm','quarterstaff']
        self.base_descriptor='A long staff capable of delivering quick blows while keeping adversaries at range.'
        self.sortingtype='weapon'
        self.material=material(quality=quality)
        self.plural=False
        self.truename=self.material.name+' quarterstaff'
        self.length=length
        self.thickness=thickness
        self.radius=self.thickness
        self.parry=True
        self.wield='grasp'
        self.curvature=0
        self.attacktype=['stab','slash']
        self.function=1
        self.attacks=[Strike_1H,Blunt_Thrust_1H,Strike_2H,Blunt_Thrust_2H]
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(3.14*self.length*self.thickness**2)
        self.movemass=self.mass
        self.centermass=0.01
        self.I=(1/12)*self.mass*self.length**2
        self.r=self.thickness
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius




############################################Armor####################################################################

class Chest(Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.9,thickness='default',in_radius=0.1,material=Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality)
        if self.material.mode=='ductile' or self.material.mode=='brittle':
            self.names=['armor','chestpiece','plate armor']
            self.truename=self.material.name+' plate armor'
            self.base_descriptor='Armor which covers the torso. Offers excellent protection for those with the strength to wear it'
        else:
            self.names=['armor','chestpiece','vest']
            self.truename=self.material.name+' vest'
            self.base_descriptor='A thick vest for covering the torso. Effective at softening blows without significantly reducing mobility'
        if thickness=='default':
            thickness=self.material.default_thickness*thickness_factor
        self.default_thickness=self.material.default_thickness
        self.length=length*scale_factor
        self.radius=scale_factor*in_radius+thickness
        self.in_radius=in_radius*scale_factor
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='chest'
        self.curvature=0
        self.attacktype=[]
        self.coverage=0.95
        self.function=1
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.material.density*(self.length*(self.radius**2-self.in_radius**2))*3.14
        self.centermass=self.length*0.5
        self.thickness=self.radius-self.in_radius
        self.r=self.radius
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.movemass=self.mass
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class Glove(Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.4,thickness='default',in_radius=0.022,material=Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality)
        if self.material.mode=='ductile' or self.material.mode=='brittle':
            self.names=['armor','hand armor','gauntlet']
            self.base_descriptor='Heavy glove for protecting the hand from injury'
            self.truename=self.material.name+' gauntlet'
        else:
            self.names=['armor','hand armor','glove']
            self.base_descriptor='Offers protection for the hand and fingers without reducing dexterity'
            self.truename=self.material.name+' glove'
        if thickness=='default':
            thickness=self.material.default_thickness*2*thickness_factor
        self.default_thickness=self.material.default_thickness*2
        self.length=length*scale_factor
        self.radius=scale_factor*in_radius+thickness
        self.in_radius=in_radius*scale_factor
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='glove'
        self.curvature=0.2
        self.attacktype=[]
        self.coverage=0.95
        self.function=1
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        super().recalc()
        self.r=self.length/2

class Legging(Item):
    def __init__(self,length=0.8,thickness='default',in_radius=0.085,material=Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality)
        if self.material.mode=='ductile' or self.material.mode=='brittle':
            self.names=['armor','leg armor','greave']
            self.truename=self.material.name+' greave'
            self.base_descriptor='Heavy armor for the leg designed to deflect and absorb shock.'
        else:
            self.names=['armor','leg armor','legging']
            self.truename=self.material.name+' legging'
            self.base_descriptor='Flexible armor for the leg. Absorbs impact without hampering movement.'
        if thickness=='default':
            thickness=self.material.default_thickness*thickness_factor
        self.default_thickness=self.material.default_thickness
        self.length=length*scale_factor
        self.radius=scale_factor*in_radius+thickness
        self.in_radius=in_radius*scale_factor
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='legging'
        self.curvature=0.1
        self.attacktype=[]
        self.coverage=0.75
        self.function=1
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        super().recalc()
        self.r=self.radius

class Armlet(Item):
    def __init__(self,length=0.375,thickness='default',in_radius=0.052,material=Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality)
        if self.material.mode=='ductile' or self.material.mode=='brittle':
            self.names=['armor','arm guard','vambrace']
            self.truename=self.material.name+' vambrace'
            self.base_descriptor='Stiff and typically heavy plated armor for protecting the arm.'
        else:
            self.names=['armor','arm guard','bracer']
            self.truename=self.material.name+' bracer'
            self.base_descriptor='Lightweight arm protection. Softens blows without slowing the movement of the arm.'
        if thickness=='default':
            thickness=self.material.default_thickness*1.1*thickness_factor
        self.default_thickness=self.material.default_thickness*1.1
        self.length=length*scale_factor
        self.radius=scale_factor*in_radius+thickness
        self.in_radius=in_radius*scale_factor
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.thickness=self.radius-in_radius
        self.r=self.radius
        self.parry=False
        self.wield='armlet'
        self.curvature=0.1
        self.attacktype=[]
        self.coverage=0.75
        self.function=1
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        super().recalc()
        self.mass=2*self.mass
        self.movemass=self.mass
        self.r=self.radius

class Boot(Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.35,thickness='default',in_radius=0.035,material=Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['armor','footwear','boot']
        self.base_descriptor='Footwear worn for protection of the foot and ankle'
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality)
        self.truename=self.material.name+' boot'
        if thickness=='default':
            thickness=self.material.default_thickness*2*thickness_factor
        self.default_thickness=self.material.default_thickness*2
        self.length=length*scale_factor
        self.radius=scale_factor*in_radius+thickness
        self.in_radius=in_radius*scale_factor
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='boot'
        self.curvature=0.2
        self.attacktype=[]
        self.coverage=1
        self.function=1
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        super().recalc()
        self.r=self.length

class Helm(Item):
    def __init__(self,length=0.1,thickness='default',in_radius=0.08,material=Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality)
        if self.material.mode=='brittle' or self.material.mode=='ductile':
            self.names=['armor','hat','helm']
            self.truename=self.material.name+' helm'
            self.base_descriptor='Provides protection for the top and sides of the head without impeding vision or hearing'
        else:
            self.names=['armor','hat','cap']
            self.truename=self.material.name+' cap'
            self.base_descriptor='A thick hat for protecting the top and sides of the head'
        if thickness=='default':
            thickness=self.material.default_thickness*thickness_factor
        self.default_thickness=self.material.default_thickness
        self.length=length*scale_factor
        self.radius=scale_factor*in_radius+thickness
        self.in_radius=in_radius*scale_factor
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='helmet'
        self.curvature=0
        self.attacktype=[]
        self.coverage=0.55
        self.function=1
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        super().recalc()
        self.r=self.length

class GreatHelm(Item):
    def __init__(self,length=0.2,thickness='default',in_radius=0.08,material=Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality)
        if self.material.mode=='brittle' or self.material.mode=='ductile':
            self.names=['armor','hat','greathelm']
            self.truename=self.material.name+' greathelm'
            self.base_descriptor='A heavy helmet completely enclosing the face and protecting the neck. Offers excellent protection, but impedes vision and hearing'
            self.vision_blocking=0.6
            self.sound_blocking=0.5
            self.smell_blocking=0.8
        else:
            self.names=['armor','hat','hood']
            self.truename=self.material.name+' hood'
            self.base_descriptor='Thick covering for the head and neck. Provides considerable protection, but reduces ability to see and hear'
            self.vision_blocking=0.5
            self.sound_blocking=0.4
            self.smell_blocking=0.1
        if thickness=='default':
            thickness=self.material.default_thickness*thickness_factor
        self.default_thickness=self.material.default_thickness
        self.length=length*scale_factor
        self.radius=scale_factor*in_radius+thickness
        self.in_radius=in_radius*scale_factor
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield='helmet'
        self.curvature=0
        self.attacktype=[]
        self.coverage=1
        self.function=1
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        super().recalc()
        self.r=self.length

class Shield(Item):
    def __init__(self,length=0.02,radius=0.36,in_radius=0,material=Iron,plural=False,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['armor','shield']
        self.base_descriptor='A large, heavy shield for absorbing and deflecting blows'
        self.sortingtype='armor'
        self.image='c:/Project/shield.png'
        self.plural=plural
        self.material=material(quality=quality)
        self.truename=self.material.name+' shield'
        self.default_thickness=0.02
        self.length=length
        self.radius=radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.block=True
        self.wield='grasp'
        self.curvature=0
        self.coverage=0.95
        self.function=1
        self.material.youngs=self.material.youngs/100
        self.defaultmaterial=material
        self.attacks=[Shield_Bash,Shield_Bash_2H]
        self.recalc()
        self.generate_descriptions()

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
        self.movemass=self.mass
        self.centermass=self.length*0.5
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.contactarea=3.14*self.radius**2
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class Buckler(Item):
    def __init__(self,length=0.02,radius=0.1,in_radius=0,material=Iron,plural=False,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['armor','shield','buckler']
        self.base_descriptor='A small shield ideal for dueling which can be quickly moved to wherever it is needed most'
        self.sortingtype='armor'
        self.image='c:/Project/shield.png'
        self.plural=plural
        self.material=material(quality=quality)
        self.defaultmaterial=material
        self.default_thickness=0.02
        self.truename=self.material.name+' buckler'
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
        self.function=1
        self.material.youngs=self.material.youngs/100
        self.attacks=[Shield_Bash,Shield_Bash_2H]
        self.recalc()
        self.generate_descriptions()

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
        self.movemass=self.mass
        self.centermass=self.length*0.5
        self.I=(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.contactarea=3.14*self.radius**2
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius



class ExperimentalMace(Mace):
    def __init__(self,material=Iron,quality=1):
        super().__init__(material=material,quality=quality)
        self.attacks=[Experimental_Bash]

default_item_weights=[(Bone,0),(Flesh,0),(Hair,0),(LongSword,10),(Gladius,5),(Knife,7),(Saber,4),(Claymore,4),(Mace,8),
                 (WarHammer,3),(Spear,5),(Axe,6),(QuarterStaff,3),(Chest,8),(Glove,12),(Legging,12),(Armlet,12),
                (Boot,12),(Helm,8),(GreatHelm,3),(Shield,6),(Buckler,6)]
total_item_weight=sum(i[1] for i in default_item_weights)

hard_material_weights=[(Iron,10),(Bone_Material,7),(Wood,10),(Copper,10),(Brass,6),(Bronze,5),(Steel,4),(Aluminum,3),(Silver,2),(Duraluminum,1),(Zicral,1)]
soft_material_weights=[(Leather,10),(Cotton,10),(Wool,9),(Silk,5),(Spider_Silk,2),(Basalt_Fiber,1),(Fur,3),(Flesh_Material,1)]

def weighted_choice(pairs):
    total=0
    for i in pairs:
        total+=i[1]
    number=random.random()*total
    for i in pairs:
        if number<=i[1]:
            return i[0]
        else: number-=i[1]

def weighted_generation(weighted_items=default_item_weights,totalweight=total_item_weight,hard_materials=hard_material_weights,soft_materials=soft_material_weights):
    chosen_material=None
    choicenumber=random.random()*totalweight
    for i in weighted_items:
        if choicenumber<=i[1]:
            itemtype=i[0]
            break
        else:
            choicenumber-=i[1]
    if itemtype in (LongSword,Gladius,Knife,Saber,Claymore,Mace,WarHammer,Spear,Axe,QuarterStaff,Shield,Buckler):
        if random.random()<0.99:
            chosen_material=weighted_choice(hard_materials)
    if chosen_material==None:
        mats=hard_materials.copy()
        mats.extend(soft_materials)
        chosen_material=weighted_choice(mats)
    item=itemtype(material=chosen_material)
    item.randomize()
    return item




allitems=[Bone,Flesh,Hair,Limb,LongSword,Gladius,Knife,Saber,Claymore,Mace,WarHammer,Spear,Axe,QuarterStaff,
          Chest,Glove,Legging,Armlet,Boot,Helm,GreatHelm,Shield,Buckler]
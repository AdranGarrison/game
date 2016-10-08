__author__ = 'Alan'


#from Materials import *
#from BaseClasses import *
import Materials as M
import BaseClasses
from Attacks import *


import BaseClasses as B
import Enchantments









##############################################ITEMS###################################################################


############################################BodyParts#######################################

class Bone(BaseClasses.Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.5,radius=0.03,in_radius=0,material=M.Bone_Material,name='bone',plural=False,quality=1,threshold=0,**kwargs):
        super().__init__(**kwargs)
        self.base_descriptor='A bone from some creature or another'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.names=['bone']
        self.knowledge_level['truename']=1
        if isinstance(self.material,M.Bone_Material) or name!='bone':
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

class Flesh(BaseClasses.Item):
    #length is limb length in meters
    #in_radius is the inner radius of the flesh
    #out_radius is the radius of the skin
    def __init__(self,length=0.5,in_radius=0.03,out_radius=0.05,material=M.Flesh_Material,name='flesh',plural=False,quality=1,threshold=0,**kwargs):
        super().__init__(**kwargs)
        self.base_descriptor='Flesh carved from some creature or another'
        self.plural=plural
        try: self.material=material(quality=quality,power=self.power)
        except: self.material=material
        self.names=['flesh']
        self.knowledge_level['truename']=1
        if isinstance(self.material,M.Flesh_Material) or name!='flesh':
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

class Hair(BaseClasses.Item):
    #length is limb length in meters
    #in_radius is the inner radius of the flesh
    #out_radius is the radius of the skin
    def __init__(self,length=0.5,in_radius=0.03,out_radius=0.05,material=M.Hair_Material,name='hair',plural=False,quality=1,threshold=0,**kwargs):
        super().__init__(painfactor=0,**kwargs)
        self.base_descriptor='Hair from some creature or another'
        self.structural=False
        self.coverage=0.1
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.names=['hair']
        self.knowledge_level['truename']=1
        if isinstance(self.material,M.Hair_Material) or isinstance(self.material,M.Fur):
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
        self.minimum_function=0.9
        self.recalc()

class Feathers(BaseClasses.Item):
    #length is limb length in meters
    #in_radius is the inner radius of the flesh
    #out_radius is the radius of the skin
    def __init__(self,length=0.5,in_radius=0.03,out_radius=0.05,material=M.Feather,name='feathers',plural=True,quality=1,threshold=0,**kwargs):
        super().__init__(painfactor=0,**kwargs)
        self.base_descriptor='Feathers from some creature or another'
        self.structural=False
        self.coverage=0.1
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.names=['feathers']
        self.knowledge_level['truename']=1
        self.name=name
        self.truename=name
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
        self.minimum_function=0.5
        self.recalc()

class Scales(BaseClasses.Item):
    #length is limb length in meters
    #in_radius is the inner radius of the flesh
    #out_radius is the radius of the skin
    def __init__(self,length=0.5,in_radius=0.03,out_radius=0.05,material=M.Keratin,name='scales',plural=True,quality=1,threshold=0,**kwargs):
        super().__init__(painfactor=0,**kwargs)
        self.base_descriptor='Scales from some creature or another'
        self.coverage=1
        self.structural=False
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.material.mode="mail"
        self.link='scale'
        self.names=['scales']
        self.knowledge_level['truename']=1
        self.name=name
        self.truename=name
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

class Corpse(BaseClasses.Item):
    def __init__(self,creature=None,**kwargs):
        super().__init__(**kwargs)
        self.base_descriptor="The deceased body of a once-living creature"
        self.creature=creature
        self.image=self.creature.image
        self.color=self.creature.color
        self.mass=self.creature.mass
        self.movemass=self.creature.movemass
        self.thickness=1
        self.sortingtype='misc'
        self.truename="Corpse of {}".format(self.creature.name)
        self.names=["A corpse","Corpse of {}".format(self.creature.name)]
        self.name="The corpse of {}".format(self.creature.name)
        self.length=1
        self.radius=1
        self.material=BaseClasses.Material()
        self.material.name=''
        self.material.basicname=""
        self.youngs=1
        self.shear=1
        self.density=1000
        self.wetdamage=None
        self.quality=1
        self.acid_reaction='None'
        self.heat_reaction='None'
        self.burn_temp=10000
        self.burn_resistance=100
        #TODO: acid should react with corpses as it reacts with creatures
        #TODO: should be able to burn like a creature


    def recalc(self):
        pass

    def damageresolve(self,attack,attacker,reactionforce=False):
        if self.creature.limbs==[]:
            return
        if self in Shell.shell.player.visible_items:
            Shell.shell.player.visible_creatures.append(self.creature)
        random.choice(self.creature.limbs).damageresolve(attack,attacker,reactionforce=reactionforce)
        self.mass=self.creature.mass
        self.movemass=self.creature.movemass

    def on_turn(self):
        super().on_turn()
        self.creature.location=self.location
        self.creature.floor=self.floor

class Magic_Rune(BaseClasses.Item):
    def __init__(self,length=0.01,in_radius=0,out_radius=0.08,material=M.Aether,name='rune',plural=False,quality=1,threshold=0,**kwargs):
        super().__init__(**kwargs)
        self.base_descriptor='A rune for binding magic to matter'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.names=['markings','rune']
        self.truename='rune'
        self.name=name
        self.length=length
        self.radius=out_radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield=None
        self.curvature=0
        self.attacktype=None
        self.threshold=threshold
        self.function=1
        self.coverage=0.5
        self.recalc()

class Mind_Object(BaseClasses.Item):
    def __init__(self,length=0.01,in_radius=0,out_radius=0.08,material=M.Aether,name='mind',plural=False,quality=1,threshold=0,**kwargs):
        super().__init__(**kwargs)
        self.base_descriptor='The power of a mind'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.names=['thoughts','mind']
        self.truename='mind'
        self.name=name
        self.length=length
        self.radius=out_radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield=None
        self.curvature=0
        self.attacktype=None
        self.threshold=threshold
        self.function=1
        self.coverage=0.5
        self.recalc()


############################################Weapons#########################################
#TODO: Blade edge needs to be sharpenable.


class LongSword(BaseClasses.Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1,edge=0.00001,tip=0.0000001,width=0.035,thickness=0.007,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','sword','long sword']
        self.base_descriptor='A straight, double-edged sword with a long blade. A well-balanced and versatile weapon for cutting and thrusting'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' long sword'
        self.length=length
        self.edge=max(edge,self.material.maxedge)
        self.tip=max(tip,self.material.maxedge**1.5)
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

class Gladius(BaseClasses.Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=0.6,edge=0.00001,tip=0.0000001,width=0.035,thickness=0.007,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','sword','gladius']
        self.base_descriptor='A two-edged short sword balanced for cutting, chopping, or thrusting'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' gladius'
        self.length=length
        self.edge=max(edge,self.material.maxedge)
        self.tip=max(tip,self.material.maxedge**1.5)
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

class Knife(BaseClasses.Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=0.3,edge=0.000005,tip=0.000000025,width=0.035,thickness=0.01,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','dagger']
        self.base_descriptor='A short, bladed weapon with a very sharp point. Suitable for throwing, slashing, or stabbing'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' dagger'
        self.length=length
        self.edge=max(edge,self.material.maxedge)
        self.tip=max(tip,self.material.maxedge**1.5)
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

class Saber(BaseClasses.Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1,edge=0.000005,tip=0.0000002,width=0.035,thickness=0.006,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','sword','saber']
        self.base_descriptor='A curved, single-edge sword optimized for cutting'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' saber'
        self.length=length
        self.edge=max(edge,self.material.maxedge)
        self.tip=max(tip,self.material.maxedge**1.5)
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

class Claymore(BaseClasses.Item):
    #length is blade length in meters
    #edge is edge width in meters
    #tip is tip surface area in square meters
    #width is blade width in meters
    #thickness is blade thickness in meters
    def __init__(self,length=1.3,edge=0.00001,tip=0.0000001,width=0.04,thickness=0.008,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','sword','claymore']
        self.base_descriptor='A broad, heavy longsword suitable only for those strong enough to effectively wield it'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' claymore'
        self.length=length
        self.edge=max(edge,self.material.maxedge)
        self.tip=max(tip,self.material.maxedge**1.5)
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

class Mace(BaseClasses.Item):
    #length is length of mace in meters
    #head is head radius in meters
    def __init__(self,length=0.8,head=0.06,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','club','mace']
        self.base_descriptor='A heavy, blunt weapon for delivering powerful blows'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
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
        self.contactarea=0.15*(1-self.curvature)*3.14*self.head**2
        self.radius=self.head
        self.thickness=0.02
        self.r=0.015
        self.movemass=self.mass
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class Flail(BaseClasses.Item):
    #length is length of mace in meters
    #head is head radius in meters
    def __init__(self,length=0.6,head=0.06,chain=0.4,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','club','flail']
        self.base_descriptor='A heavy ball at the end of a chain. Unwieldly, but dangerous in the right hands.'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.length=length
        self.head=head
        self.chain=chain
        self.parry=False
        self.truename=self.material.name+' flail'
        self.wield='grasp'
        self.curvature=0.5
        self.attacktype=['bludgeon']
        self.function=1
        self.attacks=[Flail_Strike_1H,Flail_Strike_2H]
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*3.14*0.005**2+1.33*3.14*self.head**3)
        self.headmass=self.density*1.33*3.14*self.head**3
        self.centermass=self.length+self.chain
        self.I=self.mass*self.centermass**2
        self.contactarea=0.15*(1-self.curvature)*3.14*self.head**2
        self.radius=self.head
        self.thickness=0.02
        self.r=0.015
        self.movemass=self.mass
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class FlangedMace(BaseClasses.Item):
    #length is length of mace in meters
    #head is head radius in meters
    #contactarea is the contact area of a flange or spike in square meters
    def __init__(self,length=0.8,head=0.06,edge=0.00008,penetration_depth=0.08,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','club','flanged mace']
        self.base_descriptor='A heavy mace covered in sharp blades'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.length=length
        self.head=head
        self.edge=edge
        self.penetration_depth=penetration_depth
        self.parry=True
        self.truename=self.material.name+' flanged mace'
        self.wield='grasp'
        self.curvature=0
        self.attacktype=['bludgeon']
        self.function=1
        self.attacks=[Flanged_Mace_Strike_1H,Flanged_Mace_Strike_2H]
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(self.length*3.14*0.005**2+1.33*3.14*self.head**3)
        self.centermass=self.length*0.8
        self.I=self.mass*self.centermass**2
        self.contactarea=0.15*(1-self.curvature)*3.14*self.head**2
        self.radius=self.head
        self.thickness=0.02
        self.r=0.015
        self.movemass=self.mass
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class WarHammer(BaseClasses.Item):
    #length is length of war hammer in meters
    #headvolume is the volume of the head of the warhammer
    #headsize is the area of the head in square meters
    #tip is the contact area of the spike in square meters
    #contactarea is the contact area of the hammer in square meters
    def __init__(self,length=1.1,headvolume=.0002,headsize=0.0005,tip=0.00005,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','club','war hammer']
        self.base_descriptor='A long, heavy hammer with a head for bashing attacks and a spike for piercing through armor'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.length=length
        self.headvolume=headvolume
        self.headsize=headsize
        self.tip=max(tip,self.material.maxedge**1.5)
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

class Spear(BaseClasses.Item):
    #length is spear length in meters
    #tip is tip surface area in square meters
    #thickness is shaft thickness in meters
    def __init__(self,length=2,tip=0.000000025,thickness=0.01,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','polearm','spear']
        self.base_descriptor='A long pole weapon with a sharp tip for piercing attacks.'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' spear'
        self.length=length
        self.tip=max(tip,self.material.maxedge**1.5)
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

class Axe(BaseClasses.Item):
    def __init__(self,length=0.8,edge=0.00004,width=0.2,thickness=0.01,material=M.Iron,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','axe']
        self.base_descriptor='A heavy, broad-headed bladed weapon. Somewhat clumsier than a sword but capable of delivering considerably more force.'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' axe'
        self.length=length
        self.edge=max(edge,self.material.maxedge)
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

class QuarterStaff(BaseClasses.Item):
    def __init__(self,length=2,thickness=0.05,material=M.Wood,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','polearm','quarterstaff']
        self.base_descriptor='A long staff capable of delivering quick blows while keeping adversaries at range.'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' quarterstaff'
        self.length=length
        self.thickness=thickness
        self.radius=self.thickness/2
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
        self.mass=self.density*(3.14*self.length*self.radius**2)
        self.movemass=self.mass
        self.centermass=0.01
        self.I=(1/12)*self.mass*self.length**2
        self.r=self.thickness
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class Shortbow(BaseClasses.Item):
    def __init__(self,length=1.3,thickness=0.017,height=1.1,brace=0.2,material=M.Wood,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','bow','shortbow']
        self.base_descriptor='A short bow suited for firing relatively lightweight arrows'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' shortbow'
        self.length=length
        self.thickness=thickness
        self.radius=self.thickness/2
        self.parry=True
        self.wield='grasp'
        self.height=height
        self.brace=brace
        self.curvature=0
        self.attacktype=[]
        self.function=1
        self.attacks=[Strike_1H,Strike_2H]
        self.abilities=[]
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(3.14*self.length*self.radius**2)
        self.movemass=self.mass
        self.centermass=0.01
        self.I=(1/12)*self.mass*self.length**2
        self.r=self.thickness
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius
        self.maxdraw=self.height*0.4
        self.maxdraw_strength=(1/60)*48*3.14159*1000000000*self.maxdraw*self.youngs*(self.radius**4)/(4*self.height**3)
        self.stiffness=48*3.14159*1000000000*self.youngs*(self.radius**4)/(4*self.height**3)

    def on_equip(self):
        import Abilities
        super().on_equip()
        self.fire_arrow=Abilities.Fire_Bow(self.equipped[0].owner,self)
        self.abilities=[self.fire_arrow]

    def on_unequip(self,limb,**kwargs):
        super().on_unequip(limb,**kwargs)
        self.abilities=[]

class Longbow(BaseClasses.Item):
    def __init__(self,length=2.1,thickness=0.023,height=1.8,brace=0.2,material=M.Wood,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','bow','longbow']
        self.base_descriptor='A tall bow with a long draw and great range.'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' longbow'
        self.length=length
        self.thickness=thickness
        self.radius=self.thickness/2
        self.parry=True
        self.wield='grasp'
        self.height=height
        self.brace=brace
        self.curvature=0
        self.attacktype=[]
        self.function=1
        self.attacks=[Strike_1H,Strike_2H]
        self.abilities=[]
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(3.14*self.length*self.radius**2)
        self.movemass=self.mass
        self.centermass=0.01
        self.I=(1/12)*self.mass*self.length**2
        self.r=self.thickness
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius
        self.maxdraw=self.height*0.4
        self.maxdraw_strength=(1/60)*48*3.14159*1000000000*self.maxdraw*self.youngs*(self.radius**4)/(4*self.height**3)
        self.stiffness=48*3.14159*1000000000*self.youngs*(self.radius**4)/(4*self.height**3)

    def on_equip(self):
        import Abilities
        super().on_equip()
        self.fire_arrow=Abilities.Fire_Bow(self.equipped[0].owner,self)
        self.abilities=[self.fire_arrow]

    def on_unequip(self,limb,**kwargs):
        super().on_unequip(limb,**kwargs)
        self.abilities=[]

class Crossbow(BaseClasses.Item):
    def __init__(self,length=0.8,thickness=0.1,stiffness=3000,brace=0.2,material=M.Wood,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['weapon','crossbow']
        self.base_descriptor='A mechanical bow which requires little skill to use effectively. Requires reloading between shots.'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' crossbow'
        self.length=length
        self.thickness=thickness
        self.radius=self.thickness/2
        self.parry=True
        self.wield='grasp'
        self.stiffness=stiffness
        self.ammo=None
        self.brace=brace
        self.curvature=0
        self.attacktype=[]
        self.function=1
        self.attacks=[Strike_1H,Strike_2H]
        self.abilities=[]
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(3.14*self.length*self.radius**2)
        self.movemass=self.mass
        self.centermass=0.01
        self.I=(1/12)*self.mass*self.length**2
        self.r=self.thickness
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

    def on_equip(self):
        import Abilities
        super().on_equip()
        self.fire_arrow=Abilities.Fire_Crossbow(self.equipped[0].owner,self)
        self.abilities=[self.fire_arrow]

    def on_unequip(self,limb,**kwargs):
        super().on_unequip(limb,**kwargs)
        self.abilities=[]

class Arrow(BaseClasses.Item):
    def __init__(self,length=0.85,tip=0.0000001,thickness=0.004,material=M.Wood,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.stack_id=random.random()
        self.names=['weapon','arrow']
        self.base_descriptor='A simple projectile to be fired from a bow'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' arrow'
        self.length=length
        self.thickness=thickness
        self.radius=self.thickness/2
        self.parry=True
        self.wield='quiver'
        self.tip=tip
        self.stackable=True
        self.curvature=0
        self.attacktype=[]
        self.function=1
        self.attacks=[]
        self.abilities=[]
        self.in_stack=100
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(3.14*self.length*self.radius**2)
        self.movemass=self.mass
        self.centermass=0.01
        self.I=(1/12)*self.mass*self.length**2
        self.r=self.thickness
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

    def get_from_stack(self,**kwargs):
        self.in_stack-=1
        self.generate_descriptions(name_only=True)
        new_arrow=Arrow(length=self.length,tip=self.tip,thickness=self.thickness,material=type(self.material),quality=self.quality)
        new_arrow.in_stack=1
        new_arrow.stack_id=self.stack_id
        new_arrow.knowledge_level=self.knowledge_level
        new_arrow.generate_descriptions(name_only=True)
        for i in self.enchantments:
            type(i)(new_arrow,strength=i.strength,turns=i.turns)
        return new_arrow

class Bolt(BaseClasses.Item):
    def __init__(self,length=0.5,tip=0.0000001,thickness=0.01,material=M.Wood,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.stack_id=random.random()
        self.names=['weapon','bolt']
        self.base_descriptor='A heavy bolt designed to be fired from a crossbow'
        self.sortingtype='weapon'
        self.material=material(quality=quality,power=self.power)
        self.plural=False
        self.truename=self.material.name+' bolt'
        self.length=length
        self.thickness=thickness
        self.radius=self.thickness/2
        self.parry=True
        self.wield='quiver'
        self.tip=tip
        self.stackable=True
        self.curvature=0
        self.attacktype=[]
        self.function=1
        self.attacks=[]
        self.abilities=[]
        self.in_stack=100
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        self.material_import()
        self.mass=self.density*(3.14*self.length*self.radius**2)
        self.movemass=self.mass
        self.centermass=0.01
        self.I=(1/12)*self.mass*self.length**2
        self.r=self.thickness
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

    def get_from_stack(self,**kwargs):
        self.in_stack-=1
        self.generate_descriptions(name_only=True)
        new_arrow=Arrow(length=self.length,tip=self.tip,thickness=self.thickness,material=type(self.material),quality=self.quality)
        new_arrow.in_stack=1
        new_arrow.stack_id=self.stack_id
        new_arrow.knowledge_level=self.knowledge_level
        new_arrow.generate_descriptions(name_only=True)
        for i in self.enchantments:
            type(i)(new_arrow,strength=i.strength,turns=i.turns)
        return new_arrow


############################################Armor####################################################################

class Chest(BaseClasses.Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.9,thickness='default',in_radius=0.1,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
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

class Chainmail(BaseClasses.Item):
    def __init__(self,length=0.9,thickness='default',in_radius=0.1,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.material.density*=0.3
        self.material.shear*=0.02
        self.material.mode='mail'
        self.material.shear_strength*=0.1
        self.material.tensile_strength*=0.1
        self.names=['armor','chestpiece','chainmail']
        self.truename=self.material.name+' chainmail'
        self.base_descriptor='Chain armor which covers the torso. Protects well from edged weapons while retaining a full range of motion'
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
        self.coverage=1
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

class Glove(BaseClasses.Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.4,thickness='default',in_radius=0.022,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
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

class Chain_Glove(BaseClasses.Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.4,thickness='default',in_radius=0.022,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.material.shear*=0.02
        self.material.density*=0.3
        self.material.tensile_strength*=0.1
        self.material.shear_strength*=0.1
        self.material.mode='mail'
        self.names=['armor','hand armor','chain gauntlet']
        self.base_descriptor='Heavy glove for protecting the hand from injury'
        self.truename=self.material.name+' chain gauntlet'
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

class Legging(BaseClasses.Item):
    def __init__(self,length=0.8,thickness='default',in_radius=0.085,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
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

class Chain_Legging(BaseClasses.Item):
    def __init__(self,length=0.8,thickness='default',in_radius=0.085,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.material.mode='chain'
        self.material.shear*=0.02
        self.material.density*=0.3
        self.material.shear_strength*=0.1
        self.material.tensile_strength*=0.1
        self.names=['armor','leg armor','chain legging']
        self.truename=self.material.name+' chain legging'
        self.base_descriptor='Chain leg armor ideal for absorbing the blows of edged weapons.'
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
        self.coverage=1
        self.function=1
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        super().recalc()
        self.r=self.radius

class Armlet(BaseClasses.Item):
    def __init__(self,length=0.375,thickness='default',in_radius=0.052,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
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

class Chain_Armlet(BaseClasses.Item):
    def __init__(self,length=0.375,thickness='default',in_radius=0.052,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.material.mode='chain'
        self.material.shear*=0.02
        self.material.density*=0.3
        self.material.shear_strength*=0.1
        self.material.tensile_strength*=0.1
        self.names=['armor','arm guard','chain vambrace']
        self.truename=self.material.name+' chain vambrace'
        self.base_descriptor='Flexible chain sleeve for protection of the arm.'
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
        self.coverage=1
        self.function=1
        self.recalc()
        self.generate_descriptions()

    def recalc(self):
        super().recalc()
        self.mass=2*self.mass
        self.movemass=self.mass
        self.r=self.radius

class Boot(BaseClasses.Item):
    #length is bone length in meters
    #radius is bone radius in meters
    def __init__(self,length=0.35,thickness='default',in_radius=0.035,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['armor','footwear','boot']
        self.base_descriptor='Footwear worn for protection of the foot and ankle'
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
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

class Helm(BaseClasses.Item):
    def __init__(self,length=0.1,thickness='default',in_radius=0.08,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
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

class GreatHelm(BaseClasses.Item):
    def __init__(self,length=0.2,thickness='default',in_radius=0.08,material=M.Iron,plural=False,quality=1,scale_factor=1,thickness_factor=1,**kwargs):
        super().__init__(**kwargs)
        self.sortingtype='armor'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
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

class Shield(BaseClasses.Item):
    def __init__(self,length=0.02,radius=0.36,in_radius=0,material=M.Iron,plural=False,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['armor','shield']
        self.base_descriptor='A large, heavy shield for absorbing and deflecting blows'
        self.sortingtype='armor'
        self.image='c:/Project/shield.png'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
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
        self.I=0.01#(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.contactarea=3.14*self.radius**2
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius

class Buckler(BaseClasses.Item):
    def __init__(self,length=0.02,radius=0.1,in_radius=0,material=M.Iron,plural=False,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.names=['armor','shield','buckler']
        self.base_descriptor='A small shield ideal for dueling which can be quickly moved to wherever it is needed most'
        self.sortingtype='armor'
        self.image='c:/Project/shield.png'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
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
        self.I=0.01#(1/12)*self.mass*self.length**2+self.mass*self.centermass**2
        self.contactarea=3.14*self.radius**2
        if self.base_thickness==0:
            self.base_thickness=self.thickness
        if self.base_radius==0:
            self.base_radius=self.radius



class ExperimentalMace(Mace):
    def __init__(self,material=M.Iron,quality=1):
        super().__init__(material=material,quality=quality)
        self.attacks=[Experimental_Bash]


###########################################Miscelaneous############################################################

class Stone(BaseClasses.Item):
    def __init__(self,length=0.1,in_radius=0,out_radius=0.1,material=M.Granite,name='stone',plural=False,quality=1,threshold=0,**kwargs):
        super().__init__(**kwargs)
        self.base_descriptor='A heavy ball of rock'
        self.plural=plural
        self.material=material(quality=quality,power=self.power)
        self.names=['lump','stone']
        self.truename='stone'
        self.identification_difficulty['basic']=1
        self.name=name
        self.length=length
        self.radius=out_radius
        self.in_radius=in_radius
        self.cross_section_range=[3.14*(self.radius**2-in_radius**2),self.length*2*(self.radius-in_radius)]
        self.parry=False
        self.wield=None
        self.curvature=0
        self.attacktype=None
        self.threshold=threshold
        self.function=1
        self.coverage=0.5
        self.recalc()




default_item_weights=[(Bone,0),(Flesh,0),(Hair,0),(LongSword,10),(Gladius,5),(Knife,7),(Saber,4),(Claymore,4),(Mace,8),
                 (WarHammer,3),(FlangedMace,3),(Spear,5),(Axe,6),(QuarterStaff,3),(Chest,8),(Glove,12),(Legging,12),(Armlet,12),
                (Boot,12),(Helm,8),(GreatHelm,3),(Shield,6),(Buckler,6),(Chainmail,5),(Chain_Armlet,6),(Chain_Legging,6),
                (Chain_Glove,6),(Stone,3)]
total_item_weight=sum(i[1] for i in default_item_weights)

hard_material_weights=[(M.Iron,10),(M.Bone_Material,7),(M.Wood,10),(M.Copper,10),(M.Brass,6),(M.Bronze,5),(M.Steel,4),
                       (M.Aluminum,3),(M.Silver,2),(M.Duraluminum,1),(M.Zicral,1),(M.Granite,2)]
soft_material_weights=[(M.Leather,10),(M.Cotton,10),(M.Wool,9),(M.Silk,5),(M.Spider_Silk,2),(M.Basalt_Fiber,1),(M.Fur,3),(M.Flesh_Material,1)]

def weighted_choice(pairs):
    total=0
    for i in pairs:
        total+=i[1]
    number=random.random()*total
    for i in pairs:
        if number<=i[1]:
            return i[0]
        else: number-=i[1]

def weighted_generation(weighted_items=default_item_weights,totalweight=total_item_weight,hard_materials=hard_material_weights,soft_materials=soft_material_weights,size=1):
    chosen_material=None
    choicenumber=random.random()*totalweight
    '''
    for i in weighted_items:
        if choicenumber<=i[1]:
            itemtype=i[0]
            break
        else:
            choicenumber-=i[1]
    '''
    itemtype=weighted_choice(weighted_items)
    if itemtype in (Chain_Legging,Chain_Armlet,Chainmail):
        chosen_material=weighted_choice(hard_materials)
    elif itemtype in (LongSword,Gladius,Knife,Saber,Claymore,Mace,WarHammer,Spear,Axe,QuarterStaff,Shield,Buckler):
        if random.random()<0.99:
            chosen_material=weighted_choice(hard_materials)
    elif itemtype in [Stone]:
        if random.random()>0.99:
            chosen_material=random.choice([M.Granite])
    if chosen_material==None:
        mats=hard_materials.copy()
        mats.extend(soft_materials)
        chosen_material=weighted_choice(mats)
    item=itemtype(material=chosen_material,scale_factor=size)
    item.randomize()
    return item




allitems=[Bone,Flesh,Hair,BaseClasses.Limb,LongSword,Gladius,Knife,Saber,Claymore,Mace,WarHammer,Spear,Axe,QuarterStaff,
          Chest,Glove,Legging,Armlet,Boot,Helm,GreatHelm,Shield,Buckler]
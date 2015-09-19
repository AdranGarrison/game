__author__ = 'Alan'



import kivy
from kivy.properties import ListProperty, DictProperty
from BaseClasses import *
from Materials import *
from Items import *




##############################################LIMBS###################################################################
'''Here are all the body parts we will use to create our creatures. Here we lay out the format we will adhere to:

Sizefactor represents the relative likelihood of a given part being hit on a randomly targeted swing or alternatively the
ease with which the part is hit when intentionally targeted.

If a limb is natural (natural=True), then its individual stats will be the same as its owner's and will change therewith

If self.grasp is true, the limb is currently capable of grasping objects

self.ability determines how well-functioning the limb currently is given its current wounds.

self.dexterity determines how well a limb can manipulate objects. From 1 to 10. Applies only to limbs which can grasp

self.balance determines how well a limb supports weight nimbly. Applies only to limbs which can be walked upon

wield indicates the types of equipment the limb in question can wield.
Options are:
ring, glove, bracelet, armlet, chest, helmet, necklace, legging, boot, grasp

These same above terms will be included in the self.wield for each equippable item type

self.equip is a dictionary housing the equipment for each slot

self.limbs indicates all limbs attached to the limb in question.

self.scars is currently a placeholder, but will keep track of scars from past wounds

self.descriptor is what the game will print to the player upon query

self.attacktype is the type of attack the limb grants. It depends upon current equipment when applicable
'''

buildfromtorso=False



class Finger(Limb):
    
    
    def __init__(self,stats,name='finger',scale=1,length=0.1,radius=0.01,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.painfactor=0.5
        self.owner=owner
        self.owner.limbs.append(self)
        self.sizefactor=2
        self.length=length*scale
        self.radius=radius*scale
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.primaryequip=['ring']
        self.equiptype=['ring','glove']
        self.equipment={'ring':None,'glove':None}
        self.armor=self.equipment['glove']
        self.scars=[]
        self.descriptor='This is a humanoid finger of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius*0.8,quality=0.25),Flesh(length=self.length,in_radius=self.radius*0.8,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks
        self.armortype='glove'


    def equip(self,item):
        if item.wield=='ring':
            if self.equipment['ring'] is not None:
                self.unequip('ring')
            self.equipment['ring']=item
            item.equipped=self
            if item.mass:
                self.movemass+=item.mass
            self.owner.equipped_items.append(item)

        if item.wield=='glove':
            self.equipment['glove']=item
            self.armor=self.equipment['glove']

        self.youngscalc()

    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        pass


class Hand(Limb):
    
    
    def __init__(self,stats,name='hand',scale=1,length=0.1,radius=0.022,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=10
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.length=length*scale
        self.radius=radius*scale
        self.grasp=True
        self.support=False
        self.ability=1
        self.stats=stats
        self.primaryequip=['glove','grasp']
        self.equiptype=['glove','grasp']
        self.equipment={'glove':None,'grasp':None}
        self.armor=self.equipment['glove']

        if buildfromtorso==True:
            self.thumb=Finger(stats,'thumb, {}'.format(name),owner=owner)
            self.firstfinger=Finger(stats,'first finger, {}'.format(name),owner=owner)
            self.secondfinger=Finger(stats,'second finger, {}'.format(name),owner=owner)
            self.thirdfinger=Finger(stats,'third finger, {}'.format(name),owner=owner)
            self.fourthfinger=Finger(stats,'fourth finger, {}'.format(name),owner=owner)

            self.limbs=[self.thumb,self.firstfinger,self.secondfinger,self.thirdfinger,self.fourthfinger]

        self.scars=[]
        self.descriptor='This is a humanoid hand of {}.'.format(self.owner.indefinitename)
        self.attacktype='punch'
        self.dexterity=self.ability
        for i in self.limbs:
            self.dexterity+=i.ability
            i.attachpoint=self
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius*0.9,quality=0.08),Flesh(length=self.length,in_radius=self.radius*0.9,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[Punch(self)]
        self.attacks=self.defaultattacks
        self.armortype='glove'



    def equip(self,item):
        if item.wield=='glove':
            if self.equipment['glove'] is not None:
                self.unequip('glove')
            self.equipment['glove']=item
            self.armor=self.equipment['glove']
#TODO: size of items should determine when it can be equipped. This bit of code does so, but I don't feel like implementing it everywhere right now
#            if self.radius<0.5*item.radius:
#                print("{} is too big!".format(item.name))
#            if self.radius>2*item.radius:
#                print("{} is too small!".format(item.name))
            item.equipped=self
            if item.mass:
                self.movemass+=item.mass
            for i in self.limbs:
                if isinstance(i,Finger):
                    i.equip(item)
            self.owner.equipped_items.append(item)

        if self.grasp==True:
            if item.wield=='grasp':
                if self.equipment['grasp'] is not None:
                    self.unequip('grasp')

                self.equipment['grasp']=item
                item.equipped=self
                if item.mass:
                    self.movemass+=item.mass

                self.attacks=[]
                for i in item.attacks:
                    self.attacks.append(i(item,self))
                self.owner.equipped_items.append(item)
        self.youngscalc()



    def on_wounds(self,*args):
        self.ability=max(self.ability,0)
        if self.ability==0:
            self.grasp=False
        fingerfunction=0
        fingercount=0
        for i in self.limbs:
            fingerfunction+=i.ability
            if i.ability>0:
                fingercount+=1
        if fingercount<2:
            self.grasp=False

        self.dexterity=fingerfunction+2*self.ability

        if self.grasp==False:
            if self.equipment['grasp'] is not None:
                self.equipment['grasp']=None
                self.attacktype=None


    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats

    def dex_calc(self):
        self.dexterity=self.ability
        if self.ability>0:
            for i in self.limbs:
                self.dexterity+=i.ability
        if self.dexterity<=0:
            self.grasp=False
            if self.equipment['grasp'] is not None:
                self.unequip('grasp',drop=True)
        else:
            self.grasp=True


class Arm(Limb):
    
    
    def __init__(self,stats,name='',scale=1,length=0.75,boneradius=0.013,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=50
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name+' arm'
        self.length=length*scale
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.radius=(self.stats['s']/10000)**0.5+boneradius*scale
        self.primaryequip=['armlet','bracelet']
        self.equiptype=['armlet','bracelet']
        self.equipment={'armlet':None,'bracelet':None}
        self.armor=self.equipment['armlet']

        if buildfromtorso==True:
            self.hand=Hand(stats,'{} hand'.format(name),owner=owner)
            self.hand.attachpoint=self

            self.limbs=[self.hand]
        self.scars=[]
        self.descriptor='This is an arm of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=boneradius),Flesh(length=self.length,in_radius=boneradius,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks
        self.armortype='armlet'


    def equip(self,item):
        if item.wield=='armlet':
            if self.equipment['armlet'] is not None:
                self.unequip('armlet')
            self.equipment['armlet']=item
            item.equipped=self
            self.armor=self.equipment['armlet']
            if item.mass:
                self.movemass+=item.mass
            self.owner.equipped_items.append(item)

        if item.wield=='bracelet':
            if self.equipment['bracelet'] is not None:
                self.unequip('bracelet')
            self.equipment['bracelet']=item
            item.equipped=self
            if item.mass:
                self.movemass+=item.mass
            self.owner.equipped_items.append(item)

        self.youngscalc()




    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats

    def recover(self,turns=1,**kwargs):
        if self.ability<=0:
            for i in self.limbs:
                i.inoperable=True
                i.updateability()
        else:
            for i in self.limbs:
                i.inoperable=False
                i.updateability()
        super().recover(turns=turns)


class Torso(Limb):
    
    
    def __init__(self,stats,name,scale=1,length=0.9,radius=0.1,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=40
        self.staminacost=7
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.contains_vitals=True
        self.ability=1
        self.stats=stats
        self.length=length*scale
        self.radius=radius*scale
        self.equiptype=['chest']
        self.equipment={'chest':None}
        self.armor=self.equipment['chest']

        if buildfromtorso==True:
            self.rightarm=Arm(stats,'right',owner=owner)
            self.rightarm.attachpoint=self
            self.leftarm=Arm(stats,'left',owner=owner)
            self.leftarm.attachpoint=self
            self.rightleg=Leg(stats,'right',owner=owner)
            self.rightleg.attachpoint=self
            self.leftleg=Leg(stats,'left',owner=owner)
            self.leftleg.attachpoint=self
            self.neck=Neck(stats,'neck',owner=owner)
            self.neck.attachpoint=self
            self.limbs=[self.rightarm,self.leftarm,self.rightleg,self.leftleg,self.neck]

        self.organs=Flesh(length=self.length,out_radius=self.radius*0.74,in_radius=0,name='vital organs',plural=True)

        self.owner.vitals.append(self.organs)


        self.scars=[]
        self.descriptor='This is a torso of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[self.organs,
                     Bone(length=self.length,radius=self.radius*0.9,in_radius=self.radius*0.74,name='ribs',plural=True,quality=0.9),
                     Flesh(length=self.length,in_radius=self.radius*0.9,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks
        self.armortype='chest'


    def equip(self,item):
        if item.wield=='chest':
            if self.equipment['chest'] is not None:
                self.unequip('chest')
            self.equipment['chest']=item
            item.equipped=self
            self.armor=self.equipment['chest']
            if item.mass:
                self.movemass+=item.mass
            self.owner.equipped_items.append(item)

        self.youngscalc()




    def on_wounds(self,*args):
        self.ability=1
        self.descriptor='This is a torso of {}.'.format(self.owner.indefinitename)



    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Toe(Limb):
    
    
    def __init__(self,stats,name='toe',scale=1,length=0.05,radius=0.005,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.painfactor=0.5
        self.sizefactor=2
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.length=length*scale
        self.radius=radius*scale
        self.equiptype=['boot']
        self.equipment={'boot':None}
        self.armor=self.equipment['boot']


        self.limbs=[]
        self.scars=[]
        self.descriptor='This is a humanoid toe of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius*0.8,quality=0.25),Flesh(length=self.length,in_radius=self.radius*0.8,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks
        self.armortype='boot'

    def equip(self,item):
        if item.wield=='boot':
            self.equipment['boot']=item
            self.armor=self.equipment['boot']
        self.youngscalc()




    def on_wounds(self,*args):
        self.ability=1
        self.ability=max(self.ability,0)



    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Foot(Limb):
    
    
    def __init__(self,stats,name='foot',scale=1,length=0.22,radius=0.035,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.length=length*scale
        self.radius=radius*scale
        self.sizefactor=10
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=True
        self.ability=1
        self.stats=stats
        self.primaryequip=['boot']
        self.equiptype=['boot']
        self.equipment={'boot':None}
        self.armor=self.equipment['boot']

        if buildfromtorso==True:
            self.firsttoe=Toe(stats,'big toe, {}'.format(name),owner=owner)
            self.secondtoe=Toe(stats,'second toe, {}'.format(name),owner=owner)
            self.thirdtoe=Toe(stats,'third toe, {}'.format(name),owner=owner)
            self.fourthtoe=Toe(stats,'fourth toe, {}'.format(name),owner=owner)
            self.fifthtoe=Toe(stats,'little toe, {}'.format(name),owner=owner)
            self.limbs=[self.firsttoe,self.secondtoe,self.thirdtoe,self.fourthtoe,self.fifthtoe]

        self.scars=[]
        self.descriptor='This is a humanoid foot of {}.'.format(self.owner.indefinitename)
        self.attacktype='kick'
        self.balance=self.ability
        for i in self.limbs:
            self.balance+=i.ability
            i.attachpoint=self
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius*0.8,quality=0.08),Flesh(length=self.length,in_radius=self.radius*0.8,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[Kick(self)]
        self.attacks=self.defaultattacks
        self.armortype='boot'


    def equip(self,item):
        if item.wield=='boot':
            if self.equipment['boot'] is not None:
                self.unequip('boot')
            self.equipment['boot']=item
            self.armor=self.equipment['boot']
            item.equipped=self
            if item.mass:
                self.movemass+=item.mass
            for i in self.limbs:
                if isinstance(i,Toe):
                    i.equip(item)
            self.owner.equipped_items.append(item)
        self.youngscalc()




    def on_wounds(self,*args):
        self.ability=1

        self.ability=max(self.ability,0)
        if self.ability==0:
            self.support=False
        toefunction=0
        for i in self.limbs:
            toefunction+=i.ability


        self.balance=toefunction+2*self.ability

        self.balance=min(self.balance,self.attachpoint.balance*6)

        if self.balance<2:
            self.support=False


        if self.support==False:
            self.descriptor+=' Injuries have left it impossible to walk on.'
            self.attacktype=None


    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats

    def balance_calc(self):
        self.balance=self.ability
        if self.balance>=0:
            for i in self.limbs:
                self.balance+=i.ability
        if self.balance<=0:
            self.support=False
        elif self.attachpoint is None:
            self.support=False
            self.balance=0
        elif self.attachpoint.ability<=0:
            self.support=False
            self.balance=0
        else:
            self.support=True


class Leg(Limb):
    
    
    def __init__(self,stats,name='',scale=1,length=0.8,boneradius=0.018,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.painfactor=0.8
        self.length=length*scale
        self.sizefactor=50
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name+' leg'
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.radius=(self.stats['s']/3500)**0.5+boneradius*scale
        self.primaryequip=['legging']
        self.equiptype=['legging']
        self.equipment={'legging':None}
        self.armor=self.equipment['legging']

        if buildfromtorso==True:
            self.foot=Foot(stats,'{} foot'.format(name),owner=owner)
            self.foot.attachpoint=self
            self.limbs=[self.foot]

        self.scars=[]
        self.descriptor='This is a humanoid leg of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=boneradius),Flesh(length=self.length,in_radius=boneradius,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks
        self.armortype='legging'

    def equip(self,item):
        if item.wield=='legging':
            if self.equipment['legging'] is not None:
                self.unequip('legging')
            self.equipment['legging']=item
            self.armor=self.equipment['legging']
            item.equipped=self
            if item.mass:
                self.movemass+=item.mass
            self.owner.equipped_items.append(item)

        self.youngscalc()



    def on_wounds(self,*args):
        self.ability=1

        self.ability=max(self.ability,0)



    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Ear(Limb):
    
    
    def __init__(self,stats,name='',scale=1,length=0.008,radius=0.02,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.painfactor=0.7
        self.radius=radius*scale
        self.length=length*scale
        self.owner=owner
        self.owner.limbs.append(self)
        self.sizefactor=1
        self.natural=natural
        self.name=name+' ear'
        self.hear=True
        self.hearing=1
        self.ability=1
        self.stats=stats
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=self.equipment['helmet']
        self.armortype='helmet'
        self.scars=[]
        self.descriptor='This is an ear of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Flesh(length=self.length,in_radius=0,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks

    def equip(self,item):
        if item.wield=='helmet':
            self.equipment['helmet']=item
            self.armor=self.equipment['helmet']
        self.youngscalc()


    def on_wounds(self,*args):
        self.ability=1
        self.ability=max(self.ability,0)

    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        pass


class Nose(Limb):
    
    
    def __init__(self,stats,name='nose',scale=1,length=0.01,radius=0.02,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.radius=radius*scale
        self.length=length*scale
        self.owner=owner
        self.owner.limbs.append(self)
        self.sizefactor=1
        self.natural=natural
        self.name=name
        self.smell=True
        self.smell_sense=1
        self.ability=1
        self.stats=stats
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=self.equipment['helmet']
        self.armortype='helmet'
        self.scars=[]
        self.descriptor='This is a nose of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Flesh(length=self.length,in_radius=0,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks

    def equip(self,item):
        if item.wield=='helmet':
            self.equipment['helmet']=item
            self.armor=self.equipment['helmet']

        self.youngscalc()


    def on_wounds(self,*args):
        self.ability=1
        self.ability=max(self.ability,0)

    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        pass


class Eye(Limb):
    
    
    def __init__(self,stats,name='',scale=1,length=None,radius=0.013,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.painfactor=2
        self.radius=radius*scale
        self.length=radius*scale
        self.owner=owner
        self.owner.limbs.append(self)
        self.sizefactor=1
        self.natural=natural
        self.name=name+' eye'
        self.grasp=False
        self.support=False
        self.sight=True
        self.vision=1
        self.ability=1
        self.stats=stats
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=self.equipment['helmet']
        self.armortype='helmet'
        self.scars=[]
        self.descriptor='This is an eye of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Flesh(length=self.length,in_radius=0,out_radius=self.radius,threshold=0.4)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks

    def equip(self,item):
        if item.wield=='helmet':
            self.equipment['helmet']=item
            self.armor=self.equipment['helmet']

        self.youngscalc()


    def on_wounds(self,*args):
        self.ability=1
        self.ability=max(self.ability,0)

    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        pass


class Teeth(Limb):
    
    
    def __init__(self,stats,name='teeth',scale=1,length=0.12,radius=0.005,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=1
        self.owner=owner
        self.is_teeth=True
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.length=length*scale
        self.radius=radius*scale
        self.plural=True
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=self.equipment['helmet']
        self.armortype='helmet'


        self.limbs=[]
        self.scars=[]
        self.descriptor='These are the teeth of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks

    def equip(self,item):
        if item.wield=='helmet':
            self.equipment['helmet']=item
            self.armor=self.equipment['helmet']
        self.youngscalc()




    def on_wounds(self,*args):
        self.ability=1
        self.ability=max(self.ability,0)



    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Jaw(Limb):
    
    
    def __init__(self,stats,name='jaw',scale=1,length=0.2,radius=0.018,natural=True,owner=None, can_bite=True,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=3
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.length=length*scale
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.radius=radius*scale
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=self.equipment['helmet']
        self.armortype='helmet'

        if buildfromtorso==True:
            self.teeth=Teeth(stats,"lower teeth",owner=owner)
            self.teeth.attachpoint=self
            self.limbs=[self.teeth]

        self.scars=[]
        self.descriptor='This is a jaw of {}.'.format(self.owner.indefinitename)
        self.attacktype='bite'
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius*0.8,quality=0.5),Flesh(length=self.length,in_radius=self.radius*0.8,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        if can_bite==True:
            self.defaultattacks=[Bite(self)]
        else:
            self.defaultattacks=[]
        self.attacks=self.defaultattacks


    def equip(self,item):
        if item.wield=='helmet':
            self.equipment['helmet']=item
            self.armor=self.equipment['helmet']
        self.youngscalc()




    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Head(Limb):
    
    
    def __init__(self,stats,name='head',scale=1,length=0.2,radius=0.08,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.painfactor=1.5
        self.sizefactor=19
        self.staminacost=5
        self.focuscost=10
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.contains_vitals=True
        self.ability=1
        self.stats=stats
        self.length=length*scale
        self.radius=radius*scale
        self.primaryequip=['helmet']
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=self.equipment['helmet']
        self.armortype='helmet'

        if buildfromtorso==True:
            self.righteye=Eye(stats,'right',owner=owner)
            self.righteye.attachpoint=self
            self.lefteye=Eye(stats,'left',owner=owner)
            self.lefteye.attachpoint=self
            self.rightear=Ear(stats,'right',owner=owner)
            self.rightear.attachpoint=self
            self.leftear=Ear(stats,'left',owner=owner)
            self.leftear.attachpoint=self
            self.jaw=Jaw(stats,'jaw',owner=owner)
            self.jaw.attachpoint=self
            self.nose=Nose(stats,'nose',owner=owner)
            self.nose.attachpoint=self
            self.teeth=Teeth(stats,'upper teeth',owner=owner)
            self.teeth.attachpoint=self
            self.limbs=[self.righteye,self.lefteye,self.rightear,self.leftear,self.jaw,self.nose,self.teeth]

        self.brain=Flesh(length=self.length*0.8,in_radius=0,out_radius=self.radius*0.75,name='brain',threshold=0.6)
        self.skull=Bone(length=self.length,radius=self.radius*0.98,in_radius=self.radius*0.8,name='skull',quality=0.7)
        self.owner.vitals.append(self.brain)
        self.owner.vitals.append(self.skull)



        self.scars=[]
        self.descriptor='This is a head of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[self.brain,self.skull,Flesh(length=self.length,in_radius=self.radius*0.98,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks


    def equip(self,item):
        if item.wield=='helmet':
            if self.equipment['helmet'] is not None:
                self.unequip('helmet')
            self.equipment['helmet']=item
            self.armor=self.equipment['helmet']
            item.equipped=self
            if item.mass:
                self.movemass+=item.mass
            for i in self.limbs:
                if not isinstance(i,Head):
                    i.equip(item)
            self.owner.equipped_items.append(item)
            if isinstance(item,GreatHelm):
                self.attachpoint.equip(item)

        self.youngscalc()





    def on_wounds(self,*args):
        self.ability=1
        self.descriptor='This is a head of {}.'.format(self.owner.indefinitename)



    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Neck(Limb):
    
    
    def __init__(self,stats,name='neck',scale=1,length=0.1,boneradius=0.013,radius=0.1,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=1
        self.painfactor=2
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.length=length*scale
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.radius=radius*scale
        self.primaryequip=['necklace']
        self.equiptype=['necklace','helmet']
        self.equipment={'necklace':None,'helmet':None}
        self.armor=None

        if buildfromtorso==True:
            self.head=Head(stats,'head',owner=owner)
            self.head.attachpoint=self
            self.limbs=[self.head]

        self.scars=[]
        self.descriptor='This is a neck of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None

        self.spine=Bone(length=self.length,radius=boneradius*scale,name='spine',threshold=0.2)
        self.throat=Flesh(length=self.length,in_radius=boneradius*scale,out_radius=self.radius,name='throat',quality=2,threshold=0.3)
        self.layers=[self.spine,self.throat]
        self.owner.vitals.append(self.spine)
        self.owner.vitals.append(self.throat)

        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks
        self.armortype='necklace'


    def equip(self,item):
        if item.wield=='necklace':
            if self.equipment['necklace'] is not None:
                self.unequip('necklace')
            self.equipment['necklace']=item
            item.equipped=self
            if item.mass:
                self.movemass+=item.mass
            self.owner.equipped_items.append(item)

        if isinstance(item,GreatHelm):
            self.equipment['helmet']=item
            self.armor=self.equipment['helmet']

        self.youngscalc()




    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Abdomen(Limb):
    
    
    def __init__(self,stats,name='lower torso',scale=1,length=0.4,radius=0.1,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=20
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.contains_vitals=True
        self.ability=1
        self.stats=stats
        self.length=length*scale
        self.radius=radius*scale
        self.equiptype=['chest']
        self.equipment={'chest':None}
        self.armor=self.equipment['chest']


        self.liver=Flesh(length=0.1,in_radius=0,out_radius=0.06,name='liver',painfactor=5,quality=0.5)
        self.intestines=Flesh(length=self.length,in_radius=0,out_radius=0.8*self.radius,name='intestines',painfactor=2,plural=True,quality=0.5,threshold=0.2)
        self.spine=Bone(length=self.length,radius=0.02,name='spine',painfactor=3,threshold=0.2)


        self.owner.vitals.append(self.liver)
        self.owner.vitals.append(self.intestines)


        self.scars=[]
        self.descriptor='This is an abdomen of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[self.liver,self.intestines,self.spine,Flesh(length=self.length,in_radius=0.8*self.radius,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks
        self.armortype='chest'


    def equip(self,item):
        if item.wield=='chest':
            self.equipment['chest']=item
            self.armor=self.equipment['chest']
        self.youngscalc()


    def on_wounds(self,*args):
        self.ability=1
        self.descriptor='This is a torso of {}.'.format(self.owner.indefinitename)



    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats

    def damageresolve(self,attack,attacker,reactionforce=False):
        if 'skeleton' in self.owner.classification:
            super().damageresolve(attack,attacker,reactionforce=reactionforce)
            return
        internals=[self.spine,self.liver,self.intestines]
        outerlayers=[]
        for i in self.layers:
            if self.layers.index(i)>=3:
                outerlayers.append(i)
        self.layers=[]
        if random.random()>0.85:
            if random.random()>=0.25:
                self.layers.append(self.liver)
                self.layers.append(self.intestines)
            else:
                self.layers.append(self.intestines)
                self.layers.append(self.liver)
            self.layers.append(self.spine)
        else:
            self.layers.append(self.spine)
            if random.random()>=0.25:
                self.layers.append(self.liver)
                self.layers.append(self.intestines)
            else:
                self.layers.append(self.intestines)
                self.layers.append(self.liver)
        self.layers.extend(outerlayers)
        self.youngscalc()
        super().damageresolve(attack,attacker,reactionforce=reactionforce)

    def recover(self,turns=1,**kwargs):
        if self.spine.function<=0:
            for i in self.limbs:
                i.inoperable=True
                i.updateability()
        else:
            for i in self.limbs:
                i.inoperable=False
                i.updateability()
        super().recover(turns=turns)


class Upper_Torso(Limb):
    
    
    def __init__(self,stats,name='chest',scale=1,length=0.5,radius=0.1,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=20
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.contains_vitals=True
        self.ability=1
        self.stats=stats
        self.length=length*scale
        self.radius=radius*scale
        self.primaryequip=['chest']
        self.equiptype=['chest']
        self.equipment={'chest':None}
        self.armor=self.equipment['chest']

        self.heart=Flesh(length=0.1,in_radius=0,out_radius=0.05,name='heart',quality=2,painfactor=5,threshold=0.5)
        self.lungs=Flesh(length=self.length,in_radius=0,out_radius=self.radius*0.74,name='lungs',plural=True,threshold=0.2)



        self.owner.vitals.append(self.heart)
        self.owner.vitals.append(self.lungs)


        self.scars=[]
        self.descriptor='This is a torso of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[self.heart,self.lungs,
                     Bone(length=self.length,radius=self.radius*0.9,in_radius=self.radius*0.74,name='ribs',plural=True,quality=0.9),
                     Flesh(length=self.length,in_radius=self.radius*0.9,out_radius=self.radius)]
        self.mass_calc()
        self.youngscalc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks
        self.armortype='chest'


    def equip(self,item):
        if item.wield=='chest':
            if self.equipment['chest'] is not None:
                self.unequip('chest')
            self.equipment['chest']=item
            item.equipped=self
            self.armor=self.equipment['chest']
            for i in self.limbs:
                if isinstance(i,Abdomen):
                    i.equip(item)
            if item.mass:
                self.movemass+=item.mass
            self.owner.equipped_items.append(item)

        self.youngscalc()




    def on_wounds(self,*args):
        self.ability=1
        self.descriptor='This is a torso of {}.'.format(self.owner.indefinitename)



    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


    def damageresolve(self,attack,attacker,reactionforce=False):
        if 'skeleton' in self.owner.classification:
            super().damageresolve(attack,attacker,reactionforce=reactionforce)
            return
        internals=[self.heart,self.lungs]
        outerlayers=[]
        for i in self.layers:
            if self.layers.index(i)>=2:
                outerlayers.append(i)
        self.layers=[]
        if random.random()>0.85:
            self.layers.append(self.heart)
            self.layers.append(self.lungs)
        else:
            self.layers.append(self.lungs)
            self.layers.append(self.heart)

        self.layers.extend(outerlayers)
        self.youngscalc()
        super().damageresolve(attack,attacker,reactionforce=reactionforce)


class Wing(Limb):


    def __init__(self,stats,name='wing',scale=1,length=0.06,radius=0.2,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.length=length*scale
        self.radius=radius*scale
        self.sizefactor=10
        self.owner=owner
        self.owner.limbs.append(self)
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=True
        self.ability=1
        self.stats=stats
        self.primaryequip=[]
        self.equiptype=[]
        self.equipment={}
        self.armor=None


        self.scars=[]
        self.descriptor='This is a wing of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.radius,radius=self.length*0.5,threshold=0.5),Flesh(length=self.radius*1.2,in_radius=self.length*0.8,out_radius=self.length,threshold=0.2)]
        self.mass_calc()
        self.youngscalc()
        self.balance_calc()
        self.defaultattacks=[]
        self.attacks=self.defaultattacks
        self.armortype=None


    def equip(self,item):
        self.youngscalc()




    def on_wounds(self,*args):
        self.ability=1

        self.ability=max(self.ability,0)
        if self.ability==0:
            self.support=False
        toefunction=0
        for i in self.limbs:
            toefunction+=i.ability


        self.balance=toefunction+2*self.ability

        self.balance=min(self.balance,self.attachpoint.balance*6)

        if self.balance<2:
            self.support=False


        if self.support==False:
            self.descriptor+=' Injuries have left it impossible to walk on.'
            self.attacktype=None


    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats

    def balance_calc(self):
        number_of_wings=0
        for i in self.owner.limbs:
            if isinstance(i,Wing):
                if i.ability>0.1:
                    number_of_wings+=1
        if number_of_wings<2:
            self.balance=0
            self.support=False
            return
        self.balance=5*self.ability
        if self.balance<=0:
            self.support=False
        elif self.attachpoint is None:
            self.support=False
            self.balance=0
        else:
            self.support=True
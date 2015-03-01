__author__ = 'Alan'



import kivy
from kivy.properties import ListProperty, DictProperty
from BaseClasses import *
from Materials import *
from Items import *


def inventoryadd(item):
    print('{} added to inventory'.format(item))
def dropitem(item):
    print('You drop the {}'.format(item))

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

self.diagnosis is what the game will print to the player upon query

self.attacktype is the type of attack the limb grants. It depends upon current equipment when applicable
'''




class Finger(Limb):
    limbs=ListProperty([])
    stats=DictProperty({})
    def __init__(self,stats,name,length=0.1,radius=0.01,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.owner=owner
        self.sizefactor=2
        self.length=length
        self.radius=radius
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.equiptype=['ring','glove']
        self.equipment={'ring':None,'glove':None}
        self.armor=None
        self.scars=[]
        self.diagnosis='This is a humanoid finger of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius*0.8),Flesh(length=self.length,in_radius=self.radius*0.8,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()


    def equip(self,item):
        if item.wield=='ring':
            if self.equipment['ring']!=None:
                if self.equipment['ring'].mass:
                    self.movemass-=self.equipment['ring'].mass
                inventoryadd(self.equipment['ring'])
            self.equipment['ring']=item
            if item.mass:
                self.movemass+=item.mass

        if item.wield=='glove':
            self.equipment['glove']=item


    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        pass


class Hand(Limb):
    limbs=ListProperty(())
    stats=DictProperty(None)
    def __init__(self,stats,name,length=0.1,radius=0.022,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=10
        self.owner=owner
        self.natural=natural
        self.name=name
        self.length=length
        self.radius=radius
        self.grasp=True
        self.support=False
        self.ability=1
        self.stats=stats
        self.equiptype=['glove','grasp']
        self.equipment={'glove':None,'grasp':None}
        self.armor=None

        self.thumb=Finger(stats,'thumb, {}'.format(name),owner=owner)
        self.firstfinger=Finger(stats,'first finger, {}'.format(name),owner=owner)
        self.secondfinger=Finger(stats,'second finger, {}'.format(name),owner=owner)
        self.thirdfinger=Finger(stats,'third finger, {}'.format(name),owner=owner)
        self.fourthfinger=Finger(stats,'fourth finger, {}'.format(name),owner=owner)

        self.limbs=[self.thumb,self.firstfinger,self.secondfinger,self.thirdfinger,self.fourthfinger]
        self.scars=[]
        self.diagnosis='This is a humanoid hand of {}.'.format(self.owner.indefinitename)
        self.attacktype='punch'
        self.dexterity=self.ability
        for i in self.limbs:
            self.dexterity+=i.ability
            i.attachpoint=self
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius*0.9),Flesh(length=self.length,in_radius=self.radius*0.9,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()


    def equip(self,item):
        if item.wield=='glove':
            if self.equipment['glove']!=None:
                inventoryadd(self.equipment['glove'])
                if self.equipment['glove'].mass:
                    self.movemass-=self.equipment['glove'].mass
            self.equipment['glove']=item
            if item.mass:
                self.movemass+=item.mass
            for i in self.limbs:
                i.equip(item)

        if self.grasp==True:
            if item.wield=='grasp':
                if self.equipment['grasp']!=None:
                    inventoryadd(self.equipment['grasp'])
                    if self.equipment['grasp'].mass:
                        self.movemass-=self.equipment['glove'].mass

                self.equipment['grasp']=item
                if item.mass:
                    self.movemass+=item.mass
                self.attacktype=item.attacktype



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
            if self.equipment['grasp']!=None:
                dropitem(self.equipment['grasp'])
                self.equipment['grasp']=None
                self.attacktype=None


    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Arm(Limb):
    limbs=ListProperty(())
    stats=DictProperty(None)
    def __init__(self,stats,name,length=0.75,boneradius=0.013,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=100
        self.owner=owner
        self.natural=natural
        self.name=name+' arm'
        self.length=length
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.radius=(self.stats['str']/10000+boneradius**2)**0.5
        self.equiptype=['armlet','bracelet']
        self.equipment={'armlet':None,'bracelet':None}
        self.armor=None

        self.hand=Hand(stats,'{} hand'.format(name),owner=owner)
        self.hand.attachpoint=self

        self.limbs=[self.hand]
        self.scars=[]
        self.diagnosis='This is an arm of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=boneradius),Flesh(length=self.length,in_radius=boneradius,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()


    def equip(self,item):
        if item.wield=='armlet':
            if self.equipment['armlet']!=None:
                inventoryadd(self.equipment['armlet'])
                if self.equipment['armlet'].mass:
                    self.movemass-=self.equipment['armlet'].mass
            self.equipment['armlet']=item
            if item.mass:
                self.movemass+=item.mass

        if item.wield=='bracelet':
            if self.equipment['bracelet']!=None:
                inventoryadd(self.equipment['bracelet'])
                if self.equipment['bracelet'].mass:
                    self.movemass+=self.equipment['bracelet'].mass
            self.equipment['bracelet']=item
            if item.mass:
                self.movemass+=item.mass




    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Torso(Limb):
    limbs=ListProperty(())
    stats=DictProperty(None)
    def __init__(self,stats,name,length=0.9,radius=0.1,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=40
        self.owner=owner
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.length=length
        self.radius=radius
        self.equiptype=['chest']
        self.equipment={'chest':None}
        self.armor=None

        self.rightarm=Arm(stats,'right',owner=owner)
        self.rightarm.attachpoint=self
        self.leftarm=Arm(stats,'left',owner=owner)
        self.leftarm.attachpoint=self
        self.rightleg=Leg(stats,'right',owner=owner)
        self.rightleg.attachpoint=self
        self.leftleg=Leg(stats,'left',owner=owner)
        self.leftleg.attachpoint=self
        self.head=Head(stats,'head',owner=owner)
        self.head.attachpoint=self

        self.limbs=[self.rightarm,self.leftarm,self.rightleg,self.leftleg,self.head]
        self.scars=[]
        self.diagnosis='This is a torso of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Flesh(length=self.length,out_radius=self.radius*0.8,in_radius=0,name='vital organs',plural=True),Bone(length=self.length,radius=self.radius*0.9,in_radius=self.radius*0.8,name='ribs',plural=True),Flesh(length=self.length,in_radius=self.radius*0.9,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()


    def equip(self,item):
        if item.wield=='chest':
            if self.equipment['chest']!=None:
                inventoryadd(self.equipment['chest'])
                if self.equipment['chest'].mass:
                    self.movemass-=self.equipment['chest'].mass
            self.equipment['chest']=item
            if item.mass:
                self.movemass+=item.mass




    def on_wounds(self,*args):
        self.ability=1
        self.diagnosis='This is a torso of {}.'.format(self.owner.indefinitename)



    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Toe(Limb):
    limbs=ListProperty(())
    stats=DictProperty(None)
    def __init__(self,stats,name,length=0.05,radius=0.005,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=2
        self.owner=owner
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.length=length
        self.radius=radius
        self.equiptype=['boot']
        self.equipment={'boot':None}
        self.armor=None


        self.limbs=[]
        self.scars=[]
        self.diagnosis='This is a humanoid toe of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius*0.8),Flesh(length=self.length,in_radius=self.radius*0.8,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()

    def equip(self,item):
        if item.wield=='boot':
            self.equipment['boot']=item




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
    limbs=ListProperty(())
    stats=DictProperty(None)
    def __init__(self,stats,name,length=0.22,radius=0.035,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.length=length
        self.radius=radius
        self.sizefactor=10
        self.owner=owner
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=True
        self.ability=1
        self.stats=stats
        self.equiptype=['boot']
        self.equipment={'boot':None}
        self.armor=None


        self.firsttoe=Toe(stats,'big toe, {}'.format(name),owner=owner)
        self.secondtoe=Toe(stats,'second toe, {}'.format(name),owner=owner)
        self.thirdtoe=Toe(stats,'third toe, {}'.format(name),owner=owner)
        self.fourthtoe=Toe(stats,'fourth toe, {}'.format(name),owner=owner)
        self.fifthtoe=Toe(stats,'little toe, {}'.format(name),owner=owner)

        self.limbs=[self.firsttoe,self.secondtoe,self.thirdtoe,self.fourthtoe,self.fifthtoe]
        self.scars=[]
        self.diagnosis='This is a humanoid foot of {}.'.format(self.owner.indefinitename)
        self.attacktype='kick'
        self.balance=self.ability
        for i in self.limbs:
            self.balance+=i.ability
            i.attachpoint=self
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius*0.8),Flesh(length=self.length,in_radius=self.radius*0.8,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()


    def equip(self,item):
        if item.wield=='boot':
            if self.equipment['boot']!=None:
                inventoryadd(self.equipment['boot'])
                if self.equipment['boot'].mass:
                    self.movemass-=self.equipment['boot'].mass
            self.equipment['boot']=item
            if item.mass:
                self.movemass+=item.mass
            for i in self.limbs:
                i.equip(item)




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
            self.diagnosis+=' Injuries have left it impossible to walk on.'
            self.attacktype=None


    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Leg(Limb):
    limbs=ListProperty(())
    stats=DictProperty(None)
    def __init__(self,stats,name,length=0.8,boneradius=0.018,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.length=length
        self.sizefactor=80
        self.owner=owner
        self.natural=natural
        self.name=name+'leg'
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.radius=(self.stats['str']/3500+boneradius**2)**0.5
        self.equiptype=['legging']
        self.equipment={'legging':None}
        self.armor=None

        self.foot=Foot(stats,'{} foot'.format(name),owner=owner)
        self.foot.attachpoint=self

        self.limbs=[self.foot]
        self.scars=[]
        self.diagnosis='This is a humanoid leg of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=boneradius),Flesh(length=self.length,in_radius=boneradius,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()

    def equip(self,item):
        if item.wield=='legging':
            if self.equipment['legging']!=None:
                inventoryadd(self.equipment['legging'])
                if self.equipment['legging'].mass:
                    self.movemass-=self.equipment['legging'].mass
            self.equipment['legging']=item
            if item.mass:
                self.movemass+=item.mass



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
    limbs=ListProperty([])
    stats=DictProperty({})
    def __init__(self,stats,name,length=0.008,radius=0.02,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.radius=radius
        self.length=length
        self.owner=owner
        self.sizefactor=1
        self.natural=natural
        self.name=name+'ear'
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=None
        self.scars=[]
        self.diagnosis='This is an ear of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Flesh(length=self.length,in_radius=0,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()

    def equip(self,item):
        if item.wield=='helmet':
            self.equipment['helmet']=item


    def on_wounds(self,*args):
        self.ability=1
        self.ability=max(self.ability,0)

    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        pass


class Nose(Limb):
    limbs=ListProperty([])
    stats=DictProperty({})
    def __init__(self,stats,name,length=0.01,radius=0.02,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.radius=radius
        self.length=length
        self.owner=owner
        self.sizefactor=1
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=None
        self.scars=[]
        self.diagnosis='This is a nose of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Flesh(length=self.length,in_radius=0,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()

    def equip(self,item):
        if item.wield=='helmet':
            self.equipment['helmet']=item


    def on_wounds(self,*args):
        self.ability=1
        self.ability=max(self.ability,0)

    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        pass


class Eye(Limb):
    limbs=ListProperty([])
    stats=DictProperty({})
    def __init__(self,stats,name,length=None,radius=0.013,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.radius=radius
        self.length=radius
        self.owner=owner
        self.sizefactor=1
        self.natural=natural
        self.name=name+'eye'
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=None
        self.scars=[]
        self.diagnosis='This is an eye of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Flesh(length=self.length,in_radius=0,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()

    def equip(self,item):
        if item.wield=='helmet':
            self.equipment['helmet']=item


    def on_wounds(self,*args):
        self.ability=1
        self.ability=max(self.ability,0)

    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        pass


class Teeth(Limb):
    limbs=ListProperty(())
    stats=DictProperty(None)
    def __init__(self,stats,name,length=0.12,radius=0.005,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=1
        self.owner=owner
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.length=length
        self.radius=radius
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=None


        self.limbs=[]
        self.scars=[]
        self.diagnosis='These are the teeth of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()

    def equip(self,item):
        if item.wield=='helmet':
            self.equipment['helmet']=item




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
    limbs=ListProperty(())
    stats=DictProperty(None)
    def __init__(self,stats,name,length=0.2,radius=0.018,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=3
        self.owner=owner
        self.natural=natural
        self.name=name
        self.length=length
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.radius=radius
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=None

        self.teeth=Teeth(stats,"lower teeth",owner=owner)
        self.teeth.attachpoint=self

        self.limbs=[self.teeth]
        self.scars=[]
        self.diagnosis='This is a jaw of {}.'.format(self.owner.indefinitename)
        self.attacktype='bite'
        self.attachpoint=None
        self.layers=[Bone(length=self.length,radius=self.radius*0.8),Flesh(length=self.length,in_radius=self.radius*0.8,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()


    def equip(self,item):
        if item.wield=='helmet':
            self.equipment['helmet']=item




    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


class Head(Limb):
    limbs=ListProperty(())
    stats=DictProperty(None)
    def __init__(self,stats,name,length=0.2,radius=0.08,natural=True,owner=None,**kwargs):
        super().__init__(stats,**kwargs)
        self.sizefactor=10
        self.owner=owner
        self.natural=natural
        self.name=name
        self.grasp=False
        self.support=False
        self.ability=1
        self.stats=stats
        self.length=length
        self.radius=radius
        self.equiptype=['helmet']
        self.equipment={'helmet':None}
        self.armor=None

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

        self.brain=Flesh(length=self.length*0.8,in_radius=0,out_radius=self.radius*0.75,name='brain')


        self.limbs=[self.righteye,self.lefteye,self.rightear,self.leftear,self.jaw,self.nose,self.teeth]
        self.scars=[]
        self.diagnosis='This is a head of {}.'.format(self.owner.indefinitename)
        self.attacktype=None
        self.attachpoint=None
        self.layers=[self.brain,Bone(length=self.length,radius=self.radius*0.9,in_radius=self.radius*0.75,name='skull'),Flesh(length=self.length,in_radius=self.radius*0.9,out_radius=self.radius)]
        self.mass=0
        for i in self.layers:
            self.mass+=i.mass
        self.movemass=self.mass
        for i in self.limbs:
            self.movemass+=i.movemass
        self.youngscalc()


    def equip(self,item):
        if item.wield=='helmet':
            if self.equipment['helmet']!=None:
                inventoryadd(self.equipment['helmet'])
                if self.equipment['helmet'].mass:
                    self.movemass-=self.equipment['helmet'].mass
            self.equipment['helmet']=item
            if item.mass:
                self.movemass+=item.mass
            for i in self.limbs:
                i.equip(item)





    def on_wounds(self,*args):
        self.ability=1
        self.diagnosis='This is a head of {}.'.format(self.owner.indefinitename)



    def on_limbs(self,*args):
        pass

    def on_stats(self,*args):
        for i in self.limbs:
            if i.natural==True:
                i.stats=self.stats


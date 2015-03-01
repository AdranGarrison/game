__author__ = 'Alan'

from BaseClasses import *
import random


#Thickness in mm
#Density in kg/m^3.
#Young's Modulus in GPa
#Fracture energy is in kJ/m^2
#Tensile strength is in MPa and is Ultimate Tensile Strength, not yield strength
#Mode is either brittle, ductile, or soft
#Brittle materials crack or shatter when they fail
#Ductile materials dent, bend, or shear when they fail
#Soft materials bruise or cut when they fail
#All materials can be smashed
#Fracture toughness is in MPa*m^1/2
#Shear modulus is in GPa
#Shear strength is in MPa


##############################################MATERIALS###############################################################

class Bone_Material(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='bone'
        self.maxquality=1.1
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=1900
        self.youngs=12
        self.fracture_energy=1.5*self.quality
        self.tensile_strength=50*self.quality
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=3.3
        self.shear_strength=70*self.quality
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1.5
        self.maxedge=(10**-4)/self.quality
        self.damagetype=['crack','break','crush','cut','shatter']

    def damageresolve(self,damagedobject,defender,force,pressure,attacker):
        if isinstance(defender,Limb)==True:
            defenderstats=defender.stats
        elif isinstance(defender,Creature)==True:
            defenderstats=defender.stats
        else:
            defenderstats={'str':10,'tec':10,'per':10,'wil':10,'luc':10}
        m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)


#Cutting---------------------------------------------------------------------
        rootarea=(force/pressure)**0.5
        if 1.5*force*(1/(3.5*damagedobject.thickness*rootarea)-self.density*rootarea/(3.5*damagedobject.mass))>self.shear_strength*1000000:
            damagedobject.damage['cut']+=1
#----------------------------------------------------------------------------

#Crushing--------------------------------------------------------------------
        if pressure>self.tensile_strength*(1200000-200000*random.triangular(low=0,high=1,mode=m)) and damagedobject.damage['crush']==0:
            damagedobject.damage['crush']=1
            pass
#----------------------------------------------------------------------------



#Cracking, Breaking, and Shattering------------------------------------------
        hitloc=random.triangular(low=0,high=1,mode=m)*damagedobject.length
        if force>10*(1-damagedobject.damage['crack'])*(3.14*self.tensile_strength*1000000*damagedobject.thickness**3)/hitloc:
            severity=force/((10*3.14*self.tensile_strength*1000000*damagedobject.thickness**3)/hitloc)-1
            cracklength=damagedobject.damage['crack']**0.5+severity**0.5

            #Cracked but not broken
            if cracklength<1:
                damagedobject.damage['crack']+=severity


            #Broken but not shattered
            elif severity<3 and damagedobject.damage['break']==0:
                damagedobject.damage['crack']=1
                damagedobject.damage['break']=1


            #Shattered
            elif severity>=3 and damagedobject.damage['shatter']==0:
                damagedobject.damage['crack']=1
                damagedobject.damage['break']=1
                damagedobject.damage['shatter']=1

#-----------------------------------------------------------------------------







class Flesh_Material(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='flesh'
        self.maxquality=1.1
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=1000
        self.youngs=0.00002
        self.fracture_energy=0.2*self.quality
        self.tensile_strength=1.6*self.quality
        self.mode='soft'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=0.00002
        self.shear_strength=0.4*self.quality
        self.electric_conduction=True
        self.heat_conduction=False
        self.dissipationfactor=1.5
        self.maxedge=0.01
        self.damagetype=['bruise','cut','crush']

    def damageresolve(self,damagedobject,defender,force,pressure,attacker):
        if isinstance(defender,Limb)==True:
            defenderstats=defender.stats
        elif isinstance(defender,Creature)==True:
            defenderstats=defender.stats
        else:
            defenderstats={'str':15,'tec':15,'per':15,'wil':15,'luc':15}


        #Bruising
        if pressure>self.tensile_strength*200000:
            severity=(pressure/(self.tensile_strength*200000)-1)*random.gauss(0.5*attacker.stats['luc']/defenderstats['luc'],0.5)
            pythagoreanseverity=(severity**2+damagedobject.damage['bruise']**2)**0.5
            damagedobject.damage['bruise']=pythagoreanseverity



class Iron(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='iron'
        self.maxquality=2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=7874
        self.youngs=118
        self.fracture_energy=11*self.quality
        self.tensile_strength=310*self.quality
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=48
        self.shear_strength=304*self.quality
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['crack','break','shatter','crush','cut']

    def damageresolve(self,damagedobject,defender,force,pressure,attacker):
        if isinstance(defender,Limb)==True:
            defenderstats=defender.stats
        elif isinstance(defender,Creature)==True:
            defenderstats=defender.stats
        else:
            defenderstats={'str':15,'tec':15,'per':15,'wil':15,'luc':15}

        #Cracking
        m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)
        hitloc=random.triangular(low=0,high=1,mode=m)*damagedobject.length
        if force>10*(3.14*self.tensile_strength*1000000*damagedobject.thickness**3)/hitloc:
            if damagedobject.plural==False:
                print("the {} is cracked".format(damagedobject.name))
            else:
                print("the {} are cracked".format(damagedobject.name))
            severity=force/((10*3.14*self.tensile_strength*1000000*damagedobject.thickness**3)/hitloc)-1
            damagedobject.damage['crack']+=severity


class Steel(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='steel'
        self.maxquality=3
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=7850
        self.youngs=211
        self.fracture_energy=11.8*self.quality*self.quality
        self.tensile_strength=900*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=80
        self.shear_strength=0.6*self.tensile_strength
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(5*10**-8)/self.quality
        self.damagetype=['dent','crush','bend','cut']


class Copper(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='copper'
        self.maxquality=1.2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=8960
        self.youngs=116
        self.fracture_energy=2*self.quality
        self.tensile_strength=318*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=44
        self.shear_strength=178*self.quality
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(1.5*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']

class Bronze(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='bronze'
        self.maxquality=2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=8860
        self.youngs=110
        self.fracture_energy=56*self.quality
        self.tensile_strength=491*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=43
        self.shear_strength=297*self.tensile_strength
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']

class Brass(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='brass'
        self.maxquality=2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=8550
        self.youngs=110
        self.fracture_energy=11.3*self.quality
        self.tensile_strength=435*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=39
        self.shear_strength=273*self.quality
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']


class Titanium(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='titanium'
        self.maxquality=1.5
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=4500
        self.youngs=114
        self.fracture_energy=11.3*self.quality
        self.tensile_strength=1060*self.quality
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=44
        self.shear_strength=711*self.quality
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(5*10^-8)/self.quality
        self.damagetype=['crack','break','shatter','crush','cut']

    def damageresolve(self,damagedobject,defender,force,pressure,attacker):
        if isinstance(defender,Limb)==True:
            defenderstats=defender.stats
        elif isinstance(defender,Creature)==True:
            defenderstats=defender.stats
        else:
            defenderstats={'str':15,'tec':15,'per':15,'wil':15,'luc':15}


        #Cracking
        m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)
        hitloc=random.triangular(low=0,high=1,mode=m)*damagedobject.length
        if force>10*(3.14*self.tensile_strength*1000000*damagedobject.thickness**3)/hitloc:
            if damagedobject.plural==False:
                print("the {} is cracked".format(damagedobject.name))
            else:
                print("the {} are cracked".format(damagedobject.name))
            severity=force/((10*3.14*self.tensile_strength*1000000*damagedobject.thickness**3)/hitloc)-1
            damagedobject.damage['crack']+=severity


class Silver(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='silver'
        self.maxquality=1.5
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=16000
        self.youngs=81
        self.fracture_energy=11.3*self.quality
        self.tensile_strength=333*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=30
        self.shear_strength=self.tensile_strength*0.65
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(2*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']

class Aluminum(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='aluminum'
        self.maxquality=1.1
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=2699
        self.youngs=68
        self.fracture_energy=5.88*self.quality
        self.tensile_strength=45*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=25
        self.shear_strength=self.tensile_strength*0.65
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(2*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']

class Duraluminum(Material):
    #Copper Aluminum alloy
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='duraluminum'
        self.maxquality=3
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=2780
        self.youngs=73
        self.fracture_energy=5.63*self.quality
        self.tensile_strength=200*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=27.5
        self.shear_strength=100*self.quality
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(1.5*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']

class Zicral(Material):
    #Zinc Aluminum alloy
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='zicral'
        self.maxquality=5
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=2810
        self.youngs=71.1
        self.fracture_energy=18*self.quality
        self.tensile_strength=140*self.quality
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=26.8
        self.shear_strength=100*self.quality
        self.electric_conduction=True
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['crack','break','shatter','crush','cut']

    def damageresolve(self,damagedobject,defender,force,pressure,attacker):
        if isinstance(defender,Limb)==True:
            defenderstats=defender.stats
        elif isinstance(defender,Creature)==True:
            defenderstats=defender.stats
        else:
            defenderstats={'str':15,'tec':15,'per':15,'wil':15,'luc':15}


        #Cracking
        m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)
        hitloc=random.triangular(low=0,high=1,mode=m)*damagedobject.length
        if force>10*(3.14*self.tensile_strength*1000000*damagedobject.thickness**3)/hitloc:
            if damagedobject.plural==False:
                print("the {} is cracked".format(damagedobject.name))
            else:
                print("the {} are cracked".format(damagedobject.name))
            severity=force/((10*3.14*self.tensile_strength*1000000*damagedobject.thickness**3)/hitloc)-1
            damagedobject.damage['crack']+=severity


class Wood(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        self.name='wood'
        self.maxquality=1.5
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=450
        self.youngs=11
        self.fracture_energy=1.5*self.quality
        self.tensile_strength=45*self.quality
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=2
        self.shear_strength=10*self.quality
        self.electric_conduction=False
        self.heat_conduction=False
        self.dissipationfactor=1
        self.maxedge=(10**-4)/self.quality
        self.damagetype=['dent','crack','break','crush','cut']

    def damageresolve(self,damagedobject,defender,force,pressure,attacker):
        if isinstance(defender,Limb)==True:
            defenderstats=defender.stats
        elif isinstance(defender,Creature)==True:
            defenderstats=defender.stats
        else:
            defenderstats={'str':15,'tec':15,'per':15,'wil':15,'luc':15}


        #Cracking
        m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)
        hitloc=random.triangular(low=0,high=1,mode=m)*damagedobject.length
        if force>10*(3.14*self.tensile_strength*1000000*damagedobject.thickness**3)/hitloc:
            if damagedobject.plural==False:
                print("the {} is cracked".format(damagedobject.name))
            else:
                print("the {} are cracked".format(damagedobject.name))
            severity=force/((10*3.14*self.tensile_strength*1000000*damagedobject.thickness**3)/hitloc)-1
            damagedobject.damage['crack']+=severity


class Leather(Material):
    pass

class Cloth(Material):
    pass

######################################################################################################################


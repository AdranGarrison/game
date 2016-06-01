__author__ = 'Alan'


#from BaseClasses import *
import BaseClasses
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
#Magic affinity runs from 1-10

##############################################MATERIALS###############################################################

class Bone_Material(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.8,0.8,0.8,1)
        self.poisson=0.31
        self.basicname='bone'
        self.name='bone'
        self.heat_reaction='burn'
        self.maxquality=1.1
        self.default_thickness=0.02
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=1900
        self.youngs=12
        self.fracture_energy=2.5*self.quality
        self.tensile_strength=35*self.quality
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=3.3
        self.shear_strength=30*self.quality
        self.poisonable=True
        self.electric_conduction=True
        self.heat_conduction=0.5
        self.dissipationfactor=4
        self.maxedge=(10**-4)/self.quality
        self.damagetype=['crack','break','crush','cut','shatter','sever']
        self.magic_affinity=7
        self.identification_difficulty=5
'''    def damageresolve(self,attack,attacker,reactionforce=False):
        damagedobject=attack.target
        basetarget=attack.basetarget
        if isinstance(attack.basetarget,Limb)==True:
            defenderstats=attack.basetarget.stats
        elif isinstance(attack.basetarget,Creature)==True:
            defenderstats=attack.basetarget.stats
        elif attack.basetarget.stats:
            defenderstats=attack.basetarget.stats
        else:
            defenderstats={'str':10,'tec':10,'per':10,'wil':10,'luc':10}
        m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)
        contact=False

#Cutting---------------------------------------------------------------------
        rootarea=(attack.force/attack.pressure)**0.5
        shearforce=1.5*attack.force*(1/(3.5*damagedobject.thickness*rootarea)-self.density*rootarea/(3.5*damagedobject.mass))
        if isinstance(attack.basetarget,Limb):
            shearforce=shearforce*(damagedobject.mass/basetarget.mass)**0.5
        if shearforce>self.shear_strength*1000000 and attack.contact==True and attack.type=='cut':
            damagedobject.damage['cut']+=1
            contact=True
#----------------------------------------------------------------------------

#Crushing--------------------------------------------------------------------
        if attack.force>self.tensile_strength*(1200000-200000*random.triangular(low=0,high=1,mode=m))*damagedobject.length*damagedobject.radius and damagedobject.damage['crush']==0 and attack.contact==True:
            damagedobject.damage['crush']=1
            contact=True
#----------------------------------------------------------------------------



#Cracking, Breaking, and Shattering------------------------------------------
        hitloc=random.triangular(low=0,high=1,mode=m)*damagedobject.length
        crackforce=attack.force #*(damagedobject.mass/basetarget.mass)**0.5
        if crackforce>10*(1-damagedobject.damage['crack'])*(self.tensile_strength*1000000*damagedobject.r*damagedobject.thickness**2)/hitloc:
            severity=crackforce/(10*(1-damagedobject.damage['crack'])*(self.tensile_strength*1000000*damagedobject.r*damagedobject.thickness**2)/hitloc)-1
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


        if contact==True:
            attack.contact=True
            attack.energy-=7*self.fracture_energy*1000*rootarea*damagedobject.thickness
            attack.energy_recalc()
        else:
            attack.contact=False

#-----------------------------------------------------------------------------

        if contact==True:
            attack.contact=True
            attack.energy-=7*self.fracture_energy*1000*rootarea*damagedobject.thickness
            attack.energy_recalc()
        else:
            attack.contact=False

'''

class Keratin(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.8,0.8,0.8,1)
        self.poisson=0.31
        self.basicname='bone'
        self.name='bone'
        self.heat_reaction='burn'
        self.burn_temp=300
        self.maxquality=5
        self.default_thickness=0.02
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=1500
        self.youngs=1.5
        self.fracture_energy=20*self.quality
        self.tensile_strength=45*self.quality
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=0.8
        self.shear_strength=15*self.quality
        self.electric_conduction=True
        self.heat_conduction=0.0005
        self.dissipationfactor=4
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['crack','break','crush','cut','shatter','sever']
        self.magic_affinity=7
        self.identification_difficulty=5

class Flesh_Material(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.86,0.66,0.52,1)
        self.poisson=0.45
        self.acid_resistance=4
        self.fluid='blood'
        self.heat_reaction='burn'
        self.burn_temp=90
        self.default_thickness=0.02
        self.basicname='flesh'
        self.name='flesh'
        self.maxquality=5
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=1000
        self.youngs=0.06
        self.fracture_energy=0.2*self.quality
        self.tensile_strength=1.4*self.quality
        self.mode='soft'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=0.02
        self.shear_strength=0.6*self.quality
        self.poisonable=True
        self.electric_conduction=True
        self.heat_conduction=0.25
        self.burn_resistance=80
        self.dissipationfactor=1.5
        self.maxedge=0.01
        self.damagetype=['bruise','cut','crush']
        self.magic_affinity=7
        self.identification_difficulty=5
'''
    def damageresolve(self,attack,attacker):
        damagedobject=attack.target
        basetarget=attack.basetarget
        if isinstance(attack.basetarget,Limb)==True:
            defenderstats=attack.basetarget.stats
        elif isinstance(attack.basetarget,Creature)==True:
            defenderstats=attack.basetarget.stats
        elif attack.basetarget.stats:
            defenderstats=attack.basetarget.stats
        else:
            defenderstats={'str':15,'tec':15,'per':15,'wil':15,'luc':15}
        m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)
        contact=False

#Cutting---------------------------------------------------------------------
        rootarea=(attack.force/attack.pressure)**0.5
        shearforce=1.5*attack.force*(1/(3.5*damagedobject.thickness*rootarea)-self.density*rootarea/(3.5*damagedobject.mass))
        if isinstance(attack.basetarget,Limb):
            shearforce=shearforce*(damagedobject.mass/basetarget.mass)**0.5
        if shearforce>self.shear_strength*1000000 and attack.contact==True and attack.type=='cut':
            damagedobject.damage['cut']+=1
            contact=True
#----------------------------------------------------------------------------

#Crushing--------------------------------------------------------------------
        if attack.force>self.tensile_strength*(1200000-200000*random.triangular(low=0,high=1,mode=m))*damagedobject.length*damagedobject.radius and damagedobject.damage['crush']==0 and attack.contact==True:
            damagedobject.damage['crush']=1
            contact=True
#----------------------------------------------------------------------------


#Bruising
        if attack.pressure>self.tensile_strength*200000:
            severity=(attack.pressure/(self.tensile_strength*200000)-1)*random.gauss(0.5*attacker.stats['luc']/defenderstats['luc'],0.5)
            pythagoreanseverity=(severity**2+damagedobject.damage['bruise']**2)**0.5
            damagedobject.damage['bruise']=pythagoreanseverity


        if contact==True:
            attack.contact=True
            attack.energy-=7*self.fracture_energy*1000*rootarea*damagedobject.thickness
            attack.energy_recalc()
        else:
            attack.contact=False
'''

class Slime(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.30,0.59,0.30,1)
        self.poisson=0.45
        self.acid_resistance=20
        self.fluid='slime'
        self.default_thickness=0.02
        self.basicname='slime'
        self.name='slime'
        self.maxquality=20
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=1200
        self.youngs=0.03
        self.fracture_energy=0.2*self.quality
        self.tensile_strength=1.4*self.quality
        self.mode='soft'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=0.01
        self.shear_strength=0.6*self.quality
        self.poisonable=True
        self.electric_conduction=True
        self.heat_reaction='burn'
        self.burn_temp=800
        self.heat_conduction=0.25
        self.burn_resistance=100
        self.dissipationfactor=1.5
        self.maxedge=0.01
        self.damagetype=['bruise','cut','crush']
        self.magic_affinity=8
        self.identification_difficulty=5

class Iron(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.64,0.64,0.64,1)
        self.wetdamage='rust'
        self.poisson=0.3
        self.default_thickness=0.002
        self.basicname='metal'
        self.name='iron'
        self.maxquality=2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=7874
        self.youngs=118
        self.fracture_energy=21*self.quality
        self.tensile_strength=310*self.quality
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=48
        self.shear_strength=304*self.quality
        self.electric_conduction=True
        self.heat_conduction=79
        self.burn_temp=1500
        self.dissipationfactor=8
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['crack','break','shatter','crush','cut']
        self.magic_affinity=3
        self.identification_difficulty=15
'''
    def damageresolve(self,attack,attacker):
        damagedobject=attack.target
        basetarget=attack.basetarget
        if isinstance(attack.basetarget,Limb)==True:
            defenderstats=attack.basetarget.stats
        elif isinstance(attack.basetarget,Creature)==True:
            defenderstats=attack.basetarget.stats
        elif attack.basetarget.stats:
            defenderstats=attack.basetarget.stats
        else:
            defenderstats={'str':10,'tec':10,'per':10,'wil':10,'luc':10}
        m=min(0.5*attacker.stats['luc']/defenderstats['luc'],1)
        contact=False


#Cutting---------------------------------------------------------------------
        rootarea=(attack.force/attack.pressure)**0.5
        shearforce=1.5*attack.force*(1/(3.5*damagedobject.thickness*rootarea)-self.density*rootarea/(3.5*damagedobject.mass))
        if isinstance(attack.basetarget,Limb):
            shearforce=shearforce*(damagedobject.mass/basetarget.mass)**0.5
        if shearforce>self.shear_strength*1000000 and attack.contact==True and attack.type=='cut':
            damagedobject.damage['cut']+=1
            contact=True
#----------------------------------------------------------------------------

#Crushing--------------------------------------------------------------------
        if attack.force>self.tensile_strength*(1200000-200000*random.triangular(low=0,high=1,mode=m))*damagedobject.length*damagedobject.radius and damagedobject.damage['crush']==0 and attack.contact==True:
            damagedobject.damage['crush']=1
            contact=True
#----------------------------------------------------------------------------



#Cracking, Breaking, and Shattering------------------------------------------
        hitloc=random.triangular(low=0.001,high=1,mode=m)*damagedobject.length
        crackforce=attack.force #*(damagedobject.mass/basetarget.mass)**0.5
        if crackforce>10*(1.01-damagedobject.damage['crack'])*(self.tensile_strength*1000000*damagedobject.r*damagedobject.thickness**2)/hitloc:
            severity=crackforce/(10*(1.01-damagedobject.damage['crack'])*(self.tensile_strength*1000000*damagedobject.r*damagedobject.thickness**2)/hitloc)-1
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


        if contact==True:
            attack.contact=True
            attack.energy-=7*self.fracture_energy*1000*rootarea*damagedobject.thickness
            attack.energy_recalc()
        else:
            attack.contact=False

#-----------------------------------------------------------------------------
'''

class Steel(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.64,0.64,0.64,1)
        self.acid_reaction='embrittle'
        self.wetdamage='rust'
        self.poisson=0.3
        self.default_thickness=0.002
        self.basicname='metal'
        self.name='steel'
        self.maxquality=3
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=7850
        self.youngs=211
        self.fracture_energy=40*self.quality*self.quality
        self.tensile_strength=900*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=80
        self.shear_strength=0.6*self.tensile_strength
        self.electric_conduction=True
        self.heat_conduction=50
        self.burn_temp=1500
        self.dissipationfactor=1
        self.maxedge=(5*10**-8)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=2
        self.identification_difficulty=15

class Copper(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.96,0.56,0.2,1)
        self.poisson=0.34
        self.acid_resistance=8
        self.default_thickness=0.002
        self.basicname='metal'
        self.name='copper'
        self.maxquality=1.2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=8960
        self.youngs=116
        self.fracture_energy=30*self.quality
        self.tensile_strength=318*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=44
        self.shear_strength=178*self.quality
        self.electric_conduction=True
        self.heat_conduction=385
        self.burn_temp=1085
        self.dissipationfactor=1
        self.maxedge=(1.5*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=5
        self.identification_difficulty=12

class Bronze(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.96,0.56,0.2,1)
        self.poisson=0.34
        self.acid_reaction='embrittle'
        self.acid_resistance=8
        self.default_thickness=0.002
        self.basicname='metal'
        self.name='bronze'
        self.maxquality=2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=8860
        self.youngs=110
        self.fracture_energy=35.6*self.quality
        self.tensile_strength=491*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=43
        self.shear_strength=297*self.quality
        self.electric_conduction=True
        self.heat_conduction=40
        self.burn_temp=650
        self.dissipationfactor=1
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=6
        self.identification_difficulty=12

class Brass(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.96,0.56,0.2,1)
        self.poisson=0.36
        self.acid_reaction='embrittle'
        self.acid_resistance=6
        self.default_thickness=0.002
        self.basicname='metal'
        self.name='brass'
        self.maxquality=2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=8550
        self.youngs=110
        self.fracture_energy=21.3*self.quality
        self.tensile_strength=435*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=39
        self.shear_strength=273*self.quality
        self.electric_conduction=True
        self.heat_conduction=100
        self.burn_temp=900
        self.dissipationfactor=1
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=4
        self.identification_difficulty=12

class Titanium(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.7,0.7,0.7,1)
        self.poisson=0.3
        self.acid_resistance=9
        self.default_thickness=0.002
        self.basicname='metal'
        self.name='titanium'
        self.maxquality=1.5
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=4500
        self.youngs=114
        self.fracture_energy=11.3*self.quality
        self.tensile_strength=1060*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=44
        self.shear_strength=711*self.quality
        self.electric_conduction=True
        self.heat_reaction='ignite'
        self.burn_temp=1200
        self.heat_conduction=5.8
        self.dissipationfactor=1
        self.maxedge=(5*10^-7)/self.quality
        self.damagetype=['crack','break','shatter','crush','cut']
        self.magic_affinity=2
        self.identification_difficulty=17

class Silver(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.7,0.7,0.7,1)
        self.poisson=0.37
        self.acid_resistance=12
        self.default_thickness=0.002
        self.basicname='metal'
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
        self.heat_conduction=400
        self.burn_temp=900
        self.dissipationfactor=1
        self.maxedge=(2*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=10
        self.identification_difficulty=17

class Aluminum(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.7,0.7,0.7,1)
        self.poisson=0.35
        self.acid_resistance=6
        self.acid_reaction='embrittle'
        self.default_thickness=0.002
        self.basicname='metal'
        self.name='aluminum'
        self.maxquality=1.1
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=2699
        self.youngs=68
        self.fracture_energy=15.88*self.quality
        self.tensile_strength=45*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=25
        self.shear_strength=self.tensile_strength*0.65
        self.electric_conduction=True
        self.heat_conduction=210
        self.burn_temp=500
        self.dissipationfactor=1
        self.maxedge=(2*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=4
        self.identification_difficulty=16

class Duraluminum(BaseClasses.Material):
    #Copper Aluminum alloy
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.7,0.7,0.7,1)
        self.poisson=0.35
        self.acid_resistance=5
        self.acid_reaction='embrittle'
        self.default_thickness=0.002
        self.basicname='metal'
        self.name='duraluminum'
        self.maxquality=3
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=2780
        self.youngs=73
        self.fracture_energy=15.63*self.quality
        self.tensile_strength=200*self.quality
        self.mode='ductile'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=27.5
        self.shear_strength=100*self.quality
        self.electric_conduction=True
        self.heat_conduction=225
        self.burn_temp=630
        self.dissipationfactor=1
        self.maxedge=(1.5*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=3
        self.identification_difficulty=18

class Zicral(BaseClasses.Material):
    #Zinc Aluminum alloy also called ergal
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.7,0.7,0.7,1)
        self.poisson=0.35
        self.acid_resistance=4
        self.acid_reaction='embrittle'
        self.default_thickness=0.002
        self.basicname='metal'
        self.name='zicral'
        self.maxquality=5
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=2810
        self.youngs=71.1
        self.fracture_energy=8*self.quality
        self.tensile_strength=140*self.quality
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=26.8
        self.shear_strength=100*self.quality
        self.electric_conduction=True
        self.heat_conduction=130
        self.burn_temp=550
        self.dissipationfactor=1
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['crack','break','shatter','crush','cut']
        self.magic_affinity=3.5
        self.identification_difficulty=19

class Wood(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.69,0.42,0.19,1)
        self.poisson=0.2
        self.acid_resistance=9
        self.default_thickness=0.005
        self.basicname='wood'
        self.name='wood'
        self.maxquality=1.5
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=700
        self.youngs=10
        self.fracture_energy=1.5*self.quality
        self.tensile_strength=45*self.quality
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=2
        self.shear_strength=10*self.quality
        self.electric_conduction=False
        self.heat_reaction='ignite'
        self.heat_conduction=0.1
        self.burn_temp=200
        self.dissipationfactor=1
        self.maxedge=(10**-4)/self.quality
        self.damagetype=['dent','crack','break','crush','cut']
        self.magic_affinity=7
        self.identification_difficulty=7


class Leather(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.47,0.29,.05,1)
        self.poisson=0.35
        self.acid_resistance=10
        self.default_thickness=0.01
        self.basicname='leather'
        self.name='leather'
        self.maxquality=4
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=860
        self.youngs=0.3
        self.fracture_energy=30*self.quality
        self.tensile_strength=20*self.quality
        self.mode='fabric'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=0.1
        self.shear_strength=0.6*self.tensile_strength
        self.electric_conduction=False
        self.heat_reaction='ignite'
        self.heat_conduction=0.14
        self.burn_temp=200
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=6
        self.identification_difficulty=7

class Cotton(BaseClasses.Material):
    #Cotton's material properties depend strongly on how it is woven. Tight weaves result in much higher youngs and shear moduli and higher density.
    #Maximal youngs modulus is about 7. Maximal density is about 820.
    def __init__(self,thickness=1,quality=1,weave=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.9,0.9,0.9,1)
        self.poisson=0.4
        self.weave=weave
        self.acid_resistance=6
        self.default_thickness=0.01
        self.basicname='fabric'
        self.name='cotton'
        self.maxquality=2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=820*weave/(weave+1)
        self.youngs=7*weave/(weave+10)#0.007
        self.fracture_energy=10*self.quality
        self.tensile_strength=400*self.quality*weave/(weave+5)
        self.mode='fabric'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=2.62*weave/(weave+20)#0.0023
        self.shear_strength=0.2*self.tensile_strength
        self.electric_conduction=False
        self.heat_reaction='ignite'
        self.heat_conduction=0.05
        self.burn_temp=400
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=7
        self.identification_difficulty=12

class Wool(BaseClasses.Material):
    #See note on Cotton. Much to do here in terms of weave
    def __init__(self,thickness=1,quality=1,weave=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.98,0.96,0.92,1)
        self.poisson=0.4
        self.weave=weave
        self.acid_resistance=10
        self.default_thickness=0.015
        self.basicname='fabric'
        self.name='wool'
        self.maxquality=2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=1310*weave/(weave+1)
        self.youngs=3.5*weave/(weave+10) #0.0007   #3.5 for fiber
        self.fracture_energy=30*self.quality
        self.tensile_strength=150*self.quality*weave/(weave+5)
        self.mode='fabric'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=1.31*weave/(weave+20) #0.00023   #1.31 for fiber
        self.shear_strength=0.2*self.tensile_strength
        self.electric_conduction=False
        self.heat_reaction='ignite'
        self.heat_conduction=0.07
        self.burn_temp=600
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=7
        self.identification_difficulty=12

class Hair_Material(Wool):
    def __init__(self,thickness=1,quality=1,weave=0.5,**kwargs):
        super().__init__(thickness,quality,weave=weave,**kwargs)
        self.basicname='hair'
        self.name='hair'
        self.acid_resistance=5
        self.density=400
        self.identification_difficulty=5

class Fur(Wool):
    def __init__(self,thickness=1,quality=1,weave=0.25,**kwargs):
        super().__init__(thickness,quality,weave=weave,**kwargs)
        self.basicname='hair'
        self.name='fur'
        self.acid_resistance=5
        self.density=300
        self.identification_difficulty=5

class Silk(BaseClasses.Material):
    #See note on Cotton. Much to do here in terms of weave
    def __init__(self,thickness=1,quality=1,weave=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.96,0.95,1,1)
        self.poisson=0.4
        self.weave=weave
        self.acid_resistance=9
        self.default_thickness=0.01
        self.basicname='fabric'
        self.name='silk'
        self.maxquality=1.2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=1310*weave/(weave+0.75)
        self.youngs=100*weave/(weave+5)#0.01  #100 for individual thread
        self.fracture_energy=60*self.quality
        self.tensile_strength=500*self.quality*weave/(weave+3)
        self.mode='fabric'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=3.81*weave/(weave+10)#0.0033  #3.81 for individual thread
        self.shear_strength=0.2*self.tensile_strength
        self.electric_conduction=False
        self.heat_reaction='burn'
        self.heat_conduction=0.1
        self.burn_temp=500
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=8
        self.identification_difficulty=17

class Spider_Silk(BaseClasses.Material):
    #See note on Cotton. Much to do here in terms of weave
    def __init__(self,thickness=1,quality=1,weave=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.96,0.95,1,1)
        self.poisson=0.4
        self.weave=weave
        self.acid_resistance=11
        self.default_thickness=0.01
        self.basicname='fabric'
        self.name='spider silk'
        self.maxquality=1.2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=1097*weave/(weave+0.75)
        self.youngs=12.7*weave/(weave+5)#0.0127  #12.7 for individual thread
        self.fracture_energy=160*self.quality
        self.tensile_strength=1300*self.quality*weave/(weave+3)
        self.mode='fabric'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=2.38*weave/(weave+10)#0.004  #2.38 for pure fiber
        self.shear_strength=0.2*self.tensile_strength
        self.electric_conduction=False
        self.heat_reaction='burn'
        self.heat_conduction=1
        self.burn_temp=900
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=9
        self.identification_difficulty=17

class Basalt_Fiber(BaseClasses.Material):
    #See note on Cotton. Much to do here in terms of weave
    def __init__(self,thickness=1,quality=1,weave=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.98,0.96,0.92,1)
        self.poisson=0.4
        self.weave=weave
        self.acid_resistance=13
        self.default_thickness=0.005
        self.basicname='fabric'
        self.name='basalt fiber'
        self.maxquality=1.2
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=2650*weave/(weave+1)
        self.youngs=100*weave/(weave+10)#0.01  #100 for individual thread
        self.fracture_energy=50*self.quality
        self.tensile_strength=4000*self.quality*weave/(weave+5)
        self.mode='fabric'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=33*weave/(weave+20)#0.0033
        self.shear_strength=0.2*self.tensile_strength
        self.electric_conduction=False
        self.heat_conduction=0.01
        self.burn_temp=1500
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=2
        self.identification_difficulty=18


class Demonic_Material(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,power=3,**kwargs):
        super().__init__(**kwargs)
        self.color=(random.random(),random.random(),random.random(),1)
        self.acid_reaction=random.choice(['embrittle','corrode'])
        self.wetdamage=random.choice(['rust',None,None])
        self.poisson=random.random()*0.49
        self.name='demonic'
        self.maxquality=random.random()*power
        self.quality=min(quality,self.maxquality)
        self.thickness=thickness
        self.density=abs(random.gauss(1,0.3*power/(5+power))*9000)+1
        self.youngs=abs(100*random.gauss(1,0.3*power/(5+power))**power)+0.00001
        self.fracture_energy=10*self.quality*random.triangular(0.001,10,mode=5*power/(power+5))
        self.tensile_strength=1
        for i in range(0,int(power)):self.tensile_strength+=random.gauss(0,power)**2
        moderandom=random.random()
        if moderandom<0.02:
            self.mode='soft'
            self.basicname=random.choice(['flesh','slime'])
        elif moderandom<0.4:
            self.mode='brittle'
            self.basicname=random.choice(['metal','metal','metal','bone','stone','wood','glass'])
        elif moderandom<0.7:
            self.mode='ductile'
            self.basicname='metal'
        else:
            self.mode='fabric'
            self.basicname=random.choice(['leather','fabric','fur'])
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=0.5*self.youngs/(1+self.poisson)
        self.shear_strength=1
        for i in range(0,int(power)):self.shear_strength+=random.gauss(0,power)**2
        self.shear_strength=0.6*self.shear_strength
        self.electric_conduction= random.random()>0.5
        self.heat_conduction=500/(1+random.gauss(0,power)**2)
        self.burn_temp=100*random.gauss(power**0.5,power/3)**2
        self.dissipationfactor=1
        self.maxedge=(5*10**-8)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=int(random.triangular(1,5+2*power,2*power))
        self.identification_difficulty=30
        self.default_thickness=random.random()/self.density**0.5

class Aether(BaseClasses.Material):
    def __init__(self,thickness=1,quality=1,power=3,**kwargs):
        super().__init__(**kwargs)
        self.color=(0,0.8,0.8,0.5)
        self.acid_reaction='corrode'
        self.wetdamage=None
        self.poisson=0.25
        self.name='aether'
        self.basicname='magical'
        self.maxquality=100
        self.quality=min(power,self.maxquality)
        self.thickness=thickness
        self.density=1
        self.youngs=1
        self.fracture_energy=5*power
        self.tensile_strength=1
        self.mode='brittle'
        self.fracture_toughness=(self.youngs*self.fracture_energy)**0.5
        self.shear=1
        self.shear_strength=1
        self.electric_conduction=True
        self.heat_conduction=500
        self.burn_temp=300*power
        self.dissipationfactor=1
        self.maxedge=(5*10**-8)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=10
        self.identification_difficulty=30
        self.default_thickness=0.004**power
######################################################################################################################


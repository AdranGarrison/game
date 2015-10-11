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
#Magic affinity runs from 1-10

##############################################MATERIALS###############################################################

class Bone_Material(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.8,0.8,0.8,1)
        self.poisson=0.31
        self.basicname='bone'
        self.name='bone'
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
        self.shear_strength=5*self.quality
        self.electric_conduction=True
        self.heat_conduction=True
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

class Flesh_Material(Material):
    def __init__(self,thickness=1,quality=1,**kwargs):
        super().__init__(**kwargs)
        self.color=(0.86,0.66,0.52,1)
        self.poisson=0.45
        self.acid_resistance=4
        self.fluid='blood'
        self.default_thickness=0.02
        self.basicname='flesh'
        self.name='flesh'
        self.maxquality=2
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
        self.electric_conduction=True
        self.heat_conduction=False
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

class Slime(Material):
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
        self.electric_conduction=True
        self.heat_conduction=False
        self.dissipationfactor=1.5
        self.maxedge=0.01
        self.damagetype=['bruise','cut','crush']
        self.magic_affinity=8
        self.identification_difficulty=5

class Iron(Material):
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
        self.heat_conduction=True
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

class Steel(Material):
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
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(5*10**-8)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=2
        self.identification_difficulty=15

class Copper(Material):
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
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(1.5*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=5
        self.identification_difficulty=12

class Bronze(Material):
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
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=6
        self.identification_difficulty=12

class Brass(Material):
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
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=4
        self.identification_difficulty=12

class Titanium(Material):
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
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(5*10^-7)/self.quality
        self.damagetype=['crack','break','shatter','crush','cut']
        self.magic_affinity=2
        self.identification_difficulty=17

class Silver(Material):
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
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(2*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=10
        self.identification_difficulty=17

class Aluminum(Material):
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
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(2*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=4
        self.identification_difficulty=16

class Duraluminum(Material):
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
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(1.5*10**-7)/self.quality
        self.damagetype=['dent','crush','bend','cut']
        self.magic_affinity=3
        self.identification_difficulty=18

class Zicral(Material):
    #Zinc Aluminum alloy
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
        self.heat_conduction=True
        self.dissipationfactor=1
        self.maxedge=(10**-7)/self.quality
        self.damagetype=['crack','break','shatter','crush','cut']
        self.magic_affinity=3.5
        self.identification_difficulty=19

class Wood(Material):
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
        self.heat_conduction=False
        self.dissipationfactor=1
        self.maxedge=(10**-4)/self.quality
        self.damagetype=['dent','crack','break','crush','cut']
        self.magic_affinity=7
        self.identification_difficulty=7



class Leather(Material):
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
        self.heat_conduction=False
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=6
        self.identification_difficulty=7

class Cotton(Material):
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
        self.heat_conduction=False
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=7
        self.identification_difficulty=12

class Wool(Material):
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
        self.heat_conduction=False
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

class Silk(Material):
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
        self.heat_conduction=False
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=8
        self.identification_difficulty=17

class Spider_Silk(Material):
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
        self.heat_conduction=False
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=9
        self.identification_difficulty=17

class Basalt_Fiber(Material):
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
        self.heat_conduction=False
        self.dissipationfactor=1
        self.maxedge=0.01
        self.damagetype=['pierce','cut']
        self.magic_affinity=2
        self.identification_difficulty=18
######################################################################################################################


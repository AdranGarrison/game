__author__ = 'Alan'


import kivy
from kivy.uix.widget import Widget




class Limb(Widget):
    def __init__(self,stats,natural=True,owner=None,*args,**kwargs):
        self.owner=owner
        self.stats=stats
        self.grasp=False
        self.support=False
        self.ability=1
        pass



    def youngscalc(self):
        sum=0
        i=len(self.layers)-1
        masssum=0
        ltotal=0
        limbmass=self.mass
        if self.armor is not None:
            sum+=self.armor.thickness/self.armor.material.youngs
            masssum+=self.armor.mass
            ltotal+=self.armor.thickness
            limbmass=self.mass+self.armor.mass
            print(self.armor,self.armor.mass,self.armor.thickness,self.armor.material.youngs)
        while i>=0:
            sum+=(self.layers[i].thickness/self.layers[i].material.youngs)*(1-masssum/limbmass)
            masssum+=self.layers[i].mass
            ltotal+=self.layers[i].thickness
            i-=1
        self.youngs=ltotal/sum
        self.thickness=ltotal

    def damageresolve(self,force,pressure,attacker):
        print('the {} is hit!'.format(self.name))
        i=len(self.layers)-1
        f=force
        pressure=pressure
        area=force/pressure
        mass=self.mass
        cut=False
        if self.armor is not None:
            pass
        while i>=0:
            #print(f)
            #Code cut from here in hopes of improving

            self.layers[i].damageresolve(self,f,pressure,attacker)

            if self.layers[i].material.mode=='soft':
                softnessfactor=0.3
            else:
                softnessfactor=1

            if cut==False:
                f-=softnessfactor*f*self.layers[i].mass/mass
                area=area+(3.54*self.layers[i].thickness*area**0.5)*self.layers[i].dissipationfactor/softnessfactor
                pressure=f/area
            i-=1


class Creature(Widget):
    pass

class Material():
    pass

class Item():
    pass
    def damageresolve(self,limb,force,pressure,attacker):
        self.olddamage=self.damage.copy()
        self.material.damageresolve(self,limb,force,pressure,attacker)


        #test for severing. If severed, then no other wounds need be processed
        if self.damage['cut']>self.olddamage['cut']:
            if self.plural==False:
                print("the {} is severed!".format(self.name))
            if self.plural==True:
                print("the {} are severed!".format(self.name))
            limb.cut=True
            self.function=0
            return

        #test for crushing. If crushed, no other wounds need be recognized
        if self.damage['crush']>self.olddamage['crush']:
            if self.plural==False:
                print("the {} is crushed!".format(self.name))
            if self.plural==True:
                print("the {} are crushed!".format(self.name))
            self.function=0
            return

        #Test for bruising.
        if self.damage['bruise']>self.olddamage['bruise']:
            if self.damage['bruise']<4:
                if self.plural==False:
                    print('the {} is bruised'.format(self.name))
                if self.plural==True:
                    print('the {} are bruised'.format(self.name))
            elif self.damage['bruise']<7:
                if self.plural==False:
                    print('the {} is badly bruised!'.format(self.name))
                if self.plural==True:
                    print('the {} are badly bruised!'.format(self.name))
            elif self.damage['bruise']<10:
                if self.plural==False:
                    print('the {} is severely bruised and swells with blood!'.format(self.name))
                if self.plural==True:
                    print('the {} are severely bruised and swell with blood!'.format(self.name))
            elif self.dmage['bruise']>=10:
                if self.plural==False:
                    print('the structure of the {} collapses under the impact!'.format(self.name))
                if self.plural==True:
                    print('the structure of the {} collapse under the impact!'.format(self.name))
                self.damage['crush']=1
            self.function-=self.damage['bruise']-self.olddamage['bruise']

        #Test for denting and bending


        #test for shattering. If shattered, cracks and breaks are irrelevant
        if self.damage['shatter']>self.olddamage['shatter']:
            if self.plural==False:
                print("the {} is shattered!".format(self.name))
            if self.plural==True:
                print("the {} are shattered!".format(self.name))
            self.function=0
            return
        elif self.damage['shatter']==1:
            return

        #test for breaking. If broken, further cracks are irrelevant
        if self.damage['break']>self.olddamage['break']:
            if self.plural==False:
                print("the {} is broken!".format(self.name))
            if self.plural==True:
                print("the {} are broken!".format(self.name))
            self.function=0
            return
        elif self.damage['break']==1:
            return

        #test for cracks and update function accordingly
        if self.damage['crack']>self.olddamage['crack'] and self.olddamage['crack']==0:
            if self.plural==False:
                print("the {} is cracked!".format(self.name))
            if self.plural==True:
                print("the {} are cracked!".format(self.name))
            self.function-=self.damage['crack']
            return
        elif self.damage['crack']>self.olddamage['crack']:
            if self.plural==False:
                print("the {} cracks further!".format(self.name))
            if self.plural==True:
                print("the {} crack further!".format(self.name))
            self.function-=self.damage['crack']-self.olddamage['crack']
            return

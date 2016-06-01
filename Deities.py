__author__ = 'Alan'

import BaseClasses
import random






#Lawful gods
class Istia(BaseClasses.Deity):
    def __init__(self):
        super().__init__()
        self.name="Istia, goddess of retaliation"
        self.alignment='L'
        self.acceptable_targets={}
        self.unacceptable_targets={}

    def add_follower(self,follower):
        super().add_follower(follower)
        self.acceptable_targets[follower]=[]
        self.unacceptable_targets[follower]=[]

    def invoke(self,power,**kwargs):
        super().invoke(power,**kwargs)
        chance=0
        if self.favor[power.caster]<0:
            self.favor[power.caster]-=1
            return False
        if power.targetcreature==power.caster and power.type in ('defensive','mixed'):
            chance+=0.75
        elif power.targetcreature in self.acceptable_targets[power.caster] and power.type in ('offensive','mixed'):
            chance+=1
        else:
            chance+=0.25
        if power.alignment=='L': chance*=1
        elif power.alignment=='N': chance*=0.6
        elif power.alignment=='C': chance*=0.25
        chance*=(power.caster.stats['luc']**0.5+self.favor[power.caster])
        if chance/(chance+power.difficulty)>random.random():
            rootluc=power.caster.stats['luc']**0.5
            self.favor[power.caster]-=int(power.difficulty*random.triangular(mode=rootluc/(rootluc+power.difficulty)))
            return True
        else:
            self.favor[power.caster]-=1
            return False

    def on_struck(self,follower,attack):
        super().on_struck(follower,attack)
        if attack.attacker not in self.unacceptable_targets[follower]: self.acceptable_targets[follower].append(attack.attacker)

    def on_strike(self,follower,attack):
        super().on_strike(follower,attack)
        if hasattr(attack.basetarget,'owner'):
            if attack.basetarget.owner in self.acceptable_targets[follower]:
                if follower.stats['luc']/(follower.stats['luc']+40)>random.random() and attack.damage_dealt>0: self.favor[attack.attacker]+=1
            elif attack.basetarget.owner not in self.unacceptable_targets[attack.attacker]:
                self.favor[attack.attacker]-=1
                self.unacceptable_targets[attack.attacker].append(attack.basetarget.owner)

    def on_avoid(self,follower,attack):
        super().on_struck(follower,attack)
        if attack.attacker not in self.unacceptable_targets[follower]: self.acceptable_targets[follower].append(attack.attacker)

    def on_kill(self,follower,creature):
        super().on_kill(follower,creature)
        if creature in self.acceptable_targets[follower]:
            self.acceptable_targets[follower].remove(creature)
        if creature in self.unacceptable_targets[follower]:
            self.favor[follower]-=1
            self.unacceptable_targets[follower].remove(creature)

class Cypselus(BaseClasses.Deity):
    def __init__(self):
        super().__init__()
        self.name="Cypselus, god of dominion"
        self.alignment='L'

    def invoke(self,power,**kwargs):
        super().invoke(power,**kwargs)
        chance=0
        if self.favor[power.caster]<0:
            self.favor[power.caster]-=1
            return False
        if power.targetcreature==power.caster and power.type in ('defensive','mixed'):
            chance+=0.5
        elif power.targetcreature!=power.caster and power.type in ('offensive','mixed'):
            chance+=1
        else:
            chance+=0.25
        if power.alignment=='L': chance*=1
        elif power.alignment=='N': chance*=0.5
        elif power.alignment=='C': chance*=0.2
        chance*=(power.caster.stats['luc']**0.5+self.favor[power.caster])
        if chance/(chance+power.difficulty)>random.random():
            rootluc=power.caster.stats['luc']**0.5
            self.favor[power.caster]-=int(power.difficulty*random.triangular(mode=rootluc/(rootluc+power.difficulty)))
            return True
        else:
            self.favor[power.caster]-=1
            return False

    def on_struck(self,follower,attack):
        luckfactor=(attack.attacker.stats['luc']*attack.damage_dealt)**0.5
        if luckfactor/(luckfactor+follower.stats['luc'])>random.random(): self.favor[follower]-=1

#TODO causes problems when triggering after death
    def on_strike(self,follower,attack):
        if hasattr(attack.basetarget,'owner'):
            luckfactor=follower.stats['luc']*attack.damage_dealt**0.5
            if luckfactor/(luckfactor+40)>random.random() and attack.damage_dealt>0: self.favor[attack.attacker]+=1

    def on_kill(self,follower,creature):
        super().on_kill(follower,creature)
        if creature in self.followers:
            self.favor[follower]+=1

#Neutral gods
class Kolomae(BaseClasses.Deity):
    def __init__(self):
        super().__init__()
        self.name="Kolonae, god of balance"
        self.alignment='N'
        self.prayers_answered={}

    def add_follower(self,follower):
        super().add_follower(follower)
        self.prayers_answered[follower]={'L':0,'C':0,'N':0}

    def invoke(self,power,**kwargs):
        super().invoke(power,**kwargs)
        chance=0.75
        if self.favor[power.caster]<0:
            self.favor[power.caster]-=1
            return False
        prayers=self.prayers_answered[power.caster]
        totalprayers=prayers['L']+prayers['N']+prayers['C']
        if totalprayers==0: totalprayers=1
        if power.alignment=='L': chance*=1.33-prayers['L']/totalprayers
        elif power.alignment=='N': chance*=1.33-prayers['N']/totalprayers
        elif power.alignment=='C': chance*=1.33-prayers['C']/totalprayers
        chance*=(power.caster.stats['luc']**0.5+self.favor[power.caster])
        if chance/(chance+power.difficulty)>random.random():
            rootluc=power.caster.stats['luc']**0.5
            self.favor[power.caster]-=int(power.difficulty*random.triangular(mode=rootluc/(rootluc+power.difficulty)))
            return True
        else:
            self.favor[power.caster]-=1
            return False

    def on_turn(self):
        super().on_turn()
        for i in self.followers:
            lnc=[0,0,0]
            for j in i.gods:
                if j.alignment=='C':
                    lnc[2]+=j.favor[i]
                elif j.alignment=='L':
                    lnc[0]+=j.favor[i]
                elif j.alignment=='N':
                    lnc[1]+=j.favor[i]
            avg=(lnc[0]+lnc[1]+lnc[2])/3
            if self.favor[i]<avg and i.stats['luc']/(i.stats['luc']+10)>random.random(): self.favor[i]+=1
            elif self.favor[i]>avg and 10/(i.stats['luc']+10)>random.random(): self.favor[i]-=1

class Medeina(BaseClasses.Deity):
    def __init__(self):
        super().__init__()
        self.name="Medeia, goddess of nature"
        self.alignment='N'
        self.contaminations={}

    def add_follower(self,follower):
        super().add_follower(follower)
        self.contaminations[follower]=follower.magic_contamination['total']

    def invoke(self,power,**kwargs):
        super().invoke(power,**kwargs)
        chance=1
        if self.favor[power.caster]<0:
            self.favor[power.caster]-=1
            return False
        if power.alignment=='L': chance*=0.5
        elif power.alignment=='N': chance*=1
        elif power.alignment=='C': chance*=0.5
        chance*=(power.caster.stats['luc']**0.5+self.favor[power.caster])
        if chance/(chance+power.difficulty)>random.random():
            rootluc=power.caster.stats['luc']**0.5
            self.favor[power.caster]-=int(power.difficulty*random.triangular(mode=rootluc/(rootluc+power.difficulty)))
            return True
        else:
            self.favor[power.caster]-=1
            return False

    def on_turn(self):
        super().on_turn()
        for i in self.followers:
            if (i.magic_contamination['total']-self.contaminations[i])/i.stats['luc']**2>random.random():
                self.favor[i]-=1
                self.contaminations[i]=i.magic_contamination['total']
            elif i.stats['luc']/max(self.contaminations[i],1)>random.random()*100*max(self.favor[i],1):
                self.favor[i]+=1

    def on_kill(self,follower,creature):
        super().on_kill(follower,creature)
        if 'magic' in creature.classification or 'unnatural' in creature.classification:
            self.favor[follower]+=1
        elif 'antimagic' in creature.classification:
            self.favor[follower]-=1

    def on_ability_use(self,follower,ability):
        if 'magic' in ability.classification:
            self.favor[follower]-=1
        elif 'antimagic' in ability.classification:
            self.favor[follower]+=1


#Chaotic gods
class Volos(BaseClasses.Deity):
    def __init__(self):
        super().__init__()
        self.name='Volos, god of death'
        self.alignment='C'

    def invoke(self,power,**kwargs):
        super().invoke(power,**kwargs)
        chance=0
        if self.favor[power.caster]<0:
            self.favor[power.caster]-=1
            return False
        if power.type=='defensive':
            chance+=0.25
        elif power.type=='mixed':
            chance+=0.5
        elif power.type=='offensive':
            chance+=1
        if power.alignment=='L': chance*=0.25
        elif power.alignment=='N': chance*=0.5
        elif power.alignment=='C': chance*=1
        chance*=(power.caster.stats['luc']**0.5+self.favor[power.caster])
        if chance/(chance+power.difficulty)>random.random():
            rootluc=power.caster.stats['luc']**0.5
            self.favor[power.caster]-=int(power.difficulty*random.triangular(mode=rootluc/(rootluc+power.difficulty)))
            return True
        else:
            self.favor[power.caster]-=1
            return False

    def on_turn(self):
        super().on_turn()
        for i in self.followers:
            if random.random()/(i.stats['luc']*i.stats['luc'])>random.random():
                self.favor[i]-=1

    def on_kill(self,follower,creature):
        super().on_kill(follower,creature)
        if 'living' in creature.classification:
            self.favor[follower]+=1

class Zaephex(BaseClasses.Deity):
    def __init__(self):
        super().__init__()
        self.name='Zaephex, god of chaos'
        self.alignment='C'

#TODO: Make interesting things happen on 'failure' when invoking chaos deity
    def invoke(self,power,**kwargs):
        super().invoke(power,**kwargs)
        chance=random.random()
        if self.favor[power.caster]<0:
            self.favor[power.caster]-=1
            return False
        if power.targetcreature==power.caster and power.type=='offensive':
            self.favor[power.caster]+=1
        elif power.targetcreature.hostilitycheck(power.caster) and power.type=='defensive':
            self.favor[power.caster]+=1
        if power.alignment=='L': chance*=random.random()*random.random()
        elif power.alignment=='N': chance*=random.random()
        elif power.alignment=='C': chance*=1
        chance*=(power.caster.stats['luc']**0.5+self.favor[power.caster])
        if chance/(chance+power.difficulty)>random.random():
            rootluc=power.caster.stats['luc']**0.5
            self.favor[power.caster]-=int(power.difficulty*random.triangular(mode=rootluc/(rootluc+power.difficulty)))
            return True
        else:
            self.favor[power.caster]-=1
            return False

    def on_turn(self):
        super().on_turn()
        for i in self.followers:
            if random.random()<0.01: self.favor[i]=0
            self.favor[i]+=random.choice([-1,0,1])

    def on_kill(self,follower,creature):
        super().on_kill(follower,creature)
        if 'law' in creature.classification:
            self.favor+=1

    def on_strike(self,follower,attack):
        if hasattr(attack.basetarget,'owner') and attack.basetarget.owner!=None:
            if not attack.basetarget.owner.hostilitycheck(follower):
                self.favor[follower]+=1



istia=Istia()
cypselus=Cypselus()
kolomae=Kolomae()
medeina=Medeina()
volos=Volos()
zaephex=Zaephex()

pantheon=[istia,cypselus,kolomae,medeina,volos,zaephex]
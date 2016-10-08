__author__ = 'Alan'

import BaseClasses
import random
import Shell
import Enchantments






#Lawful gods
class Istia(BaseClasses.Deity):
    def __init__(self):
        super().__init__()
        self.name="Istia, goddess of retaliation"
        self.alignment='L'
        self.acceptable_targets={}
        self.unacceptable_targets={}
        self.damage_suffered={}

    def add_follower(self,follower):
        super().add_follower(follower)
        self.acceptable_targets[follower]=[]
        self.unacceptable_targets[follower]=[]
        self.damage_suffered[follower]={}

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
        if attack.attacker not in self.unacceptable_targets[follower]:
            if attack.attacker not in self.acceptable_targets[follower]:
                self.acceptable_targets[follower].append(attack.attacker)
                self.damage_suffered[follower][attack.attacker]=0
            for i in attack.results:
                self.damage_suffered[follower][attack.attacker]+=i[1]

    def on_strike(self,follower,attack):
        super().on_strike(follower,attack)
        if hasattr(attack.basetarget,'owner') and attack.defender!=None:
            if attack.defender in self.acceptable_targets[follower]:
                if follower.stats['luc']/(follower.stats['luc']+40)>random.random() and attack.damage_dealt>0: self.favor[attack.attacker]+=1
            elif attack.defender not in self.unacceptable_targets[attack.attacker]:
                if attack.defender.hostilitycheck(follower,bidirectional=False):
                    self.favor[attack.attacker]-=1
                else:
                    self.favor[attack.attacker]-=5
                self.unacceptable_targets[attack.attacker].append(attack.basetarget.owner)

    def on_avoid(self,follower,attack):
        super().on_struck(follower,attack)
        if attack.attacker not in self.unacceptable_targets[follower]:
            if attack.attacker not in self.acceptable_targets[follower]: self.acceptable_targets[follower].append(attack.attacker)

    def on_kill(self,follower,creature):
        super().on_kill(follower,creature)
        try:
            if creature in self.acceptable_targets[follower]:
                self.acceptable_targets[follower].remove(creature)
                del self.damage_suffered[follower][creature]
            if creature in self.unacceptable_targets[follower]:
                self.favor[follower]-=1
                self.unacceptable_targets[follower].remove(creature)
        except KeyError:
            pass

    def smite_effects(self,follower,attack,prayer=None,**kwargs):
        super().smite_effects(follower,attack,prayer,**kwargs)
        if attack.basetarget.owner in self.acceptable_targets[follower]:
            power=((1+self.damage_suffered[follower][attack.basetarget.owner])*self.favor[follower]+self.smite_power)**0.5
            attack.damagefactor*=power
            attack.energy*=power
            attack.reaction_damage_factor=0
            attack.reaction_time_factor=0
            attack.blockable=0
            attack.parryable=0
            attack.dodgeable=0
        elif attack.attacker==Shell.shell.player:
            Shell.messages.append("Istia will not help you harm those who have done you no wrong!")


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
        luckfactor=(attack.attacker.stats['luc']*attack.damage_severity)**0.5
        if luckfactor/(luckfactor+follower.stats['luc'])>random.random(): self.favor[follower]-=1

#TODO causes problems when triggering after death
    def on_strike(self,follower,attack):
        if hasattr(attack.basetarget,'owner') and attack.basetarget.owner!=None and attack.basetarget.owner.alive:
            luckfactor=follower.stats['luc']*attack.damage_severity**0.5
            if luckfactor/(luckfactor+40)>random.random() and attack.damage_severity>0: self.favor[attack.attacker]+=1

    def on_kill(self,follower,creature):
        super().on_kill(follower,creature)
        if creature in self.followers:
            self.favor[follower]+=1

    def smite_effects(self,follower,attack,prayer=None,**kwargs):
        super().smite_effects(follower,attack,prayer,**kwargs)
        power=(self.favor[follower]+self.smite_power)**0.5
        attack.damagefactor*=power
        attack.energy*=power
        attack.reaction_damage_factor=0
        attack.reaction_time_factor=0
        attack.blockable=0
        attack.parryable=0
        attack.dodgeable=0
        try:
            if attack.basetarget.owner.feels_fear:
                attack.basetarget.owner.modify_fear(follower,random.randint(1,follower.stats['luc']))
                if attack.basetarget.owner==Shell.shell.player:
                    Shell.messages.append("You suddenly feel terrified of {}".format(follower.name))
                elif attack.basetarget.owner in Shell.shell.player.visible_creatures:
                    Shell.messages.append("{} looks terrified!".format(attack.basetarget.owner.name))
        except:
            pass


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

    def smite_effects(self,follower,attack,prayer=None,**kwargs):
        super().smite_effects(follower,attack,prayer,**kwargs)
        imbalance=0
        piety={'L':0,'N':0,'C':0}
        try:
            for i in attack.basetarget.owner.gods:
                piety[i.alignment]+=i.favor(attack.basetarget.owner)
            average_piety=(piety['L']+piety['N']+piety['C'])/3
            for i in ['L','N','C']:
                imbalance+=abs(average_piety-piety[i])
        except:
            pass
        power=(self.favor[follower]*(1+imbalance)+self.smite_power)**0.5
        attack.damagefactor*=power
        attack.energy*=power
        attack.reaction_damage_factor=0
        attack.reaction_time_factor=0
        attack.blockable=0
        attack.parryable=0
        attack.dodgeable=0
        #TODO: Need to implement smite effect for Kolomae. Some punishment for fanaticism? Madness (the removal of all sensible balance)? Blindness?

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
        if 'magic' in creature.classification:
            self.favor[follower]+=1
        if 'unnatural' in creature.classification:
            self.favor[follower]+=1
        if 'antimagic' in creature.classification:
            self.favor[follower]-=1

    def on_ability_use(self,follower,ability):
        if 'magic' in ability.classification:
            self.favor[follower]-=1
        elif 'antimagic' in ability.classification:
            self.favor[follower]+=1

    def smite_effects(self,follower,attack,prayer=None,**kwargs):
        super().smite_effects(follower,attack,prayer,**kwargs)
        magic=0
        try:
            magic=attack.basetarget.owner.magic_contamination['total']
        except:
            pass
        power=(self.favor[follower]*(1+magic)+self.smite_power)**0.5
        attack.damagefactor*=power
        attack.energy*=power
        attack.reaction_damage_factor=0
        attack.reaction_time_factor=0
        attack.blockable=0
        attack.parryable=0
        attack.dodgeable=0
        try:
            magic_to_remove=random.randint(0,min(int(magic),int(follower.stats['luc'])/2))
            if magic_to_remove>0:
                for i in range(0,magic_to_remove):
                    removed=False
                    magic_types=['dark','elemental','summoning','transmutation','arcane']
                    while removed==False:
                        type=random.choice(magic_types)
                        if attack.basetarget.owner.magic_contamination[type]>0:
                            attack.basetarget.owner.magic_contamination[type]-=1
                            removed=True
                enchantment=Enchantments.Silenced(attack.basetarget.owner,turns=magic_to_remove)
                enchantment.category='divine'
                if attack.basetarget.owner==Shell.shell.player:
                    Shell.messages.append("You feel magical energy drain from your body")
                elif attack.basetarget.owner in Shell.shell.player.visible_creatures:
                    Shell.messages.append("{}'s magic is drained".format(attack.basetarget.owner.name))
        except:
            pass



#Chaotic gods
class Volos(BaseClasses.Deity):
    def __init__(self):
        super().__init__()
        self.name='Volos, god of death'
        self.alignment='C'
        self.rot_attack=None

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

    def on_strike(self,follower,attack):
        super().on_strike(follower,attack)
        if self.rot_attack==attack:
            rot_occured=False
            for i in attack.damagedobjects:
                enchantment=Enchantments.Rot(i,self.favor[follower])
                enchantment.category='divine'
                enchantment.classification=["divine","negative","physical"]
                if enchantment in i.enchantments:
                    rot_occured=True
            self.rot_attack=None
            try:
                if rot_occured and attack.basetarget.owner in Shell.shell.player.visible_creatures:
                    Shell.messages.append("The {} begins to rot!".format(attack.basetarget.name))
            except:
                pass

    def on_kill(self,follower,creature):
        super().on_kill(follower,creature)
        if 'living' in creature.classification:
            self.favor[follower]+=1

    def smite_effects(self,follower,attack,prayer=None,**kwargs):
        super().smite_effects(follower,attack,prayer,**kwargs)
        power=(self.favor[follower]+self.smite_power)**0.5
        attack.damagefactor*=power
        attack.energy*=power
        attack.reaction_damage_factor=0
        attack.reaction_time_factor=0
        self.rot_attack=attack
        attack.blockable=0
        attack.parryable=0
        attack.dodgeable=0


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

#TODO: Needs to be a wide variety of smite effects for Zaephex
    def smite_effects(self,follower,attack,prayer=None,**kwargs):
        super().smite_effects(follower,attack,prayer,**kwargs)
        power=(self.favor[follower]+self.smite_power)**0.5
        attack.damagefactor*=power
        attack.energy*=power
        attack.reaction_damage_factor=0
        attack.reaction_time_factor=0
        attack.blockable=0
        attack.parryable=0
        attack.dodgeable=0
        if attack.defender!=None:
            for i in ['s','t','p','w','l']:
                if random.random()>0.9:
                    statmod=Enchantments.Creature_Stat_Modification(attack.defender,turns=int(random.random()*power),power=int(power*(0.3-random.random())),stat=i)
                    statmod.category='divine'
                    statmod.classification=['divine','negative']
            if random.random()>0.9:
                attack.defender.pain+=(power*power*power)*(random.random()-0.3)
            if random.random()>0.9:
                attack.defender.tension+=power*power*(random.random()-0.3)
            if random.random()>0.9:
                attack.defender.focus[0]=int(random.triangular(0,attack.defender.focus[1],attack.defender.focus[1]/power))
            if random.random()>0.9:
                attack.defender.stamina[0]=int(random.triangular(0,attack.defender.stamina[1],attack.defender.stamina[1]/power))



istia=Istia()
cypselus=Cypselus()
kolomae=Kolomae()
medeina=Medeina()
volos=Volos()
zaephex=Zaephex()

pantheon=[istia,cypselus,kolomae,medeina,volos,zaephex]
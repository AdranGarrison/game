__author__ = 'Alan'
import random




def dark_effect(target):
    severity=int(abs(random.gauss(1,1)*target.magic_contamination['total']/target.stats['wil']))
    dark_effects=[] #list of all possible dark effects, from least to greatest severity
    severity=max(severity,len(dark_effects)-1)
    possible_effects=dark_effects[0:severity]
    actual_effect=random.choice(possible_effects)
    actual_effect(target)

def elemental_effect(target):
    severity=int(abs(random.gauss(1,1)*target.magic_contamination['total']/target.stats['wil']))
    elemental_effects=[] #list of all possible dark effects, from least to greatest severity
    severity=max(severity,len(elemental_effects)-1)
    possible_effects=elemental_effects[0:severity]
    actual_effect=random.choice(possible_effects)
    actual_effect(target)

def summoning_effect(target):
    severity=int(abs(random.gauss(1,1)*target.magic_contamination['total']/target.stats['wil']))
    summoning_effects=[] #list of all possible dark effects, from least to greatest severity
    severity=max(severity,len(summoning_effects)-1)
    possible_effects=summoning_effects[0:severity]
    actual_effect=random.choice(possible_effects)
    actual_effect(target)

def transmutation_effect(target):
    severity=int(abs(random.gauss(1,1)*target.magic_contamination['total']/target.stats['wil']))
    transmutation_effects=[] #list of all possible dark effects, from least to greatest severity
    severity=max(severity,len(transmutation_effects)-1)
    possible_effects=transmutation_effects[0:severity]
    actual_effect=random.choice(possible_effects)
    actual_effect(target)

def arcane_effect(target):
    severity=int(abs(random.gauss(1,1)*target.magic_contamination['total']/target.stats['wil']))
    arcane_effects=[] #list of all possible dark effects, from least to greatest severity
    severity=max(severity,len(arcane_effects)-1)
    possible_effects=arcane_effects[0:severity]
    actual_effect=random.choice(possible_effects)
    actual_effect(target)
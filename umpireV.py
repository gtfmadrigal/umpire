import random
import sys

# set strings
round = 1
commandNumber = 1

# import data from gamefile

# create lists
hiddenUnits = []
hideTable = ["lightInfantry", "mediumInfantry", "heavyInfantry", "special", "engineer", "spy", "command", "lightArtillery", "mediumArtillery", "heavyArtillery", "attackSubmarine", "missileSubmarine", "stealthBomber", "recon", "transport", "drone"]
hideableTerrain = ["forest", "jungle", "swamp", "mountain"]
secrets = []
usedUnits = []

# create dictionaries
terrainTable = {}
attackTable = {"lightInfantry":4, "mediumInfantry":4, "heavyInfantry":6, "special":12, "engineer":4, "spy":4, "command":12, "lightArtillery":4, "mediumArtillery":4, "heavyArtillery":4, "lightCavalry":6, "mediumCavalry":8, "heavyCavalry":10, "amphibious":4, "patrol":4, "corvette":6, "destroyer":8, "carrier":12, "battleship":12, "cruiser":12, "heavyFighter":6, "attackSubmarine":0, "missileSubmarine":0, "lightFighter":4, "bomber":4, "stealthBomber":4, "transport":4, "recon":4, "drone":4}

# create effect dictionaries from gamefile
strengthTable = {}
speedTable = {}
precisionTable = {}
hasteTable = {}
industryTable = {}
regenerationTable = {}
resistanceTable = {}
nobilityTable = {}
visionTable = {}
silenceTable = {}
wisdomTable = {}
gallantryTable = {}

# Initialization
from foo import *
for x in hideableLocations: hideableTerrain.append(x)

# Meta-functions

def critical(attack, defense):
    global strengthTable
    global resistanceTable
    global gallantryTable
    modifier = gallantryTable.get(defense)
    base = random.randrange(1, 6)
    result = base + modifier
    if result <= 1:
        kill(defense)
        attackingStrength = strengthTable.get(attack)
        strengthTable[attack] = attackingStrength - 2
    if result == 2:
        print(defense, " is moved 0.5*max away from the battle.")
        move(defense)
        defendingStrength = strengthTable.get(defense)
        defendingResistance = resistanceTable.get(defense)
        defendingGallantry = gallantryTable.get(defense)
        strengthTable[defense] = defendingStrength - 4
        resistanceTable[defense] = defendingResistance - 4
        gallantryTable[defense] = defendingGallantry - 4
        attackingStrength = strengthTable.get(attack)
        strengthTable[attack] = attackingStrength - 1
    if result == 3:
        defendingStrength = strengthTable.get(defense)
        defendingResistance = resistanceTable.get(defense)
        defendingGallantry = gallantryTable.get(defense)
        strengthTable[defense] = defendingStrength - 3
        resistanceTable[defense] = defendingResistance - 3
        gallantryTable[defense] = defendingGallantry - 3
    if result == 4:
        defendingStrength = strengthTable.get(defense)
        defendingResistance = resistanceTable.get(defense)
        defendingGallantry = gallantryTable.get(defense)
        strengthTable[defense] = defendingStrength - 2
        resistanceTable[defense] = defendingResistance - 2
        gallantryTable[defense] = defendingGallantry - 2
    if result == 5:
        defendingStrength = strengthTable.get(defense)
        defendingResistance = resistanceTable.get(defense)
        defendingGallantry = gallantryTable.get(defense)
        strengthTable[defense] = defendingStrength - 1
        resistanceTable[defense] = defendingResistance - 1
        gallantryTable[defense] = defendingGallantry - 1
        attackingStrength = strengthTable.get(attack)
        attackingResistance = resistanceTable.get(attack)
        attackingGallantry = gallantryTable.get(attack)
        strengthTable[defense] = defendingStrength + 1
        resistanceTable[defense] = defendingResistance + 1
        gallantryTable[defense] = defendingGallantry + 1
    if result >= 6:
        defendingStrength = strengthTable.get(defense)
        defendingResistance = resistanceTable.get(defense)
        defendingGallantry = gallantryTable.get(defense)
        strengthTable[defense] = defendingStrength + 4
        resistanceTable[defense] = defendingResistance - 1
        gallantryTable[defense] = defendingGallantry + 3
        attackingStrength = strengthTable.get(attack)
        attackingResistance = resistanceTable.get(attack)
        attackingGallantry = gallantryTable.get(attack)
        strengthTable[defense] = defendingStrength + 2
        resistanceTable[defense] = defendingResistance + 2
        gallantryTable[defense] = defendingGallantry + 2

def kill(arguments):
    pass

def damage(unit, damage, teamTable):
    global firstTeamTable
    global secondTeamTable
    oldHealth = teamTable.get(unit)
    if oldHealth - damage <= 0: kill(unit)
    else:
        newHealth = oldHealth - damage
        teamTable[unit] = newHealth
        print(unit, " has health: ", newHealth)

# Umpire commands

def hide(arguments):
    global secrets
    global hiddenUnits
    if len(arguments) == 1: unit = arguments
    else: unit = arguments[1]
    try: unitType = unitTable.get(unit)
    except:
        print("Error parsing arguments in command hide().")
        return
    silence = silenceTable.get(unit)
    if silence <= -2:
        print(unit, " cannot hide, as its silence level is: ", silence)
        return
    if not unitType in hideTable:
        print(unit, " cannot hide, as its type is: ", unitType)
        return
    try: terrain = terrainTable.get(unit)
    except: terrain = "plains"
    if not terrain in hideableTerrain:
        print(unit, " cannot hide, as its location is: ", terrain)
    if unit in hiddenUnits:
        print(unit, "is already hidden at location: ", terrain)
    newSecret = unit + " is hidden at: " + terrain
    secrets.append(newSecret)
    hiddenUnits.append(unit)

def reveal(arguments):
    global hiddenUnits
    if len(arguments) == 1: unit = arguments
    else: unit = arguments[1]
    if not unit in hiddenUnits:
        print(unit, " is not hidden.")
        return
    hiddenUnits.remove[unit]
    print("Display ", unit, " on the board.")

# Theater-agnostic commands
    
def attack(arguments, teamTable, targetTeamTable):
    global hiddenUnits
    global usedUnits
    attackingUnits = []
    defendingUnits = []
    totalAttack = 0
    totalDefense = 0
    attackCritical = 0
    defenseCritical = 0
    # deal damage
    # reveal
    del arguments[0]
    for x in arguments:
        if x == ">": pass
        elif x in usedUnits: pass
        elif x in teamTable: 
            attackingUnits.append(x)
            if x in hiddenUnits: reveal(x)
        elif x in targetTeamTable: defendingUnits.append(x)
        else: print(x, " does not exist.")
    for x in attackingUnits:
        unitType = unitTable.get[x]
        max = attackTable.get[unitType]
        strength = strengthTable.get[x]
        base = random.randrange(1, max)
        total = base + strength
        if total >= max: attackCritical = True
        totalAttack = totalAttack + total
    for x in defendingUnits:
        unitType = unitTable.get[x]
        max = attackTable.get[unitType]
        resistance = resistanceTable.get[x]
        base = random.randrange(1, max)
        total = base + resistance
        if total <= 1: 
            total = 1
            defenseCritical = True
        totalDefense = totalDefense + total
    if totalDefense >= totalAttack:
        print("Attack repelled.")
        return
    netDamage = totalAttack - totalDefense
    if attackCritical > 0 and defenseCritical > 0:
        criticalUnits = min(attackCritical, defenseCritical)
        while criticalUnits > 0:
            attackCriticalUnit = (random.choice(attackingUnits))
            defenseCriticalUnit = (random.choice(defendingUnits))
            critical(attackCriticalUnit, defenseCriticalUnit)
            criticalUnits - 1
    perUnitDamage = netDamage / len(defendingUnits)
    for x in defendingUnits:
        damage(x, perUnitDamage, targetTeamTable)

def move(arguments):
    pass






            


# Army commands

# Naval commands

# Air commands

# Shell functions

# Shell
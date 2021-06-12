import random
from normandy import *

round = 1
usedUnits = []
immobileUnits = []
hiddenUnits = []
alreadyDropped = []
defendingUnits = []
disabledUnits = []
deadUnits = []
commandNumber = 1
secrets = ""
errorMessages = {"arguments":"Too many arguments for command. Type 'man' [command] for information.", "os":"Unknown operating system.", "bad":"Bad command. Type 'help' for assistance.", "team":"That unit belongs to the wrong team.", "available":"That unit is currently unavailable.", "function":"That function is unavailable to this unit.", "heading":"Unit cannot exceed its maximum heading change.", "dead":"Unit is dead.", "type":"No such unit type.", "unit":"No such unit.", "hidden":"Unit is already hidden.", "required":"Heading changes are not required for this unit.", "airborne":"Unit is not airborne."}
agnosticCommands = ["move", "hide", "reveal", "spy", "fire", "convert"]
navyCommands = ["heading", "torpedo", "sortie", "depthcharge"]
armyCommands = ["build", "missile"]
airCommands = ["takeoff", "land", "pulse", "airlift", "survey", "bomb", "kamikaze", "dogfight"]
umpireCommands = ["health", "kill", "freeze", "disable", "convert", "merge", "split"]
airPhase = True
helpTextBlock = """
Umpire commands: score, turn, details, quit, help, health, kill, freeze, convert, disable, merge, split, info
Theater-agnostic commands: attack, move, hide, reveal, spy, fire
Naval commands: heading, torpedo, sortie, depthcharge
Army commands: build, missile
Air commands: takeoff, land, pulse, airlift, survey, bomb, kamikaze, dogfight
"""
firstTeamFlying = []
secondTeamFlying = []
firstHealth = sum(firstTeamTable.values())
secondHealth = sum(secondTeamTable.values())

# Meta-functions
def update():
    global firstHealth
    global secondHealth
    global firstTeamTable
    global secondTeamTable
    firstHealth = sum(firstTeamTable.values())
    secondHealth = sum(secondTeamTable.values())

def changeList(unit, list, command):
    global usedUnits
    global immobileUnits
    global hiddenUnits
    global disabledUnits
    global alreadyDropped
    global defendingUnits
    global deadUnits
    global firstTeamFlying
    global secondTeamFlying
    if command == "append": list.append(unit)
    elif command == "clear": list.clear()
    elif command == "remove": list.remove(unit)

def evaluate(unit, unitType, table):
    if unit in immobileUnits or unit in usedUnits:
        print(errorMessages.get("available"))
        return
    if unit in deadUnits:
        print(errorMessages.get("dead"))
        return
    maximum = table.get(unitType) + 1
    return random.randrange(1, maximum)

def prompt(team, airShell, function, level):
    if level == "player": promptChar = "% "
    elif level == "umpire": promptChar = "# "
    if function == None: intermediate = " "
    else: intermediate = " " + str(function) + " "
    if airShell == True: shellPrompt = str(round) + " ~ " + str(commandNumber) + " " + str(team) + "-air" + intermediate + promptChar
    else: shellPrompt = str(round) + " ~ " + str(commandNumber) + " " + str(team) + intermediate + promptChar
    command = input(shellPrompt)
    return command

def modification():
    pass

def fog():
    pass

# One-word command functions
def score():
    update()
    firstPercent = firstHealth / firstHealthTotal * 100
    secondPercent = secondHealth / secondHealthTotal * 100
    print(firstTeam, "total health:", firstHealth, "or", firstPercent, "%")
    print(secondTeam, "total health:", secondHealth, "or", secondPercent, "%")

def turn():
    global round
    global airPhase
    score()
    changeList(True, usedUnits, "clear")
    changeList(True, immobileUnits, "clear")
    changeList(True, alreadyDropped, "clear")
    for x in disabledUnits: changeList(x, immobileUnits, "append")
    changeList(True, disabledUnits, "clear")
    round = round + 1
    airPhase = True

def details():
    print("Secrets:")
    print(secrets)
    print("Hidden units:")
    print(*hiddenUnits, sep = ", ")
    score()

def quitGame():
    areYouSure = input("Are you sure you want to quit? [Yes/no]: ")
    if areYouSure == "yes" or areYouSure == "y":
        score()
        quit()

def helpText():
    print("Commands: ")
    print(helpTextBlock)
    print("Unit types:")
    print(*allUnitTypes, sep = ", ")

def attack(team, targetTeam, targetTeamTable):
    global firstTeamTable
    global secondTeamTable
    attackPhase = True
    defensePhase = False
    willQuit = False
    totalAttackDamage = 0
    totalDefenseDamage = 0
    while attackPhase == True:
        command = prompt(team, False, "attack", "player")
        if command == "help": print("Enter a named unit to attack, 'defend' to change to the defense phase, or 'quit' to exit without saving.")
        elif command == "quit":
            attackPhase = False
            defensePhase = False
            willQuit = True
        elif command == "defend":
            attackPhase = False
            defensePhase = True
        elif command in unitTable:
            unitType = unitTable.get(command)
            attackDamage = evaluate(command, unitType, attackTable)
            if attackDamage == None: continue
            if command in hiddenUnits: reveal(command, unitType)
            totalAttackDamage = totalAttackDamage + attackDamage
            changeList(command, usedUnits, "append")
            if not command in moveFireTable: changeList(command, immobileUnits, "append")
            print("Damage dealt:", attackDamage)
            print("Total damage dealt:", totalAttackDamage)
        else: print(errorMessages.get("bad"))
    while defensePhase == True:
        command = prompt(targetTeam, False, "defend", "player")
        if command == "help": print("Enter a named unit to defend, 'save' to save changes to gamestate, or 'quit' to exit without saving.")
        elif command == "quit":
            defensePhase = False
            willQuit = True
        elif command == "save": defensePhase = False
        elif command in unitTable:
            unitType = unitTable.get(command)
            defenseDamage = evaluate(command, unitType, attackTable)
            if defenseDamage == None: continue
            if command in hiddenUnits: reveal(command, unitType)
            totalDefenseDamage = totalDefenseDamage + defenseDamage
            changeList(command, defendingUnits, "append")
            print("Defense dealt:", defenseDamage)
            print("Total defense dealt:", totalDefenseDamage)
            if totalDefenseDamage >= totalAttackDamage: defensePhase = False
        else: print(errorMessages.get("bad"))
    if willQuit == True: return
    if totalDefenseDamage >= totalAttackDamage:
        print("Attack repelled by", targetTeam)
        return
    netDamage = totalAttackDamage - totalDefenseDamage
    print("Net damage:", netDamage)
    perUnitDamage = netDamage / len(defendingUnits)
    print("Damage per unit:", perUnitDamage)
    for x in defendingUnits:
        oldHealth = targetTeamTable.get(x)
        if oldHealth - perUnitDamage <= 0: 
            newHealth = 0
            print(x, "killed.")
        else: 
            newHealth = oldHealth - perUnitDamage
            print(x, "new health:", newHealth)
        targetTeamTable[x] = newHealth
    changeList(True, defendingUnits, "clear")
    score()
    turn()

# Umpire functions
def health(unit):
    global firstTeamTable
    global secondTeamTable
    if unit in firstTeamTable: 
        relevantTeam = firstTeam
        relevantTable = firstTeamTable
    elif unit in secondTeamTable:
        relevantTeam = secondTeam
        relevantTable = secondTeamTable
    else:
        print(errorMessages.get("team"))
        return
    print("Current health: ", relevantTable.get(unit))
    newHealth = prompt(relevantTeam, False, "health", "umpire")
    if int(newHealth) <= 0: kill(unit, relevantTable)
    else: relevantTable[unit] = int(newHealth)
    update()

def kill(unit, teamTable):
    global firstTeamTable
    global secondTeamTable
    teamTable[unit] = 0
    changeList(unit, deadUnits, "append")
    update()

def freeze(unit):
    changeList(unit, immobileUnits, "append")

def convert(unit, unitType):
    global firstTeamTable
    global secondTeamTable
    global unitTable
    if unit in firstTeamTable:
        relevantTeam = firstTeam 
        relevantTable = firstTeamTable
    elif unit in secondTeamTable:
        relevantTeam = secondTeam
        relevantTable = secondTeamTable
    else:
        print(errorMessages.get("team"))
        return
    newUnitType = prompt(relevantTeam, False, "convert", "umpire")
    if not newUnitType in allUnitTypes:
        print(errorMessages.get("type"))
        return
    currentHealth = relevantTable.get(unit)
    maximumHealth = healthTable.get(newUnitType)
    if maximumHealth < currentHealth: newHealth = maximumHealth
    else: newHealth = currentHealth
    relevantTable[unit] = currentHealth
    unitTable[unit] = newUnitType
    if unit in hiddenUnits and not newUnitType in hideTable: reveal(unit, unitType)

def disable(unit):
    freeze(unit)
    changeList(unit, disabledUnits, "append")

def use(unit):
    changeList(unit, usedUnits, "append")

def merge():
    pass

def split():
    pass

# Theater-agnostic functions
def move(unit, unitType):
    if unit in immobileUnits:
        print(errorMessages.get("function"))
        return
    if unitType in headingTable: print(errorMessages.get("heading"))
    if not unitType in moveFireTable: use(unit)
    changeList(unit, immobileUnits, "append")

def hide(unit, unitType, team):
    global secrets
    if not unitType in hideTable:
        print(errorMessages.get("function"))
        return
    if unit in hiddenUnits:
        print(errorMessages.get("hidden"))
        return
    location = prompt(team, False, "hide", "player")
    newSecret = unit + " " + location
    secrets = secrets + ", " + newSecret
    changeList(unit, hiddenUnits, "append")

def reveal(unit, unitType):
    global secrets
    if not unit in hiddenUnits or not unitType in hideTable:
        print(errorMessages.get("function"))
        return
    changeList(unit, hiddenUnits, "remove")
    append = unit + "is no longer hidden."
    secrets = secrets + append

def spy(unit, unitType):
    if not unitType in spyTable:
        print(errorMessages.get("function"))
        return
    effectiveness = evaluate(unit, unitType, spyTable)
    if effectiveness == 6: print("Good information.")
    elif effectiveness == 1: print("Bad information.")
    elif effectiveness == None: return
    else: print("No information.")
    details()
    use(unit)

def fire(unit, unitType, team, targetTeamTable, version, table):
    global firstTeamTable
    global secondTeamTable
    defensePhase = True
    willQuit = False
    if not unitType in table:
        print(errorMessages.get("function"))
        return
    if unit in hiddenUnits: reveal(unit, unitType)
    while defensePhase == True:
        command = prompt(team, False, version, "player")
        if command == "help": print("Enter a named unit, 'save' to save changes to gamestate, or 'quit' to exit without saving.")
        elif command == "quit":
            defensePhase = False
            willQuit = True
        elif command == "save": defensePhase = False
        elif command in unitTable:
            try: changeList(command, defendingUnits, "append")
            except: pass
        else: print(errorMessages.get("bad"))
    if willQuit == True: return
    damage = evaluate(unit, unitType, table)
    print("Damage:", damage)
    perUnitDamage = damage / len(defendingUnits)
    print("Damage per unit:", perUnitDamage)
    for x in defendingUnits:
        oldHealth = targetTeamTable.get(x)
        if oldHealth - perUnitDamage < 0: 
            newHealth = 0
            print(x, "killed.")
        else: 
            newHealth = oldHealth - perUnitDamage
            print(x, "new health:", newHealth)
        targetTeamTable[x] = newHealth
    changeList(True, defendingUnits, "clear")
    score()

# Naval functions
def heading(unit, unitType):
    if evaluate(unit, unitType, headingTable) == 1:
        changeList(unit, immobileUnits, "append")
        if not unitType in moveFireTable: use(unit)
    else:
        print(errorMessages.get("required"))
        return

def torpedo(unit, unitType, team, targetTeamTable):
    global firstTeamTable
    global secondTeamTable
    if not unitType in torpedoTable:
        print(errorMessages.get("function"))
        return
    damage = evaluate(unit, unitType, torpedoTable)
    target = prompt(team, False, "torpedo", "player")
    if not target in targetTeamTable:
        print(errorMessages.get("team"))
    oldHealth = targetTeamTable.get(target)
    if damage == 6 or oldHealth - damage <= 0:
        print(target, "sunk.")
        kill(target, targetTeamTable)
    else:
        newHealth = oldHealth - damage
        print(target, "new health:", newHealth)
        targetTeamTable[target] = newHealth
    use(unit)
    changeList(unit, immobileUnits, "append")
    score()

def sortie(unit, unitType, team, targetTeamTable):
    global firstTeamTable
    global secondTeamTable
    if not unitType in sortieTable:
        print(errorMessages.get("function"))
        return
    attackDamage = evaluate(unit, unitType, sortieTable)
    if attackDamage == None:
        print(errorMessages.get("function"))
        return
    target = prompt(team, False, "sortie", "player")
    if not target in targetTeamTable:
        print(errorMessages.get("team"))
        return
    targetUnitType = unitTable.get(target)
    defenseDamage = evaluate(target, targetUnitType, sortieDefenseTable)
    if defenseDamage == None: defenseDamage = 0
    if defenseDamage <= attackDamage:
        netDamage = attackDamage - defenseDamage
        oldHealth = targetTeamTable[target]
        if oldHealth - netDamage < 0: kill(target, targetTeamTable)
        else: 
            newHealth = oldHealth - netDamage
            print(target, "new health:", newHealth)
            targetTeamTable[target] = newHealth
    else: print("Attack repelled by:", target)
    use(unit)
    changeList(unit, immobileUnits, "append")
    score()

def depthcharge(unit, unitType, team, targetTeamTable):
    if not unitType in depthchargeTable:
        print(errorMessages.get("function"))
        return
    if unit in alreadyDropped:
        print(errorMessages.get("available"))
        return
    target = prompt(team, False, "depthcharge", "player")
    effectiveness = evaluate(unit, unitType, depthchargeTable)
    if effectiveness == 6: 
        kill(target, targetTeamTable)
        print(target, "sunk.")
    elif effectiveness == 5:
        changeList(target, immobileUnits, "append")
        changeList(target, disabledUnits, "append")
        print(target, "frozen.")
    elif effectiveness == None: return
    else: print("Missed.")
    changeList(unit, immobileUnits, "append")
    changeList(unit, alreadyDropped, "append")
    score()

def board():
    pass

# Army functions
def build(unit, unitType):
    if not unitType in buildTable:
        print(errorMessages.get("function"))
        return
    fortification = evaluate(unit, unitType, buildTable)
    print("Fortification of strength", fortification, "built.")
    use(unit)
    changeList(unit, immobileUnits, "append")

def missile(unit, unitType, team, targetTeamTable):
    global firstTeamTable
    global secondTeamTable
    if not unitType in missileTable:
        print(errorMessages.get("function"))
        return
    if unit in hiddenUnits: reveal(unit, unitType)
    attackDamage = evaluate(unit, unitType, missileTable)
    if attackDamage == None: return
    command = prompt(team, False, "missile", "player")
    if command not in targetTeamTable:
        print(errorMessages.get("team"))
        return
    targetUnitType = unitTable.get(command)
    defenseDamage = evaluate(command, targetUnitType, missileDefenseTable)
    if defenseDamage == None: netDamage = attackDamage
    else: netDamage = attackDamage - defenseDamage
    currentHealth = targetTeamTable.get(command)
    if netDamage >= currentHealth: kill(command, targetTeamTable)
    elif netDamage >= 0:
        print("Missile repelled.")
        return
    else:
        newHealth = currentHealth - netDamage
        targetTeamTable[command] = newHealth
    changeList(unit, usedUnits, "append")
    if not unit in moveFireTable: changeList(unit, immobileUnits, "append")
    score()

# Air functions
def takeoff(unit, teamFlyingTable):
    if unit in teamFlyingTable:
        print("Already airborne.")
        return
    changeList(unit, teamFlyingTable, "append")

def land(unit, teamFlyingTable):
    changeList(unit, teamFlyingTable, "remove")
    use(unit)

def pulse(unit, unitType, team, targetTeamTable):
    effectiveness = evaluate(unit, unitType, pulseTable)
    if effectiveness == 6:
        print("Pulse effective.")
        pulsePhase = True
        pulsedUnits = []
    elif effectiveness == None: 
        print(errorMessages.get("function"))
        return
    else: 
        print("Pulse ineffective.")
        return
    while pulsePhase == True:
        command = prompt(team, False, "pulse", "player")
        if command in targetTeamTable: pulsedUnits.append(command)
        elif command == "help": print("Enter a unit that has been disabled, 'quit' to exit, or 'save' to exit and save.")
        elif command == "quit": return
        elif command == "save": 
            for x in pulsedUnits: disable(x)
            return
        else: print(errorMessages.get("unit"))
    use(unit)

def airlift(unit, unitType, team, teamTable):
    if not unitType in transportTable:
        print(errorMessages.get("function"))
        return
    liftedUnit = prompt(team, False, "airlift", "player")
    if not liftedUnit in teamTable:
        print(errorMessages.get("team"))
        return
    use(unit)

def kamikaze(unit, unitType, team, targetTeamTable):
    global firstTeamTable
    global secondTeamTable
    if not unitType in kamikazeTable:
        print(errorMessages.get("function"))
        return
    target = prompt(team, False, "kamikaze", "player")
    if not target in targetTeamTable:
        print(errorMessages.get("team"))
        return
    effectiveness = evaluate(unit, unitType, kamikazeTable)
    oldHealth = targetTeamTable.get(target)
    if effectiveness == 6 or oldHealth - effectiveness <= 0:
        print(target, "killed.")
        kill(target, targetTeamTable)
    else:
        newHealth = oldHealth - effectiveness
        print(target, "new health:", newHealth)
        targetTeamTable[target] = newHealth
    kill(unit, teamTable)

# Shell
def info(unit, unitType):
    if not unit in unitTable:
        print(errorMessages.get("team"))
        return
    print("Unit type:", unitTable.get(unit))
    print("Maximum health:", healthTable.get(unitType))
    if unit in firstTeamTable: 
        owner = firstTeam
        print("Current health:", firstTeamTable.get(unit))
        print("Owner:", firstTeam)
    else:
        owner = secondTeam
        print("Current health:", secondTeamTable.get(unit))
        print("Owner:", secondTeam)
    print("Movement:", movementTable.get(unitType))
    print("Attack:", attackTable.get(unitType))
    print("Build:", buildTable.get(unitType))
    print("Sortie:", sortieTable.get(unitType))
    print("Sortie defense:", sortieDefenseTable.get(unitType))
    print("Depth charge:", depthchargeTable.get(unitType))
    if unitType in spyTable: print("Can search.")
    if unitType in hideTable: print("Can hide.")
    if unitType in moveFireTable: print("Can move and fire in the same turn.")
    if unitType in torpedoTable: print("Can fire torpedoes.")
    if unitType in headingTable: print("Heading change required.")
    if unit in immobileUnits: print("Immovable this turn.")
    if unit in usedUnits: print("Unusable this turn.")
    if unit in hiddenUnits: print("Hidden.")

def umpireShell(command, unit, unitType):
    if command == "health": health(unit)
    elif command == "kill":
        if unit in firstTeamTable: teamTable = firstTeamTable
        else: teamTable = secondTeamTable
        kill(unit, teamTable)
    elif command == "freeze": freeze(unit)
    elif command == "disable": disable()
    elif command == "convert": convert(unit, unitType)
    elif command == "merge": merge()
    elif command == "split": split()

def airShell(team, targetTeam, teamTable, targetTeamTable, teamFlyingTable, targetTeamFlyingTable):
    global commandNumber
    global airPhase
    rawCommand = prompt(team, True, None, "player")
    if len(rawCommand.split()) == 2:
        command, unit = rawCommand.split()
        unitType = unitTable.get(unit)
        if not unit in unitTable:
            print(errorMessages.get("unit"))
            return
        if unit in deadUnits and not command == "health":
            print(errorMessages.get("dead"))
            return
        if not unitType in flyTable:
            print(errorMessages.get("function"))
            return
        if command in umpireCommands: umpireShell(command, unit, unitType)
        elif command in airCommands:
            if not unit in teamTable:
                print(errorMessages.get("team"))
                return
            if unit in deadUnits:
                print(errorMessages.get("dead"))
                return
            if unit in usedUnits:
                print(errorMessages.get("available"))
                return
            if not unit in teamFlyingTable and not command == "takeoff":
                print(errorMessages.get("airborne"))
                return
            if command == "takeoff": takeoff(unit, teamFlyingTable)
            elif command == "land": land(unit, teamFlyingTable)
            elif command == "pulse": pulse(unit, unitType, team, targetTeamTable)
            elif command == "airlift": airlift(unit, unitType, team, teamTable)
            elif command == "survey":spy(unit, unitType)
            elif command == "bomb": fire(unit, unitType, team, targetTeamTable, "bomb", bombTable)
            elif command == "missile": missile(unit, unitType, team, targetTeamTable)
            elif command == "kamikaze": kamikaze(unit, unitType, team, teamTable, targetTeamTable)
        else: print(errorMessages.get("bad"))
    elif len(rawCommand.split()) == 1:
        if rawCommand == "dogfight": pass
        elif rawCommand == "next":
            airPhase = False
            return
        elif rawCommand == "score": score()
        elif rawCommand == "help": helpText()
        elif rawCommand == "details": details()
        elif rawCommand == "quit": quitGame()
        else: 
            print(errorMessages.get("bad"))
            return
    else: 
        print(errorMessages.get("bad"))
        return
    commandNumber = commandNumber + 1
    airShell(team, targetTeam, teamTable, targetTeamTable, teamFlyingTable, targetTeamFlyingTable)

def shell(team, targetTeam, teamTable, targetTeamTable, teamFlyingTable, targetTeamFlyingTable):
    global airPhase
    global commandNumber
    if airPhase == True and airTheater == True: 
        airShell(team, targetTeam, teamTable, targetTeamTable, teamFlyingTable, targetTeamFlyingTable)
        return
    rawCommand = prompt(team, False, None, "player")
    if len(rawCommand.split()) == 2:
        command, unit = rawCommand.split()
        if not unit in unitTable:
            print(errorMessages.get("unit"))
            return
        unitType = unitTable.get(unit)
        if command in umpireCommands: umpireShell(command, unit, unitType)
        elif command in navyCommands or command in armyCommands or command in agnosticCommands:
            if not unit in teamTable:
                print(errorMessages.get("team"))
                return
            if unit in deadUnits:
                print(errorMessages.get("dead"))
                return
            if unit in usedUnits:
                print(errorMessages.get("available"))
                return
            if command == "heading": heading(unit, unitType)
            elif command == "torpedo": torpedo(unit, unitType, team, targetTeamTable)
            elif command == "sortie": sortie(unit, unitType, team, targetTeamTable)
            elif command == "depthcharge": depthcharge(unit, unitType, team, targetTeamTable)
            elif command == "build": build(unit, unitType)
            elif command == "missile": missile(unit, unitType, team, targetTeamTable)
            elif command == "move": move(unit, unitType)
            elif command == "hide": hide(unit, unitType, team)
            elif command == "info": info(unit, unitType)
            elif command == "reveal": reveal(unit, unitType)
            elif command == "spy": spy(unit, unitType)
            elif command == "fire": fire(unit, unitType, team, targetTeamTable, "fire", fireTable)
            elif command == "board": pass
            else:
                print(errorMessages.get("bad"))
                return
    elif len(rawCommand.split()) == 1:
        if rawCommand == "attack": attack(team, targetTeam, targetTeamTable)
        elif rawCommand == "score": score()
        elif rawCommand == "turn": turn()
        elif rawCommand == "quit": quitGame()
        elif rawCommand == "help": helpText()
        elif rawCommand == "details": details()
        else: print(errorMessages.get("bad"))
    else: 
        print(errorMessages.get("bad"))
        return
    commandNumber = commandNumber + 1

while True:
    while (round % 2) != 0: shell(firstTeam, secondTeam, firstTeamTable, secondTeamTable, firstTeamFlying, secondTeamFlying)
    while (round % 2) == 0: shell(secondTeam, firstTeam, secondTeamTable, firstTeamTable, secondTeamFlying, firstTeamFlying)
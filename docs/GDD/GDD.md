# GDD Module: Base Rules [GDD.CORE]

Fundamental mechanics governing character attributes and the passage of time in combat.

---

## Attributes [GDD.CORE.ATTR]
**Físico (FIS) [GDD.CORE.ATTR.FIS]:** Strength and Resistance. Defines Max Hit Points(PV).
**Habilidade (HAB) [GDD.CORE.ATTR.HAB]:** Agility and Precision. Defines Base Action Cost.
**Mente (MEN) [GDD.CORE.ATTR.MEN]:** Focus and Spirit. Defines Max Mana and Focus/Mana generation.

---

## The Time Engine [GDD.CORE.TIME]
[DEPENDS: GDD.CORE.PROG.HAB]
Combat uses a continuous flow of "Ticks" instead of rounds.

---

### Action Types [GDD.CORE.TIME.ACTION.TYPES]
[DEPENDS: GDD.CORE.PROG.HAB]
**Standard Action:** Used for attack actions, skill use, abilities, and spells. The cost of the action is determined by HAB progression table.
**Movement action:** Used for moving, using items, and quick actions. The cost of the action is equal to half the cost of a standard action.

---

### Initiative, Scheduling and Turn Order [GDD.CORE.TIME.FLOW]
[DEPENDS: GDD.CORE.TIME.ACTION.TYPES]
**Initiative [GDD.CORE.TIME.INIT]:** Characters start with a tick counter equal to their Action Cost. Lowest counter acts first. 
**Scheduling [GDD.CORE.TIME.SCHE]:** After an action, add the action cost to the character's tick counter depending on the action type. The character with the lowest counter acts next.
**Draw Resolution [GDD.CORE.TIME.DRAW]:** If two characters have the same tick counter value, the one with the higher HAB value acts first. If the HAB values ​​are equal, the tie must be resolved with a d10 die; the higher value wins. If the die values ​​are tied, roll again.

---

## Attribute Scale [GDD.CORE.SCALE]
| Value | Scale | Description |
| :--- | :--- | :--- |
| 0 | Very Weak | Below human level. |
| 2-3 | Common | Average human. |
| 4-6 | Heroic | Peak human / Adventurer. |
| 7-9 | Legendary | Near sonic speeds, town-level magic. |
| 10-12 | Epic | Semi-god level. |
| 13-15 | Divine | Reality warping, light speed. |

---

## Progression Tables [GDD.CORE.PROG]
[DEPENDS: GDD.CORE.ATTR]
Attributes progression tables.

---

### Físico (PV) [GDD.CORE.PROG.FIS]
[DEPENDS: GDD.CORE.ATTR.FIS]
| Físico | PV |
| ---: | ---: |
| 0 | 10 |
| 1 | 20 |
| 2 | 30 |
| 3 | 40 |
| 4 | 50 |
| 5 | 65 |
| 6 | 80 |
| 7 | 95 |
| 8 | 115 |
| 9 | 135 |
| 10 | 155 |
| 11 | 180 |
| 12 | 205 |
| 13 | 230 |
| 14 | 270 |
| 15 | 310 |

---

### Habilidade (Action Cost) [GDD.CORE.PROG.HAB]
[DEPENDS: GDD.CORE.ATTR.HAB]
| Habilidade | Action Cost |
| ---: | ---: |
| 0 | 60 |
| 1 | 50 |
| 2 | 40 |
| 3 | 36 |
| 4 | 32 |
| 5 | 28 |
| 6 | 25 |
| 7 | 22 |
| 8 | 20 |
| 9 | 18 |
| 10 | 16 |
| 11 | 14 |
| 12 | 13 |
| 13 | 12 |
| 14 | 11 |
| 15 | 10 |

---

### Mente (Mana) [GDD.CORE.PROG.MEN]
[DEPENDS: GDD.CORE.ATTR.MEN]
| Mente | Mana |
| ---: | ---: |
| 0 | 0 |
| 1 | 10 |
| 2 | 40 |
| 3 | 60 |
| 4 | 70 |
| 5 | 80 |
| 6 | 100 |
| 7 | 120 |
| 8 | 140 |
| 9 | 160 |
| 10 | 180 |
| 11 | 200 |
| 12 | 220 |
| 13 | 240 |
| 14 | 260 |
| 15 | 300 |

---

# GDD Module: Combat Resolution [GDD.COMBAT]

This module defines how attacks are resolved, damage is calculated, and equipment tiers are scaled.

---

## Attack Resolution [GDD.COMBAT.FLOW]
[DEPENDS: GDD.STYLES.DEFINITION]
**Rank Bonus [GDD.COMBAT.FLOW.RANK]:** Bonus defined by character level.
**Attack Dice [GDD.COMBAT.FLOW.DA]:** Dice used for attack rolls, defined by character combat style.
**Defense Dice [GDD.COMBAT.FLOW.DD]:** Dice used for defense rolls, defined by character combat style.
**Advantage [GDD.COMBAT.FLOW.ADV]:** Rolling with advantage means rolling two dice and choosing higher value.
**Disavantage [GDD.COMBAT.FLOW.DSV]:** Rolling with disadvantage means rolling two dice and choosing lower value.
**Attack Bonus (BDA) [GDD.COMBAT.FLOW.BDA]:** Attack bonus given by abilities and itens.
**Defense Bonus (BDD) [GDD.COMBAT.FLOW.BDD]:** Defense bonus given by abilities and itens.
**Attack Roll [GDD.COMBAT.FLOW.ATTACKROLL]:** Rank Bonus + Attack Dice + Attack Bonus(BDA)
**Defense Roll [GDD.COMBAT.FLOW.DEFENSEROLL]:** Rank Bonus + Defense Dice + Defense Bonus(BDD)
**Hit Grade (GdA) [GDD.COMBAT.FLOW.GDA]:** `Attack - Defense`. Represents how hard the hit was. Used in damage calculation.
**Precision (PRE) [GDD.COMBAT.FLOW.PRE]:** Allows hitting even if GdA is negative. GdA is treated as 0 for damage.
**Guard (GRD) [GDD.COMBAT.FLOW.GRD]:** Causes a hit to miss even if GdA is positive.
**Hit Formula [GDD.COMBAT.FLOW.HIT]:** GdA + Pre - Grd. If result > 0 attack hits, else attack miss.

---

## Damage Calculation [GDD.COMBAT.DAMAGE]
[DEPENDS: GDD.COMBAT.FLOW, GDD.EQUIP.TIERS.WEAPONS, GDD.STYLES.DEFINITION]
**Attack Power (PdA) [GDD.COMBAT.DAMAGE.PDA]:** Weapon Base Damage(DB) + Primary Attribute
**Attack Multiplier (MdA) [GDD.COMBAT.DAMAGE.MDA]:** Multiplies GdA in damage formula. Defined by weapon (Default: 1)
**Damage Formula [GDD.COMBAT.DAMAGE.FORMULA]:** `PdA + (GdA * MdA)`

---

# GDD Module: Equipments [GDD.EQUIP]
Informations about equipments in the game like types, progression table by tiers and effects table

---

## Equipment Types [GDD.EQUIP.TYPES]

### Weapon Types[GDD.EQUIP.TYPES.WEAPONS]
**Great Weapon [GDD.EQUIP.TYPES.WEAPONS.GREAT]:** Massive, heavy-impact weapons requiring two hands. Includes Greatswords, Greataxes, and Warhammers.
**Medium Weapon [GDD.EQUIP.TYPES.WEAPONS.MEDIUM]:** Versatile, balanced weapons usable with one or both hands. Includes Swords, Axes, Maces, and Spears.
**Light Weapon [GDD.EQUIP.TYPES.WEAPONS.LIGHT]:** Precision and and agile weapons like daggers, short swords,dueling blades and rapiers.
**Double Weapon [GDD.EQUIP.TYPES.WEAPONS.DOUBLE]:** Paired or twin-headed weapons, such as Twin-Blades or Dual Daggers. For two weapon fighting combat tyles, a pair of weapons is treated as one equipment.
**Weapon & Shield [GDD.EQUIP.TYPES.WEAPONS.W&S]:** Weapon & shield set to be equiped together. The weapon can be any light or medium weapon. The set is treated as one equipment.
**Ranged Weapons [GDD.EQUIP.TYPES.WEAPONS.RANGED]:** Projectile-based weapons. Includes Bows, Crossbows, and Firearms.
**Magical Focus [GDD.EQUIP.TYPES.WEAPONS.MAGICAL]:**
Objects used as arcane focus, such as Staves, Orbs, or Grimoires.

---

## Equipment Tiers [GDD.EQUIP.TIERS]

---

### Weapons [GDD.EQUIP.TIERS.WEAPONS]

| Tier | Base Damage (DB) | Multiplier (MdA) |
| :---: | :---: | :---: |
| **1** | 3 | 1 |
| **2** | 5 | 1 |
| **3** | 7 | 2 |
| **4** | 10 | 2 |
| **5** | 15 | 3 |

---

### Armors [GDD.EQUIP.TIERS.ARMOR]

| Tier | Cloak | Light | Heavy |
| :---: | :---: | :---: | :---: |
| **1** | 10 | 15 | 25 |
| **2** | 15 | 25 | 40 |
| **3** | 25 | 45 | 70 |
| **4** | 35 | 70 | 110 |
| **5** | 55 | 110 | 160 |

---

# GDD Module: Combat Styles [GDD.STYLES]

## Introduction [GDD.STYLES.DEFINITION]
The combat style represents how the character fights, what equipment they use, and what combat skills they possess. Combat styles define the attack die, defense die, weapon and armor type the character can use, and their main attribute, used in damage calculation.

---

## Destruidor [GDD.STYLES.DESTRUIDOR]
[DEPENDS: GDD.CORE.ATTR, GDD.COMBAT, GDD.STATUS.ATORDOADO]

**Attribute:** FIS
**Attack:** d12
**Defense:** d8
**Armor Type:** HEAVY
**Weapon Type:** GREAT_WEAPON

### Abilities:
**Força Bruta [GDD.STYLES.DESTRUIDOR.FORCA_BRUTA]:** Successful hits have their GdA doubled. Applied before Skill bonus, rounded down.
**Mãos Pesadas [GDD.STYLES.DESTRUIDOR.MAOS_PESADAS]:** If GdA > 3 with a GREAT_WEAPON, the target is ATORDOADO.
**Alcance [GDD.STYLES.DESTRUIDOR.ALCANCE]:** While using a GREAT_WEAPON, spend 2 Focus to attack all targets in melee range. [AttackType = AREA]
**Postura Defensiva [GDD.STYLES.DESTRUIDOR.POSTURA_DEFENSIVA]:** Switch dice to d10/d10. Alcance cost reduced to 1 Focus. Hits apply a -1 Precision penalty to the target's next action against you.

---

## Defensor [GDD.STYLES.DEFENSOR]
[DEPENDS: GDD.CORE.ATTR, GDD.COMBAT.FLOW, GDD.STATUS.ATORDOADO]

**Attribute:** FIS
**Attack:** d8
**Defense:** d12
**Armor Type:** HEAVY
**Weapon Type:** WEAPON_AND_SHIELD

### Abilities:
**Bloquear [GDD.STYLES.DEFENSOR.BLOQUEAR]:** While shielding, spend 2 Focus to add 1d4 to defense. If defense > attacker's roll and GdA < -3, gain +1 Attack against that opponent.
**Golpe de Escudo [GDD.STYLES.DEFENSOR.GOLPE_ESCUDO]:** Spend 2 Focus to attack using defense die. Damage halved, GdA treated as 0. If GdA > 3, target is ATORDOADO.
**Pressionar [GDD.STYLES.DEFENSOR.PRESSIONAR]:** Spend 2 Focus to gain advantage on menace tests. Every time you succeed in a menace test you gain advantage to attack that target in your next action.
**Proteger [GDD.STYLES.DEFENSOR.PROTEGER]:** Spend 2 Focus to redirect a melee attack from an adjacent ally to yourself. Does not work against SKILL or MAGIC.

---

## Duelista [GDD.STYLES.DUELISTA]
[DEPENDS: GDD.CORE.ATTR, GDD.STATUS.DESEQUILIBRADO, GDD.COMBAT.FLOW]

**Attribute:** HAB
**Attack:** d8
**Defense:** d10
**Armor Type:** LIGHT
**Weapon Type:** LIGHT_WEAPON

### Abilities:
**Graça do Duelista [GDD.STYLES.DUELISTA.GRACA]:** On hit, add 1d6 to GdA. When targeted, can spend 2 Focus to add 1d4 to defense.
**Golpe Baixo [GDD.STYLES.DUELISTA.GOLPE_BAIXO]:** Spend 2 Focus to force a HAB contest against a melee target. Success: target is DESEQUILIBRADO and Golpe Baixo costs a Movement Action. Failure: Golpe Baixo costs a Standard Action.
**Contra Ataque [GDD.STYLES.DUELISTA.CONTRA_ATAQUE]:** If GdA < 0, spend 2 Focus to counter-attack.
**Pés Ligeiros [GDD.STYLES.DUELISTA.PES_LIGEIROS]:** Spend 2 Focus during movement for +50% distance bonus or advantage on disengage tests. Melee hits gives the target -1 Precision against you on their next action.

---

## Mestre das Armas [GDD.STYLES.MESTRE_ARMAS]
[DEPENDS: GDD.CORE.ATTR, GDD.COMBAT.FLOW]

**Attribute:** FIS
**Attack:** d10
**Defense:** d10
**Armor Type:** HEAVY
**Weapon Type:** MEDIUM_WEAPON

### Abilities:
**Postura de Batalha [GDD.STYLES.MESTRE_ARMAS.POSTURAS]:** Choose at start of turn: **Offensive**:-1 Guard / +1 Precision and +2 GdA. Bonus doubles if attack die > 7; **Defensive**: -1 Precision / +1 Guard. Spend 2 Focus to re-roll defense (must keep new result).
**Ataque Concentrado [GDD.STYLES.MESTRE_ARMAS.CONCENTRADO]:** Spend movement action to prepare. Grants you advantage in attacks on your next action against one target. If in Defensive posture, switch to Offensive before attacking. Grants opportunity attack if target leaves range.
**Ataque Desarmante [GDD.STYLES.MESTRE_ARMAS.DESARMANTE]:** Spend 2 Focus. On hit, target has disadvantage on their next action. GdA treated as 0 for damage.
**Dança da Batalha [GDD.STYLES.MESTRE_ARMAS.VITAIS]:** Spend 2 Focus to gain +50% movement or gain advnatage in menace tests. Every time you roll a 10 to attack, this attack counts as a movement action.

---

## Retalhador [GDD.STYLES.RETALHADOR]
[DEPENDS: GDD.CORE.ATTR, GDD.COMBAT.FLOW]

**Attribute:** HAB
**Attack:** d10
**Defense:** d8
**Armor Type:** LIGHT
**Weapon Type:** SWORD (ANY)

### Abilities:
**Ritmo Acelerado [GDD.STYLES.RETALHADOR.RITMO_ACELERADO]:** Every time you roll 7 or more in attack, that attack counts as a movement action. This can happen 2 times in a roll. If that happens, the third attack is a standard action gain +2 PRE.
**Ritmo Crescente [GDD.STYLES.RETALHADOR.RITMO_CRESCENTE]:** +1 PRE on hit (max +2). Reset on miss.
**Pressionar [GDD.STYLES.RETALHADOR.PRESSIONAR]:** Spend 2 Focus to gain advantage on menace tests. Success grants advantage on attack against that target on your next action. Every time you hit a target, that target gains (TO BE DONE)
**Barreira de Lâminas [GDD.STYLES.RETALHADOR.BARREIRA]:** Attacks apply Precision penalty to target against you. Penalty doubles on hit.

---

## Lutador [GDD.STYLES.LUTADOR]
[DEPENDS: GDD.CORE.ATTR, GDD.COMBAT.FLOW, GDD.STATUS.ATORDOADO, GDD.STATUS.DERRUBADO]

**Attribute:** FIS
**Attack:** d10
**Defense:** d10
**Armor:** Light
**Weapons:** Gloves/Unarmed

### Abilities:
**Combo [GDD.STYLES.LUTADOR.COMBO]:** Attack action allows two attacks. If both hit, perform a third attack that Stuns.
**Investida [GDD.STYLES.LUTADOR.INVESTIDA]:** Spend 2 Focus and Attack Action to move up to speed in straight line and attack with +2 GdA.
**Balão [GDD.STYLES.LUTADOR.BALAO]:** Replace attack with grapple roll. On hit, FIS contest to throw. Target is Knocked Down and takes PdA damage.
**Evasão [GDD.STYLES.LUTADOR.EVASAO]:** Spend 2 Focus to add 1d4 to defense when targeted.

---

## Atirador [GDD.STYLES.ATIRADOR]
[DEPENDS: GDD.CORE.ATTR, GDD.COMBAT.FLOW]

**Attribute:** HAB
**Attack:** d10
**Defense:** d8
**Armor:** Light
**Weapons:** Bows, Crossbows, Firearms

### Abilities:
**Na Mosca [GDD.STYLES.ATIRADOR.NA_MOSCA]:** If outside melee, natural 8, 9, or 10 on attack die adds +1d10 Critical Die to GdA.
**Mirar [GDD.STYLES.ATIRADOR.MIRAR]:** If outside melee, spend Movement to Aim. Next action has advantage (unless damaged first).
**Versátil [GDD.STYLES.ATIRADOR.VERSATIL]:** Can use primary ability of a second HAB-based style. Can switch styles at start of turn if equipped correctly.
**Escorregadio [GDD.STYLES.ATIRADOR.ESCORREGADIO]:** Spend 2 Focus during movement for +50% distance or advantage on disengage tests.

---

## Conjurador [GDD.STYLES.CONJURADOR]
[DEPENDS: GDD.CORE.ATTR, GDD.COMBAT.FLOW]

**Attribute:** MEN
**Attack:** d8
**Defense:** d8
**Spellcasting:** d10
**Armor:** Robe
**Weapons:** Tomes, Staves, Orbs

### Abilities:
**Condutor de Mana [GDD.STYLES.CONJURADOR.CONDUTOR]:** Spend Attack Action to manifest Mana (MEN value). Can then cast if total Mana is sufficient. Damage requires MEN check (DC 5 + source attribute) to maintain Mana.
**Analítico [GDD.STYLES.CONJURADOR.ANALITICO]:** Roll Spellcasting die and keep result for next turn. Can still manifest Mana in the same turn.
**Bateria de Mana [GDD.STYLES.CONJURADOR.BATERIA]:** Can store Mana equal to MEN even outside combat.
**Resoluto [GDD.STYLES.CONJURADOR.RESOLUTO]:** Above 50% HP, gain advantage on MEN checks to maintain Mana.

---

# GDD Module: Resources [GDD.RESOURCES]

List of resources used in the game.

---

## Mana [GDD.RESOURCES.MANA]
[DEPENDS: GDD.CORE.ATTR.MEN, GDD.CORE.TIME.ACTION.TYPES]
**Manifest Mana:** Movement Action. Generates Floating Mana equal to MEN.
**Capacity:** Max Mana: defined by MEN progression table, Max Floating Mana: `5 * MEN`
**Floating Mana** Mana available to cast spells.
**Usage:** Must turn mana into floating mana to use it. Floating mana is used to cast spells. Dissipates at the end of combat.
**Concentration:** Taking damage requires a MEN test (DC 5 + source main attribute) to avoid losing manifested mana.

---

## Focus [GDD.RESOURCES.FOCUS]
[DEPENDS: GDD.CORE.ATTR.MEN, GDD.CORE.TIME.ACTION.TYPES]

**Generation:** Generated by attacking or spending a Movement Action (generates MEN value).
**Capacity:** Max Focus = `5 * MEN`.
**Usage:** Used to activate physical style abilities.
**Cumulative Costs:** Abilities with cumulative costs double the cost for each subsequent use. The cost resets at the start of your next action.
**Conversion:** For hybrid martial/magic styles, a Movement Action can convert Focus to Mana.

---

## Hit Points (PV)[GDD.RESOURCES.PV]
[DEPENDS: CORE.ATTR.FIS, CORE.PROG.FIS]

**Capacity:** Defined by the FIS attribute.
**Use:** Represents the character's health. If the value reaches equal or below zero, the character is incapacitated.
**Recovery:** Characters recover health through spells, items, or by resting in a safe place. Incapacitated characters need specific itens or a full rest ro recover.

---

# GDD Module: Status Effects [GDD.STATUS]
[DEPENDS: GDD.CORE.TIME, GDD.COMBAT.FLOW]

## Stunned (Atordoado) [GDD.STATUS.ATORDOADO]:
[DEPENDS: GDD.CORE.TIME]
Add 50% target's Action Cost value to target's tick counter. -1 BDD until end of next turn.
## Unbalanced (Desequilibrado) [GDD.STATUS.DESEQUILIBRADO]:
[DEPENDS: GDD.COMBAT.FLOW.DSV]
Defense rolls are at disadvantage until start of next turn.
## Knocked Down (Derrubado) [GDD.STATUS.DERRUBADO]:
[DEPENDS: GDD.CORE.TIME, GDD.COMBAT.FLOW.DSV]
Add 50% target's Action Cost value to target's tick counter. Defense rolls at disadvantage.
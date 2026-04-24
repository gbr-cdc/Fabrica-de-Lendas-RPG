# GDD Module: Combat Styles [GDD.STYLES]

The Combat Style determines how the character fights, the equipment they use, and grants combat abilities. It also defines the attack/defense dice and the primary attribute.

---

## 1. Destruidor [GDD.STYLES.DESTRUIDOR]
[DEPENDS: GDD.CORE.ATTR, GDD.CORE.COMBAT.FLOW, GDD.RES.FOCUS, GDD.STATUS.ATORDOADO]

*   **Attribute:** FIS
*   **Attack:** d12
*   **Defense:** d8
*   **Armor Type:** HEAVY
*   **Weapon Type:** GREAT_WEAPON

### Abilities:
*   **Força Bruta [GDD.STYLES.DESTRUIDOR.FORCA_BRUTA]**: Successful hits have their GdA doubled. Applied before Skill bonus, rounded down.
*   **Mãos Pesadas [GDD.STYLES.DESTRUIDOR.MAOS_PESADAS]**: If GdA > 3 with a GREAT_WEAPON, the target is ATORDOADO.
*   **Alcance [GDD.STYLES.DESTRUIDOR.ALCANCE]**: While using a GREAT_WEAPON, spend 2 Focus to attack all targets in melee range. [AttackType = AREA]
*   **Postura Defensiva [GDD.STYLES.DESTRUIDOR.POSTURA_DEFENSIVA]**: Switch dice to d10/d10. Alcance cost reduced to 1 Focus. Hits apply a -1 Precision penalty to the target's next action against you.

---

## 2. Defensor [GDD.STYLE.DEFENSOR]
[DEPENDS: GDD.CORE.ATTR, GDD.CORE.COMBAT.FLOW, GDD.RES.FOCUS, GDD.RES.STATUS.ATORDOADO]

*   **Attribute:** FIS
*   **Attack:** d8
*   **Defense:** d12
*   **Armor Type:** HEAVY
*   **Weapon Type:** WEAPON_AND_SHIELD

### Abilities:
*   **Bloquear [GDD.STYLE.DEFENSOR.BLOQUEAR]**: While shielding, spend 2 Focus to add 1d4 to defense. If defense > attacker's roll and GdA < -3, gain +1 Attack against that opponent.
*   **Golpe de Escudo [GDD.STYLE.DEFENSOR.GOLPE_ESCUDO]**: Spend 2 Focus to attack using defense die. Damage halved, GdA treated as 0. If GdA > 3, target is ATORDOADO.
*   **Pressionar [GDD.STYLE.DEFENSOR.PRESSIONAR]**: Spend 2 Focus to gain advantage on menace tests. Every time you succeed in a menace test you gain advantage to attack that target in your next action.
*   **Proteger [GDD.STYLE.DEFENSOR.PROTEGER]**: Spend 2 Focus to redirect a melee attack from an adjacent ally to yourself. Does not work against SKILL or MAGIC.

---

## 3. Duelista [GDD.STYLE.DUELISTA]
[DEPENDS: GDD.CORE.ATTR, GDD.RES.FOCUS, GDD.RES.STATUS.DESEQUILIBRADO, GDD.COMBAT.FLOW]

*   **Attribute:** HAB
*   **Attack:** d8
*   **Defense:** d10
*   **Armor Type:** LIGHT
*   **Weapon Type:** LIGHT_WEAPON

### Abilities:
*   **Graça do Duelista [GDD.STYLE.DUELISTA.GRACA]**: On hit, add 1d6 to GdA. When targeted, can spend 2 Focus to add 1d4 to defense.
*   **Golpe Baixo [GDD.STYLE.DUELISTA.GOLPE_BAIXO]**: Spend 2 Focus to force a HAB contest against a melee target. Success: target is DESEQUILIBRADO and Golpe Baixo costs a Movement Action. Failure: Golpe Baixo costs a Standard Action.
*   **Contra Ataque [GDD.STYLE.DUELISTA.CONTRA_ATAQUE]**: If GdA < 0, spend 2 Focus to counter-attack.
*   **Pés Ligeiros [GDD.STYLE.DUELISTA.PES_LIGEIROS]**: Spend 2 Focus during movement for +50% distance bonus or advantage on disengage tests. Melee hits gives the target -1 Precision against you on their next action.

---

## 4. Mestre das Armas [GDD.STYLE.MESTRE_ARMAS]
[DEPENDS: GDD.CORE.ATTR.FIS, GDD.RES.FOCUS, GDD.RESOL.GD_A]

*   **Attribute:** FIS
*   **Attack:** d10
*   **Defense:** d10
*   **Armor Type:** HEAVY
*   **Weapon Type:** MEDIUM_WEAPON

### Abilities:
*   **Postura de Batalha [GDD.STYLE.MESTRE_ARMAS.POSTURAS]**: Choose at start of turn:
    *   **Offensive**:-1 Guard / +1 Precision and +2 GdA. Bonus doubles if attack die > 7.
    *   **Defensive**: -1 Precision / +1 Guard. Spend 2 Focus to re-roll defense (must keep new result).
*   **Ataque Concentrado [GDD.STYLE.MESTRE_ARMAS.CONCENTRADO]**: Spend movement action to prepare. Grants you advantage in attacks on your next action against one target. If in Defensive posture, switch to Offensive before attacking. Grants opportunity attack if target leaves range.
*   **Ataque Desarmante [GDD.STYLE.MESTRE_ARMAS.DESARMANTE]**: Spend 2 Focus. On hit, target has disadvantage on their next action. GdA treated as 0 for damage.
*   **Dança da Batalha [GDD.STYLE.MESTRE_ARMAS.VITAIS]**: Spend 2 Focus to gain +50% movement or gain advnatage in menace tests. Every time toy roll a 10 to attack, this attack counts as a movement action.

---

## 5. Retalhador [GDD.STYLE.RETALHADOR]
[DEPENDS: GDD.CORE.ATTR, GDD.CORE.TIME, GDD.COMBAT.FLOW]

*   **Attribute:** HAB
*   **Attack:** d10
*   **Defense:** d8
*   **Armor Type:** LIGHT
*   **Weapon Type:** SWORD (ANY)

### Abilities:
*   **Ritmo Acelerado [GDD.STYLE.RETALHADOR.RITMO_ACELERADO]**: Every time you roll 7 or more in attack, that attack counts as a movement action. This can happen 2 times in a roll. If that happens, the third attack is a standard action gain +2 PRE.
*   **Ritmo Crescente [GDD.STYLE.RETALHADOR.RITMO_CRESCENTE]**: +1 PRE on hit (max +2). Reset on miss.
*   **Pressionar [GDD.STYLE.RETALHADOR.PRESSIONAR]**: Spend 2 Focus to gain advantage on menace tests. Success grants advantage on attack against that target on your next action. Every time you hit a target, that target gains  
*   **Barreira de Lâminas [GDD.STYLE.RETALHADOR.BARREIRA]**: Attacks apply Precision penalty to target against you. Penalty doubles on hit.

---

## 6. Lutador [GDD.STYLE.LUTADOR]
[DEPENDS: GDD.CORE.ATTR.FIS, GDD.RES.FOCUS, GDD.RES.STATUS.ATORDOADO, GDD.RES.STATUS.DERRUBADO]

*   **Attribute:** FIS
*   **Attack:** d10
*   **Defense:** d10
*   **Armor:** Light
*   **Weapons:** Gloves/Unarmed

### Abilities:
*   **Combo [GDD.STYLE.LUTADOR.COMBO]**: Attack action allows two attacks. If both hit, perform a third attack that Stuns.
*   **Investida [GDD.STYLE.LUTADOR.INVESTIDA]**: Spend 2 Focus and Attack Action to move up to speed in straight line and attack with +2 GdA.
*   **Balão [GDD.STYLE.LUTADOR.BALAO]**: Replace attack with grapple roll. On hit, FIS contest to throw. Target is Knocked Down and takes PdA damage.
*   **Evasão [GDD.STYLE.LUTADOR.EVASAO]**: Spend 2 Focus to add 1d4 to defense when targeted.

---

## 7. Atirador [GDD.STYLE.ATIRADOR]
[DEPENDS: GDD.CORE.ATTR.HAB, GDD.RES.FOCUS, GDD.RESOL.GD_A]

*   **Attribute:** HAB
*   **Attack:** d10
*   **Defense:** d8
*   **Armor:** Light
*   **Weapons:** Bows, Crossbows, Firearms

### Abilities:
*   **Na Mosca [GDD.STYLE.ATIRADOR.NA_MOSCA]**: If outside melee, natural 8, 9, or 10 on attack die adds +1d10 Critical Die to GdA.
*   **Mirar [GDD.STYLE.ATIRADOR.MIRAR]**: If outside melee, spend Movement to Aim. Next action has advantage (unless damaged first).
*   **Versátil [GDD.STYLE.ATIRADOR.VERSATIL]**: Can use primary ability of a second HAB-based style. Can switch styles at start of turn if equipped correctly.
*   **Escorregadio [GDD.STYLE.ATIRADOR.ESCORREGADIO]**: Spend 2 Focus during movement for +50% distance or advantage on disengage tests.

---

## 8. Conjurador [GDD.STYLE.CONJURADOR]
[DEPENDS: GDD.CORE.ATTR.MEN, GDD.RES.MANA, GDD.CORE.TIME]

*   **Attribute:** MEN
*   **Attack:** d8
*   **Defense:** d8
*   **Spellcasting:** d10
*   **Armor:** Robe
*   **Weapons:** Tomes, Staves, Orbs

### Abilities:
*   **Condutor de Mana [GDD.STYLE.CONJURADOR.CONDUTOR]**: Spend Attack Action to manifest Mana (MEN value). Can then cast if total Mana is sufficient. Damage requires MEN check (DC 5 + source attribute) to maintain Mana.
*   **Analítico [GDD.STYLE.CONJURADOR.ANALITICO]**: Roll Spellcasting die and keep result for next turn. Can still manifest Mana in the same turn.
*   **Bateria de Mana [GDD.STYLE.CONJURADOR.BATERIA]**: Can store Mana equal to MEN even outside combat.
*   **Resoluto [GDD.STYLE.CONJURADOR.RESOLUTO]**: Above 50% HP, gain advantage on MEN checks to maintain Mana.

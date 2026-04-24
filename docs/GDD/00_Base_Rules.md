# GDD Module: Base Rules [GDD.CORE]

Fundamental mechanics governing character attributes and the passage of time in combat.

---

## 1. Attributes [GDD.CORE.ATTR]

*   **Físico (FIS) [GDD.CORE.ATTR.FIS]:** Strength and Resistance. Defines Max HP.
*   **Habilidade (HAB) [GDD.CORE.ATTR.HAB]:** Agility and Precision. Defines Base Action Cost.
*   **Mente (MEN) [GDD.CORE.ATTR.MEN]:** Focus and Spirit. Defines Max Mana and Focus/Mana generation.

---

## 2. The Time Engine [GDD.CORE.TIME]

Combat uses a continuous flow of "Ticks" instead of rounds.

1.  **Initiative:** Characters start with a counter equal to their Action Cost. Lowest counter acts first.
2.  **Action Costs:**
    *   **Standard Action:** Equal to the character's Action Cost (defined by HAB).
    *   **Movement Action:** 50% of the Standard Action cost.
3.  **Scheduling:** After an action, add the action cost to the character's counter. The character with the lowest cumulative counter acts next.

---

## 3. Attribute Scale [GDD.CORE.SCALE]

| Value | Scale | Description |
| :--- | :--- | :--- |
| 0 | Very Weak | Below human level. |
| 2-3 | Common | Average human. |
| 4-6 | Heroic | Peak human / Adventurer. |
| 7-9 | Legendary | Near sonic speeds, town-level magic. |
| 10-12 | Epic | Semi-god level. |
| 13-15 | Divine | Reality warping, light speed. |

---

## 4. Progression Tables [GDD.CORE.PROG]

### Físico (PV) [GDD.CORE.PROG.FIS]

| Attribute | PV |
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

### Habilidade (Action Cost) [GDD.CORE.PROG.HAB]

| Attribute | Action Cost |
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

### Mente (Mana) [GDD.CORE.PROG.MND]

| Attribute | Mana |
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


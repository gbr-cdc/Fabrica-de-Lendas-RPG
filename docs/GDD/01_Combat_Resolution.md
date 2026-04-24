# GDD Module: Combat Resolution [GDD.COMBAT]

This module defines how attacks are resolved, damage is calculated, and equipment tiers are scaled.

---

## 1. Attack Resolution [GDD.COMBAT.FLOW]
[DEPENDS: GDD.CORE.ATTR]

*   **Attack Roll:** Rank Bonus + Attack Die (Style) + Attack Bonus(BDA)
*   **Defense Roll:** Rank Bonus + Defense Die (Style) + Defense Bonus(BDD)
*   **Hit Grade (GdA) [GDD.COMBAT.GDA]:** `Attack - Defense`
    *   If **GdA > 0**: Hit.
    *   If **GdA <= 0**: Miss (unless Precision overrides).

---

## 2. Damage Calculation [GDD.COMBAT.DAMAGE]
[DEPENDS: GDD.COMBAT.GDA, GDD.EQUIP.TIERS]

*   **Damage Formula:** `PdA + (GdA * MdA)`
*   **Attack Power (PdA):** Weapon Base Damage(DB) + Primary Attribute
*   **Attack Multiplier (MdA):** Defined by weapon (Default: 1)

---

## 3. Precision and Guard [GDD.RESOL.PRECISAO]

*   **Precision (PRE) +X:** Allows hitting even if GdA is negative (up to -X). GdA is treated as 0 for damage.
*   **Guard (GRD) +X:** Causes a hit to miss even if GdA is positive (up to X).

---

## 4. Equipment Tiers [GDD.EQUIP.TIERS]

### Weapons

| Tier | Base Damage (DB) | Multiplier (MdA) |
| :---: | :---: | :---: |
| **1** | 3 | 1 |
| **2** | 5 | 1 |
| **3** | 7 | 2 |
| **4** | 10 | 2 |
| **5** | 15 | 3 |

### Armaduras

| Tier | Cloak | Light | Heavy |
| :---: | :---: | :---: | :---: |
| **1** | 10 | 15 | 25 |
| **2** | 15 | 25 | 40 |
| **3** | 25 | 45 | 70 |
| **4** | 35 | 70 | 110 |
| **5** | 55 | 110 | 160 |

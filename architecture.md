# Project Documentation & Architectural Guardrails

This document serves as the primary technical reference for the **Fábrica de Lendas** RPG Engine. It combines high-level architectural rules with detailed module documentation to guide both human developers and AI agents.

---

## 1. Project Vision
**Fábrica de Lendas** is a data-driven, modular RPG engine designed for tactical combat simulation. It follows a strict **Game-MVC** pattern, where rules and logic are decoupled from presentation. The engine uses an **Event-Driven** architecture to handle complex interactions (Passives, Effects) through an Event Bus.

---

## 2. Architectural Guardrails [ARCH.GLOBAL]

These rules are context-exclusive and MUST be referenced in `MISSION_LOG.md` when relevant to the task.

### 2.1 Core Patterns
*   **Game-MVC [ARCH.1.1]**: Strict separation. 
    *   **Models**: Rules, State, and Logic in `core/`, `battle/`, `entities/`, `data/`.
    *   **Controllers**: "Brains" (Decision Flow) in `controllers/`.
    *   **Views**: Presentation layer (Logs/UI) is decoupled from the engine.
*   **Command Pattern [ARCH.1.2]**: All actions (Skills, Basic Attacks, Movements) MUST inherit from `GameAction`/`BattleAction` and implement `can_execute()` and `execute()`.
*   **Observer/EventBus [ARCH.1.3]**: Decouple reactive logic (Effects/Passives) via an EventBus. Orchestrators (e.g., `BattleManager`) manage subscriptions.
*   **IoC (Inversion of Control) [ARCH.1.4]**: Implementations (Passives/Actions) using hooks MUST expose them via `get_hooks()`. Only the Orchestrator (BattleManager) handles event registration.
*   **Data-Driven [ARCH.1.5]**: GameAction templates, CombatStyles, and GameRules MUST be defined in JSON files (`data/`). Use `DataManager` for loading.
*   **Lifecycle Safety [ARCH.1.6]**: Ephemeral hooks (valid for 1 action cycle) MUST be wrapped in `try...finally` within the Orchestrator to guarantee unsubscription.
*   **CQRS [ARCH.1.7]**: Use Methods for direct state changes (e.g., `take_damage`); use Events for notification/modification ONLY.
*   **Modifier Stack Pattern [ARCH.1.8]**: Stats are immutable. All dynamic changes (buffs/debuffs) MUST be implemented as `StatModifier` objects in the character's `modifiers` list.
*   **Anemic Entities [ARCH.1.9]**: Classes in `entities/` are data containers. All complex logic resides in Systems (e.g., `CharacterSystem`) or Actions.
*   **Protocols & Typing [ARCH.1.10]**: Use `typing.Protocol` for Dependency Injection. Use `from __future__ import annotations`. Keep typing imports in `TYPE_CHECKING` blocks to avoid circular dependencies.

### 2.2 Engine Mechanics
*   **Timeline Execution [ARCH.2.1]**: The turn order is managed by a Min-Heap timeline. Characters are re-scheduled based on `action_cost` after every non-free action.
*   **Event Payload Modification [ARCH.2.2]**: Listeners in the EventBus receive payload objects (e.g., `AttackLoad`) passed by reference. They MUST modify the object directly to influence calculations.
*   **Tick-Based Simulation [ARCH.2.3]**: The engine does not use rounds. It uses "Ticks" (discrete units of time). Logic relying on "duration" should count turns or specific events, not wall-clock time.
*   **Error Handling (Decision Loop) [ARCH.2.4]**: Controllers MUST NOT enter an infinite loop when an action fails `can_execute()`. The Orchestrator MUST implement a safety break (Max Attempts).
*   **Targeting Cardinality [ARCH.2.5]**: All `BattleAction` subclasses MUST support a `targets: List[Character]` interface. Single-target actions should use a list with one element.
*   **Area Attack Resolution (Master Roll) [ARCH.2.6]**: For `AttackType.AREA`, the attacker’s roll MUST be performed once (Master Roll) with `target=None` in the `AttackLoad`. This ensures only target-agnostic passives influence the shared roll, followed by individual resolution phases for each target.
*   **Defensive Payload Auditing [ARCH.2.7]**: Any hook that accesses `AttackLoad.target` MUST perform a null-check if the event it listens to could potentially be emitted during a Master Roll phase or a targetless context.

---

## 3. Project Structure [STRUCT.MAP]

```text
.
├── core/                # Fundamental logic, Base Classes, and Systems
├── battle/              # Combat resolution, Passives, and Battle Orchestration
├── entities/            # Data containers (Character, Items)
├── controllers/         # Decision making (AI/Player input)
├── data/                # JSON definitions (Rules, Styles, Actions)
├── utilities/           # Helper scripts and standalone tools
├── tests/               # Pytest suite (Red/Green TDD)
└── pvp_simulator/       # Main entry point for simulation
```

---

## 4. Module: Core [MODULE.core]
The `core` module contains the fundamental building blocks of the engine.

### Enums [FILE:core/Enums.py]
Centralized enumerations to ensure type safety and consistency across the engine.
- `RollState`: Defines dice roll modifiers: `ADVANTAGE` (take highest), `DISADVANTAGE` (take lowest), or `NEUTRAL`.
- `ArmorType`: Categories for physical protection: `ROBE`, `LIGHT`, `HEAVY`.
- `WeaponType`: Categories for offensive equipment, including `GREAT_WEAPON`, `RANGED_WEAPON`, and `MAGICAL_FOCUS`.
- `AttributeType`: The three primary stats: `FIS` (Physical), `HAB` (Skill), `MEN` (Mental).
- `StatusEffectType`: Identifiers for active conditions like `ATORDOADO` or `QUEIMADO`.
- `AttackType`: Classification of offensive maneuvers: `BASIC_ATTACK`, `SKILL`, `AREA`, `EXTRA_ATTACK`.
- `BattleActionType`: Action economy categories: `MOVE_ACTION`, `STANDARD_ACTION`, `FREE_ACTION`.
- `BattleState`: High-level combat outcomes: `VICTORY`, `DEFEAT`, `DRAW`, `RUNNING`, `ERROR`.

### Structs [FILE:core/Structs.py]
Data containers for passing structured information across modules.
- `GameRules [CLASS:GameRules]`: Configuration for global mechanics. Includes `hp_table` and `mp_table` for level scaling, `action_cost_table` for turn delay, and resource multipliers for Focus and Mana (MEN-based). `[ARCH.1.5]`
- `RollResult [CLASS:RollResult]`: Encapsulates a dice roll outcome. Tracks the `final_roll`, individual dice (`roll1`, `roll2` for advantage/disadvantage), and `RollState`. Used by `DiceManager` and the Event Bus.
- `BattleResult [CLASS:BattleResult]`: Summary of a finished combat. Contains the execution `history` (log of events), lists of `winners` and `losers`, `duration` in ticks, and per-character action statistics.
- `CombatStyle [CLASS:CombatStyle]`: Archetype definition for a character's fighting method. Defines attack/defense dice (e.g., d20, d12), the `main_stat` for bonuses, and required weapon/armor types. Loaded from `CombatStyles.json`.
- `AttackEffects [CLASS:AttackEffects]`: Data structure for individual components of an attack (e.g., "Lifesteal", "Stun"). Contains an `id` and a dictionary of `parameters` used by the resolution logic.
- `AttackActionTemplate [CLASS:AttackActionTemplate]`: Blueprint for complex actions. Combines action/attack types, resource costs (Focus), and a list of `AttackEffects`. Used as the base for instantiating `AttackAction`. `[ARCH.1.5]`

### Events [FILE:core/Events.py]
Mutable payload objects for the Event Bus, allowing listeners to influence action outcomes. `[ARCH.2.2]`
- `ActionLoad [CLASS:ActionLoad]`: Base payload for all battle actions. Tracks the `character` performing the action, an execution `history` (log), and a `success` flag.
- `AttackLoad [CLASS:AttackLoad]`: Specialized payload for offensive resolution. Carries the `target`, `battle_context`, `attack_type`, and states (`attack_state`, `defense_state`). Critical fields for modification: `gda` (Degree of Success), `damage`, and `hit` (boolean).

### Base Classes [FILE:core/BaseClasses.py]
Foundational abstract classes and interfaces ensuring modularity and decoupling.
- `GameAction [CLASS:GameAction]`: Abstract base for the Command Pattern. Defines `can_execute()` and `execute()`. `[ARCH.1.2]`
- `BattleAction [CLASS:BattleAction]`: Specialized `GameAction` for combat. Injected with `IBattleContext`, `targets`, and `action_type`. It provides a `target` property for single-target convenience. `[ARCH.2.5]`
- `BattlePassive [CLASS:BattlePassive]`: Base for reactive logic. Holds a reference to the `owner` and `IBattleContext`. Subclasses MUST implement `get_hooks()` to return event subscriptions. `[ARCH.1.4]`
- `IBattleContext [PROTOCOL:IBattleContext]`: Structural typing (Protocol) for the battle orchestrator. Provides methods for `emit()`, `subscribe()`, `delay_character()`, and accessing character/controller registries. `[ARCH.1.10]`

### Character System [FILE:core/CharacterSystem.py]
Stateless domain logic for manipulating `Character` entities. Isolates rule-heavy operations from data containers. `[ARCH.1.9]`
- `take_damage()`: Direct HP modification with a floor of 0. `[ARCH.1.7]`
- `generate_focus() / generate_mana()`: Replenishes floating resources based on the character's `MEN` attribute and `GameRules` limits.
- `spend_focus() / spend_mana()`: Validates and consumes resources for actions; returns success status.
- `equip_weapon() / equip_armor()`: Validates item types against `CombatStyle` and updates derived stats like `base_pda` or `max_hp`.

### Dice Manager [FILE:core/DiceManager.py]
Random number generation and deterministic roll scheduling for combat resolution.
- `roll_dice()`: Core rolling logic supporting single die or 2d20-style Advantage/Disadvantage. Returns a `RollResult`.
- `schedule_result()`: Injects a predefined integer into a queue, forcing the next `roll_dice()` call to return that value. Critical for deterministic testing.

### Data Manager [FILE:core/DataManager.py]
Central registry for loading and accessing data-driven templates from JSON files. `[ARCH.1.5]`
- `load_combat_styles() / load_game_rules() / load_characters() / load_action_templates()`: Methods to populate the internal registries from JSON data.
- `get_action_template() / get_character() / get_combat_style()`: Methods to retrieve hydrated templates or entities by their unique IDs.

### Modifiers [FILE:core/Modifiers.py]
Implementation of the Modifier Stack Pattern for dynamic stat calculation. `[ARCH.1.8]`
- `StatModifier [CLASS:StatModifier]`: Base for all stat changes. Tracks `stat_name`, `value`, and `source` with a unique UUID.
- `EphemeralModifier [CLASS:EphemeralModifier]`: Short-term changes intended to be cleared after combat or specific effect durations.
- `PersistentModifier [CLASS:PersistentModifier]`: Long-term changes typically originating from equipment, traits, or permanent conditions.

---

## 5. Module: Battle [MODULE.battle]
The `battle` module handles combat orchestration, action resolution, and reactive logic.

### Battle Manager [FILE:battle/BattleManager.py]
The central orchestrator of the combat engine, managing time and event propagation. `[ARCH.1.3]`
- `BattleManager [CLASS:BattleManager]`: Manages the `timeline` (Min-Heap), the `listeners` registry (Event Bus), and the character lifecycle. Tracks `current_tick` and maintains a `graveyard`.
- `run_battle()`: The main engine loop. Executes characters' turns in tick order, managing the "Free Action -> Move/Standard Action" cycle and ensuring `resolve_deaths()` and `judge.rule()` are checked. `[ARCH.2.4]`
- `emit()`: Triggers events on the Event Bus. Listeners modify the `ActionLoad` or `AttackLoad` payload objects directly. `[ARCH.2.2]`
- `subscribe() / unsubscribe()`: Manages dynamic listener registration, used by Passives and Status Effects. `[ARCH.1.6]`
- `delay_character()`: Pushes a character's next turn further into the future on the timeline (e.g., due to Stun). `[ARCH.2.1]`
- `resolve_deaths()`: Identifies characters at 0 HP, removes them from active play, and moves them to the `graveyard`.

### Battle Actions [FILE:battle/BattleActions.py]
Implementations of the Command Pattern for combat maneuvers. `[ARCH.1.2]`
- `AttackAction [CLASS:AttackAction]`: Generic data-driven offensive resolution. Implements the complete attack flow (Roll -> Hit Check -> GdA -> Damage -> Application). Supports `AttackType.AREA` with a Master Roll. `[ARCH.2.5]`, `[ARCH.2.6]`
- `GenerateManaAction [CLASS:GenerateManaAction]`: A Move Action that manifest mana from the daily reserve into `floating_mp`. `[ARCH.1.1]`
- `GenerateFocusAction [CLASS:GenerateFocusAction]`: A Move Action that replenishes the `floating_focus` pool.
- `TogglePosturaDefensiva [CLASS:TogglePosturaDefensiva]`: A Free Action that interacts with the `PosturaDefensiva` passive to toggle combat stances.

### Battle Passives [FILE:battle/BattlePassives.py]
Reactive logic and hooks for character-specific traits and abilities. `[ARCH.1.4]`
- `PosturaDefensiva [CLASS:PosturaDefensiva]`: A stateful stance that modifies the owner's dice pools and applies persistent `EphemeralModifier` penalties to enemies it has previously hit. `[ARCH.2.7]`
- `GracaDoDuelista [CLASS:GracaDoDuelista]`: Grants GdA bonuses on `on_gda_modify` and provides an optional defensive reaction (Evasão) that uses `choose_reaction()`.
- `Combo [CLASS:Combo]`: Monitors `on_attack_end` to trigger recursive `AttackAction` executions (Extra Attacks) upon successful hits.
- `ForçaBruta [CLASS:ForçaBruta]`: A simple multiplier applied during the `on_gda_modify` phase.
- `MãosPesadas [CLASS:MãosPesadas]`: Triggers the application of `Atordoado` status if GdA exceeds a threshold during hit resolution.

### Judges [FILE:battle/Judges.py]
Victory and defeat condition logic, called at the start of every turn and after every standard action.
- `BattleJudge [CLASS:BattleJudge]`: Evaluates the presence of living characters in each team to determine the `BattleState`.

### Status Effects [FILE:battle/StatusEffects.py]
Temporary modifiers and behavioral changes with a turn-based duration. `[ARCH.1.8]`
- `StatusEffect [CLASS:StatusEffect]`: Abstract base that extends `BattlePassive`. Implements `apply()` and `remove()` logic, including `EphemeralModifier` management.
- `Atordoado [CLASS:Atordoado]`: Stun effect. Upon application, it immediately calls `delay_character()`. It subscribes to `on_turn_start` to decrement duration or expire.

---

## 6. Module: Entities [MODULE.entities]
The `entities` module contains data-only classes representing game objects. `[ARCH.1.9]`

### Characters [FILE:entities/Characters.py]
The primary data container for actors, designed as an anemic entity with a reactive modifier stack. `[ARCH.1.9]`
- `Character [CLASS:Character]`: Tracks core state: `current_hp`, `current_mp`, `floating_mp`, and `floating_focus`. Maintains references to `CombatStyle`, `Weapon`, and `Armor`.
- **Modifier Stack**: Uses a `modifiers` list and `get_stat_total()` to compute real-time values for stats like `rank`, `bda`, `bdd`, `pre`, `grd`, `pda`, and `mda`. This ensures stats are never mutated directly. `[ARCH.1.8]`
- **Dynamic Dice**: Properties `atk_die` and `def_die` allow the modifier stack to influence the character's dice pool sizes (e.g., d12 -> d10).
- **Status Effects**: Tracks active `StatusEffect` instances that influence behavior via event hooks.

### Items [FILE:entities/Items.py]
Data structures for equipment, used by `CharacterSystem` to populate character stats.
- `Weapon [CLASS:Weapon]`: Dataclass defining offensive traits. Includes `db` (Damage Bonus), `mda` (Degree of Success multiplier), and `type` (for compatibility checks).
- `Armor [CLASS:Armor]`: Dataclass defining defensive traits. Includes `hp_bonus` and `type`.

---

## 7. Module: Controllers [MODULE.controllers]
The `controllers` module implements the "Decision Loop" for characters, separating AI/Player logic from the engine. `[ARCH.1.1]`

### Character Controller [FILE:controllers/CharacterController.py]
The "Decision Loop" interface that separates character behavior (AI or Player) from engine mechanics. `[ARCH.1.1]`
- `CharacterController [CLASS:CharacterController]`: Abstract base class. Defines the interface for tactical decision-making.
- `choose_action()`: Called at the start of a turn. Analyzes the `IBattleContext` and returns a `BattleAction` command. Supports re-decision if the previous action failed validation (via `action_load`). `[ARCH.2.4]`
- `choose_reaction()`: Called during action resolution (e.g., `on_defense_reaction`). Allows the controller to opt-in to conditional effects (like Evasion) based on the current `AttackLoad`.
- `PvP1v1Controller [CLASS:PvP1v1Controller]`: Reference implementation for automated combat. Prioritizes Skills over Basic Attacks if Focus is available.

---

## 8. Module: Data [MODULE.data]
The `data` module stores external JSON definitions that drive engine behavior and character scaling. `[ARCH.1.5]`

### Action Definitions [FILE:data/AttackActions.json]
Blueprints for all combat maneuvers. Defines `focus_cost`, `action_type`, `attack_type` (e.g., AREA), and a list of `AttackEffects` (e.g., "add_gda").

### Character Templates [FILE:data/Characters.json]
Hydration templates for characters. Defines base attributes (`FIS`, `HAB`, `MEN`), starting `Weapon` and `Armor`, and initial lists of `Abilities` and `Passives`.

### Combat Styles [FILE:data/CombatStyles.json]
Archetype definitions that govern dice pool sizes (`atq_die`, `def_die`), the `main_stat` for damage calculation, and equipment requirements (`ArmorType`, `WeaponType`).

### Game Rules [FILE:data/Rules.json]
Global constants and progression tables. Defines `limite_foco`/`limite_mana` multipliers and scaling tables for HP, MP, and `action_cost` based on attribute scores.



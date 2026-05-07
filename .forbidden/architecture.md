# Project Documentation [ARCH.GLOBAL]

This document serves as the primary technical reference for the **Fábrica de Lendas** RPG Engine. It combines high-level architectural rules with detailed module documentation to guide both human developers and AI agents.

## Project Vision [ARCH.VISION]
**Fábrica de Lendas** is a data-driven, modular RPG engine designed for tactical combat simulation. It follows a strict **Game-MVC** pattern, where rules and logic are  decoupled from presentation. The engine uses an **Event-Driven** architecture to handle complex interactions (Passives, Effects) through an Event Bus.

## Architectural Guardrails [ARCH.RULES]

These rules are context-exclusive and MUST be referenced in `MISSION_LOG.md` when relevant to the task.

### Core Patterns [ARCH.RULES.CORE]
- **Game-MVC [ARCH.RULES.CORE.MVC]:** **Models:** Files in `core/`, `battle/`, `entities/`, `data/`. Represents the game world, rules and entities; **Controllers:** Files in `controllers/`. Scripts that instantiates and orquestrates models; **Views**: Presentation layer (Logs/UI) is decoupled from the engine.
- **Command Pattern [ARCH.RULES.CORE.COMMAND]:** All actions (Skills, Basic Attacks, Movements) MUST inherit from `GameAction` and implement `can_execute()` and `execute()`. The `execute()` function returns a `ActionLoad` with a execution history.
- **Observer/EventBus [ARCH.RULES.CORE.OBSERVER]:** Decouples reactive logic (Passives/Status Effects) from core execution via an EventBus. Orchestrators manage "hooks" (listener functions) that are registered to specific battle events.
- **IoC (Inversion of Control) [ARCH.RULES.CORE.IOC]:** Reactive components (Passives/Status/Actions) do not register themselves. They MUST expose their listener functions via `get_hooks()`, returning a mapping of event keys to callbacks. The `BattleManager` remains the sole authority for subscribing and unsubscribing these hooks.
- **Data-Driven [ARCH.RULES.CORE.DATA]:** GameAction templates, CombatStyles, and GameRules are defined in JSON files (`data/`). Use `DataManager` for loading. JSON configurations should be preferred over hard coded implementations.
- **CQRS [ARCH.RULES.CORE.CQRS]:** Use Methods for direct state changes (e.g., `take_damage`); use Events for notifications and event payload modifications ONLY.
- **Modifier Stack Pattern [ARCH.RULES.CORE.MODIFIER]:** Stats are immutable. All dynamic changes (buffs/debuffs) MUST be implemented as `StatModifier` objects in the character's `modifiers` list.
- **Event Stream History [ARCH.RULES.CORE.HISTORY]:** Decouples the Engine (Model) from the presentation (View). The `history` field in `ActionLoad` payloads MUST contain only pipe-delimited structured tags (`TAG|PARAM...`). Use `HistoryEmitter` to generate standard tags. Narrative strings and localization are strictly prohibited within the Model layer; they are the exclusive responsibility of the View.
- **Anemic Entities [ARCH.RULES.CORE.ENTITIES]:** Classes in `entities/` are data containers. All complex logic resides in Systems (e.g., `CharacterSystem`) or Actions.
- **Protocols & Typing [ARCH.RULES.CORE.TYPING]:** Use `typing.Protocol` for Dependency Injection. Use `from __future__ import annotations`. Keep typing imports in `TYPE_CHECKING` blocks to avoid circular dependencies.

### Battle Engine Mechanics [ARCH.RULES.BATTLE]
- **Timeline Execution [ARCH.RULES.BATTLE.TIMELINE]:** The turn order is managed by a Min-Heap timeline. Characters are re-scheduled based on `action_cost` after every non-free action.
- **Event Payload Modification [ARCH.RULES.BATTLE.PAYLOAD]:** Listeners in the EventBus receive payload objects (e.g., `AttackLoad`) passed by reference. They MUST modify the object directly to influence calculations.
- **Tick-Based Simulation [ARCH.RULES.BATTLE.TICKS]:** The engine does not use rounds. It uses "Ticks" (discrete units of time). Logic relying on "duration" should count turns or specific events, not wall-clock time.
- **Error Handling (Decision Loop) [ARCH.RULES.BATTLE.DECISION]:** `CharacterController` MUST NOT enter an infinite loop when an action fails `can_execute()`. The `BattleManager` MUST implement a safety break (Max Attempts).
- **Targeting Cardinality [ARCH.RULES.BATTLE.TARGETING]:** All `BattleAction` subclasses MUST support a `targets: List[Character]` interface. Single-target actions should use a list with one element.
- **Area Attack Resolution (Master Roll) [ARCH.RULES.BATTLE.AREA_ATTACK]:** For `AttackType.AREA`, the attacker’s roll MUST be performed once (Master Roll) with `target=None` in the `AttackLoad`. This ensures only target-agnostic passives influence the shared roll, followed by individual resolution phases for each target.
- **Defensive Payload Auditing [ARCH.RULES.BATTLE.PAYLOAD_TARGET_CHECK]:** Any hook that accesses `AttackLoad.target` MUST perform a null-check if the event it listens to could potentially be emitted during a Master Roll phase or a targetless context..
- **Action-Scoped Interceptors [ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]:** Hooks that exist only for the duration of a single action. `BattleManager` MUST execute actions within a `try...finally` block to guarantee these hooks are unsubscribed, allowing actions (like `AttackAction`) to modify their own resolution steps via the event bus.

## Project Structure [ARCH.STRUCT_MAP]

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

## Modules Documentation [ARCH.DOC]

### MODULE: Core [ARCH.DOC.core]
The `core` module contains the fundamental building blocks of the engine. `[ARCH.RULES.CORE]`

#### Enums [ARCH.DOC.core.Enums]
Centralized enumerations to ensure type safety and consistency across the engine.
- RollState [ARCH.DOC.core.Enums.CLASS:RollState]: Defines dice roll modifiers: `ADVANTAGE` (take highest), `DISADVANTAGE` (take lowest), or `NEUTRAL`.
- ArmorType [ARCH.DOC.core.Enums.CLASS:ArmorType]: Categories for physical protection: `ROBE`, `LIGHT`, `HEAVY`.
- WeaponType [ARCH.DOC.core.Enums.CLASS:WeaponType]: Categories for offensive equipment, including `GREAT_WEAPON`, `RANGED_WEAPON`, and `MAGICAL_FOCUS`.
- AttributeType [ARCH.DOC.core.Enums.CLASS:AttributeType]: The three primary stats: `FIS` (Physical), `HAB` (Skill), `MEN` (Mental).
- StatusEffectType [ARCH.DOC.core.Enums.CLASS:StatusEffectType]: Identifiers for active conditions like `ATORDOADO` or `QUEIMADO`.
- AttackType [ARCH.DOC.core.Enums.CLASS:AttackType]: Classification of offensive maneuvers: `BASIC_ATTACK`, `SKILL`, `AREA`, `EXTRA_ATTACK`.
- BattleActionType [ARCH.DOC.core.Enums.CLASS:BattleActionType]: Action economy categories: `MOVE_ACTION`, `STANDARD_ACTION`, `FREE_ACTION`.
- BattleState [ARCH.DOC.core.Enums.CLASS:BattleState]: High-level combat outcomes: `VICTORY`, `DEFEAT`, `DRAW`, `RUNNING`, `ERROR`.

#### Structs [ARCH.DOC.core.Structs]
Data containers for passing structured information across modules. `[ARCH.RULES.CORE.DATA]`

##### GameRules [ARCH.DOC.core.Structs.CLASS:GameRules]
Configuration for global mechanics. Includes `hp_table` and `mp_table` for level scaling, `action_cost_table` for turn delay, and resource multipliers for Focus and Mana (MEN-based). `[ARCH.RULES.CORE.DATA]`

##### RollResult [ARCH.DOC.core.Structs.CLASS:RollResult]
Encapsulates a dice roll outcome. Tracks the `final_roll`, individual dice (`roll1`, `roll2` for advantage/disadvantage), and `RollState`. Used by `DiceManager` and the Event Bus.

##### BattleResult [ARCH.DOC.core.Structs.CLASS:BattleResult]
Summary of a finished combat. Contains the execution `history` (log of events), lists of `winners` and `losers`, `duration` in ticks, and per-character action statistics.

##### CombatStyle [ARCH.DOC.core.Structs.CLASS:CombatStyle]
Archetype definition for a character's fighting method. Defines attack/defense dice (e.g., d20, d12), the `main_stat` for bonuses, and required weapon/armor types. Loaded from `CombatStyles.json`. `[ARCH.RULES.CORE.DATA]`

##### AttackEffects [ARCH.DOC.core.Structs.CLASS:AttackEffects]
Data structure for individual components of an attack (e.g., "Lifesteal", "Stun"). Contains an `id` and a dictionary of `parameters` used by the resolution logic.

##### AttackActionTemplate [ARCH.DOC.core.Structs.CLASS:AttackActionTemplate]
Blueprint for complex actions. Combines action/attack types, resource costs (Focus), and a list of `AttackEffects`. Used as the base for instantiating `AttackAction`. `[ARCH.RULES.CORE.DATA]`

#### Events [ARCH.DOC.core.Events]
Mutable payload objects for the Event Bus, allowing listeners to influence action outcomes. `[ARCH.RULES.BATTLE.PAYLOAD]`

##### ActionLoad [ARCH.DOC.core.Events.CLASS:ActionLoad]
Base payload for all battle actions. Tracks the `character` performing the action, an execution `history` (log), and a `success` flag. `[ARCH.RULES.CORE.HISTORY]`
- add_event() [ARCH.DOC.core.Events.METHOD:ActionLoad.add_event]: Standardizes event insertion into history using a pipe-delimited format (`TAG|PARAM1|...`). `[ARCH.RULES.CORE.HISTORY]`

##### AttackLoad [ARCH.DOC.core.Events.CLASS:AttackLoad]
Specialized payload for offensive resolution. Carries the `target`, `battle_context`, `attack_type`, and states (`attack_state`, `defense_state`). Critical fields for modification: `gda` (Degree of Success), `damage`, and `hit` (boolean).

##### HistoryEmitter [ARCH.DOC.core.Events.CLASS:HistoryEmitter]
Static utility to generate standardized, structured event tags for the history stream (e.g., EXEC, ROLL, DMG, HP, FOCUS, MANA, STATUS). `[ARCH.RULES.CORE.HISTORY]`

#### Base Classes [ARCH.DOC.core.BaseClasses]
Foundational abstract classes and interfaces ensuring modularity and decoupling.

##### GameAction [ARCH.DOC.core.BaseClasses.CLASS:GameAction]
Abstract base for the Command Pattern. Defines `can_execute()` and `execute()`. `[ARCH.RULES.CORE.COMMAND]`

##### BattleAction [ARCH.DOC.core.BaseClasses.CLASS:BattleAction]
Specialized `GameAction` for combat. Injected with `IBattleContext`, `targets`, and `action_type`. It provides a `target` property for single-target convenience. `[ARCH.RULES.BATTLE.TARGETING]`

##### BattlePassive [ARCH.DOC.core.BaseClasses.CLASS:BattlePassive]
Base for reactive logic. Holds a reference to the `owner` and `IBattleContext`. Subclasses MUST implement `get_hooks()` to return event subscriptions. `[ARCH.RULES.CORE.IOC]`

##### IBattleContext [ARCH.DOC.core.BaseClasses.PROTOCOL:IBattleContext]
Structural typing (Protocol) for the battle orchestrator. Provides methods for `emit()`, `subscribe()`, `delay_character()`, `get_graveyard()` and accessing character/controller registries. `[ARCH.RULES.CORE.TYPING]`

##### IBattleJudge [ARCH.DOC.core.BaseClasses.PROTOCOL:IBattleJudge]
Structural typing (Protocol) for victory/defeat logic. Defines `rule(context, result)` to evaluate battle state and populate final results.
#### Character System [ARCH.DOC.core.CharacterSystem]
Stateless domain logic for manipulating `Character` entities. Isolates rule-heavy operations from data containers. `[ARCH.RULES.CORE.ENTITIES]`

- take_damage() [ARCH.DOC.core.CharacterSystem.FUNCTION:take_damage]: Direct HP modification with a floor of 0. `[ARCH.RULES.CORE.CQRS]`
- generate_focus() [ARCH.DOC.core.CharacterSystem.FUNCTION:generate_focus]: Replenishes floating resources based on the character's `MEN` attribute and `GameRules` limits.
- generate_mana() [ARCH.DOC.core.CharacterSystem.FUNCTION:generate_mana]: Replenishes floating resources based on the character's `MEN` attribute and `GameRules` limits.
- spend_focus() [ARCH.DOC.core.CharacterSystem.FUNCTION:spend_focus]: Validates and consumes resources for actions; returns success status.
- spend_mana() [ARCH.DOC.core.CharacterSystem.FUNCTION:spend_mana]: Validates and consumes resources for actions; returns success status.
- equip_weapon() [ARCH.DOC.core.CharacterSystem.FUNCTION:equip_weapon]: Validates item types against `CombatStyle` and updates derived stats like `base_pda` or `max_hp`.
- equip_armor() [ARCH.DOC.core.CharacterSystem.FUNCTION:equip_armor]: Validates item types against `CombatStyle` and updates derived stats like `base_pda` or `max_hp`.

#### Dice Manager [ARCH.DOC.core.DiceManager]
Random number generation and deterministic roll scheduling for combat resolution.

- roll_dice() [ARCH.DOC.core.DiceManager.FUNCTION:roll_dice]: Core rolling logic supporting single die or 2d20-style Advantage/Disadvantage. Returns a `RollResult`.
- schedule_result() [ARCH.DOC.core.DiceManager.FUNCTION:schedule_result]: Injects a predefined integer into a queue, forcing the next `roll_dice()` call to return that value. Critical for deterministic testing.

#### Data Manager [ARCH.DOC.core.DataManager]
Central registry for loading and accessing data-driven templates from JSON files. `[ARCH.RULES.CORE.DATA]`

- load_combat_styles() [ARCH.DOC.core.DataManager.FUNCTION:load_combat_styles]: Methods to populate the internal registries from JSON data.
- load_game_rules() [ARCH.DOC.core.DataManager.FUNCTION:load_game_rules]: Methods to populate the internal registries from JSON data.
- load_characters() [ARCH.DOC.core.DataManager.FUNCTION:load_characters]: Methods to populate the internal registries from JSON data.
- load_action_templates() [ARCH.DOC.core.DataManager.FUNCTION:load_action_templates]: Methods to populate the internal registries from JSON data.
- get_action_template() [ARCH.DOC.core.DataManager.FUNCTION:get_action_template]: Methods to retrieve hydrated templates or entities by their unique IDs.
- get_character() [ARCH.DOC.core.DataManager.FUNCTION:get_character]: Methods to retrieve hydrated templates or entities by their unique IDs.
- get_combat_style() [ARCH.DOC.core.DataManager.FUNCTION:get_combat_style]: Methods to retrieve hydrated templates or entities by their unique IDs.

#### Modifiers [ARCH.DOC.core.Modifiers]
Implementation of the Modifier Stack Pattern for dynamic stat calculation. `[ARCH.RULES.CORE.MODIFIER]`

##### StatModifier [ARCH.DOC.core.Modifiers.CLASS:StatModifier]
Base for all stat changes. Tracks `stat_name`, `value`, and `source` with a unique UUID. `[ARCH.RULES.CORE.MODIFIER]`

##### EphemeralModifier [ARCH.DOC.core.Modifiers.CLASS:EphemeralModifier]
Short-term changes intended to be cleared after combat or specific effect durations.

##### PersistentModifier [ARCH.DOC.core.Modifiers.CLASS:PersistentModifier]
Long-term changes typically originating from equipment, traits, or permanent conditions.

### MODULE: Battle [ARCH.DOC.battle]
The `battle` module handles combat orchestration, action resolution, and reactive logic.

#### Battle Manager [ARCH.DOC.battle.BattleManager]
The central orchestrator of the combat engine. It manages the timeline and serves as the Event Bus. It is responsible for collecting hook functions from active components (Passives, Actions, Status) and executing them when battle events are emitted, allowing for decoupled reactive behavior. [ARCH.RULES.CORE.OBSERVER]

##### BattleManager [ARCH.DOC.battle.BattleManager.CLASS:BattleManager]
Manages the `timeline` (Min-Heap), the `listeners` registry (Event Bus), and the character lifecycle. Tracks `current_tick` and maintains a `graveyard`. [ARCH.RULES.BATTLE.TIMELINE], [ARCH.RULES.BATTLE.TICKS]

- run_battle() [ARCH.DOC.battle.BattleManager.METHOD:BattleManager.run_battle]: The main engine loop. Executes characters turns in tick order. Registers `TURN_START` tags and ensures `resolve_deaths()` and `judge.rule(context, result)` are checked. [ARCH.RULES.BATTLE.DECISION], [ARCH.RULES.BATTLE.TICKS]
- emit() [ARCH.DOC.battle.BattleManager.METHOD:BattleManager.emit]: Triggers events on the Event Bus. Listeners modify the `ActionLoad` or `AttackLoad` payload objects directly. [ARCH.RULES.BATTLE.PAYLOAD]
- subscribe() [ARCH.DOC.battle.BattleManager.METHOD:BattleManager.subscribe]: Manages dynamic listener registration, used by Passives and Status Effects. [ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]
- unsubscribe() [ARCH.DOC.battle.BattleManager.METHOD:BattleManager.unsubscribe]: Manages dynamic listener registration, used by Passives and Status Effects. [ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]
- delay_character() [ARCH.DOC.battle.BattleManager.METHOD:BattleManager.delay_character]: Pushes a character next turn further into the future on the timeline (e.g., due to Stun). [ARCH.RULES.BATTLE.TIMELINE]
- resolve_deaths() [ARCH.DOC.battle.BattleManager.METHOD:BattleManager.resolve_deaths]: Identifies characters at 0 HP, removes them from active play, moves them to the `graveyard`, and registers `DEATH` tags.
- get_graveyard() [ARCH.DOC.battle.BattleManager.METHOD:BattleManager.get_graveyard]: Returns a list of all characters currently in the graveyard.

#### Battle Actions [ARCH.DOC.battle.BattleActions]
Implementations of the Command Pattern for combat maneuvers. Certain actions (like `AttackAction`) use hooks to allow their resolution logic to be modified by external reactive components. [ARCH.RULES.CORE.COMMAND]

##### AttackAction [ARCH.DOC.battle.BattleActions.CLASS:AttackAction]
Generic data-driven offensive resolution. Implements a multi-phase flow (Roll -> Hit Check -> GdA -> Damage -> Application). It triggers `emit()` at each phase, allowing hook functions to intercept and modify the `AttackLoad` payload (e.g., modifying damage or adding status triggers). It uses [ARCH.RULES.BATTLE.EPHEMERAL_HOOKS] to manage these temporary resolution modifiers. Registers structured tags for every phase. Supports `AttackType.AREA` with a Master Roll. [ARCH.RULES.BATTLE.TARGETING], [ARCH.RULES.BATTLE.AREA_ATTACK]

##### GenerateManaAction [ARCH.DOC.battle.BattleActions.CLASS:GenerateManaAction]
A Move Action that manifest mana from the daily pool (`MANA_T`) into the floating pool (`MANA_F`).

##### GenerateFocusAction [ARCH.DOC.battle.BattleActions.CLASS:GenerateFocusAction]
A Move Action that replenishes the `floating_focus` pool, emitting `FOCUS` tags.

##### TogglePosturaDefensiva [ARCH.DOC.battle.BattleActions.CLASS:TogglePosturaDefensiva]
A Free Action that interacts with the `PosturaDefensiva` passive to toggle combat stances.

#### Battle Passives [ARCH.DOC.battle.BattlePassives]
Reactive logic and listeners for character traits. Passives define hook functions that "hook" into battle events (e.g., `on_hit`, `on_dmg_modify`). When an event is emitted, the passive's hook is executed to apply its effects or modify a payload. They follow [ARCH.RULES.CORE.IOC] by exposing these listeners via `get_hooks()`.

##### PosturaDefensiva [ARCH.DOC.battle.BattlePassives.CLASS:PosturaDefensiva]
A stateful stance that modifies the owner's dice pools and applies persistent `EphemeralModifier` penalties to enemies it has previously hit. [ARCH.RULES.BATTLE.PAYLOAD_TARGET_CHECK]

##### GracaDoDuelista [ARCH.DOC.battle.BattlePassives.CLASS:GracaDoDuelista]
Grants GdA bonuses on `on_gda_modify` and provides an optional defensive reaction (Evasão) that uses `choose_reaction()`.

##### Combo [ARCH.DOC.battle.BattlePassives.CLASS:Combo]
Monitors `on_attack_end` to trigger recursive `AttackAction` executions (Extra Attacks) upon successful hits.

##### ForçaBruta [ARCH.DOC.battle.BattlePassives.CLASS:ForçaBruta]
A simple multiplier applied during the `on_gda_modify` phase.

##### MãosPesadas [ARCH.DOC.battle.BattlePassives.CLASS:MãosPesadas]
Triggers the application of `Atordoado` status if GdA exceeds a threshold during hit resolution.

#### Judges [ARCH.DOC.battle.Judges]
Victory and defeat condition logic, called at the start of every turn and after every standard action.

##### BattleJudge [ARCH.DOC.battle.Judges.CLASS:BattleJudge]
Evaluates the presence of living characters in each team to determine the `BattleState`. Populates `BattleResult.winners` and `BattleResult.losers` when reaching a terminal state.
- rule() [ARCH.DOC.battle.Judges.METHOD:BattleJudge.rule]: Evaluates the context to determine victory, defeat, or draw. Updates the `BattleResult` object with winners and losers based on team outcome.

#### Status Effects [ARCH.DOC.battle.StatusEffects]
Temporary modifiers and behavioral changes with a turn-based duration. They function as dynamic passives, subscribing hooks to the battle context upon application and unsubscribing when they expire. [ARCH.RULES.CORE.MODIFIER]

##### StatusEffect [ARCH.DOC.battle.StatusEffects.CLASS:StatusEffect]
Abstract base extending `BattlePassive`. Status effects act as temporary passives; they use hook functions to monitor events like `on_turn_start` while active. Upon `apply()`, their hooks are subscribed to the `BattleManager`, and upon `remove()`, they are unsubscribed, ensuring their behavioral changes are strictly limited to their duration. [ARCH.RULES.CORE.MODIFIER]

##### Atordoado [ARCH.DOC.battle.StatusEffects.CLASS:Atordoado]
Stun effect. Upon application, it immediately calls `delay_character()`. It subscribes to `on_turn_start` to decrement duration or expire. Registers `STATUS` tags when applied/removed.

### MODULE: Entities [ARCH.DOC.entities]
The `entities` module contains data-only classes representing game objects. `[ARCH.RULES.CORE.ENTITIES]`

#### Characters [ARCH.DOC.entities.Characters]
The primary data container for actors, designed as an anemic entity with a reactive modifier stack. `[ARCH.RULES.CORE.ENTITIES]`

##### Character [ARCH.DOC.entities.Characters.CLASS:Character]
Tracks core state: `current_hp`, `current_mp`, `floating_mp`, and `floating_focus`. Maintains references to `CombatStyle`, `Weapon`, and `Armor`.

- get_stat_total() [ARCH.DOC.entities.Characters.METHOD:Character.get_stat_total]: Computes real-time values for stats like `rank`, `bda`, `bdd`, `pre`, `grd`, `pda`, and `mda`. This ensures stats are never mutated directly. `[ARCH.RULES.CORE.MODIFIER]`

#### Items [ARCH.DOC.entities.Items]
Data structures for equipment, used by `CharacterSystem` to populate character stats.

##### Weapon [ARCH.DOC.entities.Items.CLASS:Weapon]
Dataclass defining offensive traits. Includes `db` (Damage Bonus), `mda` (Degree of Success multiplier), and `type` (for compatibility checks).

##### Armor [ARCH.DOC.entities.Items.CLASS:Armor]
Dataclass defining defensive traits. Includes `hp_bonus` and `type`.

### MODULE: Controllers [ARCH.DOC.controllers]
The `controllers` module implements the "Decision Loop" for characters, separating AI/Player logic from the engine. `[ARCH.RULES.CORE.MVC]`

#### Character Controller [ARCH.DOC.controllers.CharacterController]
The "Decision Loop" interface that separates character behavior (AI or Player) from engine mechanics. `[ARCH.RULES.CORE.MVC]`

##### CharacterController [ARCH.DOC.controllers.CharacterController.CLASS:CharacterController]
Abstract base class. Defines the interface for tactical decision-making.

- choose_action() [ARCH.DOC.controllers.CharacterController.METHOD:CharacterController.choose_action]: Called at the start of a turn. Analyzes the `IBattleContext` and returns a `BattleAction` command. Supports re-decision if the previous action failed validation (via `action_load`). `[ARCH.RULES.BATTLE.DECISION]`
- choose_reaction() [ARCH.DOC.controllers.CharacterController.METHOD:CharacterController.choose_reaction]: Called during action resolution (e.g., `on_defense_reaction`). Allows the controller to opt-in to conditional effects (like Evasion) based on the current `AttackLoad`.

##### PvP1v1Controller [ARCH.DOC.controllers.CharacterController.CLASS:PvP1v1Controller]
Reference implementation for automated combat. Prioritizes Skills over Basic Attacks if Focus is available.

### MODULE: Data [ARCH.DOC.data]
The `data` module stores external JSON definitions that drive engine behavior and character scaling. `[ARCH.RULES.CORE.DATA]`

#### Action Definitions [ARCH.DOC.data.AttackActions]
Blueprints for all combat maneuvers. Defines `focus_cost`, `action_type`, `attack_type` (e.g., AREA), and a list of `AttackEffects` (e.g., "add_gda").

#### Character Templates [ARCH.DOC.data.Characters]
Hydration templates for characters. Defines base attributes (`FIS`, `HAB`, `MEN`), starting `Weapon` and `Armor`, and initial lists of `Abilities` and `Passives`.

#### Combat Styles [ARCH.DOC.data.CombatStyles]
Archetype definitions that govern dice pool sizes (`atq_die`, `def_die`), the `main_stat` for damage calculation, and equipment requirements (`ArmorType`, `WeaponType`).

#### Game Rules [ARCH.DOC.data.Rules]
Global constants and progression tables. Defines `limite_foco`/`limite_mana` multipliers and scaling tables for HP, MP, and `action_cost` based on attribute scores.

### MODULE: Utilities [ARCH.DOC.utilities]
The `utilities` module provides cross-cutting tools for documentation management, system operations, and agent assistance.

#### Reference Manager [ARCH.DOC.utilities.ref_manager]
The central tool for targeted documentation extraction, recursive dependency resolution, and automated documentation maintenance.

- PATH_MAPPING [ARCH.DOC.utilities.ref_manager.GLOBAL:PATH_MAPPING]: Configuration dictionary mapping tag prefixes (e.g., `ARCH.`, `GDD.`, `WORKFLOWS.`) to their source markdown files, ensuring centralized path management.
- resolve_tag() [ARCH.DOC.utilities.ref_manager.FUNCTION:resolve_tag]: The primary recursive solver. It fetches a tag's content and iteratively resolves all nested "DEPENDS:" tags. It maintains a `resolved_tags` registry to prevent circular dependencies. When a tag is found in a header (session), all other tags within that session are automatically marked as resolved to ensure clean extraction.
- extract_section() [ARCH.DOC.utilities.ref_manager.FUNCTION:extract_section]: The parsing engine. It searches for a tag (prioritizing headers) and extracts the corresponding block of text. If the tag is found in a header, it captures all content until a header of equal or higher level is encountered.
- update_section() [ARCH.DOC.utilities.ref_manager.FUNCTION:update_section]: The modification engine. Locates a tag and replaces its entire section (if a header) or line with new content. Supports reading content from a string or an external file via `--from-file`.
- create_section() [ARCH.DOC.utilities.ref_manager.FUNCTION:create_section]: The creation engine. Implements **Smart Placement** and **Fail-Fast Validation**: it prevents duplicate tags and ensures hierarchical integrity. New tags are placed after their parent or last sibling based on prefix matching. It fails if a parent tag is missing (returning "Error: Parent tag [prefix] not found." for 3+ component tags) or if the file identifier is missing (for 2 component tags), ensuring documentation structure is maintained.
- get_path_for_tag() [ARCH.DOC.utilities.ref_manager.FUNCTION:get_path_for_tag]: A utility that normalizes tags and determines the correct source file path by matching the tag's prefix against the `PATH_MAPPING`.

##### CLI Usage [ARCH.DOC.utilities.ref_manager.CLI]
- CLI Interface: A command-line wrapper that allows agents to request multiple tags or perform documentation maintenance.
  - **Extraction:** `python3 utilities/ref_manager.py [TAG1] [TAG2]`
  - **Update:** `python3 utilities/ref_manager.py --update [TAG] "Content" [--from-file path]`
  - **Creation:** `python3 utilities/ref_manager.py --create [NEW_TAG] "Content"`
  - **Deletion:** `python3 utilities/ref_manager.py --delete [TAG]`

### MODULE: views [ARCH.DOC.views]
Contains modules responsible for presenting data to the user or translating internal state to human-readable formats.

#### BattleView.py [ARCH.DOC.views.BattleView]
Translates structured history tags from the core into technical narrative strings and handles terminal output. Adheres to `[ARCH.RULES.CORE.MVC]` and `[ARCH.RULES.CORE.HISTORY]`.

##### BattleView [ARCH.DOC.views.BattleView.CLASS:BattleView]
Class responsible for parsing battle history logs and presenting them.

- present_battle() [ARCH.DOC.views.BattleView.METHOD:BattleView.present_battle]: Takes a BattleResult, parses all history tags, and prints the battle narrative followed by a HP summary to the terminal.
- present_summary() [ARCH.DOC.views.BattleView.METHOD:BattleView.present_summary]: Aggregates statistics (wins, draws, turns) for multiple BattleResult objects and prints a summary for the given character IDs.
- parse() [ARCH.DOC.views.BattleView.METHOD:BattleView.parse]: Legacy static method. Takes a list of structured history strings and returns formatted narrative strings.
- _parse_entry() [ARCH.DOC.views.BattleView.METHOD:BattleView._parse_entry]: Private method that translates a single history tag into a human-readable string.

## Test Quality Standards [ARCH.TEST_QUALITY]

- **Behavior over Implementation [ARCH.TEST_QUALITY.TEST_BEHAVIOR]:** Tests MUST verify the outcome (e.g., final HP, ActionLoad, state changes) rather than internal implementation details (e.g., checking specific list indices or private method calls).
- **Controlled Mocking [ARCH.TEST_QUALITY.MOCKING]:** Use real instances for domain logic (Entities, Systems). Mock ONLY system boundaries (I/O, UI) or to enforce determinism. Use `DiceManager.schedule_result()` for simulating dice rolls.
- **Entity Factory [ARCH.TEST_QUALITY.ENTITY_FACTORY]:** Use `tests.utils.entity_factory` when instantiating entities for tests. Use `DataManager` only for integration tests.
- **Data Integrity [ARCH.TEST_QUALITY.DATA_INTEGRITY]:** For integration tests using `DataManager`, use `tests.utils.json_integrity_checker.get_json_keys()` to dynamically iterate over and verify all IDs in game data. This ensures tests remain decoupled from specific balance values while guaranteeing hydration logic works for all defined content.
- **Decoupling [ARCH.TEST_QUALITY.DECOUPLING]:** Ensure tests do not break upon internal refactors if the public behavior remains unchanged.
- **Invariants [ARCH.TEST_QUALITY.INVARIANTS]:** Assert that attribute modifiers `[ARCH.RULES.CORE.MODIFIER]` are properly used and Character atributes are not corrupted by bad modifications.
- **Lifecycle Auditing** [ARCH.TEST_QUALITY.LIFECYCLE]: Tests involving the EventBus MUST verify that all ephemeral hooks ([ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]) used by self modifying actions are successfully unsubscribed after the action cycle. Assert that the EventBus subscriber count returns to its baseline.
- **Battle Context [ARCH.TEST_QUALITY.IBATTLECONTEXT]:** Use `tests.utils.test_context.BattleTestContext` when a concrete implementation of `IBattleContext` is required for behavioral tests, avoiding excessive mocking of the battle state.
- **Structured History [ARCH.TEST_QUALITY.STRUCTURED_HISTORY]:** Tests verifying action outcomes MUST assert against structured event tags (`TAG|PARAM1|PARAM2...`) rather than narrative strings or partial substrings of `MSG` tags. This ensures tests remain resilient to localization changes and narrative polish. `[ARCH.RULES.CORE.HISTORY]`

## Documentation Standards [ARCH.DOC_STANDARDS]

### MISSION [ARCH.DOC_STANDARDS.MISSION]

#### ENTRY FORMAT [ARCH.DOC_STANDARDS.MISSION.ENTRY]

```
- **Header:** ## MISSION: [Title] [PART X] [MISSION.ACTIVE.TITLE_OF_MISSION]. Add `[PART X]` only if mission have more parts.
- **Summary**: Concise technical overview of the goal. Provide enough context to guide execution.
- **Rule References**: Comma-separated list ARCH.RULES tags of architectural rules relevant to the mission`.
- **Definition of Done**: Precise, objective criteria that must be satisfied for mission completion.
- **Plan**: Link to the approved `docs/plans/[mission].md`.
- **Steps**: Atomic TDD steps, organized in pairs of **RED** (Test Objective) and **GREEN** (Implementation), or independent **BLUE** steps if not TDD.

**Step Format**:
- `[RED] [Test Objective]: Detailed description of the behavior to be verified. | Files: tests/path/to/test_file.py`
- `[GREEN] [Implementation]: Brief, but self contained description of the logic to implement. | Files: path/to/file.py`
- `[BLUE]: Brief, but self contained description of the logic to implement. | Files: path/to/file.py`
```

#### ARCHIVED FORMAT [ARCH.DOC_STANDARDS.MISSION.ARCHIVED]

```
- **Header:** `## YYYY-MM-DD HH:MM: [Title] ([Status]) [PART X]`. Add `[PART X]` only if mission have more parts.
- **Summary**: Mission summary.
- **Plan**: Link to the approved `docs/plans/[mission].md`.
- **Steps**: List of completed steps. (with everything including parts "Files:" and "State:")
```

#### Rules [ARCH.DOC_STANDARDS.MISSION.RULES]
- 3-5 steps per part. Max 7 steps (split if larger).
- [RED] steps must be followed by its corresponding [GREEN] step and vice-versa. [BLUE] steps can be executed independently.
- Steps MUST be descriptive enough to allow an agent to work without reading the approved `docs/plans/`

### MODULE [ARCH.DOC_STANDARDS.MODULE]

```
## MODULE: Module_name [ARCH.module_name]
Short description of the module and a list of relevant architectural rules. `[ARCH.RULE.(...)]`, ...

### File Name [ARCH.module_name.FileName]
Short description of the file and a list of relevant architectural rules. `[ARCH.RULE.(...)]`, ...

- variable_name [ARCH.module_name.FileName.GLOBAL:variable_name]: global variable description (only if it affects multiple components or alters system behavior).
- function_name() [ARCH.module_name.FileName.FUNCTION:function_name]: standalone function description with parameters, what it returns and internal logic.

#### InterfaceName [ARCH.module_name.FileName.INTERFACE:InterfaceName]
Interface/Protocol description.

#### ClassName [ARCH.module_name.FileName.CLASS:Classname] 
Class description.
- variable_name [ARCH.module_name.FileName.VARIABLE:variable_name]: variable description (only if it influences external behavior, state transitions, or invariants).
- method_name() [ARCH.module_name.FileName.METHOD:Class.method]: method description with parameters, what it returns and internal logic.

#### CLI Usage [ARCH.module_name.FileName.CLI]
Description of command-line usage.
```

#### Rules [ARCH.DOC_STANDARDS.MODULE.RULES]
- Template shows all possible elements, include only those needed to the documentation.
- Include a section only if there is at least one relevant item.
- Sections MUST follow the order defined in the template.
- Never invent variables/functions just to satisfy the template
- Preserve existing tags when updating
- Prefer extending over rewriting
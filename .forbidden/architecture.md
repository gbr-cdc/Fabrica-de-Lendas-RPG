# Project Documentation [ARCH.GLOBAL]

This document serves as the primary technical reference for the **Fábrica de Lendas** RPG Engine. It combines high-level architectural rules with detailed module documentation to guide both human developers and AI agents.

## Project Vision [ARCH.VISION]
**Fábrica de Lendas** is a data-driven, modular RPG engine designed for tactical combat simulation. It follows a strict **Game-MVC** pattern, where rules and logic are decoupled from presentation. The engine uses an **Event-Driven** architecture to handle complex interactions (Passives, Effects) through an Event Bus.

## Architectural Guardrails [ARCH.RULES]

These rules are context-exclusive and MUST be referenced in `MISSION_LOG.md` when relevant to the task.

### Core Patterns [ARCH.RULES.CORE]
- **Game-MVC [ARCH.RULES.CORE.MVC]:** **Models:** Files in `core/`, `battle/`, `entities/`, `data/`. Represents the game world, rules and entities; **Controllers:** Files in `controllers/`. Scripts that instantiates and orquestrates models; **Views**: Presentation layer (Logs/UI) is decoupled from the engine.
- **Command Pattern [ARCH.RULES.CORE.COMMAND]**: All actions (Skills, Basic Attacks, Movements) MUST inherit from `GameAction` and implement `can_execute()` and `execute()`.
- **Observer/EventBus [ARCH.RULES.CORE.OBSERVER]**: Decouple reactive logic (Effects/Passives) via an EventBus. Orchestrators (e.g., `BattleManager`) manage subscriptions.
- **IoC (Inversion of Control) [ARCH.RULES.CORE.IOC]**: Implementations using hooks MUST expose them via `get_hooks()`. Only the EventBus orchestrator (e.g., `BattleManager`) handles event registration.
- **Data-Driven [ARCH.RULES.CORE.DATA]**: GameAction templates, CombatStyles, and GameRules are defined in JSON files (`data/`). Use `DataManager` for loading. JSON configurations should be preferred over hard coded implementations.
- **CQRS [ARCH.RULES.CORE.CQRS]**: Use Methods for direct state changes (e.g., `take_damage`); use Events for notifications and event payload modifications ONLY.
- **Modifier Stack Pattern [ARCH.RULES.CORE.MODIFIER]**: Stats are immutable. All dynamic changes (buffs/debuffs) MUST be implemented as `StatModifier` objects in the character's `modifiers` list.
- **Anemic Entities [ARCH.RULES.CORE.ENTITIES]**: Classes in `entities/` are data containers. All complex logic resides in Systems (e.g., `CharacterSystem`) or Actions.
- **Protocols & Typing [ARCH.RULES.CORE.TYPING]**: Use `typing.Protocol` for Dependency Injection. Use `from __future__ import annotations`. Keep typing imports in `TYPE_CHECKING` blocks to avoid circular dependencies.

### Engine Mechanics [ARCH.RULES.ENGINE]
- **Timeline Execution [ARCH.RULES.ENGINE.TIMELINE]:** The turn order is managed by a Min-Heap timeline. Characters are re-scheduled based on `action_cost` after every non-free action.
- **Event Payload Modification [ARCH.RULES.ENGINE.PAYLOAD]:** Listeners in the EventBus receive payload objects (e.g., `AttackLoad`) passed by reference. They MUST modify the object directly to influence calculations.
- **Tick-Based Simulation [ARCH.RULES.ENGINE.TICKS]:** The engine does not use rounds. It uses "Ticks" (discrete units of time). Logic relying on "duration" should count turns or specific events, not wall-clock time.
- **Error Handling (Decision Loop) [ARCH.RULES.ENGINE.DECISION]:** Controllers MUST NOT enter an infinite loop when an action fails `can_execute()`. The Orchestrator MUST implement a safety break (Max Attempts).
- **Targeting Cardinality [ARCH.RULES.ENGINE.TARGETING]:** All `BattleAction` subclasses MUST support a `targets: List[Character]` interface. Single-target actions should use a list with one element.
- **Area Attack Resolution (Master Roll) [ARCH.RULES.ENGINE.AREA_ATTACK]:** For `AttackType.AREA`, the attacker’s roll MUST be performed once (Master Roll) with `target=None` in the `AttackLoad`. This ensures only target-agnostic passives influence the shared roll, followed by individual resolution phases for each target.
**Defensive Payload Auditing [ARCH.RULES.ENGINE.PAYLOAD_TARGET_CHECK]:** Any hook that accesses `AttackLoad.target` MUST perform a null-check if the event it listens to could potentially be emitted during a Master Roll phase or a targetless context.
- **Lifecycle Safety [ARCH.RULES.CORE.EPHEMERAL]**: Ephemeral hooks (valid for 1 action cycle) MUST be wrapped in `try...finally` within the Orchestrator to guarantee unsubscription.

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

## MODULE: Core [ARCH.core]
The `core` module contains the fundamental building blocks of the engine. `[ARCH.RULES.CORE]`

### Enums [ARCH.core.Enums]
Centralized enumerations to ensure type safety and consistency across the engine.
- RollState [ARCH.core.Enums.CLASS:RollState]: Defines dice roll modifiers: `ADVANTAGE` (take highest), `DISADVANTAGE` (take lowest), or `NEUTRAL`.
- ArmorType [ARCH.core.Enums.CLASS:ArmorType]: Categories for physical protection: `ROBE`, `LIGHT`, `HEAVY`.
- WeaponType [ARCH.core.Enums.CLASS:WeaponType]: Categories for offensive equipment, including `GREAT_WEAPON`, `RANGED_WEAPON`, and `MAGICAL_FOCUS`.
- AttributeType [ARCH.core.Enums.CLASS:AttributeType]: The three primary stats: `FIS` (Physical), `HAB` (Skill), `MEN` (Mental).
- StatusEffectType [ARCH.core.Enums.CLASS:StatusEffectType]: Identifiers for active conditions like `ATORDOADO` or `QUEIMADO`.
- AttackType [ARCH.core.Enums.CLASS:AttackType]: Classification of offensive maneuvers: `BASIC_ATTACK`, `SKILL`, `AREA`, `EXTRA_ATTACK`.
- BattleActionType [ARCH.core.Enums.CLASS:BattleActionType]: Action economy categories: `MOVE_ACTION`, `STANDARD_ACTION`, `FREE_ACTION`.
- BattleState [ARCH.core.Enums.CLASS:BattleState]: High-level combat outcomes: `VICTORY`, `DEFEAT`, `DRAW`, `RUNNING`, `ERROR`.

### Structs [ARCH.core.Structs]
Data containers for passing structured information across modules. `[ARCH.RULES.CORE.DATA]`

#### GameRules [ARCH.core.Structs.CLASS:GameRules]
Configuration for global mechanics. Includes `hp_table` and `mp_table` for level scaling, `action_cost_table` for turn delay, and resource multipliers for Focus and Mana (MEN-based). `[ARCH.RULES.CORE.DATA]`

#### RollResult [ARCH.core.Structs.CLASS:RollResult]
Encapsulates a dice roll outcome. Tracks the `final_roll`, individual dice (`roll1`, `roll2` for advantage/disadvantage), and `RollState`. Used by `DiceManager` and the Event Bus.

#### BattleResult [ARCH.core.Structs.CLASS:BattleResult]
Summary of a finished combat. Contains the execution `history` (log of events), lists of `winners` and `losers`, `duration` in ticks, and per-character action statistics.

#### CombatStyle [ARCH.core.Structs.CLASS:CombatStyle]
Archetype definition for a character's fighting method. Defines attack/defense dice (e.g., d20, d12), the `main_stat` for bonuses, and required weapon/armor types. Loaded from `CombatStyles.json`.

#### AttackEffects [ARCH.core.Structs.CLASS:AttackEffects]
Data structure for individual components of an attack (e.g., "Lifesteal", "Stun"). Contains an `id` and a dictionary of `parameters` used by the resolution logic.

#### AttackActionTemplate [ARCH.core.Structs.CLASS:AttackActionTemplate]
Blueprint for complex actions. Combines action/attack types, resource costs (Focus), and a list of `AttackEffects`. Used as the base for instantiating `AttackAction`. `[ARCH.RULES.CORE.DATA]`

### Events [ARCH.core.Events]
Mutable payload objects for the Event Bus, allowing listeners to influence action outcomes. `[ARCH.RULES.ENGINE.PAYLOAD]`

#### ActionLoad [ARCH.core.Events.CLASS:ActionLoad]
Base payload for all battle actions. Tracks the `character` performing the action, an execution `history` (log), and a `success` flag.

#### AttackLoad [ARCH.core.Events.CLASS:AttackLoad]
Specialized payload for offensive resolution. Carries the `target`, `battle_context`, `attack_type`, and states (`attack_state`, `defense_state`). Critical fields for modification: `gda` (Degree of Success), `damage`, and `hit` (boolean).

### Base Classes [ARCH.core.BaseClasses]
Foundational abstract classes and interfaces ensuring modularity and decoupling.

#### GameAction [ARCH.core.BaseClasses.CLASS:GameAction]
Abstract base for the Command Pattern. Defines `can_execute()` and `execute()`. `[ARCH.RULES.CORE.COMMAND]`

#### BattleAction [ARCH.core.BaseClasses.CLASS:BattleAction]
Specialized `GameAction` for combat. Injected with `IBattleContext`, `targets`, and `action_type`. It provides a `target` property for single-target convenience. `[ARCH.RULES.ENGINE.TARGETING]`

#### BattlePassive [ARCH.core.BaseClasses.CLASS:BattlePassive]
Base for reactive logic. Holds a reference to the `owner` and `IBattleContext`. Subclasses MUST implement `get_hooks()` to return event subscriptions. `[ARCH.RULES.CORE.IOC]`

#### IBattleContext [ARCH.core.BaseClasses.PROTOCOL:IBattleContext]
Structural typing (Protocol) for the battle orchestrator. Provides methods for `emit()`, `subscribe()`, `delay_character()`, and accessing character/controller registries. `[ARCH.RULES.CORE.TYPING]`

### Character System [ARCH.core.CharacterSystem]
Stateless domain logic for manipulating `Character` entities. Isolates rule-heavy operations from data containers. `[ARCH.RULES.CORE.ENTITIES]`

- take_damage() [ARCH.core.CharacterSystem.FUNCTION:take_damage]: Direct HP modification with a floor of 0. `[ARCH.RULES.CORE.CQRS]`
- generate_focus() [ARCH.core.CharacterSystem.FUNCTION:generate_focus]: Replenishes floating resources based on the character's `MEN` attribute and `GameRules` limits.
- generate_mana() [ARCH.core.CharacterSystem.FUNCTION:generate_mana]: Replenishes floating resources based on the character's `MEN` attribute and `GameRules` limits.
- spend_focus() [ARCH.core.CharacterSystem.FUNCTION:spend_focus]: Validates and consumes resources for actions; returns success status.
- spend_mana() [ARCH.core.CharacterSystem.FUNCTION:spend_mana]: Validates and consumes resources for actions; returns success status.
- equip_weapon() [ARCH.core.CharacterSystem.FUNCTION:equip_weapon]: Validates item types against `CombatStyle` and updates derived stats like `base_pda` or `max_hp`.
- equip_armor() [ARCH.core.CharacterSystem.FUNCTION:equip_armor]: Validates item types against `CombatStyle` and updates derived stats like `base_pda` or `max_hp`.

### Dice Manager [ARCH.core.DiceManager]
Random number generation and deterministic roll scheduling for combat resolution.

- roll_dice() [ARCH.core.DiceManager.FUNCTION:roll_dice]: Core rolling logic supporting single die or 2d20-style Advantage/Disadvantage. Returns a `RollResult`.
- schedule_result() [ARCH.core.DiceManager.FUNCTION:schedule_result]: Injects a predefined integer into a queue, forcing the next `roll_dice()` call to return that value. Critical for deterministic testing.

### Data Manager [ARCH.core.DataManager]
Central registry for loading and accessing data-driven templates from JSON files. `[ARCH.RULES.CORE.DATA]`

- load_combat_styles() [ARCH.core.DataManager.FUNCTION:load_combat_styles]: Methods to populate the internal registries from JSON data.
- load_game_rules() [ARCH.core.DataManager.FUNCTION:load_game_rules]: Methods to populate the internal registries from JSON data.
- load_characters() [ARCH.core.DataManager.FUNCTION:load_characters]: Methods to populate the internal registries from JSON data.
- load_action_templates() [ARCH.core.DataManager.FUNCTION:load_action_templates]: Methods to populate the internal registries from JSON data.
- get_action_template() [ARCH.core.DataManager.FUNCTION:get_action_template]: Methods to retrieve hydrated templates or entities by their unique IDs.
- get_character() [ARCH.core.DataManager.FUNCTION:get_character]: Methods to retrieve hydrated templates or entities by their unique IDs.
- get_combat_style() [ARCH.core.DataManager.FUNCTION:get_combat_style]: Methods to retrieve hydrated templates or entities by their unique IDs.

### Modifiers [ARCH.core.Modifiers]
Implementation of the Modifier Stack Pattern for dynamic stat calculation. `[ARCH.RULES.CORE.MODIFIER]`

#### StatModifier [ARCH.core.Modifiers.CLASS:StatModifier]
Base for all stat changes. Tracks `stat_name`, `value`, and `source` with a unique UUID.

#### EphemeralModifier [ARCH.core.Modifiers.CLASS:EphemeralModifier]
Short-term changes intended to be cleared after combat or specific effect durations.

#### PersistentModifier [ARCH.core.Modifiers.CLASS:PersistentModifier]
Long-term changes typically originating from equipment, traits, or permanent conditions.

## MODULE: Battle [ARCH.battle]
The `battle` module handles combat orchestration, action resolution, and reactive logic.

### Battle Manager [ARCH.battle.BattleManager]
The central orchestrator of the combat engine, managing time and event propagation. `[ARCH.RULES.CORE.OBSERVER]`

#### BattleManager [ARCH.battle.BattleManager.CLASS:BattleManager]
Manages the `timeline` (Min-Heap), the `listeners` registry (Event Bus), and the character lifecycle. Tracks `current_tick` and maintains a `graveyard`.

- run_battle() [ARCH.battle.BattleManager.METHOD:BattleManager.run_battle]: The main engine loop. Executes characters' turns in tick order, managing the "Free Action -> Move/Standard Action" cycle and ensuring `resolve_deaths()` and `judge.rule()` are checked. `[ARCH.RULES.ENGINE.DECISION]`
- emit() [ARCH.battle.BattleManager.METHOD:BattleManager.emit]: Triggers events on the Event Bus. Listeners modify the `ActionLoad` or `AttackLoad` payload objects directly. `[ARCH.RULES.ENGINE.PAYLOAD]`
- subscribe() [ARCH.battle.BattleManager.METHOD:BattleManager.subscribe]: Manages dynamic listener registration, used by Passives and Status Effects. `[ARCH.RULES.CORE.EPHEMERAL]`
- unsubscribe() [ARCH.battle.BattleManager.METHOD:BattleManager.unsubscribe]: Manages dynamic listener registration, used by Passives and Status Effects.
- delay_character() [ARCH.battle.BattleManager.METHOD:BattleManager.delay_character]: Pushes a character's next turn further into the future on the timeline (e.g., due to Stun). `[ARCH.RULES.ENGINE.TIMELINE]`
- resolve_deaths() [ARCH.battle.BattleManager.METHOD:BattleManager.resolve_deaths]: Identifies characters at 0 HP, removes them from active play, and moves them to the `graveyard`.

### Battle Actions [ARCH.battle.BattleActions]
Implementations of the Command Pattern for combat maneuvers. `[ARCH.RULES.CORE.COMMAND]`

#### AttackAction [ARCH.battle.BattleActions.CLASS:AttackAction]
Generic data-driven offensive resolution. Implements the complete attack flow (Roll -> Hit Check -> GdA -> Damage -> Application). Supports `AttackType.AREA` with a Master Roll. `[ARCH.RULES.ENGINE.TARGETING]`, `[ARCH.RULES.ENGINE.AREA_ATTACK]`

#### GenerateManaAction [ARCH.battle.BattleActions.CLASS:GenerateManaAction]
A Move Action that manifest mana from the daily reserve into `floating_mp`.

#### GenerateFocusAction [ARCH.battle.BattleActions.CLASS:GenerateFocusAction]
A Move Action that replenishes the `floating_focus` pool.

#### TogglePosturaDefensiva [ARCH.battle.BattleActions.CLASS:TogglePosturaDefensiva]
A Free Action that interacts with the `PosturaDefensiva` passive to toggle combat stances.

### Battle Passives [ARCH.battle.BattlePassives]
Reactive logic and hooks for character-specific traits and abilities. `[ARCH.RULES.CORE.IOC]`

#### PosturaDefensiva [ARCH.battle.BattlePassives.CLASS:PosturaDefensiva]
A stateful stance that modifies the owner's dice pools and applies persistent `EphemeralModifier` penalties to enemies it has previously hit. `[ARCH.RULES.ENGINE.PAYLOAD_TARGET_CHECK]`

#### GracaDoDuelista [ARCH.battle.BattlePassives.CLASS:GracaDoDuelista]
Grants GdA bonuses on `on_gda_modify` and provides an optional defensive reaction (Evasão) that uses `choose_reaction()`.

#### Combo [ARCH.battle.BattlePassives.CLASS:Combo]
Monitors `on_attack_end` to trigger recursive `AttackAction` executions (Extra Attacks) upon successful hits.

#### ForçaBruta [ARCH.battle.BattlePassives.CLASS:ForçaBruta]
A simple multiplier applied during the `on_gda_modify` phase.

#### MãosPesadas [ARCH.battle.BattlePassives.CLASS:MãosPesadas]
Triggers the application of `Atordoado` status if GdA exceeds a threshold during hit resolution.

### Judges [ARCH.battle.Judges]
Victory and defeat condition logic, called at the start of every turn and after every standard action.

#### BattleJudge [ARCH.battle.Judges.CLASS:BattleJudge]
Evaluates the presence of living characters in each team to determine the `BattleState`.

### Status Effects [ARCH.battle.StatusEffects]
Temporary modifiers and behavioral changes with a turn-based duration. `[ARCH.RULES.CORE.MODIFIER]`

#### StatusEffect [ARCH.battle.StatusEffects.CLASS:StatusEffect]
Abstract base that extends `BattlePassive`. Implements `apply()` and `remove()` logic, including `EphemeralModifier` management.

#### Atordoado [ARCH.battle.StatusEffects.CLASS:Atordoado]
Stun effect. Upon application, it immediately calls `delay_character()`. It subscribes to `on_turn_start` to decrement duration or expire.

## MODULE: Entities [ARCH.entities]
The `entities` module contains data-only classes representing game objects. `[ARCH.RULES.CORE.ENTITIES]`

### Characters [ARCH.entities.Characters]
The primary data container for actors, designed as an anemic entity with a reactive modifier stack. `[ARCH.RULES.CORE.ENTITIES]`

#### Character [ARCH.entities.Characters.CLASS:Character]
Tracks core state: `current_hp`, `current_mp`, `floating_mp`, and `floating_focus`. Maintains references to `CombatStyle`, `Weapon`, and `Armor`.

- get_stat_total() [ARCH.entities.Characters.METHOD:Character.get_stat_total]: Computes real-time values for stats like `rank`, `bda`, `bdd`, `pre`, `grd`, `pda`, and `mda`. This ensures stats are never mutated directly. `[ARCH.RULES.CORE.MODIFIER]`

### Items [ARCH.entities.Items]
Data structures for equipment, used by `CharacterSystem` to populate character stats.

#### Weapon [ARCH.entities.Items.CLASS:Weapon]
Dataclass defining offensive traits. Includes `db` (Damage Bonus), `mda` (Degree of Success multiplier), and `type` (for compatibility checks).

#### Armor [ARCH.entities.Items.CLASS:Armor]
Dataclass defining defensive traits. Includes `hp_bonus` and `type`.

## MODULE: Controllers [ARCH.controllers]
The `controllers` module implements the "Decision Loop" for characters, separating AI/Player logic from the engine. `[ARCH.RULES.CORE.MVC]`

### Character Controller [ARCH.controllers.CharacterController]
The "Decision Loop" interface that separates character behavior (AI or Player) from engine mechanics. `[ARCH.RULES.CORE.MVC]`

#### CharacterController [ARCH.controllers.CharacterController.CLASS:CharacterController]
Abstract base class. Defines the interface for tactical decision-making.

- choose_action() [ARCH.controllers.CharacterController.METHOD:CharacterController.choose_action]: Called at the start of a turn. Analyzes the `IBattleContext` and returns a `BattleAction` command. Supports re-decision if the previous action failed validation (via `action_load`). `[ARCH.RULES.ENGINE.DECISION]`
- choose_reaction() [ARCH.controllers.CharacterController.METHOD:CharacterController.choose_reaction]: Called during action resolution (e.g., `on_defense_reaction`). Allows the controller to opt-in to conditional effects (like Evasion) based on the current `AttackLoad`.

#### PvP1v1Controller [ARCH.controllers.CharacterController.CLASS:PvP1v1Controller]
Reference implementation for automated combat. Prioritizes Skills over Basic Attacks if Focus is available.

## MODULE: Data [ARCH.data]
The `data` module stores external JSON definitions that drive engine behavior and character scaling. `[ARCH.RULES.CORE.DATA]`

### Action Definitions [ARCH.data.AttackActions]
Blueprints for all combat maneuvers. Defines `focus_cost`, `action_type`, `attack_type` (e.g., AREA), and a list of `AttackEffects` (e.g., "add_gda").

### Character Templates [ARCH.data.Characters]
Hydration templates for characters. Defines base attributes (`FIS`, `HAB`, `MEN`), starting `Weapon` and `Armor`, and initial lists of `Abilities` and `Passives`.

### Combat Styles [ARCH.data.CombatStyles]
Archetype definitions that govern dice pool sizes (`atq_die`, `def_die`), the `main_stat` for damage calculation, and equipment requirements (`ArmorType`, `WeaponType`).

### Game Rules [ARCH.data.Rules]
Global constants and progression tables. Defines `limite_foco`/`limite_mana` multipliers and scaling tables for HP, MP, and `action_cost` based on attribute scores.

## MODULE: Utilities [ARCH.XXXXX]
The `utilities` module provides cross-cutting tools for documentation management, system operations, and agent assistance.

### Reference Manager [ARCH.utilities.ref_manager]
The central tool for targeted documentation extraction, recursive dependency resolution, and automated documentation maintenance.

- PATH_MAPPING [ARCH.utilities.ref_manager.GLOBAL:PATH_MAPPING]: Configuration dictionary mapping tag prefixes (e.g., `ARCH.`, `GDD.`, `WORKFLOWS.`) to their source markdown files, ensuring centralized path management.
- resolve_tag() [ARCH.utilities.ref_manager.FUNCTION:resolve_tag]: The primary recursive solver. It fetches a tag's content and iteratively resolves all nested "DEPENDS:" tags. It maintains a `resolved_tags` registry to prevent circular dependencies. When a tag is found in a header (session), all other tags within that session are automatically marked as resolved to ensure clean extraction.
- extract_section() [ARCH.utilities.ref_manager.FUNCTION:extract_section]: The parsing engine. It searches for a tag (prioritizing headers) and extracts the corresponding block of text. If the tag is found in a header, it captures all content until a header of equal or higher level is encountered.
- update_section() [ARCH.utilities.ref_manager.FUNCTION:update_section]: The modification engine. Locates a tag and replaces its entire section (if a header) or line with new content. Supports reading content from a string or an external file via `--from-file`.
- create_section() [ARCH.utilities.ref_manager.FUNCTION:create_section]: The creation engine. Implements **Smart Placement** and **Fail-Fast Validation**: it prevents duplicate tags and ensures hierarchical integrity. New tags are placed after their parent or last sibling based on prefix matching. It fails if a parent tag is missing (returning `"Error: Parent tag [prefix] not found."` for 3+ component tags) or if the file identifier is missing (for 2 component tags), ensuring documentation structure is maintained. Supports manual positioning via `--after [TAG]`.
- get_path_for_tag() [ARCH.utilities.ref_manager.FUNCTION:get_path_for_tag]: A utility that normalizes tags and determines the correct source file path by matching the tag's prefix against the `PATH_MAPPING`.

#### CLI Usage [ARCH.utilities.ref_manager.CLI]
- CLI Interface: A command-line wrapper that allows agents to request multiple tags or perform documentation maintenance.
  - **Extraction:** `python3 utilities/ref_manager.py [TAG1] [TAG2]`
  - **Update:** `python3 utilities/ref_manager.py --update [TAG] "Content" [--from-file path]`
  - **Creation:** `python3 utilities/ref_manager.py --create [NEW_TAG] "Content" [--after TAG]`
  - **Deletion:** `python3 utilities/ref_manager.py --delete [TAG]`

## Test Quality Standards [ARCH.TEST_QUALITY]

- **Behavior over Implementation [ARCH.TEST_QUALITY.TEST_BEHAVIOR]:** Tests MUST verify the outcome (e.g., final HP, logs, state changes) rather than internal implementation details (e.g., checking specific list indices or private method calls).
- **Controlled Mocking [ARCH.TEST_QUALITY.MOCKING]:** Use real instances for domain logic (Entities, Systems). Mock ONLY system boundaries (I/O, UI) or to enforce determinism. Use `DiceManager.schedule_result()` for simulating dice rolls.
- **Entity Factory [ARCH.TEST_QUALITY.ENTITY_FACTORY]:** Use `tests.utils.entity_factory` when instantiating entities for tests. Use `DataManager` only for integration tests.
- **Data Integrity [ARCH.TEST_QUALITY.DATA_INTEGRITY]:** For integration tests using `DataManager`, use `tests.utils.json_integrity_checker.get_json_keys()` to dynamically iterate over and verify all IDs in game data. This ensures tests remain decoupled from specific balance values while guaranteeing hydration logic works for all defined content.
- **Decoupling [ARCH.TEST_QUALITY.DECOUPLING]:** Ensure tests do not break upon internal refactors if the public behavior remains unchanged.
- **Invariants [ARCH.TEST_QUALITY.INVARIANTS]:** Assert that system state remains valid according to ARCH rules (e.g., stats calculated via the Modifier Stack `[ARCH.RULES.CORE.MODIFIER]`, no negative HP).
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
- **Steps**: List of completed steps.
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
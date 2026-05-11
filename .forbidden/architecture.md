# Project Documentation [ARCH.GLOBAL]

This document serves as the primary technical reference for the **Fábrica de Lendas** RPG Engine. It combines high-level architectural rules with detailed module documentation to guide both human developers and AI agents.

## Project Vision [ARCH.VISION]
**Fábrica de Lendas** is a data-driven, modular RPG engine designed for tactical combat simulation. It follows a strict **Game-MVC** pattern, where rules and logic are  decoupled from presentation. The engine uses an **Event-Driven** architecture to handle complex interactions (Passives, Effects) through an Event Bus.

## Architectural Guardrails [ARCH.RULES]

These rules are context-exclusive and MUST be referenced in `MISSION_LOG.md` when relevant to the task.

### Core Patterns [ARCH.RULES.CORE]
- **Game-MVC [ARCH.RULES.CORE.MVC]:** **Models:** Files in `core/`, `battle/`, `entities/`, `data/`. Represents the game world, rules and entities; **Controllers:** Files in `controllers/`. Scripts that instantiates and orquestrates models; **Views**: Presentation layer (Logs/UI) is decoupled from the engine.
- **Command Pattern [ARCH.RULES.CORE.COMMAND]:** All actions (Skills, Basic Attacks, Movements) MUST inherit from `GameAction` and implement `can_execute()` and `execute()`. The `execute()` function returns a `ActionLoad` with a execution history.
- **Observer/EventBus [ARCH.RULES.CORE.OBSERVER]:** Decouples reactive logic (Actions/Passives/Status Effects) from core execution via an EventBus. Orchestrators manage "hooks" (listener functions) that are registered to specific battle events. Parameters of the action are passed and modified by the hooks through an `ActionLoad` object, including `ActionLoad.history`.
- **IoC (Inversion of Control) [ARCH.RULES.CORE.IOC]:** Reactive components (Passives/Status/Actions) do not register themselves. They MUST expose their listener functions via `get_hooks()`, returning a mapping of event keys to callbacks. The `BattleManager` remains the sole authority for subscribing and unsubscribing these hooks.
- **Data-Driven [ARCH.RULES.CORE.DATA]:** GameAction templates, CombatStyles, and GameRules are defined in JSON files (`data/`). Use `DataManager` for loading. JSON configurations should be preferred over hard coded implementations.
- **Modifier Stack Pattern [ARCH.RULES.CORE.MODIFIER]:** Stats are immutable. All dynamic changes (buffs/debuffs) MUST be implemented as `StatModifier` objects in the character's `modifiers` list.
- **Event Stream History [ARCH.RULES.CORE.HISTORY]:** Decouples the Engine (Model) from the presentation (View). The `history` field in `ActionLoad` payloads MUST contain only pipe-delimited structured tags (`TAG|PARAM...`). Use `HistoryEmitter` to generate standard tags. Narrative strings and localization are strictly prohibited within the Model layer; they are the exclusive responsibility of the View.
- **Anemic Entities [ARCH.RULES.CORE.ENTITIES]:** Classes in `entities/` are data containers. All complex logic resides in Systems (e.g., `CharacterSystem`) or Actions.
- **Protocols & Typing [ARCH.RULES.CORE.TYPING]:** Use `typing.Protocol` for Dependency Injection. Use `from __future__ import annotations`. Keep typing imports in `TYPE_CHECKING` blocks to avoid circular dependencies.

### Battle Engine Mechanics [ARCH.RULES.BATTLE]
- **Timeline Execution [ARCH.RULES.BATTLE.TIMELINE]:** The turn order is managed by a Min-Heap timeline. Characters are re-scheduled based on `action_cost` after every non-free action.
- **Tick-Based Simulation [ARCH.RULES.BATTLE.TICKS]:** The engine does not use rounds. It uses "Ticks" (discrete units of time). Logic relying on "duration" should count turns or specific events, not wall-clock time.
- **Error Handling (Decision Loop) [ARCH.RULES.BATTLE.DECISION]:** `CharacterController` MUST NOT enter an infinite loop when an action fails `can_execute()`. The `BattleManager` MUST implement a safety break (Max Attempts).
- **Targeting Cardinality [ARCH.RULES.BATTLE.TARGETING]:** All `BattleAction` subclasses MUST support a `targets: List[Character]` interface. Single-target actions should use a list with one element.
- **Area Attack Resolution (Master Roll) [ARCH.RULES.BATTLE.AREA_ATTACK]:** For `AttackType.AREA`, the attacker’s roll MUST be performed once (Master Roll) with `target=None` in the `AttackLoad`. This ensures only target-agnostic passives influence the shared roll, followed by individual resolution phases for each target.
- **Defensive Payload Auditing [ARCH.RULES.BATTLE.PAYLOAD_TARGET_CHECK]:** Any hook that accesses `AttackLoad.target` MUST perform a null-check if the event it listens to could potentially be emitted during a Master Roll phase or a targetless context..
- **Action-Scoped Interceptors [ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]:** Hooks that exist only for the duration of a single action. `BattleManager` MUST execute actions within a `try...finally` block to guarantee these hooks are unsubscribed, allowing actions (like `AttackAction`) to modify their own resolution steps via the event bus.
- **Status Effects Hooks [ARCH.RULES.BATTLE.STATUS_HOOKS]:** `BattleManager` subscribes hooks from any `StatusEffect`when `add_status_effect()` is called. The effect must use hooks to manage it's duration counter and call `remove_status_effect()` when the effect ends. This will remove the rooks from the event bus. 
- **Passive Abilities Hooks [ARCH.RULES.BATTLE.PASSIVE_HOOKS]:** Passive abilities are registered in `Character.passive_abilities` as a list of strings used by `BattleManager` to find the implementations when `BattleManager.add_character()` is called. `BattleManager` uses `BattlePassive.get_hooks()` to receive hooks, register them, and keep the references in `BattleManager.active_passives`. Passive hooks are removed only when `remove_character`is called.  
- **Lazy Death Resolution [ARCH.RULES.BATTLE.DEATH_RESOLUTION]:** Characters aren't removed from the timeline when they die. The `BattleManager.get_next_actor()` function should remove and ignore dead characters. The function `BattleManager.resolve_deaths()` should be called at the beginning and end of a character turn to remove dead characters from battle.
- **Data-Driven Attacks [ARCH.RULES.BATTLE.ATTACK_DATA]:** AttackAction constructor receives an AttackAction template. This template includes list of effects to modify the AttackAction resolution. Each effect have an id and a list of parameters. AttackAction uses the effects ids to find and call hook builders that return returns a tuple {"signal", hook_function}. BattleManager handles those hooks, following [ARCH.RULES.CORE.IOC] and [ARCH.RULES.BATTLE.EPHEMERAL_HOOKS].

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
Comprehensive description of the foundational entities, systems, data structures, and interfaces that comprise the core logic of the engine. It dictates how game data is loaded, how randomness is resolved, how entities modify each other, and defines the base abstractions for combat.

#### Enums.py [ARCH.DOC.core.Enums]
Defines the fundamental enumerations used throughout the system for typing and categorizing entities, attacks, and battle states.

##### RollState [ARCH.DOC.core.Enums.RollState]
[DEPENDS: GDD.COMBAT.FLOW.ADV, GDD.COMBAT.FLOW.DSV]
Enum representing advantage mechanics for dice rolls.

- `ADVANTAGE: str` [ARCH.DOC.core.Enums.RollState.ADVANTAGE]: Roll twice, take higher result.
- `DISADVANTAGE: str` [ARCH.DOC.core.Enums.RollState.DISADVANTAGE]: Roll twice, take lower result.
- `NEUTRAL: str` [ARCH.DOC.core.Enums.RollState.NEUTRAL]: Standard single roll execution.

##### ArmorType [ARCH.DOC.core.Enums.ArmorType]
[DEPENDS: GDD.EQUIP.TYPES.ARMORS]
Enum representing armor weight categories.

- `ROBE: str` [ARCH.DOC.core.Enums.ArmorType.ROBE]: Magic-focused attire with zero weight penalty.
- `LIGHT: str` [ARCH.DOC.core.Enums.ArmorType.LIGHT]: Balanced leather/chain protection.
- `HEAVY: str` [ARCH.DOC.core.Enums.ArmorType.HEAVY]: Plate or dense protection with significant mobility impact.

##### WeaponType [ARCH.DOC.core.Enums.WeaponType]
[DEPENDS: GDD.EQUIP.TYPES.WEAPONS]
Enum representing weapon classifications.

- `GREAT_WEAPON: str` [ARCH.DOC.core.Enums.WeaponType.GREAT_WEAPON]: Heavy two-handed weapons.
- `MEDIUM_WEAPON: str` [ARCH.DOC.core.Enums.WeaponType.MEDIUM_WEAPON]: Standard one-handed weapons.
- `LIGHT_WEAPON: str` [ARCH.DOC.core.Enums.WeaponType.LIGHT_WEAPON]: Agile weapons optimized for speed.
- `DOUBLE_WEAPON: str` [ARCH.DOC.core.Enums.WeaponType.DOUBLE_WEAPON]: Exotic weapons with two striking ends.
- `WEAPON_AND_SHIELD: str` [ARCH.DOC.core.Enums.WeaponType.WEAPON_AND_SHIELD]: Combined offensive and defensive setup.
- `RANGED_WEAPON: str` [ARCH.DOC.core.Enums.WeaponType.RANGED_WEAPON]: Projectile or thrown weapons.
- `MAGICAL_FOCUS: str` [ARCH.DOC.core.Enums.WeaponType.MAGICAL_FOCUS]: Implements used for spellcasting.

##### AttributeType [ARCH.DOC.core.Enums.AttributeType]
[DEPENDS: GDD.CORE.ATTR]
Enum for base character attributes.

- `FIS: str` [ARCH.DOC.core.Enums.AttributeType.FIS]: Physical strength and constitution.
- `HAB: str` [ARCH.DOC.core.Enums.AttributeType.HAB]: Agility, precision, and speed.
- `MEN: str` [ARCH.DOC.core.Enums.AttributeType.MEN]: Intelligence, willpower, and magical affinity.

##### StatusEffectType [ARCH.DOC.core.Enums.StatusEffectType]
[DEPENDS: GDD.STATUS]
Enum for names of standard status effects.

- `ATORDOADO: str` [ARCH.DOC.core.Enums.StatusEffectType.ATORDOADO]: Stunned state, restricting actions.
- `DESEQUILIBRADO: str` [ARCH.DOC.core.Enums.StatusEffectType.DESEQUILIBRADO]: Unbalanced state, penalizing defenses.
- `DERRUBADO: str` [ARCH.DOC.core.Enums.StatusEffectType.DERRUBADO]: Prone state, requiring movement to recover.

##### AttackType [ARCH.DOC.core.Enums.AttackType]
Enum classifying offensive maneuvers.

- `BASIC_ATTACK: str` [ARCH.DOC.core.Enums.AttackType.BASIC_ATTACK]: Standard weapon strike.
- `SKILL: str` [ARCH.DOC.core.Enums.AttackType.SKILL]: Specialized ability execution.
- `EXTRA_ATTACK: str` [ARCH.DOC.core.Enums.AttackType.EXTRA_ATTACK]: Additional strike within a turn.
- `AREA: str` [ARCH.DOC.core.Enums.AttackType.AREA]: Effect targeting multiple coordinates.

##### BattleActionType [ARCH.DOC.core.Enums.BattleActionType]
[DEPENDS: GDD.CORE.TIME.ACTION_TYPES]
Enum for action economy categories.

- `MOVE_ACTION: str` [ARCH.DOC.core.Enums.BattleActionType.MOVE_ACTION]: Action used for navigation.
- `STANDARD_ACTION: str` [ARCH.DOC.core.Enums.BattleActionType.STANDARD_ACTION]: Primary action (attack, cast, etc.).
- `FREE_ACTION: str` [ARCH.DOC.core.Enums.BattleActionType.FREE_ACTION]: Minor action with no tick cost.

##### BattleState [ARCH.DOC.core.Enums.BattleState]
Enum for high-level combat outcomes.

- `VICTORY: str` [ARCH.DOC.core.Enums.BattleState.VICTORY]: Player/Protagonists won the engagement.
- `DEFEAT: str` [ARCH.DOC.core.Enums.BattleState.DEFEAT]: Player/Protagonists lost the engagement.
- `DRAW: str` [ARCH.DOC.core.Enums.BattleState.DRAW]: Engagement ended with no clear victor.
- `RUNNING: str` [ARCH.DOC.core.Enums.BattleState.RUNNING]: Combat simulation is currently active.
- `ERROR: str` [ARCH.DOC.core.Enums.BattleState.ERROR]: Simulation encountered a critical logic failure.

#### Structs.py [ARCH.DOC.core.Structs]
Provides pure data container structures (DTOs) for passing complex configuration and state across domains.

##### GameRules [ARCH.DOC.core.Structs.GameRules]
[DEPENDS: GDD.CORE.PROG, ARCH.RULES.CORE.DATA]
Configuration for global mechanics and progression tables.

- Constructor [ARCH.DOC.core.Structs.GameRules.__init__]: `__init__(hp_table: Dict[str, int], mp_table: Dict[str, int], action_cost_table: Dict[str, int], limite_foco: int, limite_mana: int)`
- `hp_table: Dict[str, int]` [ARCH.DOC.core.Structs.GameRules.hp_table]: HP progression table. FIS attribute determines HP value.
- `mp_table: Dict[str, int]` [ARCH.DOC.core.Structs.GameRules.mp_table]: MP progression table. MEN attribute determines MP value.
- `action_cost_table: Dict[str, int]` [ARCH.DOC.core.Structs.GameRules.action_cost_table]: Action Cost progression table. HAB attribute determines action cost value.
- `limite_foco: int` [ARCH.DOC.core.Structs.GameRules.limite_foco]: Determines how much foco a character can hold at max. The limit is `limite_foco` * MEN.
- `limite_mana: int` [ARCH.DOC.core.Structs.GameRules.limite_mana]: Determines how much floating mana a character can hold at max. The limit is `limite_mana` * MEN.

##### RollResult [ARCH.DOC.core.Structs.RollResult]
[DEPENDS: ARCH.DOC.core.Enums.RollState]
Encapsulates a dice roll outcome. Used by DiceManager and the Event Bus.

- Constructor [ARCH.DOC.core.Structs.RollResult.__init__]: `__init__(final_roll: int, roll1: int, roll2: int | None = None, rollstate: RollState = RollState.NEUTRAL, scheduled: bool = False)`
- `final_roll: int` [ARCH.DOC.core.Structs.RollResult.final_roll]: Final roll result that must be used by the system.
- `roll1: int` [ARCH.DOC.core.Structs.RollResult.roll1]: The result of the first die rolled.
- `roll2: int | None` [ARCH.DOC.core.Structs.RollResult.roll2]: Second roll in case of Advantage/Disadvantage; otherwise None.
- `rollstate: RollState` [ARCH.DOC.core.Structs.RollResult.rollstate]: Indicates the state of the roll (ADVANTAGE, DISADVANTAGE, NEUTRAL).
- `scheduled: bool` [ARCH.DOC.core.Structs.RollResult.scheduled]: True if the result was retrieved from a pre-determined queue.

##### BattleResult [ARCH.DOC.core.Structs.BattleResult]
[DEPENDS: ARCH.DOC.core.BaseClasses.IBattleJudge, ARCH.DOC.entities.Characters.Character, ARCH.RULES.CORE.HISTORY]
Summary of a finished combat engagement, including outcome and event history.

- Constructor [ARCH.DOC.core.Structs.BattleResult.__init__]: `__init__(history: List[str] = [], winners: List[Character] = [], losers: List[Character] = [], duration: int = 0, action_per_character: Dict[str, int] = {})`
- `history: List[str]` [ARCH.DOC.core.Structs.BattleResult.history]: Chronological record of battle events. `[ARCH.RULES.CORE.HISTORY]`
- `winners: List[Character]` [ARCH.DOC.core.Structs.BattleResult.winners]: Characters belonging to the winning side.
- `losers: List[Character]` [ARCH.DOC.core.Structs.BattleResult.losers]: Characters belonging to the losing side.
- `duration: int` [ARCH.DOC.core.Structs.BattleResult.duration]: Total number of actions processed during the battle.
- `action_per_character: Dict[str, int]` [ARCH.DOC.core.Structs.BattleResult.action_per_character]: Action count tracker indexed by character ID.

##### CombatStyle [ARCH.DOC.core.Structs.CombatStyle]
[DEPENDS: GDD.STYLES.DEFINITION, ARCH.DOC.core.Enums.ArmorType, ARCH.DOC.core.Enums.WeaponType, ARCH.DOC.core.Enums.AttributeType, ARCH.RULES.CORE.DATA]
Archetype definition for a character"s fighting method, loaded from static data.

- Constructor [ARCH.DOC.core.Structs.CombatStyle.__init__]: `__init__(name: str, atq_die: int, def_die: int, main_stat: AttributeType, armor_type: ArmorType, weapon_type: WeaponType)`
- `name: str` [ARCH.DOC.core.Structs.CombatStyle.name]: Unique identifier for the combat style.
- `atq_die: int` [ARCH.DOC.core.Structs.CombatStyle.atq_die]: Die size used for attack rolls.
- `def_die: int` [ARCH.DOC.core.Structs.CombatStyle.def_die]: Die size used for defense rolls.
- `main_stat: AttributeType` [ARCH.DOC.core.Structs.CombatStyle.main_stat]: Core attribute used for style calculations.
- `armor_type: ArmorType` [ARCH.DOC.core.Structs.CombatStyle.armor_type]: Permissible armor category for this style.
- `weapon_type: WeaponType` [ARCH.DOC.core.Structs.CombatStyle.weapon_type]: Permissible weapon category for this style.

##### AttackEffects [ARCH.DOC.core.Structs.AttackEffects]
[DEPENDS: ARCH.RULES.CORE.DATA, ARCH.RULES.BATTLE.ATTACK_DATA]
Data structure for individual components and modifiers of an attack.

- Constructor [ARCH.DOC.core.Structs.AttackEffects.__init__]: `__init__(id: str, parameters: Dict[str, Any])`
- `id: str` [ARCH.DOC.core.Structs.AttackEffects.id]: Identifier used to map the effect to internal logic builders.
- `parameters: Dict[str, Any]` [ARCH.DOC.core.Structs.AttackEffects.parameters]: Configuration parameters for the specific effect.

##### AttackActionTemplate [ARCH.DOC.core.Structs.AttackActionTemplate]
[DEPENDS: ARCH.DOC.core.Structs.AttackEffects, ARCH.DOC.core.Enums.AttackType, ARCH.DOC.core.Enums.BattleActionType, ARCH.RULES.BATTLE.ATTACK_DATA]
Blueprint for complex actions, defining costs, types, and associated effects.

- Constructor [ARCH.DOC.core.Structs.AttackActionTemplate.__init__]: `__init__(nome: str, action_type: type["BattleActionType"], attack_type: type["AttackType"], focus_cost: int, effects: List[AttackEffects] = [])`
- `nome: str` [ARCH.DOC.core.Structs.AttackActionTemplate.nome]: Display name of the action.
- `action_type: type["BattleActionType"]` [ARCH.DOC.core.Structs.AttackActionTemplate.action_type]: Economy category used to calculate tick cost.
- `attack_type: type["AttackType"]` [ARCH.DOC.core.Structs.AttackActionTemplate.attack_type]: Classification for rule-specific interactions.
- `focus_cost: int` [ARCH.DOC.core.Structs.AttackActionTemplate.focus_cost]: Focus points required to execute the action.
- `effects: List[AttackEffects]` [ARCH.DOC.core.Structs.AttackActionTemplate.effects]: Collection of effects applied during execution.

#### Events.py [ARCH.DOC.core.Events]
Defines payload objects used by the Event Bus to track history and state mutation during actions. 

##### ActionLoad [ARCH.DOC.core.Events.ActionLoad]
[DEPENDS: ARCH.RULES.CORE.COMMAND, ARCH.RULES.CORE.HISTORY, ARCH.DOC.entities.Characters.Character]
Base payload for all battle actions, carrying state and execution history through the Event Bus.

- Constructor [ARCH.DOC.core.Events.ActionLoad.__init__]: `__init__(*, character: "Character", history: List[str] = [], success: bool = True)`
- `character: "Character"` [ARCH.DOC.core.Events.ActionLoad.character]: Character executing the action.
- `history: List[str]` [ARCH.DOC.core.Events.ActionLoad.history]: Chronological log of structured strings describing action results. `[ARCH.RULES.CORE.HISTORY]`
- `success: bool` [ARCH.DOC.core.Events.ActionLoad.success]: Indicates if the system execution completed without logic errors.

###### add_event [ARCH.DOC.core.Events.ActionLoad.add_event]
`add_event(tag: str, *params: any) -> None`
Method description: Standardizes event insertion into history by formatting parameters into a pipe-delimited string.
1. Joins the `tag` and stringified `params` using the `|` character.
2. Appends the resulting string to the `history` list.

##### AttackLoad [ARCH.DOC.core.Events.AttackLoad]
[DEPENDS: ARCH.DOC.core.Events.ActionLoad, ARCH.RULES.CORE.OBSERVER, ARCH.DOC.core.Enums.RollState, ARCH.DOC.core.Enums.AttackType, ARCH.RULES.BATTLE.AREA_ATTACK, GDD.COMBAT.FLOW.GDA]
Specialized payload for offensive resolution, inheriting from `ActionLoad` to add combat-specific metrics.

- Constructor [ARCH.DOC.core.Events.AttackLoad.__init__]: `__init__(*, character: "Character", history: List[str] = [], success: bool = True, target: Character | None = None, attack_type: AttackType, attack_state: RollState, defense_state: RollState, gda: int = 0, damage: int = 0, hit: bool = False)`
- `target: Character | None` [ARCH.DOC.core.Events.AttackLoad.target]: The recipient of the attack.
- `attack_type: AttackType` [ARCH.DOC.core.Events.AttackLoad.attack_type]: Categorization of the attack (Basic, Skill, etc.).
- `attack_state: RollState` [ARCH.DOC.core.Events.AttackLoad.attack_state]: Advantage state applied to the attacker.
- `defense_state: RollState` [ARCH.DOC.core.Events.AttackLoad.defense_state]: Advantage state applied to the defender.
- `gda: int` [ARCH.DOC.core.Events.AttackLoad.gda]: Degree of Success (GdA) used for final damage resolution.
- `damage: int` [ARCH.DOC.core.Events.AttackLoad.damage]: Bonus damage or reduction value added during calculation.
- `hit: bool` [ARCH.DOC.core.Events.AttackLoad.hit]: Flag indicating if the attack successfully connected with the target.

##### HistoryEmitter [ARCH.DOC.core.Events.HistoryEmitter]
[DEPENDS: ARCH.RULES.CORE.HISTORY]
Static utility class for generating standardized, machine-readable event tags for the battle history stream.

###### exec [ARCH.DOC.core.Events.HistoryEmitter.exec]
`exec(action_id: str, actor_id: str) -> str`
Method description: Returns a formatted `EXEC` event string indicating an action has started.

###### roll [ARCH.DOC.core.Events.HistoryEmitter.roll]
`roll(type: str, value: int, die_size: int, actor_id: str) -> str`
Method description: Returns a formatted `ROLL` event string representing a dice result.

###### mod [ARCH.DOC.core.Events.HistoryEmitter.mod]
`mod(source_id: str, value: int, target_id: str) -> str`
Method description: Returns a formatted `MOD` event string for value modifications.

###### hit [ARCH.DOC.core.Events.HistoryEmitter.hit]
`hit(target_id: str) -> str`
Method description: Returns a formatted `HIT` event string for successful attacks.

###### miss [ARCH.DOC.core.Events.HistoryEmitter.miss]
`miss(target_id: str) -> str`
Method description: Returns a formatted `MISS` event string for failed attacks.

###### dmg [ARCH.DOC.core.Events.HistoryEmitter.dmg]
`dmg(target_id: str, amount: int, type: str) -> str`
Method description: Returns a formatted `DMG` event string for damage instances.

###### hp [ARCH.DOC.core.Events.HistoryEmitter.hp]
`hp(entity_id: str, delta: int, current: int) -> str`
Method description: Returns a formatted `HP` event string for health changes.

###### focus [ARCH.DOC.core.Events.HistoryEmitter.focus]
`focus(entity_id: str, delta: int, current: int) -> str`
Method description: Returns a formatted `FOCUS` event string for focus changes.

###### mana_f [ARCH.DOC.core.Events.HistoryEmitter.mana_f]
`mana_f(entity_id: str, delta: int, current: int) -> str`
Method description: Returns a formatted `MANA_F` event string for floating mana changes.

###### mana_t [ARCH.DOC.core.Events.HistoryEmitter.mana_t]
`mana_t(entity_id: str, delta: int, current: int) -> str`
Method description: Returns a formatted `MANA_T` event string for total mana changes.

###### msg [ARCH.DOC.core.Events.HistoryEmitter.msg]
`msg(message: str) -> str`
Method description: Returns a formatted `MSG` event string for general messages.

###### death [ARCH.DOC.core.Events.HistoryEmitter.death]
`death(entity_id: str) -> str`
Method description: Returns a formatted `DEATH` event string for character death.

###### status [ARCH.DOC.core.Events.HistoryEmitter.status]
`status(entity_id: str, name: str, duration: int, state: str) -> str`
Method description: Returns a formatted `STATUS` event string for status effect updates.

###### turn_start [ARCH.DOC.core.Events.HistoryEmitter.turn_start]
`turn_start(actor_id: str, hp: int, max_hp: int, mp: int, max_mp: int, focus: int, mana: int) -> str`
Method description: Returns a formatted `TURN_START` event string containing full actor state at turn initialization.

#### BaseClasses.py [ARCH.DOC.core.BaseClasses]
Provides foundational abstract classes and interfaces ensuring modularity and decoupling.

##### GameAction [ARCH.DOC.core.BaseClasses.GameAction]
[DEPENDS: ARCH.RULES.CORE.COMMAND, ARCH.DOC.entities.Characters.Character, ARCH.DOC.core.Events.ActionLoad]
Abstract base for the Command Pattern representing general commands. Serves as the foundation for all user and system interactions.

- Constructor [ARCH.DOC.core.BaseClasses.GameAction.__init__]: `__init__(name: str, actor: "Character")`
- `name: str` [ARCH.DOC.core.BaseClasses.GameAction.name]: Descriptive name of the action.
- `actor: "Character"` [ARCH.DOC.core.BaseClasses.GameAction.actor]: The entity responsible for initiating the action.

###### can_execute [ARCH.DOC.core.BaseClasses.GameAction.can_execute]
`can_execute() -> tuple[bool, str]`
Method description: Validates if the action can be initiated given the current state.
1. Returns a tuple containing a boolean success flag and a contextual message.
2. Raises `NotImplementedError` by default; must be overridden by concrete actions.

###### execute [ARCH.DOC.core.BaseClasses.GameAction.execute]
`execute() -> ActionLoad`
Method description: Implements the core logic of the command.
1. Processes state mutations and logic.
2. Returns an `ActionLoad` containing the execution history.
3. Raises `NotImplementedError` by default.

###### execute_if_possible [ARCH.DOC.core.BaseClasses.GameAction.execute_if_possible]
`execute_if_possible() -> ActionLoad`
Method description: Safety wrapper that enforces validation before execution.
1. Calls `can_execute()` to verify requirements.
2. If validation fails, returns a failed `ActionLoad` with the error message.
3. If validation passes, calls and returns the result of `execute()`.

##### IDiceContext [ARCH.DOC.core.BaseClasses.IDiceContext]
Protocol defining access to the central dice rolling service.

- `dice_service: "DiceManager"` [ARCH.DOC.core.BaseClasses.IDiceContext.dice_service]: Read-only property providing access to the engine"s RNG service.

##### IEventContext [ARCH.DOC.core.BaseClasses.IEventContext]
Protocol defining the capability to broadcast events to the system.

- `emit(event_name: str, payload: "ActionLoad") -> None`: Dispatches a signal to all registered listeners. Payloads are modified by reference.

##### IEffectContext [ARCH.DOC.core.BaseClasses.IEffectContext]
Protocol defining management of active passives and status effects.

- `get_active_passive(char_id: str, name: str) -> "BattlePassive" | None`: Retrieves an active passive instance by name for a specific character.
- `add_status_effect(effect: "StatusEffect") -> None`: Registers and applies a new status effect to the simulation.
- `remove_status_effect(effect: "StatusEffect") -> None`: Removes an existing status effect and cleans up its hooks.

##### ITimelineContext [ARCH.DOC.core.BaseClasses.ITimelineContext]
Protocol defining interaction with the battle schedule and clock.

- `delay_character(character: "Character", extra_ticks: int) -> None`: Relative manipulation of a character"s next turn.
- `set_tick(character: "Character", tick: int) -> None`: Absolute manipulation of a character"s scheduled turn time.

##### IRegistryContext [ARCH.DOC.core.BaseClasses.IRegistryContext]
Protocol defining access to character and controller registries.

- `get_characters() -> List["Character"]`: Returns a list of all active participants.
- `get_graveyard() -> List["Character"]`: Returns a list of all characters removed from play.
- `get_controller(char_id: str) -> "CharacterController"`: Retrieves the AI or player controller for a character.

##### IDataContext [ARCH.DOC.core.BaseClasses.IDataContext]
Protocol defining access to static game data and templates.

- `get_template(template_id: str) -> "AttackActionTemplate"`: Loads a pre-defined action blueprint from the data service.

##### IPassiveContext [ARCH.DOC.core.BaseClasses.IPassiveContext]
[DEPENDS: ARCH.DOC.core.BaseClasses.IEventContext, ARCH.DOC.core.BaseClasses.IEffectContext, ARCH.DOC.core.BaseClasses.ITimelineContext, ARCH.DOC.core.BaseClasses.IRegistryContext, ARCH.DOC.core.BaseClasses.IDiceContext]
Composite protocol `(IEventContext, IEffectContext, ITimelineContext, IRegistryContext, IDiceContext, Protocol)` used by `BattlePassive` and `StatusEffect`. It provides the full suite of methods required for reactive logic, including event emission, effect management, and state registry access.

##### IActionContext [ARCH.DOC.core.BaseClasses.IActionContext]
[DEPENDS: ARCH.DOC.core.BaseClasses.IEventContext, ARCH.DOC.core.BaseClasses.IEffectContext, ARCH.DOC.core.BaseClasses.IDiceContext]
Composite protocol `(IEventContext, IEffectContext, IDiceContext, Protocol)` used by `BattleAction`. It provides a restricted set of tools necessary for executing combat actions, such as broadcasting results and applying immediate effects.

##### IControllerContext [ARCH.DOC.core.BaseClasses.IControllerContext]
[DEPENDS: ARCH.DOC.core.BaseClasses.IRegistryContext, ARCH.DOC.core.BaseClasses.ITimelineContext, ARCH.DOC.core.BaseClasses.IDataContext]
Composite protocol `(IRegistryContext, ITimelineContext, IDataContext, Protocol)` used by `CharacterController`. It grants controllers access to the registry, timeline, and data templates to facilitate decision-making and turn scheduling.

##### IJudgeContext [ARCH.DOC.core.BaseClasses.IJudgeContext]
[DEPENDS: ARCH.DOC.core.BaseClasses.IRegistryContext, ARCH.DOC.core.BaseClasses.ITimelineContext]
Composite protocol `(IRegistryContext, ITimelineContext, Protocol)` used by `IBattleJudge`. It provides only the essential information needed to evaluate victory, defeat, or other battle-ending conditions.

##### IBattleContext [ARCH.DOC.core.BaseClasses.IBattleContext]
[DEPENDS: ARCH.DOC.core.BaseClasses.IPassiveContext, ARCH.DOC.core.BaseClasses.IActionContext, ARCH.DOC.core.BaseClasses.IControllerContext, ARCH.DOC.core.BaseClasses.IJudgeContext]
Composite protocol `(IEventContext, IEffectContext, ITimelineContext, IRegistryContext, IDiceContext, IDataContext, Protocol)` implemented by the battle orchestrator (typically `BattleManager`). It serves as the complete contract that aggregates all segregated interfaces, ensuring the engine satisfies every requirement of the combat system.

##### IBattleJudge [ARCH.DOC.core.BaseClasses.IBattleJudge]
[DEPENDS: ARCH.DOC.core.BaseClasses.IJudgeContext, ARCH.DOC.core.Structs.BattleResult, ARCH.DOC.core.Enums.BattleState]
Protocol for evaluating victory/defeat logic at the end of each tick cycle.

###### rule [ARCH.DOC.core.BaseClasses.IBattleJudge.rule]
`rule(context: "IBattleContext", result: "BattleResult") -> "BattleState"`
Method description: Analyzes the current battle state and determines if a terminal state (Victory, Defeat, Draw) has been reached.
1. Inspects the `context` for character status and battle conditions.
2. Updates the `BattleResult` if a conclusion is reached.
3. Returns the appropriate `BattleState`.

##### BattleAction [ARCH.DOC.core.BaseClasses.BattleAction]
[DEPENDS: ARCH.RULES.CORE.COMMAND, ARCH.DOC.core.BaseClasses.GameAction, ARCH.DOC.core.BaseClasses.IActionContext, ARCH.DOC.entities.Characters.Character, ARCH.DOC.core.Enums.BattleActionType, ARCH.DOC.core.Events.ActionLoad]
Specialized `GameAction` for combat operations. Extends the Command Pattern to include targeting, context-aware execution, and action economy classification.

- Constructor [ARCH.DOC.core.BaseClasses.BattleAction.__init__]: `__init__(self, name: str, actor: "Character", targets: List["Character"], context: "IActionContext", action_type: "BattleActionType")`
- `targets: List["Character"]` [ARCH.DOC.core.BaseClasses.BattleAction.targets]: The intended recipients of the action"s effects.
- `context: "IActionContext"` [ARCH.DOC.core.BaseClasses.BattleAction.context]: Restricted interface for environmental interaction.
- `action_type: "BattleActionType"` [ARCH.DOC.core.BaseClasses.BattleAction.action_type]: Classification for tick cost determination.

###### target [ARCH.DOC.core.BaseClasses.BattleAction.target]
`target() -> "Character" | None`
Method description: Convenience property for single-target actions.
1. Returns the first element of the `targets` list or `None` if empty.

###### can_execute [ARCH.DOC.core.BaseClasses.BattleAction.can_execute]
`can_execute() -> tuple[bool, str]`
Method description: Validates if the combat action can be initiated.
1. Returns `(True, "")` by default.
2. Subclasses must override to validate resource costs (Focus, MP), range, and state.

###### execute [ARCH.DOC.core.BaseClasses.BattleAction.execute]
`execute() -> ActionLoad`
Method description: Implements the core combat logic.
1. Returns a failed `ActionLoad` by default.
2. Concrete actions must override this to implement damage, effects, and history logging.

##### BattlePassive [ARCH.DOC.core.BaseClasses.BattlePassive]
[DEPENDS: ARCH.RULES.CORE.IOC, ARCH.RULES.CORE.OBSERVER, ARCH.DOC.entities.Characters.Character, ARCH.DOC.core.BaseClasses.IPassiveContext, ARCH.DOC.core.DiceManager.DiceManager]
Base class for reactive components (Passives and Status Effects). These entities do not act directly but alter engine rules by subscribing to the Event Bus.

- Constructor [ARCH.DOC.core.BaseClasses.BattlePassive.__init__]: `__init__(self, name: str, owner: "Character", context: "IPassiveContext")`
- `name: str` [ARCH.DOC.core.BaseClasses.BattlePassive.name]: Display name of the passive.
- `owner: "Character"` [ARCH.DOC.core.BaseClasses.BattlePassive.owner]: The character holding the passive.
- `context: "IPassiveContext"` [ARCH.DOC.core.BaseClasses.BattlePassive.context]: Full-access interface for reactive logic.
- `dice_service: "DiceManager"` [ARCH.DOC.core.BaseClasses.BattlePassive.dice_service]: Derived access to RNG services.

###### get_hooks [ARCH.DOC.core.BaseClasses.BattlePassive.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Returns a mapping of event keys to callback functions. `[ARCH.RULES.CORE.IOC]`
1. Must be implemented by subclasses to register reactive logic with the orchestrator.

###### apply [ARCH.DOC.core.BaseClasses.BattlePassive.apply]
`apply() -> None`
Method description: Lifecycle method called when the passive enters the simulation.

###### remove [ARCH.DOC.core.BaseClasses.BattlePassive.remove]
`remove() -> None`
Method description: Lifecycle method called when the passive is removed from the simulation.

##### StatusEffect [ARCH.DOC.core.BaseClasses.StatusEffect]
[DEPENDS: ARCH.DOC.core.BaseClasses.BattlePassive, ARCH.DOC.entities.Characters.Character, ARCH.DOC.core.BaseClasses.IPassiveContext, ARCH.DOC.core.Modifiers.EphemeralModifier]
Represents a temporary condition with a defined duration. Extends `BattlePassive` to include modifier management and duration tracking.

- Constructor [ARCH.DOC.core.BaseClasses.StatusEffect.__init__]: `__init__(self, name: str, duration: int, target: "Character", context: "IPassiveContext")`
- `duration: int` [ARCH.DOC.core.BaseClasses.StatusEffect.duration]: Remaining simulation steps for the effect.
- `target: "Character"` [ARCH.DOC.core.BaseClasses.StatusEffect.target]: The affected entity.
- `modifiers: List["EphemeralModifier"]` [ARCH.DOC.core.BaseClasses.StatusEffect.modifiers]: Collection of active attribute modifiers.

###### apply [ARCH.DOC.core.BaseClasses.StatusEffect.apply]
`apply() -> None`
Method description: Initializes the effect within the simulation.
1. Implements logic to add modifiers to the target.
2. Raises `NotImplementedError` by default; subclasses must provide implementation.

###### remove [ARCH.DOC.core.BaseClasses.StatusEffect.remove]
`remove() -> None`
Method description: Tears down the effect and cleans up state.
1. Iterates through all `modifiers` and removes them from the target.
2. Notifies the `context` to unregister the status effect instance.

###### _add_modifier [ARCH.DOC.core.BaseClasses.StatusEffect._add_modifier]
`_add_modifier(modifier: "EphemeralModifier") -> None`
Method description: Internal utility to synchronize modifier registration.
1. Appends the `modifier` to the local collection.
2. Registers the `modifier` with the target character.

###### _remove_modifier [ARCH.DOC.core.BaseClasses.StatusEffect._remove_modifier]
`_remove_modifier(modifier: "EphemeralModifier") -> None`
Method description: Internal utility to synchronize modifier removal.
1. Removes the `modifier` from the local collection.
2. Unregisters the `modifier` from the target character.

#### CharacterSystem.py [ARCH.DOC.core.CharacterSystem]
[DEPENDS: ARCH.DOC.entities.Characters.Character, ARCH.DOC.entities.Items.Weapon, ARCH.DOC.entities.Items.Armor, ARCH.DOC.core.Structs.GameRules, ARCH.RULES.CORE.ENTITIES]
Provides stateless domain logic for manipulating Character entities. Isolates rule-heavy operations from data containers.

##### generate_focus [ARCH.DOC.core.CharacterSystem.generate_focus]
`generate_focus(character: "Character") -> int`
Method description: Generates character focus by drawing from the character"s mental pool.
1. Calculates `max_focus` as `rules.limite_foco * character.men`.
2. Adds `character.men` to `floating_focus`, capped by `max_focus`.
3. Returns the updated `floating_focus` value.

##### generate_mana [ARCH.DOC.core.CharacterSystem.generate_mana]
`generate_mana(character: "Character") -> int`
Method description: Pulls mana from the character"s total MP pool into a floating state for immediate use.
1. Calculates `max_floating` capacity based on `MEN` and global rules.
2. Determines `mana_to_pull` as the minimum of character"s `MEN`, available capacity, and current MP.
3. Deducts `mana_to_pull` from `current_mp` and adds it to `floating_mp`.
4. Returns the updated `floating_mp` value.

##### take_damage [ARCH.DOC.core.CharacterSystem.take_damage]
`take_damage(character: "Character", damage: int) -> None`
Method description: Reduces character health based on a damage value.
1. Subtracts `damage` from `current_hp`.
2. Ensures `current_hp` does not drop below a floor of 0.

##### spend_focus [ARCH.DOC.core.CharacterSystem.spend_focus]
`spend_focus(character: "Character", amount: int) -> bool`
Method description: Consumes a specific amount of floating focus.
1. Checks if `floating_focus` is greater than or equal to `amount`.
2. If sufficient, deducts the amount and returns `True`.
3. If insufficient, returns `False` without mutating state.

##### spend_mana [ARCH.DOC.core.CharacterSystem.spend_mana]
`spend_mana(character: "Character", amount: int) -> bool`
Method description: Consumes a specific amount of floating mana.
1. Checks if `floating_mp` is greater than or equal to `amount`.
2. If sufficient, deducts the amount and returns `True`.
3. If insufficient, returns `False` without mutating state.

##### is_alive [ARCH.DOC.core.CharacterSystem.is_alive]
`is_alive(character: "Character") -> bool`
Method description: Evaluates if a character is still active in the simulation.
1. Returns `True` if `current_hp` > 0, otherwise returns `False`.

##### equip_weapon [ARCH.DOC.core.CharacterSystem.equip_weapon]
`equip_weapon(character: "Character", new_weapon: "Weapon") -> Tuple[bool, str, "Weapon" | None]`
Method description: Handles weapon swaps and recalculates offensive stats.
1. Validates that `new_weapon.type` matches the character"s `CombatStyle.weapon_type`.
2. Stores the `old_weapon` for the return value.
3. Updates `character.weapon` and recalculates `base_pda` and `base_mda` based on the new weapon"s traits and character attributes.

##### equip_armor [ARCH.DOC.core.CharacterSystem.equip_armor]
`equip_armor(character: "Character", new_armor: "Armor") -> Tuple[bool, str, "Armor" | None]`
Method description: Handles armor swaps and updates health pools.
1. Validates compatibility between `new_armor.type` and character `CombatStyle.armor_type`.
2. If old armor exists, deducts its `hp_bonus` from `max_hp` and `current_hp` (ensuring at least 1 HP remains).
3. Updates `character.armor` and adds the `new_armor.hp_bonus` to both `max_hp` and `current_hp`.

#### DiceManager.py [ARCH.DOC.core.DiceManager]
Manages random number generation and deterministic roll scheduling for combat resolution.

##### DiceManager [ARCH.DOC.core.DiceManager.DiceManager]
[DEPENDS: ARCH.DOC.core.Structs.RollResult, ARCH.DOC.core.Enums.RollState]
Central service for random number generation and deterministic roll scheduling. Provides a layer of abstraction over Python's `random` module to support testing and complex roll states (Advantage/Disadvantage).

- Constructor [ARCH.DOC.core.DiceManager.DiceManager.__init__]: `__init__(seed: int | None = None)`
- `random: random.Random` [ARCH.DOC.core.DiceManager.DiceManager.random]: Internal RNG instance, optionally seeded for reproducibility.
- `queue: deque[int]` [ARCH.DOC.core.DiceManager.DiceManager.queue]: First-In-First-Out queue for scheduled deterministic results.

###### schedule_result [ARCH.DOC.core.DiceManager.DiceManager.schedule_result]
`schedule_result(val: int) -> None`
- `val: int`: The integer value to be injected into the queue.
Method description: Injects a predefined integer into the internal queue to override the next RNG call.
1. Appends the provided `val` to the `queue`.

###### roll_dice [ARCH.DOC.core.DiceManager.DiceManager.roll_dice]
`roll_dice(sides: int, state: RollState = RollState.NEUTRAL) -> RollResult`
- `sides: int`: Number of sides of the die to roll.
- `state: RollState`: Current advantage state (ADVANTAGE, DISADVANTAGE, NEUTRAL).
Method description: Executes a dice roll simulation, accounting for deterministic overrides and advantage states.
1. Checks if the `queue` is not empty. If so, pops the next value using `popleft()` and returns a `RollResult` with `final_roll` and `roll1` set to the popped value, and `scheduled` set to `True`.
2. If the `queue` is empty, evaluates the `state`:
    - `ADVANTAGE`: Performs two rolls using `random.randint(1, sides)`. Returns a `RollResult` with the higher value as `final_roll`, and both rolls stored.
    - `DISADVANTAGE`: Performs two rolls using `random.randint(1, sides)`. Returns a `RollResult` with the lower value as `final_roll`, and both rolls stored.
    - `NEUTRAL`: Performs a single roll using `random.randint(1, sides)` and returns a standard `RollResult`.

#### DataManager.py [ARCH.DOC.core.DataManager]
Acts as a central registry for loading and accessing data-driven templates from JSON files.

##### DataManager [ARCH.DOC.core.DataManager.DataManager]
[DEPENDS: ARCH.DOC.core.Structs.CombatStyle, ARCH.DOC.core.Structs.GameRules, ARCH.DOC.core.Structs.AttackActionTemplate, ARCH.DOC.core.Structs.AttackEffects, ARCH.DOC.entities.Characters.Character, ARCH.DOC.core.CharacterSystem, ARCH.DOC.entities.Items.Armor, ARCH.DOC.entities.Items.Weapon, ARCH.RULES.CORE.DATA]
Central data registry for loading and retrieving game definitions from JSON files. Ensures consistent instantiation of complex entities and rules.

- Constructor [ARCH.DOC.core.DataManager.DataManager.__init__]: `__init__()`
- `_action_templates: dict[str, AttackActionTemplate]` [ARCH.DOC.core.DataManager.DataManager._action_templates]: Private cache of combat action templates.
- `_combat_styles: dict[str, CombatStyle]` [ARCH.DOC.core.DataManager.DataManager._combat_styles]: Private cache of combat styles.
- `_characters: dict[str, Character]` [ARCH.DOC.core.DataManager.DataManager._characters]: Private cache of character templates.
- `_game_rules: GameRules | None` [ARCH.DOC.core.DataManager.DataManager._game_rules]: Global game configuration and progression rules.

###### load_combat_styles [ARCH.DOC.core.DataManager.DataManager.load_combat_styles]
`load_combat_styles(filepath: str) -> None`
- `filepath: str`: Path to the JSON file containing combat style definitions.
Method description: Loads combat styles from JSON, converting data to `CombatStyle` instances and Enums.
1. Opens and parses the JSON file at `filepath`.
2. Iterates through each style, converting string values for `main_stat`, `armor_type`, and `weapon_type` into their respective Enum types.
3. Populates `_combat_styles` with the instantiated `CombatStyle` objects.

###### load_game_rules [ARCH.DOC.core.DataManager.DataManager.load_game_rules]
`load_game_rules(filepath: str) -> None`
- `filepath: str`: Path to the JSON file containing global game rules.
Method description: Loads global game rules and progression tables from JSON into a `GameRules` instance.
1. Parses the JSON file to extract progression tables for HP, MP, and action costs.
2. Extracts global limits for focus and mana.
3. Instantiates `GameRules` and assigns it to `_game_rules`.

###### load_characters [ARCH.DOC.core.DataManager.DataManager.load_characters]
`load_characters(filepath: str) -> None`
- `filepath: str`: Path to the JSON file containing character templates.
Method description: Loads character definitions from JSON. Requires `GameRules` and `CombatStyles` to be pre-loaded.
1. Validates that `_game_rules` and `_combat_styles` are already populated.
2. Parses the JSON and iterates through character data.
3. Instantiates `Character` objects using attributes and the referenced `CombatStyle`.
4. Instantiates and equips `Weapon` and `Armor` objects via `CharacterSystem`.
5. Maps passive and active ability IDs from the JSON to the character instance.
6. Caches result in `_characters`.

###### load_action_templates [ARCH.DOC.core.DataManager.DataManager.load_action_templates]
`load_action_templates(filepath: str) -> None`
- `filepath: str`: Path to the JSON file containing action templates.
Method description: Loads combat action templates from JSON, instantiating `AttackActionTemplate` and `AttackEffects`.
1. Parses the JSON and iterates through template entries.
2. Converts `action_type` and `attack_type` strings to Enums.
3. Maps raw effect data into `AttackEffects` objects.
4. Instantiates `AttackActionTemplate` and caches it in `_action_templates`.

###### get_action_template [ARCH.DOC.core.DataManager.DataManager.get_action_template]
`get_action_template(action_id: str) -> AttackActionTemplate`
- `action_id: str`: Unique identifier for the requested action template.
Method description: Retrieves a cached action template by ID.
1. Searches `_action_templates` for the given `action_id`.
2. Returns the template if found; otherwise, raises a descriptive `KeyError`.

###### get_character [ARCH.DOC.core.DataManager.DataManager.get_character]
`get_character(char_id: str) -> Character`
- `char_id: str`: Unique identifier for the character template.
Method description: Retrieves a cached character template by ID.
1. Searches `_characters` for the given `char_id`.
2. Returns the character instance if found; otherwise, raises a descriptive `KeyError`.

###### get_combat_style [ARCH.DOC.core.DataManager.DataManager.get_combat_style]
`get_combat_style(style_id: str) -> CombatStyle`
- `style_id: str`: Unique identifier for the combat style.
Method description: Retrieves a cached combat style by ID.
1. Searches `_combat_styles` for the given `style_id`.
2. Returns the style if found; otherwise, raises a descriptive `KeyError`.

#### Modifiers.py [ARCH.DOC.core.Modifiers]
Implements the Modifier Stack Pattern for dynamic stat calculation.

##### StatModifier [ARCH.DOC.core.Modifiers.StatModifier]
[DEPENDS: ARCH.RULES.CORE.MODIFIER]
Base class for statistical modifiers. Serves as the foundation for both ephemeral and persistent attribute adjustments within the character modifier stack.

- Constructor [ARCH.DOC.core.Modifiers.StatModifier.__init__]: `__init__(stat_name: str, value: int, source: str)`
- `id: str` [ARCH.DOC.core.Modifiers.StatModifier.id]: Unique identifier for the modifier instance, generated via `uuid.uuid4()`.
- `stat_name: str` [ARCH.DOC.core.Modifiers.StatModifier.stat_name]: Name of the statistical attribute this modifier affects (e.g., "bda", "pda").
- `value: int` [ARCH.DOC.core.Modifiers.StatModifier.value]: Integer value to be added to the base stat.
- `source: str` [ARCH.DOC.core.Modifiers.StatModifier.source]: Descriptive name of the origin of the modifier (e.g., "Weapon Name", "Buff Name").

###### apply [ARCH.DOC.core.Modifiers.StatModifier.apply]
`apply(character: Character) -> None`
- `character: Character`: The character receiving the modifier.
Method description: Placeholder method for modifier application.
1. No direct mutation is performed. The character's attribute calculation system pulls values dynamically from its `modifiers` list. `[ARCH.RULES.CORE.MODIFIER]`

###### remove [ARCH.DOC.core.Modifiers.StatModifier.remove]
`remove(character: Character) -> None`
- `character: Character`: The character from whom the modifier is being removed.
Method description: Placeholder method for modifier removal.
1. Does nothing by default; removal is handled by the character's list management logic.

##### EphemeralModifier [ARCH.DOC.core.Modifiers.EphemeralModifier]
[DEPENDS: ARCH.DOC.core.Modifiers.StatModifier, ARCH.RULES.CORE.MODIFIER]
Specialized `StatModifier` for combat-specific adjustments. These modifiers represent temporary state changes (buffs/debuffs) and are typically managed by passives, status effects and skills that clear them upon expiration. Should not persist outside of battle.

- Constructor [ARCH.DOC.core.Modifiers.EphemeralModifier.__init__]: `__init__(stat_name: str, value: int, source: str)`
- Inherits all attributes and methods from `StatModifier`. `[ARCH.DOC.core.Modifiers.StatModifier]`

##### PersistentModifier [ARCH.DOC.core.Modifiers.PersistentModifier]
[DEPENDS: ARCH.DOC.core.Modifiers.StatModifier, ARCH.RULES.CORE.MODIFIER]
Specialized `StatModifier` for long-term attribute adjustments. These modifiers are typically applied by equipment, permanent traits, or lasting narrative effects (e.g., curses) and persist across combat encounters.

- Constructor [ARCH.DOC.core.Modifiers.PersistentModifier.__init__]: `__init__(stat_name: str, value: int, source: str)`
- Inherits all attributes and methods from `StatModifier`. `[ARCH.DOC.core.Modifiers.StatModifier]`

### MODULE: Battle [ARCH.DOC.battle]
Centralizes all logic related to combat resolution, timeline management, and reactive behaviors.
[ARCH.RULES.BATTLE.TIMELINE], [ARCH.RULES.CORE.IOC], [ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]

#### BattleManager.py [ARCH.DOC.battle.BattleManager]
The orchestrator of the battle engine. Manages the passage of time (Ticks), character participation, and the event-driven communication (Event Bus) between combatants. [ARCH.RULES.BATTLE.TIMELINE], [ARCH.RULES.CORE.IOC]

##### BattleManager [ARCH.DOC.battle.BattleManager.BattleManager]
[DEPENDS: ARCH.DOC.core.DiceManager.DiceManager, ARCH.DOC.core.DataManager.DataManager, ARCH.DOC.battle.Judges.BattleJudge, ARCH.DOC.entities.Characters.Character, ARCH.DOC.controllers.CharacterController.CharacterController, ARCH.DOC.core.BaseClasses.BattlePassive, ARCH.DOC.core.BaseClasses.BattleAction, ARCH.DOC.core.BaseClasses.StatusEffect, ARCH.DOC.core.Events.ActionLoad, ARCH.DOC.core.Enums.BattleState, ARCH.DOC.core.Structs.BattleResult, ARCH.RULES.BATTLE.TIMELINE, ARCH.RULES.CORE.IOC, ARCH.RULES.CORE.OBSERVER, ARCH.RULES.BATTLE.EPHEMERAL_HOOKS, ARCH.RULES.BATTLE.DECISION, ARCH.RULES.BATTLE.DEATH_RESOLUTION]
The central orchestrator of the battle engine. Manages the tick-based timeline, character participation, and the event-driven communication (Event Bus) between combatants. Implements the Observer pattern to decouple reactive logic from core execution.

- Constructor [ARCH.DOC.battle.BattleManager.BattleManager.__init__]: `__init__(dice_service: "DiceManager", data_service: "DataManager", judge: "BattleJudge")`
- `timeline: List[tuple]` [ARCH.DOC.battle.BattleManager.BattleManager.timeline]: A Min-Heap of `(tick, neg_hab, neg_roll, char_id, character)` used for turn scheduling. `[ARCH.RULES.BATTLE.TIMELINE]`
- `current_tick: int` [ARCH.DOC.battle.BattleManager.BattleManager.current_tick]: The current discrete point in time of the battle.
- `characters: Dict[str, Character]` [ARCH.DOC.battle.BattleManager.BattleManager.characters]: Active characters indexed by their unique ID.
- `listeners: Dict[str, List[Callable]]` [ARCH.DOC.battle.BattleManager.BattleManager.listeners]: Registry for the Event Bus, mapping signal names to subscriber hook functions. `[ARCH.RULES.CORE.OBSERVER]`
- `battle_state: BattleState` [ARCH.DOC.battle.BattleManager.BattleManager.battle_state]: The current state of the battle (RUNNING, FINISHED, ERROR).

###### subscribe [ARCH.DOC.battle.BattleManager.BattleManager.subscribe]
`subscribe(event_name: str, callback: Callable) -> None`
Method description: Registers a callback function to be executed when a specific event is emitted. `[ARCH.RULES.CORE.OBSERVER]`

###### unsubscribe [ARCH.DOC.battle.BattleManager.BattleManager.unsubscribe]
`unsubscribe(event_name: str, callback: Callable) -> None`
Method description: Removes a previously registered callback from the Event Bus. `[ARCH.RULES.CORE.OBSERVER]`

###### emit [ARCH.DOC.battle.BattleManager.BattleManager.emit]
`emit(event_name: str, payload: "ActionLoad") -> None`
Method description: Triggers an event, notifying all subscribed listeners. Listeners can modify the `payload` by reference. `[ARCH.RULES.CORE.OBSERVER]`

###### add_character [ARCH.DOC.battle.BattleManager.BattleManager.add_character]
`add_character(character: "Character", controller: "CharacterController", start_tick: int = 0) -> None`
Method description: Adds a character to the simulation and schedules their first turn.
1. Registers the character and its associated controller.
2. Generates a unique tie-break roll to prevent timeline collisions.
3. Pushes the character into the timeline heap.
4. Instantiates and subscribes all character passive abilities via `get_hooks()`. `[ARCH.RULES.CORE.IOC]`

###### run_battle [ARCH.DOC.battle.BattleManager.BattleManager.run_battle]
`run_battle() -> None`
Method description: The main execution loop of the combat engine.
1. Continually evaluates the battle state via the provided `BattleJudge`.
2. Retrieves the next active actor from the timeline.
3. Executes the controller"s decision logic, handling multiple free actions if applicable.
4. Manages the subscription and cleanup of ephemeral hooks for each action. `[ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]`
5. Implements safety breaks for failed action decisions to prevent infinite loops. `[ARCH.RULES.BATTLE.DECISION]`

###### run_action [ARCH.DOC.battle.BattleManager.BattleManager.run_action]
`run_action(action: "BattleAction") -> "ActionLoad"`
Method description: Simulates a single turn for a specific action. Primarily used for granular unit testing.
1. Emits `on_turn_start` signal.
2. Subscribes action-specific ephemeral hooks.
3. Executes the action and captures the resulting `ActionLoad`.
4. Resolves deaths and emits `on_turn_end` signal.
5. Ensures hook unsubscription in a `finally` block to prevent leaks. `[ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]`

###### set_tick [ARCH.DOC.battle.BattleManager.BattleManager.set_tick]
`set_tick(character: "Character", tick: int) -> None`
Method description: Deterministic timeline manipulation. Directly modifies a character"s scheduled turn time, ensuring slot uniqueness and maintaining heap integrity. `[ARCH.RULES.BATTLE.TIMELINE]`
1. Identifies the character"s current entry in the timeline.
2. Releases the old slot and calculates a new unique roll for the target tick.
3. Updates the entry and restores heap property via `heapify`.

###### delay_character [ARCH.DOC.battle.BattleManager.BattleManager.delay_character]
`delay_character(character: "Character", extra_ticks: int) -> None`
Method description: Relative timeline manipulation. Adds a delay to the character"s current scheduled tick. `[ARCH.RULES.BATTLE.TIMELINE]`
1. Locates the character in the timeline.
2. Calculates the new time (`current_tick + extra_ticks`) and a new unique roll.
3. Updates the entry and re-heapifies the timeline.

###### schedule_next_action [ARCH.DOC.battle.BattleManager.BattleManager.schedule_next_action]
`schedule_next_action(character: "Character", action_cost: int) -> None`
Method description: Re-calculates a character"s next turn based on action cost and current tick, then re-inserts them into the timeline.
1. Calculates the next tick as the sum of current tick and action cost.
2. Generates a new unique tie-break roll.
3. Pushes the updated character state back into the min-heap.

###### get_next_actor [ARCH.DOC.battle.BattleManager.BattleManager.get_next_actor]
`get_next_actor() -> "Character" | None`
Method description: Pops the top of the timeline heap. Validates character vitality and active status before advancing `current_tick` and returning the actor.
1. Repeatedly pops from the heap until an active, living character is found.
2. Updates `current_tick` to match the retrieved character"s tick.
3. Returns the character or `None` if the timeline is exhausted.

###### resolve_deaths [ARCH.DOC.battle.BattleManager.BattleManager.resolve_deaths]
`resolve_deaths() -> None`
Method description: Scans the battlefield for characters with zero or less HP, removes them from the active simulation, and moves them to the graveyard. Emits `on_character_death`. `[ARCH.RULES.BATTLE.DEATH_RESOLUTION]`
1. Checks the HP of all active characters.
2. For each dead character: removes them from play, updates the graveyard, and triggers the death signal.
3. Records the death in the battle history.

###### get_graveyard [ARCH.DOC.battle.BattleManager.BattleManager.get_graveyard]
`get_graveyard() -> List["Character"]`
Method description: Returns a list of all characters currently in the graveyard.

#### BattleActions.py [ARCH.DOC.battle.BattleActions]
Defines the available maneuvers characters can perform. Utilizes the Command Pattern and allows for behavioral modification via hooks. [ARCH.RULES.CORE.COMMAND]

- EFFECT_HOOK_BUILDERS [ARCH.DOC.battle.BattleActions.EFFECT_HOOK_BUILDERS]:
  Dictionary mapping effect IDs to builder functions. Each builder takes an effect and action and returns a dict of Event Bus hooks.
  Supported: add_gda, swap_atk_def_die, set_gda_zero_on_dmg, apply_status_on_hit_threshold.

##### AttackAction [ARCH.DOC.battle.BattleActions.AttackAction]
A data-driven action for physical/magical offenses.
Core dependencies: AttackActionTemplate, IBattleContext.
Internal state: template, attack_type. [ARCH.RULES.BATTLE.TARGETING], [ARCH.RULES.BATTLE.AREA_ATTACK]
- execute() -> ActionLoad [ARCH.DOC.battle.BattleActions.AttackAction.execute]:
  1. Consumes focus cost.
  2. If AREA, performs a Master Roll for hit state.
  3. Iterates through targets:
     a. Emits on_roll_modify, on_defense_reaction.
     b. Checks for hit (GdA > target.grd - actor.pre).
     c. If hit, emits on_hit_check, on_gda_modify, on_damage_calculation, on_damage_taken.
     d. Applies damage to target via CharacterSystem.take_damage.
  4. Emits on_attack_end for each target.

##### GenerateManaAction [ARCH.DOC.battle.BattleActions.GenerateManaAction]
Converts daily MP into floating MP.
- execute() -> ActionLoad [ARCH.DOC.battle.BattleActions.GenerateManaAction.execute]: Calls CharacterSystem.generate_mana and returns an ActionLoad with MANA_T and MANA_F events.

##### GenerateFocusAction [ARCH.DOC.battle.BattleActions.GenerateFocusAction]
Replenishes the character's focus pool.
- execute() -> ActionLoad [ARCH.DOC.battle.BattleActions.GenerateFocusAction.execute]: Calls CharacterSystem.generate_focus and returns an ActionLoad with FOCUS events.

##### TogglePosturaDefensiva [ARCH.DOC.battle.BattleActions.TogglePosturaDefensiva]
A free action to switch stances.
- execute() -> ActionLoad [ARCH.DOC.battle.BattleActions.TogglePosturaDefensiva.execute]: Retrieves the Postura Defensiva passive instance and calls its toggle() method.

#### BattlePassives.py [ARCH.DOC.battle.BattlePassives]
Reactive logic tied to characters. Passives are instantiated at battle start and subscribe to events to influence outcomes. [ARCH.RULES.CORE.IOC]

##### PosturaDefensiva [ARCH.DOC.battle.BattlePassives.PosturaDefensiva]
A stateful stance passive that modifies dice and penalizes attackers. [ARCH.RULES.BATTLE.PAYLOAD_TARGET_CHECK]
- toggle() -> str [ARCH.DOC.battle.BattlePassives.PosturaDefensiva.toggle]: Toggles is_active. If ON, adds EphemeralModifier to atk_die (-2) and def_die (+2). If OFF, removes them and clears target tracking.
- get_hooks() -> Dict[str, Callable] [ARCH.DOC.battle.BattlePassives.PosturaDefensiva.get_hooks]:
  - on_gda_modify: Marks targets hit while active.
  - on_roll_modify: Applies a -1 penalty to the pre of tracked attackers targeting the owner.
  - on_attack_end/on_turn_end: Cleans up temporary tracking.

##### GracaDoDuelista [ARCH.DOC.battle.BattlePassives.GracaDoDuelista]
Grants GdA bonuses and allows defensive reactions.
- get_hooks() -> Dict[str, Callable] [ARCH.DOC.battle.BattlePassives.GracaDoDuelista.get_hooks]:
  - on_gda_modify: Rolls 1d6 and adds it to GdA.
  - on_defense_reaction: If hit, allows the controller to choose to spend 2 focus to roll 1d4 and subtract it from the incoming GdA.

##### Combo [ARCH.DOC.battle.BattlePassives.Combo]
Triggers extra attacks on consecutive hits.
- get_hooks() -> Dict[str, Callable] [ARCH.DOC.battle.BattlePassives.Combo.get_hooks]:
  - on_attack_end: Recursively executes AttackAction (BasicAttack) if previous hits were successful, incrementing stage. At final stage, applies Atordoado.

##### ForçaBruta [ARCH.DOC.battle.BattlePassives.ForçaBruta]
Simple damage multiplier.
- get_hooks() -> Dict[str, Callable] [ARCH.DOC.battle.BattlePassives.ForçaBruta.get_hooks]:
  - on_gda_modify: Doubles the current GdA if the owner hits.

##### MãosPesadas [ARCH.DOC.battle.BattlePassives.MãosPesadas]
Threshold-based status application.
- get_hooks() -> Dict[str, Callable] [ARCH.DOC.battle.BattlePassives.MãosPesadas.get_hooks]:
  - on_gda_modify: If GdA > 3, applies Atordoado to the target.

#### Judges.py [ARCH.DOC.battle.Judges]
Logic for determining battle outcomes.

##### BattleJudge [ARCH.DOC.battle.Judges.BattleJudge]
Standard team-based victory/defeat evaluator.
- rule(context: 'IBattleContext', result: 'BattleResult') -> BattleState [ARCH.DOC.battle.Judges.BattleJudge.rule]:
  Evaluates the presence of living characters in each team.
  1. Checks if any characters are alive in team 1 and team 2.
  2. If both alive: RUNNING.
  3. If only team 1: VICTORY.
  4. If only team 2: DEFEAT.
  5. If none: DRAW.
  6. Updates result.winners and result.losers accordingly.

#### StatusEffects.py [ARCH.DOC.battle.StatusEffects]
Temporary conditions applied to characters with a turn-based duration. [ARCH.RULES.CORE.MODIFIER]

##### StatusEffect [ARCH.DOC.battle.StatusEffects.StatusEffect]
Abstract base for status effects (inherits from BattlePassive).
Internal state: duration (int), character (Character), modifiers (list[EphemeralModifier]).
- remove() -> None [ARCH.DOC.battle.StatusEffects.StatusEffect.remove]: Cleans up all modifiers and calls context.remove_status_effect.

##### Atordoado [ARCH.DOC.battle.StatusEffects.Atordoado]
Stun effect that delays characters.
- apply() -> None [ARCH.DOC.battle.StatusEffects.Atordoado.apply]: Adds a -1 bdd modifier and calls delay_character for 50% of base action cost.
- get_hooks() -> Dict[str, Callable] [ARCH.DOC.battle.StatusEffects.Atordoado.get_hooks]:
  - on_turn_start: Monitors turn start to trigger expiration and removal.

### MODULE: Entities [ARCH.DOC.entities]
The `entities` module contains data-only classes representing game objects. `[ARCH.RULES.CORE.ENTITIES]`

#### Characters [ARCH.DOC.entities.Characters]
The primary data container for actors, designed as an anemic entity with a reactive modifier stack. `[ARCH.RULES.CORE.ENTITIES]`

##### Character [ARCH.DOC.entities.Characters.Character]
Tracks core state: `current_hp`, `current_mp`, `floating_mp`, and `floating_focus`. Maintains references to `CombatStyle`, `Weapon`, and `Armor`.

- get_stat_total() [ARCH.DOC.entities.Characters.Character.get_stat_total]: Computes real-time values for stats like `rank`, `bda`, `bdd`, `pre`, `grd`, `pda`, and `mda`. This ensures stats are never mutated directly. `[ARCH.RULES.CORE.MODIFIER]`

#### Items [ARCH.DOC.entities.Items]
Data structures for equipment, used by `CharacterSystem` to populate character stats.

##### Weapon [ARCH.DOC.entities.Items.Weapon]
Dataclass defining offensive traits. Includes `db` (Damage Bonus), `mda` (Degree of Success multiplier), and `type` (for compatibility checks).

##### Armor [ARCH.DOC.entities.Items.Armor]
Dataclass defining defensive traits. Includes `hp_bonus` and `type`.

### MODULE: Controllers [ARCH.DOC.controllers]
The `controllers` module implements the "Decision Loop" for characters, separating AI/Player logic from the engine. `[ARCH.RULES.CORE.MVC]`

#### Character Controller [ARCH.DOC.controllers.CharacterController]
The "Decision Loop" interface that separates character behavior (AI or Player) from engine mechanics. `[ARCH.RULES.CORE.MVC]`

##### CharacterController [ARCH.DOC.controllers.CharacterController.CharacterController]
Abstract base class. Defines the interface for tactical decision-making.

- choose_action() [ARCH.DOC.controllers.CharacterController.CharacterController.choose_action]: Called at the start of a turn. Analyzes the `IBattleContext` and returns a `BattleAction` command. Supports re-decision if the previous action failed validation (via `action_load`). `[ARCH.RULES.BATTLE.DECISION]`
- choose_reaction() [ARCH.DOC.controllers.CharacterController.CharacterController.choose_reaction]: Called during action resolution (e.g., `on_defense_reaction`). Allows the controller to opt-in to conditional effects (like Evasion) based on the current `AttackLoad`.

##### PvP1v1Controller [ARCH.DOC.controllers.CharacterController.PvP1v1Controller]
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

- PATH_MAPPING [ARCH.DOC.utilities.ref_manager.PATH_MAPPING]: Configuration dictionary mapping tag prefixes (e.g., `ARCH.`, `GDD.`, `WORKFLOWS.`) to their source markdown files, ensuring centralized path management.
- resolve_tag() [ARCH.DOC.utilities.ref_manager.resolve_tag]: The primary recursive solver. It fetches a tag's content and iteratively resolves all nested "DEPENDS:" tags up to a specified maximum depth (`max_depth`, defaulting to 1). It maintains a `resolved_tags` registry to prevent circular dependencies. When a tag is found in a header (session), all other tags within that session are automatically marked as resolved to ensure clean extraction.
- extract_section() [ARCH.DOC.utilities.ref_manager.extract_section]: The parsing engine. It searches for a tag (prioritizing headers) and extracts the corresponding block of text. If the tag is found in a header, it captures all content until a header of equal or higher level is encountered.
- update_section() [ARCH.DOC.utilities.ref_manager.update_section]: The modification engine. Locates a tag and replaces its entire section (if a header) or line with new content. Supports reading content from a string or an external file via `--from-file`.
- create_section() [ARCH.DOC.utilities.ref_manager.create_section]: The creation engine. Implements **Smart Placement** and **Fail-Fast Validation**: it prevents duplicate tags and ensures hierarchical integrity. New tags are placed after their parent or last sibling based on prefix matching. It fails if a parent tag is missing (returning "Error: Parent tag [prefix] not found." for 3+ component tags) or if the file identifier is missing (for 2 component tags), ensuring documentation structure is maintained.
- get_path_for_tag() [ARCH.DOC.utilities.ref_manager.get_path_for_tag]: A utility that normalizes tags and determines the correct source file path by matching the tag's prefix against the `PATH_MAPPING`.

##### CLI Usage [ARCH.DOC.utilities.ref_manager.CLI]
- CLI Interface: A command-line wrapper that allows agents to request multiple tags or perform documentation maintenance. All extraction results are automatically written to `output.txt` in the current directory to prevent interface truncation, in addition to standard output.
  - **Extraction:** `python3 utilities/ref_manager.py [TAG1] [TAG2] ... [--depth N]` (depth defaults to 1)
  - **Update:** `python3 utilities/ref_manager.py --update [TAG] "Content" [--from-file path]`
  - **Creation:** `python3 utilities/ref_manager.py --create [NEW_TAG] "Content"`
  - **Deletion:** `python3 utilities/ref_manager.py --delete [TAG]`

### MODULE: Views [ARCH.DOC.views]
Contains modules responsible for presenting data to the user or translating internal state to human-readable formats.

#### BattleView.py [ARCH.DOC.views.BattleView]
Translates structured history tags from the core into technical narrative strings and handles terminal output. Adheres to `[ARCH.RULES.CORE.MVC]` and `[ARCH.RULES.CORE.HISTORY]`.

##### BattleView [ARCH.DOC.views.BattleView.BattleView]
Class responsible for parsing battle history logs and presenting them.

- present_battle() [ARCH.DOC.views.BattleView.BattleView.present_battle]: Takes a BattleResult, parses all history tags, and prints the battle narrative followed by a HP summary to the terminal.
- present_summary() [ARCH.DOC.views.BattleView.BattleView.present_summary]: Aggregates statistics (wins, draws, turns) for multiple BattleResult objects and prints a summary for the given character IDs.
- parse() [ARCH.DOC.views.BattleView.BattleView.parse]: Legacy static method. Takes a list of structured history strings and returns formatted narrative strings.
- _parse_entry() [ARCH.DOC.views.BattleView.BattleView._parse_entry]: Private method that translates a single history tag into a human-readable string.

## Test Quality Standards [ARCH.TEST_QUALITY]

- **Behavior over Implementation [ARCH.TEST_QUALITY.TEST_BEHAVIOR]:** Tests MUST verify the outcome (e.g., final HP, ActionLoad, state changes) rather than internal implementation details (e.g., checking specific list indices or private method calls).
- **Controlled Mocking [ARCH.TEST_QUALITY.MOCKING]:** Use real instances for domain logic (Entities, Systems). Mock ONLY system boundaries (I/O, UI) or to enforce determinism. Use `DiceManager.schedule_result()` for simulating dice rolls.
- **Entity Factory [ARCH.TEST_QUALITY.ENTITY_FACTORY]:** Use `tests.utils.entity_factory` when instantiating entities for tests. Use `DataManager` for getting entities only in integration tests.
- **Data Integrity [ARCH.TEST_QUALITY.DATA_INTEGRITY]:** For integration tests using `DataManager`, use `tests.utils.json_integrity_checker.get_json_keys()` to dynamically iterate over and verify all IDs in game data. This ensures tests remain decoupled from specific balance values while guaranteeing hydration logic works for all defined content.
- **Decoupling [ARCH.TEST_QUALITY.DECOUPLING]:** Ensure tests do not break upon internal refactors if the public behavior remains unchanged.
- **Invariants [ARCH.TEST_QUALITY.INVARIANTS]:** Assert that attribute modifiers `[ARCH.RULES.CORE.MODIFIER]` are properly used and Character atributes are not corrupted by bad modifications.
- **Lifecycle Auditing** [ARCH.TEST_QUALITY.LIFECYCLE]: Tests involving the EventBus MUST verify that all ephemeral hooks ([ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]) used by self modifying actions are successfully unsubscribed after the action cycle. Assert that the EventBus subscriber count returns to its baseline.
- **Battle Context [ARCH.TEST_QUALITY.IBATTLECONTEXT]:** Get a `BattleManager` with `create_test_battle_manager()` from `tests/utils/test_utils.py` when a concrete implementation of `IBattleContext` (or any of its segregated forms like `IActionContext`, `IPassiveContext`) is required for behavioral tests, avoid mocking of the battle state.
- **Testing Actions [ARCH.TEST_QUALITY.ACTIONS]:** When testing the outcome of an BattleAction, you should: use `BattleManager.add_character()` to add all actors in the battle, use `BattleManager.set_tick()` to manipulate the timeline if necessary, use `BattleManager.get_next_actor()` to take the actor you want out of the timeline, create a `BattleAction` with that actor and call `BattleManager.run_action` with that action. The actor will be reinserted in the timeline unless you executed a free action. 
- **Structured History [ARCH.TEST_QUALITY.STRUCTURED_HISTORY]:** Tests verifying action outcomes MUST assert against structured event tags (`TAG|PARAM1|PARAM2...`) rather than narrative strings or partial substrings of `MSG` tags. This ensures tests remain resilient to localization changes and narrative polish. `[ARCH.RULES.CORE.HISTORY]`
- **AttackAction Data Loading [ARCH.TEST_QUALITY.ATTACK_ACTION_DATA]:** Abilities implemented through `AttackActions` MUST be tested by loading their `AttackActionTemplate` through `DataManager` from `data/AttackActions.json`. This ensures tests reflect actual game data definitions and prevents discrepancies between hardcoded mocks and production content.

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

- Documentation use a tag system and a dependency system guided by the tags.
- [DEPENDS: ...] is a dependency tag that holds a list of comma separated tags for all dependencies of a given class or file.
- Example: [DEPENDS: ARCH.RULES.CORE.COMMAND, ARCH.DOC.entities.Characters.Character, ARCH.DOC.core.Events.ActionLoad]
- Dependency tags are used for pointing to types and methods dependencies, but can also point to relevant architectural rules for that context.

- Template:

```
### MODULE: module_name [ARCH.DOC.module_name]
Comprehensive description of the module and its primary responsibilities.

#### File Name [ARCH.DOC.module_name.FileName]
[DEPENDS: ...] <- For global variables and functions dependencies
Description of the file's domain purpose and what core concepts it handles.

- `variable_name: type` [ARCH.DOC.module_name.FileName.variable_name]: Global variable description.

##### function_name [ARCH.DOC.module_name.FileName.function_name]
`function_name(param1: type, ...) -> return_type`
- `variable_name: type`: function variable description
- Description: Detailed function description. Must include a detailed numbered step-by-step explanation of its internal logic if the function complexity allows.

##### InterfaceName [ARCH.DOC.module_name.FileName.InterfaceName]
[DEPENDS: ...] <- For Interface dependencies
Interface/Protocol description. MUST detail required properties and exact method signatures, including expected behaviors and rules for implementation.

- `property_name: type`: Interface property description.
- `method_name(param1: type, ...) -> return_type`: Interface method description.

##### ClassName [ARCH.DOC.module_name.FileName.ClassName] 
[DEPENDS: ...] <- For Class dependencies
Class description. MUST include its purpose and overall architecture role.

- Constructor [ARCH.DOC.module_name.FileName.ClassName.__init__]: `__init__(...)`
- `attribute_name: type` [ARCH.DOC.module_name.FileName.ClassName.attribute_name]: Attribute description.

###### method_name [ARCH.DOC.module_name.FileName.ClassName.method_name]
`method_name(param1: type, ...) -> return_type`
- `variable_name: type`: method variable description.
Method description: Detailed method description. Must include a detailed numbered step-by-step explanation of its internal logic if the method complexity allows. 

##### CLI Usage [ARCH.DOC.module_name.FileName.CLI]
Description of command-line usage.
```

#### Rules [ARCH.DOC_STANDARDS.MODULE.RULES]
- Template shows all possible elements, include only those needed to the documentation.
- Include a section only if there is at least one relevant item.
- Sections MUST follow the order defined in the template.
- Never invent variables/functions just to satisfy the template.
- Preserve existing tags when updating.
- Prefer extending over rewriting.

- **Section Tags for Methods:** All class methods MUST use the `######` Section Tag format to safely house multi-line logic steps without breaking tag bounding boxes.
- **Line Tags for Properties:** Properties and Constructors generally use Line Tags unless they require complex multi-line descriptions.
- **Dependencies:** `[DEPENDS: ...]` tags MUST list all requisite Interfaces, core architectural rules, and tightly coupled objects (preferring interfaces over concrete implementations to reduce tag recursive bloat).

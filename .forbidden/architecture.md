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
- **Attack Load Modification [ARCH.RULES.BATTLE.ATTACK_LOAD]:** `AttackLoad` holds all character attributes and other parameters involved in the attack resolution. Any `BattlePassive`, `StatusEffect` or effect hook that modifies `AttackAction` must do so by changing `AttackLoad` parameters. 

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

- `MOVE_ACTION: str` [ARCH.DOC.core.Enums.BattleActionType.MOVE_ACTION]: Movement action, used for moving around, drinking potions, and using items.
- `STANDARD_ACTION: str` [ARCH.DOC.core.Enums.BattleActionType.STANDARD_ACTION]: Prymary action, used for attacking, using skills and casting magics.
- `FREE_ACTION: str` [ARCH.DOC.core.Enums.BattleActionType.FREE_ACTION]: Fast actions with no tick cost.

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

- Constructor [ARCH.DOC.core.Events.AttackLoad.__init__]: `__init__(*, character: "Character", history: List[str] = [], success: bool = True, target: Character | None = None, attack_type: AttackType, attack_state: RollState, defense_state: RollState, gda: int = 0, damage: int = 0, hit: bool = False, attack_roll: int = 0, defense_roll: int = 0, pre: int = 0, bda: int = 0, bdd: int = 0, grd: int = 0, atk_die: int = 0, def_die: int = 0)`
- `target: Character | None` [ARCH.DOC.core.Events.AttackLoad.target]: The recipient of the attack.
- `attack_type: AttackType` [ARCH.DOC.core.Events.AttackLoad.attack_type]: Categorization of the attack (Basic, Skill, etc.).
- `attack_state: RollState` [ARCH.DOC.core.Events.AttackLoad.attack_state]: Advantage state applied to the attacker.
- `defense_state: RollState` [ARCH.DOC.core.Events.AttackLoad.defense_state]: Advantage state applied to the defender.
- `gda: int` [ARCH.DOC.core.Events.AttackLoad.gda]: Degree of Success (GdA) used for final damage resolution.
- `damage: int` [ARCH.DOC.core.Events.AttackLoad.damage]: Bonus damage or reduction value added during calculation.
- `hit: bool` [ARCH.DOC.core.Events.AttackLoad.hit]: Flag indicating if the attack successfully connected with the target.
- `attack_roll: int` [ARCH.DOC.core.Events.AttackLoad.attack_roll]: Raw attack dice roll result.
- `defense_roll: int` [ARCH.DOC.core.Events.AttackLoad.defense_roll]: Raw defense dice roll result.
- `pre: int` [ARCH.DOC.core.Events.AttackLoad.pre]: Action-scoped precision value of the attacker.
- `bda: int` [ARCH.DOC.core.Events.AttackLoad.bda]: Action-scoped attack bonus of the attacker.
- `bdd: int` [ARCH.DOC.core.Events.AttackLoad.bdd]: Action-scoped defense bonus of the defender.
- `grd: int` [ARCH.DOC.core.Events.AttackLoad.grd]: Action-scoped guard value of the defender.
- `atk_die: int` [ARCH.DOC.core.Events.AttackLoad.atk_die]: Action-scoped attack die size of the attacker.
- `def_die: int` [ARCH.DOC.core.Events.AttackLoad.def_die]: Action-scoped defense die size of the defender.

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

###### passive [ARCH.DOC.core.Events.HistoryEmitter.passive]
`passive(passive_name: str, owner_id: str) -> str`
Method description: Returns a formatted `PASSIVE` event string indicating a passive ability has triggered.

###### atk_load [ARCH.DOC.core.Events.HistoryEmitter.atk_load]
`atk_load(attribute: str, delta: int, current: int) -> str`
Method description: Returns a formatted `ATK_LOAD` event string indicating an internal modification to the attack load.
`action_hook(action_name: str, actor_id: str) -> str`
Method description: Returns a formatted `ACTION_HOOK` event string indicating an ephemeral action hook has triggered.
`status_hook(status_name: str, target_id: str) -> str`
Method description: Returns a formatted `STATUS_HOOK` event string indicating a status effect hook has triggered.

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
[DEPENDS: ARCH.DOC.battle.BattleManager.BattleManager.listeners.registry]
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
[DEPENDS: ARCH.DOC.core.BaseClasses.IEventContext, ARCH.DOC.core.BaseClasses.IEffectContext, ARCH.DOC.core.BaseClasses.ITimelineContext, ARCH.DOC.core.BaseClasses.IRegistryContext, ARCH.DOC.core.BaseClasses.IDiceContext, ARCH.DOC.core.BaseClasses.IActionStateContext]
Composite protocol `(IEventContext, IEffectContext, ITimelineContext, IRegistryContext, IDiceContext, IActionStateContext, Protocol)` used by `BattlePassive` and `StatusEffect`. It provides the full suite of methods required for reactive logic, including event emission, effect management, action state inspection, and state registry access.

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
Composite protocol `(IEventContext, IEffectContext, ITimelineContext, IRegistryContext, IDiceContext, IDataContext, IActionStateContext, Protocol)` implemented by the battle orchestrator (typically `BattleManager`). It serves as the complete contract that aggregates all segregated interfaces, ensuring the engine satisfies every requirement of the combat system.

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
Base class for reactive components (Passives and Status Effects). These entities do not act directly but alter engine rules by subscribing to the Event Bus to modify simulation state and resolution.

- Constructor [ARCH.DOC.core.BaseClasses.BattlePassive.__init__]: `__init__(name: str, owner: Character, context: IPassiveContext)`
- `name: str` [ARCH.DOC.core.BaseClasses.BattlePassive.name]: Display name of the passive.
- `owner: Character` [ARCH.DOC.core.BaseClasses.BattlePassive.owner]: The character holding the passive.
- `context: IPassiveContext` [ARCH.DOC.core.BaseClasses.BattlePassive.context]: Interface providing access to battle state and engine services.
- `dice_service: DiceManager` [ARCH.DOC.core.BaseClasses.BattlePassive.dice_service]: Derived access to the engine's dice service.

###### get_hooks [ARCH.DOC.core.BaseClasses.BattlePassive.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Returns a mapping of event keys to callback functions. `[ARCH.RULES.CORE.IOC]`
1. Must be implemented by subclasses to register reactive logic with the orchestrator.
2. Raises `NotImplementedError` if called directly on the base class.

###### apply [ARCH.DOC.core.BaseClasses.BattlePassive.apply]
`apply() -> None`
Method description: Lifecycle hook called when the passive is initialized or added to the simulation.
1. Placeholder method to be optionally overridden by subclasses for immediate state changes or logging.

###### remove [ARCH.DOC.core.BaseClasses.BattlePassive.remove]
`remove() -> None`
Method description: Lifecycle hook called when the passive is removed from the simulation.
1. Placeholder method to be optionally overridden by subclasses for cleanup logic.

##### StatusEffect [ARCH.DOC.core.BaseClasses.StatusEffect]
[DEPENDS: ARCH.DOC.core.BaseClasses.BattlePassive, ARCH.DOC.entities.Characters.Character, ARCH.DOC.core.BaseClasses.IPassiveContext, ARCH.DOC.core.Modifiers.EphemeralModifier]
Represents a temporary condition with a defined duration. Extends `BattlePassive` to include automated modifier management and duration tracking. Serves as the base for all combat-related status effects.

- Constructor [ARCH.DOC.core.BaseClasses.StatusEffect.__init__]: `__init__(name: str, duration: int, target: Character, context: IPassiveContext)`
- `duration: int` [ARCH.DOC.core.BaseClasses.StatusEffect.duration]: Remaining turn count for the effect.
- `character: Character` [ARCH.DOC.core.BaseClasses.StatusEffect.character]: The entity affected by the condition.
- `modifiers: List[EphemeralModifier]` [ARCH.DOC.core.BaseClasses.StatusEffect.modifiers]: Collection of active attribute modifiers tied to this effect instance.

###### apply [ARCH.DOC.core.BaseClasses.StatusEffect.apply]
`apply() -> None`
Method description: Initializes the effect within the simulation.
1. Implements the specific logic for applying the status.
2. Raises `NotImplementedError` by default; must be overridden by concrete subclasses.

###### remove [ARCH.DOC.core.BaseClasses.StatusEffect.remove]
`remove() -> None`
Method description: Tears down the effect and cleans up state.
1. Iterates through all tracked `modifiers`.
2. Calls `_remove_modifier` for each to ensure synchronization.
3. Notifies the `context` to unregister the status effect instance via `context.remove_status_effect`.

###### _add_modifier [ARCH.DOC.core.BaseClasses.StatusEffect._add_modifier]
`_add_modifier(modifier: EphemeralModifier) -> None`
- `modifier: EphemeralModifier`: The modifier to be registered.
Method description: Internal utility to synchronize modifier registration.
1. Appends the `modifier` to the internal `modifiers` list.
2. Adds the `modifier` to the owner character's modifier stack.

###### _remove_modifier [ARCH.DOC.core.BaseClasses.StatusEffect._remove_modifier]
`_remove_modifier(modifier: EphemeralModifier) -> None`
- `modifier: EphemeralModifier`: The modifier to be removed.
Method description: Internal utility to synchronize modifier removal.
1. Removes the `modifier` from the internal `modifiers` list if present.
2. Removes the `modifier` from the owner character's modifier stack.

##### IActionStateContext [ARCH.DOC.core.BaseClasses.IActionStateContext]
Protocol defining access to the currently executing battle action.

- `current_action: "BattleAction" | None` [ARCH.DOC.core.BaseClasses.IActionStateContext.current_action]: Read-only property exposing the action currently being resolved.

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
- `battle_state: BattleState` [ARCH.DOC.battle.BattleManager.BattleManager.battle_state]: The current state of the battle (RUNNING, FINISHED, ERROR).
- `listeners: Dict[str, List[Callable]]` [ARCH.DOC.battle.BattleManager.BattleManager.listeners]: Registry for the Event Bus, mapping signal names to subscriber hook functions. See [ARCH.DOC.battle.BattleManager.BattleManager.listeners.registry]. `[ARCH.RULES.CORE.OBSERVER]`
- `current_action: "BattleAction" | None` [ARCH.DOC.battle.BattleManager.BattleManager.current_action]: The currently executing action, available to ephemeral hooks during resolution.

###### listeners registry [ARCH.DOC.battle.BattleManager.BattleManager.listeners.registry]
Supported event signals and their triggers:
- `on_turn_start`: Turn start.
- `on_roll_modify`: For modifications on: `Character.bda`, `Character.bdd`, `Character.atk_die`, `Character.def_die`, `AttackLoad.attack_state` and `AttackLoad.defense_state`.  
- `on_defense_reaction`: For defensive reactions to modify `AttackLoad.gda` before hit/miss verification.
- `on_hit_check`: After hit/miss is decided for abilities that decide it's activation base on the base `AttackLoad.gda`.
- `on_gda_modify`: For damaging abilities to modify `AttackLoad.gda` after a hit is confirmed.
- `on_damage_calculation`: For skills/magics to modify `AttackLoad.gda` and `AttackLoad.damage` before damage calculation.
- `on_damage_taken`: For abilities to modify `AttackLoad.damage` by a percentage before it's applied at the target.
- `on_attack_end`: End of an attack action.
- `on_turn_end`: End of turn.
- `on_character_death`: When a character dies.

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
[DEPENDS: ARCH.RULES.CORE.COMMAND, ARCH.RULES.CORE.OBSERVER, ARCH.RULES.BATTLE.ATTACK_DATA, ARCH.DOC.core.BaseClasses.BattleAction]
Defines the available maneuvers characters can perform during combat. Utilizes the Command Pattern to encapsulate complex game logic and allows for behavioral modification via ephemeral hooks.

- `EFFECT_HOOK_BUILDERS: Dict[str, Callable]` [ARCH.DOC.battle.BattleActions.EFFECT_HOOK_BUILDERS]: Registry mapping template effect IDs to their corresponding hook builder functions.

##### _build_add_gda [ARCH.DOC.battle.BattleActions._build_add_gda]
`_build_add_gda(effect, action: AttackAction) -> Dict[str, Callable]`
- `effect`: Data object containing the "amount" parameter.
- `action`: The `AttackAction` instance triggering the hook.
- Description: Creates a hook for `on_damage_calculation`.
1. Extracts `amount` from `effect.parameters`.
2. Defines `add_gda_hook` which increases `attack_load.gda` by the amount if the actor matches the action's actor.
3. Records a `MOD` event in the attack history.

##### _build_swap_atk_def_die [ARCH.DOC.battle.BattleActions._build_swap_atk_def_die]
`_build_swap_atk_def_die(effect, action: AttackAction) -> Dict[str, Callable]`
- Description: Creates a hook to temporarily swap the characters attack die with their defense die by modifying the `attack_load` directly.
1. `swap_die_hook`: Sets `attack_load.atk_die` to `action.actor.def_die`. Registered to `on_roll_modify`.

##### _build_set_gda_zero_on_dmg [ARCH.DOC.battle.BattleActions._build_set_gda_zero_on_dmg]
`_build_set_gda_zero_on_dmg(effect, action: AttackAction) -> Dict[str, Callable]`
- Description: Forces `GdA` to 0 during damage calculation, typically for non-damaging utility hits.
1. Registers `set_gda_zero_hook` to `on_damage_calculation`.
2. Sets `attack_load.gda = 0` and adds a `MOD` event to history.

##### _build_apply_status_on_hit_threshold [ARCH.DOC.battle.BattleActions._build_apply_status_on_hit_threshold]
`_build_apply_status_on_hit_threshold(effect, action: AttackAction) -> Dict[str, Callable]`
- Description: Applies a status effect to the target if the hit is successful and `GdA` exceeds a specified threshold.
1. Extracts `status_name`, `threshold`, and `duration`.
2. Registers `apply_status_hook` to `on_hit_check`.
3. If hit is successful and `attack_load.gda > threshold`, instantiates the status effect (e.g., `Atordoado`) and adds it to the battle context.
4. Records a `STATUS` event.

##### AttackAction [ARCH.DOC.battle.BattleActions.AttackAction]
[DEPENDS: ARCH.RULES.CORE.DATA, ARCH.RULES.BATTLE.TARGETING, ARCH.RULES.BATTLE.AREA_ATTACK, ARCH.DOC.core.Structs.AttackActionTemplate, ARCH.RULES.CORE.IOC, GDD.COMBAT.FLOW, ARCH.DOC.core.Events.AttackLoad]
A generic, data-driven attack action. Logic is driven by an `AttackActionTemplate`, which defines costs, types, and special effects injected via hooks. Constructor can be called with `template = None` to instantiate a "Basic Attack".

- Constructor [ARCH.DOC.battle.BattleActions.AttackAction.__init__]: `__init__(template: AttackActionTemplate | None, actor: Character, targets: List[Character], context: IActionContext, attack_type: AttackType = None)`
- `template: AttackActionTemplate` [ARCH.DOC.battle.BattleActions.AttackAction.template]: Data template defining the action's base stats and effects.
- `attack_type: AttackType` [ARCH.DOC.battle.BattleActions.AttackAction.attack_type]: Classification of the attack (e.g., BASIC_ATTACK, AREA).

###### can_execute [ARCH.DOC.battle.BattleActions.AttackAction.can_execute]
`can_execute() -> tuple[bool, str]`
Method description: Validates if the action can be performed.
1. Verifies at least one target is selected and alive.
2. Checks if the actor has sufficient `floating_focus` to cover the template's `focus_cost`.

###### get_hooks [ARCH.DOC.battle.BattleActions.AttackAction.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Retrieves ephemeral hooks defined in the action template.
1. Iterates through `template.effects`.
2. Matches effect IDs with `EFFECT_HOOK_BUILDERS` to generate and return a dictionary of hook callbacks.

###### execute [ARCH.DOC.battle.BattleActions.AttackAction.execute]
`execute() -> ActionLoad`
Method description: Resolves the attack according to the standard Combat Flow. Handles resource consumption, Master Rolls for AoE, and individual target resolution. Initializes stat metrics (`pre`, `bda`, `bdd`, `grd`, `atk_die`, `def_die`) directly into the `AttackLoad` to support action-scoped stat modifications.
1. **Resource Consumption**: Deducts `focus_cost` from actor"s `floating_focus` and records `EXEC` and `FOCUS` events.
2. **Phase 1: Attack Roll**: 
   - If AoE, performs one "Master Roll" using `attack_load.atk_die` (emits `on_roll_modify` for the attacker).
   - If Single Target, the roll happens during individual resolution.
3. **Phase 2: Target Resolution Loop**: Iterates through each living target:
   - Emits `on_roll_modify`
   - Performs/Retrieves attack roll.
   - Performs defense roll using `attack_load.def_die`.
   - Emits `on_defense_reaction`.
   - Calculates `GdA = (Attack Roll + Rank + BDA) - (Defense Roll + Rank + BDD)`.
   - **Hit Validation**: Hit is successful if `GdA > (attack_load.grd - attack_load.pre)`.
   - If hit: Emits `on_hit_check`, `on_gda_modify`, `on_damage_calculation`, and `on_damage_taken`.
   - **Damage Application**: Calculates damage as `pda + (mda * max(0, GdA))`. Applies damage via `CharacterSystem.take_damage`.
   - Records `HIT`/`MISS`, `DMG`, and `HP` events.
4. **Finalization**: Emits `on_attack_end` for each target. If `BASIC_ATTACK`, generates actor focus. Returns `ActionLoad` with full history.

##### GenerateManaAction [ARCH.DOC.battle.BattleActions.GenerateManaAction]
[DEPENDS: ARCH.DOC.core.CharacterSystem.generate_mana, GDD.CORE.RESOURCES.MANA]
Standard Move Action to convert daily Mana into Floating MP.

- Constructor [ARCH.DOC.battle.BattleActions.GenerateManaAction.__init__]: `__init__(actor: Character, targets: List[Character], context: IActionContext, action_type: BattleActionType = BattleActionType.MOVE_ACTION)`

###### can_execute [ARCH.DOC.battle.BattleActions.GenerateManaAction.can_execute]
`can_execute() -> tuple[bool, str]`
Method description: Validates mana availability and floating capacity.
1. Checks if `current_mp` > 0.
2. Checks if `floating_mp` is below the manifest limit (`MEN * rules.limite_mana`).

###### execute [ARCH.DOC.battle.BattleActions.GenerateManaAction.execute]
`execute() -> ActionLoad`
Method description: Converts MP to floating mana.
1. Calls `CharacterSystem.generate_mana`.
2. Records `MANA_T` (total change) and `MANA_F` (floating change) events in `ActionLoad`.

##### GenerateFocusAction [ARCH.DOC.battle.BattleActions.GenerateFocusAction]
[DEPENDS: ARCH.DOC.core.CharacterSystem.generate_focus, GDD.CORE.RESOURCES.FOCUS]
Standard Move Action to replenish the character's focus pool.

- Constructor [ARCH.DOC.battle.BattleActions.GenerateFocusAction.__init__]: `__init__(actor: Character, targets: List[Character], context: IActionContext, action_type: BattleActionType = BattleActionType.MOVE_ACTION)`

###### can_execute [ARCH.DOC.battle.BattleActions.GenerateFocusAction.can_execute]
`can_execute() -> tuple[bool, str]`
Method description: Validates focus capacity.
1. Checks if `floating_focus` is below the limit (`MEN * rules.limite_foco`).

###### execute [ARCH.DOC.battle.BattleActions.GenerateFocusAction.execute]
`execute() -> ActionLoad`
Method description: Generates focus for the character.
1. Calls `CharacterSystem.generate_focus`.
2. Records a `FOCUS` event in `ActionLoad`.

##### TogglePosturaDefensiva [ARCH.DOC.battle.BattleActions.TogglePosturaDefensiva]
[DEPENDS: ARCH.RULES.CORE.COMMAND, GDD.STYLES.DESTRUIDOR.POSTURA_DEFENSIVA]
A Free Action that toggles the state of the 'Postura Defensiva' passive ability.

- Constructor [ARCH.DOC.battle.BattleActions.TogglePosturaDefensiva.__init__]: `__init__(actor: Character, targets: List[Character], context: IActionContext)`

###### execute [ARCH.DOC.battle.BattleActions.TogglePosturaDefensiva.execute]
`execute() -> ActionLoad`
Method description: Switches the stance of the defensive passive.
1. Retrieves the "Postura Defensiva" passive instance from `context.get_active_passive`.
2. Calls the passive's `toggle()` method.
3. Returns an `ActionLoad` containing the result message or an error if the passive is missing.

##### MudarPosturaBatalha [ARCH.DOC.battle.BattleActions.MudarPosturaBatalha]
[DEPENDS: ARCH.RULES.CORE.COMMAND, GDD.STYLES.MESTRE_ARMAS.POSTURAS, ARCH.DOC.battle.BattlePassives.PosturaBatalha]
A Free Action that toggles the state of the 'Postura de Batalha' passive ability.

- Constructor [ARCH.DOC.battle.BattleActions.MudarPosturaBatalha.__init__]: `__init__(actor: Character, targets: List[Character], context: IActionContext)`

###### execute [ARCH.DOC.battle.BattleActions.MudarPosturaBatalha.execute]
`execute() -> ActionLoad`
Method description: Switches the stance of the battle passive.
1. Retrieves the "Postura de Batalha" passive instance from `context.get_active_passive`.
2. Evaluates the current stance and determines the next in the cycle: `None` -> `OFFENSIVE` -> `DEFENSIVE` -> `None`.
3. Calls the passive's `set_mode()` method with the next mode and the current action load.
4. Returns an `ActionLoad` containing the result message or an error if the passive is missing.

#### BattlePassives.py [ARCH.DOC.battle.BattlePassives]
[DEPENDS: ARCH.RULES.CORE.IOC, ARCH.RULES.CORE.OBSERVER, ARCH.DOC.core.BaseClasses.BattlePassive]
Reactive components tied to character entities. Passives are instantiated at the start of battle and subscribe to event hooks to modify simulation outcomes, apply modifiers, or trigger secondary actions.

- `registry: Dict[str, Type[BattlePassive]]` [ARCH.DOC.battle.BattlePassives.registry]: Mapping of ability IDs to their concrete class implementations, used by `BattleManager` for character initialization.

##### ForçaBruta [ARCH.DOC.battle.BattlePassives.ForçaBruta]
[DEPENDS: GDD.STYLES.DESTRUIDOR.FORCA_BRUTA]
A straightforward offensive passive that multiplies success grade.

- Constructor [ARCH.DOC.battle.BattlePassives.ForçaBruta.__init__]: `__init__(owner: Character, context: IPassiveContext)`

###### get_hooks [ARCH.DOC.battle.BattlePassives.ForçaBruta.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Registers the doubling logic for successful hits.
1. `multiply_hook` (on `on_gda_modify`): If the owner hits, doubles the current `GdA` and records a `PASSIVE` trigger and an `ATK_LOAD` modification.

##### MãosPesadas [ARCH.DOC.battle.BattlePassives.MãosPesadas]
[DEPENDS: ARCH.DOC.battle.StatusEffects.Atordoado, GDD.STYLES.DESTRUIDOR.MAOS_PESADAS]
Utility passive that applies CC based on hit quality.

- Constructor [ARCH.DOC.battle.BattlePassives.MãosPesadas.__init__]: `__init__(owner: Character, context: IPassiveContext)`

###### get_hooks [ARCH.DOC.battle.BattlePassives.MãosPesadas.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Registers status application logic.
1. `effect_hook` (on `on_gda_modify`): If the owner hits with `GdA > 3`, instantiates and adds `Atordoado` status to the target. Records a `STATUS` event.

##### PosturaDefensiva [ARCH.DOC.battle.BattlePassives.PosturaDefensiva]
[DEPENDS: ARCH.RULES.BATTLE.PAYLOAD_TARGET_CHECK, ARCH.DOC.core.Modifiers.EphemeralModifier, GDD.STYLES.DESTRUIDOR.POSTURA_DEFENSIVA]
A complex, stateful stance that trades offensive accuracy for defensive stability and reactive penalties for attackers.

- Constructor [ARCH.DOC.battle.BattlePassives.PosturaDefensiva.__init__]: `__init__(owner: Character, context: IPassiveContext)`
- `is_active: bool` [ARCH.DOC.battle.BattlePassives.PosturaDefensiva.is_active]: Current state of the stance.
- `_tracked_targets: Dict[str, bool]` [ARCH.DOC.battle.BattlePassives.PosturaDefensiva._tracked_targets]: Maps character IDs to their penalty status.

###### toggle [ARCH.DOC.battle.BattlePassives.PosturaDefensiva.toggle]
`toggle() -> str`
Method description: Switches the stance on/off and updates actor stats.
1. If ON: Registers `atk_die` (-2) and `def_die` (+2) modifiers. Returns `POSTURA|actor|ON`.
2. If OFF: Removes die modifiers and clears all tracked target penalties. Returns `POSTURA|actor|OFF`.

###### get_hooks [ARCH.DOC.battle.BattlePassives.PosturaDefensiva.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Implements the reactive logic of the stance.
1. `hit_hook` (on `on_gda_modify`): While active, successful hits from the owner start tracking the target for penalties.
2. `penalty_hook` (on `on_roll_modify`): If a tracked target attacks the owner, applies a -1 penalty to `attack_load.pre`.
3. `cleanup_hook` (on `on_attack_end`): Removes tracking from the current attacker if they were tracked.
4. `turn_end_hook` (on `on_turn_end`): Safety cleanup for targets that were tracked but didn't attack.

##### GracaDoDuelista [ARCH.DOC.battle.BattlePassives.GracaDoDuelista]
[DEPENDS: ARCH.DOC.core.CharacterSystem.spend_focus, GDD.STYLES.DUELISTA.GRACA]
Advanced passive granting success bonuses and manual defensive reactions.

- Constructor [ARCH.DOC.battle.BattlePassives.GracaDoDuelista.__init__]: `__init__(owner: Character, context: IPassiveContext)`

###### get_hooks [ARCH.DOC.battle.BattlePassives.GracaDoDuelista.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Registers accuracy bonuses and reaction prompts.
1. `passiva_acerto_hook` (on `on_gda_modify`): Adds 1d6 to the owner's `GdA` for all attacks.
2. `reacao_evasao_hook` (on `on_defensive_reaction`): If the owner is targeted and hit, prompts the controller for a choice. If 2 Focus is spent, rolls 1d4 and subtracts from incoming `GdA`.

##### Combo [ARCH.DOC.battle.BattlePassives.Combo]
[DEPENDS: ARCH.DOC.battle.BattleActions.AttackAction, ARCH.DOC.battle.StatusEffects.Atordoado, GDD.STYLES.LUTADOR.COMBO]
Multi-stage passive that triggers recursive extra attacks on successful hits.

- Constructor [ARCH.DOC.battle.BattlePassives.Combo.__init__]: `__init__(owner: Character, context: IPassiveContext)`
- `stage: int` [ARCH.DOC.battle.BattlePassives.Combo.stage]: Current progression in the combo chain.

###### get_hooks [ARCH.DOC.battle.BattlePassives.Combo.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Implements recursive attack logic.
1. `checar_ataque_bonus` (on `on_attack_end`): 
   - Stage 0: If hit, executes a secondary `AttackAction`.
   - Stage 1: If previous and current hits successful, executes a third `AttackAction`.
   - Stage > 1: Applies `Atordoado` to the target on hit.
   - Merges sub-action histories into the main attack history using pipe-delimited events.

##### Bloquear [ARCH.DOC.battle.BattlePassives.Bloquear]
[DEPENDS: ARCH.DOC.core.CharacterSystem.spend_focus, GDD.STYLES.DEFENSOR.BLOQUEAR]
Defensive passive that allows focus-based reactions and grants counter-attack bonuses.

- Constructor [ARCH.DOC.battle.BattlePassives.Bloquear.__init__]: `__init__(owner: Character, context: IPassiveContext)`
- `_counter_targets: Dict[str, bool]` [ARCH.DOC.battle.BattlePassives.Bloquear._counter_targets]: Tracks attackers eligible for counter-bonuses.

###### get_hooks [ARCH.DOC.battle.BattlePassives.Bloquear.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Registers defensive reaction and counter-bonus hooks.
1. `reacao_bloqueio_hook` (on `on_defensive_reaction`): 
   - If targeted, checks for 2 Focus and controller approval.
   - Spends Focus and subtracts 1d4 from incoming `GdA`.
   - If final `GdA < -3`, marks the attacker for a counter-bonus.
2. `bonus_contra_ataque_hook` (on `on_roll_modify`): If the owner attacks a marked target, applies a +1 bonus to `attack_load.bda`.
3. `cleanup_bonus_hook` (on `on_attack_end`): Removes the target marking.

##### PosturaBatalha [ARCH.DOC.battle.BattlePassives.PosturaBatalha]
[DEPENDS: ARCH.DOC.core.Modifiers.EphemeralModifier, GDD.STYLES.MESTRE_ARMAS.POSTURAS, ARCH.DOC.core.Events.AttackLoad]
A stateful stance that grants offensive accuracy and damage bonuses, or defensive stability and reactive re-rolls, depending on the active mode.

- Constructor [ARCH.DOC.battle.BattlePassives.PosturaBatalha.__init__]: `__init__(owner: Character, context: IPassiveContext)`
- `current_postura: str | None` [ARCH.DOC.battle.BattlePassives.PosturaBatalha.current_postura]: Current state of the stance ("OFFENSIVE", "DEFENSIVE", or None).

###### set_mode [ARCH.DOC.battle.BattlePassives.PosturaBatalha.set_mode]
`set_mode(mode: str | None, action_load: ActionLoad) -> None`
Method description: Switches the stance on/off and updates actor stats via modifiers.
1. Removes any previously applied modifiers associated with this stance from the character.
2. If `OFFENSIVE`: Applies `grd` (-1) and `pre` (+1) modifiers. Records `POSTURA|actor|OFFENSIVE`.
3. If `DEFENSIVE`: Applies `pre` (-1) and `grd` (+1) modifiers. Records `POSTURA|actor|DEFENSIVE`.
4. If `None`: Records `POSTURA|actor|NONE`.

###### get_hooks [ARCH.DOC.battle.BattlePassives.PosturaBatalha.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Implements the reactive logic of the stance.
1. `on_gda_modify`: While `OFFENSIVE`, successful hits from the owner add +2 to `GdA`. If the attacker's `attack_roll > 7`, it adds +4 instead.
2. `on_defense_reaction`: While `DEFENSIVE` and the owner is targeted, prompts the controller for a re-roll reaction.
   - If approved and 2 Focus is spent: rolls `def_die` again, calculates the difference (`new_roll - old_defense_roll`), updates `GdA` and `defense_roll` inside `AttackLoad`, and registers the modification.

##### RitmoAcelerado [ARCH.DOC.battle.BattlePassives.RitmoAcelerado]
[DEPENDS: ARCH.DOC.core.Events.HistoryEmitter, ARCH.DOC.core.Enums.BattleActionType, GDD.STYLES.RETALHADOR.RITMO]
A dynamic rhythm passive that rewards consecutive successful attacks by reducing action costs and granting a precision bonus.

- Constructor [ARCH.DOC.battle.BattlePassives.RitmoAcelerado.__init__]: `__init__(owner: Character, context: IPassiveContext)`
- `consecutive_accelerations: int` [ARCH.DOC.battle.BattlePassives.RitmoAcelerado.consecutive_accelerations]: Counter for consecutive 7+ rolls.
- `processed_actions: set` [ARCH.DOC.battle.BattlePassives.RitmoAcelerado.processed_actions]: Tracks unique action IDs to prevent double counting in AoE or multi-target attacks.

###### get_hooks [ARCH.DOC.battle.BattlePassives.RitmoAcelerado.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Registers hooks for the rhythm logic.
1. `on_roll_modify`: If `consecutive_accelerations == 2`, grants +2 to `attack_load.pre`.
2. `on_attack_end`: On the first resolution of an action:
   - If `consecutive == 2`, resets the rhythm to 0.
   - If `attack_roll >= 7` and action is not a movement action, changes the action to `MOVE_ACTION`, increments `consecutive_accelerations`, and records the rhythm event.
   - Otherwise, resets the rhythm to 0.

#### Judges.py [ARCH.DOC.battle.Judges]
[DEPENDS: ARCH.DOC.core.BaseClasses.IBattleJudge, ARCH.DOC.core.Enums.BattleState]
Contains the logic for evaluating battle progression and determining final outcomes. Judges are invoked by the orchestrator to check for win/loss conditions based on the current state of the simulation.

##### BattleJudge [ARCH.DOC.battle.Judges.BattleJudge]
[DEPENDS: ARCH.DOC.core.CharacterSystem.is_alive, ARCH.DOC.core.Structs.BattleResult]
Standard team-based victory/defeat evaluator. Analyzes the survival of team members to determine the terminal state of the battle.

###### rule [ARCH.DOC.battle.Judges.BattleJudge.rule]
`rule(context: IJudgeContext, result: BattleResult) -> BattleState`
- `context: IJudgeContext`: Provides access to the list of active characters and the graveyard.
- `result: BattleResult`: Data structure to be populated with the lists of winners and losers upon battle completion.
Method description: Evaluates the presence of living characters in each team and updates the battle state.
1. Retrieves all characters from the context.
2. Checks for at least one living member in Team 1 and Team 2 using `CharacterSystem.is_alive`.
3. Determines the `BattleState`:
   - `RUNNING`: Both teams have living members.
   - `VICTORY`: Only Team 1 has living members.
   - `DEFEAT`: Only Team 2 has living members.
   - `DRAW`: No living members remain in either team.
4. If the state is terminal (not `RUNNING`):
   - Clears existing `winners` and `losers` in the `result` object.
   - Combines active characters and the graveyard into a full participant list.
   - Populates `winners` and `losers` lists based on the determined state and team alignment.
   - In a `DRAW`, everyone is moved to the `losers` list.
5. Returns the final `BattleState`.

#### StatusEffects.py [ARCH.DOC.battle.StatusEffects]
[DEPENDS: ARCH.RULES.BATTLE.STATUS_HOOKS, ARCH.DOC.core.BaseClasses.StatusEffect]
Defines temporary conditions (buffs/debuffs) applied to characters. Status effects utilize the Passive system to hook into game events and the Modifier stack to alter statistics, managing their own lifecycle and cleanup.

##### Atordoado [ARCH.DOC.battle.StatusEffects.Atordoado]
[DEPENDS: ARCH.RULES.BATTLE.TIMELINE, ARCH.DOC.core.CharacterSystem]
Stun condition that penalizes defense and delays the character's next turn.

- Constructor [ARCH.DOC.battle.StatusEffects.Atordoado.__init__]: `__init__(duration: int, target: Character, context: IPassiveContext)`

###### apply [ARCH.DOC.battle.StatusEffects.Atordoado.apply]
`apply() -> None`
Method description: Triggers the stun's immediate impact.
1. Registers an `EphemeralModifier` to `bdd` (-1) via `_add_modifier`.
2. Calls `context.delay_character` to increase the character's tick count by 50% of their base `action_cost`.

###### get_hooks [ARCH.DOC.battle.StatusEffects.Atordoado.get_hooks]
`get_hooks() -> Dict[str, Callable]`
Method description: Monitors turn progression to manage expiration.
1. `check_stun_end` (on `on_turn_start`): If the owner\"s turn starts, records a `STATUS_HOOK` activation and a `STATUS` removal event, then calls `remove()` to end the effect.

### MODULE: Entities [ARCH.DOC.entities]
The `entities` module contains data-only classes representing game objects. `[ARCH.RULES.CORE.ENTITIES]`

#### Characters.py [ARCH.DOC.entities.Characters]
[DEPENDS: ARCH.RULES.CORE.ENTITIES, ARCH.RULES.CORE.MODIFIER]
The primary data container for actors. Characters are designed as anemic entities that hold state (HP, MP, Focus) and a reactive stack of modifiers used for dynamic attribute calculation.

##### Character [ARCH.DOC.entities.Characters.Character]
[DEPENDS: ARCH.DOC.core.Structs.CombatStyle, ARCH.DOC.core.Structs.GameRules, ARCH.DOC.entities.Items.Armor, ARCH.DOC.entities.Items.Weapon, ARCH.DOC.core.Modifiers.StatModifier, ARCH.DOC.core.BaseClasses.StatusEffect, GDD.CORE.ATTR, GDD.STYLES.DEFINITION]
Data container representing a character's traits, equipment, and current vitals.

- Constructor [ARCH.DOC.entities.Characters.Character.__init__]: `__init__(char_id: str, name: str, attributes: List[int], combat_style: CombatStyle, rules: GameRules, team: int = 0)`
- `char_id: str` [ARCH.DOC.entities.Characters.Character.char_id]: Unique identifier for the character.
- `team: int` [ARCH.DOC.entities.Characters.Character.team]: Alliance identifier used by `BattleJudge`.
- `current_hp: int` [ARCH.DOC.entities.Characters.Character.current_hp]: Current health points.
- `current_mp: int` [ARCH.DOC.entities.Characters.Character.current_mp]: Daily mana reserve.
- `floating_mp: int` [ARCH.DOC.entities.Characters.Character.floating_mp]: Manifested mana available for immediate use.
- `floating_focus: int` [ARCH.DOC.entities.Characters.Character.floating_focus]: Current focus points pool.
- `modifiers: List[StatModifier]` [ARCH.DOC.entities.Characters.Character.modifiers]: Stack of active attribute modifiers.
- `status_effects: List[StatusEffect]` [ARCH.DOC.entities.Characters.Character.status_effects]: Collection of active temporary conditions.

###### get_stat_total [ARCH.DOC.entities.Characters.Character.get_stat_total]
`get_stat_total(stat_name: str, base_value: int) -> int`
- `stat_name: str`: The name of the attribute to calculate.
- `base_value: int`: The initial value before modifiers.
Method description: Computes the real-time value of an attribute by processing the modifier stack. `[ARCH.RULES.CORE.MODIFIER]`
1. Initializes `total` with the `base_value`.
2. Iterates through all `modifiers`.
3. If a modifier's `stat_name` matches, adds its value to the total.
4. Returns the final computed value.

###### Attribute Properties [ARCH.DOC.entities.Characters.Character.attributes]
Dynamic properties that use `get_stat_total` to return current values:
- `rank: int`: Combat Rank bonus.
- `bda: int`: Attack Bonus.
- `bdd: int`: Defense Bonus.
- `pre: int`: Precision (Hit accuracy).
- `grd: int`: Guard (Evasion threshold).
- `pda: int`: Power of Attack (Base damage).
- `mda: int`: Multiplier of Attack (Degree of Success influence).
- `atk_die / def_die: int`: Die sides used for attack/defense rolls.

###### add_modifier [ARCH.DOC.entities.Characters.Character.add_modifier]
`add_modifier(modifier: StatModifier) -> None`
- Method description: Appends a new `StatModifier` to the character's stack.

###### remove_modifier [ARCH.DOC.entities.Characters.Character.remove_modifier]
`remove_modifier(modifier: StatModifier) -> None`
- Method description: Removes a specific `StatModifier` instance from the stack.

###### clear_ephemeral_modifiers [ARCH.DOC.entities.Characters.Character.clear_ephemeral_modifiers]
`clear_ephemeral_modifiers() -> None`
- Method description: Mass cleanup of temporary combat modifiers.
1. Filters the `modifiers` list, retaining only non-ephemeral instances.

###### remove_modifiers_by_source [ARCH.DOC.entities.Characters.Character.remove_modifiers_by_source]
`remove_modifiers_by_source(source: str) -> None`
- `source: str`: The name of the modifier source to be cleared.
- Method description: Removes all modifiers originating from a specific source (e.g., a specific skill or status).

#### Items.py [ARCH.DOC.entities.Items]
[DEPENDS: ARCH.RULES.CORE.ENTITIES, ARCH.DOC.core.Enums.WeaponType, ARCH.DOC.core.Enums.ArmorType]
Defines the data structures for equipment. These classes are anemic data containers used by `CharacterSystem` and `DataManager` to influence character statistics and equipment compatibility.

##### Weapon [ARCH.DOC.entities.Items.Weapon]
Data structure representing an offensive item.

- Constructor [ARCH.DOC.entities.Items.Weapon.__init__]: `Weapon(name: str, db: int, mda: int, type: WeaponType, properties: List[str] = [])`
- `name: str` [ARCH.DOC.entities.Items.Weapon.name]: Display name of the weapon.
- `db: int` [ARCH.DOC.entities.Items.Weapon.db]: Damage Bonus added to the base PDA.
- `mda: int` [ARCH.DOC.entities.Items.Weapon.mda]: Multiplier of Attack value.
- `type: WeaponType` [ARCH.DOC.entities.Items.Weapon.type]: Classification for compatibility checks with combat styles.
- `properties: List[str]` [ARCH.DOC.entities.Items.Weapon.properties]: List of special traits or tags associated with the item.

##### Armor [ARCH.DOC.entities.Items.Armor]
Data structure representing a defensive item.

- Constructor [ARCH.DOC.entities.Items.Armor.__init__]: `Armor(name: str, type: ArmorType, hp_bonus: int, properties: List[str] = [])`
- `name: str` [ARCH.DOC.entities.Items.Armor.name]: Display name of the armor.
- `type: ArmorType` [ARCH.DOC.entities.Items.Armor.type]: Classification for compatibility checks with combat styles.
- `hp_bonus: int` [ARCH.DOC.entities.Items.Armor.hp_bonus]: Health points added to the character's max HP pool.
- `properties: List[str]` [ARCH.DOC.entities.Items.Armor.properties]: List of special traits or tags associated with the item.

### MODULE: Controllers [ARCH.DOC.controllers]
The `controllers` module implements the "Decision Loop" for characters, separating AI/Player logic from the engine. `[ARCH.RULES.CORE.MVC]`

#### CharacterController.py [ARCH.DOC.controllers.CharacterController]
[DEPENDS: ARCH.RULES.CORE.MVC, ARCH.DOC.core.BaseClasses.IControllerContext, ARCH.DOC.core.Events.ActionLoad]
Defines the "Decision Loop" interface that separates character behavior (AI or Player) from engine mechanics. Controllers analyze the current `IControllerContext` to issue combat commands.

- `registry: Dict[str, Type[CharacterController]]` [ARCH.DOC.controllers.CharacterController.registry]: Mapping of controller IDs to their concrete class implementations, used for character assignment.

##### CharacterController [ARCH.DOC.controllers.CharacterController.CharacterController]
Abstract base class defining the mandatory interface for tactical decision-making and reactive choices.

###### choose_action [ARCH.DOC.controllers.CharacterController.CharacterController.choose_action]
`choose_action(actor: Character, context: IControllerContext, action_load: ActionLoad | None = None) -> BattleAction`
- `actor: Character`: The character whose turn is being processed.
- `context: IControllerContext`: Interface for accessing battle participants, data templates, and the timeline.
- `action_load: ActionLoad | None`: If provided, indicates a previous execution attempt failed, allowing for re-decision. `[ARCH.RULES.BATTLE.DECISION]`
Method description: Triggered at the beginning of a character's turn to determine their maneuver.
1. Must analyze the battlefield and resource availability.
2. Returns a concrete `BattleAction` instance ready for execution.
3. Raises `NotImplementedError` by default.

###### choose_reaction [ARCH.DOC.controllers.CharacterController.CharacterController.choose_reaction]
`choose_reaction(actor: Character, reaction_id: str, action_load: ActionLoad, context: IControllerContext) -> bool`
- `reaction_id: str`: Identifier for the specific conditional effect being triggered.
Method description: Triggered during action resolution (e.g., in a defensive reaction hook).
1. Allows the controller to opt-in or opt-out of a conditional effect based on the current `action_load`.
2. Returns `True` to activate the reaction, `False` otherwise.
3. Raises `NotImplementedError` by default.

##### PvP1v1Controller [ARCH.DOC.controllers.CharacterController.PvP1v1Controller]
[DEPENDS: ARCH.DOC.battle.BattleActions.AttackAction]
Reference implementation for automated 1v1 combat.

###### choose_action [ARCH.DOC.controllers.CharacterController.PvP1v1Controller.choose_action]
`choose_action(actor: Character, context: IControllerContext, action_load: ActionLoad | None = None) -> BattleAction`
Method description: Implements basic aggressive AI logic.
1. Identifies the first character in the context that is not the actor.
2. **Re-decision Handling**: If `action_load` is present (indicating a previous failure), defaults to a `BASIC_ATTACK` to prevent infinite loops.
3. **Skill Prioritization**: Checks `floating_focus` against the cost of the "SkillN1" template.
4. If focus is sufficient, returns an `AttackAction` using the skill template.
5. Otherwise, returns a standard `BASIC_ATTACK` (AttackAction with template=None).

###### choose_reaction [ARCH.DOC.controllers.CharacterController.PvP1v1Controller.choose_reaction]
`choose_reaction(...) -> bool`
Method description: Automatically accepts all triggered reactions.
1. Always returns `True`.

### MODULE: Data [ARCH.DOC.data]
The `data` module stores external JSON definitions that drive engine behavior and character scaling. `[ARCH.RULES.CORE.DATA]`

#### Action Definitions [ARCH.DOC.data.AttackActions]
[DEPENDS: ARCH.RULES.CORE.DATA, ARCH.DOC.core.Enums.BattleActionType, ARCH.DOC.core.Enums.AttackType, ARCH.DOC.battle.BattleActions.EFFECT_HOOK_BUILDERS]
JSON-based blueprints for combat maneuvers. These templates are loaded by `DataManager` and used to instantiate `AttackAction` objects.

- `nome: str`: The display name of the maneuver.
- `action_type: str`: Economy category (`standard_action`, `move_action`, etc.) mapped to `BattleActionType`.
- `attack_type: str`: Classification (`basic_attack`, `skill`, `area`) mapped to `AttackType`.
- `focus_cost: int`: Amount of `floating_focus` consumed upon execution.
- `effects: List[Dict]`: Collection of objects defining `id` (mapped to hook builders) and optional `parameters` for behavior modification.

#### Character Templates [ARCH.DOC.data.Characters]
[DEPENDS: ARCH.RULES.CORE.DATA, ARCH.DOC.core.Enums.AttributeType, ARCH.DOC.entities.Items.Weapon, ARCH.DOC.entities.Items.Armor, ARCH.DOC.core.Structs.CombatStyle]
JSON-based hydration templates for characters. Defines the starting state, equipment, and abilities for specific character archetypes.

- `Nome: str`: Display name of the character.
- `FIS / HAB / MEN: int`: Base attribute scores used for pool calculations and damage.
- `Weapon / Armor: Dict`: Defines the starting equipment name, stats, and types.
- `Abilities / Passives: List[str]`: Identifiers for the actions and reactive components assigned to the character at start.
- `CombatStyle: str`: Reference to the archetype definition in `CombatStyles.json`.

#### Combat Styles [ARCH.DOC.data.CombatStyles]
[DEPENDS: ARCH.RULES.CORE.DATA, ARCH.DOC.core.Enums.WeaponType, ARCH.DOC.core.Enums.ArmorType]
JSON-based archetype definitions. These entries govern the fundamental combat parameters of a character.

- `atq_die / def_die: int`: Number of sides on the dice used for attack and defense rolls.
- `main_stat: str`: The attribute used for base damage calculation (PDA).
- `armor_type / weapon_type: str`: Compatibility tags used to validate equipment swaps.

#### Game Rules [ARCH.DOC.data.Rules]
[DEPENDS: ARCH.RULES.CORE.DATA, ARCH.RULES.CORE.MODIFIER]
JSON-based configuration for global constants and progression tables. Defines the core math and scaling of the system.

- `limite_foco / limite_mana: int`: Multipliers used against the `MEN` attribute to determine maximum manifest pools.
- `regras_progressao: Dict`: Contains nested tables (`tabela_hp`, `tabela_mp`, `tabela_custos`) mapping attribute scores (0-15) to their corresponding derived pool sizes or tick costs.

### MODULE: Utilities [ARCH.DOC.utilities]
The `utilities` module provides cross-cutting tools for documentation management, system operations, and agent assistance.

#### ref_manager.py [ARCH.DOC.utilities.ref_manager]
[DEPENDS: ARCH.DOC_STANDARDS.MODULE, AGENT.REF_MANAGER]
The central architectural utility for documentation extraction, recursive dependency resolution, and automated maintenance. It ensures agents can access and modify the project's knowledge base with precision and hierarchical integrity.

- `PATH_MAPPING: Dict[str, str]` [ARCH.DOC.utilities.ref_manager.PATH_MAPPING]: Configuration dictionary mapping tag prefixes (e.g., `ARCH.`, `GDD.`, `WORKFLOWS.`) to their source markdown files.

##### get_path_for_tag [ARCH.DOC.utilities.ref_manager.get_path_for_tag]
`get_path_for_tag(tag: str) -> str | None`
Method description: Determines the correct source file path for a given tag.
1. Normalizes the tag by stripping brackets.
2. Matches the prefix against `PATH_MAPPING`.
3. Returns the mapped path or `None` if no prefix matches.

##### find_tag_range [ARCH.DOC.utilities.ref_manager.find_tag_range]
`find_tag_range(tag: str, lines: List[str]) -> Tuple[int | None, int | None, bool | None]`
Method description: Locates the line range of a specific tag within a list of strings.
1. **Pass 1 (Header Search)**: Searches for the tag within Markdown headers (`#`). Skips content inside code blocks.
2. **Pass 2 (Fallback Search)**: If not found in a header, searches for the tag in any line (excluding dependency declarations).
3. **Range Calculation**:
   - If a header is found, determines the section end by looking for the next header of equal or higher level.
   - Truncates trailing blank lines from the section.
   - If a standard line is found, the range is the single line.
4. Returns the start index, end index, and a boolean indicating if it is a header section.

##### extract_section [ARCH.DOC.utilities.ref_manager.extract_section]
`extract_section(tag: str, file_path: str) -> str | None`
Method description: Retrieves the content associated with a tag.
1. Reads the file at `file_path`.
2. Calls `find_tag_range` to identify the content block.
3. Returns the joined and cleaned text of the range.

##### update_section [ARCH.DOC.utilities.ref_manager.update_section]
`update_section(tag: str, new_content: str, file_path: str) -> Tuple[bool, str]`
Method description: Replaces existing tag content with new text.
1. Identifies the tag range.
2. Swaps the old lines with the `new_content`, ensuring proper newline termination.
3. Writes the updated content back to the file.

##### create_section [ARCH.DOC.utilities.ref_manager.create_section]
`create_section(content: str, file_path: str, target_tag: str | None) -> Tuple[bool, str]`
Method description: Injects new documentation using **Smart Placement** and **Fail-Fast Validation**.
1. **Existence Check**: Prevents duplicate tags in the target file.
2. **Placement Logic**:
   - Identifies the parent prefix (e.g., `A.B` for `A.B.C`).
   - Searches for the last sibling (another `A.B.*` tag).
   - If no siblings exist, searches for the parent header.
   - Places the new content immediately after the identified range.
3. **Validation**: Fails with a descriptive error if the parent or root file identifier is missing.
4. **Spacing**: Automatically manages blank lines above and below the new section for Markdown readability.

##### delete_section [ARCH.DOC.utilities.ref_manager.delete_section]
`delete_section(tag: str, file_path: str) -> Tuple[bool, str]`
Method description: Removes a tag and its associated content.
1. Identifies the tag range and removes the lines.
2. **Spanning Cleanup**: Automatically collapses redundant blank lines created by the deletion at the start, middle, or end of the file.

##### resolve_tag [ARCH.DOC.utilities.ref_manager.resolve_tag]
`resolve_tag(tag: str, resolved_tags: Set[str] | None = None, parent_file: str | None = None, current_depth: int = 0, max_depth: int = 1) -> str`
Method description: The recursive solver for the dependency system.
1. Identifies the source file and prevents circular resolution via `resolved_tags`.
2. Extracts the base content for the tag.
3. If the content is a header section, automatically marks all other tags within that section as resolved to prevent redundant extraction.
4. **Dependency Resolution**:
   - Parses the `[DEPENDS: ...]` line immediately following the header.
   - Recursively calls itself for each dependency up to `max_depth`.
   - Concatenates dependency contents above the current tag's content using separators.
5. **Cross-File Tracking**: Adds a `> [FROM: filename]` breadcrumb if the resolved dependency comes from a different file.

##### CLI Usage [ARCH.DOC.utilities.ref_manager.CLI]
Method description: Command-line interface for manual and agent-driven maintenance.
- **Output Management**: All results are printed to STDOUT and mirrored to `output.txt` to avoid truncation.
- **Commands**: Supports `--depth`, `--update`, `--create`, and `--delete` flags.

### MODULE: Views [ARCH.DOC.views]
Contains modules responsible for presenting data to the user or translating internal state to human-readable formats.

#### BattleView.py [ARCH.DOC.views.BattleView]
[DEPENDS: ARCH.RULES.CORE.MVC, ARCH.RULES.CORE.HISTORY, ARCH.DOC.core.Structs.BattleResult]
The Presentation layer of the combat engine. BattleView translates structured history logs (pipe-delimited tags) into human-readable narrative strings and handles terminal output for battle results and aggregated statistics.

##### BattleView [ARCH.DOC.views.BattleView.BattleView]
[DEPENDS: ARCH.DOC.entities.Characters.Character]
Orchestrator for presenting battle information to the user.

###### present_battle [ARCH.DOC.views.BattleView.BattleView.present_battle]
`present_battle(result: BattleResult) -> None`
- `result: BattleResult`: The data container holding the complete history and outcome of a battle.
Method description: Processes and displays the full narrative of a single battle.
1. Iterates through each entry in `result.history`.
2. Passes each entry to `_parse_entry` and prints the resulting narrative string.
3. Aggregates the final HP state of all winners and losers.
4. Prints a formatted end-of-battle summary block.

###### present_summary [ARCH.DOC.views.BattleView.BattleView.present_summary]
`present_summary(results: List[BattleResult], char1_id: str, char2_id: str) -> None`
- `results: List[BattleResult]`: A collection of battle outcomes for statistical analysis.
- `char1_id / char2_id: str`: Character IDs used to track win/loss distribution.
Method description: Computes and displays aggregated statistics for a series of battles.
1. Tracks total battles, wins for each character, draws, and total turn duration.
2. For each result:
   - Accumulates turn count.
   - Evaluates the `winners` list against provided IDs to identify the victor (handling 1v1 logic and empty winner lists as draws).
3. Calculates average turn duration.
4. Prints a comprehensive report including win counts, draw counts, total turns, and averages.

###### _parse_entry [ARCH.DOC.views.BattleView.BattleView._parse_entry]
`_parse_entry(entry: str) -> str`
- `entry: str`: A pipe-delimited history tag (e.g., `EXEC|BasicAttack|Aragorn`).
Method description: The translation engine that converts technical tags into narrative strings.
1. Splits the string by the `|` delimiter.
2. Matches the first element (the tag) against known identifiers:
   - `EXEC`: Action usage.
   - `ROLL`: Dice roll details.
   - `MOD`: Attribute modifications.
   - `HIT / MISS`: Accuracy outcomes.
   - `DMG`: Damage application.
   - `HP / FOCUS / MANA_F / MANA_T`: Dynamic stat updates.
   - `STATUS`: Application or removal of temporary conditions.
   - `TURN_START`: Comprehensive status dump at the start of a turn.
   - `DEATH`: Defeat notification.
   - `PASSIVE`: Passive ability triggers.
   - `ACTION_HOOK / STATUS_HOOK`: Reactive hook activations.
   - `ATK_LOAD`: Action-scoped stat modifications.
3. Returns a formatted string with a category prefix (e.g., `[ACTION]`, `[ROLL]`).
4. Gracefully falls back to the raw string on error or unknown tags.

###### parse [ARCH.DOC.views.BattleView.BattleView.parse]
`parse(history: List[str]) -> List[str]`
- Method description: Legacy static wrapper for `_parse_entry` used for backward compatibility. Iterates through a list and returns a list of translated strings.

## Test Quality Standards [ARCH.TEST_QUALITY]

- **Behavior over Implementation [ARCH.TEST_QUALITY.TEST_BEHAVIOR]:** Tests MUST verify the outcome (e.g., final HP, ActionLoad, state changes) rather than internal implementation details (e.g., checking specific list indices or private method calls).
- **Controlled Mocking [ARCH.TEST_QUALITY.MOCKING]:** Use real instances for domain logic (Entities, Systems). Mock ONLY system boundaries (I/O, UI) or to enforce determinism. Use `DiceManager.schedule_result()` for simulating dice rolls.
- **Entity Factory [ARCH.TEST_QUALITY.ENTITY_FACTORY]:** Use `tests.utils.entity_factory` when instantiating entities for tests. Use `DataManager` for getting entities only in integration tests.
- **Data Integrity [ARCH.TEST_QUALITY.DATA_INTEGRITY]:** For integration tests using `DataManager`, use `tests.utils.json_integrity_checker.get_json_keys()` to dynamically iterate over and verify all IDs in game data. This ensures tests remain decoupled from specific balance values while guaranteeing hydration logic works for all defined content.
- **Decoupling [ARCH.TEST_QUALITY.DECOUPLING]:** Ensure tests do not break upon internal refactors if the public behavior remains unchanged.
- **Invariants [ARCH.TEST_QUALITY.INVARIANTS]:** Assert that attribute modifiers `[ARCH.RULES.CORE.MODIFIER]` are properly used and Character atributes are not corrupted by bad modifications.
- **Lifecycle Auditing** [ARCH.TEST_QUALITY.LIFECYCLE]: Tests involving the EventBus MUST verify that all ephemeral hooks ([ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]) used by self modifying actions are successfully unsubscribed after the action cycle. Assert that the EventBus subscriber count returns to its baseline.
- **Battle Context [ARCH.TEST_QUALITY.IBATTLECONTEXT]:** Get a `BattleManager` with `create_test_battle_manager()` from `tests/utils/test_utils.py` when a concrete implementation of `IBattleContext` (or any of its segregated forms like `IActionContext`, `IPassiveContext`) is required for behavioral tests, avoid mocking of the battle state.
- **Testing Actions [ARCH.TEST_QUALITY.ACTIONS]:** When testing the outcome of an BattleAction, you should: use `BattleManager.add_character()` to add all actors in the battle (use 'start_tick = 1000' to facilitate timeline manipulation), use `BattleManager.set_tick()` to manipulate the timeline if necessary, use `BattleManager.get_next_actor()` to take the actor you want out of the timeline, create a `BattleAction` with that actor and call `BattleManager.run_action` with that action. The actor will be reinserted in the timeline unless you executed a free action. 
- **Structured History [ARCH.TEST_QUALITY.STRUCTURED_HISTORY]:** Tests verifying action outcomes MUST assert against structured event tags (`TAG|PARAM1|PARAM2...`) rather than narrative strings or partial substrings of `MSG` tags. This ensures tests remain resilient to localization changes and narrative polish. `[ARCH.RULES.CORE.HISTORY]`
- **AttackAction Data Loading [ARCH.TEST_QUALITY.ATTACK_ACTION_DATA]:** Abilities implemented through `AttackActions` MUST be tested by loading their `AttackActionTemplate` through `DataManager` from `data/AttackActions.json`. This ensures tests reflect actual game data definitions and prevents discrepancies between hardcoded mocks and production content.

## Documentation Standards [ARCH.DOC_STANDARDS]

### MISSION [ARCH.DOC_STANDARDS.MISSION]

#### ENTRY FORMAT [ARCH.DOC_STANDARDS.MISSION.ENTRY]

```
- **Header:** ## MISSION: [Title] [PART X] [MISSION.ACTIVE.TITLE_OF_MISSION]. Add `[PART X]` only if mission have more parts.
- **Summary**: Concise technical overview of the goal. Provide enough context to guide execution.
- **Rule References**: Comma-separated list ARCH.RULES tags of architectural rules relevant to the mission`.
- **Documentation References**: Comma-separated list ARCH.DOC.module_name.FileName.ClassName tags for relevant classes documentation.
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

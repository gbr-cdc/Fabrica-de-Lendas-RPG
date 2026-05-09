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
- **Data-Driven Attacks [ARCH.RULES.BATTLE.ATTACK_DATA]:** AttackAction constructor receives an AttackAction template. This template includes list of effects to modify the AttackAction resolution. Each effect have an id and a list of paramenters. AttackAction uses the effects ids to find and call hook builders that return returns a tuple {"signal", hook_function}. BattleManager handles those hooks, following [ARCH.RULES.CORE.IOC] and [ARCH.RULES.BATTLE.EPHEMERAL_HOOKS].

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

### MODULE: core [ARCH.DOC.core]
Comprehensive description of the foundational entities, systems, data structures, and interfaces that comprise the core logic of the engine. It dictates how game data is loaded, how randomness is resolved, how entities modify each other, and defines the base abstractions for combat.

#### Enums.py [ARCH.DOC.core.Enums]
Defines the fundamental enumerations used throughout the system for typing and categorizing entities, attacks, and battle states.

##### RollState [ARCH.DOC.core.Enums.RollState]
[DEPENDS: GDD.COMBAT.FLOW.ADV, GDD.COMBAT.FLOW.DSV]
Enum representing advantage mechanics: ADVANTAGE = "advantage", DISADVANTAGE = "disadvantage", NEUTRAL = "neutral".

##### ArmorType [ARCH.DOC.core.Enums.ArmorType]
[DEPENDS: GDD.EQUIP.TYPES.ARMORS]
Enum representing armor weight categories: ROBE = "robe", LIGHT = "light", HEAVY = "heavy".

##### WeaponType [ARCH.DOC.core.Enums.WeaponType]
[DEPENDS: GDD.EQUIP.TYPES.WEAPONS]
Enum representing weapon classifications: GREAT_WEAPON = "great_weapon", MEDIUM_WEAPON = "medium_weapon", LIGHT_WEAPON = "light_weapon", DOUBLE_WEAPON = "double_weapon", WEAPON_AND_SHIELD = "weapon_and_shield", RANGED_WEAPON = "ranged_weapon", MAGICAL_FOCUS = "magical_focus".

##### AttributeType [ARCH.DOC.core.Enums.AttributeType]
[DEPENDS: GDD.CORE.ATTR]
Enum for base character attributes: FIS = "FIS", HAB = "HAB", MEN = "MEN".

##### StatusEffectType [ARCH.DOC.core.Enums.StatusEffectType]
[DEPENDS: GDD.STATUS]
Enum for names of standard status effects: ATORDOADO = "Atordoado", DESEQUILIBRADO = "Desequilibrado", DERRUBADO = "Derrubado".

##### AttackType [ARCH.DOC.core.Enums.AttackType]
Enum classifying offensive maneuvers: BASIC_ATTACK = "basic_attack", SKILL = "skill", EXTRA_ATTACK = "extra_attack", AREA = "area".

##### BattleActionType [ARCH.DOC.core.Enums.BattleActionType]
[DEPENDS: GDD.CORE.TIME.ACTION_TYPES]
Enum for action economy categories: MOVE_ACTION = "move_action", STANDARD_ACTION = "standard_action", FREE_ACTION = "free_action".

##### BattleState [ARCH.DOC.core.Enums.BattleState]
Enum for high-level combat outcomes: VICTORY = "victory", DEFEAT = "defeat", DRAW = "draw", RUNNING = "running", ERROR = "error".

#### Structs.py [ARCH.DOC.core.Structs]
Provides pure data container structures (DTOs) for passing complex configuration and state across domains.

##### GameRules [ARCH.DOC.core.Structs.GameRules]
[DEPENDS: GDD.CORE.PROG, ARCH.RULES.CORE.DATA]
Configuration for global mechanics. 

- `hp_table: Dict[str, int]` [ARCH.DOC.core.Structs.GameRules.hp_table]: HP progression table. FIS attribute determines HP value.
- `mp_table: Dict[str, int]` [ARCH.DOC.core.Structs.GameRules.mp_table]: MP progression table. MEN attribute determines MP value.
- `action_cost_table: Dict[str, int]` [ARCH.DOC.core.Structs.GameRules.mp_table]: Action Cost progression table. HAB attribute determines action cost value.
- `limite_foco: int` [ARCH.DOC.core.Structs.GameRules.limite_foco]: Determines how much foco a character can hold at max. The limit is `limite_foco` * MEN.
- `limite_mana: int` [ARCH.DOC.core.Structs.GameRules.limite_mana]: Determines how much floating mana a character can hold at max. The limit is `limite_mana` * MEN.

##### RollResult [ARCH.DOC.core.Structs.RollResult]
[DEPENDS: ARCH.DOC.core.Enums.RollState]
Encapsulates a dice roll outcome. Used by DiceManager and the Event Bus.

- `final_roll: int` [ARCH.DOC.core.Structs.RollResult.final_roll]: Final roll result. This result must be used.
- `roll1: int` [ARCH.DOC.core.Structs.RollResult.roll1]: First roll.
- `roll2: int | None = None` [ARCH.DOC.core.Structs.RollResult.roll2]: Second roll in case `rollstate` is `RollState.ADVANTAGE` or `RollState.DISADVANTAGE`.
- `rollstate: RollState = RollState.NEUTRAL` [ARCH.DOC.core.Structs.RollResult.rollstate]: If `RollState.ADVANTAGE`, two dice are rolled, `final_roll` is the higher roll. If `RollState.DISADVANTAGE`, two dice are rolled, `final_roll` is the lower roll.
- `scheduled: bool = False` [ARCH.DOC.core.Structs.RollResult.scheduled]: It's true in case the result was poped from the scheduled results queue and no dice was rolled.

##### BattleResult [ARCH.DOC.core.Structs.BattleResult]
[DEPENDS: ARCH.DOC.core.BaseClasses.IBattleJudge]
Summary of a finished combat.

- `history: List[str] = field(default_factory=list)` [ARCH.DOC.core.Structs.BattleResult.history]: List of structured strings used to keep track of events happening in battle. `[ARCH.RULES.CORE.HISTORY]`, `[ARCH.TEST_QUALITY.STRUCTURED_HISTORY]`
- `winners: List[Character] = field(default_factory=list)` [ARCH.DOC.core.Structs.BattleResult.winners]: List of winner characters, populated by a `BattleJudge` when a win condition is achieved.
- `losers: List[Character] = field(default_factory=list)` [ARCH.DOC.core.Structs.BattleResult.losers]: List of loser characters, populated by a `BattleJudge` when a win condition is achieved.
- `duration: int = 0` [ARCH.DOC.core.Structs.BattleResult.duration]: Total number of actions executed in the battle.
- `action_per_character: dict[str, int] = field(default_factory=dict)` [ARCH.DOC.core.Structs.BattleResult.action_per_character]: Dictionary that shows the total number of actions per character.

##### CombatStyle [ARCH.DOC.core.Structs.CombatStyle]
[DEPENDS: GDD.STYLES.DEFINITION, ARCH.DOC.core.Enums.ArmorType, ARCH.DOC.core.Enums.ArmorType, ARCH.RULES.CORE.DATA]
Archetype definition for a character's fighting method. Loaded from CombatStyles.json.

- `name: str` [ARCH.DOC.core.Structs.CombatStyle.name]: Combat style name.
- `atq_die: int` [ARCH.DOC.core.Structs.CombatStyle.atq_die]: Combat style attack die.
- `def_die: int` [ARCH.DOC.core.Structs.CombatStyle.def_die]: Combat style defense die.
- `main_stat: AttributeType` [ARCH.DOC.core.Structs.CombatStyle.main_stat]: Combat style main attribute.
- `armor_type: ArmorType` [ARCH.DOC.core.Structs.CombatStyle.armor_type]: `ArmorType` the character is allowed to equip.
- `weapon_type: WeaponType` [ARCH.DOC.core.Structs.CombatStyle.weapon_type]: `WeaponType` the character is allowed to equip.

##### AttackEffects [ARCH.DOC.core.Structs.AttackEffects]
[DEPENDS: ARCH.RULES.CORE.DATA, ARCH.RULES.BATTLE.ATTACK_DATA]
Data structure for individual components of an attack (e.g., "Lifesteal", "Stun").

- `id: str` [ARCH.DOC.core.Structs.AttackEffects.id]: String used to identify the effect in BattleActions.EFFECT_HOOK_BUILDERS.
- `parameters: Dict[str, Any]` [ARCH.DOC.core.Structs.AttackEffects]: List of parameters used in the effect. May be empty, but must exist.

##### AttackActionTemplate [ARCH.DOC.core.Structs.AttackActionTemplate]
[DEPENDS: ARCH.DOC.core.Structs.AttackEffects, ARCH.DOC.core.Enums.AttackType, ARCH.DOC.core.Enums.BattleActionType]
Blueprint for complex actions.

- `nome: str` [ARCH.DOC.core.Structs.AttackActionTemplate.nome]: Attack action name.
- `action_type: type['BattleActionType']` [ARCH.DOC.core.Structs.AttackActionTemplate.action_type]: `BattleActionType` used to decide the `action_cost`. 
- `attack_type: type['AttackType']` [ARCH.DOC.core.Structs.AttackActionTemplate.attack_type]: `AttackType`, used for some specific attack type logic. 
- `focus_cost: int` [ARCH.DOC.core.Structs.AttackActionTemplate.focus_cost]: focus cost of the action.
- `effects: List[AttackEffects] = field(default_factory=list)` [ARCH.DOC.core.Structs.AttackActionTemplate.effects]: List of effects to be applied to the action.

#### Events.py [ARCH.DOC.core.Events]
Defines payload objects used by the Event Bus to track history and state mutation during actions. 

##### ActionLoad [ARCH.DOC.core.Events.ActionLoad]
[DEPENDS: ARCH.RULES.CORE.OBSERVER, ARCH.RULES.CORE.HISTORY, ARCH.DOC.entities.Characters.Character]
Base payload for all battle actions.

- `character: 'Character'` [ARCH.DOC.core.Events.ActionLoad.character]: Character executing the action.
- `history: List[str] = field(default_factory=list)` [ARCH.DOC.core.Events.ActionLoad.history]: List of structured strings describing action history like action results and dice rolls.
- `success: bool = True` [ARCH.DOC.core.Events.ActionLoad.success]: Informs if the execution was a success or not. By success, it means the execution got to the end without problems, not that the action was a success in gameplay terms. A failing attack is a successful execution. `success is False` means the action could not be executed.
- `add_event(tag: str, *params: any) -> None` [ARCH.DOC.core.Events.ActionLoad.add_event]: Adds an event string to the history. Modifies the `history` list by appending a string formatted as `tag|param1|param2|...`. Does not raise exceptions.

##### AttackLoad [ARCH.DOC.core.Events.AttackLoad]
[DEPENDS: ARCH.DOC.core.Events.ActionLoad, ARCH.DOC.core.Enums.RollState, ARCH.DOC.core.Enums.AttackType, ARCH.DOC.core.BaseClasses.IBattleContext, ARCH.RULES.BATTLE.AREA_ATTACK, GDD.COMBAT.FLOW.GDA]
Specialized payload for offensive resolution, inheriting from ActionLoad.

- `target: Character | None = None` [ARCH.DOC.core.Events.AttackLoad.target]: Target of the attack action. Will be `None` in a "Master Roll" for an area attack, or have a single target for every attack resolution.
- `battle_context: 'IBattleContext'` [ARCH.DOC.core.Events.AttackLoad.battle_context]: Interface implemented by `battle.BattleManager`, allows interactions with the battle state like getting character and passives references, emiting events and manipulating the timeline.
- `attack_type: AttackType` [ARCH.DOC.core.Events.AttackLoad.attack_type]: Defines the type of the attack, e.g., "BASIC_ATTACK" or "SKILL".
- `attack_state: RollState` [ARCH.DOC.core.Events.AttackLoad.attack_state]: Defines `RollState` for the attack roll.
- `defense_state: RollState` [ARCH.DOC.core.Events.AttackLoad.defense_state]: Defines `RollState` for the defense roll.
- `gda: int = 0` [ARCH.DOC.core.Events.AttackLoad.gda]: GdA that will be used in damage calculation. Allows GdA modification after the value is defined by Attack - Defense.
- `damage: int = 0` [ARCH.DOC.core.Events.AttackLoad.damage]: This value will be added to the damage during damage calculation. Can be used to amplify or reduce the damage.
- `hit: bool = False` [ARCH.DOC.core.Events.AttackLoad.hit]: Defines if the attack was a hit or a miss. Starts as `False`, will be modified depending on GdA result before `on_hit_check` signal.

##### HistoryEmitter [ARCH.DOC.core.Events.HistoryEmitter]
Static utility class for generating standardized event tags for the history stream. Core dependencies: None. Internal state: None.
- exec(action_id: str, actor_id: str) -> str [ARCH.DOC.core.Events.HistoryEmitter.exec]: Returns formatted EXEC event string.
- roll(type: str, value: int, die_size: int, actor_id: str) -> str [ARCH.DOC.core.Events.HistoryEmitter.roll]: Returns formatted ROLL event string.
- mod(source_id: str, value: int, target_id: str) -> str [ARCH.DOC.core.Events.HistoryEmitter.mod]: Returns formatted MOD event string.
- hit(target_id: str) -> str [ARCH.DOC.core.Events.HistoryEmitter.hit]: Returns formatted HIT event string.
- miss(target_id: str) -> str [ARCH.DOC.core.Events.HistoryEmitter.miss]: Returns formatted MISS event string.
- dmg(target_id: str, amount: int, type: str) -> str [ARCH.DOC.core.Events.HistoryEmitter.dmg]: Returns formatted DMG event string.
- hp(entity_id: str, delta: int, current: int) -> str [ARCH.DOC.core.Events.HistoryEmitter.hp]: Returns formatted HP event string.
- focus(entity_id: str, delta: int, current: int) -> str [ARCH.DOC.core.Events.HistoryEmitter.focus]: Returns formatted FOCUS event string.
- mana_f(entity_id: str, delta: int, current: int) -> str [ARCH.DOC.core.Events.HistoryEmitter.mana_f]: Returns formatted MANA_F event string.
- mana_t(entity_id: str, delta: int, current: int) -> str [ARCH.DOC.core.Events.HistoryEmitter.mana_t]: Returns formatted MANA_T event string.
- msg(message: str) -> str [ARCH.DOC.core.Events.HistoryEmitter.msg]: Returns formatted MSG event string.
- death(entity_id: str) -> str [ARCH.DOC.core.Events.HistoryEmitter.death]: Returns formatted DEATH event string.
- status(entity_id: str, name: str, duration: int, state: str) -> str [ARCH.DOC.core.Events.HistoryEmitter.status]: Returns formatted STATUS event string.
- turn_start(actor_id: str, hp: int, max_hp: int, mp: int, max_mp: int, focus: int, mana: int) -> str [ARCH.DOC.core.Events.HistoryEmitter.turn_start]: Returns formatted TURN_START event string.

#### BaseClasses.py [ARCH.DOC.core.BaseClasses]
Provides foundational abstract classes and interfaces ensuring modularity and decoupling.

##### GameAction [ARCH.DOC.core.BaseClasses.GameAction]
[DEPENDS: ARCH.RULES.CORE.COMMAND, ARCH.RULES.CORE.IOC, ARCH.DOC.entities.Characters.Character]
Abstract base for the Command Pattern representing general commands. Core dependencies: Character. 

- Constructor [ARCH.DOC.core.BaseClasses.GameAction.__init__]: `__init__(self, name: str, actor: 'Character')`
- `name: str` [ARCH.DOC.core.BaseClasses.GameAction.name]: Name of the action.
- `actor: 'Character'` [ARCH.DOC.core.BaseClasses.GameAction.actor]: Character who is executing the action.
- can_execute() -> tuple[bool, str] [ARCH.DOC.core.BaseClasses.GameAction.can_execute]: Validates if the action can be used. Raises NotImplementedError by default. Subclasses must implement logic to return a boolean success and a message.
- execute() -> ActionLoad [ARCH.DOC.core.BaseClasses.GameAction.execute]: Executes the action's logic. Raises NotImplementedError by default. Returns an ActionLoad representing the result.
- execute_if_possible() -> ActionLoad [ARCH.DOC.core.BaseClasses.GameAction.execute_if_possible]: Wrapper that calls `can_execute()`. If false, returns a failed `ActionLoad` with the error message in the history. Otherwise, calls and returns `execute()`.

##### IBattleContext [ARCH.DOC.core.BaseClasses.IBattleContext]
[DEPENDS: ARCH.DOC.core.Events.ActionLoad, ARCH.DOC.core.Structs.AttackActionTemplate, ARCH.DOC.entities.Characters.Character, ARCH.DOC.core.BaseClasses.BattlePassive, ARCH.DOC.core.BaseClasses.StatusEffect, ARCH.DOC.controllers.CharacterController]
Protocol for the battle orchestrator. MUST implement `dice_service` property (DiceManager).

- emit(event_name: str, payload: 'ActionLoad') -> None [ARCH.DOC.core.BaseClasses.IBattleContext.emit]: Dispatches an event to all subscribers.
- get_template(template_id: str) -> 'AttackActionTemplate' [ARCH.DOC.core.BaseClasses.IBattleContext.get_template]: Retrieves an action template.
- delay_character(character: 'Character', extra_ticks: int) -> None [ARCH.DOC.core.BaseClasses.IBattleContext.delay_character]: Modifies character timeline position.
- set_tick(character: 'Character', tick: int) -> None [ARCH.DOC.core.BaseClasses.IBattleContext.set_tick]: Sets character absolute timeline tick.
- get_characters() -> List[Character] [ARCH.DOC.core.BaseClasses.IBattleContext.get_characters]: Returns active character list.
- get_graveyard() -> List[Character] [ARCH.DOC.core.BaseClasses.get_graveyard]: Returns dead character list.
- get_controller(char_id: str) -> 'CharacterController' [ARCH.DOC.core.BaseClasses.IBattleContext.get_controller]: Retrieves controller for a character.
- get_active_passive(char_id: str, name: str) -> 'BattlePassive' | None [ARCH.DOC.core.BaseClasses.IBattleContext.get_active_passive]: Returns an active passive instance.
- add_status_effect(effect: 'StatusEffect') -> None [ARCH.DOC.core.BaseClasses.add_status_effect]: Registers a status effect to the engine.
- remove_status_effect(effect: 'StatusEffect') -> None [ARCH.DOC.core.BaseClasses.IBattleContext.remove_status_effect]: Removes a status effect from the engine.

##### IBattleJudge [ARCH.DOC.core.BaseClasses.IBattleJudge]
[DEPENDS: ARCH.DOC.core.BaseClasses.IBattleContext, ARCH.DOC.core.Structs.BattleResult, ARCH.DOC.core.Enums.BattleState]
Protocol for evaluating victory/defeat logic.

- rule(context: 'IBattleContext', result: 'BattleResult') -> 'BattleState' [ARCH.DOC.core.BaseClasses.IBattleJudge.rule]: Analyzes the current battle context and determines the battle state.

##### BattleAction [ARCH.DOC.core.BaseClasses.BattleAction]
Specialized GameAction for combat. Core dependencies: IBattleContext, Character, BattleActionType. Internal state: `targets` (List[Character]), `context` (IBattleContext), `action_type` (BattleActionType).
- target() -> 'Character' | None [ARCH.DOC.core.BaseClasses.BattleAction.target]: Property method returning the first target in `targets` list or None.
- can_execute() -> tuple[bool, str] [ARCH.DOC.core.BaseClasses.BattleAction.can_execute]: Validates action execution. Default implementation returns (True, ""). Subclasses should override.
- execute() -> ActionLoad [ARCH.DOC.core.BaseClasses.BattleAction.execute]: Executes action. Default implementation returns a failed ActionLoad. Subclasses must override to implement logic.

##### BattlePassive [ARCH.DOC.core.BaseClasses.BattlePassive]
Base for reactive logic or characteristics that alter engine rules via Event Bus. Core dependencies: Character, IBattleContext, DiceManager. Internal state: `name` (str), `owner` (Character), `dice_service` (DiceManager), `context` (IBattleContext).
- get_hooks() -> Dict[str, Callable] [ARCH.DOC.core.BaseClasses.BattlePassive.get_hooks]: Returns a dictionary mapping event names to handler functions. Raises NotImplementedError by default.
- apply() -> None [ARCH.DOC.core.BaseClasses.BattlePassive.apply]: Called when passive enters play. Default does nothing.
- remove() -> None [ARCH.DOC.core.BaseClasses.BattlePassive.remove]: Called when passive leaves play. Default does nothing.

##### StatusEffect [ARCH.DOC.core.BaseClasses.StatusEffect]
Represents a temporary status effect applied to a character. Inherits from BattlePassive. Core dependencies: Character, IBattleContext. Internal state: `duration` (int), `character` (Character), `modifiers` (list[EphemeralModifier]).
- apply() -> None [ARCH.DOC.core.BaseClasses.StatusEffect.apply]: Applies the effect. Raises NotImplementedError. Subclasses must override.
- remove() -> None [ARCH.DOC.core.BaseClasses.StatusEffect.remove]: Cleans up all modifiers applied by this effect using `_remove_modifier`, then calls `context.remove_status_effect(self)`.
- _add_modifier(modifier: 'EphemeralModifier') -> None [ARCH.DOC.core.BaseClasses.StatusEffect._add_modifier]: Internal method. Appends modifier to `self.modifiers` and calls `self.owner.add_modifier(modifier)`.
- _remove_modifier(modifier: 'EphemeralModifier') -> None [ARCH.DOC.core.BaseClasses.StatusEffect._remove_modifier]: Internal method. Removes modifier from `self.modifiers` and calls `self.owner.remove_modifier(modifier)`.

#### CharacterSystem.py [ARCH.DOC.core.CharacterSystem]
Provides stateless domain logic for manipulating Character entities. Isolates rule-heavy operations from data containers. `[ARCH.RULES.CORE.ENTITIES]`, `[ARCH.RULES.CORE.CQRS]`

- generate_focus(character: 'Character') -> int [ARCH.DOC.core.CharacterSystem.generate_focus]: Generates character focus. Modifies `character.floating_focus` by adding `character.men`, capped at `rules.limite_foco * character.men`. Returns the new floating focus value.
- generate_mana(character: 'Character') -> int [ARCH.DOC.core.CharacterSystem.generate_mana]: Pulls mana into floating state. Pulls a maximum of `character.men` from `character.current_mp`, limited by available space (`rules.limite_mana * character.men - floating_mp`). Deducts from `current_mp` and adds to `floating_mp`. Returns the new `floating_mp`.
- take_damage(character: 'Character', damage: int) -> None [ARCH.DOC.core.CharacterSystem.take_damage]: Reduces HP. Modifies `character.current_hp` by subtracting `damage`, with a minimum floor of 0.
- spend_focus(character: 'Character', amount: int) -> bool [ARCH.DOC.core.CharacterSystem.spend_focus]: Attempts to consume focus. If `character.floating_focus >= amount`, deducts amount and returns True. Otherwise returns False without mutating.
- spend_mana(character: 'Character', amount: int) -> bool [ARCH.DOC.core.CharacterSystem.spend_mana]: Attempts to consume mana. If `character.floating_mp >= amount`, deducts amount and returns True. Otherwise returns False without mutating.
- is_alive(character: 'Character') -> bool [ARCH.DOC.core.CharacterSystem.is_alive]: Checks if character HP > 0. Returns boolean.
- equip_weapon(character: 'Character', new_weapon: 'Weapon') -> Tuple[bool, str, 'Weapon' | None] [ARCH.DOC.core.CharacterSystem.equip_weapon]: Equips a weapon. Validates if `new_weapon.type` matches `character.combat_style.weapon_type`. If it does, updates `character.weapon`, recalculates `base_pda` (`weapon.db + character attribute`) and `base_mda`. Returns success boolean, a message, and the previously equipped weapon.
- equip_armor(character: 'Character', new_armor: 'Armor') -> Tuple[bool, str, 'Armor' | None] [ARCH.DOC.core.CharacterSystem.equip_armor]: Equips armor. Validates if `new_armor.type` matches `character.combat_style.armor_type`. If so, removes old armor's HP bonus, updates `character.armor`, and adds new armor's `hp_bonus` to `max_hp` and `current_hp`. Returns success boolean, a message, and the previously equipped armor.

#### DiceManager.py [ARCH.DOC.core.DiceManager]
Manages random number generation and deterministic roll scheduling for combat resolution.

##### DiceManager [ARCH.DOC.core.DiceManager.DiceManager]
Handles all dice rolling logic. Core dependencies: Python's `random` module. Internal state: `random` (Random instance), `queue` (deque).
- schedule_result(val: int) -> None [ARCH.DOC.core.DiceManager.DiceManager.schedule_result]: Injects a predefined integer into the internal queue, forcing the next roll to use this value deterministically.
- roll_dice(sides: int, state: RollState = RollState.NEUTRAL) -> RollResult [ARCH.DOC.core.DiceManager.DiceManager.roll_dice]: Performs a dice roll. If the queue is not empty, pops a scheduled value and returns it as a RollResult. Otherwise, rolls according to the specified `state` (rolling twice for advantage/disadvantage, selecting max/min respectively). Returns a RollResult.

#### DataManager.py [ARCH.DOC.core.DataManager]
Acts as a central registry for loading and accessing data-driven templates from JSON files. `[ARCH.RULES.CORE.DATA]`

##### DataManager [ARCH.DOC.core.DataManager.DataManager]
Central data registry. Core dependencies: CharacterSystem. Internal state: `_action_templates` (dict), `_combat_styles` (dict), `_characters` (dict), `_game_rules` (GameRules | None).
- load_combat_styles(filepath: str) -> None [ARCH.DOC.core.DataManager.DataManager.load_combat_styles]: Loads JSON data into `_combat_styles` dict, creating `CombatStyle` instances and converting strings to Enum equivalents.
- load_game_rules(filepath: str) -> None [ARCH.DOC.core.DataManager.DataManager.load_game_rules]: Loads JSON data into `_game_rules`, creating a `GameRules` instance.
- load_characters(filepath: str) -> None [ARCH.DOC.core.DataManager.DataManager.load_characters]: Loads JSON data into `_characters` dict, instantiating `Character`, `Weapon`, and `Armor` objects, and utilizing `CharacterSystem` to equip items. Raises KeyError if `_game_rules` or `_combat_styles` are not loaded first or if a combat style is missing.
- load_action_templates(filepath: str) -> None [ARCH.DOC.core.DataManager.DataManager.load_action_templates]: Loads JSON data into `_action_templates` dict, creating `AttackActionTemplate` and `AttackEffects` instances. Raises ValueError if Enum conversions fail.
- get_action_template(action_id: str) -> 'AttackActionTemplate' [ARCH.DOC.core.DataManager.DataManager.get_action_template]: Retrieves an action template. Raises KeyError if the ID does not exist.
- get_character(char_id: str) -> 'Character' [ARCH.DOC.core.DataManager.DataManager.get_character]: Retrieves a character instance. Raises KeyError if the ID does not exist.
- get_combat_style(style_id: str) -> 'CombatStyle' [ARCH.DOC.core.DataManager.DataManager.get_combat_style]: Retrieves a combat style. Raises KeyError if the ID does not exist.

#### Modifiers.py [ARCH.DOC.core.Modifiers]
Implements the Modifier Stack Pattern for dynamic stat calculation. `[ARCH.RULES.CORE.MODIFIER]`

##### StatModifier [ARCH.DOC.core.Modifiers.StatModifier]
Base class for statistical modifiers. Core dependencies: `uuid` module. Internal state: `id` (str), `stat_name` (str), `value` (int), `source` (str).
- apply(character: 'Character') -> None [ARCH.DOC.core.Modifiers.StatModifier.apply]: Placeholder method. Does nothing directly since attribute computation pulls from the modifier stack.
- remove(character: 'Character') -> None [ARCH.DOC.core.Modifiers.StatModifier.remove]: Placeholder method. Does nothing.

##### EphemeralModifier [ARCH.DOC.core.Modifiers.EphemeralModifier]
Subclass of StatModifier. Represents a modifier applied during combat that should be cleared at the end of the combat or effect duration.

##### PersistentModifier [ARCH.DOC.core.Modifiers.PersistentModifier]
Subclass of StatModifier. Represents a modifier applied outside of combat, such as equipment bonuses or permanent curses.

### MODULE: Battle [ARCH.DOC.battle]
Centralizes all logic related to combat resolution, timeline management, and reactive behaviors.
[ARCH.RULES.BATTLE.TIMELINE], [ARCH.RULES.CORE.IOC], [ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]

#### BattleManager.py [ARCH.DOC.battle.BattleManager]
The orchestrator of the battle engine. Manages the passage of time (Ticks), character participation, and the event-driven communication (Event Bus) between combatants. [ARCH.RULES.BATTLE.TIMELINE], [ARCH.RULES.CORE.IOC]

##### BattleManager [ARCH.DOC.battle.BattleManager.BattleManager]
The central controller for combat.
Core dependencies: DiceManager, DataManager, BattleJudge.
Internal state:
- timeline (list): A Min-Heap of (tick, neg_hab, neg_roll, char_id, character) for turn scheduling.
- current_tick (int): The current point in time of the battle.
- characters (dict[str, Character]): Active characters indexed by ID.
- listeners (dict[str, list[Callable]]): Registry for the Event Bus, mapping event names to hook functions.

- add_character(character: 'Character', controller: 'CharacterController', start_tick: int = 0) -> None [ARCH.DOC.battle.BattleManager.BattleManager.add_character]:
  Adds a character to the battle.
  1. Registers the character and its controller.
  2. Generates a unique tie-break roll using _get_unique_roll.
  3. Pushes the character into the timeline heap.
  4. Instantiates and subscribes all character passive abilities from the registry.

- run_battle() -> None [ARCH.DOC.battle.BattleManager.BattleManager.run_battle]:
  The main execution loop.
  1. Calls judge.rule to check for terminal states.
  2. Retrieves the next actor via get_next_actor.
  3. Emits on_turn_start.
  4. Executes the controller's choose_action in a loop (handling Free Actions).
  5. Subscribes/unsubscribes ephemeral hooks from the chosen action.
  6. Emits on_turn_end and schedules the next turn.

- run_action(action: 'BattleAction') -> ActionLoad [ARCH.DOC.battle.BattleManager.BattleManager.run_action]:
  Simulates a single turn for an action. Useful for unit testing.
  1. Emits on_turn_start.
  2. Subscribes action-specific hooks.
  3. Executes the action and captures the ActionLoad.
  4. Resolves deaths and emits on_turn_end.
  5. Unsubscribes hooks in a finally block to prevent leaks. [ARCH.RULES.BATTLE.EPHEMERAL_HOOKS]

- set_tick(character: 'Character', tick: int) -> None [ARCH.DOC.battle.BattleManager.BattleManager.set_tick]:
  Directly modifies a character's position in the timeline.
  1. Finds the character's entry in the timeline.
  2. Frees the old unique slot in timeline_slots.
  3. Calculates a new unique roll for the target tick.
  4. Updates the entry and calls heapq.heapify. [ARCH.RULES.BATTLE.TIMELINE]

- delay_character(character: 'Character', extra_ticks: int) -> None [ARCH.DOC.battle.BattleManager.BattleManager.delay_character]:
  Relative version of set_tick. Adds extra_ticks to the current scheduled tick of the character. [ARCH.RULES.BATTLE.TIMELINE]

- schedule_next_action(character: 'Character', action_cost: int) -> None [ARCH.DOC.battle.BattleManager.BattleManager.schedule_next_action]:
  Calculates the next tick (current_tick + action_cost) and re-inserts the character into the timeline.

- get_next_actor() -> 'Character' | None [ARCH.DOC.battle.BattleManager.BattleManager.get_next_actor]:
  Pops the top of the timeline heap. If the character is alive and active, updates current_tick and returns it.

- get_graveyard() -> List['Character'] [ARCH.DOC.battle.BattleManager.BattleManager.get_graveyard]:
  Returns the list of characters that have been moved to the graveyard.

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
- resolve_tag() [ARCH.DOC.utilities.ref_manager.resolve_tag]: The primary recursive solver. It fetches a tag's content and iteratively resolves all nested "DEPENDS:" tags. It maintains a `resolved_tags` registry to prevent circular dependencies. When a tag is found in a header (session), all other tags within that session are automatically marked as resolved to ensure clean extraction.
- extract_section() [ARCH.DOC.utilities.ref_manager.extract_section]: The parsing engine. It searches for a tag (prioritizing headers) and extracts the corresponding block of text. If the tag is found in a header, it captures all content until a header of equal or higher level is encountered.
- update_section() [ARCH.DOC.utilities.ref_manager.update_section]: The modification engine. Locates a tag and replaces its entire section (if a header) or line with new content. Supports reading content from a string or an external file via `--from-file`.
- create_section() [ARCH.DOC.utilities.ref_manager.create_section]: The creation engine. Implements **Smart Placement** and **Fail-Fast Validation**: it prevents duplicate tags and ensures hierarchical integrity. New tags are placed after their parent or last sibling based on prefix matching. It fails if a parent tag is missing (returning "Error: Parent tag [prefix] not found." for 3+ component tags) or if the file identifier is missing (for 2 component tags), ensuring documentation structure is maintained.
- get_path_for_tag() [ARCH.DOC.utilities.ref_manager.get_path_for_tag]: A utility that normalizes tags and determines the correct source file path by matching the tag's prefix against the `PATH_MAPPING`.

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
- **Battle Context [ARCH.TEST_QUALITY.IBATTLECONTEXT]:** Get a `BattleManager` with `create_test_battle_manager()`from `tests/utils/test_utils.py` when a concrete implementation of `IBattleContext` is required for behavioral tests, avoid mocking of the battle state. 
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

```
### MODULE: Module_name [ARCH.module_name]
Comprehensive description of the module, its primary responsibilities, and a list of relevant architectural rules. `[ARCH.RULE.(...)]`, ...

#### File Name [ARCH.module_name.FileName]
Description of the file's domain purpose, what core concepts it handles, and relevant architectural rules. `[ARCH.RULE.(...)]`, ...

- variable_name [ARCH.module_name.FileName.variable_name]: Global variable description. MUST include: exact type, default value, and how it affects multiple components or alters system behavior.
- function_name(param1: type, ...) -> return_type [ARCH.module_name.FileName.function_name]: Standalone function description. MUST include: exact parameter names and types, return type, exceptions raised, and a step-by-step summary of internal logic/algorithms so the code does not need to be read.

##### InterfaceName [ARCH.module_name.FileName.INTERFACE:InterfaceName]
Interface/Protocol description. MUST detail required properties and exact method signatures, including expected behaviors and rules for implementation.

##### ClassName [ARCH.module_name.FileName.Classname] 
Class description. MUST include its purpose, core dependencies and a brief explanation of its lifecycle or instantiation requirements.
- variable_name [ARCH.module_name.FileName.VARIABLE:Class.variable_name]: Variable description. MUST include: exact type, whether it is public/private, and how it influences external behavior, state transitions, or invariants.
- method_name(param1: type, ...) -> return_type [ARCH.module_name.FileName.Class.method]: Method description. MUST include: exact parameter names and types, return type, side-effects (e.g., state changes, emitted events), exceptions raised, and a detailed explanation of its internal logic so the code does not need to be read.

##### CLI Usage [ARCH.module_name.FileName.CLI]
Description of command-line usage.
```

#### Rules [ARCH.DOC_STANDARDS.MODULE.RULES]
- Template shows all possible elements, include only those needed to the documentation.
- Include a section only if there is at least one relevant item.
- Sections MUST follow the order defined in the template.
- Never invent variables/functions just to satisfy the template.
- Preserve existing tags when updating.
- Prefer extending over rewriting.

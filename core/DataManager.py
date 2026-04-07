import json
from core.Enums import BattleActionType, ArmorType, AttributeType, WeaponType
from core.Structs import CombatStyle, GameRules
from combat.BattleActions import BattleActionTemplate
from entities.Itens import Armor, Weapon
from entities.Characters import Character
from combat.BattleActions import registry as actions_registry
from combat.PassiveAbilities import registry as passives_registry
from controllers.CharacterController import registry as controllers_registry

class DataManager:
    def __init__(self):
            # O dicionário privado que guarda os moldes na memória
            self._action_templates: dict[str, 'BattleActionTemplate'] = {}
            self._combat_styles: dict[str, CombatStyle] = {}
            self._characters: dict[str, Character] = {}
            self._game_rules: 'GameRules | None' = None


    def load_combat_styles(self, filepath: str):
        """
        Carrega os estilos de combate a partir de um arquivo JSON e converte as strings para os Enums correspondentes.
        """
        #Abre o JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        #Monta o dicionário de CombatStyles, convertendo as strings para os Enums
        styles = {}
        for key, val in data.items():
            styles[key] = CombatStyle(
                name=val["name"],
                atq_die=val["atq_die"],
                def_die=val["def_die"],
                # Converte strings para Enums para manter consistência
                main_stat=AttributeType(val["main_stat"]),
                armor_type=ArmorType(val["armor_type"]),
                weapon_type=WeaponType(val["weapon_type"])
            )
        
        # Retorna o dicionário de estilos de combate
        self._combat_styles = styles

    def load_game_rules(self, filepath: str):
        """
        Carrega as regras do jogo (atualmente apenas as tabelas de progressão) a partir de um arquivo JSON e retorna um objeto GameRules.
        """
        # Abre o JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Carrega as tabelas de progressão e retorna um objeto GameRules
        regras = data["regras_progressao"]
        self._game_rules = GameRules(
            hp_table=regras["tabela_hp"],
            mp_table=regras["tabela_mp"],
            action_cost_table=regras["tabela_custos"],
            limite_foco=data["limite_foco"],
            limite_mana=data["limite_mana"]
        )

    def load_characters(self,filepath: str):
        """
        Carrega os personagens a partir de um arquivo JSON, criando instâncias de Character. Retorna um dicionário de personagens acessível por char_id.
        """

        if(self._game_rules is None):
            raise KeyError("Tentando carregar personagens antes de carregar o GameRules")
        
        if not self._combat_styles:
            raise KeyError("Tentando carregar personagens antes de carregar os CombatStyles")
        
        # Abre o JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Inicializa o dicionário de personagens
        characters = {}

        # Para cada tupla (char_id, char_data) no JSON...
        for key, char_data in data.items():
            
            combat_style_key = char_data["CombatStyle"]
            if combat_style_key not in self._combat_styles:
                raise KeyError(f"CombatStyle '{combat_style_key}' não encontrado para personagem '{key}'")
            
            try:
                controller = controllers_registry[char_data["controller"]]()
            except KeyError as exc:
                raise KeyError(f"[ERRO FATAL] Controller {char_data["controller"]} de {key} não foi encontrado") from exc
            
            # Cria o personagem a partir de char_data
            char = Character(
                char_id=key,
                name=char_data["Nome"],
                attributes=[char_data["FIS"], char_data["HAB"], char_data["MEN"]],
                combat_style=self._combat_styles[combat_style_key],
                rules=self._game_rules,
                controller = controller
            )

            # Cria a arma e armadura a partir de char_data e equipa o personagem
            weapon = Weapon(
                name=char_data["Weapon"]["name"],
                db=char_data["Weapon"]["db"],
                mda=char_data["Weapon"]["mda"],
                type=WeaponType(char_data["Weapon"]["type"])
            )
            char.equip_weapon(weapon)
            
            armor = Armor(
                name=char_data["Armor"]["name"],
                hp_bonus=char_data["Armor"]["hp_bonus"],
                type=ArmorType(char_data["Armor"]["type"])
            )
            char.equip_armor(armor)

            # Itera sobre as habilidades listadas no JSON e cria as instâncias usando o ability_registry
            char.active_abilities = char_data["Abilities"]
            char.passive_abilities = char_data["Passives"]
            
            # Adiciona o personagem ao dicionário
            characters[key] = char
        
        self._characters = characters

    def load_action_templates(self, filepath: str):
        """
        Carrega os templates de ações de combate a partir de um arquivo JSON.
        Usa o actions_registry para preencher o campo command com a classe de ação correta.
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        templates = {}
        for key, template_data in data.items():
            action_id = key
            if action_id not in actions_registry:
                raise KeyError(f"Template '{key}' referencia action_id '{action_id}' não registrado no actions_registry.")

            action_type_value = template_data["action_type"].lower()
            try:
                action_type = BattleActionType(action_type_value)
            except ValueError as exc:
                raise ValueError(f"Action type inválido para template '{key}': '{template_data['action_type']}'") from exc

            templates[action_id] = BattleActionTemplate(
                id=action_id,
                nome=template_data["nome"],
                action_type=action_type,
                focus_cost=template_data["focus_cost"],
                command=actions_registry[action_id]
            )

        self._action_templates = templates
    
    def get_action_template(self, action_id: str) -> 'BattleActionTemplate':
        """Retorna o molde de uma ação. Estoura um KeyError se o ID não existir."""
        try:
            return self._action_templates[action_id]
        except KeyError as exc:
            raise KeyError(f"[ERRO FATAL] DataManager: ActionTemplate '{action_id}' não foi encontrado! Verifique se há erros de digitação no JSON.") from exc

    def get_character(self, char_id: str) -> 'Character':
        """Retorna a instância de um personagem. Estoura um KeyError se o ID não existir."""
        try:
            return self._characters[char_id]
        except KeyError as exc:
            raise KeyError(f"[ERRO FATAL] DataManager: Character '{char_id}' não foi encontrado no banco de dados!") from exc

    def get_combat_style(self, style_id: str) -> 'CombatStyle':
        """Retorna um estilo de combate. Estoura um KeyError se o ID não existir."""
        try:
            return self._combat_styles[style_id]
        except KeyError as exc:
            raise KeyError(f"[ERRO FATAL] DataManager: CombatStyle '{style_id}' não foi encontrado!") from exc

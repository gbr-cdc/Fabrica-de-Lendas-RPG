from typing import Dict, Any
import copy
from core.Models import Character
from core.BattleManager import BattleManager
from core.DiceManager import DiceManager
from core.DataManager import load_combat_styles, load_game_rules, load_characters

CHARACTERS_FILE = "data/Characters.json"
COMBAT_STYLES_FILE = "data/CombatStyles.json"
RULES_FILE = "data/Rules.json"

class PvPSimulator:
    def __init__(self, battle_manager: BattleManager, character1: Character, character2: Character):
        self.battle_manager = battle_manager
        self.character1 = character1
        self.character2 = character2

    @classmethod
    def from_data_files(
        cls,
        characters_filepath: str,
        combat_styles_filepath: str,
        rules_filepath: str,
        char1_id: str,
        char2_id: str,
        dice_seed: int | None = None
    ) -> "PvPSimulator":
        """
        Factory method para criar um PvPSimulator a partir dos arquivos de dados.
        """
        combat_styles = load_combat_styles(combat_styles_filepath)
        rules = load_game_rules(rules_filepath)
        characters = load_characters(characters_filepath, combat_styles, rules)

        return cls(
            battle_manager=BattleManager(DiceManager(seed=dice_seed)),
            character1=characters[char1_id],
            character2=characters[char2_id]
        )

    def single_battle_verbose(self):
        """ 
        Simula uma batalha entre os dois personagens, retornando detalhes de cada turno.
        """
        turn_count = 0
        max_turns = 1000 # Para evitar loops infinitos
        history = []

        #Insere os personagens na fila de ação, considerando o custo de ação base para determinar quem começa.
        if(self.character1.action_cost_base != self.character2.action_cost_base):
            self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base)
            self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base)
        else:
            #Se for empate, rola um dado para desempatar.
            while True:
                roll1 = self.battle_manager.dice_service.roll_dice(10)
                roll2 = self.battle_manager.dice_service.roll_dice(10)
                if roll1 != roll2:
                    break
            if roll1 > roll2:
                self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base)
                self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base)
            elif roll2 > roll1:
                self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base)
                self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base)

        #Loop principal        
        while turn_count < max_turns and self.character1.is_alive() and self.character2.is_alive():
            # Pega o próximo personagem da fila de ação
            actor = self.battle_manager.get_next_actor()
            # Para se a fila estiver vazia (o que não deveria acontecer, mas é uma medida de segurança)
            if actor is None:
                break

            # Sinaliza que o turno começou
            self.battle_manager.emit('on_turn_start', {'character': actor})
            
            history.append(f"\n[Turno {turn_count + 1}] {actor.name} (HP: {actor.current_hp}/{actor.max_hp}, Foco: {actor.floating_focus}) está agindo!")
            
            # Determina o alvo
            target = self.character2 if actor.char_id == self.character1.char_id else self.character1
            
            # Regra para usar skill(Espera que a skill seja a segunda habilidade na lista))
            can_use, msg = actor.abilities[1].can_execute(actor, target)
            if can_use:
                ability = actor.abilities[1]
                result = actor.abilities[1].execute(actor, target, self.battle_manager)
                skill_used = True
                for line in result.get("history", []):
                    history.append(f"  {line}")
            
            # Se não, usa o ataque básico (Espera que o ataque básico seja a primeira habilidade na lista)
            else:
                ability = actor.abilities[0]
                skill_used = False
                can_use, msg = ability.can_execute(actor, target)
                if can_use:
                    result = ability.execute(actor, target, self.battle_manager)
                    for line in result.get("history", []):
                        history.append(f"  {line}")
                else:
                    history.append(f"  {msg}")
            
            # Volta o personagem para a fila. Se a habilidade não tiver um custo de ação específico, usa o custo base do personagem.
            self.battle_manager.schedule_next_action(actor, ability.action_cost or actor.action_cost_base)
            turn_count += 1

            #Só gera foco se o personagem usou o ataque básico, não a skill.
            if skill_used is False:
                actor.generate_focus()
            
            #Sinaliza que o turno acabou
            self.battle_manager.emit('on_turn_end', {'character': actor})
        
        history.append(f"\n{'='*50}")
        history.append(f"Batalha terminada! {self.character1.name}: {self.character1.current_hp}HP | {self.character2.name}: {self.character2.current_hp}HP")

        return {
            "winner": self.character1.name if self.character1.is_alive() else self.character2.name,
            "turns": turn_count,
            "final_hp": {
                self.character1.name: self.character1.current_hp,
                self.character2.name: self.character2.current_hp
            },
            "history": history
        }

    def single_battle_summary(self):
        """ 
        Simula uma batalha entre os dois personagens, mas retorna apenas o resultado final
        """
        turn_count = 0
        max_turns = 1000 # Para evitar loops infinitos
        # Insere os personagens na fila de ação, considerando o custo de ação base para determinar quem começa.
        if(self.character1.action_cost_base != self.character2.action_cost_base):
            self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base)
            self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base)
        else:
            # Se for empate, rola um dado para desempatar.
            while True:
                roll1 = self.battle_manager.dice_service.roll_dice(10)
                roll2 = self.battle_manager.dice_service.roll_dice(10)
                if roll1 != roll2:
                    break
            if roll1 > roll2:
                self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base)
                self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base)
            elif roll2 > roll1:
                self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base)
                self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base)

        # Loop principal
        while turn_count < max_turns and self.character1.is_alive() and self.character2.is_alive():
            # Pega o próximo personagem da fila de ação
            actor = self.battle_manager.get_next_actor()
            # Para se a fila estiver vazia (o que não deveria acontecer, mas é uma medida de segurança)
            if actor is None:
                break
            
            # Sinaliza que o turno começou
            self.battle_manager.emit('on_turn_start', {'character': actor})
            
            # Determina o alvo
            target = self.character2 if actor.char_id == self.character1.char_id else self.character1
            
            # Regra para usar skill(Espera que a skill seja a segunda habilidade na lista))
            can_use, msg = actor.abilities[1].can_execute(actor, target)
            if can_use:
                ability = actor.abilities[1]
                skill_used = True
                ability.execute(actor, target, self.battle_manager)
            
            # Se não, usa o ataque básico (Espera que o ataque básico seja a primeira habilidade na lista)
            else:
                ability = actor.abilities[0]
                skill_used = False
                can_use, msg = ability.can_execute(actor, target)
                if can_use:
                    ability.execute(actor, target, self.battle_manager)
            
            # Volta o personagem para a fila. Se a habilidade não tiver um custo de ação específico, usa o custo base do personagem.
            self.battle_manager.schedule_next_action(actor, ability.action_cost or actor.action_cost_base)
            turn_count += 1

            #Só gera foco se o personagem usou o ataque básico, não a skill.
            if skill_used is False:
                actor.generate_focus()
            
            #Sinaliza que o turno acabou
            self.battle_manager.emit('on_turn_end', {'character': actor})
        
        return {
            "winner": self.character1.name if self.character1.is_alive() else self.character2.name,
            "turns": turn_count,
            "final_hp": {
                self.character1.name: self.character1.current_hp,
                self.character2.name: self.character2.current_hp
            }
        }

def simulate_multiple_battles(
    num_simulations: int,
    char1_id: str,
    char2_id: str,
    characters_filepath: str = CHARACTERS_FILE,
    combat_styles_filepath: str = COMBAT_STYLES_FILE,
    rules_filepath: str = RULES_FILE,
) -> Dict[str, Any]:
    """
    Simula múltiplas batalhas entre dois personagens e retorna estatísticas agregadas.
    """
    # Carrega os dados uma vez fora do loop
    combat_styles = load_combat_styles(combat_styles_filepath)
    rules = load_game_rules(rules_filepath)
    all_characters = load_characters(characters_filepath, combat_styles, rules)
    
    # Templates para os personagens específicos
    char1_template = all_characters[char1_id]
    char2_template = all_characters[char2_id]

    # Inicializa o dicionário de resultados
    results = {
        char1_id: 0,
        char2_id: 0,
        "draws": 0,
        "total_turns": 0,
        "average_turns": 0.0
    }

    # Lista para armazenar o número de turnos de cada batalha
    turns_list = []

    # Loop de simulações
    for _ in range(num_simulations):
        # Cria cópias profundas dos templates para instâncias frescas
        heroi1 = copy.deepcopy(char1_template)
        heroi2 = copy.deepcopy(char2_template)

        # Cria um novo simulador para cada batalha, garantindo que o estado seja limpo
        simulator = PvPSimulator(
            BattleManager(DiceManager()),
            heroi1,
            heroi2
        )

        # Simula a batalha e coleta o resumo
        summary = simulator.single_battle_summary()
        winner = summary["winner"]
        turns = summary["turns"]
        
        # Acumula o número de turnos para calcular a média depois
        turns_list.append(turns)

        # Atualiza os resultados de vitórias/derrotas/empates
        if winner == heroi1.name:
            results[char1_id] += 1
        elif winner == heroi2.name:
            results[char2_id] += 1
        else:
            results["draws"] += 1

    # Calcula o total e a média de turnos
    results["total_turns"] = sum(turns_list)
    results["average_turns"] = sum(turns_list) / len(turns_list) if turns_list else 0.0

    return results

# Funções de interface para rodar as simulações a partir do Main.py
def multy(char1_id: str, char2_id: str):
    results = simulate_multiple_battles(10000, char1_id, char2_id)

    print("Resultados das 10000 batalhas:")
    print(f"{char1_id}: {results[char1_id]} vitórias")
    print(f"{char2_id}: {results[char2_id]} vitórias")
    print(f"Empates: {results['draws']}")
    print(f"Total de turnos: {results['total_turns']}")
    print(f"Média de turnos por batalha: {results['average_turns']:.2f}")


def mono(char1_id: str, char2_id: str):
    simulator = PvPSimulator.from_data_files(
        CHARACTERS_FILE,
        COMBAT_STYLES_FILE,
        RULES_FILE,
        char1_id,
        char2_id
    )
    result = simulator.single_battle_verbose()
    for line in result["history"]:
        print(line)

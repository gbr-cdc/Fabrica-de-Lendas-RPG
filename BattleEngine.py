import heapq
import random
import sys
from typing import List, Callable, Dict, Any
from dataclasses import dataclass

@dataclass
class CombatStyle:
    name: str
    atq_die: int
    def_die: int
    main: str
    second: str
    third: str

combat_styles = {
    "Destruidor": CombatStyle(name="Destruidor", atq_die=12, def_die=8, main="FIS", second="HAB", third="MEN"),
    "Duelista": CombatStyle(name="Duelista", atq_die=10, def_die=10, main="HAB", second="FIS", third="MEN"),
}

class Ability:
    """
    Command Pattern: Cada habilidade (inclusive o ataque básico) é um objeto encapsulado.
    """
    def __init__(self, name: str, focus_cost: int, action_cost: int):
        self.name = name
        self.focus_cost = focus_cost
        self.action_cost = action_cost # Quanto avança no relógio

    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        """
        Método sobrescrito por habilidades passivas para se inscreverem no Event Bus.
        Por padrão, não faz nada.
        """
        pass

    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        """
        Valida se a habilidade pode ser usada ANTES de gastar o turno.
        Retorna (Pode Usar?, "Mensagem de Erro")
        """        
        return True, ""

    def execute(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager') -> Dict[str, Any]:
        """
        Executa a lógica da habilidade e retorna um dicionário de resultados para a View ler.
        Deve ser sobrescrito por subclasses (ex: BasicAttack, Fireball).
        """
        raise NotImplementedError("A habilidade deve implementar o método execute.")
    
class StatusEffect:
    # O alvo agora é obrigatório para nascer!
    def __init__(self, name: str, duration: int, target: 'Character'):
        self.name = name
        self.duration = duration
        self.character = target
        self.battle_manager = None
        
    # --- MÉTODOS DO MOTOR ---
    def apply(self, battle_manager: 'BattleManager'):
        # Apply agora só precisa receber o Motor!
        self.battle_manager = battle_manager
        self.character.status_effects.append(self)
        
        if self.battle_manager is not None:
            self.battle_manager.subscribe('on_turn_end', self._tick_duration)
        
        # Chama a sua lógica limpa!
        self.on_apply() 
        self.register_listeners(self.battle_manager)

    def remove(self):
        if self.battle_manager is not None:
            self.battle_manager.unsubscribe('on_turn_end', self._tick_duration)
            self.on_unsubscribe(self.battle_manager)
        self.on_remove()

    def _tick_duration(self, event_data: dict) -> dict:
        # Fim das checagens chatas do self.character!
        if event_data.get('character') and event_data['character'].char_id == self.character.char_id:
            self.duration -= 1
            event_data = self.on_tick(event_data)
            
            if self.duration <= 0:
                self.remove()
                if self in self.character.status_effects:
                    self.character.status_effects.remove(self)
        return event_data

    # --- MÉTODOS DE GAME DESIGN ---
    # Agora você pode voltar a usar self.character livremente aqui dentro!
    def on_apply(self):
        pass

    def on_remove(self):
        pass

    def on_unsubscribe(self, battle_manager: 'BattleManager'):
        pass

    def on_tick(self, event_data: dict) -> dict:
        return event_data
        
    def register_listeners(self, battle_manager: 'BattleManager'):
        pass

class Weapon:
    def __init__(self, name: str, pda: int, mda: int):
        self.name = name
        self.pda = pda
        self.mda = mda

class Armor:
    def __init__(self, name: str, hp_bonus: int):
        self.name = name
        self.hp_bonus = hp_bonus


class Character:
    """
    A representação dos dados e status do personagem.
    """
    def __init__(self, char_id: str, name: str, attributes: List[int], combat_style: CombatStyle, bda=0, bdd=0 ):
        self.char_id = char_id
        self.name = name
        
        self.fis, self.hab, self.men = attributes
        
        # Atributos Base
        self.max_hp = self._hp_val(self.fis)
        self.max_mp = self._mp_val(self.men)
        self.current_mp = self.max_mp # Adicionar esta linha!
        self.floating_mp = 0  # MP flutuante para habilidades que custam MP
        self.floating_focus = 0 # Foco flutuante para habilidades que custam Foco
        self.current_hp = self.max_hp
        
        # Equipamentos/Status Dinâmicos (Podem ser extraídos para classes próprias depois)
        self.pda = 0  # Poder de Ataque
        self.mda = 1   # Multiplicador de Ataque
        self.atk_die = combat_style.atq_die
        self.def_die = combat_style.def_die # d6, d8, d10, etc
        self.combat_style = combat_style
        self.bdc = self.calcular_bdc(combat_style) # Bônus de Combate, calculado a partir do estilo de combate e atributos
        self.bda = bda
        self.bdd = bdd
        
        self.action_cost_base = self._action_cost_val(self.hab)
        
        self.abilities: List[Ability] = []
        self.status_effects: List[StatusEffect] = []

        self.weapon = None
        self.armor = None

    def _action_cost_val(self, hab: int) -> int:
        # Simplificação da sua tabela para o esqueleto
        tabela_custos = {0: 60, 1: 50, 2: 40, 3: 36, 4: 32, 5: 28, 6: 25, 7: 22, 8: 20, 9: 18, 10: 16, 11: 8, 12: 8, 13: 8, 14: 8, 15: 8}
        if hab not in tabela_custos:
            raise ValueError(f"Valor de HAB {hab} não está no intervalo válido (0-15)")
        return tabela_custos[hab]
    
    def _hp_val(self, fis: int) -> int:
        # Simplificação da sua tabela para o esqueleto
        tabela_hp = {0: 10, 1: 20, 2: 30, 3: 40, 4: 50, 5: 65, 6: 80, 7: 95, 8: 115, 9: 135, 10: 155, 11: 180, 12: 205, 13: 230, 14: 270, 15: 310}
        if fis not in tabela_hp:
            raise ValueError(f"Valor de FIS {fis} não está no intervalo válido (0-15)")
        return tabela_hp[fis]
    
    def _mp_val(self, men: int) -> int:
        # Simplificação da sua tabela para o esqueleto
        tabela_mp = {0: 0, 1: 10, 2: 40, 3: 60, 4: 70, 5: 80, 6: 100, 7: 120, 8: 140, 9: 160, 10: 180, 11: 200, 12: 220, 13: 240, 14: 260, 15: 300}
        if men not in tabela_mp:
            raise ValueError(f"Valor de MEN {men} não está no intervalo válido (0-15)")
        return tabela_mp[men]
    
    def calcular_bdc(self, style: CombatStyle):
        # 1. Criamos um "tradutor" ligando as strings do Estilo aos valores do Personagem
        mapa_atributos = {
            "FIS": self.fis,
            "HAB": self.hab,
            "MEN": self.men
        }
        
        # 2. Resgatamos os valores na ordem exata que o Estilo de Combate mandou
        valor_main = mapa_atributos[self.combat_style.main]
        valor_sec = mapa_atributos[self.combat_style.second]
        valor_third = mapa_atributos[self.combat_style.third]
        
        # 3. Calculamos o BdC usando a divisão inteira (//)
        self.bdc = (valor_main // 2) + (valor_sec // 3) + (valor_third // 4)

        return self.bdc
    
    def generate_focus(self) -> int:
         # O teto máximo é 5x a Mente
        max_focus = 5 * self.men
    
        # Soma a MEN, mas trava o resultado no max_focus
        self.floating_focus = min(self.floating_focus + self.men, max_focus)
    
        return self.floating_focus
    
    def generate_mana(self) -> int:
        max_floating = 5 * self.men
        
        # Quanto de mana ele TEM ESPAÇO para gerar nas mãos?
        space_available = max_floating - self.floating_mp
        
        # Quanto ele REALMENTE consegue gerar neste turno? (limitado pela MEN e pelo tanque)
        mana_to_pull = min(self.men, space_available, self.current_mp)
        
        self.current_mp -= mana_to_pull
        self.floating_mp += mana_to_pull
        
        return self.floating_mp
    
    def take_damage(self, damage: int):
        self.current_hp = max(self.current_hp - damage, 0)

    def spend_focus(self, amount: int) -> bool:
        if self.floating_focus >= amount:
            self.floating_focus -= amount
            return True
        return False
    
    def spend_mana(self, amount: int) -> bool:
        if self.floating_mp >= amount:
            self.floating_mp -= amount
            return True
        return False

    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def equip_weapon(self, weapon: Weapon):
        self.weapon = weapon
        self.pda = weapon.pda
        self.mda = weapon.mda

    def equip_armor(self, armor: Armor):
        if self.armor is not None:
            # Se já tiver uma armadura equipada, remove o bônus de HP dela
            self.max_hp -= self.armor.hp_bonus
            self.current_hp = max(self.current_hp - self.armor.hp_bonus, 1)
        self.armor = armor
        self.max_hp += armor.hp_bonus
        self.current_hp += armor.hp_bonus

class BattleManager:
    """
    O Gerenciador Central. Controla o Relógio de Ticks e o Event Bus (Observer Pattern).
    """
    def __init__(self):
        # Min-Heap para o Relógio de Ticks: (tick_number, char_id, character_object)
        self.timeline = []
        self.current_tick = 0
        
        self.characters: Dict[str, Character] = {}
        
        # Event Bus (Observer Pattern) para passivas e aprimoramentos
        self.listeners: Dict[str, List[Callable]] = {
            'on_defense_reaction': [],
            'on_hit_check': [],
            'on_gda_modify': [],
            'on_damage_calculation': [],
            'on_damage_taken': [],
            'on_attack_end': [],
            'on_turn_end': [],
            'on_turn_start': []
        }

    def add_character(self, character: 'Character', start_tick: int = 0):
        self.characters[character.char_id] = character
        heapq.heappush(self.timeline, (start_tick, character.char_id, character))
        
        # O Pulo do Gato: Registra todos os listeners deste personagem
        for ability in character.abilities:
            ability.register_listeners(character, self)

    def subscribe(self, event_name: str, callback: Callable):
        if event_name in self.listeners:
            self.listeners[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: Callable):
        if event_name in self.listeners:
            self.listeners[event_name].remove(callback)

    def emit(self, event_name: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispara um evento para todos os ouvintes. Os ouvintes podem modificar o event_data (ex: dobrar GdA).
        """
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(event_data)
        return event_data

    def get_next_actor(self) -> 'None | Character':
        """
        Avança o tempo para o próximo personagem na fila.
        """
        if not self.timeline:
            return None
            
        tick, char_id, character = heapq.heappop(self.timeline)
        self.current_tick = tick
        return character

    def schedule_next_action(self, character: Character, action_cost: int):
        """
        Reinsere o personagem na fila de tempo após ele agir.
        """
        next_tick = self.current_tick + action_cost
        heapq.heappush(self.timeline, (next_tick, character.char_id, character))
    
    def delay_character(self, character: 'Character', extra_ticks: int | float):
        """
        Encontra o personagem na linha do tempo e empurra a ação dele mais para o futuro.
        """
        for i, entry in enumerate(self.timeline):
            tick, char_id, char = entry 
            
            if char_id == character.char_id:
                # 1. Remove a "senha" antiga da fila
                self.timeline.pop(i)
                
                # 2. Calcula o novo tempo (empurrando pro futuro)
                novo_tick = tick + extra_ticks
                
                # 3. Insere a nova "senha" restaurando os TRÊS itens da tupla!
                self.timeline.append((novo_tick, char_id, char))
                
                # 4. Reorganiza a árvore do Min-Heap com a ferramenta certa
                heapq.heapify(self.timeline)
                
                break # Achou o personagem, não precisa continuar procurando

class BasicAttack(Ability):
    
    def __init__(self):
        # O Ataque Básico custa 0 de foco e seu tempo de ação é dinâmico (vem da HAB)
        super().__init__(name="Ataque Básico", focus_cost=0, action_cost=0)
    
    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        # Regra 1: O alvo está vivo?
        if not target.is_alive():
            return False, "O alvo já está derrotado!"
        
        return True, ""

    def execute(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager', **kwargs) -> Dict[str, Any]:
        event_data = {'caster': caster, 'target': target, 'battle_manager': battle_manager, 'is_skill': kwargs.get('is_skill', False)}
        # 1. Rola os dados
        atk_roll = random.randint(1, caster.atk_die)
        mod_atk_roll = atk_roll + caster.bdc + caster.bda
        event_data["history"] = [f"{caster.name} rolou {atk_roll} para atacar!"]
        event_data["history"].append(f"Bônus de Combate do atacante: {caster.bdc} | Bônus de Ataque: {caster.bda} | Total modificado: {mod_atk_roll}")
        def_roll = random.randint(1, target.def_die)
        mod_def_roll = def_roll + target.bdc + target.bdd
        event_data["history"].append(f"{target.name} rolou {def_roll} para defender!")
        event_data["history"].append(f"Bônus de Combate do defensor: {target.bdc} | Bônus de Defesa: {target.bdd} | Total modificado: {mod_def_roll}")
        
        # 2. Calcula o GdA base
        gda = mod_atk_roll - mod_def_roll
        event_data['gda'] = gda
        event_data["history"].append(f"GdA base é {gda} ({mod_atk_roll} - {mod_def_roll})")
        event_data = battle_manager.emit('on_defense_reaction', event_data) # Permite que passivas possam anular o hit (ex: Esquiva Perfeita)
        event_data = battle_manager.emit('on_hit_check', event_data) # Permite que passivas chequem o gda inicial para suas condições de ativação
        
        event_data = battle_manager.emit('on_gda_modify', event_data) # Permite que passivas modifiquem o GdA (ex: Força Bruta, Letalidade)
        final_gda = event_data['gda']

        damage = 0
        hit = False

        # 3. Resolve o Dano
        if final_gda > 0:
            event_data["history"].append("O ataque acertou!")
            event_data = battle_manager.emit('on_damage_calculation', event_data) # Momento onde Habilidades Marciais aplicam seus bônus de dano
            final_gda = event_data['gda'] # Recarrega o GdA caso alguma passiva tenha modificado ele na etapa de cálculo de dano
            hit = True
            damage = caster.pda + (caster.mda * final_gda)
            event_data["history"].append(f"Dano calculado: PDA {caster.pda} + (MDA {caster.mda} x GdA {final_gda}) = {damage}") 
            target.take_damage(damage)
            event_data["damage"] = damage
            event_data = battle_manager.emit('on_damage_taken', event_data)
        else:
            event_data["history"].append("O ataque foi completamente defendido!")

        # O custo de ação é puxado direto do atributo do personagem
        self.action_cost = caster.action_cost_base

        event_data = battle_manager.emit('on_attack_end', event_data)

        # Retorna o resumo para o View (Terminal/Pygame) renderizar
        return event_data

class GenerateManaAction(Ability):
    def __init__(self):
        # Gerar mana não custa foco, mas custa o Tempo de Ação base do personagem
        super().__init__(name="Concentrar Mana", focus_cost=0, action_cost=0)

    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        # Regra 1: O tanque secou?
        if caster.current_mp <= 0:
            return False, "Sua reserva diária de mana esgotou!"
            
        # Regra 2: A mão já está cheia?
        max_floating = 5 * caster.men
        if caster.floating_mp >= max_floating:
            return False, "Sua mana engatilhada já está no limite!"
            
        return True, ""

    def execute(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager') -> dict:
        # Usa a lógica que você já fez na classe Character
        old_floating = caster.floating_mp
        new_floating = caster.generate_mana()
        generated = new_floating - old_floating
        
        self.action_cost = caster.action_cost_base # Puxa o custo de HAB

        return {
            "history": f"{caster.name} gerou {generated} de Mana!"
        }

class GenerateFocusAction(Ability):
    def __init__(self):
        # Como é uma ação ativa do turno, não custa foco para usar, mas custará o Tempo de Ação
        super().__init__(name="Concentrar Foco", focus_cost=0, action_cost=0)

    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        # O teto máximo de foco é 5 vezes a Mente (MEN)
        max_focus = 5 * caster.men
        
        # Validação: O tanque já está cheio?
        if caster.floating_focus >= max_focus:
            return False, "Seu Foco já está no limite máximo!"
            
        return True, ""

    def execute(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager') -> dict:
        # Guardamos o valor antigo para saber exatamente quanto foi gerado neste turno
        old_focus = caster.floating_focus
        
        # Chama o método matemático limpo que você já construiu no Character
        new_focus = caster.generate_focus()
        
        generated = new_focus - old_focus
        
        # A ação gasta o tempo padrão do personagem no Relógio de Ticks
        self.action_cost = caster.action_cost_base

        # Retorna o dicionário para a View ler e mostrar na tela/terminal
        return {
            "history": f"{caster.name} respirou fundo e gerou {generated} de Foco!"
        }

class ForcaBruta(Ability):
    def __init__(self):
        # É uma passiva, não gasta recursos nem tempo
        super().__init__(name="Força Bruta", focus_cost=0, action_cost=0)

    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        # Aqui ela avisa o BattleManager: "Me chame quando o GdA for calculado!"
        battle_manager.subscribe('on_gda_modify', self.apply_passive)

        # Guardamos a referência do dono para saber se o evento é nosso
        self.caster = caster

    def apply_passive(self, event_data: dict) -> dict:
        # Verifica se quem está atacando é o dono desta habilidade
        if event_data['caster'].char_id == self.caster.char_id:
            if event_data['gda'] > 0:
                # Dobra o GdA silenciosamente
                event_data['gda'] *= 2 
                event_data['history'].append(f"[PASSIVA] {self.caster.name} ativou Força Bruta! GdA dobrado para {event_data['gda']}!")
        
        return event_data

    # can_execute e execute podem simplesmente retornar False ou pass, 
    # pois o jogador nunca seleciona essa habilidade ativamente no menu.
    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        return False, "Esta é uma habilidade passiva."
    
class RitmoAcelerado(Ability):
    def __init__(self):
        super().__init__(name="Ritmo Acelerado", focus_cost=0, action_cost=0)
        self.current_target_id = None
        
        # O nosso Mutex / Guarda de Reentrada
        self.is_busy = False
    
    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        # Aqui ela avisa o BattleManager: "Me chame quando o ataque terminar!"
        battle_manager.subscribe('on_attack_end', self.checar_ataque_bonus)

        # Guardamos a referência do dono para saber se o evento é nosso
        self.caster = caster

    def checar_ataque_bonus(self, event_data: dict) -> dict:
        # 1. A trava de segurança! Se já estamos processando um ataque bônus, ignora.
        if self.is_busy:
            return event_data
        
        if event_data.get('is_skill', False): 
            return event_data

        if event_data['caster'].char_id == self.caster.char_id:
            
            if self.current_target_id == event_data['target'].char_id:
                event_data['history'].append(f"[PASSIVA] Ritmo Acelerado! Ataque extra em {event_data['target'].name}!")
                
                ataque_bonus = BasicAttack()
                self.current_target_id = None
                
                # 2. Tranca o Mutex
                self.is_busy = True 
                
                try:
                    # 3. Executa o ataque. Qualquer evento que ele gerar vai bater no 'if self.is_busy' ali em cima e ser ignorado por esta passiva.
                    extra_data = ataque_bonus.execute(self.caster, event_data['target'], event_data['battle_manager'])
                    event_data['history'].extend(extra_data['history'])
                finally:
                    # 4. Libera o Mutex, INDEPENDENTEMENTE de o ataque ter dado certo ou lançado uma exceção/erro.
                    self.is_busy = False
            else:
                # Se o ataque foi para um alvo diferente, atualiza o alvo monitorado por esta passiva.
                self.current_target_id = event_data['target'].char_id
                
        return event_data

class Combo(Ability):
    
    def __init__(self, name = "Combo", focus_cost = 0, action_cost = 0):
        super().__init__(name, focus_cost, action_cost)
        self.stage = 0
    
    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        # Aqui ela avisa o BattleManager: "Me chame quando o ataque terminar!"
        battle_manager.subscribe('on_attack_end', self.checar_ataque_bonus)

        # Guardamos a referência do dono para saber se o evento é nosso
        self.caster = caster
    
    def checar_ataque_bonus(self, event_data: dict) -> dict:
        if event_data.get('is_skill', False): 
            return event_data
        if event_data['caster'].char_id == self.caster.char_id:
            if self.stage == 0 or self.stage == 1:
                if event_data['gda'] > 0:
                    event_data['history'].append(f"[PASSIVA] Combo! {self.caster.name} ataca novamente!")
                    ataque_bonus = BasicAttack()
                    self.stage += 1
                    extra_data = ataque_bonus.execute(self.caster, event_data['target'], event_data['battle_manager'])
                    event_data['history'].extend(extra_data['history'])
                else:
                    self.stage = 0 # Reseta o combo se errar o ataque
            else:
                self.stage = 0 # Reseta o combo se chegar no estágio 3 (ou seja, após 3 ataques)
        return event_data

class SkillNivelUm(Ability):
    def __init__(self):
        super().__init__(name="Skill Nível 1", focus_cost=4, action_cost=0)

    def can_execute(self, caster: 'Character', target: 'Character') -> tuple[bool, str]:
        if caster.floating_focus < self.focus_cost:
            return False, "Foco insuficiente para usar esta habilidade!"
        return True, ""

    def execute(self, caster: 'Character', target: 'Character', battle_manager: 'BattleManager') -> dict:
        self.caster = caster
        caster.spend_focus(self.focus_cost)
        battle_manager.subscribe('on_damage_calculation', self.add_Damage)
        ataque = BasicAttack()
        event_data = ataque.execute(caster, target, battle_manager, is_skill=True)
        battle_manager.unsubscribe('on_damage_calculation', self.add_Damage)

        return event_data
    
    def add_Damage(self, event_data: dict) -> dict:
        if event_data['caster'].char_id == self.caster.char_id:
            event_data['gda'] += 5 # Adiciona um bônus fixo de GdA
            event_data['history'].append(f"[SKILL] {self.name} aumentou o GdA em +5!")
        return event_data

class Letalidade(Ability):
    def __init__(self):
        super().__init__(name="Letalidade", focus_cost=0, action_cost=0)

    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        battle_manager.subscribe('on_gda_modify', self.apply_passive)
        self.caster = caster

    def apply_passive(self, event_data: dict) -> dict:
        if event_data['caster'].char_id == self.caster.char_id:
            if event_data['gda'] > 0:
                roll = random.randint(1, 6)
                event_data['gda'] += roll # Adiciona 1d6 de GdA
                event_data['history'].append(f"[PASSIVA] {self.caster.name} ativou Letalidade! GdA aumentado em {roll} para {event_data['gda']}!")
        
        return event_data

class MãosPesadas(Ability):
    def __init__(self):
        super().__init__(name="Mãos Pesadas", focus_cost=0, action_cost=0)
    
    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        battle_manager.subscribe('on_hit_check', self.apply_passive)
        self.caster = caster
    
    def apply_passive(self, event_data: dict) -> dict:
        if event_data['caster'].char_id == self.caster.char_id:
            if event_data['gda'] > 3:
                atordoamento = Atordoado(duration=0, target=event_data['target'])
                atordoamento.apply(event_data['battle_manager'])
        return event_data
    
class Evasão(Ability):
    def __init__(self):
        super().__init__(name="Evasão", focus_cost=2, action_cost=0)
    
    def register_listeners(self, caster: 'Character', battle_manager: 'BattleManager'):
        battle_manager.subscribe('on_defense_reaction', self.apply_passive)
        self.caster = caster
    
    def can_execute(self, caster: Character, target: Character) -> tuple[bool, str]:
        if caster.floating_focus < self.focus_cost:
            return False, "Foco insuficiente para usar esta habilidade!"
        return True, ""
    
    def apply_passive(self, event_data: dict) -> dict:
        if event_data['target'].char_id == self.caster.char_id:
            if event_data['gda'] > 0:
                can_use, msg = self.can_execute(self.caster, event_data['caster'])
                if can_use:
                    self.caster.spend_focus(self.focus_cost)
                    roll = random.randint(1, 4)
                    event_data['gda'] -= roll # Reduz o GdA com um rolamento de 1d4
                    event_data['history'].append(f"[SKILL] {self.caster.name} usou Evasão! GdA reduzido em {roll} para {event_data['gda']}!")
        
        return event_data


class Atordoado(StatusEffect):
    def __init__(self, duration: int, target: 'Character'):
        super().__init__(name="Atordoado", duration=duration, target=target)

    def on_apply(self):
        # Pode usar self.character sem medo do VS Code gritar!
        self.character.bdc -= 2
        if self.battle_manager is not None:
            battle_manager = self.battle_manager
            battle_manager.delay_character(self.character, self.character.action_cost_base * 0.5)

    def on_remove(self):
        self.character.bdc += 2
    
    def register_listeners(self, battle_manager: BattleManager):
        battle_manager.subscribe('on_turn_start', self.effect_end)
    
    def effect_end(self, event_data: dict) -> dict:
        if event_data.get('character') and event_data['character'].char_id == self.character.char_id:
            self.remove()
        return event_data
    
    def on_unsubscribe(self, battle_manager: 'BattleManager'):
        battle_manager.unsubscribe('on_turn_start', self.effect_end)


class PvPSimulator:
    def __init__(self, battle_manager: BattleManager, character1: Character, character2: Character):
        self.battle_manager = battle_manager
        self.character1 = character1
        self.character2 = character2

    def single_battle_verbose(self):
        turn_count = 0
        max_turns = 1000
        if(self.character1.action_cost_base != self.character2.action_cost_base):
            self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base)
            self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base)
        else:
            while True:
                roll1 = random.randint(1, 10)
                roll2 = random.randint(1, 10)
                if roll1 != roll2:
                    break
            if roll1 > roll2:
                self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base)
                self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base + 1)
            elif roll2 > roll1:
                self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base)
                self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base + 1)
        while turn_count < max_turns and self.character1.is_alive() and self.character2.is_alive():
            actor = self.battle_manager.get_next_actor()
            self.battle_manager.emit('on_turn_start', {'character': actor})
            if actor is None:
                break
            
            print(f"\n[Turno {turn_count + 1}] {actor.name} (HP: {actor.current_hp}/{actor.max_hp}, Foco: {actor.floating_focus}) está agindo!")
            
            target = self.character2 if actor.char_id == self.character1.char_id else self.character1
            can_use, msg = actor.abilities[1].can_execute(actor, target)
            if can_use:
                ability = actor.abilities[1]
                result = actor.abilities[1].execute(actor, target, self.battle_manager)
                skill_used = True
                for line in result.get("history", []):
                    print(f"  {line}")
            else:
                ability = actor.abilities[0]  # Sempre usa ataque básico
                skill_used = False
                can_use, msg = ability.can_execute(actor, target)
                if can_use:
                    result = ability.execute(actor, target, self.battle_manager)
                    for line in result.get("history", []):
                        print(f"  {line}")
                else:
                    print(f"  {msg}")
            
            self.battle_manager.schedule_next_action(actor, ability.action_cost or actor.action_cost_base)
            turn_count += 1
            if skill_used is False:
                actor.generate_focus()
            self.battle_manager.emit('on_turn_end', {'character': actor})
        
        print(f"\n{'='*50}")
        print(f"Batalha terminada! {self.character1.name}: {self.character1.current_hp}HP | {self.character2.name}: {self.character2.current_hp}HP")

    def single_battle_summary(self):
        # Método para simular uma batalha e retornar apenas o resultado final (sem prints detalhados)
        turn_count = 0
        max_turns = 1000
        if(self.character1.action_cost_base != self.character2.action_cost_base):
            self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base)
            self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base)
        else:
            while True:
                roll1 = random.randint(1, 10)
                roll2 = random.randint(1, 10)
                if roll1 != roll2:
                    break
            if roll1 > roll2:
                self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base)
                self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base + 1)
            elif roll2 > roll1:
                self.battle_manager.add_character(self.character2, start_tick=self.character2.action_cost_base)
                self.battle_manager.add_character(self.character1, start_tick=self.character1.action_cost_base + 1)        
        while turn_count < max_turns and self.character1.is_alive() and self.character2.is_alive():
            actor = self.battle_manager.get_next_actor()
            if actor is None:
                break
            
            target = self.character2 if actor.char_id == self.character1.char_id else self.character1
            can_use, msg = actor.abilities[1].can_execute(actor, target)
            if can_use:
                ability = actor.abilities[1]
                skill_used = True
                ability.execute(actor, target, self.battle_manager)
            else:
                ability = actor.abilities[0]
                skill_used = False

                can_use, msg = ability.can_execute(actor, target)
                if can_use:
                    ability.execute(actor, target, self.battle_manager)
            
            self.battle_manager.schedule_next_action(actor, ability.action_cost or actor.action_cost_base)
            turn_count += 1
            if skill_used is False:
                actor.generate_focus()
            self.battle_manager.emit('on_turn_end', {'character': actor})
        
        return {
            "winner": self.character1.name if self.character1.is_alive() else self.character2.name,
            "turns": turn_count,
            "final_hp": {
                self.character1.name: self.character1.current_hp,
                self.character2.name: self.character2.current_hp
            }
        }

def simulate_multiple_battles(num_simulations: int, char1_data: Dict[str, Any], char2_data: Dict[str, Any]) -> Dict[str, Any]:
        results = {
            char1_data["Nome"]: 0,
            char2_data["Nome"]: 0,
            "draws": 0,
            "total_turns": 0,
            "average_turns": 0.0
        }
        
        turns_list = []
        for _ in range(num_simulations):
            heroi1 = Character(
            char_id="hero_1",
            name=char1_data["Nome"],
            attributes=[char1_data["FIS"], char1_data["HAB"], char1_data["MEN"]],
            combat_style = char1_data["CombatStyle"]
            )       

            heroi1.equip_weapon(char1_data["Weapon"])
            heroi1.equip_armor(char1_data["Armor"])
            heroi1.abilities = char1_data["Abilities"]()

            heroi2 = Character(
            char_id="hero_2",
            name=char2_data["Nome"],
            attributes=[char2_data["FIS"], char2_data["HAB"], char2_data["MEN"]],
            combat_style = char2_data["CombatStyle"],
            bda=2
            )

            heroi2.equip_weapon(char2_data["Weapon"])
            heroi2.equip_armor(char2_data["Armor"])
            heroi2.abilities = char2_data["Abilities"]()
            
            simulator = PvPSimulator(BattleManager(), heroi1, heroi2)
            
            summary = simulator.single_battle_summary()
            winner = summary["winner"]
            turns = summary["turns"]
            
            turns_list.append(turns)
            
            if winner == char1_data["Nome"]:
                results[char1_data["Nome"]] += 1
            elif winner == char2_data["Nome"]:
                results[char2_data["Nome"]] += 1
            else:
                results["draws"] += 1
        
        results["total_turns"] = sum(turns_list)
        results["average_turns"] = sum(turns_list) / len(turns_list) if turns_list else 0.0
        
        return results

Char1 = {"Nome": "Destruidor", 
         "FIS": 5, "HAB": 3, "MEN": 2,
         "Weapon": Weapon(name="Espada Larga", pda=15, mda=1), 
         "Armor": Armor(name="Armadura Pesada", hp_bonus=25),
         "Abilities": lambda: [BasicAttack(), SkillNivelUm(), GenerateManaAction(), GenerateFocusAction(),],
         "CombatStyle": combat_styles["Duelista"]}

Char2 = {"Nome": "Cavaleiro", 
         "FIS": 5, "HAB": 3, "MEN": 2,
         "Weapon": Weapon(name="Espada Larga", pda=15, mda=1), 
         "Armor": Armor(name="Armadura Pesada", hp_bonus=25),
         "Abilities": lambda: [BasicAttack(), SkillNivelUm(), GenerateManaAction(), GenerateFocusAction()],
         "CombatStyle": combat_styles["Duelista"]}

def mult():
    results = simulate_multiple_battles(10000, Char1, Char2)
    
    print("Resultados das 10000 batalhas:")
    print(f"{Char1['Nome']}: {results[Char1['Nome']]} vitórias")
    print(f"{Char2['Nome']}: {results[Char2['Nome']]} vitórias")
    print(f"Empates: {results['draws']}")
    print(f"Total de turnos: {results['total_turns']}")
    print(f"Média de turnos por batalha: {results['average_turns']:.2f}")

def mono():
    heroi1 = Character(
            char_id="hero_1",
            name=Char1["Nome"],
            attributes=[Char1["FIS"], Char1["HAB"], Char1["MEN"]],
            combat_style = Char1["CombatStyle"],
            ) 
    heroi1.equip_weapon(Char1["Weapon"])
    heroi1.equip_armor(Char1["Armor"])
    heroi1.abilities = Char1["Abilities"]()

    heroi2 = Character(
            char_id="hero_2",
            name=Char2["Nome"],
            attributes=[Char2["FIS"], Char2["HAB"], Char2["MEN"]],
            combat_style = Char2["CombatStyle"],
            bda=1
            )
    heroi2.equip_weapon(Char2["Weapon"])
    heroi2.equip_armor(Char2["Armor"])
    heroi2.abilities = Char2["Abilities"]()
   
    simulator = PvPSimulator(BattleManager(), heroi1, heroi2)
    simulator.single_battle_verbose()

def main():
    if len(sys.argv) != 2:
        print("Usage: python BattleEngine.py <mono|multi>")
        return
    mode = sys.argv[1]
    if mode == "mono":
        mono()
    elif mode == "multi":
        mult()
    else:
        print("Invalid mode. Use 'mono' or 'multi'")

if __name__ == "__main__":
    main()
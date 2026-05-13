from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from core.Structs import BattleResult

class BattleView:
    def present_battle(self, result: 'BattleResult'):
        """
        Parses and prints the complete battle narrative from a BattleResult.
        """
        for entry in result.history:
            print(self._parse_entry(entry))
        
        all_chars = result.winners + result.losers
        summary_line = "Batalha terminada! " + " | ".join([f"{c.name}: {c.current_hp}HP" for c in all_chars])
        
        print(f"\n{'='*50}")
        print(summary_line)

    def present_summary(self, results: List['BattleResult'], char1_id: str, char2_id: str):
        """
        Calculates and prints aggregated statistics for multiple battles.
        """
        total = len(results)
        wins1 = 0
        wins2 = 0
        draws = 0
        total_turns = 0
        
        for res in results:
            total_turns += res.duration
            # Determine winner by checking winners list against the IDs provided
            winner_ids = [w.char_id for w in res.winners]
            
            if char1_id in winner_ids and char2_id not in winner_ids:
                wins1 += 1
            elif char2_id in winner_ids and char1_id not in winner_ids:
                wins2 += 1
            elif not res.winners:
                draws += 1
            else:
                # This could be a complex case with multiple winners, 
                # but for 1v1 we simplify.
                draws += 1
        
        avg_turns = total_turns / total if total > 0 else 0
        
        print(f"Resultados das {total} batalhas:")
        print(f"{char1_id}: {wins1} vitórias")
        print(f"{char2_id}: {wins2} vitórias")
        print(f"Empates: {draws}")
        print(f"Total de turnos: {total_turns}")
        print(f"Média de turnos por batalha: {avg_turns:.2f}")

    def _parse_entry(self, entry: str) -> str:
        """
        Translates a single structured history tag into a human-readable string.
        """
        parts = entry.split('|')
        tag = parts[0]
        try:
            if tag == "EXEC":
                return f"[ACTION] {parts[2]} uses {parts[1]}"
            elif tag == "ROLL":
                return f"[ROLL] {parts[4]}: {parts[1]} -> {parts[2]} (d{parts[3]})"
            elif tag == "MOD":
                return f"[MODIFIER] {parts[1]} adds {parts[2]} to {parts[3]}"
            elif tag == "HIT":
                return f"[HIT] {parts[1]}"
            elif tag == "MISS":
                return f"[MISS] {parts[1]}"
            elif tag == "DMG":
                return f"[DAMAGE] {parts[1]} receives {parts[2]} {parts[3]} damage"
            elif tag == "HP":
                return f"[STATS] {parts[1]} HP: {parts[3]} ({parts[2]})"
            elif tag == "FOCUS":
                return f"[STATS] {parts[1]} FOCUS: {parts[3]} ({parts[2]})"
            elif tag == "MANA_F":
                return f"[STATS] {parts[1]} Floating MANA: {parts[3]} ({parts[2]})"
            elif tag == "MANA_T":
                return f"[STATS] {parts[1]} Total MANA: {parts[3]} ({parts[2]})"
            elif tag == "MSG":
                return f"[MSG] {parts[1]}"
            elif tag == "DEATH":
                return f"[DEATH] {parts[1]} has been defeated!"
            elif tag == "STATUS":
                return f"[STATUS] {parts[1]}: {parts[2]} ({parts[3]} turns) -> {parts[4]}"
            elif tag == "TURN_START":
                return f">>> TURN START: {parts[1]} (HP: {parts[2]}/{parts[3]}, MP: {parts[4]}/{parts[5]}, Focus: {parts[6]}, Mana: {parts[7]})"
            elif tag == "PASSIVE":
                return f"[PASSIVE] {parts[2]} triggers {parts[1]}"
            elif tag == "ACTION_HOOK":
                return f"[HOOK] {parts[2]} triggers {parts[1]} effect"
            elif tag == "STATUS_HOOK":
                return f"[HOOK] {parts[1]} effect triggered on {parts[2]}"
            elif tag == "ATK_LOAD":
                return f"[ATK_LOAD] {parts[1]} modified: {parts[3]} ({parts[2]})"
            elif tag == "ATK_CALC":
                # ATK_CALC|actor_id|roll|rank|bda|final
                return f"[CALC] {parts[1]} Final Attack: {parts[5]} = {parts[2]} (Roll) + {parts[3]} (Rank) + {parts[4]} (BdA)"
            elif tag == "DMG_CALC":
                # DMG_CALC|target_id|pda|gda|mda|modifier|final
                return f"[CALC] {parts[1]} Damage: {parts[6]} = {parts[2]} (PdA) + ({parts[3]} GdA * {parts[4]} MdA) + {parts[5]} (Mod)"
            elif tag == "DEF_CALC":
                # DEF_CALC|target_id|roll|rank|bdd|final
                return f"[CALC] {parts[1]} Final Defense: {parts[5]} = {parts[2]} (Roll) + {parts[3]} (Rank) + {parts[4]} (BdD)"
            else:
                return entry
        except IndexError:
            return entry

    @staticmethod
    def parse(history: List[str]) -> List[str]:
        """
        Legacy static method for compatibility. 
        Will be deprecated in favor of present_battle.
        """
        view = BattleView()
        return [view._parse_entry(entry) for entry in history]

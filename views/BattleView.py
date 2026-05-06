from typing import List

class BattleView:
    @staticmethod
    def parse(history: List[str]) -> List[str]:
        parsed = []
        for entry in history:
            parts = entry.split('|')
            tag = parts[0]
            try:
                if tag == "EXEC":
                    parsed.append(f"[ACTION] {parts[2]} uses {parts[1]}")
                elif tag == "ROLL":
                    parsed.append(f"[ROLL] {parts[4]}: {parts[1]} -> {parts[2]} (d{parts[3]})")
                elif tag == "MOD":
                    parsed.append(f"[MODIFIER] {parts[1]} adds {parts[2]} to {parts[3]}")
                elif tag == "HIT":
                    parsed.append(f"[HIT] {parts[1]}")
                elif tag == "MISS":
                    parsed.append(f"[MISS] {parts[1]}")
                elif tag == "DMG":
                    parsed.append(f"[DAMAGE] {parts[1]} receives {parts[2]} {parts[3]} damage")
                elif tag == "HP":
                    parsed.append(f"[STATS] {parts[1]} HP: {parts[3]} ({parts[2]})")
                elif tag == "FOCUS":
                    parsed.append(f"[STATS] {parts[1]} FOCUS: {parts[3]} ({parts[2]})")
                elif tag == "MANA_F":
                    parsed.append(f"[STATS] {parts[1]} Floating MANA: {parts[3]} ({parts[2]})")
                elif tag == "MANA_T":
                    parsed.append(f"[STATS] {parts[1]} Total MANA: {parts[3]} ({parts[2]})")
                elif tag == "MSG":
                    parsed.append(f"[MSG] {parts[1]}")
                elif tag == "DEATH":
                    parsed.append(f"[DEATH] {parts[1]} has been defeated!")
                elif tag == "STATUS":
                    parsed.append(f"[STATUS] {parts[1]}: {parts[2]} ({parts[3]} turns) -> {parts[4]}")
                elif tag == "TURN_START":
                    parsed.append(f">>> TURN START: {parts[1]} (HP: {parts[2]}/{parts[3]}, MP: {parts[4]}/{parts[5]}, Focus: {parts[6]}, Mana: {parts[7]})")
                else:
                    parsed.append(entry)
            except IndexError:
                # If there is a malformed tag with missing parts, just append the raw entry
                parsed.append(entry)
        return parsed

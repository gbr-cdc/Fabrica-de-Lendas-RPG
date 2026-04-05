from implementation.Actions import (
    BasicAttack,
    GenerateManaAction,
    GenerateFocusAction,
    SkillNivelUm,
    Evasão,
)
from implementation.Passives import (
    Letalidade,
    MãosPesadas,
    ForcaBruta,
    RitmoAcelerado,
    Combo,
)

ability_registry = {
    "BasicAttack": BasicAttack,
    "GenerateManaAction": GenerateManaAction,
    "GenerateFocusAction": GenerateFocusAction,
    "SkillNivelUm": SkillNivelUm,
    "Evasão": Evasão,
    "Letalidade": Letalidade,
    "MãosPesadas": MãosPesadas,
    "ForcaBruta": ForcaBruta,
    "RitmoAcelerado": RitmoAcelerado,
    "Combo": Combo,
}

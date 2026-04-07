from implementation.Actions import (
    BasicAttack,
    GenerateManaAction,
    GenerateFocusAction,
    SkillNivelUm,
)
from implementation.Passives import (
    ForçaBruta,
    GracaDoDuelista,
    MãosPesadas,
    Combo,
)

ability_registry = {
    "BasicAttack": BasicAttack,
    "GenerateManaAction": GenerateManaAction,
    "GenerateFocusAction": GenerateFocusAction,
    "SkillNivelUm": SkillNivelUm,
    "MãosPesadas": MãosPesadas,
    "ForçaBruta": ForçaBruta,
    "Combo": Combo,
    "GraçaDoDuelista": GracaDoDuelista
}

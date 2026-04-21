import matplotlib.pyplot as plt
from collections import defaultdict

def calcular_estatisticas(dado_atk, mod_atk, dado_def, mod_def):
    resultados = defaultdict(int)
    total_combinacoes = dado_atk * dado_def
    
    # Testa todas as combinações possíveis
    for a in range(1, dado_atk + 1):
        for d in range(1, dado_def + 1):
            total_atk = a + mod_atk
            total_def = d + mod_def
            
            # Dano só ocorre se ataque for estritamente maior
            if total_atk > total_def:
                dano = total_atk - total_def
                resultados[dano] += 1
            else:
                resultados[0] += 1
                
    # Calcula as probabilidades em %
    distribuicao = {dano: (cont / total_combinacoes) * 100 
                    for dano, cont in sorted(resultados.items())}
    
    chance_acerto = sum(prob for dano, prob in distribuicao.items() if dano > 0)
    dano_medio = sum(dano * (prob / 100) for dano, prob in distribuicao.items())
    
    return dano_medio, chance_acerto, distribuicao


def gerar_histograma(distribuicao, titulo, chance_acerto=None, dano_medio=None, dano_medio_acerto=None):
    danos = sorted(distribuicao.keys())
    probs = [distribuicao[d] for d in danos]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(danos, probs, color='skyblue', edgecolor='black')
    plt.title(titulo)
    plt.xlabel('Dano (0 = Erro / Defesa bem-sucedida)')
    plt.ylabel('Probabilidade (%)')
    plt.xticks(range(0, max(danos) + 1))
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Exibe valores acima de cada barra
    for bar, prob in zip(bars, probs):
        altura = bar.get_height()
        if altura > 0:
            plt.text(bar.get_x() + bar.get_width() / 2, altura,
                     f"{prob:.1f}%", ha='center', va='bottom', fontsize=8)

    # Exibe estatísticas no canto superior direito
    if chance_acerto is not None and dano_medio is not None and dano_medio_acerto is not None:
        box_text = (
            f"Chance de Acerto: {chance_acerto:.1f}%\n"
            f"Dano Médio (Geral): {dano_medio:.2f}\n"
            f"Dano Médio (Acerto): {dano_medio_acerto:.2f}"
        )
        plt.gca().text(
            0.98, 0.98, box_text,
            transform=plt.gca().transAxes,
            fontsize=10,
            va='top', ha='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8, edgecolor='gray')
        )

    plt.tight_layout()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Simula distribuição de dano para 1dX vs 1dY com modificadores.')
    parser.add_argument('atk', type=int, help='Número de faces do dado de ataque (ex: 8 para d8)')
    parser.add_argument('mod_atk', type=int, nargs='?', default=0, help='Modificador de ataque (opcional, padrão 0)')
    parser.add_argument('defs', type=int, help='Número de faces do dado de defesa (ex: 10 para d10)')
    parser.add_argument('mod_def', type=int, nargs='?', default=0, help='Modificador de defesa (opcional, padrão 0)')
    parser.add_argument('--no-show', action='store_true', help='Não exibir gráfico (útil para CI/scripting)')

    args = parser.parse_args()

    media, acerto, dist = calcular_estatisticas(args.atk, args.mod_atk, args.defs, args.mod_def)

    print(f"--- {args.atk} vs {args.defs} with +{args.mod_atk}/+{args.mod_def} ---")
    print(f"Chance de Acerto: {acerto:.1f}%")
    print(f"Dano Médio (Geral): {media:.2f}")
    if acerto > 0:
        print(f"Dano Médio (Se acertar): {(media / (acerto/100)):.2f}")

    dano_medio_acerto = (media / (acerto/100)) if acerto > 0 else 0
    gerar_histograma(
        dist,
        f'Distribuição de Dano: 1d{args.atk}+{args.mod_atk} vs 1d{args.defs}+{args.mod_def}',
        chance_acerto=acerto,
        dano_medio=media,
        dano_medio_acerto=dano_medio_acerto
    )

    if not args.no_show:
        plt.show()


if __name__ == '__main__':
    main()

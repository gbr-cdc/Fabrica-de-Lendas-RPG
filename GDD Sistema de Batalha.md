# GDD: Sistema de RPG Fábrica de Lendas
**Versão:** 1.0 (Draft Mecânico)
**Autor:** Gabriel

---

## 1. Visão Geral do Sistema
* **Objetivo:** Criar um sistema de RPG focado em histórias de alta fantasia, com a estética e a energia de cenários de anime shonen. O sistema prioriza a simplicidade e a versatilidade, utilizando um combate que se comporta mecanicamente de forma inspirada em jogos eletrônicos. Ele é projetado para representar toda a jornada de desenvolvimento de um personagem, desde um aventureiro comum até se tornar uma lenda que se aproxima do nível das divindades.
* **Pilares de Design:**
  * **Simplicidade e Fluidez:** Para que o combate transmita uma sensação imersiva e tática, o sistema roda de maneira fluida, sem regras truncadas, longas paradas de dados ou cálculos complicados. Na parte interpretativa, o foco é a liberdade, oferecendo uma estrutura simples para a resolução de conflitos. A criação de personagem permite ao jogador personalizar sua fantasia por meio de um sistema modular, separando estritamente as mecânicas de combate das mecânicas de interpretação, garantindo que não haja concorrência de recursos entre esses dois pilares.
  * **Gameficação do Combate:** O sistema trata o combate de uma forma abertamente gameficada, em vez de ter foco cinematográfico ou narrativo. O foco é duplo: deve ser divertido "combar" e montar a build do personagem, e deve ser divertido jogar o combate na mesa. Fica a cargo dos jogadores e do mestre dar o teor narrativo e o sabor da cena sobre essa base mecânica. 
  * **Personalização:** Tendo em vista que a ideia é criar um sistema genérico focado em cenários de alta fantasia e anime, ele precisa dar uma grande liberdade para a criação de conceitos de personagem. Ele o faz através de uma abordagem modular onde o jogador pode comprar características e pacotes de habilidades separadas, ao invés de comprar classes definidas.
  * **Sistema de Batalha Ativo:** Uma das ideias que originou esse sistema foi a tentativa de trabalhar com um sistema de turnos com passagem ativa de tempo, onde a ação de cada personagem aconteça em um número definido de "ticks", de forma que seja possível um personagem ter vantagem nos turnos e agir mais vezes. Isto tem inspiração em jogos que usam o ATB (Active Time Battle) como os Final Fantasy antigos e o Chrono Trigger. Isso leva à economia de ações que é explicada na seção 3.

---

## 2. Atributos Base
O Fábrica de Lendas utiliza três atributos principais que buscam englobar três arquétipos clássicos de personagens em histórias fantásticas: os personagens fortes e resistentes (**Físico**), os personagens rápidos e habilidosos (**Habilidade**) e personagens conjuradores, que focam em magias ou poderes especiais (**Mente**).

* **Físico (FIS):** Representa a força e a resistência do personagem, o quanto ele é fisicamente desenvolvido.
  * **Impacto mecânico:** Define os PV (Pontos de Vida) máximos.
* **Habilidade (HAB):** Representa a agilidade e destreza do personagem, sua velocidade e a precisão de seus golpes.
  * **Impacto mecânico:** Define o **Custo de Ação Base** (velocidade na linha do tempo).
* **Mente (MEN):** Representa a disciplina, capacidade de concentração e força espiritual do personagem.
  * **Impacto mecânico:** Define o teto de Mana e a capacidade de geração de Foco/Mana por turno (conceitos explicados na seção 5).
  
> **Nota de Design:** Estes três arquétipos de personagem — o rápido, o forte e o conjurador — são bastante genéricos, de maneira que não é tão claro determinar em qual deles um dado personagem da ficção se encaixa, mas é uma tríade muito comum em jogos — o tank, o dps e o mago — e aqui serve como base para orientar as fantasias de personagem. Eu reduzi o número de atributos para apenas três, agrupando alguns conceitos que normalmente são separados, como Força e Constituição em Físico, e Destreza e Agilidade em Habilidade. O caso de Mente é especial: esse atributo seria o equivalente a Inteligência e Sabedoria. A questão é que eu não quero que atributos relacionados ao combate disputem recursos com atributos relacionados à interpretação. Então, Mente aqui diz mais respeito à capacidade de seu personagem usar habilidades especiais e magias. Quanto à precisão de ataque e dano, o atributo utilizado para calcular os bônus depende do atributo principal do personagem. 

---

## 3. O Motor de Tempo (A Linha do Tempo)

O controle de turnos no Fábrica de Lendas se comporta de maneira diferente. Não existe uma noção de rodadas; o tempo flui de maneira contínua em unidades chamadas "ticks" e as ações dos personagens custam um certo número de ticks. A maneira como isso é feito é através das seguintes regras:

1. No início do combate, anote um contador com o custo de ação de cada personagem. O personagem com menor custo age primeiro. Em caso de empate, o conflito é resolvido no dado uma vez para o resto do combate.

2. Existem duas ações básicas: uma ação de ataque e uma ação de movimento. O custo de uma ação de ataque é o valor de custo de ação determinado pela Habilidade do personagem. O valor de uma ação de movimento é metade deste custo. Movimento inclui se movimentar, tomar poções e usar itens. 

3. Após um personagem agir, some o custo daquela ação ao contador daquele personagem. O próximo personagem a agir será aquele que tiver o menor custo acumulado.

***/TO DO/***
- [ ] Como fazer esse controle de turnos à mão pode ser complicado, eu quero criar uma representação gráfica utilizando um círculo com 60 segmentos, similar a um relógio, para marcar a posição de cada personagem na ordem de turnos e usar um ponteiro para marcar a passagem de tempo.
- [ ] Outra possibilidade é fazer um aplicativo online que faz esse controle de turnos automaticamente.

### Tabela de Custo de Ações

| Atributo | Custo | Diff 1 | Diff 2 | Diff 3 | Diff 4 | Diff 5 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | 60 | - | - | - | - | - |
| 1 | 50 | 5 | - | - | - | - |
| 2 | 40 | 4 | 2 | - | - | - |
| 3 | 36 | 9 | 2,57 | 1,5 | x | - |
| 4 | 32 | 8 | 4 | 1,78 | 1,14 | - |
| 5 | 28 | 7 | 3,5 | 2,33 | 1,27 | 0,88 |
| 6 | 25 | 8,33 | 3,57 | 2,27 | 1,67 | 1 |
| 7 | 22 | 7,33 | 3,67 | 2,2 | 1,57 | 1,22 |
| 8 | 20 | 10 | 4 | 2,5 | 1,67 | 1,25 |
| 9 | 18 | 9 | 4,5 | 2,57 | 1,8 | 1,29 |
| 10 | 16 | 8 | 5 | 2,6 | 1,78 | 1,33 |

---

As colunas Diff X desta tabela mostram a quantidade de ataques necessária antes de conseguir um ataque bônus contra um inimigo com X pontos de Habilidade a menos que você. Repare que números quebrados, na prática, são arredondados para cima; se você precisa de 2,57 ataques para ganhar um ataque na frente do oponente, vai precisar de três. Apesar disso, esses "quebrados" contam ao longo do combate se ele durar o suficiente.

> ***Nota de Design:*** Eu demorei dias brigando com números e tabelas do Excel para chegar até os valores desta tabela. Eu usei o motor de testes automatizados presente nesse projeto para testar e, ao que tudo indica, estes valores funcionam. Repare que os atributos 0 e 1 neste RPG são usados para personagens fracos, por isso os números relativos a eles são diferentes. A sacada que eu tive para balancear a progressão foi focar nos "breakpoints", momentos onde a vantagem de velocidade é efetiva e o personagem passa a ter, por exemplo, de 1 ataque bônus a cada 4 ataques para um ataque bônus a cada 3 ataques. E uma concessão que tive que fazer para esses números funcionarem na prática é que a diferença de 1 ponto de atributo, em geral, não é significativa. Assim, a diferença de dois pontos faz com que o personagem ganhe um ataque bônus a aproximadamente 4 ataques; a diferença de três ganha 1 ataque bônus a cada dois ataques; e a partir da diferença de quatro, a vantagem é de 1 ataque bônus a cada 2 ataques. Isso aproximadamente, os "quebrados" também se acumulam. Então, como a diferença de ataques de HAB 5 para 3 é 1/2,33, supondo que o personagem de HAB 5 seja o P1 e o outro o P2, a sequência de ações pelo relógio de turnos ficaria: P1 - P2 - P1 - P2 - P1 - **P1** - P2 - P1 - P2 - P1 - **P1**. Ou seja, P1 ganha um ataque extra em três ataques e dois ataques extras em cinco. Agir mais vezes é uma vantagem muito forte se considerarmos que a economia de ações dita o ritmo do jogo. Para equilibrar isso, ações de movimento têm um custo separado. Isso serve para aliviar a vantagem de personagens rápidos de atacarem e se moverem mais rápido, atrasando o ritmo de ataques do personagem se ele quiser se reposicionar (na minha ideia original esses números definiam a ordem de turnos, de maneira que o personagem ganhava um turno bônus ao invés de uma ação de ataque bônus). O custo de movimentar é metade do custo de um ataque, de maneira que ele também diminui à medida que a habilidade do personagem aumenta. A única coisa que incomoda é que os números usados para a progressão parecem aleatórios à primeira vista; não são uma sequência mais intuitiva como de 1 em 1, 5 em 5 ou 10 em 10. Isto é porque a matemática envolvida no balanceamento dessa progressão, por ser uma curva decrescente e pelos "breakpoints" que mencionei, é bastante complexa e os números são muito sensíveis. Variar um ponto em qualquer um desses valores atrapalha a curva inteira.

## 4. Resolução de Combate
*A matemática por trás de um ataque.*

***/TO DO/***
- [ ] Escrever

---

## 5. Economia de Recursos
*Como os personagens pagam por suas habilidades.*

***/TO DO/***
- [ ] Escrever
---

## 6. Estilos de Combate
*A definição dos estilos de combate.*
***/TO DO/***
- [ ] Escrever

---

## 7. Equipamentos e Status
*Como os itens e condições modificam a matemática base.*

***/TO DO/***
- [ ] Escrever
---

## 8. Filosofia de Balanceamento
*Uma nota sobre como o jogo foi testado (excelente para o portfólio).*

***/TO DO/***
- [ ] Escrever

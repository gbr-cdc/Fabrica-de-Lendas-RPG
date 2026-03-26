# GDD: Sistema de RPG Fábrica de Lendas
**Versão:** 1.0 (Draft Mecânico)
**Autor:** Gabriel

---

## 1. Visão Geral do Sistema
* **Objetivo:** Criar um sistema de RPG focado em histórias de alta fantasia, com a estética e a energia de cenários de anime shonen. O sistema prioriza a simplicidade e a versatilidade, utilizando um combate que se comporta mecanicamente de forma inspirada em jogos eletrônicos. Ele é projetado para representar toda a jornada de desenvolvimento de um personagem, desde um aventureiro comum até se tornar uma lenda que se aproxima do nível das divindades.
* **Pilares de Design:**
  * **Simplicidade e Fluidez:** Para que o combate transmita uma sensação imersiva e tática, o sistema roda de maneira fluida, sem regras truncadas, longas paradas de dados ou cálculos complicados. Na parte interpretativa, a prioridade é a liberdade, oferecendo uma estrutura simples para a resolução de conflitos. A criação de personagem permite ao jogador personalizar sua fantasia por meio de um sistema modular, separando estritamente as mecânicas de combate das mecânicas de interpretação, garantindo que não haja concorrência de recursos entre esses dois pilares.
  * **Gameficação do Combate:** O sistema trata o combate de uma forma abertamente gameficada, em vez de ter foco cinematográfico ou narrativo. Os objetivos principais são: deve ser divertido "combar" e montar a build do personagem, e deve ser divertido jogar o combate na mesa. Fica a cargo dos jogadores e do mestre dar o teor narrativo e o sabor da cena sobre essa base mecânica. 
  * **Personalização:** Tendo em vista que a ideia é criar um sistema genérico focado em cenários de alta fantasia e anime, ele precisa dar uma grande liberdade para a criação de conceitos de personagem. Ele o faz através de uma abordagem modular onde o jogador pode comprar características e pacotes de habilidades separadas, ao invés de comprar classes definidas.
  * **Sistema de Batalha Ativo:** Uma das ideias que originou esse RPG foi a tentativa de trabalhar com um sistema de turnos com passagem ativa de tempo, onde a ação de cada personagem aconteça em um número definido de "ticks", de forma que seja possível um personagem ter vantagem nos turnos e agir mais vezes. Isto tem inspiração em jogos que usam o ATB (Active Time Battle) como os Final Fantasy antigos e o Chrono Trigger. Esta abordagem leva à economia de ações que é explicada na seção 3.

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

> ***Nota de Design:*** Eu demorei dias brigando com números e tabelas do Excel para chegar até os valores desta tabela. Eu usei o motor de testes automatizados presente nesse projeto para testar e, ao que tudo indica, estes valores funcionam. Repare que os atributos 0 e 1 neste RPG são usados para personagens fracos, por isso os números relativos a eles são diferentes. A sacada que eu tive para balancear a progressão foi focar nos "breakpoints", momentos onde a vantagem de velocidade é efetiva e o personagem passa a ter, por exemplo, de 1 ataque bônus a cada 4 ataques para 1 ataque bônus a cada 3 ataques. E uma concessão que tive que fazer para esses números funcionarem na prática é que a diferença de 1 ponto de atributo, em geral, não é significativa. Assim, a diferença de dois pontos faz com que o personagem ganhe um ataque bônus a aproximadamente 4 ataques; a diferença de três ganha 1 ataque bônus a cada dois ataques; e a partir da diferença de quatro pontos, a vantagem é de 1 ataque bônus a cada 2 ataques. Isso aproximadamente, os "quebrados" também se acumulam. Então, como os ataques bônus ganhos de HAB 5 para 2 são 1 por 2,33 ataques, supondo que o personagem de HAB 5 seja o P1 e o outro o P2, a sequência de ações pelo relógio de turnos ficaria: P1 - P2 - P1 - P2 - P1 - **P1** - P2 - P1 - P2 - P1 - **P1**. Ou seja, P1 ganha um ataque extra em três ataques e dois ataques extras em cinco. Agir mais vezes é uma vantagem muito forte se considerarmos que a economia de ações dita o ritmo do jogo. Para equilibrar isso, ações de movimento têm um custo separado. Isso serve para aliviar a vantagem de personagens focados em HAB de atacarem e se moverem mais rápido, atrasando o ritmo de ataques do personagem se ele quiser se reposicionar (na minha ideia original esses números definiam a ordem de turnos, de maneira que o personagem ganhava um turno bônus ao invés de uma ação de ataque bônus). O custo de movimentar é metade do custo de um ataque, de maneira que ele também diminui à medida que a habilidade do personagem aumenta. A única coisa que me incomoda é que os números usados para a progressão parecem aleatórios à primeira vista; não são uma sequência mais intuitiva como de 1 em 1, 5 em 5 ou 10 em 10. Isto é porque a matemática envolvida no balanceamento dessa progressão, por ser uma curva decrescente e pelos "breakpoints" que mencionei, é bastante complexa e os números são muito sensíveis. Variar um ponto em qualquer um desses valores atrapalha a curva inteira.

## 4. Resolução de Combate

* Ataque = Bônus de Rank + Dado de Ataque + Modificadores
* Defesa = Bônus de Rank + Dado de Defesa + Modificadores
* Grau de Acerto (GdA) = Ataque - Defesa
* Se GdA > 0, então o ataque acertou.
* Dano = Poder de Ataque (PdA) + (GdA * Multiplicador de Ataque (MdA))
* Poder de Ataque: Dano Base da Arma + Atributo Principal
* Multiplicador de Ataque: Definido pela arma, 1 por padrão.
* Atributo Principal: Definido pelo Estilo de Combate (explicado na seção 6).
* O Dado de Ataque e o Dado de Defesa também são definidos pelo Estilo de Combate.
* Bônus de Rank cresce com o nível do personagem.
* Bônus de Precisão/Guarda: Mecânica presente em itens e habilidades. Um bônus de Precisão +1 permite que um ataque acerte com GdA 0, Precisão +2 acerta com GdA -1, e assim por diante. Nestes casos, no cálculo de dano, o GdA é considerado 0. O bônus de Guarda +1 faz com que um ataque com GdA 1 erre, GdA 2 para Guarda +2, e assim segue.

> **Nota de Design:** Eu comecei esse sistema pensando em baseá-lo no d10 e usar jogadas resistidas (1d10 vs 1d10) para definir acerto e dano. Eu então adicionei um valor base na fórmula de dano e a ideia de um multiplicador para conseguir ajustar a variabilidade. Normalmente, se jogarmos um d10 contra um d10, temos uma situação onde o dano médio é 1.65 e o dano máximo é 9, o que dificulta certos balanceamentos. Com a minha fórmula, eu reduzo consideravelmente a diferença entre o dano médio e o dano máximo. Depois veio a ideia de variar os dados de acordo com os Estilos de Combate (que definem como o personagem luta e fazem parte da composição da "classe" do personagem). Isso me ajudou a criar identidades diferentes para estilos diferentes e me ajudou a balancear personagens de HAB, que têm a vantagem de serem mais rápidos (uma vantagem muito forte, já que a economia de ações rege este tipo de jogo). Mas, ao trabalhar com dados menores, eu subestimei o impacto que bônus como +1 ou +2 teriam nas jogadas. Uma diferença de um bônus +1 no ataque é suficiente para levar a taxa de vitória entre personagens iguais de 50/50 para 66/34; com um bônus +2 a diferença chega a 80/20, o que eu considero desequilibrado para uma diferença tão pequena. Eu cogitei usar apenas o d20 para jogadas de ataque, mas em um teste resistido a variabilidade do d20 torna-se muito grande, com a diferença entre os dados podendo ir de 1 a 19. Eu poderia ajustar isso com a minha fórmula de dano, mas senti que usar um d20 também alteraria a identidade do sistema que eu estava criando. Então, eu mantive os dados variando entre 1d8 e 1d12 e defini como regra que os valores dessas rolagens não devem ser alterados, a menos que sejam bônus instantâneos que se aplicam em apenas um ataque. Mas isso fez com que eu perdesse as interações de adicionar bônus permanentes na hora de criar habilidades de personagens e itens. Por isso, criei a mecânica de bônus de Precisão e bônus de Guarda, que giram em torno do GdA, que é um valor central nas minhas interações de combate. Estas mecânicas ainda precisam ser implementadas e testadas no meu motor de testes. Por último, o Bônus de Rank é uma esseção à regra, pois serve para diferenciar personagens mais poderosos de personagens mais fracos. Como os dados de ataque e defesa não mudam, sem o Bônus de Rank um personagem nivel 1 teria a mesma chance de acertar outro personagem nivel 1 e um personagem nível 20.

---

## 5. Economia de Recursos
Existem dois recursos de combate especiais no Fábrica de Lendas: Mana e Foco.

* **Mana:**
  * Personagens possuem um valor máximo de Mana definido pelo seu valor de MEN.
  * Para usar magias é preciso primeiro manifestar a Mana necessária.
  * **Manifestar Mana:** Ação que gera uma quantidade de Mana igual ao valor de MEN do personagem. Se, ao realizar essa ação, o personagem possuir mana o suficiente para usar uma magia, ele pode fazê-lo. Se não, ele precisa aguardar seu próximo turno para gerar mais mana. Esta ação tem o custo de uma ação padrão, independentemente de uma magia ter sido utilizada ou não.
  * Se o personagem receber dano, ele precisa fazer um teste de MEN com dificuldade igual a 5 + o atributo principal da fonte de dano para não perder a mana manifestada. Se a fonte de dano não for um personagem, o mestre estipula a dificuldade.

* **Foco:** 
  * Foco é gerado quando o personagem ataca. Alternativamente, ele pode gastar uma ação de movimento para gerar o seu valor de Foco.
  * O valor gerado é igual a MEN e o máximo que pode ser acumulado é igual a 3 * MEN.
  * Foco é usado para ativar habilidades do personagem.

* **Especial:** Para personagens com um Estilo de Combate marcial que ganhem acesso a magias, é possível gastar uma ação de movimento para transformar seu Foco em Mana. 

> **Notas de Design:** Com magos precisando manifestar a mana antes de usar suas magias e correndo o risco de perder essa mana ao tomar dano, a minha intenção é fazer com que eles funcionem a partir de uma mecânica de risco e recompensa. Se eles conseguirem ficar seguros, conseguem dar muito dano. Por outro lado, se os inimigos os alcançarem, eles ficam em perigo. Isso faz com que atrapalhar a concentração dos conjuradores do oponente enquanto protege a concentração de seus aliados seja um objetivo tático importante. Entretanto, nem o dano das magias nem o tempo necessário para usá-las deve ser tão alto assim para que o combate não gire só em torno disso. Um mago vai precisar de dois turnos (um juntando mana e outro completando a mana e usando a magia) para usar uma magia de seu nível, e três turnos para usar uma magia mais forte. Quatro turnos seria para tentar usar uma magia muito avançada para o seu nível. O dano deve ser o suficiente para machucar, mas não para virar o rumo da batalha, a menos que seja uma magia de nível muito alto. Eu estou revendo minhas tabelas de dano, mas a base que eu estava usando em quantidade de ataques para derrubar um alvo, também conhecido como TTK (Time to Kill), seria 5 acertos para golpes normais e 3 acertos para magias. Além disso, nada impede que através de habilidades e magias específicas um mago consiga entrar no calor da batalha. 
> 
> Quanto ao Foco, é a mana dos guerreiros. A vantagem do Foco é que ele pode ser gerado enquanto se ataca, diferente dos magos que precisam ficar parados. Por outro lado, habilidades são menos poderosas do que magias. Isso gera uma dualidade: guerreiros querem ficar no calor do combate, onde conseguem atacar constantemente, e magos querem ficar seguros enquanto carregam suas magias. Quanto a converter Foco em Mana, isso é para personagens híbridos. Existe um Estilo de Combate chamado Conjurador, que é para quem quer usar magia. Mas personagens que não pegaram esse estilo ainda podem ter acesso a magias através de Especializações. Entretanto, estes personagens não vão ter MEN como atributo principal, o que quer dizer que o Foco gerado vai ser menor, e eles não vão ter as habilidades de um Conjurador, que auxiliam bastante no uso de magias. Além de tudo, eles precisam gastar uma ação de movimento. Desta forma, não acho que a conversão seja desequilibrada. Outro ponto sobre esse sistema de recursos é que ele também é focado no gerenciamento. Guardar alguns pontos de Mana/Foco para um momento crítico, assim como para usar magias/habilidades de reação, faz parte da estratégia.

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

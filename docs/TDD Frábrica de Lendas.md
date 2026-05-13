# TDD: Frábrica de Lendas: Implementação do motor
**Autor:** Shino

## Prefácio

Quando eu comecei a criar o sistema de RPG Fábrica de Lendas, muitas dúvidas e dificuldades surgiram com relação ao balanceamento do jogo. Questões sobre como criar a curva de progressão de PV, curva de dano das armas de acordo com os tiers, se tal habilidade deveria dar um bônus de +1 ou +2 no ataque, e a famosa pergunda: "como eu sei se isso está quebrado ou não?". Muitas destas perguntas eu consegui responder estudando design de jogos, entendendo conceitos como "economia de ação" e "TTK(Tunr to Kill) e usando meus conhecimentos de estatística e probabilidade. Mas balanceamento de sistemas de jogos é uma terefa inerentemente complexa, e mesmo que eu esteja começando a entender as diretrizes básicas, continua sendo bastante complicado. Então, eu criei um script em python para simular batalhas, de maneira que eu pudesse fazer dois personagens se infrentarem dezenas de centenas de vezes e analisar a taxa de vitória de cada um. Dessa forma, eu teria uma linha base para determinar se o núcleo do combate do sistema funciona, se os atributos e suas tabelas de progressão estão ok e se uma determinada habilidade está muito forte ou não. Mas, para testar as habilidades de personagem, eu precisava implementá-las no script. À medida que eu fui adicionando elementos e regras, um script em um único arquivo se tornou um projeto inteiro de implementação de um motor de combate de turnos ao ponto que, embora a versão atual implemente o meu sistema de RPG, a organização arquitetural do projeto é robusta e modularizada o suficiente para que o motor possa ser utilizado em qualquer RPG de turnos, como Pokemon, Final Fantasy, etc... Com isso resolvi expandir o escopo desse projeto para o desenvolvimento de um jogo completo que use o meu sistema de RPG como base. Este arquivo serve como a documentação da implementação dos módulos do jogo, começando pelo módulo de batalha.

## Padrões de Projeto Core

**Game-MVC:** 
  Eu me basiei no no famoso padrão de projeto MVC para criar uma versão de separação de responsabilidades na implementação de jogos. Basicamente, eu chamo de *Model*(Modelo) tudo aquilo que representa o mundo do jogo e suas regras. Então modelo aqui vai para alemém de modelo de dados, para também representar regras e comportamentos. O meu `BattleManager` por exemplo, que reune a lógica de execução de uma batalha, é parte do modelo. Eu chamo de *Controller*(Controle) tudo aquilo que instancia e manuseia *modelos*. Quem instancia um `BattleManager`, manda ele executar a batalha e captura o retorno para passar para a visualização é um controle. A *View*(Visualização), assim como no MVC padrão, é responsável por exibir os estados do modelo na tela.

  Isso nos garante uma implementação que é altamente desaclopada e assim facilita a manutenção, reusabilidade e expansão do projeto. O módulo de batalha pode funcionar de maneira completamente independente da visualização e sem nem mesmo conhecer o resto do jogo, se preocupando apenas com o que é referente ao seu contexto. Podemos exibir o jogo de diversas formas diferentes apenas mudando a implementação da visualização e separar regras de negócio do jogo (como, quando e de que forma uma batalha é iniciada) dos elementos que o formam (o que é uma batalha e como ela acontece).

  Um detalhe importante é que essa aplicação do MVC se encaixa perfeitamente em jogos baseados em turnos, uma vez que, neste contexto, as mudanças de estado do modelo são sempre pontuais e discretas. Em interações de tempo real, as atualizações constantes saturariam a comunicação entre o Modelo e a Visualização. Além disso, a estrutura orientada a objetos do MVC faz com que os dados fiquem fragmentados na memória, prejudicando a localidade de cache da CPU. Para contornar esses gargalos em jogos de tempo real, o modelo arquitetural padrão adotado pela indústria é o *ECS (Entity-Component-System)*.

**Command Pattern:**
 Comandos do jogo, como ações de ataque, uso de magias e itens, são implementados utilizando o padrão de projeto Command. Nesse padrão, as funções que representam as ações são encapsuladas em objetos através de uma classe base que expõe o método de interface executar(). Dessa forma, o motor do jogo é capaz de invocar e resolver uma ação de forma totalmente agnóstica, sem precisar conhecer a lógica interna ou os detalhes do que está sendo feito. Isso aumenta drasticamente a modularização do sistema e facilita a comunicação desacoplada entre os controladores de personagens e o modelo de batalha.

 Uma adição importante à minha implementação foi a introdução dos métodos `can_execute()` e `execute_if_possible()`. O `can_execute()` implementa a lógica responsável por verificar se uma ação é válida e pode ser resolvida em um determinado contexto — uma ação de ataque, por exemplo, verifica se o alvo ainda está vivo. Já o `execute_if_possible()` atua como um método *wrapper*, acionando o `can_execute()` para validar o estado antes de invocar o `execute()` de fato. Essa estrutura é fundamental para garantir a robustez do sistema e prevenir erros decorrentes de mudanças de estado entre a escolha e a resolução da ação.

 **Observer Pattern**

Os efeitos de habilidades ativas, passivas e de estados alterados (como "envenenado") são implementados através do padrão de projeto *Observer*. O `BattleManager`, atuando como núcleo central do combate, possui um *Event Bus* integrado. A `AttackAction` (Comando de Ataque) utiliza o método `BattleManager.emit()` para disparar sinais em instantes específicos da sua resolução. As funções ouvintes (*listeners*) recebem um objeto de contexto chamado `AttackLoad`, que contém a lista de parâmetros do ataque atual. Esse objeto é mutável e compartilhado, o que permite que funções específicas interceptem e alterem a resolução do ataque em tempo real.

A cadeia de resolução de ataques reconhece os seguintes sinais (gatilhos):

*   `on_turn_start`: Início do turno do personagem (Emitido pelo `BattleManager`).
*   `on_roll_modify`: Gatilho para modificadores sobre as rolagens de ataque e defesa.
*   `on_defense_reaction`: Gatilho para reações defensivas (pode transformar um acerto em um erro).
*   `on_hit_check`: Gatilho para efeitos que dependem da confirmação de acerto/erro.
*   `on_gda_modify`: Gatilho para habilidades que alteram a GdA (Grau de Acerto), conceito nativo do *Fábrica de Lendas*.
*   `on_damage_calculation`: Gatilho para habilidades que atuam no cálculo de dano.
*   `on_damage_taken`: Último gatilho para interceptação antes de o dano final ser descontado dos Pontos de Vida do alvo.
*   `on_attack_end`: Fim do fluxo de ataque.
*   `on_turn_end`: Fim do turno do personagem (Emitido pelo `BattleManager`).
*   `on_character_death`: Gatilho disparado quando os Pontos de Vida de um personagem chegam a zero.

Esta arquitetura evita a duplicação da lógica de resolução para diferentes habilidades ofensivas. Em vez de *hardcodar* regras, novas habilidades são criadas apenas atrelando funções de efeito (*hooks*) ao *Event Bus* durante a resolução de uma `AttackAction`. Com isso, o desenvolvimento se torna altamente **desacoplado** e **orientado a dados**, permitindo que as habilidades sejam totalmente customizadas através de um arquivo de configuração `.json`. O gerenciador de batalha inspeciona a existência desses *hooks* na ação através da função `BattleAction.get_hooks()`.

O ciclo de vida de passivas e de efeitos de estado (*status*) segue o mesmo princípio central, diferindo apenas no momento de registro no *Event Bus*. Habilidades passivas são validadas e registradas no início do combate, durando até a derrota do personagem (e sendo **reprocessadas** caso ele retorne à batalha). Já os estados temporários (como "envenenado") instanciam e atrelam seus próprios *hooks* de forma dinâmica através do método `BattleManager.add_status_effect()`.
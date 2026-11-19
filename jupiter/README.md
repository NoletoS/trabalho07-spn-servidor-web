# Trabalho 07 no Jupiter Analytics

Os modelos descrevem um servidor web com fila limitada. O repositório contém os 14 experimentos E1–E4 e as estimativas produzidas pelo motor oficial do Jupiter Analytics.

- `modelos/` contém 14 redes importáveis no Jupiter com **File → Import (Local)**.
- `cenarios.csv` contém a taxa de chegada `lambda`, o número de processadores `c`, o limite de espera `B` e a taxa de serviço por processador `mu`.
- `simulacoes/` guarda cada requisição feita ao motor e a resposta integral, com métricas e intervalos.
- `resultados.csv` reúne as médias de vazão, resposta, espera, ocupação, descarte e processamento. Taxas em req/s, tempos em ms, ocupação e descarte em porcentagem.
- `intervalos.csv` detalha intervalos de confiança de 95% e o número de réplicas.

## Reprodução

1. Abra o Jupiter Analytics, versão 1.17.0. Importe `modelos/E2b.json` para demonstrar a referência. Use `modelos/E2c.json` para comparar três processadores.
2. Para repetir todos os experimentos com a API local oficial, execute `python executar_jupiter.py` nesta pasta, com o Jupiter ativo em localhost.
3. Execute `python consolidar.py` para ler as respostas e gerar os CSVs.

Os parâmetros de execução ficam nos JSONs de `simulacoes/`. A chegada usa a média `1 / LAMBDA` segundos, e o serviço de cada processador usa `1 / MU` segundos. O lugar Fonte tem um token e um autolaço na transição de chegada. Ele mantém um relógio de chegada ativo inclusive quando a capacidade se esgota. As tentativas que encontram o sistema cheio são direcionadas à transição de descarte.


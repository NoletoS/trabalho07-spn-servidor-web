# Desempenho de um servidor web com fila limitada

Modelo de rede de Petri estocástica generalizada com chegadas Poisson, serviço exponencial em paralelo e limite de admissão. Os números são a avaliação estacionária de um cenário hipotético, calculada em Jupyter Notebook 7.6.5.

## Arquivos

- modelo_spn.ipynb: notebook executado, com a tabela e a seleção por metas.
- avaliar.py: regras de disparo, enumeração de marcações, balanço e cálculo das métricas.
- cenarios.csv: 14 configurações E1–E4. As colunas lambda e mu são taxas em requisições por segundo.
- resultados.csv: seis métricas por cenário. Tempos em milissegundos, utilização e descarte em porcentagem.
- estacionario.csv: probabilidade estacionária pi para cada marcação tangível.
- graficos.py e diagrama.py: geração dos gráficos, da tabela LaTeX e do diagrama. Dependem de Pillow.

Para reproduzir em Jupyter, mantenha o notebook junto de avaliar.py e cenarios.csv na mesma pasta e execute todas as células. A avaliação também pode ser executada com `python avaliar.py`. Para gerar as figuras e a tabela, execute `python graficos.py` e `python diagrama.py`. Os arquivos visuais são escritos na pasta vizinha overleaf/figuras.

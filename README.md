# CNPJ - full
Utilitário em Python para carregar a base completa de CNPJ disponibilizada pela Receita Federal (aprox. 85 GB!) e transformá-la em arquivos csv ou sqlite para fácil consumo. Processa dados de empresas, sócios e CNAEs.

## Como executar
`python cnpj.py <arquivo original> <tipo de saída:csv ou sqlite> <pasta saída>`

### Exemplo
`python cnpj.py "data\F.K032001K.D81106D" sqlite "data"`

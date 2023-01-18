# Projeto de WebScrapping: Star Jeans

### Disclaimer
Todo contexto de negócio envolvendo este projeto é fictício.<br>
Este desenvolvimento foi inspirado no curso "Python do DS ao Dev" e contou com o apoio da [Comunidade DS](https://www.comunidadedatascience.com/).

## 1. Negócio

Dois sócios estão planejando entrar no mercado de moda dos USA como um modelo de negócio do tipo E-commerce.
A ideia inicial é entrar no mercado com apenas um produto e para um público específico, no caso o produto seria calças Jenas para o público masculino. O objetivo é manter o custo de operação baixo e escalar a medida que forem conseguindo clientes.

Porém, mesmo com o produto de entrada e a audiência definidos, os dois sócios não tem experiência nesse mercado de moda e portanto não sabem definir coisas básicas como preço, o tipo de calça e o material para a fabricação de cada peça.

As principais concorrentes da empresa Start Jeans são as americadas H&M e Macys.

### 1.1. Questões de negócio

A partir das principais dores desses dois sócios, podemos identificar duas principais:

1. Qual o melhor preço de venda para as calças?
2. Quantos tipos de calças e suas cores para o produto inicial?
3. Quais as matérias-prima necessárias para confeccionar as calças?

### 1.2. Fonte de dados

A fonte de dados a ser extraídas como parâmetro para essas decisões vem de dois e-commerces:

1. H&M: https://www2.hm.com/en_us/men/products/jeans.html
2. Macys: https://www.macys.com/shop/mens-clothing/mens-jeans

As principais informações a serem extraídas tiveram como escopo fechado:

1. Produto
2. Preço
3. Tempo
4. Localidade
5. Atributo do produto

## 2. Planejamento da Solução

### 2.1 Produto Final
O que será entregue?

- A mediana dos valores dos produtos do site dos concorrentes em tabela ou gráfico.

### 2.2 Ferramentas

- Python 3.8.3
- Bibliotecas de Webscrapping ( BS4, Selenium )
- LunarVim
- Jupyter Notebook ( Análise e prototipagens )
- Cronjob

### 2.3 Processo (Passo a passo)

1. Passo a passso para construir o cálculo da mediana ou média
	- Realizar o calculo da mediana sobre o produto, tipo e cor
2. Definir o formato da entrega ( Visualização, Tabela, Frase )
	- Gráfico de barras com a mediana dos preço dos produtos, por tipo e cor dos últimos 30 dia- Tabela com as seguintes colunas: id | product_name | product_type | product_color | produ- Definição do schema: Colunas e seu tipo
	- Definição a infraestrutura de armazenamento ( SQLITE3 )
	- Design do ETL ( Scripts de Extração, Transformação e Carga )
	- Planejamento de Agendamento dos scripts ( dependencias entre os scripts )
	- Fazer as visualizações
	- Entrega do produto final
3. Decidir o local de entrega ( PowerBi, Telegram, Email, Streamlit, Intranet )
	- Tabela em formato CSV
	- E-mail com resposta das perguntas dos sócios.

## 3. Resultado da Extração

Foram extraídos 282 registros e 14 variáveis apenas do site da H&M via BeautifulSoup4.

Desta forma, a tabela gerada teve a seguinte estrutura.

| Name_Feature | Description |
| ----------- | --------- |
| product_id | Identificador único do estilo da calça jeans + Identificador da cor |
| style_id | Identificador único do estilo da calça jeans. |
| color_id | Identificador da cor. |
| product_name | Nome do modelo da calça. |
| product_color | Cor da calça. |
| fit | Tipo de modelo da calça. |
| product_price | Preço da calça. |
| cotton | Porcentagem de cotton na composição da calça. |
| polyester | Porcentagem de polyester na composição da calça. |
| elastomultiester | Porcentagem de elastomultiester na composição da calça. |
| spandex | Porcentagem de spandex na composição da calça. |
| scrapy_datetime  | Horário que foi realizado o scrapy no site. |

## 4. Resultados da Análise

| attributes | min | max | range | media | mediana | std | skew | kurtosis |
| ----------- | --------- | ----------- | --------- | ----------- | --------- | ----------- | --------- | --------- |
| product_price | 7.99 | 49.99 | 42.00 | 10.241720 | 26.809149 | 22.99 | 0.707784 | -0.363797 |
| cotton | 0.77 | 1.00 | 0.23 | 0.060639 | 0.968723 | 0.99 | -2.527530 | 4.933861 |
| polyester | 0.00 | 1.00 | 1.00 | 0.341348 | 0.291738 | 0.00 | 0.543038 | -1.359736 |
| elastomultiester | 0.00 | 0.09 | 0.09 | 0.019333 | 0.004574 | 0.00 | 4.025848 | 14.373866 |
| spandex | 0.00 | 0.02 | 0.02 | 0.006611 | 0.012128 | 0.01 | -0.263802 | -0.761313 |

### 4.1 Qual o melhor preço de venda para as calças?

- De acordo com o resultado apresentado acima, a mediana do preço das calças jeans indica que o melhor preço da venda para as calças é de $ 26,80

### 4.2 Quantos tipos de calças e suas cores para o produto inicial?

- Os três tipos de calça mais recomendados são: skinny_fit, regular_fit e slim_fit
- As cores recomendadas são: light_denim_blue, black, denim_blue

### 4.3 Quais as matérias-prima necessárias para confeccionar as calças?

- As principais confecções exigem no mínimo as quatro matérias:
  - Cotton
  - Polyester
  - Elastomultiester
  - Spandex

## 5. Conclusão

O objetivo do projeto foi alcançado com sucesso para que os dois sócios possam tomar suas decisões para definir seu produto e a sua precificação para que possam inaugurar seu e-commerce.

## 6. Próximos Passos

Complementar o webscrapy do site da Macys e aprimorar a entrega com o Streamlit para que os sócios tenham uma melhor visibilidade de seus dados para melhor tomada de decisão.

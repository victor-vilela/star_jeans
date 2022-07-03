# ============ IMPORTS ============
import requests
import re
import os
import sqlite3
import logging
import pandas   as pd
import numpy    as np

from bs4        import BeautifulSoup
from datetime   import datetime
from sqlalchemy import create_engine

# ============ DATA COLLECTIONS ======================
def data_collection(url, headers):
# Request to URL
    page = requests.get( url, headers=headers)

# Beautiful Soup Object
    soup = BeautifulSoup(page.text, 'html.parser')

# ==================== Product Data ====================
    products = soup.find('ul',class_='products-listing small')

    products_list = products.find_all('article', class_='hm-product-item')

# product_id
    product_id = [p.get('data-articlecode') for p in products_list]

# product_category
    product_category = [p.get('data-category') for p in products_list]

# product_name
    product_name = [p.find('a',class_='link').get_text() for p in products_list]

# product_price
    product_price = [p.find('span',class_='price regular').get_text() for p in products_list]

    data = pd.DataFrame([product_id, product_name, product_category, product_price]).T
    data.columns = ['product_id', 'product_name', 'product_category', 'product_price']

# scrapy datetime
    data['scrapy_datetime'] = datetime.now().strftime(' %Y-%m-%d %H:%M:%S ')

    return data

# método para criar a lista de composition
def define_lista_composition(lista_composition):
    composition = []
    for p in lista_composition:
        lista = list(filter(None, p.get_text().split('\n')))
        if 'messages.' in lista[0]:
            # identifica a posicao do character para pegar o nome da coluna
            res = [idx for idx, chr in enumerate(lista[0]) if chr.isupper()]
            lista[0] = lista[0][res[0]:]
        composition.append(lista)
    return composition

# ========================== DATA COLLECTIONS BY PRODUCT =====================================
def data_collection_by_product(data, headers):

# Empty DataFrame
    df_compositions = pd.DataFrame()

# unique columns for all products
    aux = []

    cols = ['Art. No.', 'Care instructions', 'Composition', 'Concept', 'Description', 'Fit', 'Imported',
     'Length', 'Material', 'More sustainable materials', 'Nice to know', 'Rise', 'Size', 'Style']

    df_pattern = pd.DataFrame(columns=cols)

    for i in range(len(data)):

        # API Requests
        url_id = 'https://www2.hm.com/en_us/productpage.' + data.loc[i, 'product_id'] + '.html'
        logger.debug('Product: %s', url_id)

        page_id = requests.get( url_id, headers=headers)

        # Beautiful Soap Object
        soup_id = BeautifulSoup( page_id.text, 'html.parser' )

        # =============== color name =================
        products_list_color = soup_id.find_all('a', class_='filter-option miniature active') + soup_id.find_all('a', class_='filter-option miniature')
        product_color = [p.get('data-color') for p in products_list_color]

        # product id
        id_product = [p.get('data-articlecode') for p in products_list_color]

        df_color = pd.DataFrame([id_product,product_color]).T
        df_color.columns = ['product_id','product_color']
        
        for j in range(len(df_color)):
            
            url_id_color = 'https://www2.hm.com/en_us/productpage.' + df_color.loc[j, 'product_id'] + '.html'
            logger.debug('Color: %s', url_id_color)

            page_id_color = requests.get( url_id_color, headers=headers)

            # Beautiful Soap Object
            soup_id_color = BeautifulSoup( page_id_color.text, 'html.parser' )
            
            # product_name
            product_name = soup_id_color.find('h1').get_text()
            
            # product_price
            product_price = soup_id_color.find('span', class_='price-value').get_text()
            product_price = re.findall( r'\d+\.?\d+', product_price)[0]
            
            #products_list_composition
            products_list_composition = soup_id_color.find_all('div', class_='details-attributes-list-item')

            # build list composition
            product_composition = define_lista_composition(products_list_composition)

            # rename dataframe
            df_composition = pd.DataFrame(product_composition).T
            df_composition.columns = df_composition.iloc[0]

            # delete first row
            df_composition = df_composition.iloc[1:].fillna(method='ffill')

            # Remove pocket lining, shell and lining
            df_composition['Composition'] = df_composition['Composition'].str.replace('Pocket lining: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].str.replace('Pocket: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].str.replace('Shell: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].str.replace('Lining: ', '', regex=True)

            # garantee the same number of columns
            df_composition = pd.concat([df_pattern, df_composition], axis=0)

            # rename columns
            df_composition.columns = ['product_id', 'care_instructions', 'composition', 'concept', 'description', 'fit', 'imported', 
                                      'length', 'material', 'sustainable_materials', 'nice_to_know', 'rise', 'size', 'style']
            df_composition['product_name'] = product_name
            df_composition['product_price'] = product_price

            # unique columns for all products
            aux = aux + df_composition.columns.tolist()

            # merge df_color + df_composition
            df_composition = pd.merge(df_composition, df_color, how='left', on='product_id')
            #data_sku = data_sku[~data_sku.duplicated()]

            # all products
            df_compositions = pd.concat([df_compositions, df_composition], axis=0)
           
    # Join Showroom data + details
    df_compositions['style_id'] = df_compositions['product_id'].apply(lambda x: x[:-3])
    df_compositions['color_id'] = df_compositions['product_id'].apply(lambda x: x[-3:])
        
    # scrapy datetime
    df_compositions['scrapy_datetime'] = datetime.now().strftime(' %Y-%m-%d %H:%M:%S ')
    
    return df_compositions


#  ======================== DATA CLEANING =========================
def data_cleaning(data_product):

# product id
    df_data = data_product.dropna( subset=['product_id'] )

# product name
    df_data['product_name'] = df_data['product_name'].apply( lambda x: x.replace( ' ','_' ).lower() )

# product price
    df_data['product_price'] = df_data['product_price'].astype( float )
                       
# color name
    df_data['product_color'] = df_data['product_color'].apply( lambda x: x.replace( ' ', '_' ).lower() if pd.notnull( x ) else x )

# fit
    df_data['fit'] = df_data['fit'].apply( lambda x: x.replace( ' ', '_' ).lower() if pd.notnull( x ) else x )

# size number
    df_data['size_number'] = df_data['size'].apply( lambda x: re.search( '\d{2}\.\d', x ).group(0) if pd.notnull( x ) else x )

# size model
    df_data['size_model'] = df_data['size'].str.extract( '\(Size (.*?)\)' )

# =========== composition ===========

# break composition by comma
    df1 = df_data['composition'].str.split( ',', expand=True ).reset_index(drop=True)

# cotton | polyester | Elastomultiester | Spandex 
    df_ref = pd.DataFrame( index=np.arange( len( data ) ), columns=['cotton','polyester', 'elastomultiester', 'spandex'] )

# ------------- cotton
    df_cotton_0 = df1.loc[df1[0].str.contains('Cotton', na=True), 0]
    df_cotton_0.name = 'cotton'

    df_cotton_1 = df1.loc[df1[1].str.contains('Cotton', na=True), 1]
    df_cotton_1.name = 'cotton'

# combine cotton
    df_cotton = df_cotton_0.combine_first(df_cotton_1)

    df_ref = pd.concat( [df_ref, df_cotton ], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last')]

# ------------- polyester
    df_polyester_0 = df1.loc[df1[0].str.contains('Polyester', na=True), 0]
    df_polyester_0.name = 'polyester'

    df_polyester_1 = df1.loc[df1[1].str.contains('Polyester', na=True), 1]
    df_polyester_1.name = 'polyester'

# combine polyester
    df_polyester = df_polyester_0.combine_first(df_polyester_1)

    df_ref = pd.concat( [df_ref, df_polyester], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last') ]

# elastomultiester
    df_elastomultiester = df1.loc[df1[1].str.contains('Elastomultiester', na=True), 1]
    df_elastomultiester.name = 'elastomultiester'

    df_ref = pd.concat( [df_ref, df_elastomultiester], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last') ]

# ------------- spandex
    df_spandex_0 = df1.loc[df1[1].str.contains('Spandex', na=True), 1]
    df_spandex_0.name = 'spandex'

    df_spandex_1 = df1.loc[df1[2].str.contains('Spandex', na=True), 2]
    df_spandex_1.name = 'spandex'

# combine spandex
    df_spandex = df_spandex_0.combine_first(df_spandex_1)

    df_ref = pd.concat( [df_ref, df_spandex], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last') ]

# join of combine with product_id
    df_aux = pd.concat( [df_data['product_id'].reset_index(drop=True), df_ref], axis=1 )

# format composition data
    df_aux['cotton'] = df_aux['cotton'].apply( lambda x: int( re.search( '\d+', x ).group(0) ) / 100 if pd.notnull( x ) else x )
    df_aux['polyester'] = df_aux['polyester'].apply( lambda x: int( re.search( '\d+', x).group(0) ) / 100 if pd.notnull( x ) else x )
    df_aux['elastomultiester'] = df_aux['elastomultiester'].apply( lambda x: int( re.search( '\d+', x ).group(0) ) / 100 if pd.notnull( x ) else x )
    df_aux['spandex'] = df_aux['spandex'].apply( lambda x: int( re.search( '\d+', x ).group(0) ) / 100 if pd.notnull( x ) else x )

# final join
    df_aux = df_aux.groupby( 'product_id' ).max().reset_index().fillna(0)
    df_data = pd.merge( df_data, df_aux, on='product_id', how='left' )

# drop columns
    df_data = df_data.drop( columns=['size', 'composition','imported', 'length', 'material', 'care_instructions', 'concept',
                                     'description', 'sustainable_materials', 'nice_to_know', 'rise', 'style'], axis=1 )

# drop duplicates
    df_data = df_data.groupby( 'product_id' ).max().reset_index().fillna(np.nan)
    df_data = df_data.drop_duplicates()

    return df_data

# =========== DATA INSERT ================
def data_insert(df_data):

    data_insert = df_data[[
        'product_id',
        'style_id',
        'color_id',
        'product_name',
        'product_color',
        'fit',
        'product_price',
        'size_number',
        'size_model',
        'cotton',
        'polyester',
        'elastomultiester',
        'spandex',
        'scrapy_datetime'
    ]]

# create database connection
    conn = create_engine( 'sqlite:///database_hm.sqlite', echo=False )

# data insert
    data_insert.to_sql( 'vitrine', con=conn, if_exists='append', index=False )


if __name__ == "__main__":
    
    # Logging
    path = '/home/vvilela/repos/python_ds_dev/'
    
    if not os.path.exists( path + 'logs' ):
        os.makedirs( path + 'logs' )
    
    logging.basicConfig(
        filename = path + 'logs/webscrapgin_hm.log',
        level = logging.DEBUG,
        format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger('webscrapgin_hm')
    

    # ===== parameters and constants =====

    # header
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    # URL
    url = 'https://www2.hm.com/en_us/men/products/jeans.html'
    
    # data colletion
    data = data_collection( url, headers )
    logging.info('data collection done')

    # data colletion by product
    data_product = data_collection_by_product(data, headers)
    logging.info('data collection by product done')
    
    # data cleaning
    data_product_cleaned = data_cleaning(data_product)
    logging.info('data cleaning done')

    # data insertion
    data_insert(data_product_cleaned)
    logging.info('data insertion done')


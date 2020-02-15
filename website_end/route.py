import os
import sys
import re
import numpy as np
import pandas as pd
import sqlite3
import datetime

from bokeh.embed import components
from bokeh.models import ColumnDataSource, Legend, LegendItem
from bokeh.palettes import Spectral11
from bokeh.plotting import figure, output_file, show

from flask import render_template, url_for, redirect, request
from website_end import app

def get_brands():
    cleared_data = []
    with sqlite3.connect(r'./website_end/database.db') as conn:
        c = conn.cursor()
        c.execute("SELECT DISTINCT brand FROM product_information where brand <> 'None'")
        for i in c.fetchall():
            cleared_data.append(*i)
        return cleared_data

def get_models(brand):
    if brand is None:
        return ['']
    else:
        cleared_data = []
        with sqlite3.connect(r'./website_end/database.db') as conn:
            c = conn.cursor()
            c.execute(f'SELECT model FROM product_information where brand = "{brand}"')
            db_data = c.fetchall()
            for i in db_data:
                cleared_data.append(*i)
            cleared_data.sort()
            cleared_data.insert(0, "")
            return cleared_data

def clear_models_list(models):
    n_models = []
    for model in models:
        if model != '' and model is not None:
            n_models.append(model)
    return n_models

def get_records(models):
    with sqlite3.connect('./website_end/database.db') as conn:
        c = conn.cursor()
        if len(models) == 1:
            c.execute(f"SELECT p.model, r.date_of_scrap, r.price FROM records r INNER JOIN product_information p \
                        ON r.title =  p.product_title where p.model in ('{models[0]}')")
        else:
            c.execute(f"SELECT p.model, r.date_of_scrap, r.price FROM records r INNER JOIN product_information p \
                        ON r.title =  p.product_title where p.model in {tuple(models)}")

        return c.fetchall()

def get_site_items_list():
    full_list = []
    only_profiles = []
    with sqlite3.connect('./website_end/database.db') as conn:
        c = conn.cursor()
        c.execute(f"SELECT * FROM sites_items")

        for item in c.fetchall():
            full_list.append(list(item))
            only_profiles.append(item[0])
        only_profiles.insert(0, "")
        return full_list, only_profiles

def add_new_site_item(items):
    with sqlite3.connect('./website_end/database.db') as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO sites_items VALUES(?,?,?,?,?)", tuple(items))
        except:
            print('blad inserta', file=sys.stderr)
            return 'value_already_there'
    conn.commit()

def get_models_from_site_list(item_list):
    cleared_data = []
    models = []
    with sqlite3.connect('./website_end/database.db') as conn:
        c = conn.cursor()

        c.execute(f"SELECT item_1_id, item_2_id, item_3_id, item_4_id FROM sites_items WHERE profiles_name = '{item_list}' ")
        for i in c.fetchall()[0]:
            models.append(i)
        c.execute(f"SELECT brand, model FROM product_information where model in {tuple(models)}")
        for i in c.fetchall():
            cleared_data.append([(*i)])
        for i in range(0, 4-len(cleared_data)):
            cleared_data.append([None, None])

        return cleared_data

 
def convert_to_pandas(records, models):
    df = pd.DataFrame.from_records(data = records, columns = ['model', 'date', 'price']).drop_duplicates()
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = df['price'].str.replace('$', '')
    df['price'].astype('float')

    date_series = []
    for i in range(0, (df.max()[1] - df.min()[1]).days):
        date_series.append((df.min()[1] + datetime.timedelta(days=i)).date())

    models_prices=[]
    for i, model in enumerate(models):
        models_prices.append([])
        for date in date_series:
            if not df[df['date']==date][df['model']==model].empty:
                models_prices[i].append(float((df[df['date']==date][df['model']==model].values[0][2])))
            else:
                models_prices[i].append(np.nan)
    return date_series, models_prices, models

def create_graph(date_series, records_data, models):
    numlines = len(models)
    time_array=[]
    for _ in range(0, numlines):
        time_array.append(date_series)
    mypalette=Spectral11[0:len(models)]
        
    p = figure(width=1000, height=400, x_axis_type="datetime")     
    r = p.multi_line(
        xs=time_array,
        ys=records_data,
        line_color=mypalette,
        line_width=5)

    if models[0] != ',':
        legend_items = []
        for i, item in enumerate(models):
            legend_items.append(LegendItem(label=item, renderers=[r], index=i))

        legend = Legend(items=legend_items)
        p.add_layout(legend)
    return p

def save_to_temp(items):
    with sqlite3.connect('./website_end/database.db') as conn:
        c = conn.cursor()
        try:
            c.execute(f"""
                UPDATE sites_items 
                SET item_1_id = '{items[0]}',
                item_2_id = '{items[1]}',
                item_3_id = '{items[2]}',
                item_4_id = '{items[3]}'
                WHERE profiles_name = 'temp'
                """)
            conn.commit()
        except:
            print('blad update', file=sys.stderr)
    conn.commit()

def get_temp_profile():
    temp_profiles = []
    with sqlite3.connect('./website_end/database.db') as conn:
        c = conn.cursor()
        c.execute(f"SELECT item_1_id, item_2_id, item_3_id, item_4_id FROM sites_items WHERE profiles_name = 'temp' ")
        for i in c.fetchall()[0]:
            temp_profiles.append(i)
        return temp_profiles

@app.route('/', methods=['GET', 'POST'])
def home():
    models = []
    set_brands = get_brands()
    full_site_items_list, set_site_items = get_site_items_list()
    get_site_items = request.form.get('site_item')
    saving_name = request.form.get('input_name')

    if get_site_items is None:
        get_brand_1, get_model_1 = request.form.get('dropdown-brand_1'), request.form.get('dropdown-model_1')
        set_models_1 = get_models(get_brand_1)  
        if get_model_1 not in set_models_1:
            get_model_1 = None 

        get_brand_2, get_model_2 = request.form.get('dropdown-brand_2'), request.form.get('dropdown-model_2')
        set_models_2 = get_models(get_brand_2) 
        if get_model_2 not in set_models_2:
            get_model_2 = None 

        get_brand_3, get_model_3 = request.form.get('dropdown-brand_3'), request.form.get('dropdown-model_3')
        set_models_3 = get_models(get_brand_3)  
        if get_model_3 not in set_models_3:
            get_model_3 = None 

        get_brand_4, get_model_4 = request.form.get('dropdown-brand_4'), request.form.get('dropdown-model_4')
        set_models_4 = get_models(get_brand_4) 
        if get_model_4 not in set_models_4:
            get_model_4 = None 
    else:
        site_data = get_models_from_site_list(get_site_items)
        get_brand_1, get_model_1 = site_data[0][0], site_data[0][1]
        set_models_1 = get_models(get_brand_1)  
        if get_model_1 not in set_models_1:
            get_model_1 = None 

        get_brand_2, get_model_2 = site_data[1][0], site_data[1][1]
        set_models_2 = get_models(get_brand_2) 
        if get_model_2 not in set_models_2:
            get_model_2 = None 

        get_brand_3, get_model_3 = site_data[2][0], site_data[2][1]
        set_models_3 = get_models(get_brand_3)  
        if get_model_3 not in set_models_3:
            get_model_3 = None 

        get_brand_4, get_model_4 = site_data[3][0], site_data[3][1]
        set_models_4 = get_models(get_brand_4) 
        if get_model_4 not in set_models_4:
            get_model_4 = None 

    models_set=[get_model_1,get_model_2,get_model_3,get_model_4]
    if models_set != [None, None, None, None]:
        save_to_temp(models_set)
    else:
        if saving_name != None and saving_name != 'temp':
            profiles = get_temp_profile()
            profiles.insert(0, saving_name)
            add_new_site_item(profiles)
        else:
            pass
    
    models.extend((get_model_1, get_model_2, get_model_3, get_model_4))
    models = clear_models_list(models) 
    if models:
        records = get_records(models)
        date_series, models_prices, models = convert_to_pandas(records, models)
        script_price_graph, div_price_graph = components(create_graph(date_series, models_prices, models))
    else:
        script_price_graph, div_price_graph = components(create_graph([1], [1], [',']))

    return render_template('home.html', set_brands=set_brands,
        get_brand_1=get_brand_1, get_model_1=get_model_1, set_models_1=set_models_1,
        get_brand_2=get_brand_2, get_model_2=get_model_2, set_models_2=set_models_2,
        get_brand_3=get_brand_3, get_model_3=get_model_3, set_models_3=set_models_3,
        get_brand_4=get_brand_4, get_model_4=get_model_4, set_models_4=set_models_4,
        div_price_graph=div_price_graph, script_price_graph=script_price_graph,
        get_site_items=get_site_items, set_site_items=set_site_items
        )
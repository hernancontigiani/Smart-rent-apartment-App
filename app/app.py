#!/usr/bin/env python
'''
Rent-Apartment-Search-Api
---------------------------
Autor: Hernan Contigiani
 
Descripcion:
One of the most tedious thing is looking for new apartment, one of the most 
popular web used in Argentina for this purpose is Mercadolibre
This Rest API make scrapping from Mercadolibre search to get the information
of thousands of apartments for rent, prince, location and make a intelligence analysis
to make something that could take as a week in a couple of seconds.
 
Usage: First run the Rest API Flask server:
python ./api.py

Then open your browser and enter this URL example:
http://127.0.0.1:5000/

What you will see?
After the program load all information of your zone, you will see all apartments for rent with differents colours based on the following analysis:

Green: Aparment rent price close to average price.
Yewllow: Aparment rent price bellow average price.
Red: Aparment rent price above average price.
Blue: Aparment rent price in dolars US$.

We could get the analysis from the group of aparments rent price with the following URL:
URL report:
http://127.0.0.1:5000/reporte

We could get the prediction about the relation between price and size based on Machine Learning Linear Regression algorithm:
URL prediction:
http://127.0.0.1:5000/prediccion

Needed:

- Python 3.6.x / 3.7.x
- Libraries
    pip install numpy
    pip install pandas
    pip install -U Flask
'''

__author__ = "Hernan Contigiani"
__email__ = "hernan4790@gmail.com"
__version__ = "2.0"

import os
import traceback

import pandas as pd
from flask import Flask, request, jsonify, render_template, Response, redirect, url_for, session

import meli
from analytics import preprocess, visualize, clustering, report

app = Flask(__name__)
app.secret_key = "flask_session_key_inventada"


@app.route("/")
def index():
    return redirect(url_for('map'))


@app.route("/map")
def map():
    try:
        city = request.args.get('city')
        if city is None or city == '':
            city = 'Capital Federal'
        else:
            city = str(city)

        return render_template('map.html', city=city)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route('/propiedades', methods=['POST']) # Your API endpoint URL would consist /predict
def propiedades():
    try:
        city = request.form.get('city')

        if city is None:
            city = 'Capital Federal'
        else:
            city = str(city)

        scrapper = meli.mercadolibreAPI()
        scrapper.set_debug(False)
        scrapper.search(meli.Inmueble(city))
        df = scrapper.df

        # Clasifico los alquileres según el precio de cada uno
        propiedades_pesos = df.loc[df['moneda'] == 'ARS']

        # Analizo la media y los alquilers que se encuentra a un 20% de ella
        q_low = propiedades_pesos["precio"].quantile(0.30)
        q_hi  = propiedades_pesos["precio"].quantile(0.70)

        red_marker = 'http://www.openstreetmap.org/openlayers/img/marker.png'
        blue_marker = 'http://www.openstreetmap.org/openlayers/img/marker-blue.png'
        gold_marker = 'http://www.openstreetmap.org/openlayers/img/marker-gold.png'
        green_marker = 'http://www.openstreetmap.org/openlayers/img/marker-green.png'

        # Marco que bandera o marca mostrar en cada caso
        df['marca'] = df.apply(lambda x: blue_marker if x['moneda'] == 'USD' else gold_marker if x['precio'] < q_low else red_marker if x['precio'] > q_hi else green_marker, axis=1 )

        
        result = df.to_json()

        # Dataset is to big for cookies (improve with mongoDB)
        df2 = preprocess(df)
        ip = request.remote_addr
        df2.to_csv(f'{ip}.csv')

        return(result)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return jsonify({'trace': traceback.format_exc()})


@app.route('/reporte') # Your API endpoint URL would consist /predict
def reporte():
    try:
        # Dataset is to big for cookies (improve with mongoDB)
        ip = request.remote_addr
        if os.path.exists(f'{ip}.csv') == False:
            return redirect(url_for('map'))

        df = pd.read_csv(f'{ip}.csv')
        output = report(df)
        return Response(output.getvalue(), mimetype='image/png')
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route('/ml', methods=['GET', 'POST']) # Your API endpoint URL would consist /predict
def ml():
    try:
        if request.method == 'GET':

            # Dataset is to big for cookies (improve with mongoDB)
            ip = request.remote_addr
            if os.path.exists(f'{ip}.csv') == False:
                return redirect(url_for('map'))
        
            df = pd.read_csv(f'{ip}.csv')
            propiedades_pesos = df.loc[df['moneda'] == 'ARS']
            encoded_img = visualize(propiedades_pesos)
            return render_template('ml.html', overview_graph=encoded_img)
        else:
            algorithm_type = request.form.get('clusterAlgorithm')
            clusters = int(request.form.get('clusters'))

            ip = request.remote_addr
            df = pd.read_csv(f'{ip}.csv')

            encoded_img = clustering(df, algorithm_type=algorithm_type, n_clusters=clusters)
            return Response(encoded_img, mimetype='image/png')
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/about")
def about():
    return redirect(url_for('/'))


if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line argument
    except:
        port = 5000 # Puerto default
        
    app.run(host='0.0.0.0', port=port, debug=True)
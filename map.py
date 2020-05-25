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
__version__ = "1.0.0"

import reporte as rp

from flask import Flask, request, jsonify, render_template, Response
import pandas as pd
import numpy as np
import traceback

import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
from sklearn import linear_model

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/propiedades') # Your API endpoint URL would consist /predict
def propiedades():
    try:
        df = pd.read_csv("propiedades.csv")

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
        return(result)
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route('/reporte') # Your API endpoint URL would consist /predict
def reporte():
    try:
        # Utilizo el programa de reporte para generar el gráfico y mostrarlo en la web
        fig = rp.generate(reporte=0, silent_mode=True)
        
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route('/prediccion') # Your API endpoint URL would consist /predict
def prediccion():
    try:
        # Utilizo el programa de reporte para generar el gráfico y mostrarlo en la web
        fig = rp.generate(reporte=5, silent_mode=True)

        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    except:
        return jsonify({'trace': traceback.format_exc()})


if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line argument
    except:
        port = 5000 # Puerto default
        
    app.run(host='0.0.0.0', port=port, debug=True)
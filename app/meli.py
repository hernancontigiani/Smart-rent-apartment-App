#!/usr/bin/env python
'''
SCRAPPING Alquieres con MERCADOLIBRE - API
---------------------------
Autor: Hernan Contigiani
Version: 2.0
 
Descripcion:
Bajada de datos desde mercadolibre, utilizando el acceso via API POST que proveen.
El proceso esta preparado para descargar elementos de la categoría Inmblues, filtrado por Departamentos y Alquiler
 
Se puede configurar modo DEBUG (set_debug(true)) para solo procesar los primeros elementos, esto
tambien activa el modo "verbose" con salida detallada
 
Requisitos de instalacion:
 
- Python 3.x
- Libreriras (incluye los comandos de instalacion)
    pip install numpy
    pip install pandas

Datos útiles de la API de MercadoLibre
ID de las distintas categorías existentes
    https://developers.mercadolibre.com.ar/es_ar/categorias-y-atributos

'''

__author__ = "Hernan Contigiani"
__email__ = "hernan4790@gmail.com"
__version__ = "2.0"

import time
import requests
import json
import re
from time import gmtime, strftime

import pandas as pd
pd.options.display.float_format = '{:.2f}'.format

import asyncio
import aiohttp
from aiohttp import ClientSession
 
class Inmueble():
    columnas = ['fecha', 'latitud', 'longitud', 'url', 'titulo', 'tipo_propiedad', 'precio', 'moneda', 'm2', 'ambientes']
    
    def __init__(self, ubicacion='Capital Federal'):
        #mercadolibre_id = 'MLA79242' # Locales
        #mercadolibre_id = 'MLA79243' # Alquiler
        self.mercadolibre_id = 'MLA1459' # Inmuebles
        self.ubicacion = ubicacion
 
    # Serializo de json a dataframe y rearmado de datos para que sea formato tabla
    def parse(self, json):
        data_list = []
        if 'results' in json:
            jslist = json['results']
            for js in jslist:
                try:
                    data = {}
                    data['fecha'] = strftime("%Y_%m_%d", gmtime())
                    data['mercadolibre_id'] = js['id']
                    data['latitud'] = js['location']['latitude']
                    data['longitud'] = js['location']['longitude']
                    data['url'] = js['permalink']
                    data['titulo'] = js['title']
                    data['precio'] = js['price']
                    data['moneda'] = js['currency_id']
                    data['tipo_propiedad'] = 'DESCONOCIDO'
                    data['m2'] = ''
                    data['ambientes'] = ''

                    for attr in js['attributes']:
                        if attr['id'] == 'PROPERTY_TYPE':
                            data['tipo_propiedad'] = attr['value_name']
                        if attr['id'] == 'TOTAL_AREA':
                            data['m2'] = attr['value_name'].split(' ')[0]
                        if attr['id'] == 'ROOMS':
                            data['ambientes'] = attr['value_name']

                    data_list.append(data)
                except:
                    pass

        return data_list

    def serialize(self, items):
        data = pd.DataFrame(items)
        data = data.groupby(['mercadolibre_id']).first().reset_index() # Elimina duplicados
        data = data.fillna('') # Los nulos los completamos con un string vacio       
        return data[self.columnas]


class mercadolibreAPI:
    debug = False

    def __init__(self):    
        self.query = None 
        self.objeto = None
        self.df = None
        self.meli_url = 'http://api.mercadolibre.com/sites/MLA/search?category='
        self.query_max_limit = 50
        self.query_max_offset = 1000
        self.__jsdata_async = []
 
    def set_debug(self, debug):
        self.debug = debug
        if(self.debug): print("Modo Debug ENCENDIDO")
 
    def request_get(self, url):
        if self.debug: print("Procesando url: ", url)
        try:
            return requests.get(url).json()
        except:
            return None

    async def request_get_async(self, url):
        if self.debug:
            print("Procesando url: ", url)
        try:
            async with aiohttp.ClientSession() as session2:
                async with session2.get(url) as response:
                    js = await response.json()                    
                    if js is not None:
                        data = self.objeto.parse(js)
                        self.__jsdata_async = self.__jsdata_async + data
        except Exception as e:
            print("request Excep", e)

    def search(self, objeto, pages_to_load=0):
        self.objeto = objeto
        jsdata = []
        parameters = '&q=Departamentos%20Alquiler%20' + re.sub("[ ,.]", "%20", self.objeto.ubicacion)
        url = self.meli_url + self.objeto.mercadolibre_id + parameters 
        print("Buscando: " + url)
        if(self.debug):
            paginators = 5
        
        paginators = round(self.request_get(url)['paging']['total'] / self.query_max_limit) + 1

        if pages_to_load > 0 and pages_to_load < paginators:
            paginators = pages_to_load

        jsdata = asyncio.run(self.get_data(parameters, paginators))
        self.df = self.objeto.serialize(jsdata)

    async def get_data(self, parameters, paginators):
        self.__jsdata_async = []
        tasks = []
        count = 0
        for pag in range(0, paginators):
            offset = pag * self.query_max_limit
            if offset > self.query_max_offset:
                break
            url = self.meli_url + self.objeto.mercadolibre_id + parameters + f'&limit={self.query_max_limit}&offset={offset}'
            tasks.append(self.request_get_async(url))
            count += 1
            if count == 10:
                await asyncio.gather(*tasks)
                count = 0
                tasks = []
        if tasks:
            await asyncio.gather(*tasks)

        return self.__jsdata_async

    def export(self, tipo = 'csv'):
        if tipo.lower() == 'sql':
            self.export_sql()
        elif tipo.lower() == 'csv':
            self.export_csv()
        else:
            print("No existe el metodo de exportacion: " + tipo.lower())
    
    def export_sql(self):
        ## No implementado
        return None
 
    def export_csv(self):
        file_name = "propiedades2" + ".csv"
        
        with open(file_name,"w+") as file_name:
            if self.debug:
                print("Guardando archivo", file_name)
            self.df.to_csv(file_name, sep=",", decimal=".")

        
if __name__ == "__main__":
 
    meli = mercadolibreAPI()
    meli.set_debug(False)
    meli.search(Inmueble())
    meli.export()
    print("Fin")
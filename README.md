# Rent-Aparment-Search
One of the most tedious thing is looking for new aparment, one of the most popular web used in Argentina for this purpose is Mercadolibre\
This Rest API make scrapping from Mercadolibre search to get the information of thousands of apartments for rent, prince, location and make a intelligence analyisi to make something that could take as a week in a couple of seconds.

# Enviroment:
This API was made with Flask


# Launch API
Usage:
First run the Rest API Flask server:\
`python ./api.py`

Then open your browser and enter this URL example:\
http://127.0.0.1:5000/

# What you will see?
After the program load all information of your zone, you will see all apartments for rent with differents colours based on the following analysis:
- Green: Aparment rent price close to average price.
- Yewllow: Aparment rent price bellow average price.
- Red: Aparment rent price above average price.
- Blue: Aparment rent price in dolars US$.

![Inove banner](/images/map.png)

- We could get the analysis from the group of aparments rent price with the following URL:

__URL report__\
http://127.0.0.1:5000/reporte

![Inove banner](/images/reporte.png)

- We could get the prediction about the relation between price and size based on Machine Learning Linear Regression algorithm:

__URL prediction__\
http://127.0.0.1:5000/prediccion

![Inove banner](/images/prediccion.png)

# Thanks!

Feel free to contact me by mail _hernan4790@gmail.com_ for any doubt..

Enjoy :smile:!!

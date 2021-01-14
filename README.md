# Rent-Apartment-Search
One of the most tedious thing is looking for new aparment, one of the most popular web used in Argentina for this purpose is Mercadolibre.\
This Rest API make scrapping from Mercadolibre search to get the information of thousands of apartments for rent, prince, location and make a intelligence analysis to make something that could take as a week in a couple of seconds.

# Enviroment:
This API was made with Flask


# Launch API
Usage:
First run the Rest API Flask server:
```
cd ./app
python app.py
```

Then open your browser and enter this URL example:\
http://127.0.0.1:5000/


# What you will see?
After the program load all information of your zone, you will see all apartments for rent with differents colours based on the following analysis:
- Green: Apartment rent price close to average price.
- Yewllow: Apartment rent price bellow average price.
- Red: Apartment rent price above average price.
- Blue: Apartment rent price in dollars US$.

By default it's loaded Capital Federal aparments, but you could look for other places:\
![map](/images/map.png)

- You could get the analysis from the group of apartments by click on "Report" tab:\
![reporte](/images/reporte.png)

- You could get the prediction about the relation between price and size based on Machine Learning Linear Regression algorithm and Clustering algorthms by click on "Machine Learning":\
![ml1](/images/machine_learning1.png)\\
![ml2](/images/machine_learning2.png)

# Docker
If you have Docker install you could build and start the app with the following commands:
```
docker build -t python-rent-app .
docker run --rm -d -p 5000:5000 python-rent-app
```
Or use docker-compose
```
docker-compose build
docker-compose up
```

# Thanks!
Feel free to contact me by mail _hernan4790@gmail.com_ for any doubt..\
Enjoy :smile:!!

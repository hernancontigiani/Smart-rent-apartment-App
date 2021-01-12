import io
import base64

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')   # For multi thread, non-interactive backend (avoid run in main loop)
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import cluster, mixture 
from sklearn import linear_model


__author__ = "Hernan Contigiani"
__email__ = "hernan4790@gmail.com"
__version__ = "2.0"


class ClusterAlgorithm():
    __factory_registry = {}  # Registered subclasses
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__factory_registry[cls.__name__] = cls  # Add class to registry

    @classmethod
    def create(cls, class_name):
        '''Factory create method'''
        subclass = cls.__factory_registry.get(class_name)
        if subclass:
            return subclass
        else:
            raise ValueError(class_name)

    def __init__(self, algorithm, n_clusters):
        self.n_clusters = n_clusters
        self.algorithm = algorithm

    def fit(self, x):
        self.algorithm.fit(x)

    def predict(self, x):
        if hasattr(self.algorithm, 'labels_'):
            labels = self.algorithm.labels_.astype(int)
        else:
            labels = self.algorithm.predict(x)
        return labels


class Birch(ClusterAlgorithm):
    def __init__(self, n_clusters):        
        algorithm = cluster.Birch(n_clusters=n_clusters)
        super().__init__(algorithm, n_clusters)


class KMeans(ClusterAlgorithm):
    def __init__(self, n_clusters):
        algorithm = cluster.KMeans(init="k-means++", n_clusters=n_clusters)
        super().__init__(algorithm, n_clusters)


class Gaussian(ClusterAlgorithm):
    def __init__(self, n_clusters):
        algorithm = mixture.GaussianMixture(n_components=n_clusters, covariance_type='spherical')
        super().__init__(algorithm, n_clusters)


class Spectral(ClusterAlgorithm):
    def __init__(self, n_clusters):
        algorithm = cluster.SpectralClustering(n_clusters=n_clusters, eigen_solver='arpack', affinity="nearest_neighbors")
        super().__init__(algorithm, n_clusters)


def preprocess(df):
    df2 = df.copy()
    df2 = df2.reset_index()
    df2.dropna(subset=['m2'], inplace=True)
    df2.dropna(subset=['ambientes'], inplace=True)
    df2 = df[df['moneda'] == 'ARS']
    df2["m2"] = pd.to_numeric(df2["m2"])
    df2["ambientes"] = pd.to_numeric(df2["ambientes"])
    q_low = df2['m2'].quantile(0.05)
    q_hi  = df2['m2'].quantile(0.95)
    df2 = df2[(df2['m2'] > q_low) & (df2['m2'] < q_hi)]
    return df2


def graph(X, y, labels=None, lines=None):
    fig = plt.figure()
    ax = fig.add_subplot()
    sns.set_style("whitegrid", {'grid.linestyle': '--'})
    if labels is None:
        sns.scatterplot(x=X[:, 0], y=y, color='b', label='precio vs m2', ax=ax)
    else:
        sns.scatterplot(x=X[:, 0], y=y, hue=labels, ax=ax)

    if lines:
        for line in lines:
            m, b = line
            lx = np.array([X.min(), X.max()])
            ly = lx * m + b
            ax.plot(lx, ly)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    encoded_img = base64.encodebytes(output.getvalue())
    plt.close(fig)  # Cerramos la imagen para que no consuma memoria del sistema
    return encoded_img


def visualize(df):
    X = df[['m2']].values
    y = df['precio'].values
    return graph(X, y)

def clustering(df, algorithm_type, n_clusters):
    X = df[['m2']].values
    y = df['precio'].values

    X_clustering = np.zeros(shape=(X.shape[0], 2))
    X_clustering[:, 0] = X[:, 0]
    X_clustering[:, 1] = y

    algorithm = ClusterAlgorithm.create(algorithm_type)(n_clusters)
    algorithm.fit(X_clustering)
    labels = algorithm.predict(X_clustering)

    lines = []
    for cluster in np.unique(labels):
        X_train, y_train = X[labels == cluster], y[labels == cluster]

        lr = linear_model.LinearRegression()
        lr.fit(X_train, y_train)
        lines.append((lr.coef_, lr.intercept_))

    return graph(X, y, labels, lines)


def report(df):
    # Sacamos todas las filas de la tabla las cuales el campo "m2" o "ambientes" se encuentre vacio
    propiedades = df[df['m2'].notna()]
    propiedades = propiedades[propiedades['ambientes'].notna()]

    # Nos quedamos solamente con aquellas filas que el precio haya sido informado en pesos Argentinos
    propiedades = propiedades.loc[propiedades['moneda'] == 'ARS']
   
    # Obtener cuantos alquileres por ambientes hay
    ambientes = propiedades.groupby('ambientes')['ambientes'].count()
    ambientes_df = ambientes.reset_index(name='cantidad')

    # Obtener el precio promedio por cantidad de ambientes
    precio_por_ambiente = propiedades.groupby('ambientes')['precio'].mean()/1000
    precio_por_ambiente_df = precio_por_ambiente.reset_index(name='precio')

    fig = plt.figure(figsize=(16,9))
    axs = np.empty(4, dtype=type(matplotlib.axes))
    
    sns.set_style("white")
    axs[0] = fig.add_subplot(221)
    axs[1] = fig.add_subplot(222)
    axs[2] = fig.add_subplot(223)
    axs[3] = fig.add_subplot(224)

    # Graficar "Cantidad de alquileres por ambiente"
    ax = sns.barplot(x=ambientes_df['ambientes'], y=ambientes_df['cantidad'], ax=axs[0])
    ax.set_alpha(0.8)
    ax.set_title("Cantidad de alquileres por ambiente", fontsize=15)
    ax.set_ylabel("Cantidad", fontsize=12)
    ax.set_xlabel("Ambientes", fontsize=12)

    # Graficar "Precio por ambiente"
    ax = sns.barplot(x=precio_por_ambiente_df['ambientes'], y=precio_por_ambiente_df['precio'], palette="pastel", ax=axs[1])
    ax.set_alpha(0.8)
    ax.set_title("Precio por ambiente", fontsize=15)
    ax.set_ylabel("Precio[miles de pesos]", fontsize=12)

    # Graficar "Cantidad de alquileres por m2"
    ax = sns.distplot(propiedades['m2'], bins=40, kde=True, kde_kws={"color": "blue", "alpha":0.3, "linewidth": 1, "shade":True }, ax=axs[2])
    ax.set_title("Cantidad de alquileres por m2", fontsize=15, y=0.7, x = 0.5)
    ax.set_ylabel("Cantidad", fontsize=12)
    ax.set_xlabel('m2')

    # Graficar "Precio por m2"
    ax = sns.scatterplot(propiedades['m2'],propiedades['precio']/1000, ax=axs[3])
    ax.set_title("Precio por m2", fontsize=15, y=-0.01)
    ax.set_ylabel("Precio[miles de pesos]", fontsize=12)
    ax.set_xlabel('m2')

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)  # Cerramos la imagen para que no consuma memoria del sistema
    return output

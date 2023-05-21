from django.http import HttpResponse
from django.template import loader
from django import forms


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px


data = pd.read_csv(r'C:\Users\zakan\Documents\Dataviz_DVF_Python\mysite\valeursfoncieres-2022.txt', sep='|', decimal=',')
data2019 = pd.read_csv(r'C:\Users\zakan\Documents\Dataviz_DVF_Python\mysite\valeursfoncieres-2019.txt', sep='|', decimal=',')
data2021 = pd.read_csv(r'C:\Users\zakan\Documents\Dataviz_DVF_Python\mysite\valeursfoncieres-2021.txt', sep='|', decimal=',')

#Formatage
#Retraits de colonnes
data.drop('Identifiant de document', axis=1)
data.drop('Reference document', axis=1)
data.drop('1 Articles CGI', axis=1)
data.drop('2 Articles CGI', axis=1)
data.drop('3 Articles CGI', axis=1)
data.drop('4 Articles CGI', axis=1)
data.drop('5 Articles CGI', axis=1)
data.drop('Identifiant local', axis=1)

#Format des dates 
data['Date mutation'] = pd.to_datetime(data['Date mutation'])

#Format de l'alias lié à la Corse (2A/2B)
data['Code departement'] = data['Code departement'].astype(str).str.replace('2A','20').str.replace('2B','20').str.replace('971','97').str.replace('972','97').str.replace('973','97').str.replace('974','97').str.replace('976','97').astype(int)


def index(request):
    ListeVisualisations = ['VenteParJourFoncieremoins300', 'VenteDepartement10PlusVendeur', 'VenteDepartement10MoinsVendeur','CamembertRepartitionVenteDepartement']
    #VenteParJourFoncieremoins300 = nombre de vente sur l'année classé par date de vente dont la valeur fonciere est inférieure 30 000 000
    #VenteDepartement10PlusVendeur = top 10 des départements qui ont eu le plus de vente sur l'année
    #VenteDepartement10MoinsVendeur = top 10 des départements qui ont eu le moins de vente sur l'année
    #CamembertRepartitionVenteDepartement = camembert en % des départements en fonction de leur volume de vente
    template = loader.get_template("template0.html")
    #return HttpResponse("Hello, world. You're at the polls index.")
    
    data_dep = data.groupby(data['Code departement'])
    
    data_dep_size = data_dep.size()

    x_data = data_dep_size.index.tolist()  # Convertir les valeurs uniques de la colonne en liste
    y_data = data_dep_size.tolist()  # Convertir les tailles de groupe en liste

    fig=px.scatter(x_data, y_data)
    premier_plot=fig.to_html(full_html=False, default_height=700, default_width=700)
    context={'data':data, 'premier_plot':premier_plot}
    return HttpResponse(template.render(context, request))

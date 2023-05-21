from django.http import HttpResponse
from django.template import loader
from django import forms
from django.shortcuts import render
import json
import statsmodels.api as sm
import requests as rq
from unidecode import unidecode

import pandas as pd
import numpy as np
import plotly.express as px


data = pd.read_csv('valeursfoncieres-2022.txt', sep='|', decimal=',')
data2019 = pd.read_csv('valeursfoncieres-2019.txt', sep='|', decimal=',')
data2021 = pd.read_csv('valeursfoncieres-2021.txt', sep='|', decimal=',')
data2020 = pd.read_csv('valeursfoncieres-2020.txt', sep='|', decimal=',')

#Formatage des jeux de données
#Retraits de colonnes
data.drop('Identifiant de document', axis=1)
data.drop('Reference document', axis=1)
data.drop('1 Articles CGI', axis=1)
data.drop('2 Articles CGI', axis=1)
data.drop('3 Articles CGI', axis=1)
data.drop('4 Articles CGI', axis=1)
data.drop('5 Articles CGI', axis=1)
data.drop('Identifiant local', axis=1)

data2019.drop('Identifiant de document', axis=1)
data2019.drop('Reference document', axis=1)
data2019.drop('1 Articles CGI', axis=1)
data2019.drop('2 Articles CGI', axis=1)
data2019.drop('3 Articles CGI', axis=1)
data2019.drop('4 Articles CGI', axis=1)
data2019.drop('5 Articles CGI', axis=1)
data2019.drop('Identifiant local', axis=1)

data2020.drop('Identifiant de document', axis=1)
data2020.drop('Reference document', axis=1)
data2020.drop('1 Articles CGI', axis=1)
data2020.drop('2 Articles CGI', axis=1)
data2020.drop('3 Articles CGI', axis=1)
data2020.drop('4 Articles CGI', axis=1)
data2020.drop('5 Articles CGI', axis=1)
data2020.drop('Identifiant local', axis=1)

data2021.drop('Identifiant de document', axis=1)
data2021.drop('Reference document', axis=1)
data2021.drop('1 Articles CGI', axis=1)
data2021.drop('2 Articles CGI', axis=1)
data2021.drop('3 Articles CGI', axis=1)
data2021.drop('4 Articles CGI', axis=1)
data2021.drop('5 Articles CGI', axis=1)
data2021.drop('Identifiant local', axis=1)


#Format des dates 
data['Date mutation'] = pd.to_datetime(data['Date mutation'])
data2019['Date mutation'] = pd.to_datetime(data2019['Date mutation'])
data2020['Date mutation'] = pd.to_datetime(data2020['Date mutation'])
data2021['Date mutation'] = pd.to_datetime(data2021['Date mutation'])

def formatCodeCommune(codeCommune):
    codeCommune = str(codeCommune)
    if len(codeCommune) - 3 != 0:
        s = '0' * -(len(codeCommune) - 3)
        codeCommune = s + codeCommune
    return codeCommune

def formatCodeINSEE(codeINSEE):
    if len(str(codeINSEE)) > 5:
        codeINSEE = codeINSEE.replace('0', '', 1)
    return codeINSEE
    
#Format des codes département et des codes commune
data['Code departement'] = data['Code departement'].astype(str).apply(lambda x: '0'+x if len(x) == 1 else x) #pour avoir des codes département à deux/trois chiffres uniquement
data2019['Code departement'] = data2019['Code departement'].astype(str).apply(lambda x: '0'+x if len(x) == 1 else x)
data2020['Code departement'] = data2020['Code departement'].astype(str).apply(lambda x: '0'+x if len(x) == 1 else x)
data2021['Code departement'] = data2021['Code departement'].astype(str).apply(lambda x: '0'+x if len(x) == 1 else x)


data['Code commune'] = data['Code commune'].astype(str).apply(lambda x: formatCodeCommune(x))
data2019['Code commune'] = data2019['Code commune'].astype(str).apply(lambda x: formatCodeCommune(x))
data2020['Code commune'] = data2020['Code commune'].astype(str).apply(lambda x: formatCodeCommune(x))
data2021['Code commune'] = data2021['Code commune'].astype(str).apply(lambda x: formatCodeCommune(x))

data['Code INSEE'] = data['Code departement'] + data['Code commune']
data['Code INSEE'] = data['Code INSEE'].apply(lambda x: formatCodeINSEE(x))
data2019['Code INSEE'] = data2019['Code departement'] + data2019['Code commune']
data2019['Code INSEE'] = data2019['Code INSEE'].apply(lambda x: formatCodeINSEE(x))
data2020['Code INSEE'] = data2020['Code departement'] + data2020['Code commune']
data2020['Code INSEE'] = data2020['Code INSEE'].apply(lambda x: formatCodeINSEE(x))
data2021['Code INSEE'] = data2021['Code departement'] + data2021['Code commune']
data2021['Code INSEE'] = data2021['Code INSEE'].apply(lambda x: formatCodeINSEE(x))

#Ajout des descriptions de département et régions
departements = {
    "01": "Ain",
    "02": "Aisne",
    "03": "Allier",
    "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes",
    "06": "Alpes-Maritimes",
    "07": "Ardèche",
    "08": "Ardennes",
    "09": "Ariège",
    "10": "Aube",
    "11": "Aude",
    "12": "Aveyron",
    "13": "Bouches-du-Rhône",
    "14": "Calvados",
    "15": "Cantal",
    "16": "Charente",
    "17": "Charente-Maritime",
    "18": "Cher",
    "19": "Corrèze",
    "21": "Côte-d'Or",
    "22": "Côtes-d'Armor",
    "23": "Creuse",
    "24": "Dordogne",
    "25": "Doubs",
    "26": "Drôme",
    "27": "Eure",
    "28": "Eure-et-Loir",
    "29": "Finistère",
    "2A": "Corse-du-Sud",
    "2B": "Haute-Corse",
    "30": "Gard",
    "31": "Haute-Garonne",
    "32": "Gers",
    "33": "Gironde",
    "34": "Hérault",
    "35": "Ille-et-Vilaine",
    "36": "Indre",
    "37": "Indre-et-Loire",
    "38": "Isère",
    "39": "Jura",
    "40": "Landes",
    "41": "Loir-et-Cher",
    "42": "Loire",
    "43": "Haute-Loire",
    "44": "Loire-Atlantique",
    "45": "Loiret",
    "46": "Lot",
    "47": "Lot-et-Garonne",
    "48": "Lozère",
    "49": "Maine-et-Loire",
    "50": "Manche",
    "51": "Marne",
    "52": "Haute-Marne",
    "53": "Mayenne",
    "54": "Meurthe-et-Moselle",
    "55": "Meuse",
    "56": "Morbihan",
    "57": "Moselle",
    "58": "Nièvre",
    "59": "Nord",
    "60": "Oise",
    "61": "Orne",
    "62": "Pas-de-Calais",
    "63": "Puy-de-Dôme",
    "64": "Pyrénées-Atlantiques",
    "65": "Hautes-Pyrénées",
    "66": "Pyrénées-Orientales",
    "67": "Bas-Rhin",
    "68": "Haut-Rhin",
    "69": "Rhône",
    "70": "Haute-Saône",
    "71": "Saône-et-Loire",
    "72": "Sarthe",
    "73": "Savoie",
    "74": "Haute-Savoie",
    "75": "Paris",
    "76": "Seine-Maritime",
    "77": "Seine-et-Marne",
    "78": "Yvelines",
    "79": "Deux-Sèvres",
    "80": "Somme",
    "81": "Tarn",
    "82": "Tarn-et-Garonne",
    "83": "Var",
    "84": "Vaucluse",
    "85": "Vendée",
    "86": "Vienne",
    "87": "Haute-Vienne",
    "88": "Vosges",
    "89": "Yonne",
    "90": "Territoire de Belfort",
    "91": "Essonne",
    "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne",
    "95": "Val-d'Oise",
    "971": "Guadeloupe",
    "972": "Martinique",
    "973": "Guyane",
    "974": "La Réunion",
    "976": "Mayotte"
}

departements_par_region = {
    "Auvergne-Rhône-Alpes": ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"],
    "Bourgogne-Franche-Comté": ["21", "25", "39", "58", "70", "71", "89", "90"],
    "Bretagne": ["22", "29", "35", "56"],
    "Centre-Val de Loire": ["18", "28", "36", "37", "41", "45"],
    "Corse": ["2A", "2B"],
    "Grand Est": ["08", "10", "51", "52", "54", "55", "57", "67", "68", "88"],
    "Hauts-de-France": ["02", "59", "60", "62", "80"],
    "Île-de-France": ["75", "77", "78", "91", "92", "93", "94", "95"],
    "Normandie": ["14", "27", "50", "61", "76"],
    "Nouvelle-Aquitaine": ["16", "17", "19", "23", "24", "33", "40", "47", "64", "79", "86", "87"],
    "Occitanie": ["09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"],
    "Pays de la Loire": ["44", "49", "53", "72", "85"],
    "Provence-Alpes-Côte d'Azur": ["04", "05", "06", "13", "83", "84"],
    "Outre-Mer": ["971", "972", "973", "974", "976"]
}

#Fonctions utilitaires pour les cartes

def getMapDataURL_Departement(codeDep):
    nomDep = departements.get(codeDep)
    nomDepFormate = unidecode(nomDep.lower())
    nomDepFormate = nomDepFormate.replace(' ', '-')
    return nomDep, f'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements/{codeDep}-{nomDepFormate}/communes-{codeDep}-{nomDepFormate}.geojson'

def getCentreDepartement(codeINSEE):
    response = rq.get(f'https://geo.api.gouv.fr/communes/{codeINSEE}?fields=centre&format=json&geometry=centre')
    if response.status_code == 200:
        donnees = response.json()
        centre = donnees.get('centre', {}).get('coordinates', [48.89832425138175, 2.2356448513901768])
        return centre
    else: 
        return [48.89832425138175, 2.2356448513901768]

def index(request):
    ListeVisualisations = ['VenteParJourFoncieremoins300','ValeurFonciereParMois' , 'ValeurFonciereMedianeIDF' , 'VenteDepartement10PlusVendeur', 
                           'VenteDepartement10MoinsVendeur','CamembertRepartitionVenteDepartement', 
                           'NombreDeVenteParDépartement', 'ValeurFonciereParDepartement', 'GraphiqueComparatifValeurFonciereAnnee2019-2022',
                           "SurfaceMedianeParDepartement", 'RepartitionTypeDeLocauxDansDepartementUrbain', 'RepartitionTypeDeLocauxDansDepartementRural',
                           'TypeDeLocauxMajoritaireEnFrance', 'TypeLocalAValeurFonciereMoyenneForteDepartement', 'TypeDeLocauxMajoritaireDansParis',
                           'TypeDeLocauxMajoritaireDansLeVaucluse', 'SurfaceMedianeVendueParDepartementParAnnee', 'PrixMedianM2ParDepartement',
                           'SurfaceMoyenneTerrainEnFonctionDuDepartement2019', 'SurfaceMoyenneTerrainEnFonctionDuDepartement2021'
                           ]
    
    
    #VenteParJourFoncieremoins300 = nombre de vente sur l'année classé par date de vente dont la valeur fonciere est inférieure 30 000 000
    #ValeurFonciereParMois = valeur foncière par mois de l'année
    #ValeurFonciereMedianeIDF = valeur fonciere médiane en Ile de France 
    
    #VenteDepartement10PlusVendeur = top 10 des départements qui ont eu le plus de vente sur l'année
    #VenteDepartement10MoinsVendeur = top 10 des départements qui ont eu le moins de vente sur l'année
    #CamembertRepartitionVenteDepartement = camembert en % des départements en fonction de leur volume de vente
    #TendanceEvolutionValeurFonciereMediane = 
    #NombreDeVenteParDépartement = nombre de vente par département
    #ValeurFonciereParDepartement = valeur foncière médiane par département
    #GraphiqueComparatifValeurFonciereAnnee = graphique comparatif des valeurs foncières entre 2019 et 2022
    #SurfaceMoyenneParDepartement = surface totale moyenne par département
    #RepartitionTypeDeLocauxDansDepartementUrbain = camembert de pourcentage pour les types de locaux vendus dans un département urbain, exemple : maison, apparetement, ...
    #RepartitionTypeDeLocauxDansDepartementRural = camembert de pourcentage pour les types de locaux vendus dans un département rural, exemple : maison, apparetement, ...
    #TypeDeLocauxMajoritaireEnFrance = carte de France avec les types de locaux majoritaire
    #TypeLocalAValeurFonciereMoyenneForteDepartement = carte de France avec le type de locaux qui a la valeur fonciere moyenne la plus forte
    #TypeDeLocauxMajoritaireDansParis = Carte Paris des locaux majoritaire dans chaque arrondissement
    #TypeDeLocauxMajoritaireDansLeVaucluse = Carte Vaucluse des locaux majoritaire dans chaque commune
    #SurfaceMedianeVendueParDepartementParAnnee = graphique ordonné des départements ayant la plus grande surface médiane vendue
    #PrixMedianM2ParDepartement = prix median du metre carre en fonction du département
    #SurfaceMoyenneTerrainEnFonctionDuDepartement2019 = prix median du metre carré par département sur 2019
    #SurfaceMoyenneTerrainEnFonctionDuDepartement2021 = prix median du metre carré par département sur 2021
    
    
    
    visualisationchoisie = None
    context = {'visualisations': ListeVisualisations}
    
    
    if request.method == 'POST':
        visualisationchoisie = request.POST.get('EnsembleVisualisations')
    
    if visualisationchoisie == 'VenteParJourFoncieremoins300':
        datafiltre = data[data['Valeur fonciere'] < 300000000]
        fig = px.scatter(datafiltre['Date mutation'], datafiltre['Valeur fonciere'], title='Ensemble des transactions réalisées sur l\'année 2022')
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
            'visualisations': ListeVisualisations,
            'visualisationchoisie': visualisationchoisie,
            'testplot': testplot
            }
        
    elif visualisationchoisie == 'ValeurFonciereParMois':
        nombreventes_mois = data.groupby('Date mutation').sum()
        nombreventes_mois = nombreventes_mois.groupby([nombreventes_mois.index.year.values,nombreventes_mois.index.month.values]).sum()
        mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        nombreventes_mois['mois'] = nombreventes_mois.index.get_level_values(1)
        nombreventes_mois['mois'] = nombreventes_mois['mois'].apply(lambda x: mois[x-1] + " 2022") # on récupère le mois dans la date
                
        fig = px.bar(x=nombreventes_mois['mois'], y=nombreventes_mois['Valeur fonciere'], title='Volume de vente par mois en € en 2022', labels={'x': 'Mois', 'y': 'Valeur foncière en milliers d\'euros'})
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
            'visualisations': ListeVisualisations,
            'visualisationchoisie': visualisationchoisie,
            'testplot': testplot
            }
        
    elif visualisationchoisie == 'ValeurFonciereMedianeIDF':
        #*
        with open('departements-ile-de-france.geojson','r') as response:
            map = json.load(response)
            data['Valeur fonciere'] = data['Valeur fonciere'].fillna(0)
            data_dep = data.groupby(data['Code departement']).median() #J'ai juste remplacé .mean() par .median()
            
            data_dep['departement'] = data_dep.index
            fig = px.choropleth_mapbox(data_dep, geojson=map, color='Valeur fonciere',
                                   locations="departement", featureidkey="properties.code",center={"lat": 48.7517, "lon": 2.7073},
                                   mapbox_style="carto-positron", zoom=7)
        fig.update_layout(title="Valeur foncière médiane par département d'Île-de-France (2022)", legend_title="Valeur")
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    elif visualisationchoisie == 'VenteDepartement10PlusVendeur':
       nombreventes_dpt = data.groupby('Code departement').sum()
       nombreventes_dpt['count'] = data['Code departement'].value_counts()
       nombreventes_dpt['dept'] = nombreventes_dpt.index

       nombreventes_dpt['dept'] = nombreventes_dpt['dept'].apply(lambda x: str(departements.get(x)) + ' (' + x + ')')
        
       nombreventes_dpt = nombreventes_dpt.sort_values(by=['count'], axis=0, ascending=False)
       nombreventes_dpt_10_pgrand = nombreventes_dpt.head(10)
       fig = px.bar(nombreventes_dpt_10_pgrand.sort_values(by=['count'], axis=0), y='dept', x='count', title='Volume de vente pour les 10 plus gros départements vendeurs (2022)', labels={'count': 'Nombre de transactions réalisées', 'dept': 'Département'}, color='dept', orientation='h').update_yaxes(type='category', categoryorder='max ascending')
       testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
       context = {
            'visualisations': ListeVisualisations,
            'visualisationchoisie': visualisationchoisie,
            'testplot': testplot
            }
       
    elif visualisationchoisie == 'VenteDepartement10MoinsVendeur':
       nombreventes_dpt = data.groupby('Code departement').sum()
       nombreventes_dpt['count'] = data['Code departement'].value_counts()
       nombreventes_dpt['dept'] = nombreventes_dpt.index

       nombreventes_dpt['dept'] = nombreventes_dpt['dept'].apply(lambda x: str(departements.get(x)) + ' (' + x + ')')
        
       nombreventes_dpt = nombreventes_dpt.sort_values(by=['count'], axis=0, ascending=False)
       nombreventes_dpt_10_ppetit = nombreventes_dpt.tail(10)
       fig = px.bar(nombreventes_dpt_10_ppetit, y='dept', x='count', title='Volume de vente pour les 10 plus petits départements vendeurs (2022)', labels={'count': 'Nombre de transactions réalisées', 'dept': 'Département'}, color='dept', orientation='h').update_yaxes(type='category')
       testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
       context = {
            'visualisations': ListeVisualisations,
            'visualisationchoisie': visualisationchoisie,
            'testplot': testplot
            }
    
        
    elif visualisationchoisie == 'CamembertRepartitionVenteDepartement':
        nombreventes_dpt = data.groupby('Code departement').sum()
        nombreventes_dpt['count'] = data['Code departement'].value_counts()
        nombreventes_dpt['dept'] = nombreventes_dpt.index
        nombreventes_dpt = nombreventes_dpt.sort_values(by=['count'], axis=0, ascending=False)
        rep_dep_vol_transac = nombreventes_dpt
        rep_dep_vol_transac.loc[rep_dep_vol_transac['count'] < 50000, 'dept'] = 'Reste des départements'
        fig = px.pie(rep_dep_vol_transac, values='count', names='dept', title='Répartition des départements en fonction du volume de transactions en 2022')
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
        #à finir
    
    elif visualisationchoisie == 'TendanceEvolutionValeurFonciereMediane':        
        fig = px.scatter(data, x="Date mutation", y="Valeur fonciere", trendline="ols")
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
        
    elif visualisationchoisie == 'NombreDeVenteParDépartement':
        with open('departements-avec-outre-mer.geojson','r') as response:
            map = json.load(response)
        nombreventes_dpt = data.groupby('Code departement').sum()
        nombreventes_dpt['count'] = data['Code departement'].value_counts()
        nombreventes_dpt['dept'] = nombreventes_dpt.index
        
        nombreventes_dpt = nombreventes_dpt.sort_values(by=['count'], axis=0, ascending=False)
        fig = px.choropleth_mapbox(nombreventes_dpt, geojson=map, color='count',
                                   locations="dept", featureidkey="properties.code",center={"lat": 48.7517, "lon": 2.7073},
                               mapbox_style="carto-positron", zoom=7)
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    elif visualisationchoisie == 'ValeurFonciereParDepartement':
        with open('departements-avec-outre-mer.geojson','r') as response:
            map = json.load(response)
        
        data['Valeur fonciere'] = data['Valeur fonciere'].fillna(0)
        data_dep = data.groupby(data['Code departement']).median()
        data_dep['departement'] = data_dep.index
        fig = px.choropleth_mapbox(data_dep, geojson=map, color='Valeur fonciere',
                           locations="departement", featureidkey="properties.code",center={"lat": 48.7517, "lon": 2.7073},
                           mapbox_style="carto-positron", zoom=7)
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    elif visualisationchoisie == 'GraphiqueComparatifValeurFonciereAnnee2019-2022':
        
        data['Valeur fonciere'] = data['Valeur fonciere'].fillna(0)
        data_dep = data.groupby(data['Code departement']).median()
        data_dep['departement'] = data_dep.index
        
        data2019['Valeur fonciere'] = data2019['Valeur fonciere'].fillna(0)
        data_dep19 = data2019.groupby(data2019['Code departement']).median()
        data_dep19['Code departement'] = data_dep19.index
        
        data2021['Valeur fonciere'] = data2021['Valeur fonciere'].fillna(0)
        data_dep21 = data2021.groupby(data2021['Code departement']).median()
        data_dep21['Code departement'] = data_dep21.index
        
        data_global = pd.DataFrame({
            'Code departement' : data_dep19['Code departement'],
            'Valeurs 2019' : data_dep19['Valeur fonciere'],
            'Valeurs 2021' : data_dep21['Valeur fonciere'],
            'Valeurs 2022' : data_dep['Valeur fonciere']
            })
        
        fig = px.bar(data_global, x='Code departement', y=['Valeurs 2022','Valeurs 2021','Valeurs 2019'])
        fig.update_layout(xaxis_title='Département', yaxis_title='Valeurs foncières médianes par année', legend_title_text='Légende')
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    elif visualisationchoisie == 'SurfaceMedianeParDepartement':
        #*
        surfacemoyenne_dpt = data.fillna(0)
        surfacemoyenne_dpt['surface carrez'] = surfacemoyenne_dpt["Surface Carrez du 1er lot"]+ surfacemoyenne_dpt["Surface Carrez du 2eme lot"]+ surfacemoyenne_dpt["Surface Carrez du 3eme lot"]+ surfacemoyenne_dpt["Surface Carrez du 4eme lot"]+ surfacemoyenne_dpt["Surface Carrez du 5eme lot"]
        surfacemoyenne_dpt.loc[surfacemoyenne_dpt['surface carrez'] > 0, 'surface'] = surfacemoyenne_dpt['surface carrez']
        surfacemoyenne_dpt.loc[surfacemoyenne_dpt['surface carrez'] <= 0, 'surface'] = surfacemoyenne_dpt['Surface reelle bati']
        surfacemoyenne_dpt.loc[surfacemoyenne_dpt['surface'] == 0, 'surface'] = surfacemoyenne_dpt['Surface terrain']
        
        surfacemoyenne_dpt['count'] = surfacemoyenne_dpt['Code departement'].value_counts()
        surfacemoyenne_dpt = surfacemoyenne_dpt.groupby('Code departement').median()
        surfacemoyenne_dpt['dept'] = surfacemoyenne_dpt.index

        surfacemoyenne_dpt['dept'] = surfacemoyenne_dpt['dept'].apply(lambda x: str(departements.get(x)) + ' (' + x + ')')
        
        fig = px.bar(surfacemoyenne_dpt, y='dept', x='surface', title='Surface médiane ayant fait l\'objet d\'une transaction en fonction du département de vente (2022)', labels={'surface': 'Surface médiane en m²', 'dept': 'Département'}, color='dept', orientation='h').update_yaxes(type='category', categoryorder='max ascending')
        
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    
    elif visualisationchoisie == 'RepartitionTypeDeLocauxDansDepartementUrbain':
        replocaux_rhone = data[data['Code departement'] == '69']
        replocaux_rhone['Type local'] = replocaux_rhone['Type local'].fillna('Autres (terrains non bâtis...)')
        
        fig = px.pie(replocaux_rhone, values=replocaux_rhone['Type local'].value_counts().values, names=replocaux_rhone['Type local'].value_counts().index, title='Répartition des types de locaux vendus dans le Rhône (urbain) (2022)', labels={'names': 'Type local', 'values' : 'Nombre de locaux vendus'})
                
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    elif visualisationchoisie == 'RepartitionTypeDeLocauxDansDepartementRural':

        replocaux_cantal = data[data['Code departement'] == '15']
        replocaux_cantal['Type local'] = replocaux_cantal['Type local'].fillna('Autres (terrains non bâtis...)')
        fig = px.pie(replocaux_cantal, values=replocaux_cantal['Type local'].value_counts().values, names=replocaux_cantal['Type local'].value_counts().index, title='Répartition des types de locaux vendus dans le Cantal (rural) (2022)', labels={'names': 'Type local', 'values' : 'Nombre de locaux vendus'})
        
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    elif visualisationchoisie == 'TypeDeLocauxMajoritaireEnFrance':
        
        maxlocaux_nat = data[['Code departement', 'Type local']]
        maxlocaux_nat['Type local'] = maxlocaux_nat['Type local'].dropna()
        locaux_counts = maxlocaux_nat.groupby(['Code departement', 'Type local']).size().reset_index(name='count')
        locaux_majoritaires = locaux_counts.groupby('Code departement')['count'].idxmax()
        maxlocaux_nat = locaux_counts.loc[locaux_majoritaires]
        
        with open('departements-avec-outre-mer.geojson','r') as response:
            map = json.load(response)
        # Plot
        fig = px.choropleth_mapbox(maxlocaux_nat, geojson=map, color='Type local',
                           locations="Code departement", featureidkey="properties.code",center={"lat": 48.7517, "lon": 2.7073},
                           mapbox_style="carto-positron", zoom=4, title='Type de local majoritaire (hors terrains à bâtir et autres) concernés par une transaction immobilière (2022)')
        
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
    
    elif visualisationchoisie == 'TypeLocalAValeurFonciereMoyenneForteDepartement':

        meanlocaux_nat = data.groupby(['Code departement', 'Type local'])['Valeur fonciere'].mean().reset_index(name='mean_value')        
        locaux_idx = meanlocaux_nat.groupby('Code departement')['mean_value'].idxmax()
        meanlocaux_nat = meanlocaux_nat.loc[locaux_idx]
        meanlocaux_nat['Code departement'] = meanlocaux_nat['Code departement'].astype(str).apply(lambda x: '0'+x if len(x) == 1 else x)
        
        with open('departements-avec-outre-mer.geojson','r') as response:
            map = json.load(response)
        # Plot
        fig = px.choropleth_mapbox(meanlocaux_nat, geojson=map, color='Type local',
                           locations="Code departement", featureidkey="properties.code",center={"lat": 48.7517, "lon": 2.7073},
                           mapbox_style="carto-positron", zoom=4, title='Type de local ayant la valeur foncière moyenne la plus forte (2022)')
        
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    elif visualisationchoisie == 'TypeDeLocauxMajoritaireDansParis':

        parisdata = data[data['Code departement'] == '75']
        parisdata['Code INSEE'] = parisdata['Code departement'].astype(str) + parisdata['Code commune'].astype(str)
        parisdata['Code postal'] = parisdata['Code postal'].astype(str).apply(lambda x: x[:-2])
        
        parisdata = parisdata[['Code INSEE', 'Type local']]
        locaux_counts = parisdata.groupby(['Code INSEE', 'Type local']).size().reset_index(name='count')
        locaux_majoritaires = locaux_counts.groupby('Code INSEE')['count'].idxmax()
        parisdata = locaux_counts.loc[locaux_majoritaires]
        
        with open('communes-75-paris.geojson','r') as response:
            map = json.load(response)
        # Plot
        fig = px.choropleth_mapbox(parisdata, geojson=map, color='Type local',
                           locations="Code INSEE", featureidkey="properties.code",center={"lat": 48.7517, "lon": 2.7073},
                           mapbox_style="carto-positron", zoom=4, title='Type de local majoritairement concernés par une transaction immobilière à Paris (2022)')

        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    elif visualisationchoisie == 'TypeDeLocauxMajoritaireDansLeVaucluse':
        #**
        codeDep = '84'
        vauclusedata = data[data['Code departement'] == codeDep]
        nomDep, MapDataURL = getMapDataURL_Departement(codeDep)

        """
        vauclusedata.loc[vauclusedata['Commune'] == 'CABRIERES-D AIGUES', 'Commune'] = 'CABRIERES-D\'AIGUES'
        vauclusedata.loc[vauclusedata['Commune'] == 'CABRIERES-D AVIGNON', 'Commune'] = 'CABRIERES-D\'AVIGNON'
        vauclusedata.loc[vauclusedata['Commune'] == 'CRESTET (LE)', 'Commune'] = 'CRESTET'
        vauclusedata.loc[vauclusedata['Commune'] == 'L ISLE SUR LA SORGUE', 'Commune'] = 'L\'ISLE SUR LA SORGUE'
        vauclusedata.loc[vauclusedata['Commune'] == 'LA MOTTE D AIGUES', 'Commune'] = 'LA MOTTE D\'AIGUES'
        vauclusedata.loc[vauclusedata['Commune'] == 'LA TOUR D AIGUES', 'Commune'] = 'LA TOUR D\'AIGUES'
        vauclusedata.loc[vauclusedata['Commune'] == 'LES TAILLADES', 'Commune'] = 'TAILLADES'
        vauclusedata.loc[vauclusedata['Commune'] == 'PEYPIN-D AIGUES', 'Commune'] = 'PEYPIN-D\'AIGUES'
        vauclusedata.loc[vauclusedata['Commune'] == 'SAINT-MARCELIN-LES-VAISON', 'Commune'] = 'SAINT-MARCELLIN-LES-VAISON'
        vauclusedata.loc[vauclusedata['Commune'] == 'SAVOILLANS', 'Commune'] = 'SAVOILLAN'
        vauclusedata.loc[vauclusedata['Commune'] == 'ST HIPPOLYTE LE GRAVERON', 'Commune'] = 'Saint-Hippolyte-le-Graveyron'
        """
        
        vauclusedata = vauclusedata[['Code INSEE', 'Commune', 'Type local']]
        locaux_counts = vauclusedata.groupby(['Code INSEE', 'Commune', 'Type local']).size().reset_index(name='Locaux concernés')
        locaux_majoritaires = locaux_counts.groupby('Code INSEE')['Locaux concernés'].idxmax()
        vauclusedata = locaux_counts.loc[locaux_majoritaires]
        
        geoCentre = getCentreDepartement(vauclusedata['Code INSEE'].iloc[0])    

        fig = px.choropleth_mapbox(vauclusedata, geojson=MapDataURL, color='Type local',
                           locations="Code INSEE", featureidkey="properties.code",center={"lon": geoCentre[0], "lat": geoCentre[1]}, hover_data=['Commune', 'Locaux concernés'],
                           mapbox_style="carto-positron", zoom=4, title=f'Type de local majoritairement concernés par une transaction immobilière dans le département {nomDep} (2022)')
        
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    elif visualisationchoisie == 'SurfaceMedianeVendueParDepartementParAnnee':
        
        data_area = data.fillna(0) #à affiner pour éviter de tout passer à zéro

        #Ajout d'une case agrégeant les surfaces Carrez et d'une case Surface des locaux
        data_area['surface carrez'] = data_area["Surface Carrez du 1er lot"]+ data_area["Surface Carrez du 2eme lot"]+ data_area["Surface Carrez du 3eme lot"]+ data_area["Surface Carrez du 4eme lot"]+ data_area["Surface Carrez du 5eme lot"]
        data_area.loc[data_area['surface carrez'] > 0, 'surface'] = data_area['surface carrez']
        data_area.loc[data_area['surface carrez'] <= 0, 'surface'] = data_area['Surface reelle bati']
        data_area.loc[data_area['surface'] == 0, 'surface'] = data_area['Surface terrain']
        
        data_area['count'] = data_area['Code departement'].value_counts()
        
        data_area['prix du m2'] = data_area['Valeur fonciere']/data_area['surface']
        
        data_area = data_area.groupby('Code departement').median()
        data_area['dept'] = data_area.index
        
        data_area['dept'] = data_area['dept'].apply(lambda x: str(departements.get(x)) + ' (' + str(x) + ')')
        
        
        data_area21 = data2021.fillna(0) #à affiner pour éviter de tout passer à zéro

        #Ajout d'une case agrégeant les surfaces Carrez et d'une case Surface des locaux
        data_area21['surface carrez'] = data_area21["Surface Carrez du 1er lot"]+ data_area21["Surface Carrez du 2eme lot"]+ data_area21["Surface Carrez du 3eme lot"]+ data_area21["Surface Carrez du 4eme lot"]+ data_area21["Surface Carrez du 5eme lot"]
        data_area21.loc[data_area21['surface carrez'] > 0, 'surface'] = data_area21['surface carrez']
        data_area21.loc[data_area21['surface carrez'] <= 0, 'surface'] = data_area21['Surface reelle bati']
        data_area21.loc[data_area21['surface'] == 0, 'surface'] = data_area21['Surface terrain']
        
        data_area21['count'] = data_area21['Code departement'].value_counts()
        
        data_area21['prix du m2'] = data_area21['Valeur fonciere']/data_area21['surface']
        
        data_area21 = data_area21.groupby('Code departement').median()
        data_area21['dept'] = data_area21.index
        
        data_area21['dept'] = data_area21['dept'].apply(lambda x: str(departements.get(x)) + ' (' + str(x) + ')')
        
        data_area19 = data2019.fillna(0) #à affiner pour éviter de tout passer à zéro

        #Ajout d'une case agrégeant les surfaces Carrez et d'une case Surface des locaux
        data_area19['surface carrez'] = data_area19["Surface Carrez du 1er lot"]+ data_area19["Surface Carrez du 2eme lot"]+ data_area19["Surface Carrez du 3eme lot"]+ data_area19["Surface Carrez du 4eme lot"]+ data_area19["Surface Carrez du 5eme lot"]
        data_area19.loc[data_area19['surface carrez'] > 0, 'surface'] = data_area19['surface carrez']
        data_area19.loc[data_area19['surface carrez'] <= 0, 'surface'] = data_area19['Surface reelle bati']
        data_area19.loc[data_area19['surface'] == 0, 'surface'] = data_area19['Surface terrain']
        
        data_area19['count'] = data_area19['Code departement'].value_counts()
        
        data_area19['prix du m2'] = data_area19['Valeur fonciere']/data_area19['surface']
        
        data_area19 = data_area19.groupby('Code departement').median()
        data_area19['dept'] = data_area19.index
        
        data_area19['dept'] = data_area19['dept'].apply(lambda x: str(departements.get(x)) + ' (' + str(x) + ')')
        
        data_surf = pd.DataFrame({
            'dept' : data_area['dept'],
            'surface 2022' : data_area['surface'],
            'surface 2021' : data_area21['surface'],
            'surface 2019' : data_area19['surface'],
            'surface 2019-22' : data_area['surface']+data_area21['surface']+data_area19['surface']
        })

        fig = px.bar(data_surf, y='dept', x=['surface 2022', 'surface 2021', 'surface 2019'], title='Surface médiane vendue en fonction du département de vente', labels={'surface': 'Surface médiane en m²', 'dept': 'Département'}, color='dept', orientation='h')
        fig.update_yaxes(title="Département",type='category', categoryorder='sum ascending')
        fig.update_xaxes(title="Surface")
        fig.update_layout(legend_title_text="Légende")
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
    
    
    elif visualisationchoisie == 'PrixMedianM2ParDepartement':
        
        surfacemoyenne_dpt = data.fillna(0) #à affiner pour éviter de tout passer à zéro

        #Ajout d'une case agrégeant les surfaces Carrez et d'une case Surface des locaux
        surfacemoyenne_dpt['surface carrez'] = surfacemoyenne_dpt["Surface Carrez du 1er lot"]+ surfacemoyenne_dpt["Surface Carrez du 2eme lot"]+ surfacemoyenne_dpt["Surface Carrez du 3eme lot"]+ surfacemoyenne_dpt["Surface Carrez du 4eme lot"]+ surfacemoyenne_dpt["Surface Carrez du 5eme lot"]
        surfacemoyenne_dpt.loc[surfacemoyenne_dpt['surface carrez'] > 0, 'surface'] = surfacemoyenne_dpt['surface carrez']
        surfacemoyenne_dpt.loc[surfacemoyenne_dpt['surface carrez'] <= 0, 'surface'] = surfacemoyenne_dpt['Surface reelle bati']
        surfacemoyenne_dpt.loc[surfacemoyenne_dpt['surface'] == 0, 'surface'] = surfacemoyenne_dpt['Surface terrain']
        
        surfacemoyenne_dpt['count'] = surfacemoyenne_dpt['Code departement'].value_counts()
        surfacemoyenne_dpt = surfacemoyenne_dpt.groupby('Code departement').median()
        surfacemoyenne_dpt['dept'] = surfacemoyenne_dpt.index        
        
        surfacemoyenne_dpt['dept'] = surfacemoyenne_dpt['dept'].apply(lambda x: str(departements.get(x)) + ' (' + str(x) + ')')
        surfacemoyenne_dpt['prix du m2'] = surfacemoyenne_dpt['Valeur fonciere']/surfacemoyenne_dpt['surface']
        
        data_area = data.fillna(0) #à affiner pour éviter de tout passer à zéro

        #Ajout d'une case agrégeant les surfaces Carrez et d'une case Surface des locaux
        data_area['surface carrez'] = data_area["Surface Carrez du 1er lot"]+ data_area["Surface Carrez du 2eme lot"]+ data_area["Surface Carrez du 3eme lot"]+ data_area["Surface Carrez du 4eme lot"]+ data_area["Surface Carrez du 5eme lot"]
        data_area.loc[data_area['surface carrez'] > 0, 'surface'] = data_area['surface carrez']
        data_area.loc[data_area['surface carrez'] <= 0, 'surface'] = data_area['Surface reelle bati']
        data_area.loc[data_area['surface'] == 0, 'surface'] = data_area['Surface terrain']
        
        data_area['count'] = data_area['Code departement'].value_counts()
        
        data_area['prix du m2'] = data_area['Valeur fonciere']/data_area['surface']
        
        data_area = data_area.groupby('Code departement').median()
        data_area['dept'] = data_area.index
        
        
        data_area['dept'] = data_area['dept'].apply(lambda x: str(departements.get(x)) + ' (' + str(x) + ')')
        
        
        data_area21 = data2021.fillna(0) #à affiner pour éviter de tout passer à zéro

        #Ajout d'une case agrégeant les surfaces Carrez et d'une case Surface des locaux
        data_area21['surface carrez'] = data_area21["Surface Carrez du 1er lot"]+ data_area21["Surface Carrez du 2eme lot"]+ data_area21["Surface Carrez du 3eme lot"]+ data_area21["Surface Carrez du 4eme lot"]+ data_area21["Surface Carrez du 5eme lot"]
        data_area21.loc[data_area21['surface carrez'] > 0, 'surface'] = data_area21['surface carrez']
        data_area21.loc[data_area21['surface carrez'] <= 0, 'surface'] = data_area21['Surface reelle bati']
        data_area21.loc[data_area21['surface'] == 0, 'surface'] = data_area21['Surface terrain']
        
        data_area21['count'] = data_area21['Code departement'].value_counts()
        
        data_area21['prix du m2'] = data_area21['Valeur fonciere']/data_area21['surface']
        
        data_area21 = data_area21.groupby('Code departement').median()
        data_area21['dept'] = data_area21.index
        
        data_area21['dept'] = data_area21['dept'].apply(lambda x: str(departements.get(x)) + ' (' + str(x) + ')')
        
        data_area19 = data2019.fillna(0) #à affiner pour éviter de tout passer à zéro

        #Ajout d'une case agrégeant les surfaces Carrez et d'une case Surface des locaux
        data_area19['surface carrez'] = data_area19["Surface Carrez du 1er lot"]+ data_area19["Surface Carrez du 2eme lot"]+ data_area19["Surface Carrez du 3eme lot"]+ data_area19["Surface Carrez du 4eme lot"]+ data_area19["Surface Carrez du 5eme lot"]
        data_area19.loc[data_area19['surface carrez'] > 0, 'surface'] = data_area19['surface carrez']
        data_area19.loc[data_area19['surface carrez'] <= 0, 'surface'] = data_area19['Surface reelle bati']
        data_area19.loc[data_area19['surface'] == 0, 'surface'] = data_area19['Surface terrain']
        
        data_area19['count'] = data_area19['Code departement'].value_counts()
        
        data_area19['prix du m2'] = data_area19['Valeur fonciere']/data_area19['surface']
        
        data_area19 = data_area19.groupby('Code departement').median()
        data_area19['dept'] = data_area19.index
        
        data_area19['dept'] = data_area19['dept'].apply(lambda x: str(departements.get(x)) + ' (' + str(x) + ')')
        
        data_area20 = data2020.fillna(0) #à affiner pour éviter de tout passer à zéro

        #Ajout d'une case agrégeant les surfaces Carrez et d'une case Surface des locaux
        data_area20['surface carrez'] = data_area20["Surface Carrez du 1er lot"]+ data_area20["Surface Carrez du 2eme lot"]+ data_area20["Surface Carrez du 3eme lot"]+ data_area20["Surface Carrez du 4eme lot"]+ data_area20["Surface Carrez du 5eme lot"]
        data_area20.loc[data_area20['surface carrez'] > 0, 'surface'] = data_area20['surface carrez']
        data_area20.loc[data_area20['surface carrez'] <= 0, 'surface'] = data_area20['Surface reelle bati']
        data_area20.loc[data_area20['surface'] == 0, 'surface'] = data_area20['Surface terrain']
        
        data_area20['prix du m2'] = data_area20['Valeur fonciere']/data_area20['surface']
        
        data_area20 = data_area20.groupby('Code departement').median()
        data_area20['dept'] = data_area20.index
        data_area20['prix du m2'] = data_area20['Valeur fonciere']/data_area20['surface']
        
        data_area20['dept'] = data_area20['dept'].apply(lambda x: str(departements.get(x)) + ' (' + str(x) + ')')
        
        data_area_all = pd.DataFrame({
            'dept' : data_area19['dept'], #Choix de l'année totalement arbitraire
            'prix 2022' : surfacemoyenne_dpt['prix du m2'],
            'prix 2021' : data_area21['prix du m2'],
            'prix 2020' : data_area20['prix du m2'],
            'prix 2019' : data_area19['prix du m2'],
        })

        fig = px.bar(data_area_all, y='dept', x=['prix 2022', 'prix 2021', 'prix 2020', 'prix 2019'], title='Prix médian du mètre carré en fonction du département de vente', labels={'surface': 'Surface médiane en m²', 'dept': 'Département'}, color='dept', orientation='h')
        fig.update_yaxes(title="Département",type='category', categoryorder='sum ascending')
        fig.update_xaxes(title="Prix du m2")
        fig.update_layout(legend_title_text="Légende")
        
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }
        
    elif visualisationchoisie == 'SurfaceMoyenneTerrainEnFonctionDuDepartement2019':
        data_area19 = data2019.fillna(0) #à affiner pour éviter de tout passer à zéro
        
        #Ajout d'une case agrégeant les surfaces Carrez et d'une case Surface des locaux
        data_area19['surface carrez'] = data_area19["Surface Carrez du 1er lot"]+ data_area19["Surface Carrez du 2eme lot"]+ data_area19["Surface Carrez du 3eme lot"]+ data_area19["Surface Carrez du 4eme lot"]+ data_area19["Surface Carrez du 5eme lot"]
        data_area19.loc[data_area19['surface carrez'] > 0, 'surface'] = data_area19['surface carrez']
        data_area19.loc[data_area19['surface carrez'] <= 0, 'surface'] = data_area19['Surface reelle bati']
        data_area19.loc[data_area19['surface'] == 0, 'surface'] = data_area19['Surface terrain']
        
        data_area19['count'] = data_area19['Code departement'].value_counts()
        
        data_area19['prix du m2'] = data_area19['Valeur fonciere']/data_area19['surface']
        
        data_area19 = data_area19.groupby('Code departement').median()
        data_area19['dept'] = data_area19.index
        
        data_area19['dept'] = data_area19['dept'].apply(lambda x: str(departements.get(x)) + ' (' + str(x) + ')')
        fig = px.bar(data_area19, y='dept', x='prix du m2', title='Prix médian du mètre carré en fonction du département de vente (2019)', labels={'surface': 'Surface médiane en m²', 'dept': 'Département'}, color='dept', orientation='h').update_yaxes(type='category', categoryorder='max ascending')

        
        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
            'visualisations': ListeVisualisations,
            'visualisationchoisie': visualisationchoisie,
            'testplot': testplot
            }
    elif visualisationchoisie == 'SurfaceMoyenneTerrainEnFonctionDuDepartement2021':
        
        data_area21 = data2021.fillna(0) #à affiner pour éviter de tout passer à zéro

        #Ajout d'une case agrégeant les surfaces Carrez et d'une case Surface des locaux
        data_area21['surface carrez'] = data_area21["Surface Carrez du 1er lot"]+ data_area21["Surface Carrez du 2eme lot"]+ data_area21["Surface Carrez du 3eme lot"]+ data_area21["Surface Carrez du 4eme lot"]+ data_area21["Surface Carrez du 5eme lot"]
        data_area21.loc[data_area21['surface carrez'] > 0, 'surface'] = data_area21['surface carrez']
        data_area21.loc[data_area21['surface carrez'] <= 0, 'surface'] = data_area21['Surface reelle bati']
        data_area21.loc[data_area21['surface'] == 0, 'surface'] = data_area21['Surface terrain']
        
        data_area21['count'] = data_area21['Code departement'].value_counts()
        
        data_area21['prix du m2'] = data_area21['Valeur fonciere']/data_area21['surface']
        
        data_area21 = data_area21.groupby('Code departement').median()
        data_area21['dept'] = data_area21.index
        
        data_area21['dept'] = data_area21['dept'].apply(lambda x: str(departements.get(x)) + ' (' + str(x) + ')')
        fig = px.bar(data_area21, y='dept', x='prix du m2', title='Prix médian du mètre carré en fonction du département de vente (2021)', labels={'surface': 'Surface médiane en m²', 'dept': 'Département'}, color='dept', orientation='h').update_yaxes(type='category', categoryorder='max ascending')

        testplot = fig.to_html(full_html = False , default_height = 1000 , default_width = 1500)
        context = {
             'visualisations': ListeVisualisations,
             'visualisationchoisie': visualisationchoisie,
             'testplot': testplot
             }

    return render(request, 'template0.html', context)

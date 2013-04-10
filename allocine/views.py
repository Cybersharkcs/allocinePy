#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render
#from django.http import HttpResponse
from allocine.models import Cinema, Film

# Create your views here.

def index(request):
    motCle=['saint', 'cloud', '']
    cinema=Cinema()
    film=Film()
    filmsoup=[]
    infosfilms=[]
    infosDateSortie=[]
    result=[]
    soup=cinema.findCinemaSoup(motCle)
    nbr=cinema.findNbFilmsSoup(soup)
    #Noms
    for i in range(nbr):
        filmsoup.append(cinema.getFilmSoup(soup, i))
        infosfilms.append(film.getNom(filmsoup[i]))
        infosDateSortie.append(film.getDateSortie(filmsoup[i], result))
    
    #return HttpResponse(infosfilms)    
    return render(request, 'allocine/index.html', {'infosfilms':infosfilms, 'infosDateSortie':infosDateSortie})
#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import re
from bs4 import BeautifulSoup
import sqlite3

# Create your models here.

class Cinema():
    def __init__(self):
        self.urlAllocine='http://www.allocine.fr'
        self.film=["div", { "class" : "datablock w-shareyourshowtime" }]
    
    def findCinemaSoup(self, motCle):
        #recherche allocine
        sourceAllocine=getSource(self.urlAllocine+"/recherche/?q="+motCle[0]+"+"+motCle[1]+"+"+motCle[2])
        linkCinema = re.findall('/seance/salle_gen_csalle=.*.html', sourceAllocine)
        sourceCinema=getSource(self.urlAllocine+linkCinema[0])
        #recherche UGC ...
        
        #enregistrement soupe cinema recherché
        return BeautifulSoup(sourceCinema)
    
    def findNbFilmsSoup(self, soup):
        #nombre films projectés
        films=soup.find_all("a", href=re.compile("#movie.*"))
        nbr=len(films)
        return nbr
    
    def getFilmSoup(self, soup, numFilm):
        mainzone=soup.find_all( self.film[0], self.film[1], limit=self.findNbFilmsSoup(soup) )[numFilm]
        return mainzone

class Database():
    def __init__(self):
        self.conn = sqlite3.connect('/home/maxime-pi/db/films.db')
        try:
            initDatabase=self.conn.cursor()
            #3 champs fixe
            initDatabase.execute("CREATE TABLE films (id INTEGER primary key, nom TEXT, date_sortie TEXT);")
            #6 champs fixe
            initDatabase.execute("CREATE TABLE acteurs_id (id INTEGER primary key, realisateur VARCHAR(30), acteur_1 VARCHAR(30), acteur_2 VARCHAR(30), acteur_3 VARCHAR(30), acteur_4 VARCHAR(30));")
            #2 champs fixe
            initDatabase.execute("CREATE TABLE bandes_annonce (id INTEGER primary key, url TEXT);")
            #8 champs fixe
            initDatabase.cexecute("CREATE TABLE horaires_id (id INTEGER primary key, heure_1 TEXT, heure_2 TEXT, heure_3 TEXT, heure_4 TEXT, heure_5 TEXT, heure_6 TEXT, heure_7 TEXT);")
            #8 champs fixe
            initDatabase.cexecute("CREATE TABLE jours_projection_id (id INTEGER primary key, jour_1 TEXT, jour_2 TEXT, jour_3 TEXT, jour_4 TEXT, jour_5 TEXT, jour_6 TEXT, jour_7 TEXT);")
            #3 champs fixe
            initDatabase.execute("CREATE TABLE format_id (id INTEGER primary key, version VARCHAR(30), type VARCHAR(30));")
            #3 champs fixe
            initDatabase.execute("CREATE TABLE notes_id (id INTEGER primary key, presse VARCHAR(30), spectateurs VARCHAR(30));")
            self.conn.commit()
            initDatabase.close()
        except:
            print "Databases deja init"

    def deleteResultsTable(self, nomTable):
        c=self.conn.cursor()
        c.execute("DELETE FROM "+nomTable)
        self.conn.commit()
        c.close()

    def appendResultsTable(self, index, nomTable, donnees, tailleTableDynamique, tailleTableStatique):
        c=self.conn.cursor()
        print tailleTableDynamique, tailleTableStatique, donnees
        value=[index]
        #on rajoute les donnees de la taille dynamique a value
        for j in range(0, tailleTableDynamique):
            if(j<tailleTableStatique-1):
                try:
                    value.append(donnees[j].string)
                except:
                    print "no attribute string"
                    #cas particulier BA
                    if(donnees[j]):
                        value.append(donnees[j])
                    else:
                        value.append(" ")
        #on complete si besoin les donnees
        while(tailleTableDynamique<tailleTableStatique-1):
            value.append(" ")
            tailleTableDynamique=tailleTableDynamique+1
        print value
        valueTuple=tuple(value)
        requete='''INSERT INTO {0} VALUES ({1})'''.format(nomTable, ','.join('?'*len(value)))
        print requete
        print valueTuple
        c.execute(requete, valueTuple)
        self.conn.commit()
        c.close()

    def readResultsTable(self, nomTable):
        c=self.conn.cursor()
        c.execute("SELECT * FROM "+nomTable+";")
        for row in c:
            print row
        c.close()
        
class Film:
    def __init__(self):
        #criteres de recherche : nom, date sortie, acteurs, notes, bandeannonce, joursprojection, V, heures
        self.nom=["a","/film/fichefilm_gen_cfilm.*.html"]
        self.dateSortie=["b"]
        self.acteurs=["a", "/personne/fichepersonne_gen_cpersonne=.*.html"]
        self.bandeAnnonce=["a" , "/video/player_gen_cmedia=.*"]
        self.horaires=["div", { "class" : re.compile('^pane.*') }, "rel", "em"]
        self.format=["span", { "class" : "bold" }]
        self.jourProjection=["ul", { "class" : "items"}, "span"]
        self.notes=["span", { "class" : "moreinfo" }]
        self.infosNom=[]
        self.infosDateSortie=[]
        self.infosActeurs=[]
        self.infosBA=[]
        self.infosHoraires=[]
        self.infosFormat=[]
        self.infosJoursProjection=[]
        self.infosNotes=[]
        self.result=[]
    
    def getNom(self, mainzone):
        self.result=[]
        self.result.append(mainzone.find_all( self.nom[0], href=re.compile( self.nom[1] ) ))
        self.infosNom=self.result[0][1].string
        return self.infosNom
    
    def getDateSortie(self, mainzone, resultt):
        resultt.append(mainzone.find_all( self.dateSortie[0] ))
        self.dateSortie=resultt[0][0].string
        return self.dateSortie
    
    def getActeurs(self, mainzone):
        self.result=[]
        self.result.append(mainzone.find_all( self.acteurs[0], href=re.compile( self.acteurs[1] ) ))
        for j in range(len(self.result[0])):
            self.infosActeurs.append(self.result[0][j].string)
        return self.infosActeurs
    
    def getBandeAnnonce(self, mainzone, result):
        result.append(mainzone.find_all( self.bandeAnnonce[0], href=re.compile( self.bandeAnnonce[1]) ))
        urlBA=re.match(r'(.*)/video/player_gen_cmedia=(.*).html(\.*)', str(result[0][0]), re.M|re.I)
        self.infosBA.append("www.allocine.fr/video/player_gen_cmedia="+urlBA.group(2)+".html")
        return self.infosBA
    
    def getHoraires(self, mainzone, result):
        #Horaires niveau 1
        result.append(mainzone.find_all( self.horaires[0], self.horaires[1] ))
                
        #Horaires niveau 2
        buf=result[7]
        buf=str(buf)
        soupp=BeautifulSoup(buf)
        horairesAujourdhui=soupp.find_all( self.horaires[3] )
        for j in range(len(horairesAujourdhui)):
            self.infosHoraires.append(horairesAujourdhui[j].string)
        return self.infosHoraires
    
    def getFormat(self, mainzone, result):
        result.append(mainzone.find_all( self.format[0], self.format[1] ))
        for j in range(len(result[0])):
            self.infosFormat.append(result[0][j].string)
        return self.infosFormat
    
    def getJourProjection(self, mainzone, result):
        #Jours projection niveau 1
        result.append(mainzone.find_all( self.jourProjection[0], self.jourProjection[1] ))
                
        #Jours projection niveau 2 (4 max)
        buf=result[0]
        buf=str(buf)
        soupp=BeautifulSoup(buf)
        joursProjection=soupp.find_all( self.jourProjection[2] )
        for j in range(len(joursProjection)):
            self.infosJoursProjection.append(joursProjection[j].string)
        return self.infosJoursProjection
    
    def getNotes(self, mainzone, result):
        result.append(mainzone.find_all( self.notes[0], self.notes[1] ))
        for j in range(len(result[0])):
            self.infosNotes.append(result[0][j].string)
        return self.infosNotes
    
    def getDuree(self, mainzone, result):
        return self.duree

def getSource(url):
    usock = urllib2.urlopen(url)
    htmlSource=usock.read()
    usock.close()
    return htmlSource

def debug(content, debug):
    if debug==True:
        try:
            print content.encode("utf-8")
        except:
            print content
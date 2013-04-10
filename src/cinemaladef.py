#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import re
from bs4 import BeautifulSoup
import sqlite3
import sys

class Cinema():
    def __init__(self):
        self.urlAllocine='http://www.allocine.fr'
        self.film=["div", { "class" : "datablock w-shareyourshowtime" }]
    
    def findSourceCinema(self, motCle):
        #recherche allocine
        sourceAllocine=getSource(self.urlAllocine+"/recherche/?q="+motCle[0]+"+"+motCle[1]+"+"+motCle[2])
        linkCinema = re.findall('/seance/salle_gen_csalle=.*.html', sourceAllocine)
        debug(linkCinema, False)
        sourceCinema=getSource(self.urlAllocine+linkCinema[0])
        debug(sourceCinema, False)
        #enregistrement soupe cinema recherché
        soup=BeautifulSoup(sourceCinema)
        return soup
    
    def findNbFilms(self, soup):
        #nombre films projectés
        films=soup.find_all("a", href=re.compile("#movie.*"))
        nbr=len(films)
        debug(nbr, False)
        return nbr
    
    def getFilm(self):
        return self.film
    
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

    def readResults(self, nomTable):
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
        self.horaires=["div", { "class" : re.compile('^pane.*') }, "rel"]
        self.format=["span", { "class" : "bold" }]
        self.jourProjection=["ul", { "class" : "items"}]
        self.notes=["span", { "class" : "moreinfo" }]
        self.duree=[]
    
    def getNom(self):
        return self.nom
    def getDateSortie(self):
        return self.dateSortie
    def getActeurs(self):
        return self.acteurs
    def getBandeAnnonce(self):
        return self.bandeAnnonce
    def getHoraires(self):
        return self.horaires
    def getFormat(self):
        return self.format
    def getJourProjection(self):
        return self.jourProjection
    def getNotes(self):
        return self.notes
    def getDuree(self):
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

#creation des objets et init des variables
index=1
motCle=[sys.argv[1], sys.argv[2], sys.argv[3]]
cinema=Cinema()
film=Film()
database=Database()

#recuperation source cinema
soup=cinema.findSourceCinema(motCle)

#Efface donnees bdd
try:
    database.deleteResultsTable("films")
    database.deleteResultsTable("acteurs_id")
    database.deleteResultsTable("format_id")
    database.deleteResultsTable("notes_id")
    database.deleteResultsTable("horaires_id")
    database.deleteResultsTable("jours_projection_id")
    database.deleteResultsTable("bandes_annonce")
except:
    print "Tables clean"

#extraction des infos films: nom, date sortie, acteurs, notes, bandeannonce, joursprojection, V, heures
for i in range(cinema.findNbFilms(soup)):
    # on recupere les infos generales d'un film niveau 1
    mainzone=soup.find_all( cinema.getFilm()[0], cinema.getFilm()[1], limit=cinema.findNbFilms(soup) )[i]
    debug(mainzone, False)
        
    #tableau contenant les infos precises niveau 2
    result=[]
    
    #Nom
    debug("Nom----------------------------------", True)
    result.append(mainzone.find_all( film.getNom()[0], href=re.compile( film.getNom()[1] ) ))
    debug(result[0][1].string, True)
        
    #Date de sortie
    debug("Date de sortie----------------------------------", True)
    result.append(mainzone.find_all( film.getDateSortie()[0] ))
    #exception si aucun result
    try:
        debug(result[1][0].string, True)
        database.appendResultsTable(index, "films", [result[0][1].string, result[1][0].string], len(result[0])+len(result[1]), 3)
    except:
        database.appendResultsTable(index, "films", [result[0][1].string, ''], len(result[0])+len(result[1]), 3)
        
    #figurants
    result.append(mainzone.find_all( film.getActeurs()[0], href=re.compile( film.getActeurs()[1] ) ))
    #realisateur
    debug("Realisateur, acteurs...----------------------------------", True)
    print len(result[2])
    for j in range(len(result[2])):
        debug(result[2][j].string, True)
    database.appendResultsTable(index, "acteurs_id", result[2], len(result[2]), 6)
    
    #Bande annonce buggy (recuperer celle de youtube à la place)
    result.append(mainzone.find_all( film.getBandeAnnonce()[0], href=re.compile( film.getBandeAnnonce()[1]) ))
    debug(result[3][0].string, True)
    urlBA=re.match(r'(.*)/video/player_gen_cmedia=(.*).html(\.*)', str(result[3][0]), re.M|re.I)
    debug(urlBA.group(), True)
    database.appendResultsTable(index, "bandes_annonce", ["www.allocine.fr/video/player_gen_cmedia="+urlBA.group(2)+".html"], len(result[3]), 2)
    
    #Format VO/VF, numerique/3D
    debug("Format----------------------------------", True)
    result.append(mainzone.find_all( film.getFormat()[0], film.getFormat()[1] ))
    print len(result[4])
    for j in range(len(result[4])):
        debug(result[4][j].string, True)
    database.appendResultsTable(index, "format_id", result[4], len(result[4]), 3)
        
    #Jours projection niveau 1
    debug("Jours projection----------------------------------", True)
    result.append(mainzone.find_all( film.getJourProjection()[0], film.getJourProjection()[1] ))
    debug(result[5], False)
    
    #Jours projection niveau 2 (4 max)
    buf=result[5]
    debug(buf, False)
    buf=str(buf)
    soupp=BeautifulSoup(buf)
    joursProjection=[]
    joursProjection=soupp.find_all("span")
    
    print len(joursProjection)
    for j in range(len(joursProjection)):
        debug(joursProjection[j].string, True)
    database.appendResultsTable(index, "jours_projection_id", joursProjection, len(joursProjection), 8)
        
    #Notes presse/spectateurs
    result.append(mainzone.find_all( film.getNotes()[0], film.getNotes()[1] ))
    debug("Note presse/spectateurs----------------------------------", True)
    print len(result[6])
    for j in range(len(result[6])):
        debug(result[6][j].string, True)
    database.appendResultsTable(index, "notes_id", result[6], len(result[6]), 3)
    
    #Horaires niveau 1
    result.append(mainzone.find_all( film.getHoraires()[0], film.getHoraires()[1] ))
    debug(result[7], False)
    
    #Horaires niveau 2
    buf=result[7]
    debug(buf, False)
    buf=str(buf)
    soupp=BeautifulSoup(buf)
    horairesAujourdhui=[]
    horairesAujourdhui=soupp.find_all("em")
    
    debug("Horaires-----------------------------------------------------", True)
    print len(horairesAujourdhui)
    for j in range(len(horairesAujourdhui)):
        debug(horairesAujourdhui[j].string, True)
    database.appendResultsTable(index, "horaires_id", horairesAujourdhui, len(horairesAujourdhui), 8)
    
#    Duree
#    debug("Duree ----------------------------------", True)    
#    result.append(mainzone.find_all( film.getDuree[0] ))
#    debug(result[8], True)
    
    index=index+1
    debug("-----------------------------------------------------------------------------------------", True)
    debug(" ", True)
    #tableau result rempli !

debug("DATABASE DEBUG---------------------------------------------------------------------------------", True)
database.readResults("films")
database.readResults("acteurs_id")
database.readResults("format_id")
database.readResults("notes_id")
database.readResults("horaires_id")
database.readResults("jours_projection_id")
database.readResults("bandes_annonce")
#REQUIREMENTS:
# * Display: Debugging met Jupyter ondersteuning
# * ArcGIS GIS: Obvious reasons. Aanmelden & Group manipulatie
# * ArcGIS GROUP: Om groepen te kunnen beheren
# * Keyring: Voor sign-in-loze redenen
#Credits
# Geschreven door Guus Klaas - BI-GIS (STEDIN)

from IPython.display import display
from arcgis.gis import GIS
from arcgis.gis import Group
import keyring
import time
import requests
import datetime
import re
webhook = "https://hooks.slack.com/services/SUPERGEHEIM"

print("Signing in to Stedin Maps...")

#Veilig aanmelden met een keyring-profile; zodat credentials niet in het script staan
agssite = GIS(profile="gis-prod")

print("ArcGIS aangemeld als: " + agssite.properties.user.username + "\nChecking for new users...")

#Array van ArcGIS Groepen waar gebruikers in moeten
groupList = []
groupList.append(Group(agssite, '82221da5de0c4e14b7076762c25026cd'))        #Algemeen
groupList.append(Group(agssite, 'ba926e1a8ee44fc89cdd1c0f40e92194'))        #Elektra
groupList.append(Group(agssite, '3e31d72d56354e7d9f5f1358fdb9366f'))        #Gas
groupList.append(Group(agssite, '7242484284f6457daea06b1b03dbe15c'))        #Kaarten
groupList.append(Group(agssite, '62822382baef442b83e626b2dc6f7735'))        #Featured


#Formaat tijd/datum in output, de rest is allemaal unix epoch
fmt = "%d-%m-%Y %H:%M:%S"

#gebruik de RE import om ook een nieuw user bericht op Slack te plaatsen
def PostUserToSlack(UserString):
    r = requests.post(webhook, data='{"text": "'+UserString+'", "username": "Python", "icon_emoji":":snake:"}')

while True:
    #Kijk 20 minuten geleden
    now = datetime.datetime.timestamp(datetime.datetime.now() - datetime.timedelta(minutes=20))
    
    #Zoek ArcGIS naar users, en sorteer ze op created date
    gebruikerslijst = agssite.users.search(query='!esri', max_users=15000)
    gebruikerslijst.sort(key=lambda x: x.created)

    #Voeg users gemaakt in de laatste 20 minuten toe aan alle groepen in de array van arcgis groepen
    for gebruiker in gebruikerslijst:
        #Chronomancy
        t = datetime.datetime.fromtimestamp(float(gebruiker.created)/1000.)
        createddate = t.strftime(fmt)

        #Doe alleen iets met users gemaakt in de laatste 20min
        if float(gebruiker.created/1000.) > now:
            # En alleen als ze NIET van een van onderstaande domeinen komen
            match = re.search(r'\b(joulz.nl|Joulz.nl|sg.stedingroep.nl)\b', str(gebruiker.email))
            if match:
                PostUserToSlack(str('\nNew user found! OTHER USER:  \t' + str(gebruiker.username) + "; \t" + str(gebruiker.level) + "; \t" + str(gebruiker.email) + "; \t" + str(createddate)))
                print('\nNew user found! \nOTHER USER:  \t' + str(gebruiker.username) + "; \t" + str(gebruiker.level) + "; \t" + str(gebruiker.email) + "; \t" + str(createddate))
            else:
                PostUserToSlack(str('\nI found a new user and added to groups. Its a STEDIN USER: \t' + str(gebruiker.username) + "; \t" + str(gebruiker.level) + "; \t" + str(gebruiker.email) + "; \t" + str(createddate)))
                print('\nNew user found! \nSTEDIN USER: \t' + str(gebruiker.username) + "; \t" + str(gebruiker.level) + "; \t" + str(gebruiker.email) + "; \t" + str(createddate))
                #Voeg ze toe aan groepen
                for group in groupList:
                    group.add_users(gebruiker)
                    print('\t\tUser ' + str(gebruiker.username) + " added to " + group.title)
    # Wacht 10min en doe het nogmaals
    time.sleep(600)

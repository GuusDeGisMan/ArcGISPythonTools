# ArcGISPythonTools
This repository contains my Python Tools that I use a lot for work related stuff relating to ArcGIS Enterprise

## NewUsersToGroups.py
This script is used to add users who joined up in the past ~20 minutes automatically to groups in an ArcGIS organisation (either Portal or Online), and then post a message about it to a Slack application by means of a webhook.

> Note: this script is used in Stedin. To accomodate local culture, comments and messages are written intermixed in Dutch, English, and [Nenglish](https://www.amazon.com/I-Always-Get-My-Sin/dp/9045305615). 

It uses the following imports:
* IPython - for Jupyter compatibility
* The [ArcGIS Python API](https://github.com/Esri/arcgis-python-api)
* Keyring
* Time
* re
* requests
* datetime

### What it does
It creates an array "grouplist" which consists of several group ID's from your previously configured ArcGIS Site (`agssite = GIS()`). Each append adds a single group. The Group ID is easily accessible from the URL of said group in your ArcGIS environment (wether it is online or an on-prem Enterprise).

```python
groupList = []
groupList.append(Group(agssite, '82221da5de0c4e14b7076762c25026cd'))        #Algemeen
groupList.append(Group(agssite, 'ba926e1a8ee44fc89cdd1c0f40e92194'))        #Elektra
groupList.append(Group(agssite, '3e31d72d56354e7d9f5f1358fdb9366f'))        #Gas
groupList.append(Group(agssite, '7242484284f6457daea06b1b03dbe15c'))        #Kaarten
groupList.append(Group(agssite, '62822382baef442b83e626b2dc6f7735'))        #Featured
```

After that, it uses chronomancy and epochs to determine the epoch as it was ~20 minutes ago (the script is an eternal loop with a rerun time of 10 minutes, using a 20 min window is a safe way to accomodate long running searches; in case of especially huge portals); and then uses the ArcGIS Search API + Python sorting to get a list of ArcGIS users sorted descending by date. As the ArcGIS Search API (which is a near must to create a list of users) does not as of yet has a known way to sort by user create date, this is the best way to work. On a ~1150 user large portal it takes roughly 0.3 seconds to complete the search.

It then iterates the users, and users that are found to be new, get added to all groups in the previously determined array; with a regular expression to exclude certain domains (handy in the case of self-enrolling multi-organisational portals):

```python
for group in groupList:
        group.add_users(gebruiker)
        print('\t\tUser ' + str(gebruiker.username) + " added to " + group.title)
```

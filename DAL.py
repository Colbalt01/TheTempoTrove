import requests
import json
import pymongo

myclient = pymongo.MongoClient("mongodb+srv://joeyk:SamDean@thetempotrove.nldybwy.mongodb.net/")
mydb = myclient["Data"]

headers = {
	"X-RapidAPI-Key": "6bce6bb485msh231417874be574ap1d6d68jsnfd0b0b35be1e",
	"X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
}
bandSearchUrl = "https://spotify-scraper.p.rapidapi.com/v1/artist/search"
searchUrl = "https://spotify-scraper.p.rapidapi.com/v1/search"
songSearchUrl = "https://spotify-scraper.p.rapidapi.com/v1/track/search"
concertUrl = "https://spotify-scraper.p.rapidapi.com/v1/artist/concerts"

mycolB = mydb["Bands"]
mycolA = mydb["Albums"]
mycolS = mydb["Songs"]
mycolUser = mydb["Users"]
mycolFav = mydb["Favorites"]
mycolConcert = mydb["Concerts"]

class DAL:
    def getData(url, querystring):
        response = requests.get(url, headers=headers, params=querystring)
        resjson = response.json()
        return resjson

    def insertBand(name, user):
        if(name != ""):
            bands = DAL.getAllBands()
            for band in bands:
                if band.get('name') == name:
                    return {}
            querystring = {"name":name}
            data = DAL.getData(bandSearchUrl, querystring)
            DAL.insertFavorite(user, name, "artist")
            inserted = mycolB.insert_one(data)
            print(inserted)
            return data
    
    def insertAlbum(name, albumName, user):
        if(name != ""):
            querystring = {"term":name,"type":"album"}
            album = {}
            albums = DAL.getAllAlbums()
            for a in albums:
                if a.get('name') == name:
                    return{}            
            data = DAL.getData(searchUrl, querystring)
            for a in data.get('albums').get('items'):
                if(a.get("artists")[0].get("name") == albumName and a.get("name") == name):
                    album = a
            if(album != {}):
                DAL.insertBand(albumName)
                DAL.insertFavorite(user, name, "album")
                inserted = mycolA.insert_one(album)
                print(inserted)
            return album
    
    def insertSong(name, songName, user):
        songs = DAL.getAllSongs()
        for song in songs:
            if song.get('name') == name:
                return {}
        if(name != "" and songName != ""):            
            DAL.insertBand(songName)
            querystring = {"name":name + " " + songName}
            data = DAL.getData(songSearchUrl, querystring)
            DAL.insertFavorite(user, name, "track")
            inserted = mycolS.insert_one(data)
            print(inserted)
            return data
    
    def insertUser(username, email, password):
        if(username != "" and password != "" and email !=""):
            user = {"username": username, "password":password, "email":email}
            inserted = mycolUser.insert_one(user)
            print(inserted)
            return user

    def insertFavorite(username, name, type):
        users = DAL.getUsers()
        item = {}
        for user in users:
            if (user.get('username') == username):
                if(type == "artist"):
                    item = DAL.getAllBands()
                elif(type == "album"):
                    item = DAL.getAllAlbums()
                elif(type == "track"):
                    item = DAL.getAllSongs()
                for i in item:
                    if(i.get("name") == name):
                        return False
                    itemFav = {"user":username, "name":name, "type":type}
                    inserted = mycolFav.insert_one(itemFav)
                    print(inserted)
                    return True
        return False

    def getAllBands():
        bands = []
        for x in mycolB.find():
            bands.append(x)
        # print(bands)
        return bands

    def getBands(i):
        bands = []
        e = 0
        for x in mycolB.find():
            if(e < i):
                bands.append(x)
                e = e + 1
        # print(bands)
        return bands

    def getAllAlbums():
        albums = []
        for x in mycolA.find():
            albums.append(x)
        # print(albums)
        return albums

    def getAlbums(i):
        albums = []
        e = 0
        for x in mycolA.find():
            if(e < i):
                albums.append(x)
                e = e + 1
        # print(albums)
        return albums

    def getAllSongs():
        songs = []
        for x in mycolS.find():
            songs.append(x)
        # print(songs)
        return songs

    def getSongs(i):
        songs = []
        e = 0
        for x in mycolS.find():
            if(e < i):
                songs.append(x)
                e = e + 1
        # print(songs)
        return songs
    
    def getUsers():
        users = []
        for u in mycolUser.find():
            users.append(u)
        return users

    def getBand(b):
        band = {}
        for x in mycolB.find({},{"_id": 0}):
            if(x.get('name') == b):
                band = x
            else:
                band = [False]
        return band 

    def getAlbum(a):
        album = {}
        for x in mycolA.find({},{"_id": 0}):
            if(x.get("name") == a):
                album = x
            else:
                album = [False]
        return album
    
    def getSong(s):
        song = {}

        for x in mycolS.find({},{"_id": 0}):
            if(x.get("name") == s):
                song = x
            else:
                song = [False]
        return song

    def getUser(u):
        user = {}
        for x in mycolUser.find({},{ "_id": 0, "username": 1, "email" : 1 }):
            if(x.get('username') == u):
                user = x
            # else:
            #     print(False)
        return user
    
    def favItem(fu, fi, type):        
        fUser = DAL.getUser(fu).get('username')
        favBU = {}
        if(type == "artist"):
            fBand = DAL.getBand(fi)
            if(fBand != [False]):
                favBU = {"user":fUser, "name":fBand.get('name'), "type": type}
        elif(type == "album"):
            fAlbum = DAL.getAlbum(fi)
            if(fAlbum != [False]):
                favBU = {"user":fUser, "name":fAlbum.get('name'), "type": type}
        elif(type == "track"):
            fSong = DAL.getSong(fi)
            if(fSong != [False]):
                favBU = {"user":fUser, "name":fSong.get('name'), "type": type}
        if(favBU != {}):
            inserted = mycolFav.insert_one(favBU)
            # print(favBU)
            print(inserted)
        else:
            print("something went wrong")
        return favBU

    def getFavorites(user):
        fav = []
        fUser = DAL.getUser(user)
        if(fUser != [] or user == ""):
            for f in mycolFav.find({}, {"_id": 0}):
                if (user == "" or f.get('user') == user):
                    fav.append(f)
            if(fav == []):
                print("no favorites")
        else:
            print("user not found")
        return fav

    def getConcerts():
        concerts = []
        for c in mycolConcert.find():
            concerts.append(c)
        return concerts

    def insertConcerts(user, location):
        # print(fUser)
        if(user == DAL.getUser(user).get("username")):
            for fav in DAL.getFavorites(user):
                for c in DAL.getConcerts():
                    cName = c.get('title').str.lower()
                    # if (cName != )
                b = DAL.getBand(fav.get("name"))
                querystring = {"artistId":b.get("id")}
                data = DAL.getData(concertUrl, querystring)
                for c in data.get("concerts"):
                    if (c.get("location") == location):
                        mycolConcert.insert_one(c)

# DAL.insertFavorite("Colbalt01", "In This Moment", "artist")
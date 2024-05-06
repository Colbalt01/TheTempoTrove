import requests
import json
import pymongo

myclient = pymongo.MongoClient("mongodb+srv://joeyk:SamDean@thetempotrove.nldybwy.mongodb.net/")
mydb = myclient["Data"]

headers = {
	"X-RapidAPI-Key": "6bce6bb485msh231417874be574ap1d6d68jsnfd0b0b35be1e",
	"X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
}

headersG = {
	"X-RapidAPI-Key": "6bce6bb485msh231417874be574ap1d6d68jsnfd0b0b35be1e",
	"X-RapidAPI-Host": "spotify23.p.rapidapi.com"
}

bandSearchUrl = "https://spotify-scraper.p.rapidapi.com/v1/artist/search"
searchUrl = "https://spotify-scraper.p.rapidapi.com/v1/search"
songSearchUrl = "https://spotify-scraper.p.rapidapi.com/v1/track/search"
concertUrl = "https://spotify-scraper.p.rapidapi.com/v1/artist/concerts"
relatedUrl = "https://spotify-scraper.p.rapidapi.com/v1/artist/related"
genreUrl = "https://spotify23.p.rapidapi.com/artists/"

mycolB = mydb["Bands"]
mycolA = mydb["Albums"]
mycolS = mydb["Songs"]
mycolUser = mydb["Users"]
mycolFav = mydb["Favorites"]
mycolConcert = mydb["Concerts"]
myColRelated = mydb["Related"]
myColGenre = mydb["Genres"]

class DAL:
    def getData(url, querystring):
        response = requests.get(url, headers=headers, params=querystring)
        resjson = response.json()
        return resjson

    def insertBand(name, user):
        if(name != ""):
            bands = DAL.getAllBands()
            for band in bands:
                if band.get('name').lower() == name.lower():
                    DAL.favItem(user, band.get('name'), "artist")
                    return {}
            querystring = {"name":name}
            data = DAL.getData(bandSearchUrl, querystring)
            mycolB.insert_one(data)
            DAL.favItem(user, band.get('name'), "artist")
            return data
    
    def insertAlbum(name, bandName, user):
        if(name != ""):
            querystring = {"term":name,"type":"album"}
            album = {}
            albums = DAL.getAllAlbums()
            bandName = bandName
            name = name
            for a in albums:
                if (a.get('name') == name):
                    return {}
            data = DAL.getData(searchUrl, querystring)
            for a2 in data.get('albums').get('items'):
                if (a2.get("artists")[0].get("name").lower() == bandName.lower() and a2.get("name").lower() == name.lower()):
                    print("everything works")
                    print(a2.get("artists")[0].get("name") + ": album name:" + bandName)
                    print(a2.get("name") + ": album name: " + name)
                    album = a2
            if(album != {}):
                mycolA.insert_one(album)
                DAL.favItem(user, album.get('name'), "album")
            return album
    
    def insertSong(name, bandName, user):
        songs = DAL.getAllSongs()
        for song in songs:
            if song.get('name').lower() == name.lower():
                return {}
        if(name != "" and bandName != ""):
            querystring = {"name":name + " " + bandName}
            data = DAL.getData(songSearchUrl, querystring)
            mycolS.insert_one(data)
            DAL.favItem(user, data.get('name'), "track")
            return data

    def insertUser(username, email, password):
        if(username != "" and password != "" and email !=""):
            user = {"username": username, "password":password, "email":email}
            mycolUser.insert_one(user)
            return user

    def getAllBands():
        bands = []
        for x in mycolB.find():
            bands.append(x)
        return bands

    def getBands(i):
        bands = []
        e = 0
        z = 0
        for x in mycolB.find().sort({ "$natural": -1 }).limit(i):
            z = z + 1
            if(e < i):
                bands.append(x)
                e = e + 1
        return bands

    def getAllAlbums():
        albums = []
        for x in mycolA.find():
            albums.append(x)
        return albums

    def getAlbums(i):
        albums = []
        e = 0
        for x in mycolA.find().sort({ "$natural": -1 }).limit(i):
            if(e < i):
                albums.append(x)
                e = e + 1
        return albums

    def getAllSongs():
        songs = []
        for x in mycolS.find():
            songs.append(x)
        return songs

    def getSongs(i):
        songs = []
        e = 0
        for x in mycolS.find().sort({ "$natural": -1 }).limit(i):
            if(e < i):
                songs.append(x)
                e = e + 1
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
                return x
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
        return user

    def favItem(fu, fi, type):        
        fUser = DAL.getUser(fu).get('username')
        favs = DAL.getFavorites(fu)
        favBU = {}
        print("Testing")
        for fav in favs:
            if(fav.get("name").lower() == fi.lower() and fav.get("username") == fu):
                print("No")
                return False
        if(type == "artist"):
            fBand = DAL.getBand(fi)
            print(fi, "Test")
            if(fBand != [False]):
                favBU = {"user":fUser, "name":fBand.get('name'), "type": type}
            else:
                print("band not in database")
        elif(type == "album"):
            fAlbum = DAL.getAlbum(fi)
            if(fAlbum != [False]):
                favBU = {"user":fUser, "name":fAlbum.get('name'), "type": type}
        elif(type == "track"):
            fSong = DAL.getSong(fi)
            if(fSong != [False]):
                favBU = {"user":fUser, "name":fSong.get('name'), "type": type}
        if(favBU != {}):
            mycolFav.insert_one(favBU)
        else:
            print("something went wrong")
        return favBU

    def getFavorites(user):
        fav = []
        fUser = DAL.getUser(user)
        if(fUser != [] or user == ""):
            for f in mycolFav.find({}, {"_id": 0}).sort({ "$natural": -1 }).limit(5):
                if (user == "" or f.get('user') == user):
                    fav.append(f)
            if(fav == []):
                print("no favorites")
        else:
            print("user not found")
        return fav
    
    def getAllFavorites(user):
        fav = []
        fUser = DAL.getUser(user)
        if(fUser != [] or user == ""):
            for f in mycolFav.find({}, {"_id": 0}).sort({ "$natural": -1 }):
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

    def insertConcerts(user, band, location):
        concerts = DAL.getConcerts()
        b = DAL.getBand(band)
        status = 0
        if(b == [False]):
            print("band not found")
            status = 2
            return status
        for c in concerts:
            if ('noConcerts' in c.keys() and band == c.get('band')):
                print(band + ": testing")
                status = 3
                return status
        for c in concerts:
            cBands = c.get('artists')
            if ('noConcerts' not in c.keys()):
                for cBand in cBands:
                    if(band == cBand.get("name") and location == c.get('location')):
                        print("found")
                    else:
                        querystring = {"artistId":b.get("id")}
                        data = DAL.getData(concertUrl, querystring)
                        if(data.get('concerts') != []):
                            for co in data.get("concerts"):
                                if (co.get("location") == location):
                                    print(co)
                                    mycolConcert.insert_one(co)
                                    status = 1
                                    return status
                                else:
                                    status = 4
                        else:
                            fCon = {"band":band, "noConcerts":True}
                            mycolConcert.insert_one(fCon)
                            status = 3
                            return status
        return status
    
    def insertRelated(bands):
        inDB = 0
        maxInDB = 0
        inDBItems = []
        relBands = []
        returnedR= []
        allDbReturned = []
        r = DAL.getRelated()
        for band in bands:
            maxInDB = maxInDB + 1
        for band in bands:
            b = DAL.getBand(band)
            for rel in r:
                if(rel.get('name') == b.get('name') and rel.get('name') == band):
                    # print("in DB")
                    inDB = inDB + 1
                    inDBItems.append(rel)
                    allDbReturned.append(rel)
                    # continue
                if(inDB == maxInDB):
                    print("All in DB")
                    # print(r)
                    # print(allDbReturned)
                    return allDbReturned
        if(inDB <=1):
            for inD in inDBItems:
                returnedR.append(inD)
                # print(inD)
                # print(any(r.get('name')==inD.get("name") for r in returnedR))
            # print("Some", returnedR)
        # print(returnedR)
        for band in bands:
            if(any(r.get('name')!=band for r in returnedR) or returnedR == []):
                print("Something")
                b = DAL.getBand(band)
                newRel = {"name":band}
                querystring = {"artistId":b.get("id")}
                data = DAL.getData(relatedUrl, querystring)
                print(returnedR, querystring)
                rBands = data.get('relatedArtists').get('items')
                i = 0
                for rBand in rBands:
                    if(i < 5):
                        relBands.append(rBand.get('name'))
                    i = i + 1
                newRel["bands"] = relBands
                returnedR.append(newRel)
                print(newRel)
                myColRelated.insert_one(newRel)
        return returnedR

    def getRelated():
        related = []
        for r in myColRelated.find({}, {"_id": 0}):
            related.append(r)
        return related
    
    def insertGenres(band):
        genresInDB = DAL.getGenres()
        for g in genresInDB:
            if(g.get('name') == band):
                return ""
        bandId = DAL.getBand(band).get('id')
        querystring = {"ids":bandId}
        response = requests.get(genreUrl, headers=headersG, params=querystring)
        data = response.json()
        genres = data.get('artists')[0]
        myColGenre.insert_one(genres)
        newGenresInDB = DAL.getGenres()
        return newGenresInDB

    def getGenres():
        genres = []
        for g in myColGenre.find({}, {"_id": 0, "genres": 1, "name":1}):
            genres.append(g)
        return genres
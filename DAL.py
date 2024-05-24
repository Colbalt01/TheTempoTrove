import requests
import json
import pymongo

myclient = pymongo.MongoClient("mongodb+srv://joeyk:SamDean@thetempotrove.nldybwy.mongodb.net/")
mydb = myclient["Data"]

headersM = {
	"X-RapidAPI-Key": "6bce6bb485msh231417874be574ap1d6d68jsnfd0b0b35be1e",
	"X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
}

headersG = {
	"X-RapidAPI-Key": "6bce6bb485msh231417874be574ap1d6d68jsnfd0b0b35be1e",
	"X-RapidAPI-Host": "spotify23.p.rapidapi.com"
}

bandInfoUrl = "https://spotify23.p.rapidapi.com/artist_overview/"
albumInfoUrl = "https://spotify23.p.rapidapi.com/album_metadata/"
songLyricUrl = "https://spotify23.p.rapidapi.com/track_lyrics/"
bandSearchUrl = "https://spotify-scraper.p.rapidapi.com/v1/artist/search"
searchUrl = "https://spotify-scraper.p.rapidapi.com/v1/search"
songSearchUrl = "https://spotify-scraper.p.rapidapi.com/v1/track/search"
concertUrl = "https://spotify-scraper.p.rapidapi.com/v1/artist/concerts"
relatedUrl = "https://spotify-scraper.p.rapidapi.com/v1/artist/related"
genreUrl = "https://spotify23.p.rapidapi.com/artists/"
AlbumTrackUrl = "https://spotify23.p.rapidapi.com/album_tracks/"

myColB = mydb["Bands"]
myColA = mydb["Albums"]
myColS = mydb["Songs"]
myColUser = mydb["Users"]
myColFav = mydb["Favorites"]
myColConcert = mydb["Concerts"]
myColRelated = mydb["Related"]
myColGenre = mydb["Genres"]
myColInfo = mydb["Info"]
myColLyrics = mydb["SongLyrics"]
myColAlbumTracks = mydb["AlbumTracks"]

class DAL:
    def getData(url, querystring):
        response = requests.get(url, headers=headersM, params=querystring)
        resjson = response.json()
        return resjson

    def insertBand(name, user):
        if(name != ""):
            bands = DAL.getAllBands()
            for band in bands:
                if band.get('name').lower() == name.lower():
                    DAL.favItem(user, band.get('name'), "artist", band.get('visuals'))
                    return {}
            querystring = {"name":name}
            data = DAL.getData(bandSearchUrl, querystring)
            myColB.insert_one(data)
            DAL.favItem(user, data.get('name'), "artist", data.get('visuals'))
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
                    DAL.favItem(user, a.get('name'), "album", a.get('cover'))
                    return {}
            data = DAL.getData(searchUrl, querystring)
            for a2 in data.get('albums').get('items'):
                if (a2.get("artists")[0].get("name").lower() == bandName.lower() and a2.get("name").lower() == name.lower()):
                    album = a2
            if(album != {}):
                myColA.insert_one(album)
                DAL.favItem(user, album.get('name'), "album", album.get('cover'))
            return album
    
    def insertSong(name, bandName, user):
        songs = DAL.getAllSongs()
        for song in songs:
            if song.get('name').lower() == name.lower():
                print(song)
                DAL.favItem(user, song.get('name'), "track", song.get('album'))
                return {}
        if(name != "" and bandName != ""):
            querystring = {"name":name + " " + bandName}
            data = DAL.getData(songSearchUrl, querystring)
            myColS.insert_one(data)
            DAL.favItem(user, data.get('name'), "track", song.get('album'))
            return data

    def insertUser(name, username, email, password):
        if(name != "" and username != "" and password != "" and email !=""):
            user = {"name":name, "username": username, "password":password, "email":email}
            myColUser.insert_one(user)
            return user

    def getBandInfo(name):
        for i in myColInfo.find({},{"_id": 0}):
            if(i.get('type') == "artist"):
                if(i.get('data').get('profile').get('name').lower() == name.lower()):
                    print("Band Inner loop")
                    return i
        id = DAL.getBand(name).get('id')
        querystring = {"id":id}
        print(querystring)
        response = requests.get(bandInfoUrl, headers=headersG, params=querystring)
        resjson = response.json().get('data').get('artist')
        info = {"type":"artist","data":{"id":resjson.get('id'),"profile":resjson.get('profile'),"visuals":resjson.get("visuals"),"stats":resjson.get("stats")}}
        result = myColInfo.insert_one(info)
        print(result)
        return info

    def getAlbumInfo(name):
        for i in myColInfo.find({},{"_id": 0}):
            if(i.get('type') == "album"):
                if(i.get('data').get('name').lower() == name.lower()):
                    print("Album Info Inner Loop")
                    return i
        id = DAL.getAlbum(name).get('id')
        querystring = {"id":id}
        response = requests.get(albumInfoUrl, headers=headersG, params=querystring)
        resjson = response.json().get('data').get('album')
        info = {"type":"album","data":{"id":id, "name":resjson.get('name'), "artists":resjson.get("artists"), "coverArt":resjson.get("coverArt"), "tracks":resjson.get("tracks")}}
        result = myColInfo.insert_one(info)
        print(result)
        return info

    def getAlbumTracks(name):
        for i in myColAlbumTracks.find({},{"_id": 0}):
            if(i.get('name').lower() == name.lower()):
                print("Album Info Inner Loop")
                return i
        album = DAL.getAlbum(name)
        id = album.get('id')
        querystring = {"id":id,"offset":"0","limit":"300"}
        print("Lyric Test")
        # response = requests.get(AlbumTrackUrl, headers=headersG, params=querystring)
        # resjson = response.json().get('data').get('album')
        # info = {"name":album.get('name'), "tracks":resjson.get('tracks')}
        # result = myColAlbumTracks.insert_one(info)
        # print(result)
        # return info

    def getSongLyrics(name):
        id = DAL.getSong(name).get('id')
        for s in myColLyrics.find({},{"_id": 0}):
            if(s.get('songId') == id):
                print("Lyric Inner Loop")
                return s
        querystring = {"id":id}
        print(querystring)
        response = requests.get(songLyricUrl, headers=headersG, params=querystring)
        resjson = response.json().get('lyrics')
        lyrics = {"songId":id,"lyrics":resjson.get('lines'), "provider":resjson.get('provider')}
        result = myColLyrics.insert_one(lyrics)
        print(result)
        return lyrics

    def getAllBands():
        bands = []
        for x in myColB.find():
            bands.append(x)
        return bands

    def getBands(i):
        bands = []
        e = 0
        z = 0
        for x in myColB.find().sort({ "$natural": -1 }).limit(i):
            z = z + 1
            if(e < i):
                bands.append(x)
                e = e + 1
        return bands

    def getAllAlbums():
        albums = []
        for x in myColA.find():
            albums.append(x)
        return albums

    def getAlbums(i):
        albums = []
        e = 0
        for x in myColA.find().sort({ "$natural": -1 }).limit(i):
            if(e < i):
                albums.append(x)
                e = e + 1
        return albums

    def getAllSongs():
        songs = []
        for x in myColS.find():
            songs.append(x)
        return songs

    def getSongs(i):
        songs = []
        e = 0
        for x in myColS.find().sort({ "$natural": -1 }).limit(i):
            if(e < i):
                songs.append(x)
                e = e + 1
        return songs
    
    def getUsers():
        users = []
        for u in myColUser.find():
            users.append(u)
        return users

    def getBand(b):
        band = {}
        for x in myColB.find({},{"_id": 0}):
            if(x.get('name').lower() == b.lower()):
                return x
            else:
                band = [False]
        return band

    def getAlbum(a):
        album = {}
        for x in myColA.find({},{"_id": 0}):
            if(x.get("name").lower() == a.lower()):
                return x
            else:
                album = [False]
        return album
    
    def getSong(s):
        song = {}
        for x in myColS.find({},{"_id": 0}):
            # print(x.get("name"), ": from DB S/", s, ": from input S")
            # print(x.get("name").lower() == s.lower(), ": getSong Test")
            if(x.get("name").lower() == s.lower()):
                return x
            else:
                song = [False]
        return song

    def getUser(u):
        user = {}
        for x in myColUser.find({},{ "_id": 0}):
            if(x.get('username') == u):
                user = x
        return user

    def favItem(fu, fi, type, visuals):
        fUser = DAL.getUser(fu).get('username')
        favs = DAL.getAllFavorites(fu)
        favBU = {}
        print(fi, "Test: ", type)
        for fav in favs:
            print(fav.get("name").lower(), ": testing 1: ", fi.lower())
            print(fav.get("name").lower() == fi.lower())
            print("")
            if(fav.get("name").lower() == fi.lower() and fav.get("user") == fu and fav.get("type").lower() == type.lower()):
                print("No", fav.get('name'))
                return False
        if(type == "artist"):
            fBand = DAL.getBand(fi)
            print(fBand, "Band test favItem")
            if(fBand != [False]):
                favBU = {"user":fUser, "name":fBand.get('name'), "type": type, "visuals":visuals}
        elif(type == "album"):
            fAlbum = DAL.getAlbum(fi)
            print(fAlbum, "Album test favItem")
            if(fAlbum != [False]):
                favBU = {"user":fUser, "name":fAlbum.get('name'), "type": type, "cover":visuals}
        elif(type == "track"):
            fSong = DAL.getSong(fi)
            print(fSong, "Song test favItem")
            if(fSong != [False]):
                favBU = {"user":fUser, "name":fSong.get('name'), "type": type, "album":visuals}
        if(favBU != {}):
            myColFav.insert_one(favBU)
        else:
            print("something went wrong favItem", fi)
        return favBU

    def getFavorites(user):
        fav = []
        fUser = DAL.getUser(user)
        if(fUser != [] or user == ""):
            for f in myColFav.find({}, {"_id": 0}).sort({ "$natural": -1 }).limit(5):
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
            for f in myColFav.find({}, {"_id": 0}).sort({ "$natural": -1 }):
                if (user == "" or f.get('user') == user):
                    fav.append(f)
            if(fav == []):
                print("no favorites")
        else:
            print("user not found")
        return fav

    def getConcerts():
        concerts = []
        for c in myColConcert.find():
            concerts.append(c)
        return concerts

    def getConcert(cName, cLocation):
        concerts = {}
        for c in concerts:
            if ('noConcerts' in c.keys() and cName == c.get('band')):
                status = 3
                return status
        for c in myColConcert.find({},{"_id":0}):
            if ('noConcerts' in c.keys()):
                continue
            cBands = c.get('artists')
            print(c)
            for cBand in cBands:
                if(cName.lower() == cBand.get("name").lower() and cLocation.lower() == c.get('location').lower()):
                    print("found")
                    return c
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
                print(c.get('band'), ": Don't hit")
                status = 3
                return status
        i = 0
        for c in concerts:
            cBands = c.get('artists')
            if ('noConcerts' not in c.keys()):
                for cBand in cBands:
                    i = i + 1
                    if(band.lower() == cBand.get("name").lower() and location.lower() == c.get('location').lower()):
                        print("found")
                        status = 4
                        return status
        querystring = {"artistId":b.get("id")}
        print("Don't hit")
        data = DAL.getData(concertUrl, querystring)
        if(data.get('concerts') != []):
            for co in data.get("concerts"):
                if (co.get("location") == location):
                    myColConcert.insert_one(co)
                    status = 4
                    return status
                else:
                    status = 5
        else:
            fCon = {"band":band, "noConcerts":True}
            myColConcert.insert_one(fCon)
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
                    inDB = inDB + 1
                    inDBItems.append(rel)
                    allDbReturned.append(rel)
                if(inDB == maxInDB):
                    print("All in DB")
                    return allDbReturned
        if(inDB <=1):
            for inD in inDBItems:
                returnedR.append(inD)
        for band in bands:
            if(any(r.get('name')!=band for r in returnedR) or returnedR == []):
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

    def getGenres():
        genres = []
        for g in myColGenre.find({}, {"_id": 0, "genres": 1, "name":1}):
            if(len(g.get('genres')) > 1):
                gLen = len(g.get('genres'))
                g.get('genres').remove(g.get('genres')[1])
            if(g.get('name') == "Asking Alexandria"):
                print(g)
            genres.append(g)
        return genres
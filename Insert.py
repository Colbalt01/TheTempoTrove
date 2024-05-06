import DAL
class input:
    def insertItem(band, album, song, user):
        print(band, album, song, user)
        if(album == "" and song == ""):
            DAL.DAL.insertBand(band, user)
        elif(album == ""):
            DAL.DAL.insertSong(song, band, user)
            DAL.DAL.insertBand(band, user)
        elif(song == ""):
            DAL.DAL.insertAlbum(album, band, user)
            DAL.DAL.insertBand(band, user)
        else:
            DAL.DAL.insertSong(song, band, user)
            DAL.DAL.insertAlbum(album, band, user)
            DAL.DAL.insertBand(band, user)
    
    def insertConcert(user, band, location):
        s = DAL.DAL.insertConcerts(user, band, location)
        return s
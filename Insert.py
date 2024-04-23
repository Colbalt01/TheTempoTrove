import DAL
class input:
    def insertItem(band, album, song, user):
        if(album == "" and song == ""):
            DAL.DAL.insertBand(band, user)
        elif(album == ""):
            DAL.DAL.insertSong(song, band, user)
        elif(song == ""):
            DAL.DAL.insertAlbum(album, band, user)
        else:
            print(band, album, song)
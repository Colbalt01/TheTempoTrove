import DAL
class input:
    def insertItem(band, album, song):
        if(album == "" and song == ""):
            DAL.DAL.insertBand(band)
        elif(album == ""):
            DAL.DAL.insertSong(song, band)
        elif(song == ""):
            DAL.DAL.insertAlbum(album, band)
        else:
            print(band, album, song)
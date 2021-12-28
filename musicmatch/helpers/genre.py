import  itertools, operator

def genreCategorize(genre):
    ''' helper function to organize the 1516 spotify
        genres into the ticketmaster umbrella genres '''
    if('pop' in genre):
        genre = "Pop"
    elif('rap' in genre):
        genre = "Hip-hop/Rap"
    elif('hip-hop' in genre):
        genre = "Hip-hop/Rap"
    elif('trap' in genre):
        genre = "Hip-hop/Rap"
    elif('drill' in genre):
        genre = "Hip-hop/Rap"
    elif('house' in genre):
        genre = "Dance/Electronic"
    elif('country' in genre):
        genre = "Country"
    elif("classical" in genre):
        genre = "Classical"
    elif('alt' in genre):
        genre = "Altenative"
    elif("indie" in genre):
        genre = "Alternative"
    elif("edm" in genre):
        genre = "Dance/Electronic"
    elif("dance" in genre):
        genre = "Dance/Electronic"
    elif("electronic" in genre):
        genre = "Dance/Electronic"
    elif("electric" in genre):
        genre = "Dance/Electronic"
    elif("dubstep" in genre):
        genre = "Dance/Electronic"
    elif('jazz' in genre):
        genre = "Jazz"
    elif("latin" in genre):
        genre = "Latin"
    elif("spanish" in genre):
        genre = "Latin"
    elif('metal' in genre):
        genre = "Metal"
    elif("rock" in genre):
        genre = "rock"
    elif("punk" in genre):
        genre = "rock"    
    elif("R&B" in genre):
        genre = "R&B"    
    elif("blues" in genre):
        genre = "R&B" 
    else:
        genre = "Other"

    #after assigning a renamed umbrella term return genre
    return genre


def genreListConsolidate(genre_list):
    ''' helper function to take a list of lists and 
        consolidate it into an ordered list in the
        ticketmaster genre umbrella terms rather than
        the spotify obnoxious ones '''

    #use the itertools.chain to conver the list of lists into a flat list
    flat_list = list(itertools.chain(*genre_list))

    # convert the flat_list of all the spotify genres into a dictionary with counts
    genres = {x:flat_list.count(x) for x in flat_list}

    # categorize each of the spotify genres into the umbrella terms and make a list
    genres_umbrella = [genreCategorize(spotify_genre) for spotify_genre in flat_list]

    # conver the list of the ticketmatster genres into a dictionary with counts
    genres = {x:genres_umbrella.count(x) for x in genres_umbrella}

    #sort the dictionary by counts and descending so highest occurence first
    sorted_genres = dict(sorted(genres.items(), key=operator.itemgetter(1),reverse=True))

    #get the keys which are the umbrella genres as a list and return them 
    genre_keys = list(sorted_genres.keys())

    return genre_keys

def compareGenres(self_genre, other_genre):
    ''' helper function that takes 2 people umbrella
        genres lists and creates a list of their 
        genres they have in common'''

    #lc through the self and add to both_genre only if in other_genre
    both_genre = [genre for genre in self_genre if genre in other_genre]

    #return the list with genres only in both peoples 
    return both_genre
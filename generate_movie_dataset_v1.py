#!/usr/bin/env python
# coding: utf-8
import os,sys
import numpy as np
from tqdm import tqdm
import pandas
import datetime
from imdb import IMDb
from mediawikiapi import MediaWikiAPI

mediawikiapi = MediaWikiAPI()
lists_of_films = mediawikiapi.page("Lists of films")
subpage_names = [subpage for subpage in lists_of_films.links if 'List of films:' in subpage]

lists_of_films = []
for subpage in subpage_names:
    try:
        page = mediawikiapi.page(subpage)
        lists_of_films.extend(page.links)
    except:
        e = sys.exc_info()[0]
        print(f"Error: {e} on {subpage}")
lists_of_films = np.asarray(lists_of_films)

def get_movie_info(movie_name):
    search_movie = ia.search_movie(movie_name)
    if search_movie:
        if search_movie[0]['kind'] in ['movie','video movie']:
            imdb_movie = ia.get_movie(search_movie[0].movieID)
        else:
            i=1
            try:
                while search_movie[i]['kind'] != 'movie':
                    i+=1
                imdb_movie = ia.get_movie(search_movie[i].movieID)
            except:
                return 0.0
        return imdb_movie
    else:
        return 0.0

# create an instance of the IMDb class
ia = IMDb()

interesting_parameters = ['title','genres','year','languages','votes','runtimes','rating']

def check_if_good_movie(imdb_movie):
    if isinstance(imdb_movie,float):
        return False
    elif any(ip not in imdb_movie.keys() for ip in interesting_parameters):
        return False
    else:
        if 'rating' in imdb_movie.keys():
            if imdb_movie['rating'] == 0.:
                 return False
        else:
            return False
        if 'runtimes' in imdb_movie.keys():
            if imdb_movie['runtimes'][0] == 0.:
                 return False
        else:
            return False
        if 'votes' in imdb_movie.keys():
            if imdb_movie['votes'] < 500.:
                 return False
        else:
            return False
    return True
def split_movie_name(movie_name):
    if '(film)' in movie_name:
        movie_name = movie_name.split('(film)')[0]
    elif ' film' in movie_name:
        movie_name = movie_name.split(' film)')[0] + ')'
    return movie_name

save_data_file = './Misc_Files/imdb_movie_selection_v1.npy'
save_slice = 100

if os.path.isfile(save_data_file):
    print('loading...')
    loaded_data = np.load(save_data_file,allow_pickle=True)
    movie_selection_text = pandas.DataFrame(loaded_data,columns=interesting_parameters)
else:
    movie_selection_text = pandas.DataFrame(data=None, index=None, columns=interesting_parameters, dtype=None, copy=False)

num_movies = 1000
rand_movies = [split_movie_name(mn) for mn in np.random.choice(lists_of_films,num_movies,replace=False)]
for i,movie_name in enumerate(tqdm(rand_movies)):
    imdb_movie = get_movie_info(movie_name)
    good_movie = check_if_good_movie(imdb_movie)
    while not good_movie:
        #If something went wrong with the movie, pick a different one
        rand_movies[i] = split_movie_name(np.random.choice(lists_of_films,1,replace=False)[0])
        imdb_movie = get_movie_info(rand_movies[i])
        good_movie = check_if_good_movie(imdb_movie)
    row_insert = {}
    for par in interesting_parameters:
        if par in imdb_movie.keys():
            if par in ['genres','director','languages']:
                row_insert[par] = str(imdb_movie[par][0])
            elif par in ['runtimes']:
                row_insert[par] = imdb_movie[par][0]
            else:
                row_insert[par] = imdb_movie[par]
        else:
            if par in ['title','genres','director','languages']:
                row_insert[par] = 'N/A'
            else:
                row_insert[par] = 0.
    if i == 0 and not os.path.isfile(save_data_file):
        movie_selection_text = pandas.DataFrame([row_insert])
    else:
        movie_selection_text = movie_selection_text.append(row_insert,ignore_index=True)
    if i%save_slice == 0 and i != 0:
        print('')
        print(f'Saving! i={i}')
        print('')
        np.save(save_data_file,movie_selection_text.to_numpy())

np.save(save_data_file,movie_selection_text.to_numpy())
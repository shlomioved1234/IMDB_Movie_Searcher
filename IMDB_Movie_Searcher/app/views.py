from flask import render_template, request, redirect
from flask import Flask
from app import app
from .forms import SearchForm
from bs4 import BeautifulSoup
from collections import OrderedDict
import requests
import json
import codecs

#Function that gets data from IMDB
def getJSON(html):
    data = {}
    #Finds the title of the movie
    data['title'] =  html.find(itemprop='name').text.strip()
    #Finds the Rating of the Movie out of 10
    data['rating'] = html.find(itemprop='ratingValue').text
    #Gives the Rating of the Movie (PG-13, R Rated, Etc.)
    data['rated'] = html.find(itemprop='contentRating')['content']
    #Finds the Genres of the Movie
    tags = html.findAll("span",{"itemprop":"genre"})
    genres = []
    for genre in tags:
        genres.append(genre.text.strip())
    data['genre'] = genres
    #Finds the Actors/Cast of the Movie
    tags = html.findAll(itemprop="actors")
    actors = []
    for actor in tags:
        actors.append(actor.text.strip().replace(',',''))
    data['cast'] = actors
    #Finds the Writers of Movie
    tags = html.findAll(itemprop="creator")
    creators = []
    for creator in tags:
        creators.append(creator.text.strip().replace(',',''))
    data['writers'] = creators
    #Finds the Director of the Movie
    directors = []
    tags = html.findAll(itemprop="director")
    for director in tags:
        directors.append(director.text.strip().replace(',',''))
    data['directors'] = directors
    #Returns the data from the function
    json_data = json.dumps(data)
    json_parsed=json.loads(json_data)
    return json_parsed

#Function that puts the URL through Beautiful Soup
def getHTML(url):
    response = requests.get(url)
    return BeautifulSoup(response.content,'html.parser', from_encoding="utf-8")

#Function that gets the URL
def getURL(input):
    try:
        if input[0] == 't' and input[1] == 't':
            html = getHTML('http://www.imdb.com/title/'+input+'/')
        
        else:
            html = getHTML('https://www.google.co.in/search?q='+input)
            for cite in html.findAll('cite'):
                if 'imdb.com/title/tt' in cite.text:
                    html = getHTML('http://'+cite.text)
                    break
        return getJSON(html)
    except Exception as e:
        return 'Invalid input or Network Error!'

#Function that gets movie data
def getMovie(movie):
    #Gets Data of the Movie
    parsed=getURL(movie)
    #Puts details of movie in dictionary
    d = {}
    try:
        d['Link']=getURLRaw(movie)
        #d['Image Link']=parsed['poster']
        d['Title']=parsed['title']
        d['Rating']= parsed['rating']
        d['Certification']= parsed['rated']
        d['Genre']= parsed['genre']
        jlist=[]
        for j in parsed['cast']:
            j = j.encode('ascii', 'ignore').decode('ascii')
            jlist.append(j)
        d['Cast']=jlist
        d['Directors']=parsed['directors']
        llist=[]
        for l in parsed['cast']:
            l = l.encode('ascii', 'ignore').decode('ascii')
            llist.append(l)
        d['Cast']=llist
        klist=[]
        for k in parsed['writers']:
            k = k.encode('ascii', 'ignore').decode('ascii')
            klist.append(k)
        d['Writers']=klist
    except (UnicodeEncodeError, TypeError, UnboundLocalError):
        pass
    return OrderedDict(d)

#Function that gets the URL RAW
def getURLRaw(input):
    try:
        if input[0] == 't' and input[1] == 't':
            html = getHTML('http://www.imdb.com/title/'+input+'/')
            htmlR = 'http://www.imdb.com/title/'+input+'/'
        
        else:
            html = getHTML('https://www.google.co.in/search?q='+input)
            for cite in html.findAll('cite'):
                if 'imdb.com/title/tt' in cite.text:
                    html = getHTML('http://'+cite.text)
                    htmlR = 'http://'+cite.text
                    break
        return htmlR
    except Exception as e:
        return 'Invalid input or Network Error!'

#Gets URL with Query in it
def url_for(string, query):
    return '/'+string+ '/'+ str(query)

#Gets link for image
def getImageLink(movie):
    link= getURLRaw(movie)
    response = requests.get(link)
    html = BeautifulSoup(response.content,'html.parser', from_encoding="utf-8")
    image = html.find(itemprop='image')['src']
    return image

#Routes Index Page
@app.route('/')
@app.route('/index')
@app.route('/index/')
def index():
    return render_template("index.html",
                           title='Home')

#Routes Search Page
@app.route('/search/', methods=['GET', 'POST'])
@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('search_results', query=form.search.data))
    return render_template("search.html",
                           title='Search',
                           form=form)

#Routes Result Page
@app.route('/search_results/<query>')
def search_results(query):
    results = getMovie(query)
    results = iter(results.items())
    image = getImageLink(query)
    return render_template("search_results.html",query=query,results=results, image=image)

#Routes About Page
@app.route('/about')
@app.route('/about/')
def about():
    return render_template("about.html",
                           title='About')





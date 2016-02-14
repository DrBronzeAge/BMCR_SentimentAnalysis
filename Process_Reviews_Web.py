# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 16:36:53 2015
The scripts here are intended to let you collect and begin processing academic
book reviews from the web. I have only made a minimal effort to generalize these
for other collections of academic book reviews, simply because it is difficult to 
anticipate some elements of web formatting. If you wish to use it on something other
than than the Brynn Mawr Classical Review, you'll need to configure some elements
yourself.

@author: Anonymous
"""

import bs4
import requests
import re
import pymongo



#
bmcrH='http://bmcr.brynmawr.edu/archive.html'
#page=bs4.BeautifulSoup(requests.get(bmcrH).text)
#links=[link.get('href') for link in page.find_all('a')]
#yr_arch=[link for link in links if re.search('[1-2][0-9]{3}',link)]
##simple fix for most recent year
#yr_arch[-1]='http://bmcr.brynmawr.edu/'+yr_arch[-1]

def findReviewLinks(home=bmcrH, Indexpattern='[1-2][0-9]{3}', 
                    Reviewpattern='[0-9][0-9].[0-9][0-9].html'):
    """Function for collecting the links to reviews. It is essentially
    a spider that is limited to two levels, and that only visits some of the links
    it finds.  The BMCR has a two level index-- one page of links that lead to 
    an index for each year.
    Home: a url passed as a string.  This will be the seed for your pseudo-spider
    Indexpattern: a (uncompiled) regular expression that will act as a filter for the
                links found on the home page. If you want the spider to visit all of
                those links rather than some of them, simply set this to '[a-zA-Z]'.
    Reviewpattern: another (uncompiled) regular expression.  Not all links on the
                page will be book reviews. This pattern is used to filter for only
                book reviews. Even if you are confident you have this pattern correct,
                you will almost certainly need to double-check the list of links
                before passing it to the parser function.

    """
    idp=re.compile(Indexpattern)
    rp=re.compile(Reviewpattern)
    
    page=bs4.BeautifulSoup(requests.get(home).text)
    firstlinks=[link.get('href') for link in page.find_all('a') if idp.search(link.get('href'))]
    
    secondlinks=[]
    for linky in firstlinks:
        page=bs4.BeautifulSoup(requests.get(linky).text)
        revs=[link.get('href') for link in page.find_all('a') if rp.search(link.get('href'))]
        secondlinks.extend(revs)
    return(secondlinks)
        

        
    
    
    
    


catalogue={}
def get_rev_links(page,catalogue):
    nmatch=re.compile('[1-2][0-9]{3}')
    name=nmatch.search(page).group(0)
    pattern='[0-9][0-9].[0-9][0-9].html'
    ind=bs4.BeautifulSoup(requests.get(page).text)
    
    revs=[link.get('href') for link in ind.find_all('a') if re.search(pattern, link.get('href'))]
    catalogue[name]=revs
    return (catalogue)

for year in yr_arch:
    get_rev_links(year, catalogue)
    
#Let's connect to the database, this assumes you already have a mongodb instance running
#and that it is running on the default port
#for help installing and setting up Mongodb, look here: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-windows/
#if you have it running on something other than the default port, you probably don't need my help.
    
client=pymongo.MongoClient() #start a client
db=client['bmcr'] #open the database
collection=db['reviews_raw'] #open the collection
    
link=catalogue['1998'][15]
ProblemChildren={}    
def process_review (link, ProblemChildren):
    page=bs4.BeautifulSoup(requests.get(link).text)
   
   
    #Let's get some basic identifying information
    try:
       stuff=[tag.text for tag in page.find_all('font')]
       keypat=re.compile('[1-2][0-9]{3}\.[0-1][0-9]\.[0-9]*')
       kstr=str([thing for thing in stuff if 'Bryn Mawr Classical Review' in thing])
       #we'll use this as a key
       keyNumber=keypat.search(kstr).group(0)
       #Could calculate it later, but can also use it as a checksum
       wc=str([thing for thing in stuff if "Word count" in thing])
       wpat=re.compile('[0-9]+')
       wCount=wpat.search(wc).group(0)
    
    except AttributeError:
        print("preliminaries failed for: ,",link)
        wCount='NA'
   
    
    #Let's try to find the reviewer's information
    try:
        revr=page.find_all('b')
        bingo=[str(tag) for tag in revr if "Reviewed by" in str(tag)][0]
        bingo=bingo.replace('<b>', '').replace('</b>','')
        rName=bingo.replace('Reviewed by','').split(',')[0].strip()
        rLoc=bingo.split(',')[1].strip()
    except AttributeError:
        print('Could not get reviewer info for: ',link)
        ProblemChildren[link]='Reviewer Info'
    #Let's get the Book's information
    try: 
        biblio=page.find('h3')
        book=biblio.find('i').text
        author=str(biblio).split('<i>')[0].replace('<h3>','')[0:-2] 
        #above is the best way to deal with the possibility of multiple authors
        #just take the stuff before the title begins
        bb=str(biblio)
        pubLoc=bb.split('</i>.')[1].split(':')[0].strip() #get publication info lazy way
        #by splitting on the trailing tag
        pubHouse=bb.split('</i>.')[1].split(':')[1].split(', ')[0].strip()
        yrpat=re.compile(', [1-2][0-9]{3}\.') #years easier to grab with regex
        pubYear=yrpat.search(bb.split('</i>.')[1]).group(0)[2:-1]
        #here we hit our first wrinkle-- what if prices are in a different currency?
        #pricestub=bb.split('$')[1].split('<')[0]
        ppat=re.compile('[0-9]*\.[0-9][0-9]\.')
        bookPrice=ppat.search(bb).group(0)[0:-1]
        pagpat=re.compile('Pp\. .*?[0-9]\.')
        bookPages=pagpat.search(bb).group(0)[3:-1].strip()
        
    except AttributeError:
        print('Book details failed for: ',link)
        problemChildren[link]="book Details"
    #Now the big one, Let's get the text of the review itself;
    #We'll worry about tokenizing and tagging it later.
    try:
        text=[p.text for p in page.find_all('p')]
    except:
        print("Couldn't get text for: ", link)
    
    #Stitch all these together then insert
    #open up the dict/json/bson object (whatever) for this review
    entry={'_id':keyNumber,
           'Link':link,
           "ReviwerName":rName,
           "ReviewerLocation":rLoc,
           "WordCount":wCount, 
           "Text":text,
           "BookAuthor":author, 
           "BookTitle":book, 
           "BookPubLocation":pubLoc,
           "BookPubHouse":pubHouse,
           "BookPubYear":pubYear, 
           "BookPrice":bookPrice,
           "BookPages":bookPages }
           
           
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #Last step: insert that object into the database
    collection.insert_one(entry)
           

    
        
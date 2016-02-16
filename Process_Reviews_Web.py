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
ProblemChildrenDefault={}    
#page=bs4.BeautifulSoup(requests.get(bmcrH).text)
#links=[link.get('href') for link in page.find_all('a')]
#yr_arch=[link for link in links if re.search('[1-2][0-9]{3}',link)]
##simple fix for most recent year
#yr_arch[-1]='http://bmcr.brynmawr.edu/'+yr_arch[-1]

def findReviewLinks(home=bmcrH, Indexpattern='http.*[1-2][0-9]{3}',Reviewpattern='http.*[0-9][0-9].[0-9][0-9].html'):
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
        

  

      
    
    
    
    


#catalogue={}
#def get_rev_links(page,catalogue):
#    nmatch=re.compile('[1-2][0-9]{3}')
#    name=nmatch.search(page).group(0)
#    pattern='[0-9][0-9].[0-9][0-9].html'
#    ind=bs4.BeautifulSoup(requests.get(page).text)
#    
#    revs=[link.get('href') for link in ind.find_all('a') if re.search(pattern, link.get('href'))]
#    catalogue[name]=revs
#    return (catalogue)
#
#for year in yr_arch:
#    get_rev_links(year, catalogue)
 
def OpenDBConnection(dbname='bmcr',collectionname='reviews_raw'):
    """Let's connect to the database, this assumes you already have a mongodb 
    instance running and that it is running on the default port for help 
    installing and setting up Mongodb, look here:
    http://docs.mongodb.org/manual/tutorial/install-mongodb-on-windows/
    if you have it running on something other than the default port, you probably 
    don't need my help and won't be running this function.
    dbname:  string-- filename for this database
    collectionname: string-- collection name for the database
    these will create a new db and collection if they don't already exist
    """   
    
    client=pymongo.MongoClient() #start a client
    db=client[dbname] #open the database
    collection=db[collectionname] #open the collection
    
    return(collection)


    
#link=catalogue['1998'][15]
#TODO: find a way to generalize this-- though there really isn't one.
def process_BMCreview (link, ProblemChildren=ProblemChildrenDefault):
    
   """
   Parse the web page of a book review into a loose schema
   and return a tuple (parsedReview, dictionary of bugs). Although the function
   is built on the assumption that you will be using MongoDB to store the data,
   it fills the schema with NA values where it fails to collect the real one. 
   It does this for two reasons: 1) Although you don't *need* it, having your 
   records follow a schema can make working with a MongoDB
   collection easier in some instances, and 2) a user may prefer to store this 
   information in a SQL database or simply populate a dataframe with some 
   elements for immediate rather than repeated use.
   
   Arguments:
   link: string-- pretty self-explanatory, but it is the url for the review you
   want to parse
   ProblemChildren: dict-- in case you want an easy way to keep track of links
                   that you failed to fully parse and why.  The idea is that you
                   keep sending it the same dict, or one that you have collected
                   from earlier test runs.
   Returns: (dict,dict)  The first element is the parsed review, the second is a
   dict containing a running list of link urls that failed to parse in some way.
   (in case the user wants to return later to fix incomplete entries)
   """
   
   page=bs4.BeautifulSoup(requests.get(link).text)
   try: 
        #if 'ISBN' in str(page.find_all('meta')):  #only bother to process reviews
        #different version to work with 1997 and 1998
        #if 'Pp' in str(page.find_all('meta')):
        #still even another fix for another formatting inconsistency
        revr=page.find_all('b')
        revr.extend(page.find_all('p'))
        revr.extend(page.find_all('h4'))
        monkey=str([tag.text for tag in revr])
        if 'Reviewed' in monkey:        #the BMCR contains a lot of things that 
            print('I am executing')     #are not reviews-- better to skip them
            #Let's get some basic identifying information
            try:
               stuff=[tag.text for tag in page.find_all('font')]
               if len(stuff) !=0:
                   keypat=re.compile('[1-2]?[09]?[019][0-9]\.[0-1]?[0-9]\.[0-9]*')
                   kstr=str([thing for thing in stuff if 'Bryn Mawr Classical Review' in thing])
                   #we'll use this as a key
                   keyNumber=keypat.search(kstr).group(0)
                   #Could calculate it later, but can also use it as a checksum
                   wc=str([thing for thing in stuff if "Word count" in thing])
                   wpat=re.compile('[0-9]+')
                   wCount=wpat.search(wc).group(0)
                   
               else:
                   title=str(page.find('title').contents)
                   keypat=re.compile('[1-2]?[0-9]?[019][0-9]\.[01]?[0-9]\.[0-9]*')
                   keyNumber=keypat.search(title).group(0)
                   wCount='NA'
                   
            
            except AttributeError:
                print("No Word Count for: ,",link)
                wCount='NA'
           
            
            #Let's try to find the reviewer's information
            try:
                revr=page.find_all('b')
                revr.extend(page.find_all('p'))
                #And this is why people hate you when you put manual formatting in your html.
                #this one only seen in 1997 and 1998, seemingly
                revr.extend(page.find_all('h4'))
                bingo=[str(tag.contents).replace('\\n',' ') for tag in revr if "Reviewed" in str(tag)][0]
                bingo=bingo.replace('<b>', '').replace('</b>','').replace("['", '').replace("']",'')
                sepr=','
                if '--' in bingo:
                    sepr='--'
                
                rName=bingo.replace('Reviewed by','').split(sepr,maxsplit=1)[0].strip()
                try:
                    rLoc=bingo.split(sepr, maxsplit=1)[1].strip()
                except IndexError:
                    rLoc="ProblematicFormat"+bingo
            except AttributeError or IndexError as e:
                print('Could not get reviewer info for: ',link,e)
                ProblemChildren[link]='Reviewer Info '+ str(e)
            #Let's get the Book's information
            try: 
                biblio=page.find_all('h3')
                for tag in biblio:
                    if "ISBN" in str(tag):
                        bingo=tag
                if bingo:
                    book=bingo.find('i').text
                    author=str(bingo).split('<i>')[0].replace('<h3>','')[0:-2] 
                #above is the best way to deal with the possibility of multiple authors
                #just take the stuff before the title begins
                    bb=str(bingo)
                try:
                    pubLoc=bb.split('</i>')[1].split(':',maxsplit=1)[0].strip() #get publication info lazy way
                    #by splitting on the trailing tag
                    pubHouse=bb.split('</i>',maxsplit=1)[1].split(':',maxsplit=1)[1].split(', ',maxsplit=1)[0].strip()
                except IndexError:
                    pubHouse="ProblematicFormat"+pubLoc
                try:
                    yrpat=re.compile('[1-2][019][0-9][0-9]\.') #years easier to grab with regex
                    pubYear=yrpat.search(bb.split('</i>',maxsplit=1)[1]).group(0)[2:-1]
                #here we hit our first wrinkle-- what if prices are in a different currency?
                #pricestub=bb.split('$')[1].split('<')[0]
                    pagpat=re.compile('Pp\. .*?[0-9]\.')
                    bookPages=pagpat.search(bb).group(0)[3:-1].strip()
                except IndexError:
                    pubYear,bookPages="ProblematicFormat"+pubLoc
                
            except AttributeError:
                print('Book details failed for: ',link)
                ProblemChildren[link]="book Details"
       # They don't all have prices, so we'll handle that on its own
            try: 
                ppat=re.compile('[0-9]*\.[0-9][0-9]')
                bookPrice=ppat.search(bb).group(0)[0:-1]
            except AttributeError:
                bookPrice='NA'
            #Now the big one, Let's get the text of the review itself;
            #We'll worry about tokenizing and tagging it later.
            try:
                text=[str(p.contents) for p in page.find_all('p')] #we want to keep the
                #<i> tags for ease of extracting entities, so we use p.contents, not p.text
            except:
                print("Couldn't get text for: ", link)
            
            #Stitch all these together then insert
            #open up the dict/json/bson object (whatever) for this review
            try:
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
                return(entry,ProblemChildren)
            except UnboundLocalError:
                ProblemChildren[link]='Execution Failed-- some value not found'
        
        else: 
            print(link+" probably isn't a review.")
            ProblemChildren[link]="Looks like it wasn't a review"
   except:
        print('Unknown error in '+link)
        ProblemChildren[link]="Unkown Error"
        
   return(None,ProblemChildren)
        
   
       



 
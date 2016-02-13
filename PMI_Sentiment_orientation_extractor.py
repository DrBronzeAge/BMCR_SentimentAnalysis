# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 18:13:24 2016
IR-PMI sentiment analysis engine (Stands for Information retrieval Pointwise
Mutual Information)
This is based on the work of Turney 2002 (http://www.aclweb.org/anthology/P02-1053.pdf)
which I mostly love because of it's brilliant laziness in calculating sentiment
orientation.  Once we've identified probable opinion phrases-- which here are mostly
target and modifier, we use number of hits on a search engine to give them a score
that is basically PMI with 'Excellent" and "Poor" in the corpus of the web.
actual equation works out to log2([phrase+excellent*allHitsPoor]/[phrase+poor*allHitsExcellent])
So brilliant. 
Perversely, Yahoo seems to work best for this. I think I'll substitute 'terrible'
for poor and see what happens
TODO: test to see whether restricting to domain:amazon.com or domain:goodreads.com
(which are mostly book reviews) produces more accurate results.  The general
web search ones seem to whiff on some easy ones.
@author: s
"""

import pymongo
import re
import pandas as pd
import nltk
import numpy as np
import requests
import bs4
import math


TreeBankTags={'adjective':re.compile('JJ'),'noun':re.compile('^NN$|NNS'),
              'adverb':re.compile('^RB$|RBS|RBR'), 'verb':re.compile('^VB$|VBD|VBN|VBG')}

cli=pymongo.MongoClient()
db=cli['bmcr']
revs=db['reviews_raw']

ff=revs.find_one({'Sentiments':{'$exists':True}})
sents=ff['Sentiments']
tsents=[s[2] for s in sents]


        


def MakeShingles(sent, shingleSize=3):
    """
    This one is pretty self-explanatory, but there's no need to clutter up the 
    matching function with it.  Expects a list of tuples, but can handle triples 
    that include a dictionary-applied sentiment label for a word, so long as the
    first and second elements are the word and the PosTag
    """
    shingles=[]
    for i in range (0,len(sent)-shingleSize):
        shingles.append(sent[i:i+shingleSize])
    return shingles



def Turney_matcher (shingle, tags=TreeBankTags):
    """
    Based on Turney 2002. These are the patterns that are most likely to be part
    of an opinion.  Will often be several in a sentence. I assume most people will
    use the treebank tags, but if not, just feed it a dict with entries that has
    as keys adjective,noun,adverb and verb, and the values should be compiled
    regular expressions that will match those tags
    The shingles need to be lists of three (word,tag) tuples, or triples as above.
    """
    adjective,noun,adverb,verb=tags['adjective'],tags['noun'],tags['adverb'],tags['verb']
    
    if adjective.match(shingle[0][1]) and noun.match(shingle[1][1]):
        return(shingle[0][0],shingle[1][0])
    if adjective.match(shingle[0][1]) and adjective.match(shingle[1][1]) and not noun.match(shingle[2][1]):
       return(shingle[0][0],shingle[1][0])
    if adverb.match(shingle[0][1]) and adjective.match(shingle[1][1]) and not noun.match(shingle[2][1]):
       return(shingle[0][0],shingle[1][0])
    if noun.match(shingle[0][1]) and adjective.match(shingle[1][1]) and not noun.match(shingle[2][1]):
        return(shingle[0][0],shingle[1][0])
    if adverb.match(shingle[0][1]) and verb.match(shingle[1][1]):
        return(shingle[0][0],shingle[1][0])
    return
    

def get_matches(sents, matcher=Turney_matcher):
    """
    
    """
    matches=[]
    for sent in sents:
        shingles=MakeShingles(sent)
        matches.append([matcher(shingle) for shingle in shingles if matcher(shingle)])
    return(matches)
    
#test=get_matches(tsents)

def Score_Phrase(phrase, Good='excellent', Bad='terrible',site=None, Ghits=None,Bhits=None):
    """
    TODO: Generalize this to accept other baseline terms (for good and bad)
    Accepts a two word list as input, output is a single float
    negative numbers indicate negative sentiment, positive numbers positive sentiment
    """
   
    searchbase='https://ca.search.yahoo.com/search?p='
    if site:
        searchbase='https://ca.search.yahoo.com/search?p=site%3'+site+'+'
    if not Ghits:
        Ghits=Get_Num_Hits(searchbase+Good)
    if not Bhits:
        Bhits=Get_Num_Hits(searchbase+Bad)
    searchurl=searchbase+'"'+phrase[0]+'+'+phrase[1]+'"'+'+'
    wBad=Get_Num_Hits(searchurl+'terrible')
    wGood=Get_Num_Hits(searchurl+'excellent')
    if wBad==None: #when restricted to a small domain, zeroes are a prob
        wBad=1
    if wGood==None:
        wGood=1
    eqtop=wGood*Bhits 
    eqbot=wBad*Ghits
    score=math.log2(eqtop/eqbot)
    return(score)

def Get_Num_Hits(url):
    nums=re.compile('[0-9,]+')
    page=bs4.BeautifulSoup(requests.get(url).text)
    narrow=page.find_all('span')
    goods=[tag for tag in narrow if tag.get('class')==None]
    for tag in goods:
        if 'results' in tag.text:
            hits=int(nums.match(tag.text).group(0).replace(',',''))
            return(hits)
            
def ReformExpandSentiments(sval):
    """
    Expects to be sent the "Sentiments" value from a the MongoDB record of a
    BMCR review, as it was created/inserted by the lexicon-based sentiment 
    analysis algorithm of sentimentAnalysisBMCR.py
    Decided to change it to a dictionary of sentences, each with named elements
    because accessing a specific element was getting to be a top-heavy headache
    """
    dictSent={}
    SentKeys=[k for k,v in enumerate(sval)]
    for key in SentKeys:
        dictSentV={}
        dictSentV['PlainText']=sval[key][1]
        dictSentV['TaggedTokens']=sval[key][2]
        dictSentV['SentScoreDict']=sval[key][0]
        #Okay, so the next one is terrible to read.  It's going to produce
        #a list of tuples that are (Phrase, sentiment score) for each sentence
        #get_matches expects a list of sentences, not a list of tokens, so that's
        #why there's an extra[] around sval[][]
        dictSentV['TurneyPhrasesWScores']=[(match,Score_Phrase(match)) for match in get_matches([sval[key][2]])[0] ]
        dictSent[key]=dictSentV
    return(dictSent)
        
        
class SentimentsInfo:
   
    def __init__(self,dbobj):
        self.LexiconScores=[dbobj[key]['SentScoreDict'] for key in sorted(dbobj.keys())]
        self.Turney=[dbobj[key]['TurneyPhrasesWScores'] for key in sorted(dbobj.keys())]
        self.TaggedTokens=[dbobj[key]['TaggedTokens'] for key in sorted(dbobj.keys())]
        self.SentencesPT=[dbobj[key]['PlainText'] for key in sorted(dbobj.keys())]
        #self.AllTurneyPhrases=[' '.join(p) for p,v in self.Turney]
#        self.TurneyScoredSentences=
#       
        def reviewScoreLexicon(self):
            return(sum(self.LexiconScores))
        def TurneyScoreSentence(sent):
            return(sum([v for f,v in sent]))
        def TurneyreviewScore():
            return(sum([TurneyScoreSentence(sent) for sent in self.Turney]))
        def TurneyPositives(sent,thresh=1):
            return([' '.join(p) for p,v in sent if v>=thresh])
        def TurneyNegatives(sent, thresh=-1):
            return([' '.join(p) for p,v in sent if v<=thresh])
        def AllTurneyPositives(self,thresh=1):
            return([TurneyPositives(sent,thresh) for sent in self.Turney])
        def AllTurneyNegatives(self,thresh=-1):
            retrun([TurneyNegatives(sent,thresh) for sent in self.Turney])
        def PositveLexiconSentences(self):
            return([(self.LexiconScores[i],self.SentencesPT[i]) for i in
            range(0,len(self.LexiconScores)) if LexiconScores[1]>0])
        def NegativeLexiconSentences(self):
            return([(self.LexiconScores[i],self.SentencesPT[i]) for i in 
            range(0,len(self.LexiconScores)) if LexiconScores[1]<0])
            
            
class IR_PMI_SentimentAnalyzer:
#TODO: genaralize this with **kwargs for other matching functions    
    """
    Class to actually perform the IR-PMI sentiment analysis. If you don't know,
    IR-PMI is the brilliantly lazy way to measure the sentiment orientation (how
    positive or negative something is) using the internet.  You use the number of 
    hits generated by a search engine for your term + some word meaning good, and
    your term + some word meaning bad.  The actual equation is:
    log2( (hits_for_term_with_good_word * hits_for_bad_word_only) / (term_with_bad * Good_only)  )
   
    Parameters 
    site-- if you want to restrict the search to a single site.  www.goodreads.com,
    www.epinions.com and www.amazon.com all show some upside.
    Good-- what single word or term do you want to use to mean 'i like this'
    Bad-- ditto but for 'I don't like this'
    matcher-- a function that finds 'sentiment phrases'  --words/combinations that
            are likely to be part of an opinion. The default one is from Turney.
    tags-- a dictionary where the keys are part of speech and the values are
            compiled regular expressions that match your POS tagging system
    """
    def __init__(self,site=None,Good='excellent',Bad='terrible',
                               matcher=Turney_matcher, tags=TreeBankTags):
        self.site=site
        self.Good=Good
        self.Bad=Bad
        self.matcher=matcher
        self.tags=tags
        searchbase='https://ca.search.yahoo.com/search?p='
        if self.site:
            searchbase='https://ca.search.yahoo.com/search?p=site%3'+self.site+'+'
        self.Ghits=Get_Num_Hits(searchbase+self.Good)
        if self.Ghits==None or self.Ghits<3000:
            print('You may want to consider a different combination of site/complimentary word.')
            print("'%s' only appears '%s' times on '%s'." %(self.Good, self.Ghits, self.site))
        self.Bhits=Get_Num_Hits(searchbase+self.Bad)
        if self.Bhits==None or self.Bhits<3000:
            print('You may want to consider a different combination of site/insulting word.')
            print("'%s' only appears '%s' times on '%s'." %(self.Bad, self.Bhits, self.site))
    
    def ScoreReview(self,tokenizedSents):
        
        matches=get_matches(tokenizedSents)
        output=[]
        for sent in matches:
            if sent!=[]:
                output.append([(match,Score_Phrase(match, Good=self.Good, 
                                Bad=self.Bad,site=self.site, Ghits=self.Ghits,
                                Bhits=self.Bhits)) for match in sent])
            else:
                output.append(None)
        
        return(output)
        
    def ScoreReviewBySentence(self, tokenizedSents):
        scored=ScoreReview(tokenizedSents)
        sentScores=[]
        for score in scored:
            if score==None:
                
        
            
pm=IR_PMI_SentimentAnalyzer()
outer=pm.ScoreReview(tsents)

output=[]
for sent in mats:
    if sent!=[]:
        output.append([(match,Score_Phrase(match, Good=pm.Good, 
                        Bad=pm.Bad,site=pm.site, Ghits=pm.Ghits,
                        Bhits=pm.Bhits)) for match in sent])
    else:
        output.append([])
        
Score_Phrase(mats[0][0], Good=pm.Good, 
                        Bad=pm.Bad,site=pm.site, Ghits=pm.Ghits,
                        Bhits=pm.Bhits)
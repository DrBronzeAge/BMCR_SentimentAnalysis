# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 14:34:56 2015
A Sentiment Analysis engine for Book reviews on the Brynn Mawr Classical Review.
It was inspired by this: 
http://fjavieralba.com/basic-sentiment-analysis-with-python.html
I scraped the book reviews from the web (http://bmcr.brynmawr.edu/), processed
them a little bit and made a database of them in MongoDB.
This feeds on the raw text of those reviews.  It only calculates a score for
each sentence. It's trivial to sum the scores of the sentences when I want them,
and being able to quickly select sentences that are 'positive' or 'critical' is
more useful for my research.
@author: Chris
"""

import nltk
import pymongo
#import re
import pickle
import numpy as np
import pandas as pd
#from ProcessBMCRStepTwo import stringify

#get our dictionary of sentiment words
#kept in a separate file for ease

with open('sentimentWords.pickle', 'rb') as f:
    diction = pickle.load(f)

#we'll need these later
frog=nltk.corpus.stopwords.words('french')
kraut=nltk.corpus.stopwords.words('german')
wasp=nltk.corpus.stopwords.words('english')
    
cli=pymongo.MongoClient()
db=cli['bmcr']
revs=db['reviews_raw']

#foo=revs.find_one()['Text']  #just reminding myself of the structure of these

def stringify(text):
    """
    The only meaningful input is the value of 'Text' for an object in the 
    BMCR.reviews_raw database.
    Output is a single string.
    Since Beautiful Soup had some trouble with the inconsistent formatting
    of the BMCRs, there's often a lot of html junk still in the text of the 
    reviews Also, the reviews are stored as a list of paragraphs, when for NLP 
    it makes more sense to have a single string.
    """
    tqt=""
    for p in text:
        tqt+=p
    tqt=tqt.replace('[','').replace(']','').replace("\\n", ' ') #get rid of some artefacts
    tqt=tqt.replace("\\\/",' ').replace("\\",' ') #clear out some exta slashes
    return(tqt)


def TagForSentiment(word_tuple, dictionary=diction):
    """
    Input is a tuple (word, POS_tag) i.e. "Part of Speech" tag.
    Returns a single string to indicate what kind of sentiment the word conveys
    
    This function checks the first element of the tuple (word_tuple) against a 
    dict of domain-specific keywords (dictionary).
    If found, it returns that word's value ('positive','negative','increment','
    'decrement' or 'invert')
    Normally called iteratively against each word_tuple in a sentence (list).
    """
    word=word_tuple[0].lower()
    if word in dictionary.keys():
        return(dictionary[word])
    return('neutral') #if not in dictionary, word assumed to be neutral
    
def ScoreSentence(sent):
    """
    Input is a list of threeples (word,POS_tag,sentiment value)
    Output is a single float, most often 0.0
    Default assumption is that this is a sentence that has been word-tokenized,
    POS tagged and fed through TagForSentiment
    Function called iteratively against each sentence in a review
    """
    tot_score=0.0
    marker=0
    for a in range(0,len(sent)):
        if sent[a][2]=='positive':
            score=1.0
            #dont wantthe whole sentence (they're very long & hypotactic), 
            #just a window around the word in question
            for word in sent[max(marker, a-5):min(a+2, len(sent))]: 
                if word[2]=='increment':
                    score*=2.0
                if word[2]=='decrement':
                    score/=2.0
                if word[2]=='invert':
                    score*=-1.0
            marker=a
            tot_score+=score
        if sent[a][2]=='negative':
            score=-1
            for word in sent[marker:min(a+2, len(sent))]:
                if word[2]=='increment':
                    score*=2.0
                if word[2]=='decrement':
                    score/=2.0
                if word[2]=='invert':
                    score*=-1.0
            marker=a
            tot_score+=score
    return tot_score



def testLanguage(sample,frog=frog, kraut=kraut, wasp=wasp):
    """
    Simple function to test the language of a document
    Inputs are a string, and lists of stopwords
    Returns a string that indicates language
    
    We're usually only interested in documents in English
    
    """
    franco=len([w for w in sample if w.lower() in frog])
    prussian=len([w for w in sample if w.lower() in kraut])
    war=len([w for w in sample if w.lower() in wasp])
    if war==max(franco,prussian,war):
        return('ENG')
    if franco==max(franco,prussian,war):
        return('FRE')
    if prussian==max(franco,prussian,war):
        return('GER')
    return('Inconcievable!!!!!')



def DoSentAnalysis(doc):
    """
    Input is assumed to be a document from the BMCR.reveiws_raw database
    although it would work on any dict-like object with a field called 'Text'.
    Output is either False (only happens with documents in languages other than
    English), or a list of threeples: 1) Float(score),2)Sentence, as a single,
    string, 3) sentence as a list of (word, POS_tag, sentiment_value) tuples
    It's big, but the tokenization and POS_tagging is by far the most 'expensive'
    part of the process. So I was happy to trade a few MB of hard-disk space for
    never having to run it again.
    """
    sents1=nltk.sent_tokenize(stringify(doc['Text']))
    wsents=[nltk.word_tokenize(sent) for sent in sents1] 
    #pause here so we dont' bother pos tagging non-english reviews
    #send to check language
    smp=[]
    for sent in wsents:
        smp.extend([w for w in sent])
    if testLanguage(smp)=='ENG':
        sents=[nltk.pos_tag(sent) for sent in wsents]
        #~8 seconds to run, on average
        sentThreep=[([(tup[0],tup[1],TagForSentiment(tup)) for tup in sent])
        for sent in sents] 
        sentFinal=[(sent,ScoreSentence(sent)) for sent in sentThreep]
        return([(sentFinal[ct][1],sents1[ct],sentFinal[ct][0]) for ct in 
        range(0,len(sentFinal))])
        #this is big, but the tokenization algorithm is the most expensive part
        #not needing to run it again if I want to change anything or do
        #something else with it is worth a few mb of HD space
    return (False)


def CalcFScore(RealSet,TestSet):
    """
    Function that calculates precision and recall for the sentiment analysis 
    engine.
    Input is two lists of floats (or mix of ints and floats), both of which are
    the scores for a randomly drawn sample of sentences/reviews.
    TestSet is the scores assigned by the machine, RealSet are the scores
    (normally assigned by a domain expert, i.e. me) against which they'll be
    checked.
    Returns a list of 6 numbers: True positives, False Positives and 
    False Negatives for Positive sentiments and Negative sentiments respectively
    Those can be used to calculate precision and recall, and hence f-score

    """
    pos=[] #both will be filled with a lot of true negatives (TN), some True Positives(TP)
    neg=[] #also False Negatives(FN) and False Positives(FP)
    for i in range(0,min(len(RealSet),len(TestSet))):
        r,t=RealSet[i],TestSet[i]
        if r>=0.5:
            if t>=0.5:
                pos.append('TP')
                neg.append('TN')
            if t==0.0:
                pos.append('FN')
                neg.append('TN')
            if t<=-0.5:
                pos.append('TN')
                neg.append('FN')
        if r==0.0:
            if t>=0.5:
                pos.append('FP')
                neg.append('TN')
            if t==0.0:
                pos.append('TN')
                neg.append('TN')
            if t<=-0.5:
                pos.append('TN')
                neg.append('FP')
        if r<=-0.5:
            if t>=0.5:
                pos.append('FP')
                neg.append('TN')
            if t==0.0:
                pos.append('TN')
                neg.append('FN')
            if t<=-0.5:
                pos.append('TN')
                neg.append('TP')
        Ptp=[p for p in pos if p=='TP']
        Pfp=[p for p in pos if p=='FP']
        Pfn=[p for p in pos if p=='FN']
        Ftp=[p for p in neg if p=='TP']
        Ffp=[p for p in neg if p=='FP']
        Ffn=[p for p in neg if p=='FN']
        
        #for reasons I don't see at the moment, these work fine in the interpreter
        #but become division by zero errors when run in the function.
        #Not enough of a hassle to worry about fixing it for now
#        PP=len(Ptp)/(len(Ptp) + len(Pfp))
#        PR=len(Ptp)/(len(Ptp) + len(Pfn)) 
#        NP=len(Ftp)/(len(Ftp) + len(Ffp))
#        NR=len(Ftp)/(len(Ftp) + len(Ffn))      
#        return ([PP,PR,NP,NR])
        #for now, just return the raw numbers
        return([len(Ptp),len(Pfp),len(Pfn),len(Ftp),len(Ffp),len(Ffn)])


####################################################################
#Code below here was only used as I refined the sentiment analysis engine
###################################################################

#keys=revs.distinct('_id')
#testkeys=np.random.choice(keys, 5) 
#goldens=pd.DataFrame(columns=["TrueScore","Sentence","Score"])
#foo=[]
#bar=[]
#for key in testkeys:
#    thing=DoSentAnalysis(revs.find_one({'_id':key}))
#    if thing:
#        foo.extend([s for n,s,t in thing]) #sentence in plain text
#        bar.extend([n for n,s,t in thing])#score assigned to that sentence

#goldens['Sentence']=foo
#goldens['Score']=bar
##'TrueScore will be done by hand
#goldens.to_csv('goldenSetForSA.csv')
##done by hand, now read it back in
#gs=pd.read_csv('truscore.csv',encoding='UTF-8')
#goldens['TrueScore']=gs['TrueScore']
##save some edits
#gs['TrueScore']=goldens['TrueScore']
#gs.to_csv('truscore2.csv')

#3scores=CalcFScore(goldens['TrueScore'],goldens['Score2'])
##Positive Precision, Recall= 0.65, 0.68
##Negative Precision, Recall= 0.76,0.60
#re-run the above code with pared dictionary

########################################################################
#Code below this was only used once, to actually do the sentiment analysis
#and update the database
#Since POS tagging was the hold-up, but only used one processor core,
#I split the set of keys in two and ran two threads in parallel
########################################################################
#keys=revs.distinct('_id')
#
#keys1=keys[0:4400]
#keys2=keys[4400:]
#count=0
#for key in keys1:
#    record=revs.find_one({'_id':key})
#    goods=DoSentAnalysis(record)
#    if goods:
#        revs.update_one({'_id':key},{'$set':{'Sentiments':goods}})
#        print("Updated: ",record['BookTitle'])
#    count+=1
#    print(count) 
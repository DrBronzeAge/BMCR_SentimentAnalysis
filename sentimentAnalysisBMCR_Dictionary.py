# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 14:34:56 2015
A Sentiment Analysis engine for Book reviews on the Brynn Mawr Classical Review.
It was inspired by this: 
http://fjavieralba.com/basic-sentiment-analysis-with-python.html
This module assumes that you are me, and that you have already scraped ~9000
book reviews from the web (http://bmcr.brynmawr.edu/), processed
them a little bit and made a database of them in MongoDB. If you aren't me (or
haven't run the rest of the code for this project) the Sentiment_Analyzer
class will accept the raw text of any book review. It only calculates a score for
each individual sentence.  The default dictionary was made by an expert in book 
reviews on Ancient History and Classics. If you are applying it to reviews of 
books in another discipline, you may need to revise it.
@author: Anonymous
"""

import nltk
import pymongo
#import re
import pickle
import numpy as np
import pandas as pd
import yattag
from yattag import doc
#from ProcessBMCRStepTwo import stringify



with open('sentimentWords.pickle', 'rb') as f:
    diction = pickle.load(f)
"""
retrieve the default sentiment dictionary
"""

frog=nltk.corpus.stopwords.words('french')
kraut=nltk.corpus.stopwords.words('german')
wasp=nltk.corpus.stopwords.words('english')
"""
Module level variables-- we need them for language tests
"""

  
#cli=pymongo.MongoClient()
#db=cli['bmcr']
#revs=db['reviews_raw']

"""
Start a connection to the database
TODO: maybe call the openDBConnection function instead
"""

class Sentiments(Outputlist):
    """Container Class for the output of the Sentiment Analysis.
    
       It should only get called in conjunction with the do_analysis()
       method of the SentimentAnalyzer class.
       
       Arguments:
       Outputlist (list)-- this is a list of threeples as below
       (sentiment score,plaintextOfSentence,[TaggedTokens]).
    """
    def __init__(self, Outputlist):
        self.sentiments=Outputlist
        self.PlainText=[P for S,P,T in Outputlist]
        self.Scores=[S for S,P,T in Outputlist]
        self.Tokens=[T for S,P,T in Outputlist]    
        self.OverallScore=sum(self.Scores)
        self.Praise=[(S,P) for S,P,T in Outputlist if S>0]
        self.Blame=[(S,P) for S,P,T in Outputlist if S<0]
        
    def StoreInMongoDB(self,reviewdb=revs,quer,AttName='Sentiments'):
        """
        Update a record in a MongoDB collection.
        
        
        Another method that assumes you're me. This will append the sentiments
        to the MongoDB record for the review they came from.
        
        Arguments:
        reviewdb(connection)-- this is actually a connection to a specific
        collection within the database.
        
        quer-- a query that will lead you to the correct record. Will often
        be of the form:
        
            quer={'_id':uniqueIDofThisReview}
        
        AttName(str)-- What will this attribute be called? Save yourself
        heartache and be consistent if you decide to change the default.
        
        """
        try:
            reviewdb.update_one(quer,{'$set':{ObjectName:self.sentiments}})
            print('Database successfully Updated')
        except:
            #TODO: Add specialized error messages with hints for how to solve
            #common problems.
            print("You are not me. I can't diagnose your database problem.")


class SentimentAnalyzer(dictionary=diction):
    """This class contains all of the functions necessary to both fine-tune
    your sentiment dictionary, and to actually perform the analysis at scale. 
    For now, it assumes that users will make additions/subtractions/changes to
    the sentiment dictionary manually.
    The only parameter the class needs to initialize is a dictionary where the
    keys are 'Sentiment Words' like 'excellent' or 'terrible' and the values are
    strings from the set{'positive','negative','increment','decrement','invert'}.
    
    Arguments:
        dictionary(dict)-- a dict where the keys are words and the values are
        their sentiment orientation (as above).
    
    """
    def __init__(self, dictionary):
        self.D=self.dictionary
    #Todo implement a testAccuracy method
    def TestAccuracy(self, GoldenSet):
        
        """
        Calculates the accuracy of your sentiment analyzer, returns a list.
        
        
        Call this method to begin calculating the accuracy (F1 Score) of the
        current instance of the sentiment analyzer. The process requres the user
        to provide accurate scores for each sentence in a 'Golden Set'. If the
        user has some pre-scored sentences, great. If not, there will be a
        method implemented below to make the process easier.  Just as a warning,
        if you plan to adjust your sentiment dictionary based on problems that 
        emerge in this test, you will need to provide an entirely different 
        'GoldenSet' to run the test again, at least if you are actually interested
        in measuring general performance.
        
        Arguments:
        Goldenset(list)--The golden set should be a list of tuples:
        [(PlaintTextSentence (str), TrueScore(float--usually between -2 and +2))]
        
        Returns:
        A list of six numbers: F1 score for compliments and Criticisms,
        precision and recall for both of those respectively. Also prints values
        to console with labels.
        """
        GoldenScores=[ts for s,ts in GoldenSet]
        TestFodder='  '.join([s for s,ts in GoldenSet])
        RealSet=[S for S,P,T in DoSentAnalysis(TestFodder)]
        if len(RealSet)!=len(GoldenSet):
            return("Could not calculate F score; Number of Sentences in GoldenSet"+
            ' and Test Set do not match')
        return(CalcFScore(GoldenScores,RealSet))
    
    def AnalyzeReview(self,review):
        """
        Method to actually do the analysis. 
        
        It just calls several of the functions
        below. Parameters are the self.D (sentiment dictionary) and the plaintext
        of a review (or reviews, really.  I wouldn't want to join them all into
        one and keep them in a big bag, but if someone else does they can.)
        
        review: string
        
        returns: Either False (if the review is in a languageother than English)
                 or a list of threeples(score, sentence, tokenized_sentence)
                 
        
        """
        return(DoSentAnalysis(review, self.D))
    
        
    #TODO implement a method to quickly generate a 'GoldenSet' for testing accuracy
    
    def GenerateGoldenSet_FullReviews (self, reviews ):
        reviews='     '.join(reviews)
        sents=nltk.sent_tokenize(reviews)
        
    
        
    

#foo=revs.find_one()['Text']  #just reminding myself of the structure of these

def stringify(text):
    """
    Turns a review into a single string.
    
    The only meaningful input is the value of 'Text' for an object in the 
    BMCR.reviews_raw database.
    Output is a single string.
    Since Beautiful Soup had some trouble with the inconsistent formatting
    of the BMCRs, there's often a lot of html junk still in the text of the 
    reviews Also, the reviews are stored as a list of paragraphs, when for NLP 
    it makes more sense to have a single string.
    
    Arguments:
    text(list)-- a list of things that were in <p> tags in a review.
    """
    tqt=""
    for p in text:
        tqt+=p
    tqt=tqt.replace('[','').replace(']','').replace("\\n", ' ') #get rid of some artefacts
    tqt=tqt.replace("\\\/",' ').replace("\\",' ') #clear out some exta slashes
    return(tqt)


def TagForSentiment(word_tuple, dictionary=diction):
    """
    Assigns a sentiment value to a word. Returns a string.
    
    
    This function checks the first element of the tuple (word_tuple) against a 
    dict of domain-specific keywords (dictionary).
    If found, it returns that word's value ('positive','negative','increment','
    'decrement' or 'invert').  If not found, returns 'neutral'.
    Normally called iteratively against each word_tuple in a sentence (list).
      
      >>>sentValues=[(word, POS_tag, TagForSentiment(word,POS_tag)) for 
              word,POS_tag in TokenizedSentence]
    
    Arguments:
    word_tuple(tuple)-- a word and it's POS_tag  i.e. "Part of Speech" tag.
    
    dictionary(dict)-- a sentiment dictionary (words and their sentiment values)
    
    Returns:
    a single string to indicate what kind of sentiment the word conveys.
    
    """
    word=word_tuple[0].lower()
    if word in dictionary.keys():
        return(dictionary[word])
    return('neutral') #if not in dictionary, word assumed to be neutral
    
def ScoreSentence(sent):
    """
    Calculate the sentiment score for a sentence, return a float.
    
    Takes a sentence that has already been tagged for sentiment and calculates
    the sentence's overall score. It makes some effort to consider phrases, rather
    than sentences as it does it's arithmetic.  That is, a positive value in
    word one possibly shouldn't be inverted because word twenty has a value of
    'invert' and so on.  The nature of the calculation sometimes produces very
    high/low numbers. You may want to a apply a cieling to them before you start
    your actual analysis.
    
    
    Arguements:
    sent (list)--a list of threeples (word,POS_tag,sentiment value)
    
    Returns:
    Output is a single float, most often 0.0
    
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
    Checks the language of a review.  Returns a string
    
    Simple function to test the language of a document
    Inputs are a string, and lists of stopwords
    Returns a string that indicates language
    We're usually only interested in documents in English
    
    Arguments:
    sample(list)-- a bag of words from the review (can be the whole review)

    frog (list)-- a list of common French words (usually stopwords)
    
    kraut(list)-- a list of common German words (ditto)
    
    wasp(list)-- a list of common English words (ditto)
    
    
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



def DoSentAnalysis(doc,dictionary=diction):
    """
    Analyze a review + assign a sentiment score to each sentence. Returns list.    
    
    This function pulls the Text of a review out of a database record or
    similar object, cleans it up a little, then tokenizes (splits into words) 
    it. If the text is in English, it applies POS_tags then calculates a 
    Sentiment score for each sentence.
    
    Arguments:
    
    doc-- is assumed to be a document from the BMCR.reveiws_raw database,
    although it would work on any dict-like object with a field called 'Text'.
    It is assumed that that field is a list.
    
    Returns
    Output is either None (only happens with documents in languages other than
    English), or a list of threeples: 1) Float(score),2)Sentence, as a single,
    string, 3) sentence as a list of (word, POS_tag, sentiment_value) tuples
    
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
        sentThreep=[([(tup[0],tup[1],TagForSentiment(tup,dictionary=dictionary)) for tup in sent])
        for sent in sents] 
        sentFinal=[(sent,ScoreSentence(sent)) for sent in sentThreep]
        return([(sentFinal[ct][1],sents1[ct],sentFinal[ct][0]) for ct in 
        range(0,len(sentFinal))])
        #this is big, but the tokenization algorithm is the most expensive part
        #not needing to run it again if I want to change anything or do
        #something else with it is worth a few mb of HD space
    return (None)


def CalcFScore(RealSet,TestSet):
    """
    Calculates accuracy for the sentiment analysis engine.  Returns list.
    
    
    F1 Score is the harmonic mean of precision (ratio of true positives to all
    cases labled positive) and recall (ratio of cases labled positive to all
    things that should be positive)
    This function calculates separate F1 scores (and components) for sentences
    which praise a book and sentences which criticise it.
    
    Arguments
    RealSet (list)-- a list of floats which are the verified correct scores for
        a series of sentences.
        
    TestSet (list)-- a list of floats which are the scores assigned by the
    sentiment analysis engine.
    
    Returns:
     A list of six numbers: F1 score for compliments and Criticisms,
     precision and recall for both of those respectively. Also prints values
     to console with labels. 
    """
    pos=[] #both will be filled with a lot of true negatives (TN), some True Positives(TP)
    neg=[] #also False Negatives(FN) and False Positives(FP)
    for i in range(0,min(len(RealSet),len(TestSet))):
        r,t=RealSet[i],TestSet[i]
#        print([r,t])
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
                
    Praise_true_p=len([p for p in pos if p=='TP'])
    Praise_false_p=len([p for p in pos if p=='FP'])
    Praise_false_n=len([p for p in pos if p=='FN'])
    Blame_true_p=len([p for p in neg if p=='TP'])
    Blame_false_p=len([p for p in neg if p=='FP'])
    Blame_false_n=len([p for p in neg if p=='FN'])
        
       
    praise_precision=Praise_true_p/(Praise_true_p+Praise_false_p)
    praise_recall=Praise_true_p/(Praise_true_p+Praise_false_n)
    blame_precision=Blame_true_p/(Blame_true_p+Blame_false_p)
    blame_recall=Blame_true_p/(Blame_true_p+Blame_false_n)
        
    praise_f1=2*praise_precision*praise_recall/(praise_precision+praise_recall)
    blame_f1=2*blame_precision*blame_recall/(blame_precision+blame_recall)
        
#        for reasons I don't see at the moment, these work fine in the interpreter
#        but become division by zero errors when run in the function.
#        Not enough of a hassle to worry about fixing it for now
#        PP=len(Ptp)/(len(Ptp) + len(Pfp))
#        PR=len(Ptp)/(len(Ptp) + len(Pfn)) 
#        NP=len(Ftp)/(len(Ftp) + len(Ffp))
#        NR=len(Ftp)/(len(Ftp) + len(Ffn))      
#        return ([PP,PR,NP,NR])
        #for now, just return the raw numbers
    print("F1 score for sentences of praise: %.2f" %(praise_f1))
    print("F1 score for sentences of blame: %.2f" %(blame_f1))
    print('*************************************************')
    print("Precision for sentences of praise: %.2f"%(praise_precision))
    print("Recall for sentences of praise: %.2f" %(praise_recall))
    print("Precision for sentences of blame: %.2f" %(blame_precision))
    print("Recall for sentences of blame: %.2f" %(blame_recall))
    
    return([praise_f1,blame_f1,praise_precision,praise_recall,blame_precision,
            blame_recall])


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
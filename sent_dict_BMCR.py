# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:55:06 2015
Making a dict of pos/neg/increment/decrement/inverter words
Done by expert survey of these randomly chosen BMCRS
http://bmcr.brynmawr.edu/1991/02.01.01.html
http://bmcr.brynmawr.edu/1991/02.06.09.html -- that one is Peter Green, which is hilarious
http://bmcr.brynmawr.edu/1996/96.02.11.html
http://bmcr.brynmawr.edu/1996/96.04.08.html
http://bmcr.brynmawr.edu/2000/2000-01-14.html
http://bmcr.brynmawr.edu/2009/2009-01-15.html
http://bmcr.brynmawr.edu/2009/2009-02-15.html
http://bmcr.brynmawr.edu/2012/2012-01-02.html
@author: Anonymous
"""
import pickle
sentiment_Words={
    'useful':'positive',
    'excels':'positive',
    'excel':'positive',
    'excellent':'positive',
    'basically':'decrement',
    'essentially':'decrement',
    'expertise':'positive', #this seems destined to become a problem
    'mainly':'decrement',
    'very': 'increment',
    'good':'positive',
    'apt':'positive', #also destinied to be a problem
    #'short':'negative', #though only when used with 'fall'
    'accurate':'positive',
    'falls':'invert',
    'mistakes': 'negative',
    'mistake':'negative',
    'irritating': 'negative',
    'error':'negative',
    'errors':'negative',
    'minor':'decrement',
    'failure':'negative',
    'objectionable':'negative',
    'confuse':'negative',
    'significantly':'increment',
    'oversimplification':'negative',
    'reliable':'positive',
    'not':'invert',
    'splendid':'positive',
    'positive':'positive',
    'enormous':'increment',
    'completely':'increment',
    'flaw':'negative',
    'flaws':'negative',
    'distort':'negative',
    'distorts':'negative',
    'suffers':'negative',
    'seriously':'increment',
    'suffer':'increment',
    'omissions':'negative',
    'large':'increment',
    'omission':'negative',
    'convincing':'positive',
    'well-argued':'positive',
    'most':'increment',
    'exaggerated':'negative',
    'dislike':'negative',
    'recommend':'positive',
    'learned':'positive', #the only new tag to emerge from a philosophy review
    'redundant':'negative',
    'overly':'negative',
    #'new':'positive', #causing a lot of imprecision
    'succeeds':'positive',
    'admirably':'increment',
    'helpful':'positive',
    'seldom':'decrement',
    'greatly':'increment',
    'detract':'negative',
    'impressive':'positive',
    'unfairly':'negative',
    'unwarranted':'negative',
    'sensibly':'positive',
    #'well':'positive', #too many false positives
    'deft':'positive',
    'excess':'negative',
    'superfluous':'negative',
    'overabundance':'negative',
    'inconsistent':'negative',
    'inconsistencies':'negative',
    'weak':'negative',
    'almost':'decrement',
    'interesting':'positive',
    'stimulating':'positive',
    'valuable':'positive',
    'occasionally':'decrement',
    'incorrect':'negative',
    'fail':'negative',
    #misses that should be added-- decide whether to do that before running
    'nuanced':'positive',
    'emphatically':'increment',
    'jargon':'negative',
    'without':'invert',
    'convinced':'positive',
    'convincing':'positive',
    'entirely':'increment',
    'extraneous':'negative',
    'much':'increment',
    'unnecessary':'negative',
    'no':'invert',
    'especially':'increment',
    'rightly':'positive',
    'repetitious':'negative',
    'first-rate':'positive',
    'less':'invert', #seems like it could go wrong...
    'unclear':'negative',
    'well-chosen':'positive',
    'omits':'negative',
    'perfectly':'positive',
    'simplistic':'negative',
    'unnecessarily':'negative',
    'indispensible':'positive',
    'correct':'positive',
    'correctly':'positive',
    'excessively':'negative'

}


with open('sentimentWords.pickle', 'wb') as f:
    pickle.dump(sentiment_Words, f, pickle.HIGHEST_PROTOCOL)
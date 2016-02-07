# 
# I find R's plotting functions more intuitive, and it is better adapted to tables
# and dataframes, so I collect and clean data in Python, and then work with
# it in R.
# This takes in a couple of .csv files that came out of Python. The one read in 
# as 'dat' is larger. It has a row for all ~8000 books and colums for title, number of
# pages, publication date, list price, Named Entities mentioned, total sentiment score and lists
# of positive and negative sentences.
# The one labled dat2 is a collection of frequency distributions for the 2300 +change words (excluding stopwords)
# that show up in sentences that were scored as either critical or positive (in a hand full of permutations).


#general housekeeping at the top

setwd("~/Python Scripts")

library (tm)
library (wordcloud)
library (png)
library (stringr)

windowsFonts(
  A=windowsFont("Georgia"),
  B=windowsFont("Euphemia"),
  C=windowsFont("Copperplate Gothic Bold"),
  D=windowsFont("Symbol")
)

ImageOverlay<-function(image,alpha=0.1){
  
#   R will let you show background images behind a plot, but doesn't provide
#   a handle to change the alpha. This takes the image you want
#   and uses matrix multiplaction to change the alpha manually, then draws it
#   to the plot window
#   image should be a string specifying file name/path for a .png
#   alpha is alpha
#   mostly taken from stack overflow  
  
  lim<-par()
  m <- readPNG(image)
  w <- matrix(rgb(m[,,1],m[,,2],m[,,3], m[,,4] * alpha), nrow=dim(m)[1])
  rasterImage(w, lim$usr[1], lim$usr[3], lim$usr[2], lim$usr[4])
  
  
}

dat<-read.csv('BMCR4.csv')
dat2<-read.csv('praiseBlametdm2.csv')

#quick cleaning
#By way of explanation, an earlier post joked about the number of colons
#academic books use in their titles. This section just riffs on that by
#putting ';' and ':' together in a version of the frequency distribution, to 
#show how excessively reviewers use those punctuation marks

fd<-cbind(dat2$positive,dat2$negative)
row.names(fd)<-dat2$word
tmp<-fd[';',]+fd[':',]
fd[':',]<-tmp

fd<-fd[!row.names(fd)==';',]
row.names(fd)[row.names(fd)==':']<-'colons'
colnames(fd)<-c('Praise','Blame')
fd<-data.frame(fd)

#wordcloud one-- just for laughs
#plots word clouds for the words in complimentary and critical 
#sentences next to each other

par(mfrow=c(1,2))
wordcloud(row.names(fd),fd$Praise,main='Words of Praise',max.words=90, colors=topo.colors(5))
ImageOverlay('clouds.png')
title('Sentences of Praise', family='C')
wordcloud(row.names(fd),fd$Blame,max.words=90, colors=heat.colors(5))
ImageOverlay('clouds.png')
title('Sentences of Blame', family='C')


#now let's play with change over time
erevs<-1203 #Number of reviews total in each of two four-year windows
lrevs<-2135 #known from before-- can't be reconstructed from current data
npe<-7445 #number positive early etc-- count of sentences with scores above or below zero
nne<-2052 #
npl<-9250
nnl<-2202

#so there are some calculations to do
dat2$p_e_r<-dat2$p_early/npe
dat2$n_e_r<-dat2$n_early/nne
dat2$p_l_r<-dat2$p_late/npl
dat2$n_l_r<-dat2$n_late/nnl
dat2$pdelt<-(dat2$p_l_r/dat2$p_e_r)*100
dat2$ndelt<-(dat2$n_l_r/dat2$n_e_r)*100

crit<-dat2[order(dat2$negative,decreasing=TRUE),]
crit<-crit[3:152,] #first two are ';' and ';', which we don't want

#by way of explanation below, the wordcloud package doesn't let you
#assign colours to words based on a categorical variable. As a work-around,
#you can order the words by that variable, and then make a vector of colours
#to match them.
crit<-crit[order(crit$ndelt),] #ordered coldest to hottest
summary(crit$ndelt) # looks reasonable enough! But it's always a good idea to check a calculated column
len<-crit$ndelt[crit$ndelt<90]#53
len<-crit$ndelt[crit$ndelt<110]#103-53=50
len<-crit$ndelt[crit$ndelt<200]#144-103=41, meaning 6 very hot
ncols<-c(rep('navy',53),rep(colours()[142],50), rep(colours()[556],41),rep(colours()[641],6))

pos<-dat2[order(dat2$positive, decreasing=TRUE),]
pos<-pos[2:152,]
pos<-pos[-2,]
pos<-pos[order(pos$pdelt),]
summary(pos$pdelt) #also looks reasonable enough
len<-pos$pdelt[pos$pdelt<90] #36
len<-pos$pdelt[pos$pdelt<110]#95-36=59
len<-pos$pdelt[pos$pdelt<200]#149-95=54, meaning 1 very hot
pcols<-c(rep('navy',36),rep(colours()[142],59), rep(colours()[556],54),rep(colours()[641],1))

#PraisHeatCloud
par(mfrow=c(1,1))
wordcloud(pos$word,pos$positive, colors=pcols,ordered.colors=TRUE,random.order=FALSE,scale=c(4,.3))
ImageOverlay('clouds.png')
legend(-.4,.3,c('Decreased > 10%','Held Steady','Increased > 10%','Increased > 100%'),lty=c(1,1,1,1),lwd=c(2,2,2,2),col=unique(pcols),cex=.8)
#wordcloud also doesn't play nicely with the 'title' parameter, so we do it manually
text(.5,1.01,labels="Words of Praise",family="C",cex=1.4)

#BlameHeatCloud

wordcloud(crit$word,crit$positive, colors=ncols,ordered.colors=TRUE,random.order=FALSE,scale=c(4,.3))
ImageOverlay('clouds.png')
legend(-.4,.3,c('Decreased > 10%','Held Steady','Increased > 10%','Increased > 100%'),lty=c(1,1,1,1),lwd=c(2,2,2,2),col=unique(pcols),cex=.8)
text(.5,1.01,labels="Words of Blame",family="C",cex=1.4)



#closing scatterplot
#this was to see if there was a major difference between books praised
#for the length of their bibliography and those criticised for it.
#there's a relationship but the sample size is too small for 
#statistical significance

bibpos<-c()
bibneg<-c()
for (i in 1:length(dat$title)){
  ng<-as.character(dat$neg)[i]
  ps<-as.character(dat$pos)[i]
  bibpos[i]<-str_detect(ps,'[bB]ibliograph')
  bibneg[i]<-str_detect(ng,'[bB]ibliograph')
  
}
dat$bibpos<-bibpos
dat$bibneg<-bibneg

plot(dat$pages,dat$score,xlim=c(100,800),ylim=c(0,8),pch=1, cex=.5,col='blue',xlab='Book Length (pages)',ylab='Score')
ImageOverlay('milestone.png',.3)
title("Longer Books Get Better
      Reviews",family='C')

reg<-lm(dat$score~dat$pages) #VERY significant
bp<-lm(dat$score~dat$pages, subset=(dat$bibpos==TRUE)) #only significant at p=.05
bn<-lm(dat$score~dat$pages, subset=(dat$bibneg==TRUE)) #not significant, sample to small
abline(reg,col='tomato',lwd=3)
legend(610,2,'Average Score
       by Length',lty=1,lwd=2,col='tomato')

#abline(bp,col='navy',lwd=3)
#abline(bn,col='goldenrod',lwd=3)

#############################################
#Code below was only used in exploration phase
#Didn't show enough to be used in final version
##############################################

# comparison.cloud(fd)
# commonality.cloud(fd)
# 
# other_words<-c('span','class','href','the','this','will','also','but')
# praise<-gsub("'", '',unlist(as.character(dat$pos)))
# blame<-gsub("'",'',unlist(as.character(dat$neg)))
# praise<-do.call('paste',list(praise, sep=''))
# praise<-str_c(praise, collapse='')
# blame<-str_c(blame, collapse='')
# 
# all<-Corpus(VectorSource(c(praise,blame)))
# all<-tm_map(all, removeWords, stopwords())
# all<-tm_map(all, removeWords,other_words)
# all<-tm_map(all, removePunctuation)
# 
# tdm<-TermDocumentMatrix(all)
# tdm<-removeSparseTerms(tdm,.99)
# tdm<-as.matrix(tdm)
# colnames(tdm)<-c('Praise','Blame')
# 
# praise<-VectorSource(praise)
# blame<-VectorSource(blame)
# praise<-Corpus(praise)
# blame<-Corpus(blame) 
# praise<-tm_map(praise,removeWords, stopwords())
# blame<-tm_map(blame, removeWords, stopwords())
# blame<-tm_map(blame, removePunctuation)
# praise<-tm_map(praise, removePunctuation)
# 
# praise<-tm_map(praise, removeWords, other_words)
# blame<-tm_map(blame,removeWords,other_words)
# total<-Corpus(VectorSource(c(praise,blame)))
# 
# 
# wordcloud(praise,max.words=150)
# 

# 
# #scatterplot for variety
# plot(dat$pages,dat$score,xlim=c(100,1000),ylim=c(-1,10))
# abline(lm(dat$score~dat$pages))
# #not enlightening
# plot(dat$price,dat$score,xlim=c(10,200),ylim=c(-1,10))
# abline(lm(dat$score~dat$price))
# 
# #closing scatterplot
# plot(dat$pages,dat$score,xlim=c(100,1000),ylim=c(0,8))
# abline(lm(dat$score~dat$pages),col='tomato',lwd=3)
# reg<-lm(dat$score~dat$pages)

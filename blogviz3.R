library (plotrix)
library(png)
library(Hmisc)
library(plyr)

windowsFonts(
  A=windowsFont("Georgia"),
  B=windowsFont("Euphemia"),
  C=windowsFont("Copperplate Gothic Bold"),
  D=windowsFont("Symbol")
)

ImageOverlay<-function(image,alpha=0.1){
  #image should be a string specifying file name/path for a .png
  #alpha is alpha
  lim<-par()
  m <- readPNG(image)
  w <- matrix(rgb(m[,,1],m[,,2],m[,,3], m[,,4] * alpha), nrow=dim(m)[1])
  rasterImage(w, lim$usr[1], lim$usr[3], lim$usr[2], lim$usr[4])
  
  
}

setwd("~/Python Scripts")

data<-read.csv('SentimentData.csv')
colnames(data)[3]<-'totsc'

#first Histogram

# hdat<-cut(data$totsc, c(-10,-2,0,1,2,3,4,5,6,7,8,9,10,20))
# hist(as.numeric(hdat), xlab=c()

clrs=c(rep('red',length(-22:2)),colours()[380],colours()[412],c(rep('darkgreen',length(6:52))))
hist(data$totsc, breaks=c(-22:52) , xlim=c(-10,30),col=clrs, main="Distribution of Scores", family='C',xlab='Approval Score',ylab="Frequency")
ImageOverlay('Temple-of-Apollo.png',0.06)
legend(16,850,c('Median Score: 4', "Mean Score: ~5"), lty=c(1,1), lwd=c(2,2), col=c(clrs[26],clrs[27]))
minor.tick(nx=2)

#Boxplots for publishers
phs<-unique(data$Publisher)
data$ph<-(tolower(as.character(data$Publisher)))
#clean up one problem
data$ph[data$ph=='de gruyter']<-'walter de gruyter'
frqs<-count(data$ph)
bg<-frqs[frqs$freq>99,]
med<-frqs[frqs$freq<80 & frqs$freq>19,]
med$x<-as.character(med$x)
meds<-as.character(med$x)
bg$x<-as.character(bg$x)
bigs<-bg$x
bd<-rbind(data[data$ph==bigs[1],], data[data$ph==bigs[2],])
for (i in 3:11){
  bd<-rbind(bd,data[data$ph==bigs[i],])
  
}

#code for small, medium, large

data$phsize<-rep("Small",8157)
for (i in 1:11){
  data$phsize[data$ph==bigs[i]]<-'Large'
}
for (i in 1:54){
  data$phsize[data$ph==meds[i]]<-'Medium'
}
data$phsize<-as.factor(data$phsize)
par(family="C")
boxplot(data$totsc~data$phsize, col=rainbow(3,.8,.8), main="Approval Rating by
        Size of Publishing House", family='C', ylab="Review Score", varwidth=TRUE, boxwex=.5, ylim=c(-5,20))
ImageOverlay('larnax.png',.08)


boxplot(data$totsc~data$ph,subset= data$ph==bigs[1:11], col=rainbow(11,.8,.8), 
        main="Major Publishing Houses",
        ylab="Review Score", ylim=c(-5,20),
        xlab = "",
        lab=c(0,8,0),
        xaxt='n', family="C", varwidth=TRUE,
        space=1)
#rotate 60 degrees, srt=60
blabs<-c("Brill","Cambridge",'Clarendon','Duckworth','Franz Steiner','Harvard','Oxford',"Princeton","Routledge", "University
         of California", 'Walter de 
         Gruyter')
text(seq(1:11), par("usr")[3]-0.25, 
     srt = 60, adj= 1, xpd = TRUE,
     labels = blabs, cex=0.75)
ImageOverlay('larnax.png',.15)


#By Date
yr<-c()
month<-c()
for (i in 1:8157){
  foo<-data$RevDate[i]
  yr<-append(yr, unlist(strsplit(as.character(foo),'\\.'))[1])
  month<-append(month, unlist(strsplit(as.character(foo),'\\.'))[2])
  
}

yr[yr=='01']<-'1990'
yr[yr=='02']<-'1991'
yr[yr=='03']<-'1992'
yr[yr=='04']<-'1993'
yr[yr=='94']<-'1994'
yr[yr=='95']<-'1995'
yr[yr=='96']<-'1996'
yr[yr=='97']<-'1997'
yr[yr=='98']<-'1998'

month<-as.numeric(month)


data$yr<-yr
data$month<-month
par(family="C")
boxplot(data$totsc~as.factor(data$yr), ylim=c(-5,20), main="Approval Ratings by Year",
        ylab="Review Score", font='C', col=rainbow(24,.8,.8), varwidth=TRUE)
ImageOverlay('larnax.png',.15)
nineties=as.character(c(1990:1999))

#month
par(family="C", xlab='Month')
boxplot(data$totsc~as.factor(data$month), subset=data$yr==nineties, ylim=c(-5,20), main="The Nineties Were a
        Lot More Fun",
        ylab="Review Score", xlab='Month', col=rainbow(12,.8,.8), varwidth=TRUE)
ImageOverlay('larnax.png',.15)


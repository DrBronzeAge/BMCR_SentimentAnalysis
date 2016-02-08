setwd("~/Python Scripts")

library(png)
library(Hmisc)
library(plotrix)

#tab<-read.csv('publicationdata1.csv')
tab<-read.csv('BMCR1dotupdate.csv')
tab$EngPublished<-tab$BooksPublished-tab$BooksPublishedEuro #calculated column easier here than in Python
#pubtab<-read.csv('BMCRPubHousedat.csv')
pubtab<-read.csv('BMCRpubdatdotupdate.csv')

#okay, so that's not what I was used to.  Apparently you can only grab columns as vectors if
#index, not if you grab them by name?  Weird
start<-(pubtab[,21]+pubtab[,22]+pubtab[,24])/3
end<-(pubtab[,24] +pubtab[,25])/2
deltas<-(end-start)/end
pubtab$deltas<-deltas

get_delta<-function (table,startcols, endcols){
  size<-length(startcols[1])
  deltas<-c()
  for (i in 1:size){
    sta<-mean(table[i,startcols])
    nd<-mean(table[i, endcols])
    deltas[i]<-nd-sta
  }
  return (deltas)
}


# Set up my own fonts
windowsFonts(
  A=windowsFont("Georgia"),
  B=windowsFont("Euphemia"),
  C=windowsFont("Copperplate Gothic Bold"),
  D=windowsFont("Symbol")
)

#with a little help from bill_080 on StackOverflow
numrev<-c(10,67,58,79,99, 156,89,149,165,226,287,301,388,384,440,494,510,557,555,654,675,691,675,662, 467)
#yeah, that's a lazy way to do that
ima <- readPNG("books2.png")
#try adjusting alpha
m <- readPNG("books2.png")
w <- matrix(rgb(m[,,1],m[,,2],m[,,3], m[,,4] * 0.2), nrow=dim(m)[1]) #the decimal outside the vector is alpha
#Set up the plot area
plot(c(1990:2014),numrev,main="BMCRs Filling your Inbox", xlab='Year',ylab='Books Reviewed/Year', type='n', family="C")

#Get the plot information so the image will fill the plot box, and draw it
lim <- par()
rasterImage(w, lim$usr[1], lim$usr[3], lim$usr[2], lim$usr[4])
#grid()
lines(c(1990:2014),numrev,type='b',pch=1,cex=.5, lwd=3, col=colours()[507])
text(1998,420, labels="That's almost a 45 degree
     slope over 15 years...", cex=1.0, family="A", col=colours()[507])
text(2009.5,450, labels="\"Almost two a day is
     probably a little
     excessive, guys...\"", cex=1.0, family='A',col=colours()[507])
minor.tick(nx=5)


#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#what went on there was terrible
#is all out of order
#we manually set the alpha by matrix multiplication (w) then used it as a background image
#we'll try to do it right below

#read in the image and adjust the alpha manually
imgmat<-readPNG('library.png')
alph<- matrix(rgb(imgmat[,,1],imgmat[,,2],imgmat[,,3], imgmat[,,4] * 0.4), nrow=dim(imgmat)[1])

#base plot for size and labels
plot(tab$Year[9:26],tab$BooksPublished[9:26],  xlab=" Publication Year", ylab="Books Submitted", family="C")
title("Books Recieved by the BMCR 1999-2015
By year of Publication", family="C")

lim<-par() #get the dimensions and anchor points for the plot
rasterImage(alph,lim$usr[2], lim$usr[3], lim$usr[1], lim$usr[4]) #draw the image in place
#add the lines
lines(tab$Year[9:26],tab$BooksPublished[9:26],type='b', pch=1,cex=.5,lwd=3,col=colours()[556])
minor.tick(nx=5)
text(2009, 500,'You wrecked a pretty
stable trend there,
     2011 and 2012.', family="A", cex=1.2, col=colours()[556], adj=0)
legend(1998,1300,"Total: 13193",adj=.19)

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

##Now we'll do that one again with a couple more lines
imgmat<-readPNG('map.png')
alph<- matrix(rgb(imgmat[,,1],imgmat[,,2],imgmat[,,3], imgmat[,,4] * 0.4), nrow=dim(imgmat)[1])

plot(tab$Year[9:26],tab$BooksPublished[9:26],  xlab=" Publication Year", ylab="Books Submitted", family="C")
title("Books Recieved by the BMCR 1999-2015
      By year of Publication", family="C")

lim<-par() #get the dimensions and anchor points for the plot
rasterImage(alph,lim$usr[1], lim$usr[3], lim$usr[2], lim$usr[4]) #draw the image in place
#add the lines
lines(tab$Year[9:26],tab$BooksPublished[9:26],type='b', pch=1,cex=.5,lwd=3,col=colours()[453])
lines(tab$Year[9:26],tab$EngPublished[9:26],type='b', pch=1,cex=.5,lwd=3,col=colours()[500])
minor.tick(nx=5)
lines(tab$Year[9:26],tab$BooksPublishedEuro[9:26],type='b', pch=1,cex=.5,lwd=3,col=colours()[574])
abline(lm(tab$BooksPublished[10:21]~tab$Year[10:21]), col=colours()[453],lwd=2,lty=3)
abline(lm(tab$EngPublished[10:21]~tab$Year[10:21]), col=colours()[500],lwd=2,lty=3)
abline(lm(tab$BooksPublishedEuro[10:23]~tab$Year[10:23]), col=colours()[574], lwd=2,lty=3)
legend(1998,1050,c('All', 'English', 'Continental'),lty=c(1,1,1),col=c(colours()[453], colours()[500],colours()[574]))

#####$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#how we got the increase
intTab<-pubtab[pubtab[,23]>=8,]
intTab<-pubtab[(pubtab$x2011>8 ),]
pubtab$deltraw<-pubtab[,25]-pubtab[,24]

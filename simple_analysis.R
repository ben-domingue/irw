load("vocab_assessment_3_to_8_year_old_children.Rdata")

long2resp<-function(df) {
    items<-unique(df$item)
    L<-split(df,df$item)
    x<-L[[1]][,c("id","resp")]
    names(x)[2]<-paste("item",names(L)[1],sep='')
    for (i in 2:length(L)) {
        z<-L[[i]][,c("id","resp")]
        names(z)[2]<-paste("item",names(L)[i],sep='')
        x<-merge(x,z,all=TRUE)
    }
    data.frame(x[,-1])
}

x<-long2resp(df)
ncat<-apply(x,2,function(z) length(unique(z[!is.na(z)])))
x<-x[,ncat>1]

##basic cronbach's alpha calculation (i tried to get ascii art of cronbach but it just won't come out right :( )
library(psych)
alpha(x)$total[1]

##now test and item response functions
library(mirt)
mm<-mirt(x,technical=list(NCYCLES=2000))

par(mfrow=c(1,2),mgp=c(2,1,0),mar=c(3,3,1,1))
th<-matrix(seq(-5,5,length.out=1000),ncol=1)
plot(th,expected.test(mm,th),type='l',lwd=2,xlab='theta',ylab='expected score') #test response function

plot(NULL,xlim=range(th[,1]),ylim=0:1)
for (i in 1:ncol(x)) {
    mi<-extract.item(mm,i)
    lines(th,expected.item(mi,Theta=th),col='gray',lwd=.5,xlab='theta',ylab='expected response') #all IRFs
}

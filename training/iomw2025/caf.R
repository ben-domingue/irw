##a quick tutorial to show you how flexible and fun splines can be!
x<-sort(rnorm(1000))
y<-.3*x^3+.2*x^2+.5*x+rnorm(length(x))
plot(x,y)
abline(lm(y~x))
library(splines)
spl<-splines::bs(x)
head(cbind(x,spl))
m<-lm(y~spl)
summary(m)
lines(x,fitted(m),col='red',lwd=3)

df<-irwpkg::irw_fetch("roar_lexical")

caf<-function(df,nspl=3) {
    ##rescaling responses
    df$resp<-as.numeric(df$resp)
    df <- df[!is.na(df$resp),]
    M<-max(df$resp)-min(df$resp)
    df$resp<-(df$resp-min(df$resp))/M
    ##sanity checking the repsonse times
    df$rt<-as.numeric(df$rt)
    df<-df[df$rt>0,]
    df$rt<-log(df$rt)
    x<-df[!is.na(df$rt),]
    ##splines
    library(splines)
    spl<-bs(x$rt,df=nspl)
    for (i in 1:ncol(spl)) x[[paste("spl",i,sep='')]]<-spl[,i]
    ##now model accuracy
    library(lme4) 
    fm.spl<-paste(paste("spl",1:nspl,sep=""),collapse="+")
    fm<-paste("resp~(1|id+item)+(",fm.spl,")",sep='')
    m<-glmer(fm,x,family='binomial')
    xv<-seq(min(x$rt),max(x$rt),length.out=250)
    z<-predict(spl,xv)
    z<-cbind(1,z)
    k<-as.matrix(z) %*% matrix(fixef(m),ncol=1)
    acc<-1/(1+exp(-k))
    z<-data.frame(t=xv,acc=acc)
    z
}
z<-caf(df)

par(mgp=c(2,1,0))
qu<-quantile(df$rt,c(.01,.99))
plot(z$t,z$acc,type='l',xlab='rt',ylab='change in repsonse',xlim=qu,xaxt='n',lwd=3)
tvals<-c(1,2,3,5,10,15,30,60,120)
axis(side=1,at=log(tvals),as.character(tvals))
qu<-quantile(df$rt,c(.025,.975))
polygon(c(qu[1],qu[1],qu[2],qu[2]),c(0,1,1,0),col=rgb(1,0,0,alpha=.35))

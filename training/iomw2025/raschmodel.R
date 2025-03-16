library(irwpkg)
df<-irw_fetch("verbagg")

load("roar_lexical.Rdata")

pvalue<-by(df$resp,df$item,mean)
sumscore<-by(df$resp,df$id,sum)
par(mfrow=c(1,2),mgp=c(2,1,0),mar=c(3,3,1,1))
hist(pvalue)
plot(density(sumscore))

resp<-irwpkg::irw_long2resp(df)
head(resp) ##note first column is the `id`

library(mirt)
m<-mirt(resp[,-1],1,'Rasch')
itemfit(m,'infit')

library(WrightMap)
th<-fscores(m)[,1]
diff<-coef(m,simplify=TRUE,IRTpa=TRUE)$items[,2]
##
wrightMap(thetas=th,difficulties=sort(diff))

#hist(diff,freq=FALSE,main='',sub='',xlab=expression(theta),xlim=c(-4,4))
h<-hist(diff,freq=FALSE)
den<-density(th)
M<-max(c(h$density,den$y))
plot(h,freq=FALSE,main='',sub='',xlab=expression(theta),xlim=c(-4,4),ylim=c(0,M))
lines(den)
points(diff,rep(0,length(diff)),col='red')

#load("../src/snapshot.Rdata")

##ncme
ss<-read.csv("/home/bdomingu/Dropbox/Apps/Overleaf/IRW/ncmeproposal/snapshot.csv",sep=",",header=TRUE)
#pdf("/home/bd/Dropbox/Apps/Overleaf/IRW/Ns.pdf",width=7,height=3)
pdf("~/Dropbox/Apps/Overleaf/IRW/ncmeproposal/Ns.pdf",width=5,height=2.4)
par(mfrow=c(1,2),mgp=c(2,1,0),mar=c(3,3,1,1),oma=rep(.5,4))
hist(log10(ss$nresp),col='blue',main='',breaks=20,xlab="log10 (N responses)")
mtext(side=3,adj=0,line=0,'A')
plot(log10(ss$person.n),log10(ss$item.n),pch=19,cex=.5,col='blue',xlab="log10(N person)",ylab="log10(N item)",xlim=c(0,6.2),ylim=c(0,6.2))
mtext(side=3,adj=0,line=0,'B')
abline(0,1)
dev.off()
dim(ss)
sum(ss$nresp)

median(ss$person.n)

table(ss$resp.per.person>ss$resp.per.item)
z<-ss[ss$resp.per.person>ss$resp.per.item,]
summary(z$resp.per.person)
summary(z$resp.per.item)

x<-ifelse(ss$sparse<1,0,NA)
x<-ifelse(is.na(x) & ss$sparse>1,2,x)
x<-ifelse(is.na(x) & ss$sparse==1,1,x)
table(x)
z<-ss[ss$sparse<1,]
table(z$sparse<.5)
summary(z$sparse)

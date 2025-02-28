library(irwpkg)
load("verbagg.Rdata")

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

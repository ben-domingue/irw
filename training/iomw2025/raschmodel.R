library(irwpkg)
df<-irw_fetch("DART_Brysbaert_2020_1")

#################################################################################################
##BLOCK A
pvalue<-by(df$resp,df$item,mean)
sumscore<-by(df$resp,df$id,sum)
par(mfrow=c(2,1),mgp=c(2,1,0),mar=c(3,3,1,1))
hist(pvalue,main='',xlab='item p value')
legend("topright",bty='n',paste(length(pvalue),' items',sep=''))
hist(sumscore,main='',xlab='person sum score')
legend("topright",bty='n',paste(length(sumscore),' persons',sep=''))

#################################################################################################
##BLOCK B
resp<-irwpkg::irw_long2resp(df) ##bd. note the importance of this function
dim(df)
dim(resp)
head(df)
head(resp) ##note first column is the `id`

##to simplify our lives a little.
txt<-colnames(resp)
colnames(resp)<-gsub("item_Is de volgende persoon een auteur- ","",txt)

#################################################################################################
##BLOCK C
library(mirt)
m<-mirt(resp[,-1],1,'Rasch')

co<-coef(m,simplify=TRUE,IRTpars=TRUE)
diff<-co$item
diff<-diff[order(diff[,2]),]
head(diff) #easiest items
tail(diff) #hardest items

##for fun
## tam.model<-TAM::tam(resp[,-1])
## tam.diff<-tam.model$xsi$xsi
## erm.model<-eRm::RM(resp[,-1])
## erm.diff<-erm.model$betapar

## plot(data.frame(mirt.diff=co$item[,2],tam.diff=tam.diff,erm.diff=erm.diff))

#################################################################################################
##BLOCK D
fitstat<-itemfit(m,'infit')
sd(fitstat$outfit)
sqrt(2/nrow(resp))

#################################################################################################
##BLOCK E
dev.new() ##maximize this new window

th<-fscores(m)[,1]
diff<-coef(m,simplify=TRUE,IRTpa=TRUE)$items[,2]
##
library(WrightMap)
wrightMap(thetas=th,thresholds=sort(diff), label.items.srt = 45)

#################################################################################################
##BLOCK F
library(difR)
gender<-df[,c("id","gender")]
gender<-gender[!duplicated(gender$id),]
index<-match(gender$id,resp$id)
gender<-gender[index,]
difstat<-difLogistic(resp[,-1],type='udif',group=gender$gender,focal.name="Vrouw")
z<-difstat$parM0[,3]/difstat$seM0[,3]
nms<-colnames(resp)[-1]
z<-data.frame(author=nms,z=z)
z<-z[order(z$z),]
z[abs(z$z)>2,]

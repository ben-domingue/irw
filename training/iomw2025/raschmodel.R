library(irwpkg)
df<-irw_fetch("DART_Brysbaert_2020_1")

##bd. pause and give them questions to explore about the data


pvalue<-by(df$resp,df$item,mean)
sumscore<-by(df$resp,df$id,sum)
par(mfrow=c(1,2),mgp=c(2,1,0),mar=c(3,3,1,1))
hist(pvalue)
plot(density(sumscore))

resp<-irwpkg::irw_long2resp(df) ##bd. note the importance of this function
head(resp) ##note first column is the `id`

library(mirt)
m<-mirt(resp[,-1],1,'Rasch')
fitstat<-itemfit(m,'infit')
sd(fitstat$outfit)
sqrt(2/nrow(resp))

library(WrightMap)
th<-fscores(m)[,1]
diff<-coef(m,simplify=TRUE,IRTpa=TRUE)$items[,2]
##
wrightMap(thetas=th,thresholds=sort(diff), label.items.srt = 45)

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

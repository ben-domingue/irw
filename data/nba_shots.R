##https://github.com/DomSamangy/NBA_Shots_04_23

x<-read.csv("NBA_2023_Shots.csv")
id<-x$PLAYER_ID
item<-'trial'
resp<-ifelse(x$EVENT_TYPE=="Made Shot",1,0)
lx<-x$LOC_X
ly<-x$LOC_Y
dist<-sqrt(lx^2+ly^2)
by(dist,x$SHOT_TYPE,summary)
threept<-ifelse(x$SHOT_TYPE=="3PT Field Goal",1,0)
## par(mfrow=c(1,2))
## i<-sample(1:nrow(x),5000)
## m<-loess(resp[i]~dist[i])
## plot(m$x,predict(m))
## plot(dist,x$SHOT_DISTANCE)

df<-data.frame(id=id,resp=resp,trial__locx=lx,trial__locy=ly,trial__three=threept)
save(df,file="nba2023shots.Rdata")

library(lme4)
m<-lmer(resp~abs(trial__locx)+trial__locy+threept+(1|id),df)
z<-ranef(m)$id
names(z)[1]<-'th'
z$id<-rownames(z)
##
tab<-table(x$PLAYER_ID)
qu<-quantile(tab,.25)
ids<-names(tab)[tab>qu]
x<-x[x$PLAYER_ID %in% ids,]
m<-by(x$SHOT_DISTANCE,x$PLAYER_ID,mean)
z<-merge(z,data.frame(id=names(m),dist=unlist(m)))
y<-x[,c("PLAYER_ID","PLAYER_NAME")]
y<-y[!duplicated(y),]
z<-merge(z,y,by=1)

plot(z$dist,z$th,type='n')
text(z$dist,z$th,z$PLAYER_NAME,cex=.5)

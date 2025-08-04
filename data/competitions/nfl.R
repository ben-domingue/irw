##https://www.kaggle.com/datasets/davidsasser/nfl-game-stats-20102019

L<-list()
for (y in 2010:2019) {
    z<-read.csv(paste("game_stats_",y,".csv",sep=""))
    z$year<-y
    L[[as.character(y)]]<-z
}
x<-do.call("rbind",L)

delta<-x$H.Score-x$A.Score

test<-delta>=0
id_1<-ifelse(test,x$HomeTeam,x$AwayTeam)
id_2<-ifelse(!test,x$AwayTeam,x$AwayTeam)
df<-data.frame(id_1=id_1,id_2=id_2,resp=abs(delta),year=x$year,week=x$Week)

m<-min(df$year)
ws<-7*24*60*60
d<-(df$week-1)*ws
ys<-365*24*60*60
y<-(df$year-m)*ys
df$date<-d+y

write.csv(df,file="nfl_2010-2019.csv",quote=FALSE,row.names=FALSE)

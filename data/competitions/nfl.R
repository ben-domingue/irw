##https://www.kaggle.com/datasets/davidsasser/nfl-game-stats-20102019

L<-list()
for (y in 2010:2019) {
    z<-read.csv(paste("game_stats_",y,".csv",sep=""))
    z$year<-y
    L[[as.character(y)]]<-z
}
x<-do.call("rbind",L)

df<-x[,c("HomeTeam","AwayTeam","H.Score","A.Score")]
names(df)<-c("agent_a","agent_b","score_a","score_b")

m<-min(x$year)
ws<-7*24*60*60
d<-(x$Week-1)*ws
ys<-365*24*60*60
y<-(x$year-m)*ys
df$date<-d+y

df$winner<-ifelse(df$score_a>df$score_b,'agent_a','agent_b')
df$winner<-ifelse(df$score_a==df$score_b,'draw',df$winner)


write.csv(df,file="nfl_2010-2019.csv",quote=FALSE,row.names=FALSE)

##https://www.kaggle.com/datasets/pablote/nba-enhanced-stats
x1<-read.csv("2012-18_teamBoxScore.csv")
x2<-read.csv("2016-17_teamBoxScore.csv")
x3<-read.csv("2017-18_teamBoxScore.csv")
x<-rbind(x1,x2,x3)

x<-x[x$teamLoc=="Home",]
df<-x[,c("teamAbbr","teamPTS","opptAbbr","opptPTS")]
names(df)<-c("agent_a","score_a","agent_b","score_b")
df$date<-as.numeric(strptime(x$gmDate,format='%Y-%m-%d'))
df$hometeam<-'agent_a'

df$winner<-ifelse(df$score_a>df$score_b,'agent_a','agent_b')
df$winner<-ifelse(df$score_a==df$score_b,'draw',df$winner)

write.csv(df,file="nba_2012-2018.csv",quote=FALSE,row.names=FALSE)

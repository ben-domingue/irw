##https://github.com/sportstensor/MLB/blob/main/data_and_models/mlb_elo.csv
##based on 538 data

x<-read.csv("mlb_elo.csv")
df<-data.frame(agent_a=x$team1,agent_b=x$team2,season=x$season,score_a=x$score1,score_b=x$score2)
df$homefield<-'agent_a'

df$date<-as.numeric(strptime(x$date,format='%Y-%m-%d'))
df$winner<-ifelse(df$score_a>df$score_b,'agent_a','agent_b')
df$winner<-ifelse(df$score_a==df$score_b,'draw',df$winner)

write.csv(df,file="mlb_through2023.csv",quote=FALSE,row.names=FALSE)

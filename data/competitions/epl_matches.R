##https://www.kaggle.com/datasets/shubhamgadekar/english-premier-league20202022-dataset
x<-read.csv("matches.csv")
x<-x[x$venue=="Home",]

df<-data.frame(agent_a=x$team,agent_b=x$opponent)
df$date<-as.numeric(strptime(x$date,format='%Y-%m-%d'))
df$score_a<-x$gf
df$score_b<-x$ga
df$homefield<-'agent_a'

df$winner<-ifelse(df$score_a>df$score_b,'agent_a','agent_b')
df$winner<-ifelse(df$score_a==df$score_b,'draw',df$winner)

write.csv(df,file="epl_matches_2021-2022.csv",quote=FALSE,row.names=FALSE)

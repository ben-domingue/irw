##https://www.kaggle.com/datasets/thedevastator/analyzing-college-football-2022-wins-losses-rank
x1<-read.csv("games2021.csv")
x2<-read.csv("games2022.csv")
x<-rbind(x1,x2)

df<-data.frame(agent_a=x$home_id,agent_b=x$away_id)
z<-substr(x$start_date,1,10)
df$date<-as.numeric(strptime(z,format='%Y-%m-%d'))
df$homefield<-ifelse(x$neutral_site=='False','agent_a',NA)

df$score_a<-x$home_points
df$score_b<-x$away_points

df$winner<-ifelse(df$score_a>df$score_b,'agent_a','agent_b')
df$winner<-ifelse(df$score_a==df$score_b,'draw',df$winner)

write.csv(df,file="collegefb_2021and2022.csv",quote=FALSE,row.names=FALSE)

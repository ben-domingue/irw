##https://www.kaggle.com/datasets/pablote/nba-enhanced-stats
x1<-read.csv("2012-18_teamBoxScore.csv")
x2<-read.csv("2016-17_teamBoxScore.csv")
x3<-read.csv("2017-18_teamBoxScore.csv")
x<-rbind(x1,x2,x3)

x<-x[x$teamLoc=="Home",]
x[,c("gmDate","teamAbbr","teamPTS","opptAbbr","opptPTS")]

delta<-x$teamPTS-x$opptPTS

test<-delta>=0
id_1<-ifelse(test,x$teamAbbr,x$opptAbbr)
id_2<-ifelse(!test,x$teamAbbr,x$opptAbbr)
df<-data.frame(id_1=id_1,id_2=id_2,resp=abs(delta))

df$date<-as.numeric(strptime(x$gmDate,format='%Y-%m-%d'))

save(df,file="nba_2012-2018.Rdata")
write.csv(df,file="nba_2012-2018.csv",quote=FALSE,row.names=FALSE)

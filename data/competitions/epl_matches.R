##https://www.kaggle.com/datasets/shubhamgadekar/english-premier-league20202022-dataset
x<-read.csv("matches.csv")
x<-x[x$venue=="Home",]

delta<-x$gf-x$ga

test<-delta>=0
id_1<-ifelse(test,x$team,x$opponent)
id_2<-ifelse(!test,x$team,x$opponent)
df<-data.frame(id_1=id_1,id_2=id_2,resp=abs(delta))

df$date<-as.numeric(strptime(x$date,format='%Y-%m-%d'))
save(df,file="epl_matches_2021-2022.Rdata")
write.csv(df,file="epl_matches_2021-2022.csv",quote=FALSE,row.names=FALSE)

##https://www.kaggle.com/datasets/thedevastator/analyzing-college-football-2022-wins-losses-rank
x1<-read.csv("games2021.csv")
x2<-read.csv("games2022.csv")
x<-rbind(x1,x2)

start_date
home_idaway_id

delta<-x$home_points-x$away_points

test<-delta>=0
id_1<-ifelse(test,x$home_id,x$away_id)
id_2<-ifelse(!test,x$home_id,x$away_id)
df<-data.frame(id_1=id_1,id_2=id_2,resp=abs(delta))

z<-substr(x$start_date,1,10)
df$date<-as.numeric(strptime(z,format='%Y-%m-%d'))

save(df,file="collegefb_2021and2022.Rdata")
write.csv(df,file="collegefb_2021and2022.csv",quote=FALSE,row.names=FALSE)

##https://www.kaggle.com/datasets/neelagiriaditya/ufc-datasets-1994-2025

x<-read.csv("UFC.csv")
x<-x[x$winner_id!="",]
x<-x[,c("winner","date","b_name","r_name")]
ln<-ifelse(x$winner==x$b_name,x$r_name,x$b_name)
df<-data.frame(id_1=x$winner,id_2=ln,resp=1)

df$date<-as.numeric(strptime(x$date,format='%Y/%m/%d'))

write.csv(df,file="ufc.csv",quote=FALSE,row.names=FALSE)

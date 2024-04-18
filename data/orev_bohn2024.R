x<-read.csv("clean_data.csv")
rt<-x$responseTime/1000
age<-x$age_group
item<-x$targetWord
id<-x$subjID

df<-data.frame(id=id,item=item,rt=rt,age=age,resp=ifelse(x$correct==1,1,0))
save(df,file="orev_bohn2024.Rdata")

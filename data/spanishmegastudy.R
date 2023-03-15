x<-read.csv("answers.csv",header=TRUE)
df<-data.frame(id=x$id_user,item=x$id_item,resp=x$hit,rt=x$rt/1000,order=x$trial_order)

save(df,file="spanishmegastudy.Rdata")

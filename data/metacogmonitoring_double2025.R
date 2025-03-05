x<-read.csv("ex1-self-reports-metacognition-clean-data.csv")
id<-x$ResponseId
age<-x$Age
sex<-x$Sex
x<-x[,-(1:3)]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,cov_age=age,cov_sex=sex,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

write.csv(df,file="metacogmonitoring_double2025.csv",quote=FALSE,row.names=FALSE)

x<-read.csv("Ratings_RawData.csv")
x<-x[x$Filter==1,]
x<-x[x$Rating %in% 1:5,]
item<-x$Participant
id<-x$Expression
resp<-x$Rating

df<-data.frame(id=id,item=item,resp=resp)
save(df,file="concretewords.Rdata")

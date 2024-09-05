#https://mqscores.lsa.umich.edu/replication.php

load("mqData2021.Rda")
term<-mqData$term
time<-mqData$time
item<-mqData$caseId
mqData$term<-mqData$time<-mqData$caseId<-NULL

out<-list()
for (i in 1:ncol(mqData)) {
    resp<-mqData[,i]
    id<-names(mqData)[i]
    out[[i]]<-data.frame(id=id,item=item,term=term,resp=resp)
}
df<-data.frame(do.call("rbind",out))

df<-df[!is.na(df$resp),]

##converting term
paste("8-1-",df$term,sep='')->d
d<-strptime(d,"%m-%d-%Y")
df$date<-as.numeric(as.POSIXct(d))



save(df,file='mq_supremecourt.Rdata')


## ANDRICH.RData
load("ANDRICH.RData")
x<-ANDRICH
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="andrich_mudfold.Rdata")


## EURPAR2.RData
load("EURPAR2.RData")
x<-EURPAR2
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="eurpar2_mudfold.Rdata")

## Loneliness.RData
load("Loneliness.RData")
x<-Loneliness
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=as.numeric(x[,i]))
df<-data.frame(do.call("rbind",L))
save(df,file="loneliness_mudfold.Rdata")

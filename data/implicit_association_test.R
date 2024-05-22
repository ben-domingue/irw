
y<- read.csv("Study2_Data.csv")
x<-y[,c(1, 3, 17:58)]
x=x[x$duplicate_id!=1,]
x=x[,-2]
x=x[,-match(c("ageid", "arabid", "politicsid", "raceid", "sexid", "skinid", "weightid"), names(x))]
colnames(x)[1] <- "id"
L<-list()
for (i in 2:ncol(x)) L[[i]]<-data.frame(id=x[,1],item=colnames(x)[i],resp=x[,i])
df1<-data.frame(do.call("rbind",L))
save(df1,file='IAT_study2.Rdata')


y<- read.csv("Study3_Data.csv")
x<-y[,c(1, 3, 17:52)]
x=x[x$duplicate_id!=1,]
x=x[,-2]
x=x[,-match(c("politicsid", "raceid", "sexid", "vegid", "weightid"), names(x))]
colnames(x)[1] <- "id"
L<-list()
for (i in 2:ncol(x)) L[[i]]<-data.frame(id=x[,1],item=colnames(x)[i],resp=x[,i])
df2<-data.frame(do.call("rbind",L)); df
save(df2, file='IAT_study3.Rdata')

x<-read.csv("BHS AND SI.csv",sep=';')
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

save(df,file="bhs_floreskanter2021.Rdata")

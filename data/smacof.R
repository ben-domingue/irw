#PVQ40
#, 43

load("PVQ40.rda")
x<-PVQ40
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df<-df[df$resp>0,]
save(df,file="smacof_pvq40.Rdata")

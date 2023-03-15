x<-read.csv("TDRI_dataset.csv",header=TRUE,sep=";")

id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

save(df,file='tdri.Rdata')

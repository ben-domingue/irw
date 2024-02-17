x<-read.csv("journal.pone.0294671.s006.txt")
x$AUD<-NULL

id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

save(df,file="alcoholresearch_sumscore.Rdata")

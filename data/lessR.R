load("dataMach4.rda")
x<-dataMach4
id<-1:nrow(x)
L<-list()
for (i in 2:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="lessR_Mach4.Rdata")

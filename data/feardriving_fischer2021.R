x<-read.csv("Data Set 2 Instrument for Fear of Driving.csv",sep=';')

id<-1:nrow(x)
i1<-grep("^ISAP",names(x))[1:5] #Not the total
i2<-grep("^DCQ",names(x))
x<-x[,c(i1,i2)]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

save(df,file="feardriving_fisher2021.Rdata")

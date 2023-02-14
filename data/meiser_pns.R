library(foreign)
x<-read.spss("PNS_N=1789.sav",to.data.frame=TRUE)
id<-x$id
x<-x[,grep("^pns",names(x))]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="meiser_pns.Rdata")

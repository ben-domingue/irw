##https://osf.io/2pkaw/
load("usData.rda")
i<-grep("^MFQ",names(USdata))[1:36]
x<-USdata[,names(USdata)[i]]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mft_validationandreplication.Rdata")



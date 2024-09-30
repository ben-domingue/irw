x<-read.csv("data_dass21.csv",sep="|")
id<-1:nrow(x)
L<-list()
for (i in 9:29) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

save(df,file="dass_Thiyagarajan2022.Rdata")


library(GDINA)

resp<-frac20$dat
L<-list()
names(resp)<-paste("item_",1:ncol(resp),sep='')
for (i in 1:ncol(resp)) L[[i]]<-data.frame(item=names(resp)[i],id=1:nrow(resp),resp=as.numeric(resp[,i]))
df<-data.frame(do.call("rbind",L))

Q<-frac20$Q
names(Q)<-paste("Qmatrix",1:ncol(Q),sep="__")
Q$item<-names(resp)
attr(df,which='item')<-Q

save(df,file="frac20.Rdata")

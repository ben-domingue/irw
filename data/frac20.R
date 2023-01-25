library(GDINA)

resp<-frac20$dat
L<-list()
for (i in 1:ncol(resp)) L[[i]]<-data.frame(item=paste0("item_",i),id=1:nrow(resp),resp=as.numeric(resp[,i]))
df<-data.frame(do.call("rbind",L))

save(df,file="frac20.Rdata")

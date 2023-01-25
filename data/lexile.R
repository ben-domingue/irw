################################################################################################
read.csv("duval_4.csv")->d4
d4[-1,]->d4
NULL->d4$Total
for (i in 1:ncol(d4)) ifelse(d4[,i]=="*",NA,d4[,i])->d4[,i]
L<-list()
for (i in 1:ncol(d4)) L[[i]]<-data.frame(item=paste0("item_",i),id=1:nrow(d4),resp=as.numeric(d4[,i]))
df<-data.frame(do.call("rbind",L))
save(df,file="duval4.Rdata")

read.csv("duval_8.csv")->d8
d8[-1,]->d8
NULL->d8$Total
for (i in 1:ncol(d8)) ifelse(d8[,i]=="*",NA,d8[,i])->d8[,i]
L<-list()
for (i in 1:ncol(d8)) L[[i]]<-data.frame(item=paste0("item_",i),id=1:nrow(d8),resp=as.numeric(d8[,i]))
df<-data.frame(do.call("rbind",L))
save(df,file="duval8.Rdata")

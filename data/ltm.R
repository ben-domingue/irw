library(ltm)

#WIRS
#Mobility
#LSAT
#Abortion

##Wirs
x<-WIRS
names(x)<-paste("item_",1:ncol(x),sep='')
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="wirs.Rdata")

##Mobility
x<-Mobility
names(x)<-paste("item_",1:ncol(x),sep='')
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mobility.Rdata")

##LSAT
x<-LSAT
names(x)<-paste("item_",1:ncol(x),sep='')
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="lsat.Rdata")

##Abortion
x<-Abortion
names(x)<-paste("item_",1:ncol(x),sep='')
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="abortion.Rdata")

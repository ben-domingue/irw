## immer09
load("data.immer09.rda")
x<-data.immer09
names(x)<-c("id","item","resp")
df<-x
save(df,file="immer09_immer.Rdata")

## immer10
load("data.immer10.rda")
x<-data.immer10
id<-x$item
difficulty<-x$itemdiff
L<-list()
for (i in 3:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],difficulty=difficulty,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="immer10_immer.Rdata")

## immer11
#load("data.immer11.rda")
#x<-data.immer11 #something is wrong with t his

## immer12
load("data.immer12.rda")
x<-data.immer12
id<-x$idpair
rater<-x$judge
L<-list()
for (i in 4:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],rater=rater,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="immer12_immer.Rdata")

## data.ptam1
load("data.ptam1.rda")
x<-data.ptam1
id<-x$pid
rater<-x$rater
L<-list()
for (i in 3:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],rater=rater,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="ptam1_immer.Rdata")

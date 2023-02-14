load('data.ecpe.rda')
x<-data.ecpe
Q<-x$q.matrix
x<-x$data
id<-x$id
x$id<-NULL
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
##
rownames(Q)<-names(x)
names(Q)<-paste("Qmatrix",names(Q),sep="__")
Q$item<-rownames(Q)
attr(df,which='item')<-Q
save(df,file="cdm_ecpe.Rdata")

load('data.hr.rda')
x<-data.hr
Q<-x$q.matrix
x<-x$data
names(x)<-rownames(Q)
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
##
names(Q)<-paste("Qmatrix",names(Q),sep="__")
Q$item<-rownames(Q)
attr(df,which='item')<-Q
save(df,file="cdm_hr.Rdata")


load('data.pisa00R.ct.rda')
x<-data.pisa00R.ct
Q<-x$q.matrix
x<-x$data
index<-grep("^R",names(x))
x<-x[,index]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
##
names(Q)<-paste("Qmatrix",names(Q),sep="__")
Q<-data.frame(Q)
Q$item<-rownames(Q)
attr(df,which='item')<-Q
save(df,file="cdm_pisa00R.Rdata")

load("data.timss03.G8.su.rda")
x<-data.timss03.G8.su
Q<-x$q.matrix
x<-x$data
index<-grep("^M",names(x))
x<-x[,index]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
##
names(Q)<-paste("Qmatrix",names(Q),sep="__")
Q<-data.frame(Q)
Q$item<-rownames(Q)
attr(df,which='item')<-Q
save(df,file="cdm_timss03.Rdata")

load("data.timss07.G4.lee.rda")
x<-data.timss07.G4.lee
Q<-x$q.matrix
x<-x$data
booklet<-x$idbook
index<-grep("^M",names(x))
x<-x[,index]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],booklet=booklet)
df<-data.frame(do.call("rbind",L))
df<-df[!is.na(df$resp),]
##
names(Q)<-paste("Qmatrix",names(Q),sep="__")
Q<-data.frame(Q)
Q$item<-rownames(Q)
attr(df,which='item')<-Q
save(df,file="cdm_timss07.Rdata")

load("data.timss11.G4.AUT.rda")
x<-data.timss11.G4.AUT
Q<-x$q.matrix1
x<-x$data
booklet<-x$IDBOOK
x<-x[,as.character(Q$item)]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],booklet=booklet)
df<-data.frame(do.call("rbind",L))
df<-df[!is.na(df$resp),]
##
items<-Q$item
Q$item<-NULL
names(Q)<-paste("Qmatrix",names(Q),sep="__")
Q<-data.frame(Q)
Q$item<-items
attr(df,which='item')<-Q
save(df,file="cdm_timss11.Rdata")

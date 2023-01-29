## data.big5, 34, 255
load("data.big5.rda")
x<-data.big5
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="big5_sirt.Rdata")

## data.g308, 50
load("data.g308.rda")
x<-data.g308
# define testlets
testlet <- c(1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4, 5, 5, 6, 6, 6)
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],testlet=testlet[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="g308_sirt.Rdata")

## data.math, 59
load("data.math.rda")
x<-data.math
hold<-x$item
x<-x$data
x<-x[,-(1:2)]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df<-merge(df,hold)
save(df,file="4thgrade_math_sirt.Rdata")

## data.pirlsmissing, 67
load("data.pirlsmissing.rda")
x<-data.pirlsmissing
z<-x[,1:3]
x<-x[,-(1:3)]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i],country=z$country,wt=z$studwgt)
df<-data.frame(do.call("rbind",L))
df$resp<-ifelse(df$resp==9,NA,df$resp) #not reached responses coded as NA
save(df,file="pirlsmissing_sirt.Rdata")


## data.si09 (data.sirt), 
load("data.si09.rda")
x<-data.si09
country<-x$country
x$country<-NULL
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i],country=country)
df<-data.frame(do.call("rbind",L))
save(df,file="si09_sirt.Rdata")

## data.trees, 106
load("data.trees.rda")
x<-data.trees
x<-x[,-1]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="trees_sirt.Rdata")

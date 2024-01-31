## 1-ability, 2
load("ability.rda")
x<-ability
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="psychtools_ability.Rdata")

## 2-Athenstaedt, 6
load("Athenstaedt.rda")
x<-Athenstaedt
i<-grep("^V",names(x))
#id<-x[,1]
id<-1:nrow(x)
gender<-x[,2]
x<-x[,i]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],gender=gender,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="psychtools_Athenstaedt.Rdata")

## 3-bfi, 9
load("bfi.rda")
x<-bfi
x$education<-NULL
x$age<-NULL
x$gender<-NULL
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="psychtools_bfi.Rdata")

## 4-blot, 15
load("blot.rda")
x<-blot
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df$item<-gsub(' ','',df$item)
save(df,file="psychtools_blot.Rdata")

## 5-epi, 27
load("epi.rda")
x<-epi
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df$resp<-df$resp-1
save(df,file="psychtools_epi.Rdata")

## 6-GERAS, 33
load("GERAS.rda")
x<-GERAS.items
id<-1:nrow(x)
gender<-x$gender
x$gender<-NULL
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],gender=gender,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="psychtools_geras.Rdata")

## 7-msq, 45
load("msq.rda")
x<-msq
id<-paste(x$exper,x$ID)
test<-!duplicated(id)
x<-x[test,]
id<-id[test]
x<-x[,1:75]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="psychtools_msq.Rdata")

## 8-sai, 70
load("sai.rda")
x<-sai
id<-paste(x$study,x$id)
occasion<-x$time
x<-x[,-(1:3)]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],occasion=occasion,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="psychtools_sai.Rdata")

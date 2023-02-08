## acl, 8
load("acl.rda")
#(0 = completely disagree, 1 = disagree,
#    2 = agree nor disagree, 3 = agree, 4 = completely agree)
x<-acl
id<-1:nrow(x)
L<-list()
## Communality Items 1-10 Change Items 111-119
## Achievement Items 11-20 Succorance Items 120-129
## Dominance Items 21-30 Abasement Items 130-139
## Endurance Items 31-40 Deference* Items 140-149
## Order Items 41-50 Personal Adjustment Items 150-159
## Intraception Items 51-60 Ideal Self Items 160-169
## Nurturance Items 61-70 Critical parent Items 170-179
## Affiliation Items 71-80 Nurturant parent Items 180-189
## Exhibition Items 81-90 Adult Items 190-199
## Autonomy Items 91-100 Free Child Items 200-209
## Aggression Items 101-110 Adapted Child Items 210-218
f<-function(x,n) rep(x,length(n))
scales<-c(f("Communality",1:10),
  f("Achievment",11:20),
  f("Dominance",21:30),
  f("Endurance",31:40),
  f("Order",41:50),
  f("Intraception",51:60),
  f("Nurturance",61:70),
  f("Affiliation",71:80),
  f("Exhibitiion",81:90),
  f("Autonomy",91:100),
  f("Aggression",101:110),
  f("Change",111:119),
  f("Succorance",120:129),
  f("Abasement",130:139),
  f("Deference*",140:149),
  f("Personal Adjustment",150:159),
  f("Ideal self",160:169),
  f("Critical parent",170:179),
  f("Nurturant parent",180:189),
  f("Adult",190:199),
  f("Free child",200:209),
  f("Adapter child",210:218))
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],scale=scales[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="acl_mokken.Rdata")

## autonomySupport, 12
load("autonomySupport.rda")
x<-autonomySupport
L<-list()
for (i in 1:nrow(x)) {
    for (j in 2:ncol(x)) {
        L[[paste(i,j)]]<-data.frame(id=x$Teacher[i],rater=i,item=names(x)[j],resp=x[i,j])
    }
}
df<-data.frame(do.call("rbind",L))
save(df,file="autonomysupport_mokken.Rdata")

## balance, 13
load("balance.rda")
x<-balance
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="balance_mokken.Rdata")

## cavalini, 14
load("cavalini.rda")
x<-cavalini
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="cavalini_mokken.Rdata")


## DS14, 34
load("DS14.rda")
x<-data.frame(DS14)
##recoding two as per instructions
x[,3]<-abs(5-x[,3])
x[,5]<-abs(5-x[,3])
id<-1:nrow(x)
L<-list()
for (i in 3:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],age=x$Age,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="ds14_mokken.Rdata")

## mcmi, 37
load("mcmi.rda")
x<-data.frame(mcmi)
Q<-attributes(mcmi)$Q
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
##
rownames(Q)<-names(x)
names(Q)<-paste("Qmatrix",names(Q),sep="__")
Q$item<-rownames(Q)
attr(df,which='item')<-Q
save(df,file="mcmi_mokken.Rdata")

## SWMD, 57
load("SWMD.rda")
x<-data.frame(SWMD)
L<-list()
for (i in 1:nrow(x)) {
    for (j in 2:ncol(x)) {
        L[[paste(i,j)]]<-data.frame(id=x$classId[i],rater=i,item=names(x)[j],resp=x[i,j])
    }
}
df<-data.frame(do.call("rbind",L))
save(df,file="swmd_mokken.Rdata")

## transreas, 60
load("transreas.rda")
x<-data.frame(transreas)
id<-1:nrow(x)
L<-list()
for (i in 2:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],grade=x$Groep)
df<-data.frame(do.call("rbind",L))
save(df,file="transreas_mokken.Rdata")

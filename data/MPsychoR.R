## ASTI
load("ASTI.rda")
x<-ASTI
id<-1:nrow(x)
ii<-grep("^ASTI",names(x))
x<-x[,ii]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_asti.Rdata")

## AvalanchePrep
load("AvalanchePrep.rda")
x<-AvalanchePrep
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df$resp<-as.numeric(as.character(df$resp))
save(df,file="mpsycho_avlancheprep.Rdata")

## BSSS
load("BSSS.rda")
x<-BSSS
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_bsss.Rdata")

## CEAQ
load("CEAQ.rda")
x<-CEAQ
id<-1:nrow(x)
age<-x$age
ii<-grep("^ceaq",names(x))
x<-x[,ii]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],age=age)
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_ceaq.Rdata")

## condom
load("condom.rda")
x<-condom
id<-1:nrow(x)
x<-x[,1:6]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_condom.Rdata")

## Lakes
load("Lakes.rda")
df<-Lakes
names(df)<-c("id","rater","item","resp","subtest")
save(df,file="mpsycho_lakes.Rdata")

## learnemo
load("learnemo.rda")
x<-learnemo
id<-1:nrow(x)
ii<-grep("^pc",names(x))
x<-x[,ii]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_learnemo.Rdata")

## Rmotivation
load("Rmotivation.rda")
x<-Rmotivation
id<-1:nrow(x)
x<-x[,1:36]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_Rmotivation.Rdata")

## ## Rogers
## load("Rogers.rda")
## x<-Rogers
## id<-1:nrow(x)
## L<-list()
## for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
## df<-data.frame(do.call("rbind",L))
## save(df,file="mpsycho_Rogers.Rdata")

## ## Rogers_Adolescent
## load("Rogers_Adolescent.rda")
## x<-Rogers_Adolescent
## id<-1:nrow(x)
## L<-list()
## for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
## df<-data.frame(do.call("rbind",L))
## save(df,file="mpsycho_Rogers_adolescent.Rdata")

## Rogers & Rogers_Adolescent
load("Rogers.rda")
x<-Rogers
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df$cov_sample<-'adult'
load("Rogers_Adolescent.rda")
x<-Rogers_Adolescent
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df1<-data.frame(do.call("rbind",L))
df1$cov_sample<-'adolescent'
df<-data.frame(rbind(df,df1))
##https://github.com/ben-domingue/irw/issues/1239#issuecomment-3673618435
ocd<-c("obtime", "obinterfer", "obdistress", "obresist", "obcontrol", "comptime","compinterf", "compdis", "compresis", "compcont")
test<-df$item %in% ocd
ocd<-df[test,]
dep<-df[!test,]
ocd$id<-paste(ocd$id,ocd$cov_sample,sep='--')
dep$id<-paste(dep$id,dep$cov_sample,sep='--')
write.csv(ocd,file="mpsycho_rogers_ocd.csv",quote=FALSE,row.names=FALSE)
write.csv(dep,file="mpsycho_rogers_depression.csv",quote=FALSE,row.names=FALSE)


## RWDQ
load("RWDQ.rda")
x<-RWDQ
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_rwdq.Rdata")

## SDOwave

## Wenchuan
load("Wenchuan.rda")
x<-Wenchuan
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_wenchuan.Rdata")

## Wilmer
load("Wilmer.rda")
x<-Wilmer
id<-1:nrow(x)
age<-x$age
x<-x[,-(1:2)]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],age=age)
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_wilmer.Rdata")

## WilPat
load("WilPat.rda")
x<-WilPat
z<-data.frame()
id<-1:nrow(x)
z<-data.frame(id=id)
for (nm in c("Country","LibCons","LeftRight","Gender","Age")) {
    z[[nm]]<-x[[nm]]
    x[[nm]]<-NULL
}
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(item=names(x)[i],resp=x[,i],z)
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_wilpat.Rdata")

## YouthDep
load("YouthDep.rda")
x<-YouthDep
id<-1:nrow(x)
race<-x$race
x$race<-NULL
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],race=race)
df<-data.frame(do.call("rbind",L))
df$resp<-as.numeric(as.character(df$resp))
save(df,file="mpsycho_YouthDep.Rdata")

## zareki
load("zareki.rda")
x<-zareki
id<-1:nrow(x)
x$class<-x$time<-NULL
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mpsycho_zareki.Rdata")



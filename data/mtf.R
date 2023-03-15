##initial prep work done by colleagues at columbia
##see 'MTF Code wrangling Internalizing.sas'

#library(sas7bdat)
#x<-read.sas7bdat("imputedallyears_81012_3142023.sas7bdat")
#save(x,file="imputedallyears_81012_3142023.Rdata")
load("imputedallyears_81012_3142023.Rdata")


x$id<-1:nrow(x) #x$id

L<-list()
## 5. lonelniess
z<-x[x$Lone_scoremiss==3,]
z0<-z[,c("lonely","leftout","wishfrd")]
for (i in 1:ncol(z0)) {
    nm<-names(z0)[i]
    nm<-paste0("loneliness__",nm)
    L[[nm]]<-data.frame(id=z$id,year=z$year,grade=z$grade,item=nm,resp=z0[,i])
}

## 1. self-derogation
z<-x[x$Dero_scoremiss==4,]
z0<-z[,c("notproud","nogood","nothingright","notuseful")]
for (i in 1:ncol(z0)) {
    nm<-names(z0)[i]
    nm<-paste0("selfderogation__",nm)
    L[[nm]]<-data.frame(id=z$id,year=z$year,grade=z$grade,item=nm,resp=z0[,i])
}

## 2. self-esteem: Esteem1 Esteem2 Esteem3 Esteem4
z<-x[x$Esteem_scoremiss==4,]
z0<-z[,c("pos_att","eq_worth","wellothers","satisfied")]
for (i in 1:ncol(z0)) {
    nm<-names(z0)[i]
    nm<-paste0("selfesteem__",nm)
    L[[nm]]<-data.frame(id=z$id,year=z$year,grade=z$grade,item=nm,resp=z0[,i])
}

## 3. depressive affect: dep1 dep2 dep3 dep4
z<-x[x$Dep_scoremiss==4,]
z0<-z[,c("nolifemean","enjoylife","fut_nohope","goodalive")]
for (i in 1:ncol(z0)) {
    nm<-names(z0)[i]
    nm<-paste0("depress__",nm)
    L[[nm]]<-data.frame(id=z$id,year=z$year,grade=z$grade,item=nm,resp=z0[,i])
}

##
df<-data.frame(do.call("rbind",L))
table(df$item,df$resp)

save(df,file="mtf.Rdata")

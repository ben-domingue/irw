##https://osf.io/pyb8s/wiki/home/


x<-read.csv("data.csv")

index<-grep("^q",names(x))
resp<-list()
for (i in index) resp[[i]]<-data.frame(id=x$id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",resp))


person<-x[,c("id","date","time","gender","age","natlangs","dyslexia","education","countries","elogit")]
attr(df,which='id')<-person

save(df,file="criticalperiod.Rdata")

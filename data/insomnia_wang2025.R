x<-read.csv("isi_bifactor_dat.csv")
id<-1:nrow(x)
for (nm in c("ASLEC","ISI","PHQ")) {
    ii<-grep(nm,names(x))
    L<-list()
    for (i in ii) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
    df<-data.frame(do.call("rbind",L))
    print(table(df$item,df$resp))
    nm<-paste(nm,"_insomnia_wang2025.csv",sep='')
    nm<-tolower(nm)
    print(nm)
    write.csv(df,nm,row.names=FALSE,quote=FALSE)
}

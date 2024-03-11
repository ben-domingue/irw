x.all<-read.csv("data-final.csv",sep="\t",header=TRUE)

#df<-x[sample(1:nrow(x),10000),1:50]

for (nm in c("EXT","EST","AGR","CSN","OPN")) {
    ii<-paste(nm,1:10,sep='')
    x<-x.all[,ii]
    for (i in 1:ncol(x)) {
        x[,i]<-as.numeric(x[,i])
        x[,i]<-ifelse(x[,i]==0,NA,x[,i])
    }
    ##respose time
    ii<-paste(nm,1:10,"_E",sep='')
    t<-x.all[,ii]
    for (i in 1:ncol(x)) {
        t[,i]<-as.numeric(t[,i])/1000
    }
    ## for (i in 1:ncol(x)) {
    ##     rs<-rowMeans(x[,-i],na.rm=TRUE)
    ##     rho<-cor(x[,i],rs,use='p')
    ##     print(rho)
    ##     if (rho<0) x[,i]<-6-x[,i]
    ## }
    names(x)<-paste("item_",1:ncol(x),sep='')
    id<-1:nrow(x)
    L<-list()
    for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],rt=t[,i])
    df<-data.frame(do.call("rbind",L))

    save(df,file=paste("ffm_",nm,".Rdata",sep=""))
}


##removing negative rt values

for (fn in c("ffm_CSN","ffm_EXT", "ffm_AGR","ffm_EST", "ffm_OPN")) {
    fn<-paste0(fn,".Rdata")
    load(fn)
    print(summary(df$rt))
    df$rt<-ifelse(df$rt<0,NA,df$rt)
    print(summary(df$rt))
    save(df,file=fn)
}

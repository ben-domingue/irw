x.all<-read.csv("data-final.csv",sep="\t",header=TRUE)

#df<-x[sample(1:nrow(x),10000),1:50]

for (nm in c("EXT","EST","AGR","CSN","OPN")) {
    ii<-paste(nm,1:10,sep='')
    x<-x.all[,ii]
    for (i in 1:ncol(x)) {
        x[,i]<-as.numeric(x[,i])
        x[,i]<-ifelse(x[,i]==0,NA,x[,i])
    }
    for (i in 1:ncol(x)) {
        rs<-rowMeans(x[,-i],na.rm=TRUE)
        rho<-cor(x[,i],rs,use='p')
        print(rho)
        if (rho<0) x[,i]<-6-x[,i]
    }
    names(x)<-paste("item_",1:ncol(x),sep='')
    id<-1:nrow(x)
    L<-list()
    for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
    df<-data.frame(do.call("rbind",L))
    save(df,file=paste("ffm_",nm,".Rdata",sep=""))
}

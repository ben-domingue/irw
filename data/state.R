
#################################################################################################
##dichotomous items

list.files(pattern="*_2007_.+responses.txt")->lf
for (i in 1:length(lf)) {
    lf[i]->fn
    read.table(fn,header=TRUE)->x
    names(x)<-tolower(names(x))
    grep("^mc",names(x))->index
    x[,index]->x
    #
    #
    L<-list()
    for (j in 1:ncol(x)) L[[j]]<-data.frame(item=names(x)[j],id=1:nrow(x),resp=as.numeric(x[,j]))
    df<-data.frame(do.call("rbind",L))
    save(df,file=paste(gsub(".txt",".Rdata",fn),sep=""))
}

#################################################################################################
##polytomous items

list.files(pattern="*_2007_.+responses.txt")->lf
for (i in 1:length(lf)) {
    lf[i]->fn
    read.table(fn,header=TRUE)->x
    names(x)<-tolower(names(x))
    grep("^cr",names(x))->index
    x[,index]->x
    #
    #
    L<-list()
    for (j in 1:ncol(x)) L[[j]]<-data.frame(item=names(x)[j],id=1:nrow(x),resp=as.numeric(x[,j]))
    df<-data.frame(do.call("rbind",L))
    save(df,file=paste('cr_',gsub(".txt",".Rdata",fn),sep=""))
}

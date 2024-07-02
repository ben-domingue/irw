##Ben
f<-function(ii) {
    library(readxl)
    fn<-paste("QPart",ii,"Data_objects.xlsx",sep='')
    x<-as.data.frame(read_excel(fn))
    print(dim(x))
    questions<-as.character(x[1,])
    x<-x[-1,]
    ##
    rem<-grep("quality control",questions)
    questions<-questions[-rem]
    x<-x[,-rem]
    index<-grep("weird",questions)
    L.out<-list()
    for (i in 1:length(index)) {
        fn<-index[i]
        cols<-fn:(fn+6)
        col.qu<-questions[cols]
        x2<-x[,cols]
        obj<-x[,fn+7]
        tab<-table(obj)
        print(tab)
        obj<-names(tab)[which.max(tab)]
        ##
        rater<-x[,9]
        id<-obj
        L<-list()
        for (j in 1:ncol(x2)) L[[j]]<-data.frame(id=obj,
                                                 rater=rater,
                                                 item=col.qu[j],
                                                 resp=as.numeric(x2[,j]),
                                                 form=ii)
        L.out[[i]]<-data.frame(do.call("rbind",L))
    }
    df<-data.frame(do.call("rbind",L.out))
    df
}
L<-list()
for (i in 1:8) L[[i]]<-f(i)
df<-data.frame(do.call("rbind",L))

test<-grepl("How hard is it to identify",df$item)
df$item<-ifelse(test,'How hard to identify the image',df$item)

                                             
## ##Roza
## library(readxl)
## y <- read_excel("QPart1Data_objects.xlsx")
## x=y[, 19:190 ]
## colnames(x)<-x[1,]
## x<-x[-1,]
## x=x[,-grep("Text", colnames(x)) ]
## x=x[, -grep("quality", colnames(x))]
## n=dim(x)[2]/8
## rater.id= y$IPAddress[-1]
## L=list()
## for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
## df=data.frame()
## for (i in 1:n){
##   l=L[[i]][,-8]
##   id=L[[i]][1,8]
##   m=list()
##   for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
##   for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
##   d<-data.frame(do.call("rbind",m))
##   df=rbind(df, d)
## }
## df1=df


## y <- read_excel("QPart2Data_objects.xlsx")
## x=y[, 19:190 ]
## colnames(x)<-x[1,]
## x<-x[-1,]
## x=x[,-grep("Text", colnames(x)) ]
## x=x[, -grep("quality", colnames(x))]
## n=dim(x)[2]/8
## rater.id= y$IPAddress[-1]
## L=list()
## for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
## df=data.frame()
## for (i in 1:n){
##   l=L[[i]][,-8]
##   id=L[[i]][1,8]
##   m=list()
##   for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
##   for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
##   d<-data.frame(do.call("rbind",m))
##   df=rbind(df, d)
## }
## df2=df


## y <- read_excel("QPart3Data_objects.xlsx")
## x=y[, 19:190 ]
## colnames(x)<-x[1,]
## x<-x[-1,]
## x=x[,-grep("Text", colnames(x)) ]
## x=x[, -grep("quality", colnames(x))]
## n=dim(x)[2]/8
## rater.id= y$IPAddress[-1]
## L=list()
## for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
## df=data.frame()
## for (i in 1:n){
##   l=L[[i]][,-8]
##   id=L[[i]][1,8]
##   m=list()
##   for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
##   for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
##   d<-data.frame(do.call("rbind",m))
##   df=rbind(df, d)
## }
## df3=df


## y <- read_excel("QPart4Data_objects.xlsx")
## x=y[, 19:190 ]
## colnames(x)<-x[1,]
## x<-x[-1,]
## x=x[,-grep("Text", colnames(x)) ]
## x=x[, -grep("quality", colnames(x))]
## n=dim(x)[2]/8
## rater.id= y$IPAddress[-1]
## L=list()
## for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
## df=data.frame()
## for (i in 1:n){
##   l=L[[i]][,-8]
##   id=L[[i]][1,8]
##   m=list()
##   for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
##   for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
##   d<-data.frame(do.call("rbind",m))
##   df=rbind(df, d)
## }
## df4=df


## y <- read_excel("QPart5Data_objects.xlsx")
## x=y[, 19:190 ]
## colnames(x)<-x[1,]
## x<-x[-1,]
## x=x[,-grep("Text", colnames(x)) ]
## x=x[, -grep("quality", colnames(x))]
## n=dim(x)[2]/8
## rater.id= y$IPAddress[-1]
## L=list()
## for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
## df=data.frame()
## for (i in 1:n){
##   l=L[[i]][,-8]
##   id=L[[i]][1,8]
##   m=list()
##   for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
##   for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
##   d<-data.frame(do.call("rbind",m))
##   df=rbind(df, d)
## }
## df5=df


## y <- read_excel("QPart6Data_objects.xlsx")
## x=y[, 19:190 ]
## colnames(x)<-x[1,]
## x<-x[-1,]
## x=x[,-grep("Text", colnames(x)) ]
## x=x[, -grep("quality", colnames(x))]
## n=dim(x)[2]/8
## rater.id= y$IPAddress[-1]
## L=list()
## for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
## df=data.frame()
## for (i in 1:n){
##   l=L[[i]][,-8]
##   id=L[[i]][1,8]
##   m=list()
##   for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
##   for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
##   d<-data.frame(do.call("rbind",m))
##   df=rbind(df, d)
## }
## df6=df

## y <- read_excel("QPart7Data_objects.xlsx")
## x=y[, 19:190 ]
## colnames(x)<-x[1,]
## x<-x[-1,]
## x=x[,-grep("Text", colnames(x)) ]
## x=x[, -grep("quality", colnames(x))]
## n=dim(x)[2]/8
## rater.id= y$IPAddress[-1]
## L=list()
## for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
## df=data.frame()
## for (i in 1:n){
##   l=L[[i]][,-8]
##   id=L[[i]][1,8]
##   m=list()
##   for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
##   for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
##   d<-data.frame(do.call("rbind",m))
##   df=rbind(df, d)
## }
## df7=df

## y <- read_excel("QPart8Data_objects.xlsx")
## x=y[, 19:190 ]
## colnames(x)<-x[1,]
## x<-x[-1,]
## x=x[,-grep("Text", colnames(x)) ]
## x=x[, -grep("quality", colnames(x))]
## n=dim(x)[2]/8
## rater.id= y$IPAddress[-1]
## L=list()
## for (i in 1:n) L[[i]]<-x[,((i-1)*8+1):(i*8)]
## df=data.frame()
## for (i in 1:n){
##   l=L[[i]][,-8]
##   id=L[[i]][1,8]
##   m=list()
##   for (j in 1:ncol(l)) m[[j]]=data.frame(rater.id=rater.id, id=id, item=colnames(l)[j], resp=x[,j])
##   for (i in 1:ncol(l)) colnames(m[[i]])<-c("rater.id", "id", "item", "resp")
##   d<-data.frame(do.call("rbind",m))
##   df=rbind(df, d)
## }
## df8=df

## d=rbind(df1, df2, df3, df4, df5, df6, df7, df8)
## save(d, file='Object.stimulus.set.Rdata')

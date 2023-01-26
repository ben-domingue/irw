library(diffIRT)
data(rotation)
acc<-rotation[,1:10]
rt<-rotation[,11:20]

id<-1:nrow(rt)
item<-1:ncol(rt)
L<-list()
for (i in 1:ncol(rt)) {
    L[[i]]<-data.frame(resp=acc[,i],rt=rt[,i],id=id,item=item[i])
}
x<-data.frame(do.call("rbind",L))
#x$rt<-log(x$rt)
df<-x[!is.na(x$rt),]

save(df,file="dd_rotation.Rdata")

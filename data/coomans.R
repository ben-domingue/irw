#https://journals.plos.org/plosone/article/authors?id=10.1371/journal.pone.0155149
lf<-c("addition.RData","division.RData","letterchaos.RData","multiplication.RData","subtraction.RData","set.RData")

for (fn in lf) {
    load(fn)
    x<-res_max2
    x<-x[order(x$days),]
    id<-paste(x$user_id,x$item_id)
    x<-x[!duplicated(id),]
    ##
    x<-x[,c("user_id","item_id","response_in_milliseconds","correct_answered","days")]
    names(x)<-c("id","item","rt","resp","days")
    x$id<-paste(x$id,x$days) #round(x$days/10))
    x$rt<-x$rt/1000
    #
    df<-x
    save(df,file=paste("coomans",fn,sep=''))
}

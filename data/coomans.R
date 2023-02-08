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
    names(x)<-c("id","item","rt","resp","date")
    x$rt<-x$rt/1000
    ##date
    m<-min(x$date,na.rm=TRUE)
    x$date<-x$date-m
    secperday<-24*60*60
    x$date<-x$date*secperday
    #
    df<-x
    ##
    fn2<-gsub("RData","Rdata",fn)
    save(df,file=paste("coomans",fn2,sep=''))
}

long2resp<-function(df) {
    L<-split(df,df$id)
    items<-unique(df$item)
    f<-function(x) {
        index<-match(items,x$item)
        x$resp[index]
    }
    resp<-sapply(L,f)
    t(resp)
}

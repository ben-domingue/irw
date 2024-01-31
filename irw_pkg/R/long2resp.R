long2resp<-function(df) {
    items<-unique(df$item)
    if (all(items %in% 1:length(items))) {
        df$item<-paste("item_",df$item,sep='')
        items<-unique(df$item)
    }
    L<-split(df,df$id)
    f<-function(x) {
        index<-match(items,x$item)
        x$resp[index]
    }
    resp<-sapply(L,f)
    resp<-t(resp)
    colnames(resp)<-items
    resp<-data.frame(resp)
    resp$id<-names(L)
    resp
}

getp<-function(m,ability='EAP',id,
               x #dataframe containing oos to merge in
               ) {
    co<-coef(m)
    nms<-names(co)
    co<-do.call("rbind",co[-length(co)])
    item<-data.frame(item=nms[-length(nms)],co)
    ##
    th<-fscores(m,method=ability)
    stud<-data.frame(id=id,th=th[,1])
    ##
    x<-merge(x[x$oos==1,],stud)
    x<-merge(x,item)
    ##
    kk<-x$th*x$a+x$d
    kk<-exp(kk)
    x$p<-x$g+(x$u-x$g)*kk/(1+kk)
    x
}


reliability<-function(fn,max.item=100) { ##see eqn at top of section 3.1, https://www.citrenz.ac.nz/conferences/2007/151.pdf
    print(fn)
    load(fn)
    k<-length(unique(df$item))
    ## if (k>max.item) {
    ##     items<-sample(unique(df$item),max.item)
    ##     df<-df[df$item %in% items,]
    ##     k<-length(unique(df$item))
    ## }
    ids<-unique(df$id)
    #L<-split(df[,c("id","resp")],df$item)
    df0<-data.frame(id=ids)
    items<-unique(df$item)
    #
    if (k>max.item) {
        gr<-floor(k/100)
        groups<-sample(1:gr,k,replace=TRUE)
    } else groups<-rep(1,k)
    #
    getresp<-function(x,df0) {
        x<-merge(df0,x,all.x=TRUE)
        x$resp
    }
    coors<-list()
    for (i in unique(groups)) {
        item.tmp<-items[groups==i]
        tmp<-df[df$item %in% item.tmp,]
        L<-split(tmp[,c("id","resp")],tmp$item)
        L<-lapply(L,getresp,df0=df0)
        tmp<-do.call("cbind",L)
        r<-cor(tmp,use='p')
        coors[[i]]<-r[upper.tri(r,diag=FALSE)]
    }
    r<-mean(unlist(coors))
    alpha<-k*r/(1+(k-1)*r)
    alpha
}

lf<-list.files(pattern="*.Rdata")
test<-grepl("misc.Rdata",lf,fixed=TRUE)
lf<-lf[!test]
omit.list<-c("duolingo__listen.Rdata","duolingo__reverse_tap.Rdata","duolingo__reverse_translate.Rdata","geography.Rdata",
             'mq_supremecourt.Rdata', #too sparse
             'rr98_accuracy.Rdata' #repeated trials
             )
lf<-lf[!(lf %in% omit.list)]

alpha<-sapply(lf,reliability)


##                abortion.Rdata    c1_2007_10_responses.Rdata     c1_2007_3_responses.Rdata 
##                          0.87                          0.83                          0.87 
##     c1_2007_4_responses.Rdata     c1_2007_5_responses.Rdata     c1_2007_6_responses.Rdata 
##                          0.92                          0.91                          0.91 
##     c1_2007_7_responses.Rdata     c1_2007_8_responses.Rdata     c1_2007_9_responses.Rdata 
##                          0.91                          0.90                          0.90 
##     c3_2007_5_responses.Rdata     c3_2007_6_responses.Rdata     c3_2007_7_responses.Rdata 
##                          0.92                          0.91                          0.88 
##     c3_2007_8_responses.Rdata     c3_2007_9_responses.Rdata                   chess.Rdata 
##                          0.86                          0.85                          0.94 
## cr_c1_2007_10_responses.Rdata  cr_c1_2007_3_responses.Rdata  cr_c1_2007_4_responses.Rdata 
##                          0.83                          0.66                          0.81 
##  cr_c1_2007_5_responses.Rdata  cr_c1_2007_6_responses.Rdata  cr_c1_2007_7_responses.Rdata 
##                          0.84                          0.83                          0.82 
##  cr_c1_2007_8_responses.Rdata  cr_c1_2007_9_responses.Rdata  cr_c3_2007_5_responses.Rdata 
##                          0.85                          0.85                          0.82 
##  cr_c3_2007_6_responses.Rdata  cr_c3_2007_7_responses.Rdata  cr_c3_2007_8_responses.Rdata 
##                          0.85                          0.80                          0.83 
##  cr_c3_2007_9_responses.Rdata     criticalperiod_resp.Rdata             dd_rotation.Rdata 
##                          0.79                          0.86                          0.64 
##                  duval4.Rdata                  duval8.Rdata                    enem.Rdata 
##                          0.91                          0.95                          0.72 
##                 ffm_AGR.Rdata                 ffm_CSN.Rdata                 ffm_EST.Rdata 
##                          0.84                          0.82                          0.87 
##                 ffm_EXT.Rdata                 ffm_OPN.Rdata                  frac20.Rdata 
##                          0.89                          0.80                          0.94 
##                    grit.Rdata                    lsat.Rdata                mobility.Rdata 
##                          0.83                          0.29                          0.79 
##                  motion.Rdata                   nshap.Rdata         pks_probability.Rdata 
##                          0.68                          0.75                          0.88 
##              quantshort.Rdata            roar_lexical.Rdata                     sds.Rdata 
##                          0.74                          0.98                          0.71 
##                     tma.Rdata                    wirs.Rdata                 wordsum.Rdata 
##                          0.91                          0.44                          0.64 

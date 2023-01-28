f<-function(fn,nsamp=25000) { ##to add: cronbach's alpha
    print(fn)
    load(fn)
    ##
    person.n<-length(unique(df$id))
    item.n<-length(unique(df$item))
    n<-length(df$resp)
    ncat<-length(unique(df$resp[!is.na(df$resp)]))
    per<-(person.n/sqrt(n))*(item.n/sqrt(n))
    resp.per.person<-mean(as.numeric(table(df$id)))
    resp.per.item<-mean(as.numeric(table(df$item)))
    ##
    if (is.numeric(nsamp)) {
        nn<-nrow(df)
        if (nn>nsamp) {
            ii<-sample(1:nn,nsamp)
            df<-df[ii,]
        }
    }
    df<-df[!is.na(df$resp),]
    tmp<-df[,c("item","resp")]
    tmp$resp<-as.numeric(tmp$resp)
    L<-split(tmp,tmp$item)
    ff<-function(x) x$resp/max(x$resp,na.rm=TRUE)
    L<-lapply(L,ff)
    mean.resp<-mean(unlist(L),na.rm=TRUE)
    ##
    c(nresp=n,ncat=ncat,person.n=person.n,item.n=item.n,sparse=per,resp.per.person=resp.per.person,resp.per.item=resp.per.item,mean=mean.resp)
}

lf<-NULL #lf<-c('hads_multilcirt.Rdata','naep_multilcirt.Rdata')
if (is.null(lf)) lf<-list.files(pattern="*.Rdata")
test<-grepl("misc.Rdata",lf,fixed=TRUE)
lf<-lf[!test]
tab<-t(sapply(lf,f))
tab<-data.frame(tab)
tab<-tab[order(tab$sparse),]

tab
write.csv(tab,'')


lf<-NULL 
f<-function(fn,nsamp=25000) { 
    print(fn)
    load(fn)
    ##
    person.n<-length(unique(df$id))
    item.n<-length(unique(df$item))
    n<-length(df$resp)
    ncat<-length(unique(df$resp[!is.na(df$resp)]))
    per<-(sqrt(n)/person.n)*(sqrt(n)/item.n)
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
    date.index<-('date' %in% names(df))
    rater.index<-('rater' %in% names(df))
    rt.index<-('rt' %in% names(df))
    ##
    c(nresp=n,ncat=ncat,person.n=person.n,item.n=item.n,sparse=per,resp.per.person=resp.per.person,resp.per.item=resp.per.item,mean=mean.resp,rt=rt.index,date=date.index,rater=rater.index)
}


#lf<-c("mpsycho_asti.Rdata","mpsycho_avlancheprep.Rdata","mpsycho_bsss.Rdata","mpsycho_ceaq.Rdata","mpsycho_condom.Rdata","mpsycho_lakes.Rdata","mpsycho_learnemo.Rdata","mpsycho_Rmotivation.Rdata","mpsycho_Rogers.Rdata","mpsycho_Rogers_adolescent.Rdata","mpsycho_rwdq.Rdata","mpsycho_wenchuan.Rdata","mpsycho_wilmer.Rdata","mpsycho_wilpat.Rdata","mpsycho_YouthDep.Rdata","mpsycho_zareki.Rdata")
if (is.null(lf)) lf<-list.files(pattern="*.Rdata")
tab<-t(sapply(lf,f))
tab<-data.frame(tab)
ss<-tab[order(tab$sparse),]


write.csv(ss,'')

save(ss,file="~/Dropbox/projects/irw/src/snapshot.Rdata")













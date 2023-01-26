
reliability<-function(fn) { ##see eqn at top of section 3.1, https://www.citrenz.ac.nz/conferences/2007/151.pdf
    print(fn)
    load(fn)
    k<-length(unique(df$item))
    if (k>250) {
        items<-sample(unique(df$item),250)
        df<-df[df$item %in% items,]
        k<-length(df$item)
    }
    ids<-unique(df$id)
    L<-split(df[,c("id","resp")],df$item)
    df0<-data.frame(id=ids)
    getresp<-function(x,df0) {
        x<-merge(df0,x,all.x=TRUE)
        x$resp
    }
    L<-lapply(L,getresp,df0=df0)
    if (k>50) {
        gr<-floor(k/25)
        groups<-sample(1:gr,k,replace=TRUE)
    } else groups<-rep(1,k)
    coors<-list()
    for (i in unique(groups)) {
        tmp<-L[groups==i]
        tmp<-do.call("cbind",tmp)
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
omit.list<-c("duolingo__listen.Rdata","duolingo__reverse_tap.Rdata","duolingo__reverse_translate.Rdata","geography.Rdata")
lf<-lf[!(lf %in% omit.list)]

library(parallel)
alpha<-mclapply(lf,reliability,mc.cores=3)



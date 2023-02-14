
reliability<-function(df,max.item=100) { ##see eqn at top of section 3.1, https://www.citrenz.ac.nz/conferences/2007/151.pdf
    k<-length(unique(df$item))
    ids<-unique(df$id)
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
    r<-mean(unlist(coors),na.rm=TRUE)
    alpha<-k*r/(1+(k-1)*r)
    alpha
}

reliability_traditional<-function(df) {
    library(psych)
    x<-df[,c("id","item","resp")]
    L<- split(x,x$item)
    f<-function(x) {
        nm<-unique(x$item)
        x$item<-NULL
        names(x)[2]<-nm
        x
    }
    L<-lapply(L,f)
    x<-L[[1]]
    for (i in 2:length(L)) x<-merge(x,L[[i]],all=TRUE)
    z<-alpha(x[,-1],check.keys=TRUE)
    z$total$raw_alpha
}

load("../src/snapshot.Rdata")
ss<-ss[ss$nresp>250,]
ss<-ss[ss$sparse<=1 & ss$sparse>.01,]
#z<-ss$resp.per.person/ss$resp.per.item
#ss<-ss[z>1,] ##woa
ss<-ss[ss$item.n<2000,]
lf<-rownames(ss)

alpha<-alpha_trad<-numeric()
for (i in 1:length(lf)) {
    fn<-lf[i]
    print(fn)
    load(fn)
    k<-length(unique(df$item))
    if (k<100) alpha_trad[i]<-reliability_traditional(df) else alpha_trad[i]<-NA
    if (is.na(alpha_trad[i])) alpha[i]<-reliability(df) else alpha[i]<-NA
}

z<-data.frame(fn=lf,a=alpha,at=unlist(alpha_trad))
alpha<-ifelse(is.na(z$at),z$a,z$at)

z<-z[z$a> -1,]
plot(z[,-1],pch=19); abline(0,1)


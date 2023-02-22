
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
    c(alpha,k)
}

reliability_traditional<-function(df) {
    k<-length(unique(df$item))
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
    c(z$total$raw_alpha,k)
}

load("../src/snapshot.Rdata")
ss<-ss[ss$nresp>250,]
ss<-ss[ss$sparse<=1 & ss$sparse>.01,]
#z<-ss$resp.per.person/ss$resp.per.item
#ss<-ss[z>1,] ##woa
ss<-ss[ss$item.n<1000,]
lf<-rownames(ss)

alpha<-alpha_trad<-list()
for (i in 1:length(lf)) {
    fn<-lf[i]
    print(fn)
    load(fn)
    k<-length(unique(df$item))
    if (k<100) alpha_trad[[i]]<-reliability_traditional(df) else alpha_trad[[i]]<-NA
    noise<-runif(1) #this is just to get reliabilites for some for comparison
    if (is.na(alpha_trad[[i]][1]) | noise>.8) alpha[[i]]<-reliability(df) else alpha[[i]]<-NA
}

alpha<-do.call("rbind",alpha)
k1<-alpha[,2]
alpha<-alpha[,1]
alpha_trad<-do.call("rbind",alpha_trad)
k2<-alpha_trad[,2]
alpha_trad<-alpha_trad[,1]

z<-data.frame(fn=lf,a=alpha,at=unlist(alpha_trad))
alpha<-ifelse(is.na(z$at),z$a,z$at)
kk<-ifelse(!is.na(k2),k2,k1)

cor(alpha,kk,method='spearman')


load("../src/snapshot.Rdata")
z<-ss[ss$rt==1,]
lf<-rownames(z)

den<-list()
for (fn in lf) {
    load(fn)
    z<-df$rt
    z<-z[z>0]
    qu<-quantile(z,.99,na.rm=TRUE)
    z<-z[z<qu]
    den[[fn]]<-density(log(z),na.rm=TRUE)
}

M<-sapply(den,function(x) mean(x$x))
den<-den[order(M)]

pdf("/home/bd/Dropbox/Apps/Overleaf/IRW/alpha.pdf",width=7,height=3)
par(mfrow=c(1,2),mgp=c(2,1,0),mar=c(3,3,1,1),oma=rep(.5,4))
hist(alpha,main='',sub='',xlab='Reliability',col='blue',xlim=c(0,1),breaks=25)
##
cols<-colorRampPalette(c("blue", "red"))( length(den))
f<-function(x) c(range(x$x),range(x$y))
lims<-lapply(den,f)
lims<-do.call("rbind",lims)
xl<-c(min(lims[,1]),max(lims[,2]))
xl<-c(-5,6)
yl<-c(min(lims[,3]),max(lims[,4]))
yl<-c(0,1.5)
plot(NULL,xlim=xl,ylim=yl,xlab="log(response time)",ylab='density')
for (i in 1:length(den)) lines(den[[i]],col=cols[i])
dev.off()

imv<-function(pr,p1,p2,eps=1e-6) {
    pr$pv1<-pr[[p1]]
    pr$pv2<-pr[[p2]]
    pr$pv1<-ifelse(pr$pv1 < eps,eps,pr$pv1)
    pr$pv2<-ifelse(pr$pv2 < eps,eps,pr$pv2)
    pr$pv1<-ifelse(pr$pv1 > 1-eps,1-eps,pr$pv1)
    pr$pv2<-ifelse(pr$pv2 > 1-eps,1-eps,pr$pv2)
    ##
    ll<-function(x,p='pv') {
        z<-log(x[[p]])*x$resp+log(1-x[[p]])*(1-x$resp)
        z<-sum(z)/nrow(x)
        exp(z)
    }    
    loglik1<-ll(pr,'pv1')
    loglik2<-ll(pr,'pv2')
    getcoins<-function(a) {
        f<-function(p,a) abs(p*log(p)+(1-p)*log(1-p)-log(a))
        nlminb(.5,f,lower=0.001,upper=.999,a=a)$par
    }
    c1<-getcoins(loglik1)
    c2<-getcoins(loglik2)
    ew<-function(p1,p0) (p1-p0)/p0
    imv<-ew(c2,c1)
    imv
}

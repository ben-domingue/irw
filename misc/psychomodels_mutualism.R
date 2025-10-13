##https://www.psychomodels.org/models/mutualism-model/

getcoors<-function(df) {
    coors<-cor(df[,-1],use='p')
    coors<-coors[upper.tri(coors,diag=FALSE)]
    coors
}
df<-irw::irw_fetch("gilbert_meta_15",resp=TRUE)
c1<-getcoors(df)
df<-irw::irw_fetch("hexaco_silvia_2025",resp=TRUE)
c2<-getcoors(df)

par(mfrow=c(2,1),mgp=c(2,1,0),mar=c(3,3,1,1))
hist(c1,xlab='ravens',xlim=c(-1,1),freq=FALSE)
hist(c2,xlab='hexaco',xlim=c(-1,1),freq=FALSE)

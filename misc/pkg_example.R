#devtools::install_github("redivis/redivis-r", ref="main")
#devtools::install_github("ben-domingue/irw/irw_pkg")

##example analysis of one dataset
dataset <- redivis::user("datapages")$dataset("item_response_warehouse")
#df <- dataset$table("4thgrade_math_sirt")$to_data_frame()
df <- dataset$table("content_literacy_intervention")$to_data_frame()
items<-unique(df$item)
if (all(items %in% 1:length(items))) {
    df$item<-paste("item_",df$item,sep='')
    items<-unique(df$item)
}


##load('~/Dropbox/projects/irw/data/pub/4thgrade_math_sirt.Rdata')
library(irw)
resp<-irw::long2resp(df)



library(mirt)
id<-resp$id
resp$id<-NULL
mod.rasch<-mirt(resp,1,'Rasch')

##cross-validation for models estimated in mirt
ntimes<-4
df$gr<-sample(1:ntimes,nrow(df),replace=TRUE)
x.hold<-df
omega<-numeric()
for (i in 1:ntimes) {
    x<-x.hold
    x$oos<-ifelse(x$gr==i,1,0)
    x0<-x[x$oos==0,]
    resp0<-data.frame(irw::long2resp(x0))
    id<-resp0$id
    resp0$id<-NULL
    ##rasch model
    m0<-mirt(resp0,1,'Rasch')
    ##2pl
    ni<-ncol(resp0)
    s<-paste("F=1-",ni,"
             PRIOR = (1-",ni,", a1, lnorm, 0.0, 1.0)",sep="")
    model<-mirt.model(s)
    m1<-mirt(resp0,model,itemtype=rep("2PL",ni),method="EM",technical=list(NCYCLES=10000))
    ##
    z0<-getp(m0,x=x[x$oos==1,],id=id)
    z1<-getp(m1,x=x[x$oos==1,],id=id)
    z0<-z0[,c("item","id","resp","p")]
    names(z0)[4]<-'p1'
    z1<-z1[,c("item","id","p")]
    names(z1)[3]<-'p2'
    z<-merge(z0,z1)
    omega[i]<-imv(z,p1="p1",p2="p2")
}
mean(omega)
    

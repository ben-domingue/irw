f<-function(tab) {
    load(paste(tab,'.Rdata',sep=''))
    resp<-irwpkg::irw_long2resp(df)
    library(mirt)
    m<-mirt::mirt(resp[,-1],1,'Rasch')
    fit<-mirt::itemfit(m,'infit')
    s<-sd(fit$outfit)
    s0<-sqrt(2/nrow(fit))
    c(asymptotic=s0,estvar=s)
}

meta<-read.csv("~/Dropbox/projects/irw/src/metadata/metadata.csv")
m<-meta[meta$density>.9 & meta$density<=1 & meta$n_categories==2,]

out<-t(sapply(m$table[1:10],f))
summary(out[2,]/out[,1])

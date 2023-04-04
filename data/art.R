L<-list()
load("mac_art_17_18_19.rda")
L$mac.meld<-irt_meld
L$mac.native<-irt_native
L$mac.nonnative<-irt_nonnative

load("moh_art.rda")
L$moh.native<-irt_native_moh
L$moh.nonnative<-irt_nonnative_moh

for (i in 1:length(L)) {
    x<-L[[i]]
    id<-paste(i,1:nrow(x))
    l<-list()
    for (j in 1:ncol(x)) l[[j]]<-data.frame(id=id,item=names(x)[j],resp=x[,j])
    L[[i]]<-data.frame(do.call("rbind",l))
}

df<-data.frame(do.call("rbind",L))
save(df,file="art.Rdata")

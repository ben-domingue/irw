#MLCIRTwithin package

load("RLMS.RData")
x<-RLMS
id<-1:nrow(x)
L<-list()
for (i in 1:4) {
    nm<-paste("Y",i,sep="")
    L[[i]]<-data.frame(id=id,item=nm,resp=x[,nm])
}
df<-data.frame(do.call("rbind",L))
save(df,file="RLMS_MLCIRTwithin.Rdata")


load("SF12.RData")
x<-SF12
id<-1:nrow(x)
L<-list()
for (i in 1:12) {
    nm<-paste("Y",i,sep="")
    L[[i]]<-data.frame(id=id,item=nm,resp=x[,nm])
}
df<-data.frame(do.call("rbind",L))
save(df,file="SF12_MLCIRTwithin.Rdata")

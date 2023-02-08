load("CNES.rda")
x<-CNES
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

levs<-c("StronglyDisagree","Disagree","Agree","StronglyAgree")
ii<-match(df$resp,levs)
df$resp<-ii
save(df,file="sem_cnes.Rdata")

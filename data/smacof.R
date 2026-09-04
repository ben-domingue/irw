#PVQ40
#, 43

load("PVQ40.rda")
x<-PVQ40
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
# `df$resp>0` is NA wherever resp is NA, and subsetting by an NA index does not
# drop the row -- it inserts an all-NA one. That put six rows of id=NA,item=NA
# into the shipped table, which then read as a single respondent answering the
# same missing item six times (irw#1842 block G).
df<-df[!is.na(df$resp) & df$resp>0,]
save(df,file="smacof_pvq40.Rdata")
write.csv(df,"smacof_pvq40.csv",row.names=FALSE)

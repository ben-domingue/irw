x<- read.csv("OSF_SAM_itemlevelfullsample_orig-ratings.csv")
colnames(x)[1] <- "id"
L<-list()
for (i in 2:ncol(x)) L[[i]]<-data.frame(id=x[,1],item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df, file='Survey_AM.Rdata')


x<- read.csv("aipsychometrics_ai_raw.csv")
x=x[, c(1,209:233)]; x
colnames(x)[1] <- "id"
L<-list()
for (i in 2:ncol(x)) L[[i]]<-data.frame(id=x[,1],item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df, file='AM_followup.Rdata')



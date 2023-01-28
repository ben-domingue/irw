#pcmrs R package, emotion, tenseness

load("emotion.RData")
x<-emotion
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="emotion_pcmrs.Rdata")

load("tenseness.RData")
x<-tenseness
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="tenseness_pcmrs.Rdata")

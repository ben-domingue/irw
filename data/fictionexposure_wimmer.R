library(foreign)
x<-read.spss("AssessmentFictionExposure.sav",to.data.frame=TRUE)
test<-logical()
for (i in 1:ncol(x)) test[i]<-length(unique(x[,i]))==2
nms<-names(x)[test]
z<-x[,nms[3:200]]
for (i in 1:ncol(z)) z[,i]<-ifelse(z[,i]==0,0,1)
x<-z

id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="fictionexposure_wimmer.Rdata")

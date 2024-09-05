library(foreign)
x<-read.spss("me_N1361.sav",to.data.frame=TRUE,use.value=F)
nms<-c("negaf1_r","leg1","info1","sozn1","unt1","negaf2_r","leg2","info2","sozn2","unt2","negaf3_r","leg3_r","info3","sozn3","unt3")
y<-x[,nms]

language<-x$language
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(y)) L[[i]]<-data.frame(id=id,language=language,item=names(y)[i],resp=y[,i])
df<-data.frame(do.call("rbind",L))

save(df,file="sabers_vesper2023.Rdata")

library(rtdists)
rr98->x
x$resp<-ifelse(x$correct,1,0)
x$item<-paste("i",x$strength)
x$id<-paste(x$id,x$session)
L<-split(x,x$instruction)

x<-L$accuracy
x<-x[,c("id","resp","item","rt")]

df<-x

save(df,file="rr98_accuracy.Rdata")

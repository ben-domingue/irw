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


Ratcliff, R., & Rouder, J. N. (1998). Modeling Response Times for Two-Choice Decisions. Psychological Science, 9(5), 347-356. http://doi.org/10.1111/1467-9280.00067

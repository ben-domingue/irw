#https://link.springer.com/article/10.3758/s13428-020-01489-y#notes
library(foreign)
x<-read.spss("dat_rep.sav",to.data.frame=T)
x<-x[,1:90]
id<-1:nrow(x)

levs<-c("not at all wrong", "not too wrong", "somewhat wrong", "very wrong", 
"extremely wrong")
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
z<-match(df$resp,levs)
df$resp<-z
df<-df[!is.na(df$resp),]

save(df,file="moralfoundations_vignette.Rdata")


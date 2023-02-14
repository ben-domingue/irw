
load("MSATB.rda")
x<-MSATB
id<-1:nrow(x)
gender<-x$gender
x$gender<-NULL
L<-list()
for (i in 1:20) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],gender=gender)
df<-data.frame(do.call("rbind",L))

save(df,file="difNLR_msatb.Rdata")

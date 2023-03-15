## load("HolzingerSwineford1939.rda")
## x<-HolzingerSwineford1939
## id<-x$id
## age<-x$ageyr+(x$agemo-.5)/12
## x<-x[,paste("x",1:9,sep='')]

## L<-list()
## for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],age=age,resp=x[,i])
## df<-data.frame(do.call("rbind",L))
## save(df,file="lavaan_holzingerswineford.Rdata")

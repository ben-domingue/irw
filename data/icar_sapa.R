load("sapaICARData18aug2010thru20may2013.rdata")
nms<-ItemLists$ICAR60
x<-sapaICARData18aug2010thru20may2013[,nms]
L<-list()
id<-1:nrow(x)
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=as.numeric(x[,i]))
df<-data.frame(do.call("rbind",L))

df<-df[!is.na(df$resp),]

save(df,file="icar_sapa.Rdata")

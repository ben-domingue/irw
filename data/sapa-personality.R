load("sapaTempData696items08dec2013thru26jul2014.RData")
x<-sapaTempData696items08dec2013thru26jul2014
z<-x[,grep("^q_",names(x))]
id<-1:nrow(x)

L<-list()
for (i in 1:ncol(z)) L[[i]]<-data.frame(id=id,item=names(z)[i],resp=z[,i])
df<-data.frame(do.call("rbind",L))
df<-df[!is.na(df$resp),]

save(df,file="sapa_personality.Rdata")

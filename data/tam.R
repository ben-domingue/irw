##tam r package

#tam. data.fims.Aus.Jpn.scored; data.geiser; data.janssen; timss

load("data.fims.Aus.Jpn.scored.rda")
x<-data.fims.Aus.Jpn.scored
#
ii<-grep("^M1",names(x))
id<-1:nrow(x)
L<-list()
for (i in ii) L[[i]]<-data.frame(id=id,item=names(x)[i],country=x$country,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="fims_tam.Rdata")

load("data.geiser.rda")
x<-data.geiser
#
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="geiser_tam.Rdata")

load("data.janssen2.rda")
x<-data.janssen2
#
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="janssen2_tam.Rdata")

load("data.timssAusTwn.rda")
x<-data.timssAusTwn
#
ii<-grep("^M0",names(x))
id<-1:nrow(x)
L<-list()
for (i in ii) L[[i]]<-data.frame(id=id,item=names(x)[i],country=x$IDCNTRY,booklet=x$IDBOOK,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="timss_tam.Rdata")

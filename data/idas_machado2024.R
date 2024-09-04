library(foreign)
#x1<-read.spss("bdIDAS1.externas.sav",to.data.frame=TRUE)
#x2<-read.spss("bdIDAS2.externas.sav",to.data.frame=TRUE)
#x3<-read.spss("bdIDAS2_externas_USA.sav",to.data.frame=TRUE)
x4<-read.spss("bd.IDAS_Puro_2.sav",to.data.frame=TRUE,use.value.labels=FALSE)

ii<-grep("^IDAS",names(x4))
names(x4)[ii]
x<-x4[,ii]
apply(x,2,table)

id<-x4[,2]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

save(df,file='idas_machado2024.Rdata')

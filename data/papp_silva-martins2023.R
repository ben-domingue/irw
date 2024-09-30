x<-read.csv("PAPP_dataset.csv",sep=';')
id<-x$casenum
nm1<-paste("i",1:31,sep='')
nm2<-paste("IIi",1:31,sep='')

L<-list()
for (nm in nm1) L[[nm]]<-data.frame(id=id,item=nm,resp=x[[nm]])
df<-data.frame(do.call("rbind",L))
df$wave<-0
z<-df

x$IIi1<-x$lli1
L<-list()
for (nm in nm2) L[[nm]]<-data.frame(id=id,item=nm,resp=x[[nm]])
df<-data.frame(do.call("rbind",L))
df$wave<-1

df<-data.frame(rbind(z,df))
df<-df[!is.na(df$resp),]

save(df,file="papp_silva-martins2023.Rdata")

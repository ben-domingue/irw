read=read.csv("WMI_Read_Han_Wide.csv")[,-1]
x<-read
id<-1:nrow(x)
L<-list()
for (i in 2:ncol(x)) L[[i]]<-data.frame(id=x[,1],item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L)); df; x
save(df,file='WMI_Read_Han.Rdata')


rot=read.csv("WMI_Rot_Han_Wide.csv")[,-1]
x<-rot
id<-1:nrow(x)
L<-list()
for (i in 2:ncol(x)) L[[i]]<-data.frame(id=x[,1],item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L)); df; x
save(df,file='WMI_Rot_Han.Rdata')

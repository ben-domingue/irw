x<-read.table("Berger and Anaki disgust scale 2014_1 tab delimeted",sep="\t",header=TRUE)
x<-x[x$Catch_response==1 & x$FILTER==1,]
                                        #x<-x[x$Q12_Catch==4 & x$Q16_Catch==0,]
x$Q12_Catch<-x$Q16_Catch<-NULL

ii<-grep("^Q",names(x))
id<-1:nrow(x)
L<-list()
for (i in ii) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df$resp<-ifelse(df$resp>4,NA,df$resp)
df$resp<-ifelse(df$resp==as.integer(df$resp),df$resp,NA)

x<-x[,1:5]
names(x)<-tolower(names(x))
names(x)<-paste("cov_",names(x),sep='')
x$id<-id

df<-merge(df,x)

write.csv(df,file="disgust_berger2014.csv",quote=FALSE,row.names=FALSE)

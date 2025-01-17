##https://dataverse.harvard.edu/file.xhtml?fileId=5153037&version=3.0&toolType=PREVIEW
##Davis, Nicholas, 2021, "Replication Data for: "The psychometric properties of the Christian nationalism index"", https://doi.org/10.7910/DVN/GUSJEI, Harvard Dataverse, V3; small-relig.tab [fileName], UNF:6:S9zD+VLQ5KTxcmfUA8L/xw== [fileUNF]


x<-read.table("small-relig.tab",sep="\t",header=TRUE)
id<-x[,1]
items<-names(x)[-1]
L<-list()
for (i in 2:ncol(x)) L[[i]]<-data.frame(id=id,item=items[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df$resp<-as.integer(df$resp)
df$id<-as.character(df$id)

write.csv(df,file="christiannatinoalism_davis2021.csv",quote=FALSE,row.names=FALSE)


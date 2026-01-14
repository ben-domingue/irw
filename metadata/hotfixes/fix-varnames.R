df<-read.csv("metadata.csv")
x<-df$variables
L<-strsplit(x,'|',fixed=TRUE)

z<-unlist(L)
z<-gsub(" ","",z)

index<-grepl("^cov_",z)
pc<-z[index]
z<-z[!index]
index<-grepl("^itemcov_",z)
ic<-z[index]
z<-z[!index]

tab<-sort(table(z),decreasing=TRUE)
write.csv(tab,"",row.names=FALSE)
tab<-sort(table(pc),decreasing=TRUE)
write.csv(tab,"",row.names=FALSE)
tab<-sort(table(ic),decreasing=TRUE)
write.csv(tab,"",row.names=FALSE)

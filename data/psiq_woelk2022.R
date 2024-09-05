library(foreign)
data1<-read.spss("Data Study 1.sav",to.data.frame=TRUE)
data2<-read.spss("Data Study 2.sav",to.data.frame=TRUE)

##PsiQ-NL-35
total35 <- data1[7:41]
names(total35)<-gsub("_1","",names(total35))
##PsiQ-NL-35
total35_2 <- data2[6:40]

id<-1:nrow(total35)
L<-list()
for (i in 1:ncol(total35)) L[[i]]<-data.frame(id=id,study='study1',item=names(total35)[i],resp=total35[,i])
L1<-L
id<-paste("s2_",1:nrow(total35_2),sep='')
L<-list()
for (i in 1:ncol(total35_2)) L[[i]]<-data.frame(id=id,study='study2',item=names(total35_2)[i],resp=total35_2[,i])
L2<-L

df<-data.frame(do.call("rbind",c(L1,L2)))
save(df,file="psiq_woelk2022.Rdata")




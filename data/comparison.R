#install.packages("tidyverse")

data1 <- read.csv("Data_Full.csv")
x<-data1[,-(1:2)]
group_info <- data1[,2]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,group=group_info,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

save(df,file="Ecomparison.Rdata")

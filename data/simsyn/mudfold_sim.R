##see https://cran.r-project.org/web/packages/mudfold/refman/mudfold.html#mudfoldsim
library(mudfold)
n.seed <- 10
sim1 <- mudfoldsim(N=10, n=1000, gamma1=5, gamma2=-10, zeros=FALSE,seed=n.seed) ##i increased sample size

x<-sim1$dat
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

write.csv(df,file="mudfoldsim.csv",quote=FALSE,row.names=FALSE)

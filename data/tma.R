##https://openpsychometrics.org/_rawdata/
##https://openpsychometrics.org/tests/TMAS/
#Taylor, J. (1953). "A personality scale of manifest anxiety". The Journal of Abnormal and Social Psychology, 48(2), 285-290.

x<-read.csv("data.csv")
sc<-x$score
x<-x[,paste("Q",1:50,sep='')]
for (i in 1:ncol(x)) x[,i]<-ifelse(x[,i]==0,NA,x[,i])
for (i in 1:ncol(x)) x[,i]<-ifelse(x[,i]==2,0,x[,i])

plot(sc,rowSums(x))
## score. = ( $_POST['Q1'] != 1 )
## 			   + ( $_POST['Q3'] != 1 )
## 			   + ( $_POST['Q4'] != 1 )
## 			   + ( $_POST['Q9'] != 1 )
## 			   + ( $_POST['Q12'] != 1 )
## 			   + ( $_POST['Q15'] != 1 )
## 			   + ( $_POST['Q18'] != 1 )
## 			   + ( $_POST['Q20'] != 1 )
## 			   + ( $_POST['Q29'] != 1 )
## 			   + ( $_POST['Q32'] != 1 )
## 			   + ( $_POST['Q38'] != 1 )
## 			   + ( $_POST['Q50'] != 1 );
for (n in c(1,3,4,9,12,15,18,20,29,32,38,50)) {
    nm<-paste("Q",n,sep='')
    x[,nm]<-abs(1-x[,nm])
}
plot(rowSums(x),sc)

id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

save(df,file="tma.Rdata")

    

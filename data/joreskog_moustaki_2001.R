##table 3, Factor Analysis of Ordinal Variables: A Comparison of Three Approaches, Multivariate Behavior Resarch, 2001

z<-c(2,2,2,2,2,2,97,
3,3,2,3,3,3,70,
3,2,2,2,2,2,49,
3,3,3,3,3,3,45,
3,3,2,2,2,2,45,
3,2,2,3,3,3,40,
3,3,2,3,2,2,32,
3,3,2,3,2,3,31,
2,2,1,2,2,2,25,
1,1,1,1,1,1,23,
3,2,2,3,2,2,20,
2,2,1,1,1,1,18,
3,3,2,2,2,3,18,
2,3,2,2,2,2,17,
3,2,2,3,2,3,16,
3,3,3,3,2,3,16,
3,3,2,3,3,2,15,
3,2,3,3,3,3,15,
2,1,2,2,2,2,14,
2,2,2,3,2,2,13,
3,3,2,2,3,3,12,
3,3,3,2,2,2,12,
3,2,3,3,2,2,11,
2,2,3,2,2,2,11,
3,3,2,2,3,2,10,
3,3,3,3,2,2,10,
3,1,2,3,3,3,10,
3,1,2,2,2,2,10,
3,2,3,3,2,3,10)

mat<-matrix(z,byrow=TRUE,ncol=7)
L<-list()
for (i in 1:nrow(mat)) {
    z<-mat[i,]
    nn<-z[length(z)]
    z<-z[-length(z)]
    tmp<-list()
    for (ii in 1:nn) tmp[[ii]]<-z
    L[[i]]<-do.call("rbind",tmp)
}
x<-do.call("rbind",L)

id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=paste('item',i,sep=''),resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="/home/bd/Dropbox/projects/irw/proc/joreskog_moustaki_2001.Rdata")

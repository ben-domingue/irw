##https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/EL62UQ
##https://www.mdpi.com/2079-3200/11/10/191

load("R2Ddata_07feb2017thru26feb2023.rdata")
x<-R2Ditems_fullSample
id<-1:nrow(x)
L<-list()

for (i in 3:ncol(x)) {
    z<-data.frame(id=id,item=names(x)[i],resp=x[,i],cov_age=x$age,cov_gender=x$sex)
    z<-z[!is.na(z$resp),]
    L[[i]]<-z
}
df<-data.frame(do.call("rbind",L))

write.csv(df,file="twod_rotation_mather2023.csv",quote=FALSE,row.names=FALSE)

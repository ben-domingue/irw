##https://cran.r-project.org/web/packages/hmcdm/hmcdm.pdf

##Design_array.rda  L_real_array.rda  Q_matrix.rda  Test_order.rda  Test_versions.RData  Y_real_array.rda

load("Design_array.rda")
load("L_real_array.rda")
load("Y_real_array.rda")
load("Q_matrix.rda")

for (i in 5) {
    da<-Design_array[,,i]
    rt<-L_real_array[,,i]
    resp<-Y_real_array[,,i]
    id<-1:nrow(resp)
    tmp<-list()
    for (j in 1:ncol(resp)) tmp[[j]]<-data.frame(id=id,item=paste("item",j,sep=''),rt=rt[,j],resp=resp[,j],obs=da[,j])
    df<-data.frame(do.call("rbind",tmp))
    df<-df[!is.na(df$obs),]
    df$obs<-NULL
}

qm<-data.frame(Q_matrix)
names(qm)<-paste("Qmatrix__",1:4,sep='')
qm$item<-paste("item",1:nrow(qm),sep='')
dim(df)
df<-merge(df,qm)
dim(df)

save(df,file="hmcdm_spatialreasoning.Rdata")

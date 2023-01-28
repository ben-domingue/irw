##get data from raw source. https://cran.r-project.org/src/contrib/TestGardener_3.1.1.tar.gz

##quantshort
load("./TestGardener/data/Quantshort_U.rda")
load("./TestGardener/data/Quantshort_key.rda")
L<-list()
for (i in 1:ncol(Quantshort_U)) {
    z<-data.frame(id=1:nrow(Quantshort_U),item=i)
    z$resp<-ifelse(Quantshort_U[,i]==Quantshort_key[i],1,0)
    L[[i]]<-z
}
df<-data.frame(do.call('rbind',L))
save(df,file="quantshort.Rdata")

load("./TestGardener/data/SDS_U.rda")
L<-list()
for (i in 1:ncol(SDS_U)) {
    z<-data.frame(id=1:nrow(SDS_U),item=i)
    z$resp<-SDS_U[,i]
    L[[i]]<-z
}
df<-data.frame(do.call('rbind',L))
save(df,file="sds.Rdata")



Ramsay J (2023). _TestGardener: Optimal Analysis of Test and Rating Scale Data_. R package version 3.1.4, <https://CRAN.R-project.org/package=TestGardener>.

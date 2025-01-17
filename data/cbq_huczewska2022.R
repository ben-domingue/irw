#https://link.springer.com/article/10.1007/s10826-022-02497-6#Sec9
#https://osf.io/f73jq/

x1<-read.csv("dataset.adults.csv")
x2<-read.csv("dataset.teens.csv")
##p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p19,p20,p21,p22,p23,p24,p25,p26,p27,p28,p29,p30,p31,p32,p33,p34,p35,n1,n2,n3,n4,n5,n6,n7,n8,n9,n10,n11,n12,n13,n14,n15,n16,n17,n18,n19,n20,n21,n22,n23,n24,n25,n26,n27,n28,n29

items<-c(paste("p",1:35,sep=''),paste("n",1:29,sep=''))
z1<-x1[,items]
z2<-x2[,items]
z<-list(z1,z2)

id1<-paste("adult",1:nrow(z1))
id2<-paste("adolescent",1:nrow(z2))
id<-list(id1,id2)
sex1<-x1$sex
sex2<-x2$sex
sex<-list(sex1,sex2)
group<-c("adult","adolescent")

LL<-list()
for (i in 1:2) {
    L<-list()
    for (j in 1:length(items)) L[[j]]<-data.frame(id=id[[i]],cov_sex=sex[[i]],item=items[j],resp=z[[i]][,j],cov_group=group[i])
    LL[[i]]<-do.call("rbind",L)
}
df<-data.frame(do.call("rbind",LL))
df$resp<-ifelse(df$resp>4,NA,df$resp)

save(df,file="cbq_huczewska2022.Rdata")

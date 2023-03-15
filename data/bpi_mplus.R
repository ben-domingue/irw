#https://www.tqmp.org/RegularArticles/vol17-2/p141/


## child parent ad1 ad2 hs1 as1
##   	ad3 hs2 hy1 hy2 as2 hs3 as3
##   	pp1 hy3 ad4 pp2 hy4 hy5 hs4
##   	hs5 ad5 pp3 as4 de1 de2 de3
## de4 na1 na2 na3 na4 as5 as6;

#  (F7.0 F5.0 32F2.0)
x<-read.fwf("NLSY79 BPI 2012.dat",c(7,5,rep(2,32)),header=FALSE)
id<-x[,1]
parent<-x[,2]
x<-x[,-c(1,2)]

nms<-c("ad1","ad2","hs1","as1",
  "ad3","hs2","hy1","hy2","as2","hs3","as3",
  "pp1","hy3","ad4","pp2","hy4","hy5","hs4",
  "hs5","ad5","pp3","as4","de1","de2","de3",
  "de4","na1","na2","na3","na4","as5","as6")
names(x)<-nms

L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],parent=parent,resp=x[,i])
df<-data.frame(do.call("rbind",L))

save(df,file="bpi_mplus.Rdata")

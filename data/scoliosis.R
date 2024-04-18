x<-read.csv("SQLI_Example.csv", na = "NA")
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="Bifactor_Approach_Subscore_Assessment.Rdata")
##saved as scoliosis_dueber.Rdata

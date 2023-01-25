#2018 wordsum. https://gss.norc.org/get-the-data/stata
#documentation. https://gss.norc.org/Get-Documentation

library(foreign)
x<-read.dta("GSS2018.dta")
x<-x[,paste("word",letters[1:10],sep='')]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) {
    sc<-as.character(x[,i])
    sc<-ifelse(sc %in% c("correct","incorrect"),sc,NA)
    sc<-ifelse(sc=="correct",1,0)
    L[[i]]<-data.frame(id=id,item=names(x)[i],resp=sc)
}
df<-data.frame(do.call("rbind",L))

save(df,file="wordsum.Rdata")

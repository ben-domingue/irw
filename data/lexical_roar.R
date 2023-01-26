#https://github.com/yeatmanlab/LexicalDecision/blob/master/data_allsubs/LDT_alldata_long.csv
x<-read.csv("LDT_alldata_long.csv")
x$resp<-x$acc
x$item<-x$word
x$id<-x$subj

df<-x[,c("id","item","resp","rt","realpseudo")]

save(df,file='roar_lexical.Rdata')

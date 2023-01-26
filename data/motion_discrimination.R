#see here: https://github.com/yeatmanlab/Parametric_public/blob/master/Analysis/Clean_Motion_Data.csv
#paper: https://www.biorxiv.org/content/10.1101/773853v1

x<-read.csv("Clean_Motion_Data.csv")
x$item<-paste(x$block,x$stim)
x<-x[x$block<=6,]
x<-x[,c("subj_idx","response","rt","item")]
names(x)<-c("id","resp","rt","item")

df<-x

save(df,file="motion.Rdata")

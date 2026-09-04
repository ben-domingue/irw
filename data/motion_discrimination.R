#see here: https://github.com/yeatmanlab/Parametric_public/blob/master/Analysis/Clean_Motion_Data.csv
#paper: https://www.biorxiv.org/content/10.1101/773853v1

x<-read.csv("Clean_Motion_Data.csv")
x$item<-paste(x$block,x$stim)
x<-x[x$block<=6,]
# Each participant sees every (block, stim) ten times -- every id+item pair in
# this table appears exactly 10x, 3,180 of them -- and the source's `trial`
# column says which of the ten a row is. Dropping it left `rt` as the only
# thing separating the trials, which is a measurement, not an identifier
# (irw#1842 block J). Keeping it takes the excess to zero.
x<-x[,c("subj_idx","response","rt","item","trial")]
names(x)<-c("id","resp","rt","item","trialnum")

df<-x

save(df,file="motion.Rdata")

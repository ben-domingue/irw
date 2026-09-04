library(rtdists)
rr98->x
x$resp<-ifelse(x$correct,1,0)
x$item<-paste("i",x$strength)
x$id<-paste(x$id,x$session)
L<-split(x,x$instruction)

x<-L$accuracy
# `block` and `trial` are what say which of a participant's repeated exposures
# to a given stimulus strength a row is; without them `rt` was carrying the
# load, and 11,229 id+item pairs repeated with nothing to tell them apart
# (irw#1842 block J). `trial` alone is not enough -- it restarts each block --
# so both are needed, and together the excess is zero.
x<-x[,c("id","resp","item","rt","block","trial")]
names(x)[names(x)=="trial"]<-"trialnum"

df<-x

save(df,file="rr98_accuracy.Rdata")


Ratcliff, R., & Rouder, J. N. (1998). Modeling Response Times for Two-Choice Decisions. Psychological Science, 9(5), 347-356. http://doi.org/10.1111/1467-9280.00067

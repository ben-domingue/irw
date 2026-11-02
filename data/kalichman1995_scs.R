##The full dataset is available at the following URL: \emph{https://openpsychometrics.org/_rawdata/} }

##obtained via difR
x<-read.table("SCS.txt")
L<-list()
for (i in 1:10) {
    L[[i]]<-data.frame(id=1:nrow(x),item=names(x)[i],resp=x[,i],cov_gender=x$Gender)
}
df<-data.frame(do.call("rbind",L))

## row.names = FALSE: the default wrote R's row index as an unnamed first
## column, which reached the published table as `_unnamed_var` (irw#3229).
## (write.csv ignores `sep`; the old sep="|" did nothing.)
write.csv(df, file = "kalichman1995_scs.csv", row.names = FALSE)

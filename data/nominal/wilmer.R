df<-irw::irw_fetch("wilmer-mrmet-normative-data-set-2022")
tab<-table(df$raw_resp)
dim(df)
df<-df[df$raw_resp %in% names(tab)[tab>2],]
dim(df)
df$text<-df$raw_resp
df$raw_resp<-NULL
write.table(df,"wilmer-mrmet-normative-data-set-2022",quote=FALSE,row.names=FALSE,sep="|")


df<-irw::irw_fetch("wilmer-rmet-normative-data-set-2022")
df$text<-df$raw_resp
df$raw_resp<-NULL
write.table(df,"wilmer-rmet-normative-data-set-2022",quote=FALSE,row.names=FALSE,sep="|")

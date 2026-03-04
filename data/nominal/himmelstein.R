irw::irw_fetch("himmelstein-berlin_numeracy-2025")->df
df$text<-df$resp_raw
df$resp_raw<-NULL
write.table(df,"himmelstein-berlin_numeracy-2025",quote=FALSE,row.names=FALSE,sep="|")

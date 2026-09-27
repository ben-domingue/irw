df<-irw::irw_fetch("borges_brazil_residency_2024_cbt")
df$text<-df$resp_raw
df$resp_raw<-NULL
write.table(df,"borges_brazil_residency_2024_cbt_nom",quote=FALSE,row.names=FALSE,sep="|")


df<-irw::irw_fetch("borges_brazil_residency_2024_pbt")
df$text<-df$resp_raw
df$resp_raw<-NULL
write.table(df,"borges_brazil_residency_2024_pbt_nom",quote=FALSE,row.names=FALSE,sep="|")

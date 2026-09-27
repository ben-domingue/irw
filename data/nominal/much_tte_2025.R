df<-irw::irw_fetch("much_tte_2025_concentrationtask")
tab<-table(df$raw_resp)
dim(df)
df<-df[df$raw_resp %in% names(tab)[tab>2],]
dim(df)
df$text<-df$raw_resp
df$raw_resp<-NULL
write.table(df,"much_tte_2025_concentrationtask_nom.csv",quote=FALSE,row.names=FALSE,sep="|")

df<-irw::irw_fetch("much_tte_2025_matrixreasoning")
tab<-table(df$raw_resp)
dim(df)
df<-df[df$raw_resp %in% names(tab)[tab>2],]
dim(df)
df$text<-df$raw_resp
df$raw_resp<-NULL
write.table(df,"much_tte_2025_matrixreasoning_nom.csv",quote=FALSE,row.names=FALSE,sep="|")

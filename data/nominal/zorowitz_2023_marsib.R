##Nominal companion of zorowitz_2023_marsib (#1591). resp_raw there is the option
##picked relative to the key: 0 = the correct option, 1-3 = the three distractors.
##The source does not say which distractor is which beyond that, so text keeps
##the code as deposited.
df<-irw::irw_fetch("zorowitz_2023_marsib")
df$text<-df$resp_raw
df$resp_raw<-NULL
write.csv(df,"zorowitz_2023_marsib_nom.csv",quote=TRUE,row.names=FALSE,na="")

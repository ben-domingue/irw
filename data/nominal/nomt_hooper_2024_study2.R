##Nominal companion of nomt_hooper_2024_study2 (#2664). That table's resp_raw is
##the source's "Selection" column: which of the three options the participant
##picked on each Novel Object Memory Test trial (3-alternative forced choice).
##The correct option varies across items, and each option is chosen on roughly a
##third of trials, so the code is a choice, not a constant. text keeps the option
##number as deposited.
df<-irw::irw_fetch("nomt_hooper_2024_study2")
df$text<-df$resp_raw
df$resp_raw<-NULL
write.csv(df,"nomt_hooper_2024_study2_nom.csv",quote=TRUE,row.names=FALSE,na="")

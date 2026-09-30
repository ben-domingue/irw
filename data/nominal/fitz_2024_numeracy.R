##Nominal companion of fitz_2024_numeracy. resp_raw there is the respondent's
##free-text answer (e.g. "1 in 200", "2%"), or the option number for the two
##multiple-choice items numeracy4/numeracy5. Blanks were already dropped upstream.
df<-irw::irw_fetch("fitz_2024_numeracy")
df$text<-df$resp_raw
df$resp_raw<-NULL
write.csv(df,"fitz_2024_numeracy_nom.csv",quote=TRUE,row.names=FALSE,na="")

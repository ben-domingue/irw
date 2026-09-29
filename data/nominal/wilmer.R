## `text` is the per-item option code from the core table's resp_raw ("1" = keyed
## answer, "2"-"4" = distractors in alphabetical order of their word), not the chosen
## word: ARC's terms cover the RMET/MRMET option words (irw#2513, D13, 2026-09-28).
## The core tables name the column resp_raw; `raw_resp` here was a stale name that no
## longer matches what irw_fetch returns.
df<-irw::irw_fetch("wilmer-mrmet-normative-data-set-2022")
tab<-table(df$resp_raw)
dim(df)
df<-df[df$resp_raw %in% names(tab)[tab>2],]
dim(df)
df$text<-df$resp_raw
df$resp_raw<-NULL
write.table(df,"wilmer-mrmet-normative-data-set-2022_nom",quote=FALSE,row.names=FALSE,sep="|")


df<-irw::irw_fetch("wilmer-rmet-normative-data-set-2022")
df$text<-df$resp_raw
df$resp_raw<-NULL
write.table(df,"wilmer-rmet-normative-data-set-2022_nom",quote=FALSE,row.names=FALSE,sep="|")

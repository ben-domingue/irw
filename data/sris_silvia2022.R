##https://osf.io/qsa5w/
##https://link.springer.com/article/10.1007/s12144-020-01299-7

x<-read.csv("SRIS 1200 Cases.csv")
study<-x$study
# The source's `id` restarts within each of the 15 studies, so participant 1 of
# AreaS1 and participant 1 of MDD arrived as one person: 221 ids where 1,192
# people were measured, and 19,420 of the table's 23,840 rows excess
# (irw#1842 block E). The study is what separates them.
id<-paste0(study, "_", x$id)

nms<-c("sr01", "sr02", "sr03", "sr04", "sr05", "sr06", "sr07", "sr08", 
"sr09", "sr10", "sr11", "sr12", "ins01", "ins02", "ins03", "ins04", 
"ins05", "ins06", "ins07", "ins08")
L<-list()
for (nm in nms) L[[nm]]<-data.frame(id=id,study=study,item=nm,resp=x[[nm]])

df<-data.frame(do.call("rbind",L))

save(df,file="sris_silvia2022.Rdata")

                                    

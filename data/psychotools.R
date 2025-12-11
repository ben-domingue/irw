## ConspiracistBeliefs2016, 14
load("ConspiracistBeliefs2016.rda")
x<-ConspiracistBeliefs2016
x<-x$resp
#x$area<-NULL
#x$gender<-NULL
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file='psychotools_conspiracist.Rdata')

## MathExam14W, 38
load("MathExam14W.rda")
x<-MathExam14W
x<-x$credit
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file='psychotools_mathexam.Rdata')

## YouthGratitude, 100
load("YouthGratitude.rda")
x<-YouthGratitude
x<-x[,-(1:3)]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=colnames(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
z<-round(df$resp)
df$resp<-ifelse(z==df$resp,df$resp,NA)
df$resp<-ifelse(df$resp>9,NA,df$resp)
save(df,file='psychotools_gratitude.Rdata')
##note, split to 3 tables on 12-11-2025 using something like below
"table_gart <- df[ grepl("^ao_|^sa_|^losd_", df[["item"]]), ]
table_gac <- df[ grepl("^gac_", df[["item"]]), ]
table_gq6 <- df[ grepl("^gq6_", df[["item"]]), ]

write.csv(table_gart,  "psychotools_gratitude_gart.csv",  row.names = FALSE)
write.csv(table_gac, "psychotools_gratitude_gac.csv", row.names = FALSE)
write.csv(table_gq6, "psychotools_gratitude_gq6.csv", row.names = FALSE)"


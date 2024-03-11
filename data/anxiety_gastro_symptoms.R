x<-read.spss("EHAS_CFA.sav",to.data.frame=T)
x$ARFID<-NULL
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
z<-c("Strongly Disagree", "Somewhat Disagree", "Neither Agree nor Disagree", 
"Somewhat Agree", "Strongly Agree")
df$resp<-match(df$resp,z)
save(df,file="anxiety_gastro_symptoms.Rdata")

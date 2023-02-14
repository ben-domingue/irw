#https://ggum.gatech.edu/capsdesc.html
x<-read.table("cpdat.txt",colClasses="character")
#In addition to scaling statements, Roberts (1995) had 245 subjects indicate the extent to which they agreed with each of the 24 statements. Responses were on a 6-point rating scale where 1=Strongly Disagree, 2=Disagree, 3=Slightly Disagree, 4=Slightly Agree, 5=Agree and 6=Strongly Agree. The data are formatted as follows:
L<-strsplit(x[,2],'')
x<-do.call("rbind",L)
L<-list()
id<-1:nrow(x)
for (j in 1:ncol(x)) {
    L[[paste(j)]]<-data.frame(id=id,item=paste("item",j),resp=x[,j])
}
df<-data.frame(do.call("rbind",L))
df$resp<-as.numeric(df$resp)
save(df,file="gatech_cappunish.Rdata")

#https://ggum.gatech.edu/censdesc.html
x<-read.table("cendat.txt",colClasses="character")
#In addition to scaling statements, Roberts (1995) had 223 subjects indicate the extent to which they agreed with each of the 20 statements. Responses were on a 6-point rating scale where 1=Strongly Disagree, 2=Disagree, 3=Slightly Disagree, 4=Slightly Agree, 5=Agree and 6=Strongly Agree. The data are formatted as follows:
L<-strsplit(x[,2],'')
x<-do.call("rbind",L)
L<-list()
id<-1:nrow(x)
for (j in 1:ncol(x)) {
    L[[paste(j)]]<-data.frame(id=id,item=paste("item",j),resp=x[,j])
}
df<-data.frame(do.call("rbind",L))
df$resp<-as.numeric(df$resp)
save(df,file="gatech_censor.Rdata")


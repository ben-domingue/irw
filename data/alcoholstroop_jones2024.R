##https://osf.io/25m8a
##https://link.springer.com/article/10.3758/s13428-024-02377-5#data-availability

x<-read.csv("STROOP_ONLINE.csv",sep="|")
x<-x[x$TRIALCODE!="practiceword",]
id<-x$Subject
num<-x$TRIALNUM
stimulus<-x$stimulus
item<-x$WORD
resp<-x$correct_response_stroop
rt<-x$response_time/60
df<-data.frame(id=id,trialnum=num,stimulus=stimulus,item=item,resp=resp,rt=rt)

save(df,file="alcoholstroop_jones2024.Rdata")

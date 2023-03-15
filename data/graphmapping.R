x<-read.csv("Study1_dataset.csv",header=TRUE,sep=";")
df<-data.frame(id=x$Participan,order=paste(x$SESSION,x$TRIAL_ORDER,sep="-"))
rt<-x$Response.time
rt<-gsub(',','.',rt)
df$rt<-as.numeric(rt)
df$resp<-x$Correct_ans

df$item<-paste(x$No..of.edges,x$Targets,x$Crossed,sep="--")
save(df,file="graphmapping_study1.Rdata")


#x<-read.csv("Study2_dataset.csv",header=TRUE,sep=";")

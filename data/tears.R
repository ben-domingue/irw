#https://osf.io/uyjeg/

x<-read.csv("Observer ratings.csv",header=TRUE,sep=';')
rater<-x$ID
id<-x$Video_ID
stimulus<-x$Stimulus
phase<-x$Phase

z<-x[,c("Valence_pos","Valence_neg","Arousal","Genuine","Happiness","Sadness","Anger","Fear","Disgust","Surprise","Neutral")]
L<-list()
for (i in 1:ncol(z)) L[[i]]<-data.frame(id=id,rater=rater,stimulus=stimulus,phase=phase,item=names(z)[i],resp=z[,i])
df<-data.frame(do.call("rbind",L))
df<-df[!is.na(df$resp),]

save(df,file="tears.Rdata")

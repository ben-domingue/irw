library(footBayes)
L<-list()
load("england.rda") ##from package source
L$england<-england
load("italy.rda") ##from package source
L$italy<-italy

for (ii in 1:length(L)) {
    x<-L[[ii]]
    df<-data.frame(agent_a=x$home,agent_b=x$visitor)
    df$date<-as.numeric(strptime(x$Date,format='%Y-%m-%d'))
    df$score_a<-x$hgoal
    df$score_b<-x$vgoal
    df$homefield<-'agent_a'
    df$winner<-ifelse(df$score_a>df$score_b,'agent_a','agent_b')
    df$winner<-ifelse(df$score_a==df$score_b,'draw',df$winner)
    df$season<-x$Season
    write.csv(df,file=paste("footbayes_",names(L)[ii],".csv",sep=''),quote=FALSE,row.names=FALSE)
}

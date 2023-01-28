library(lme4)
df<-data.frame(id=VerbAgg$id, item=VerbAgg$item, resp=VerbAgg$r2)
df$resp<-ifelse(df$resp=="Y",1,0)
save(df,file="verbagg.Rdata")


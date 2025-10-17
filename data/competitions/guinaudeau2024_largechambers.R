##https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/0ULECU

x<-readRDS("0_respondents_rating.rds")
x<-x[x$mp_1<x$mp_2,]
df<-data.frame(agent_a=x$mp_1,agent_b=x$mp_2,rater=x$respondent,rater_cov_party=x$respondent_party,agent_a_cov_party=x$mp_party_1,agent_b_cov_party=x$mp_party_2)

df$winner<-ifelse(x$outcome==2,'draw','agent_a')
df$winner<-ifelse(x$outcome==1,'agent_b',df$winner)

write.csv(df,file="guinaudeau2024_largechambers.csv",quote=FALSE,row.names=FALSE)


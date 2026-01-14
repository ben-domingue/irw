##https://cran.r-project.org/web/packages/hyper2/refman/hyper2.html#T20

                                        #t20
x<-T20_table
df<-data.frame(agent_a=x$team1,agent_b=x$team2,homefield=x$toss_winner,winner=x$match_winner)
write.csv(df,file="t20_hyper.csv",quote=FALSE,row.names=FALSE)

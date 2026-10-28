##https://cran.r-project.org/web/packages/hyper2/refman/hyper2.html#T20

                                        #t20
x<-T20_table
df<-data.frame(agent_a=x$team1,agent_b=x$team2)
##match_winner and toss_winner name a team. The competition standard wants the
##agent slot, not the name -- a raw name in `winner` reads as an unknown level
##to anything keyed on it, including the Bradley-Terry recipe on the standard
##page, which scores every row as a loss for agent_a (#3279). Verified on the
##published table: every match_winner and every toss_winner is one of the two
##teams in its own row, so neither map can fall through.
as_agent<-function(nm) ifelse(nm==x$team1,'agent_a',ifelse(nm==x$team2,'agent_b',NA))
df$homefield<-as_agent(x$toss_winner)
df$winner<-as_agent(x$match_winner)
stopifnot(!any(is.na(df$winner)), !any(is.na(df$homefield)))
write.csv(df,file="t20_hyper.csv",quote=FALSE,row.names=FALSE)

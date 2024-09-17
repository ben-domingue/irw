##https://github.com/DomSamangy/NBA_Shots_04_23

years<-2004:2024
L<-list()
for (y in years) {
    print(y)
    x<-read.csv(paste0("NBA_",y,"_Shots.csv"))
    id<-x$PLAYER_ID
    item<-'trial'
    resp<-ifelse(x$EVENT_TYPE=="Made Shot",1,0)
    lx<-x$LOC_X
    ly<-x$LOC_Y
    dist<-sqrt(lx^2+ly^2)
    by(dist,x$SHOT_TYPE,summary)
    threept<-ifelse(x$SHOT_TYPE=="3PT Field Goal",1,0)
    ##game date
    year<-x$SEASON_1
    date<-as.numeric(as.POSIXct(x$GAME_DATE, format="%m-%d-%Y"))
    ##
    quarter<-x$QUARTER
    mins<-as.numeric(x$MINS_LEFT+x$SECS_LEFT/60)
    gameclock<-12*(quarter-1)+12-mins
    ##
    L[[as.character(y)]]<-data.frame(id=id,resp=resp,trial_locx=lx,trial_locy=ly,trial_three=threept,
                   date=date,year=year,
                   gameclock=gameclock
                   )
}
df<-data.frame(do.call("rbind",L))
df<-df[df$gameclock<=48,]
save(df,file="nbashots_samangy.Rdata")

library(lme4)
m<-lmer(resp~abs(trial_locx)+trial_locy+trial_three+(1|id),df)
m<-lmer(resp~abs(trial_locx)+trial_locy+trial_three+gameclock+(1|id),df[df$gameclock>45,])

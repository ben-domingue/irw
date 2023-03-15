#https://github.com/grecabral/Supplemental-files/blob/432faf450506aff8f94ef050b0cb8aa2e9bee661/data.csv
#https://link.springer.com/article/10.3758/s13428-021-01661-y#data-availability

x<-read.csv("data.csv")
x$id<-paste(x$Player.Id,x$Experiment)
L<-split(x,x$Game)

f<-function(z) {
    id<-z$id
    order<-z$Game.Order
    npc.strategy<-z$NPC.Strategy
    ll<-list()
    for (i in 1:10) {
        ll[[i]]<-data.frame(id=id,game.order=order,npc.strategy=npc.strategy,item=paste(unique(z$Game),i,sep='.'),round=i,resp=z[[paste("Round.",i,sep='')]])
    }
    df<-data.frame(do.call("rbind",ll))
    #df$order<-10*(df$order.game-1)+df$round
    df
}

L<-lapply(L,f)
df<-data.frame(do.call("rbind",L))
save(df,file="slingshot.Rdata")

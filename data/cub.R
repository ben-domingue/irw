load("relgoods.rda")
x<-relgoods
id<-x$ID
nms<-c("Videogames","Reading","Cinema","Drawing","Shopping","Writing","Bicycle","Tv","StayWFriend","Groups","Walking","HandWork","Internet","Sport","SocialNetwork","Gym","Quiz","MusicInstr","GoAroundCar","Dog","GoOutEat")
x<-x[,nms]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file='cub_relgoods.Rdata')

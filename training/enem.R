## see notes about installation of `irw` and associated authentication issues here: https://github.com/itemresponsewarehouse/Rpkg
df<-irw::irw_fetch("enem_2022_1mil_mt")
ids<-sample(unique(df$id),5000)
df<-df[df$id %in% ids,]
resp<-irw::irw_long2resp(df)
nc<-apply(resp,2,function(x) length(unique(x[!is.na(x)])))
resp<-resp[,nc==2]
mirt::mirt(resp,1,'Rasch')

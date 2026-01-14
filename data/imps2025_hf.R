k<-readRDS("kimochis_hf.rds")
p<-readRDS("plus_hf_merged.rds")
p$cohort<-'plus'
k$cohort<-'k'
k$rt<-k$rt_all*1000
k$time_limit<-3000
test<-grepl("Spring",p$time)
p$time_limit<-ifelse(test,1250,750)

## > names(p)
##  [1] "stud_id"    "sch_id"     "teach_id"   "pl_grade"   "pl_fem"     "pl_age"    
##  [7] "trial_num"  "resp_side"  "rt"         "block"      "time_limit" "stim_shape"
## [13] "stim_side"  "time"      
## > names(k)
##  [1] "id"         "time"       "ht_stim"    "ft_stim"    "block"      "trial_num" 
##  [7] "stim_time"  "stim_shape" "stim_side"  "resp_time"  "resp_side"  "acc"       
## [13] "acc_to"     "rt_all"     "to"         "ar"         "switch"     "grade"     
## [19] "female"     "age"       

p<-p[,c("stud_id","pl_grade","pl_fem","pl_age","trial_num","resp_side","rt","block","time_limit","stim_side","time","stim_shape","cohort")]
k<-k[,c("id","grade","female","age","trial_num","resp_side","rt","block","time_limit","stim_side","time","stim_shape","cohort")]
names(p)<-names(k)
k$id<-paste("k",k$id)
df<-data.frame(rbind(p,k))
df$resp_side<-tolower(df$resp_side)
df$stim_side<-tolower(df$stim_side)
df$stim_shape<-tolower(df$stim_shape)
h<-df[df$stim_shape=='heart',]
f<-df[df$stim_shape=='flower',]
h$resp<-ifelse(h$stim_side==h$resp_side,1,0)
f$resp<-ifelse(f$stim_side!=f$resp_side,1,0)
df<-data.frame(rbind(h,f))
df$time_limit<-df$time_limit/1000
test<-grepl("practice",df$block)
df<-df[!test,]
df$rt<-df$rt/1000
names(df)[2:4]<-paste("cov_",names(df)[2:4],sep='')

df<-df[df$rt<df$time_limit,]
f<-function(df) {
    qu<-quantile(df$rt,1:9/10,na.rm=TRUE)
    gr<-cut(df$rt,c(-Inf,qu,Inf))
    table(gr,df$resp,useNA='always')
}
lapply(split(df,df$cohort),f)
df<-df[!is.na(df$resp),]
df<-df[!is.na(df$rt),]

z<-c(rep(1,75),rep(2,15),rep(3,15))
gr<-sample(z,nrow(df),replace=TRUE)
train<-df[gr==1,]
test<-df[gr==2,]
hold<-df[gr==3,]
write.csv(train,file="imps2025_train.csv",quote=FALSE,row.names=FALSE)
write.csv(test,file="imps2025_test.csv",quote=FALSE,row.names=FALSE)
write.csv(hold,file="imps2025_hold.csv",quote=FALSE,row.names=FALSE) ##not to be shared


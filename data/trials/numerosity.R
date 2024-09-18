##https://osf.io/za9y8/
##https://github.com/ben-domingue/irw/issues/60
## 6.  task_number
##     Task number = 1 for dot difference
## Task number = 2 for dot numerosity

##task 1
x<-read.csv("Experiment2.data",sep=",") #see coding in https://osf.io/xcyrp
x<-x[x$response_key_ID>0,]
x<-x[x$task_number==1,]
id<-x$subject_number
rt<-x$reaction_time/60
more.blue<-x$column_7_value<x$column_8_value
resp<-x$response_key_ID
resp<-ifelse((resp==1 & !more.blue) | (resp==2 & more.blue),1,0)
trial_total.dot.area<-x$column_9_value
trial_area.yellow.dots<-x$column_10_value
trial_area.blue.dots<-x$column_11_value
df<-data.frame(id=id,rt=rt,resp=resp,
               trial_total.dot.area=trial_total.dot.area,
               trial_area.yellow.dots=trial_area.yellow.dots,
               trial_area.blue.dots=trial_area.blue.dots
               )

save(df,file="differences_ratcliff2021.Rdata")

##task 2
x<-read.csv("Experiment2.data",sep=",") #see coding in https://osf.io/xcyrp
x<-x[x$response_key_ID>0,]
x<-x[x$task_number==2,]
id<-x$subject_number
rt<-x$reaction_time/60
dots<-x$column_7_value
resp<-x$response_key_ID
resp<-ifelse((dots<25 & resp==2) | (dots>25 & resp==1),1,0)

trial_area.flag<-x$column_8_value
trial_total.area<-x$column_9_value
trial_mean.area<-x$column_10_value
df<-data.frame(id=id,rt=rt,resp=resp,
               trial_area.flag=trial_area.flag,
               trial_total.area=trial_total.area,
               trial_mean.area=trial_mean.area
               )

save(df,file="numerosity_ratcliff2021.Rdata")

x<-read.csv("OFAQData.csv",sep="|",header=TRUE)
x<-x[!duplicated(x$Participant),]


ofaq<-c("T1_OFAQ_1", "T1_OFAQ_2", "T1_OFAQ_3", 
"T1_OFAQ_4", "T1_OFAQ_5", "T1_OFAQ_6", "T1_OFAQ_7", "T1_OFAQ_8", 
"T1_OFAQ_9", "T1_OFAQ_10", "T1_OFAQ_11", "T1_OFAQ_12", "T1_OFAQ_13", 
"T1_OFAQ_14", "T1_OFAQ_15", "T1_OFAQ_16", "T1_OFAQ_17", "T1_OFAQ_18", 
"T1_OFAQ_19", "T1_OFAQ_20", "T1_OFAQ_21", "T1_OFAQ_22", "T1_OFAQ_23", 
"T1_OFAQ_24", "T1_OFAQ_25", "T1_OFAQ_26", "T1_OFAQ_27", "T1_OFAQ_28", 
"T1_OFAQ_29", "T1_OFAQ_30", "T1_OFAQ_31", "T1_OFAQ_32", "T1_OFAQ_33", 
"T1_OFAQ_34", "T1_OFAQ_35", "T1_OFAQ_36", "T1_OFAQ_37")


bigfive<-c("T1_BigFive_1", 
"T1_BigFive_2", "T1_BigFive_3", "T1_BigFive_4", "T1_BigFive_5", 
"T1_BigFive_6", "T1_BigFive_7", "T1_BigFive_8", "T1_BigFive_9", 
"T1_BigFive_10", "T1_BigFive_11", "T1_BigFive_12", "T1_BigFive_13", 
"T1_BigFive_14", "T1_BigFive_15", "T1_BigFive_16", "T1_BigFive_17", 
"T1_BigFive_18", "T1_BigFive_19", "T1_BigFive_20", "T1_BigFive_21", 
"T1_BigFive_22", "T1_BigFive_23", "T1_BigFive_24", "T1_BigFive_25", 
"T1_BigFive_26", "T1_BigFive_27", "T1_BigFive_28", "T1_BigFive_29", 
"T1_BigFive_30", "T1_BigFive_31", "T1_BigFive_32", "T1_BigFive_33", 
"T1_BigFive_34", "T1_BigFive_35", "T1_BigFive_36", "T1_BigFive_37", 
"T1_BigFive_38", "T1_BigFive_39", "T1_BigFive_40", "T1_BigFive_41", 
"T1_BigFive_42", "T1_BigFive_43", "T1_BigFive_44")

dospert<-c("T1_DOSPERT_1", 
"T1_DOSPERT_2", "T1_DOSPERT_3", "T1_DOSPERT_4", "T1_DOSPERT_5", 
"T1_DOSPERT_6", "T1_DOSPERT_7", "T1_DOSPERT_8", "T1_DOSPERT_9", 
"T1_DOSPERT_10", "T1_DOSPERT_11", "T1_DOSPERT_12", "T1_DOSPERT_13", 
"T1_DOSPERT_14", "T1_DOSPERT_15", "T1_DOSPERT_16", "T1_DOSPERT_17", 
"T1_DOSPERT_18", "T1_DOSPERT_19", "T1_DOSPERT_20", "T1_DOSPERT_21", 
"T1_DOSPERT_22", "T1_DOSPERT_23", "T1_DOSPERT_24", "T1_DOSPERT_25", 
"T1_DOSPERT_26", "T1_DOSPERT_27", "T1_DOSPERT_28", "T1_DOSPERT_29", 
"T1_DOSPERT_30")

f<-function(nms,x) {
    id<-x$Participant
    x<-x[,nms]
    L<-list()
    for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
    df<-data.frame(do.call("rbind",L))
    df
}


df<-f(x=x,nms=ofaq)
table(df$resp)
z<-c("Strongly Disagree","Disagree","Neither Agree nor Disagree","Agree","Strongly Agree")
z<-match(df$resp,z)
df$resp<-z
save(df,file="offlinefriend_ofaq.Rdata")

df<-f(x=x,nms=bigfive)
table(df$resp)
z<-c("Disagree Strongly","Disagree a little", "Neither agree nor disagree","Agree a little", "Agree Strongly")
z<-match(df$resp,z)
df$resp<-z
save(df,file="offlinefriend_bigfive.Rdata")

df<-f(x=x,nms=dospert)
table(df$resp)
df<-df[df$resp!="Not sure",]
z <-c("Extremely unlikely","Moderately unlikely","Somewhat unlikely",
      "Somewhat likely", "Moderately likely" ,  "Extremely likely")
z<-match(df$resp,z)
df$resp<-z
save(df,file="offlinefriend_dospert.Rdata")



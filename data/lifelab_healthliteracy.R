##https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0250545
library(readstata13)
x<-read.dta13("lifelabtrial.dta")

id<-x$serial
intervention<-x$intervention

##These were a series of five questions, four of which used a Likert scale, with five responses ranging from ‘strongly disagree’, (scored 1), to ‘strongly agree’ (scored 5), the fifth question “At what age do you think our nutrition starts to affect our future health?” has responses from before birth then in decades up to > 60 years.
x<-x[,c("agenutaf12","fdnow12","fdpregh12","fdnowc12","fdadch12")]

##these were coded as >30 years = 1, 20–30 = 2, 10–20 = 3, 0–10 = 4, Before birth = 5.
levs<-c("Before we are born",
  "11-20 years old",
  "0-10 years old",
  "21-30 years old",
  "31-40 years old",
  "41-50 years old",
  "61+ years old",
  "51-60 years old")
ii<-match(x[,1],levs)
vals<-c(5,3,4,2,1,1,1,1)
z<-vals[ii]
table(x[,1],z)
items<-list()
items$agenutaf12<-z

##These were a series of five questions, four of which used a Likert scale, with five responses ranging from ‘strongly disagree’, (scored 1), to ‘strongly agree’ (scored 5),
for (i in 2:ncol(x)) {
    levs<-c("Strongly disagree","Disagree","I do not know","Agree","Strongly agree")
    ii<-match(x[,i],levs)
    vals<-1:5
    z<-vals[ii]
    print(table(x[,i],z))
    items[[names(x)[i]]]<-z
}

df<-list()
for (i in 1:length(items)) df[[i]]<-data.frame(id=id,intervention=intervention,item=names(items)[i],resp=items[[i]])
df<-data.frame(do.call("rbind",df))

save(df,file="lifelab_healthliteracy.Rdata")

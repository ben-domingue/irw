##tam r package

#tam. data.fims.Aus.Jpn.scored; data.geiser; data.janssen; timss

load("data.fims.Aus.Jpn.scored.rda")
x<-data.fims.Aus.Jpn.scored
#
ii<-grep("^M1",names(x))
id<-1:nrow(x)
L<-list()
for (i in ii) L[[i]]<-data.frame(id=id,item=names(x)[i],country=x$country,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="fims_tam.Rdata")

load("data.geiser.rda")
x<-data.geiser
#
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="geiser_tam.Rdata")

load("data.janssen2.rda")
x<-data.janssen2
#
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="janssen2_tam.Rdata")

load("data.timssAusTwn.rda")
x<-data.timssAusTwn
#
ii<-grep("^M0",names(x))
id<-1:nrow(x)
L<-list()
for (i in ii) L[[i]]<-data.frame(id=id,item=names(x)[i],country=x$IDCNTRY,booklet=x$IDBOOK,resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="timss_tam.Rdata")
##
# Data fix
setwd(dirname(rstudioapi::getActiveDocumentContext()$path)) 
library(readr)
library(dplyr)

timss_tam <- read_csv("timss_tam.csv")

# Set missing values
timss_tam$resp[timss_tam$resp %in% c(6, 9, 96, 99)] <- NA

# Recode CR items
timss_tam$resp[timss_tam$resp %in% c(20, 21)] <- 2    # fully correct
timss_tam$resp[timss_tam$resp %in% c(10, 11)] <- 1    # partially correct
timss_tam$resp[timss_tam$resp %in% c(70, 79)] <- 0    # incorrect

# Recode MC items
correct_keys <- c(
  "M032166" = 2,
  "M032721" = 2,
  "M032626" = 4,
  "M032595" = 3,
  "M032673" = 3
)

timss_tam <- timss_tam %>%
  mutate(resp = if_else(
    item %in% names(correct_keys) & !is.na(resp),
    as.numeric(resp == correct_keys[item]),
    resp
  ))

write_csv(timss_tam, "timss_tam.csv")

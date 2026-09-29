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

# Omitted vs not reached (irw#2513, 2026-09-28; datastandard "omitted vs not
# reached"). TIMSS codes omitted as 9 (MC) / 99 (CR) and not reached as 6 (MC) /
# 96 (CR); the TAM data keeps them apart (1,768 omitted and 84 not-reached cells
# in these 11 items, plus 44 NA). Following IEA calibration scoring, an omitted
# item is scored 0 with its source code kept in resp_raw, and a not-reached item
# was never administered, so its row is dropped. This replaces #1046's rule
# (both set to NA). resp_raw carries the source code for every row.
timss_tam$resp_raw <- as.character(timss_tam$resp)
timss_tam <- timss_tam[!(timss_tam$resp %in% c(6, 96)), ]
timss_tam$resp[timss_tam$resp %in% c(9, 99)] <- 0

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

timss_tam <- timss_tam %>% select(id, item, resp, resp_raw, everything())
write_csv(timss_tam, "timss_tam.csv", na = "")  # not the string "NA" (#2029)

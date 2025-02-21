######################## en_es ######################## 

con<-file("en_es.slam.20190204.train")
x<-readLines(con)
close(con)

print(x)


index<-grep("# prompt",x)
index<-c(index,length(x))
L<-list()
for (i in 1:(length(index)-1)) L[[i]]<-x[index[i]:(index[i+1]-1)]

print(L)

f<-function(x) {
  item<-gsub("# prompt:","",x[1])
  users<-grep("user:",x)
  ##
  out<-list()
  for (j in 1:length(users)) {
    z<-strsplit(x[users[j]]," ")[[1]][-1]
    z<-z[z!=""]
    z<-strsplit(z,":")
    nms<-sapply(z,"[",1,drop=FALSE)
    dat<-sapply(z,"[",2,drop=FALSE)
    ##response
    mm<-ifelse(j==length(users),length(x),users[j+1]-1)
    z<-strsplit(x[(users[j]+1):mm]," ")
    z<-lapply(z,function(z) z[z!=""])
    z<-data.frame(do.call("rbind",z))
    ## A Unique 12-digit ID for each token instance: the first 8 digits are a B64-encoded ID representing the session, the next 2 digits denote the index of this exercise within the session, and the last 2 digits denote the index of the token (word) in this exercise
    ## The token (word)
    ## Part of speech in Universal Dependencies (UD) format
    ## Morphological features in UD format
    ## Dependency edge label in UD format
    ## Dependency edge head in UD format (this corresponds to the last 1-2 digits of the ID in the first column)
    ##     The label to be predicted (0 or 1)
    names(z)<-c("resp.id","token","part.speech","morphology","dependency.label","dependency.head","resp")
    ##
    z$item<-item
    for (i in 1:length(nms)) z[nms[i]]<-dat[i]
    z$resp<-as.numeric(z$resp)
    out[[as.character(j)]]<-z
  }
  data.frame(do.call("rbind",out))
}
#options(warn=2)
#for (i in 1:length(L)) L[[i]]<-f(L[[i]])
library(parallel)
L<-mclapply(L,f,mc.cores=3)

print(L)

library(dplyr)
df <- purrr::map_dfr(L, as_tibble)

df_ <- df %>%
  select(user, item, resp, session, format, time, part.speech, morphology, dependency.label, dependency.head, token)

df_$stem<-df_$item

df_$item <- paste(df_$item, df_$token, sep = "__")
  
df_$rt<-as.numeric(df_$time)

df_$id<-df_$user


df_ <- df_ %>%
  select(id, item, resp, session, format, rt, part.speech, morphology, dependency.label, dependency.head, stem)

df_reverse_translate <- df_ %>% filter(format == "reverse_translate")

df_reverse_tap <- df_ %>% filter(format == "reverse_tap")

df_listen <- df_ %>% filter(format == "listen")


table(df_listen$resp)


write.csv(df_reverse_translate, "duolingo_en_es__reverse_translate.csv", row.names = FALSE)
write.csv(df_reverse_tap, "duolingo_en_es__reverse_tap.csv", row.names = FALSE)
write.csv(df_listen, "duolingo_en_es__listen.csv", row.names = FALSE)


######################## es_en ######################## 

con<-file("es_en.slam.20190204.train")
x<-readLines(con)
close(con)

print(x)


index<-grep("# prompt",x)
index<-c(index,length(x))
L<-list()
for (i in 1:(length(index)-1)) L[[i]]<-x[index[i]:(index[i+1]-1)]

print(L)

f<-function(x) {
  item<-gsub("# prompt:","",x[1])
  users<-grep("user:",x)
  ##
  out<-list()
  for (j in 1:length(users)) {
    z<-strsplit(x[users[j]]," ")[[1]][-1]
    z<-z[z!=""]
    z<-strsplit(z,":")
    nms<-sapply(z,"[",1,drop=FALSE)
    dat<-sapply(z,"[",2,drop=FALSE)
    ##response
    mm<-ifelse(j==length(users),length(x),users[j+1]-1)
    z<-strsplit(x[(users[j]+1):mm]," ")
    z<-lapply(z,function(z) z[z!=""])
    z<-data.frame(do.call("rbind",z))
    ## A Unique 12-digit ID for each token instance: the first 8 digits are a B64-encoded ID representing the session, the next 2 digits denote the index of this exercise within the session, and the last 2 digits denote the index of the token (word) in this exercise
    ## The token (word)
    ## Part of speech in Universal Dependencies (UD) format
    ## Morphological features in UD format
    ## Dependency edge label in UD format
    ## Dependency edge head in UD format (this corresponds to the last 1-2 digits of the ID in the first column)
    ##     The label to be predicted (0 or 1)
    names(z)<-c("resp.id","token","part.speech","morphology","dependency.label","dependency.head","resp")
    ##
    z$item<-item
    for (i in 1:length(nms)) z[nms[i]]<-dat[i]
    z$resp<-as.numeric(z$resp)
    out[[as.character(j)]]<-z
  }
  data.frame(do.call("rbind",out))
}
#options(warn=2)
#for (i in 1:length(L)) L[[i]]<-f(L[[i]])
library(parallel)
L<-mclapply(L,f,mc.cores=3)

print(L)

library(dplyr)
df <- purrr::map_dfr(L, as_tibble)

df_ <- df %>%
  select(user, item, resp, session, format, time, part.speech, morphology, dependency.label, dependency.head, token)

df_$stem<-df_$item

df_$item <- paste(df_$item, df_$token, sep = "__")

df_$rt<-as.numeric(df_$time)

df_$id<-df_$user


df_ <- df_ %>%
  select(id, item, resp, session, format, rt, part.speech, morphology, dependency.label, dependency.head, stem)

df_reverse_translate <- df_ %>% filter(format == "reverse_translate")

df_reverse_tap <- df_ %>% filter(format == "reverse_tap")

df_listen <- df_ %>% filter(format == "listen")


table(df_listen$resp)


write.csv(df_reverse_translate, "duolingo_es_en__reverse_translate.csv", row.names = FALSE)
write.csv(df_reverse_tap, "duolingo_es_en__reverse_tap.csv", row.names = FALSE)
write.csv(df_listen, "duolingo_es_en__listen.csv", row.names = FALSE)


######################## fr_en ######################## 

con<-file("fr_en.slam.20190204.train")
x<-readLines(con)
close(con)

print(x)


index<-grep("# prompt",x)
index<-c(index,length(x))
L<-list()
for (i in 1:(length(index)-1)) L[[i]]<-x[index[i]:(index[i+1]-1)]

print(L)

f<-function(x) {
  item<-gsub("# prompt:","",x[1])
  users<-grep("user:",x)
  ##
  out<-list()
  for (j in 1:length(users)) {
    z<-strsplit(x[users[j]]," ")[[1]][-1]
    z<-z[z!=""]
    z<-strsplit(z,":")
    nms<-sapply(z,"[",1,drop=FALSE)
    dat<-sapply(z,"[",2,drop=FALSE)
    ##response
    mm<-ifelse(j==length(users),length(x),users[j+1]-1)
    z<-strsplit(x[(users[j]+1):mm]," ")
    z<-lapply(z,function(z) z[z!=""])
    z<-data.frame(do.call("rbind",z))
    ## A Unique 12-digit ID for each token instance: the first 8 digits are a B64-encoded ID representing the session, the next 2 digits denote the index of this exercise within the session, and the last 2 digits denote the index of the token (word) in this exercise
    ## The token (word)
    ## Part of speech in Universal Dependencies (UD) format
    ## Morphological features in UD format
    ## Dependency edge label in UD format
    ## Dependency edge head in UD format (this corresponds to the last 1-2 digits of the ID in the first column)
    ##     The label to be predicted (0 or 1)
    names(z)<-c("resp.id","token","part.speech","morphology","dependency.label","dependency.head","resp")
    ##
    z$item<-item
    for (i in 1:length(nms)) z[nms[i]]<-dat[i]
    z$resp<-as.numeric(z$resp)
    out[[as.character(j)]]<-z
  }
  data.frame(do.call("rbind",out))
}
#options(warn=2)
#for (i in 1:length(L)) L[[i]]<-f(L[[i]])
library(parallel)
L<-mclapply(L,f,mc.cores=3)

print(L)

library(dplyr)
df <- purrr::map_dfr(L, as_tibble)

df_ <- df %>%
  select(user, item, resp, session, format, time, part.speech, morphology, dependency.label, dependency.head, token)

df_$stem<-df_$item

df_$item <- paste(df_$item, df_$token, sep = "__")

df_$rt<-as.numeric(df_$time)

df_$id<-df_$user


df_ <- df_ %>%
  select(id, item, resp, session, format, rt, part.speech, morphology, dependency.label, dependency.head, stem)

df_reverse_translate <- df_ %>% filter(format == "reverse_translate")

df_reverse_tap <- df_ %>% filter(format == "reverse_tap")

df_listen <- df_ %>% filter(format == "listen")


table(df_listen$resp)


write.csv(df_reverse_translate, "duolingo_fr_en__reverse_translate.csv", row.names = FALSE)
write.csv(df_reverse_tap, "duolingo_fr_en__reverse_tap.csv", row.names = FALSE)
write.csv(df_listen, "duolingo_fr_en__listen.csv", row.names = FALSE)

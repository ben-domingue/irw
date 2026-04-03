library(redivis)
user <- redivis$user("bdomingu")
dataset <- user$dataset("irw_meta:bdxt:latest")
table <- dataset$table("metadata:h5gs")
meta <- table$to_tibble()
meta<-meta[,c("table", "n_responses", "n_categories", "n_participants", 
              "n_items", "responses_per_participant", "responses_per_item", 
              "density")]
ii<-grep("^pezzuti",meta$table)
red.tables<-meta$table[ii]

irw_dict=gsheet::gsheet2tbl('https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=1337607315#gid=1337607315')
ii<-grep("^pezzuti",irw_dict$table)
dict.tables<-irw_dict$table[ii]

length(red.tables)
length(dict.tables)
base::table(dict.tables %in% red.tables) #should be all of them
index<-red.tables %in% dict.tables
base::table(base::table(dict.tables))
red.tables[!index] #to be removed

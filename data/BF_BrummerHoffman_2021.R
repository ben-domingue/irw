# Paper: https://doi.org/10.1037/pas0001323
# Data: https://osf.io/p8j2v
library(dplyr)
library(tidyr)

df <- readRDS("./Depression_and_anxiety_question_framing_data_set.Rds")
df <- df |>
  select(-Framing_sequence, -Sex, -Date_of_birth, # Removal of demographic data
         -state, -skin_color, -sexual_orientation, 
         -marital_status, -religion, -kids, -family_income, 
         -cohabitants, -educational_attainment, -educational_years, 
         -working_status, -Date_of_interview, -lte_events) |>
  rename(id=ID, group=Study, date=Date_time_of_interview, age=Age)
df$date <- as.numeric(as.POSIXct(df$date, format="%d/%m/%Y %H:%M:%S", tz="UTC")) # Change date to Unix timestamp

df <- df %>% # Mutate column value types for merging purpose
  mutate(across(-c(id, age, group, date), as.double)) 
df <- pivot_longer(df, cols=c(-id, -group, -date, -age), names_to='item', values_to='resp')

df <- df %>% # Filter out unattempted items of Study Group 2
  filter(!(grepl("^promis_dep", item) & group == "Study 2 - Frame primed by symptom" & is.na(resp)))
df <- df %>%
  filter(!(grepl("^promis_anx", item) & group == "Study 2 - Frame primed by symptom" & is.na(resp)))
na_count <- which(is.na(df$resp))

# Rights recode (irw#2101 precedent): the deposit's PROMIS column names carry the
# bank's own symptom word -- promis_anx_apprehensive_frequency. PROMIS wording does
# not ship (register verdict block, 2026-09-05), so the symptom word is replaced by
# an index while the study's 16-stem x 5-frame design is kept intact. The index is
# the alphabetical rank of the symptom word within its subscale, so no word list is
# stored here and the recode regenerates from the raw file alone.
promis <- grepl("^promis_(anx|dep)_", df$item)
parts  <- regmatches(df$item[promis],
                     regexec("^promis_(anx|dep)_(.+)_(ability|bothered|context|duration|frequency)$",
                             df$item[promis]))
sub    <- vapply(parts, `[`, "", 2)
word   <- vapply(parts, `[`, "", 3)
facet  <- vapply(parts, `[`, "", 4)
rank   <- ave(word, sub, FUN = function(w) match(w, sort(unique(w))))
df$item[promis] <- sprintf("promis_%s_%02d_%s", sub, as.integer(rank), facet)

write.csv(df, "BF_BrummerHoffman_2021.csv", row.names=FALSE)

##bd add'n
x<-read.csv("BF_BrummerHoffman_2021.csv")

nms<-c("promis","phq","gad","audit","grit","whodas",
                                        #"lte",
       "ucla","wemwbs")
for (nm in nms) {
    ii<-grepl(paste("^",nm,sep=''),x$item)
    df<-x[ii,]
                                        #print(unique(y$item))
    fn<-paste(nm,'_BrummerHoffman_2021.Rdata',sep='')
    save(df,file=fn)
    print(nm)
    print(dim(df))
}
  

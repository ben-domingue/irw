library(labelled)
library(tidyverse)
library(haven)

df <- read_sav('DeceptionBan_GameData_OSF.sav')

names(df) <- tolower(names(df))

df <- df |>
  rename(id = participantid) 

df <- df |>
  select(id,
         age,
         attractive,
         intelligent,
         stronger,
         wealthy,
         unpromptedsuspicion,
         promptedsuspicion,
         suspicionconfidence,
         ydeceivedpeople,
         ydeceivedanswers,
         ydeceivedpayment,
         ydeceivedtask,
         ydeceivedother,
         ynotdeceived,
         ydeceptionstandard,
         ynoreason,
         yunclearblank,
         nnotallowed,
         nseemedreal,
         ntrustexp,
         nother,
         ndeceived,
         nnoreason,
         influenceofsuspicion,
         nunclearblank)

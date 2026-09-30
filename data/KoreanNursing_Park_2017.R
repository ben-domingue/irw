library(tidyr)
library(dplyr)

# Source: Harvard Dataverse doi:10.7910/DVN/ECDLXG, "Jeehp-14-20_raw data.tab" (CC0).
# 741 examinees x 50 case-based items, scored 0/1. The file has NO header row.
#
# Until 2026-09-30 this read the file with header=TRUE, which consumed the first
# examinee as the header: that person was lost (740 of 741 ids), and R's
# make.names() turned their 0/1 answers into the item codes below (irw#2096).
# The codes are kept (Ben, 2026-09-30) so existing references and the published
# item text still join: CODES[i] is question i of the exam, in file column order
# (a data note says so). Ids are kept too: the examinee in file row r+1 keeps id r,
# and the restored first examinee is id 741.
CODES <- c("X0", "X1", "X1.1", "X0.1", "X0.2", "X0.3", "X1.2", "X0.4", "X0.5", "X0.6",
           "X0.7", "X0.8", "X1.3", "X0.9", "X0.10", "X0.11", "X0.12", "X0.13", "X0.14", "X0.15",
           "X0.16", "X0.17", "X0.18", "X0.19", "X0.20", "X0.21", "X0.22", "X0.23", "X0.24", "X0.25",
           "X0.26", "X0.27", "X1.4", "X1.5", "X0.28", "X0.29", "X0.30", "X0.31", "X0.32", "X1.6",
           "X0.33", "X0.34", "X0.35", "X1.7", "X0.36", "X0.37", "X0.38", "X1.8", "X1.9", "X0.39")

df <- read.table("https://dataverse.harvard.edu/api/access/datafile/3051798", header=FALSE)
stopifnot(nrow(df) == 741, ncol(df) == length(CODES))
names(df) <- CODES

df$id <- c(741, seq(1, nrow(df) - 1))

df <- df %>%
  pivot_longer(c(-id),
               names_to = "item",
               values_to = "resp") %>%
  filter(!is.na(resp))

write.csv(df, "KoreanNursing_Park_2017.csv", row.names=FALSE)

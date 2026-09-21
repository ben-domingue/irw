library(readxl)

# The deposit (https://osf.io/nwv5a/) is a single extensionless file that is
# actually an xlsx workbook; the ratings are on the PleasantFamiliarConfidence
# sheet. The previous version of this script read a hand-made pipe-delimited
# export of that sheet ("Prelim Data.csv"), which is not in the deposit, so it
# could not be re-run. Read the workbook directly instead.
x <- as.data.frame(read_excel("Prelim Data.xlsx",
                              sheet = "PleasantFamiliarConfidence "))
names(x) <- make.names(names(x))

rater <- x$Subject.Code
# Sample.Name is inconsistently capitalised in the source ("B3 wine- Pleasantness"
# and "B3 wine- pleasantness" are the same wine), which split five of the twelve
# samples into two ids each. id is the WINE here and rater is the person, so the
# split was at the unit of analysis. Fold case to make one sample one id.
id <- tolower(trimws(x$Sample.Name))

intense <- x$How.intense.do.you.find.this.aroma.
pleasant <- x$Pleasantness
familiar <- x$Familiarity
x1 <- data.frame(rater = rater, id = id, item = 'intense',  resp = intense)
x2 <- data.frame(rater = rater, id = id, item = 'pleasant', resp = pleasant)
x3 <- data.frame(rater = rater, id = id, item = 'familiar', resp = familiar)
df <- data.frame(do.call("rbind", list(x1, x2, x3)))
save(df, file = "wine_luckett2021.Rdata")

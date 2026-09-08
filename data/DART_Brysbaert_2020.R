# Paper: https://journalofcognition.org/articles/10.5334/joc.95
# Data: https://osf.io/u4vhs/
library(readxl)
library(tidyr)
library(dplyr)

# The deposited study-1 workbook was damaged by a global find/replace of "ja"
# -> "1" before it was uploaded to OSF (#1950). Four of its 138 headers carry
# the artifact, three of which become IRW item codes:
#
#   "... auteur- [1ne Austen]"      -> Jane Austen
#   "... auteur- [1mes Patterson]"  -> James Patterson
#   "... auteur- [1ne Jessup]"      -> Jane Jessup
#   "Aantal boeken gelezen in het afgelopen 1ar-"  -> "jaar"; dropped below, so
#                                                    it never reaches IRW
#
# Repaired as FIXED STRINGS rather than by reversing the find/replace. A blanket
# "1" -> "ja" would rewrite any legitimate digit, and the point of the repair is
# that we know these three names, not that we can invert the damage.
#
# The names are not reconstructed -- they are copied from
# DART_Brysbaert_2020_3_4_5, which carries the same three people uncorrupted
# ("Jane Austen", "James Patterson", "Jane Jessup") because studies 3-5 were
# deposited as separate workbooks that the find/replace never touched.
#
# `Jane Jessup` is the one that matters most: it is one of the test's foils, a
# non-existent author, correctly rejected by 94% of respondents. Its exact
# string is what a reuser matches on to identify the false-alarm items, and
# "1ne Jessup" matches nothing.
DART1_HEADER_REPAIRS <- c(
  "Is de volgende persoon een auteur- [1ne Austen]"     = "Is de volgende persoon een auteur- [Jane Austen]",
  "Is de volgende persoon een auteur- [1mes Patterson]" = "Is de volgende persoon een auteur- [James Patterson]",
  "Is de volgende persoon een auteur- [1ne Jessup]"     = "Is de volgende persoon een auteur- [Jane Jessup]"
)

repair_dart1_headers <- function(df) {
  hit <- match(names(df), names(DART1_HEADER_REPAIRS))
  found <- sum(!is.na(hit))
  # Stop rather than warn if the deposit no longer needs repairing. Silently
  # doing nothing would leave no signal that the source had changed under us,
  # and this script is only ever run by hand against a freshly downloaded
  # workbook -- the moment to notice is now, not after upload.
  if (found != length(DART1_HEADER_REPAIRS)) {
    stop("DART study 1: expected ", length(DART1_HEADER_REPAIRS),
         " corrupted headers to repair, found ", found,
         ". If OSF has fixed the deposit, delete DART1_HEADER_REPAIRS (#1950).")
  }
  names(df)[!is.na(hit)] <- DART1_HEADER_REPAIRS[hit[!is.na(hit)]]
  df
}

# -------- Process Dataset 1 --------
df1 <- read_excel("raw_data_study1.xlsx")
df1 <- repair_dart1_headers(df1)
df1 <- df1 |>
  rename(id=Toegangscode, mother_language=`Moedertaal-`, gender=`Geslacht-`, age=`Leeftijd-`)
df1$mother_language <- ifelse(!is.na(df1$`Moedertaal- [Andere]`), df1$`Moedertaal- [Andere]`, df1$mother_language)
df1 <- df1 |>
  select(-`Moedertaal- [Andere]`, -`Aantal boeken gelezen in het afgelopen 1ar-`)
df1 <-  pivot_longer(df1, cols=-c(id, gender, age, mother_language), names_to='item', values_to='resp')

save(df1, file="DART_Brysbaert_2020_1.Rdata")
write.csv(df1, "DART_Brysbaert_2020_1.csv", row.names=FALSE)

# -------- Process Dataset 3 & 4 -------- 
df3 <- read_excel("raw_data_study3.xlsx")
df3 <- df3 |>
  rename(id=Subject, item=Name, resp=Correct) |>
  select(-ItemNr, -Condition)

df4 <- read_excel("raw_data_study4.xlsx")
df4 <- df4 |>
  rename(id=Subject, item=Name, resp=Correct) |>
  select(-ItemNr, -Condition)

# -------- Process Dataset 5 -------- 
# Pre-process artist data for accuracy evaluation of Dataset5
artist_data <- read_excel("DART_R Excel versie.xlsx")
Name <- c(artist_data$Name...1, artist_data$Name...4, artist_data$Name...7)
Code <- c(artist_data$Code...2, artist_data$Code...5, artist_data$Code...8)
artist_data <- data.frame(Name, Code)

df5 <- read_excel("raw_data_study5.xlsx")
df5 <- df5 |>
  rename(id=Participantcode)
artist_codes <- setNames(artist_data$Code, artist_data$Name)

# Loop through each artist's column in df5 and encode the responses
for (artist in names(df5)[-1]) {
  # Compare the participants' responses with the correct code and update df5 directly
  df5[[artist]] <- ifelse(df5[[artist]] == artist_codes[artist], 1, 0)
}
df5 <-  pivot_longer(df5, cols=-c(id), names_to='item', values_to='resp')

# -------- Item-code convention --------
# Studies 3 and 4 take `item` from a `Name` COLUMN in their workbooks, which
# spells authors the way the deposit does ("Agatha Christie", "Jean M. Auel").
# Study 5 has no such column: its authors are column HEADERS, pivoted into
# `item` below, and that workbook renders the same names lossily -- spaces
# become underscores ("Agatha_Christie"), middle-initial periods are dropped
# ("Jean M Auel"), and double spaces collapse. Nothing reconciled the two before
# bind_rows(), so the pooled table carried both renderings and 106 of its 158
# authors appeared twice, once per convention, from disjoint samples (#2052).
# The issue reported 90; that count saw only the underscored pairs. Six more
# differ by a dropped middle-initial period or a collapsed double space, and ten
# by initials run together ("J.K. Rowling" / "JK Rowling") -- 106 in all.
#
# No id+item key ever repeated, so no duplicate check could see it. The effect
# was that an IRT model fitted to the pooled table estimated those 106 people
# twice, as unrelated items -- for 106 of 158 authors the pooling this table
# exists for silently did not happen.
#
# The repair maps each study-5 code onto the studies-3/4 spelling of the same
# name, rather than picking a rendering of our own: that column is the deposit's
# own and is what two of the three studies already shipped. Matching is on a
# LETTERS-AND-DIGITS-ONLY key: the study-5 workbook does not merely swap one
# separator for another, it deletes them ("J.K. Rowling" is spelled "JK
# Rowling"), so a key that treated the period as a separator still missed ten
# authors. Dropping every non-alphanumeric character and casefolding catches all
# 106. That is safe here because these codes are personal names: the near-misses
# the DART deliberately contains stay distinct under it ("Susan Smith" vs the
# real "Susan Smit"), and the assertions below fail loudly if that stops holding.
# Whitespace runs are collapsed in the output because a double space is not
# information.
#
# A study-5 author with NO counterpart in studies 3 and 4 is one of the 25
# replacements the paper's Study 5 section introduces (Haruki Murakami, Jeff
# Kinney, ...). Those keep their own name, de-underscored.
#
# This runs AFTER study 5's answer-key lookup, which is keyed on the raw
# underscored headers; normalising earlier would break all 132 of its joins.
squash_ws     <- function(x) trimws(gsub("[[:space:]]+", " ", x))
variant_key   <- function(x) tolower(gsub("[^[:alnum:]]", "", x))

canon_names   <- squash_ws(unique(c(df3$item, df4$item)))
canon_by_key  <- setNames(canon_names, variant_key(canon_names))

canonicalise_item <- function(x) {
  x   <- squash_ws(gsub("_", " ", x, fixed = TRUE))
  hit <- canon_by_key[variant_key(x)]
  ifelse(is.na(hit), x, hit)
}

stacked_df <- bind_rows(
  df3 %>% mutate(group = "Study 3"),
  df4 %>% mutate(group = "Study 4"),
  df5 %>% mutate(group = "Study 5")
) %>% mutate(item = canonicalise_item(item))

# The pooling is only real if the renderings actually collapse onto each other,
# and merging codes must not silently create a repeated id+item key. Assert both
# rather than trust them.
stopifnot(!any(duplicated(variant_key(unique(stacked_df$item)))))
stopifnot(!any(duplicated(stacked_df[, c("id", "item")])))

save(stacked_df, file="DART_Brysbaert_2020_3&4&5.Rdata")
write.csv(stacked_df, "DART_Brysbaert_2020_3&4&5.csv", row.names=FALSE)

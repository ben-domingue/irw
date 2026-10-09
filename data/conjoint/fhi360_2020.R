##Contraceptive microarray-patch discrete choice experiment (India, Nigeria) from
##FHI 360. (2020). Discreet choice experiment survey for development of a contraceptive
##microarray patch in India and Nigeria (FHI360 2017-2018) [Data set]. Harvard Dataverse.
##https://doi.org/10.7910/DVN/TOSSWN  (CC0 1.0, no restricted files; no article linked)
##Files read: MNPIndiaSurvey_data.tab (original csv), Nigeria_Sample1_final_data.tab (original
##xlsx), Nigeria_Sample2_final_data.tab (original csv): one row per respondent, the chosen concept
##(1/2) of each task in CBC_Random<k>, design version in sys_CBCVersion_CBC; the Sawtooth design
##files MNPIndiaSurvey_CBC1_1509713792.cgi, Nigeria_Sample1_final_CBC1_1509544491.cgi,
##Nigeria_Sample2_final_CBC1_1520005048.cgi (binary; the trailing text block states 300 versions,
##2 concepts, no None option, balanced overlap, no prohibitions, the task count and levels per
##attribute); the Lighthouse Studio study files MNPIndiaSurvey.ssi, Nigeria_Sample1_final.ssi,
##Nigeria_Sample2_final.ssi (text: attribute and level text shown, in order). Read as text: the
##English questionnaires MNP DCE Survey India Final.docx / Nigeria Final.docx (instructions,
##question wording; their example card is illustrative and its attributes are not the fielded ones).
##Usage: Rscript fhi360_2020.R <raw dir> <output dir>
##
##Women of reproductive age (New Delhi, India; Ibadan, Nigeria; interviewer-administered on a tablet
##in the local language) chose between two options of a not-yet-available contraceptive patch on
##each card: "Look carefully at the features of the two method options. Which of these methods do
##you prefer?" (English master questionnaire; respondents heard/saw Hindi or Yoruba). Forced
##choice, no None option. THREE TABLES (separate samples and design files; Nigeria sample 2 used a
##different design):
##  fhi360_2020_mnp_india: 10 random tasks, 6 attributes (pain when the needles go in, skin
##    reaction, location, size, duration of protection, effect on menstruation); Hindi text.
##  fhi360_2020_mnp_nigeria_s1: same 10-task, 6-attribute design structure; Yoruba text.
##  fhi360_2020_mnp_nigeria_s2: 12 random tasks, 5 attributes (no menstruation attribute); Yoruba.
##Decoding the design (.cgi): a 25-byte header (version/time stamp, attributes, versions 300, tasks,
##concepts), then one byte per version x task x concept x attribute, 0-based level index in .ssi
##order, then a 4-byte length and the text block. Checked: each attribute takes exactly as many
##values as the text block's levels per attribute, with counts equal to within 2 across the 300
##versions; the byte block ends exactly at the length field. Version v of the data = block v.
##Level text is the displayed text from the .ssi with HTML and the picture tag removed (each level
##was shown with an illustration; the English .ssi level names, e.g. "no pain", "light prick",
##are not stored). Sanity check: the decoded levels give the expected strong preferences, see the
##spot check line.
##Spot check (share chosen): India menstruation regular 0.81, irregular 0.43, no period 0.26; skin
##reaction one day 0.55 vs three days 0.45; Nigeria s2 duration 6 months 0.69, 3 months 0.52, 1 month
##0.29; pain none 0.62, light 0.49, hard 0.39. Ordered as expected, which a wrong decoding would not give.
##No task shows two identical profiles. N: 496, 530 and 416 respondents with a design version (the
##deposit description gives no sample sizes; no article checked).
##Task = random-task number (CBC_Random1.. in order). Dropped: the fixed holdout task CBC_Fixed1
##(its position among the screens and its level coding are not documented with certainty);
##respondents with no design version (did not reach the DCE: India 31, Nigeria 1 13); tasks without
##an answer; every questionnaire item (sociodemographics are numeric codes; the coding sits in the
##questionnaire docx and was not mapped here) and all sys_ fields (IP address field holds only
##127.0.0.1; user agent, device ID, timings). Respondent id = sys_RespNum re-keyed to integers.
library(data.table); library(readxl)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
attrs6 <- c("pain", "reaction", "Location", "size", "duration", "menstruation")
lev_en <- list(pain = c("no pain", "light prick", "hard prick"), reaction = c("one day", "three days"),
               Location = c("foot", "kneecap", "wrist"), size = c("small", "medium", "large"),
               duration = c("one month", "three months", "six months"),
               menstruation = c("regular", "irregular", "amenorrhea"))
strip <- function(x) trimws(gsub("\\s+", " ", gsub("<[^>]*>", " ", x)))
ssi_levels <- function(f, at) {
  L <- sub("\r$", "", readLines(f, encoding = "UTF-8", warn = FALSE))
  i0 <- which(L == "pain")[1]; stopifnot(!is.na(i0))
  res <- list(); i <- i0
  for (k in at) {
    i <- which(L == k & seq_along(L) >= i)[1]; stopifnot(!is.na(i))
    res[[k]] <- vapply(lev_en[[k]], function(e) {
      j <- which(L == e & seq_along(L) > i)[1]; stopifnot(!is.na(j))
      t <- strip(L[j - 1]); if (t == "") t <- strip(L[j - 2]); stopifnot(t != ""); i <<- j; t }, "")
  }
  res
}
read_cgi <- function(f, nT, nA, nlev) {
  b <- readBin(f, "raw", file.info(f)$size)
  txt <- rawToChar(b[(grepRaw("This CBC", b)):length(b)])
  stopifnot(grepl(paste0("Number of Random Choice Tasks:  ", nT), txt), grepl("Number of Questionnaire Versions:  300", txt),
            grepl("excluding None option\\):  2", txt), grepl("Prohibitions:  None", txt),
            grepl(paste0("Number of Levels per Attribute:  ", paste(nlev, collapse = " ")), txt))
  n <- 300 * nT * 2 * nA
  v <- as.integer(b[26:(25 + n)])
  stopifnot(grepRaw("This CBC", b) == 26 + n + 8)   # design bytes end at the 4-byte length field + CR LF LF LF
  d <- data.table(version = rep(1:300, each = nT * 2 * nA), task = rep(rep(1:nT, each = 2 * nA), 300),
                  profile = rep(rep(1:2, each = nA), 300 * nT), a = rep(1:nA, 300 * nT * 2), lev = v)
  for (k in 1:nA) { x <- d[a == k]$lev; stopifnot(all(x %in% 0:(nlev[k] - 1)), diff(range(table(x))) <= 2) }
  dcast(d, version + task + profile ~ a, value.var = "lev")
}
specs <- list(
  fhi360_2020_mnp_india = list(data = "MNPIndiaSurvey_data.csv", cgi = "MNPIndiaSurvey_CBC1_1509713792.cgi",
                               ssi = "MNPIndiaSurvey.ssi", nT = 10, at = attrs6, n = 496),
  fhi360_2020_mnp_nigeria_s1 = list(data = "Nigeria_Sample1_final_data.xlsx", cgi = "Nigeria_Sample1_final_CBC1_1509544491.cgi",
                                    ssi = "Nigeria_Sample1_final.ssi", nT = 10, at = attrs6, n = 530),
  fhi360_2020_mnp_nigeria_s2 = list(data = "Nigeria_Sample2_final_data.csv", cgi = "Nigeria_Sample2_final_CBC1_1520005048.cgi",
                                    ssi = "Nigeria_Sample2_final.ssi", nT = 12, at = attrs6[1:5], n = 416))
cn <- c(pain = "pain", reaction = "skin_reaction", Location = "location", size = "size", duration = "duration",
        menstruation = "menstruation")
for (nm in names(specs)) {
  sp <- specs[[nm]]
  s <- if (grepl("xlsx$", sp$data)) as.data.table(read_excel(file.path(raw, sp$data))) else fread(file.path(raw, sp$data))
  nlev <- lengths(lev_en[sp$at])
  D <- read_cgi(file.path(raw, sp$cgi), sp$nT, length(sp$at), nlev)
  txt <- ssi_levels(file.path(raw, sp$ssi), sp$at)
  s <- s[!is.na(sys_CBCVersion_CBC)]
  stopifnot(uniqueN(s$sys_RespNum) == nrow(s), all(s$sys_CBCVersion_CBC %in% 1:300))
  ch <- rbindlist(lapply(1:sp$nT, function(t) data.table(resp = s$sys_RespNum, version = as.integer(s$sys_CBCVersion_CBC),
                                                         task = t, v = s[[paste0("CBC_Random", t)]])))
  ch <- ch[!is.na(v)]; stopifnot(all(ch$v %in% 1:2))
  d <- merge(ch, D, by = c("version", "task"), allow.cartesian = TRUE)
  ids <- sort(unique(d$resp))
  o <- d[, .(id = match(resp, ids), task, profile, choice = as.integer(profile == v))]
  for (k in seq_along(sp$at)) o[, paste0("attr_", cn[[sp$at[k]]]) := unname(txt[[sp$at[k]]][d[[as.character(k)]] + 1L])]
  stopifnot(o[, sum(choice), .(id, task)][, all(V1 == 1)], o[, .N, .(id, task)][, all(N == 2)], uniqueN(o$id) == sp$n,
            !anyNA(o))
  setorder(o, id, task, profile)
  fwrite(o, file.path(out, paste0(nm, ".csv")))
  cat(nm, uniqueN(o$id), "respondents", nrow(o), "rows\n")
}

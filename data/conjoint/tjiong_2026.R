##Mobile-data-package discrete choice experiment (zero-price effects) from
##Tjiong, J., Dekker, T., Hess, S., Giergiczny, M., Ojeda-Cabral, M., & Czajkowski, M. (2026).
##Capturing zero-price effects in stated choice surveys: implications for willingness-to-pay
##and welfare. Journal of Choice Modelling, 58, 100582. https://doi.org/10.1016/j.jocm.2025.100582
##Data: Zenodo record 20179488, doi:10.5281/zenodo.20179488, CC BY 4.0 (record licence; no README).
##File read: Mobile_Results.xlsx, sheets ngene1 (choices, long), D1_B1 ... D3_B3 (design
##cards with the app's display strings), dane1 (respondent sheet). Sheet indeksy (student
##index numbers, empty first/last-name columns) is not read. Design facts and wording from the
##University of Warsaw working-paper version (WNE WP 15/2026, sections 2.1-2.2.4, Table 1).
##Usage: Rscript tjiong_2026.R <raw dir> <output dir>
##
##University of Warsaw students, December 2017, survey app. Each answered three choice
##experiments in sequence (the paper discusses order effects "following SP1" in SP2), 26 tasks:
##  SP1 (trial_treatment "SP1", tasks 1-8): free campus Wi-Fi status quo (profile 1) vs two 4G
##      LTE data packages (profiles 2-3);
##  SP2 ("SP2", tasks 9-16): the same, but a 1 or 3 zl Wi-Fi fee can apply to all alternatives;
##  SP3 ("SP3", tasks 17-26): two 4G packages only (profiles 1-2), no status quo, 4G fee can be
##      0-3 zl.
##ONE TABLE, tjiong_2026_mobile_data: same respondents, same four attributes and choice
##question in all three; the authors estimate each treatment and also a joint model with scale
##parameters (paper section 4.4). trial_treatment says which; trial_block = the design block.
##Attributes, as the app's display strings in the design sheets (column 20/16 tuples):
##  attr_wifi_fee (monthly campus Wi-Fi fee, "0 zl"/"1 zl"/"3 zl"; in SP3 the tuples have no Wi-Fi
##  entry -> "(not shown)"); attr_data_fee (monthly 4G fee, "0 zl".."40 zl"); attr_data_limit
##  (GB/month, "3 GB".."20 GB"); attr_devices (number of devices, "1"/"3"). The status-quo
##  alternative shows "-" for the three 4G attributes (its tuple), kept as displayed; because
##  it shows a Wi-Fi fee it is stored as a profile (choice = choosing it), not as an opt-out.
##  "zl" above is the stored "zł". The attribute names shown in the app are not deposited (Figure 1
##  is an image); levels were checked against the ngene1 codes card by card (stopifnot).
##Outcome: choice = ngene1 `best` (1 = chosen alternative), exactly one per task. Question
##wording not deposited: paraphrased from the paper ("choose between retaining the free campus-
##wide Wi-Fi service ... or to purchase a 4G LTE data package").
##Task = treatment offset + ngene1 `step` (undocumented; taken as the within-treatment display
##position, it is a permutation of 1-8 or 1-10 per respondent; `cs` is the
##Ngene card number, the design sheets' "Choice Task # Ngene" column). Treatment order
##SP1 -> SP2 -> SP3 is from the paper's text;
##profile = ngene1 alternative number (left-to-right order on screen not documented).
##Fixed blocked Bayesian D-efficient designs (SP1, SP2: 2 blocks of 8; SP3: 3 blocks of 10;
##62 cards); each respondent got one block per treatment (ngene1 bigset A-L).
##Dropped: 5 student ids that appear twice in ngene1 and dane1 (two complete sessions each,
##136 rows; which one counts cannot be told), so N = 297 of the paper's 302; response times;
##the dane1 questionnaire items A1-B6 (numeric codes, no codebook), the free-text SQ1T reasons,
##start/end timestamps. Student index numbers (university IDs) re-keyed to 1..N.
##cov_sex_code = dane1 M0 as stored ("K"/"M"; presumably Polish kobieta/mezczyzna, but no codebook
##says so, hence _code).
##Spot check: respondents choosing the status quo in all 8 tasks (non-traders) are 11.1% in SP1
##and 8.8% in SP2; the paper reports 11% and 9% (section 2.2.4).
suppressMessages(library(readxl)); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
f <- file.path(raw, "Mobile_Results.xlsx")
n <- as.data.table(suppressWarnings(suppressMessages(read_excel(f, "ngene1", col_types = "text"))))
setnames(n, c("student", "step", "cs", "alt", "bigset", "smallset", "best", "time", "wifi", "c4g", "data", "dev"))
dup <- n[, .N, student][N > 68, student]; stopifnot(length(dup) == 5)
n <- n[!student %in% dup]
n[, design := substr(smallset, 1, 2)]
# display strings from the design sheets, card by card
cards <- rbindlist(lapply(c("D1_B1", "D1_B2", "D2_B1", "D2_B2", "D3_B1", "D3_B2", "D3_B3"), function(s) {
  x <- suppressMessages(read_excel(f, s, col_names = FALSE, col_types = "text"))
  x <- x[grepl("^D", x[[1]]) & !is.na(x[[2]]), ]
  tx <- x[[ncol(x)]]
  rbindlist(lapply(seq_along(tx), function(i) {
    tu <- regmatches(tx[i], gregexpr("\\(('[^)]*)\\)", tx[i]))[[1]]
    rbindlist(lapply(seq_along(tu), function(j) {
      v <- gsub("'", "", strsplit(gsub("^\\(|\\)$", "", tu[j]), "',")[[1]])
      v <- trimws(v); v <- v[-length(v)]
      if (length(v) == 3) v <- c("(not shown)", v)
      data.table(smallset = s, cs = as.character(x[[5]][i]), alt = as.character(j),
                 attr_wifi_fee = v[1], attr_data_fee = v[2], attr_data_limit = v[3], attr_devices = v[4])
    }))
  }))
}))
d <- merge(n, cards, by = c("smallset", "cs", "alt"), all.x = TRUE)
stopifnot(!anyNA(d$attr_devices))
num <- function(x) sub(" .*", "", x)
stopifnot(d[design != "D3", all(num(attr_wifi_fee) == wifi)], d[design == "D3", all(wifi == "-")],
          d[is.na(c4g), all(attr_data_fee == "-" & attr_data_limit == "-" & attr_devices == "-")],
          d[!is.na(c4g), all(num(attr_data_fee) == c4g & num(attr_data_limit) == data & attr_devices == dev)])
d[, `:=`(trial_treatment = c(D1 = "SP1", D2 = "SP2", D3 = "SP3")[design],
         task = c(D1 = 0L, D2 = 8L, D3 = 16L)[design] + as.integer(step), profile = as.integer(alt),
         choice = as.integer(!is.na(best)))]
stopifnot(d[, sum(choice), .(student, task)][, all(V1 == 1)], d[, .N, .(student, task)][, all(N == fifelse(task > 16, 2L, 3L))])
d[, trial_block := smallset]
dn <- as.data.table(suppressMessages(read_excel(f, "dane1", col_types = "text")))[!INDEX %in% dup]
stopifnot(!anyDuplicated(dn$INDEX), all(unique(d$student) %in% dn$INDEX), all(dn$M0 %in% c("K", "M")))
d[, cov_sex_code := dn$M0[match(student, dn$INDEX)]]
d[, id := match(student, sort(unique(student)))]
d <- d[, .(id, task, profile, choice, attr_wifi_fee, attr_data_fee, attr_data_limit, attr_devices,
           trial_treatment, trial_block, cov_sex_code)]
setorder(d, id, task, profile)
fwrite(d, file.path(out, "tjiong_2026_mobile_data.csv"))

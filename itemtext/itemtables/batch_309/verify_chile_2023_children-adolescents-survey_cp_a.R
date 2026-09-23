# verify_chile_2023_children-adolescents-survey_cp_a.R
#
# WHAT IS BEING VERIFIED
# ----------------------
# Every shipped item_text / option_text pair in
# chile_2023_children-adolescents-survey_cp_a__items.csv is keyed to a variable
# NAME (ac1_1 ... ac6_77) of the EANNA 2023 deposit. The do-file
# data/chile_2023_children-adolescents-survey.do carries that name straight
# through (`gen item = "`var'"`), so `item` IS the source column name, and the
# deposit's own variable labels / the Cuestionario Cuidador(a) Principal tie
# each name to its wording. mapping_basis is therefore data_labels; this script
# exists anyway so that the tie between LIVE codes and DEPOSIT variables is
# re-checkable rather than asserted.
#
# Falsifiable prediction: re-running the do-file's filter (rp2 == 1, i.e. the
# primary caregiver; -98 'Sin Dato' and the other mvdecode codes set missing)
# over the deposit's own "Base de datos EANNA 2023.dta" gives, for every
# variable and every value, a count. If the live item code ac2_1 did not hold
# the deposit's ac2_1 (say it had been swapped with ac2_2), the live counts
# would sit against the wrong profile. The 30 profiles below are all distinct,
# so the route distinguishes every item from every other -- including inside
# the ac1_*/ac2_* (n=17631), ac5_* (n=5035) and ac6_* (n=506) blocks whose
# per-item n are identical and could NOT be told apart by n alone.
#
# The deposit counts are hard-coded (template rule 4): they were computed once
# from the BIDAT STATA download of dataset e3ceb7aa-95a8-4838-909b-155719847d21
# (17 MB) with haven::read_dta, and a published deposit will not change. Value
# labels in that .dta and in the codebook (sheet '2. Cuidador(a) Principal')
# are 1 = 'Sí', 2 = 'No' for every one of the 30 variables, and the
# questionnaire states "Las alternativas de respuesta se encuentran numeradas
# y coinciden con el valor que aparece en la base de datos".
#
# Live counts come from a server-side GROUP BY, not irw_fetch(): the table is
# 529,770 rows and a full export is not warranted for 60 numbers.

suppressMessages(library(irw))

TABLE <- "chile_2023_children-adolescents-survey_cp_a"
TOL   <- 0

DEPOSIT <- data.frame(matrix(c(
  "ac1_1", 1, 1106,
  "ac1_1", 2, 16525,
  "ac1_2", 1, 639,
  "ac1_2", 2, 16992,
  "ac1_3", 1, 919,
  "ac1_3", 2, 16712,
  "ac1_4", 1, 407,
  "ac1_4", 2, 17224,
  "ac1_5", 1, 62,
  "ac1_5", 2, 17569,
  "ac1_6", 1, 17,
  "ac1_6", 2, 17614,
  "ac1_7", 1, 276,
  "ac1_7", 2, 17355,
  "ac1_8", 1, 40,
  "ac1_8", 2, 17591,
  "ac2_1", 1, 4328,
  "ac2_1", 2, 13303,
  "ac2_2", 1, 2825,
  "ac2_2", 2, 14806,
  "ac2_3", 1, 565,
  "ac2_3", 2, 17066,
  "ac2_4", 1, 468,
  "ac2_4", 2, 17163,
  "ac2_5", 1, 1060,
  "ac2_5", 2, 16571,
  "ac3", 1, 5035,
  "ac3", 2, 3210,
  "ac5_1", 1, 3006,
  "ac5_1", 2, 2029,
  "ac5_10", 1, 2260,
  "ac5_10", 2, 2775,
  "ac5_2", 1, 1102,
  "ac5_2", 2, 3933,
  "ac5_3", 1, 1935,
  "ac5_3", 2, 3100,
  "ac5_4", 1, 900,
  "ac5_4", 2, 4135,
  "ac5_5", 1, 1006,
  "ac5_5", 2, 4029,
  "ac5_6", 1, 22,
  "ac5_6", 2, 5013,
  "ac5_7", 1, 3017,
  "ac5_7", 2, 2018,
  "ac5_77", 1, 129,
  "ac5_77", 2, 4906,
  "ac5_8", 1, 506,
  "ac5_8", 2, 4529,
  "ac5_9", 1, 1050,
  "ac5_9", 2, 3985,
  "ac6_1", 1, 11,
  "ac6_1", 2, 495,
  "ac6_2", 1, 25,
  "ac6_2", 2, 481,
  "ac6_3", 1, 78,
  "ac6_3", 2, 428,
  "ac6_4", 1, 128,
  "ac6_4", 2, 378,
  "ac6_77", 1, 123,
  "ac6_77", 2, 383
), ncol = 3, byrow = TRUE), stringsAsFactors = FALSE)
names(DEPOSIT) <- c("item", "resp", "dep_n")
DEPOSIT$resp  <- as.integer(DEPOSIT$resp)
DEPOSIT$dep_n <- as.integer(DEPOSIT$dep_n)

# --- the shipped mapping, read from the CSV beside this script -------------
here <- tryCatch({
    a <- commandArgs(trailingOnly = FALSE)
    f <- sub("^--file=", "", a[grep("^--file=", a)])
    if (length(f)) dirname(normalizePath(f[1])) else "."
}, error = function(e) ".")
items_csv <- file.path(here, paste0(TABLE, "__items.csv"))
shipped <- if (file.exists(items_csv)) read.csv(items_csv, stringsAsFactors = FALSE) else NULL

# --- live per-item x per-resp counts, server side --------------------------
ref <- irw::irw_table_sets(TABLE, source = "core")$table
sql <- sprintf(
  "SELECT item, resp, COUNT(*) AS n FROM `%s` WHERE resp IS NOT NULL GROUP BY item, resp",
  ref)
live <- suppressWarnings(redivis::query(sql))$to_data_frame()
live$resp <- as.integer(live$resp)
live$n    <- as.integer(live$n)

m <- merge(DEPOSIT, live, by = c("item", "resp"), all = TRUE)
m <- m[order(m$item, m$resp), ]
m$diff <- m$n - m$dep_n

cat(sprintf("%-8s %5s %10s %10s %6s  %s\n",
            "item", "resp", "deposit_n", "live_n", "diff", "shipped item_text / option_text"))
for (i in seq_len(nrow(m))) {
    txt <- ""
    if (!is.null(shipped)) {
        k <- which(shipped$item == m$item[i] & shipped$resp == m$resp[i])
        if (length(k)) txt <- paste0(substr(shipped$item_text[k[1]], 1, 50), " / ",
                                     shipped$option_text[k[1]])
    }
    cat(sprintf("%-8s %5d %10s %10s %6s  %s\n", m$item[i], m$resp[i],
                ifelse(is.na(m$dep_n[i]), "-", m$dep_n[i]),
                ifelse(is.na(m$n[i]), "-", m$n[i]),
                ifelse(is.na(m$diff[i]), "?", m$diff[i]), txt))
}

n_cells <- nrow(m)
exact   <- sum(!is.na(m$diff) & m$diff == 0)
worst   <- suppressWarnings(max(abs(m$diff), na.rm = TRUE))
cat(sprintf("\ncells compared: %d | exact: %d | largest |diff|: %s (tolerance %d)\n",
            n_cells, exact, ifelse(is.finite(worst), worst, "NA"), TOL))

prof <- tapply(seq_len(nrow(DEPOSIT)), DEPOSIT$item,
               function(ix) paste(DEPOSIT$dep_n[ix][order(DEPOSIT$resp[ix])], collapse = "/"))
cat(sprintf("distinct (Si/No) frequency profiles: %d of %d items\n",
            length(unique(prof)), length(prof)))

# Shipped option_text must read Si for 1 and No for 2 on every item.
opt_ok <- TRUE
if (!is.null(shipped)) {
    o1 <- unique(shipped$option_text[shipped$resp == 1])
    o2 <- unique(shipped$option_text[shipped$resp == 2])
    cat(sprintf("shipped option_text at resp=1: %s | resp=2: %s\n",
                paste(o1, collapse = ","), paste(o2, collapse = ",")))
    opt_ok <- identical(o1, "Sí") && identical(o2, "No")
} else cat("items CSV not found beside this script; option_text check skipped\n")

cat("\nWhat this establishes: each of the 30 live item codes carries exactly the\n",
    "per-value counts of the deposit variable of the same name under the\n",
    "do-file's caregiver filter, and all 30 profiles are distinct, so no pair of\n",
    "items could be exchanged without breaking the match; with 1=Si/2=No fixed\n",
    "by the .dta value labels it pins option_text too.\n",
    "What it does NOT establish: that the deposit's own variable labels are\n",
    "correctly assigned at source -- nothing in the deposit is independent of it.\n", sep = "")

ok <- is.finite(worst) && worst <= TOL &&
      all(!is.na(m$dep_n)) && all(!is.na(m$n)) &&
      length(unique(prof)) == length(prof) && opt_ok
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

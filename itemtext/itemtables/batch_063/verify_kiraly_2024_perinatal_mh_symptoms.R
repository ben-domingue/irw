# verify_kiraly_2024_perinatal_mh_symptoms.R
#
# Step 5b re-runnable evidence. mapping_basis = data_labels: the IRW `item` codes
# ARE the column names of the study's S2 Data workbook (data/kiraly_2024_
# perinatal_mh_providers.py, SYMPTOM_COLS, melted by name -- no positional step),
# and each column name is a snake_case rendering of one of the 19 choices of the
# survey's symptom-checklist question. The shipped WORDS come from a second
# source -- the study's own Qualtrics obstetrician form (S1 File,
# SV_7TDMCGYEnrYiSyN), question QID13 -- so the code->column tie and the
# code->wording tie are checked separately.
#
# CHECK 1 (code <-> source column): per-item n and per-item YES count in the S2
#   workbook must reproduce the live values exactly. Discriminating for 15 of 19
#   items; four yes-counts tie in pairs (43, 46, 48, 25).
# CHECK 2 (paper <-> live, breaks those ties): the PLOS article's Results text
#   names nine symptoms in plain English with the % of OBSTETRICIANS endorsing
#   each. Recomputing those from the live data (cov_provider_group ==
#   "Obstetrician") must reproduce them. This is a paper->live tie that never
#   passes through the workbook, and it separates every one of the four tied
#   pairs (Excessive_crying 100 vs Intrusive_thoughts 73; Feelings_of_failure 93
#   vs Little_feeling_of_enjoyment 80; Hopelessness 67 vs Agitation 87; Anxiety
#   87 vs Insomnia 80).
# CHECK 3 (column <-> shipped wording): each shipped item_text, reduced to
#   content tokens, must have its OWN item code as its single best token-overlap
#   match among all 19 codes. A swap of any two item_texts breaks the identity
#   permutation.
#
# Not checked here because it is not a mapping question: the shipped
# `instructions` stem is the obstetrician form's wording; the pediatrician/NP
# form (SV_78tIETxvPI5iqNf), taken by 85 of the 101 respondents, is paginated
# behind an SSO-gated preview and its stem could not be retrieved. See
# notes_kiraly_2024_perinatal_mh_symptoms.csv.

suppressMessages(library(irw))

TABLE <- "kiraly_2024_perinatal_mh_symptoms"
XLSX  <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0306265.s002")

items_csv <- file.path(dirname(sub("^--file=", "",
    commandArgs(FALSE)[grep("^--file=", commandArgs(FALSE))][1])),
    paste0(TABLE, "__items.csv"))
shipped <- unique(read.csv(items_csv, colClasses = "character")[, c("item", "item_text")])

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
live <- data.frame(item = sort(unique(d$item)), stringsAsFactors = FALSE)
live$n   <- sapply(live$item, function(x) sum(d$item == x))
live$yes <- sapply(live$item, function(x) sum(d$resp[d$item == x] == 1))

## ---- CHECK 1 --------------------------------------------------------------
tmp <- tempfile(fileext = ".xlsx")
utils::download.file(XLSX, tmp, quiet = TRUE, mode = "wb")
raw <- as.data.frame(readxl::read_excel(tmp))
src_n   <- sapply(live$item, function(x) sum(tolower(trimws(as.character(raw[[x]]))) %in% c("yes", "no")))
src_yes <- sapply(live$item, function(x) sum(tolower(trimws(as.character(raw[[x]]))) == "yes"))

cat(sprintf("%-84s %6s %6s %7s %7s\n", "item (= S2 workbook column name)",
            "live n", "xlsx n", "live yes", "xlsx yes"))
for (i in seq_len(nrow(live)))
    cat(sprintf("%-84s %6d %6d %7d %7d\n", substr(live$item[i], 1, 84),
                live$n[i], src_n[i], live$yes[i], src_yes[i]))
ok1 <- all(live$n == src_n) && all(live$yes == src_yes)
tied <- sum(duplicated(live$yes) | duplicated(live$yes, fromLast = TRUE))
cat(sprintf("\nCHECK 1 code<->column: %d/%d items reproduce n AND yes-count exactly (%d items sit in tied yes-count pairs -> CHECK 2)\n",
            sum(live$n == src_n & live$yes == src_yes), nrow(live), tied))

## ---- CHECK 2 --------------------------------------------------------------
# PLOS ONE 19(10):e0306265, Results, "Identification of mental health symptoms".
PUB <- c(Excessive_crying = 100, Feeling_little_to_no_attachment_to_the_baby = 100,
         Little_feeling_of_enjoyment = 80, Feelings_of_failure = 93.3,
         Hopelessness = 66.7, Agitation_with_self_others_baby = 86.7,
         Fear_of_being_alone_with_the_baby = 73.3, Fear_these_symptoms_will_last = 80,
         Anxiety = 86.7)
ob <- subset(d, cov_provider_group == "Obstetrician")
cat(sprintf("\n%-46s %10s %10s %7s\n", "item", "paper %ob", "live %ob", "diff"))
ok2 <- TRUE
for (nm in names(PUB)) {
    v <- ob$resp[ob$item == nm]
    o <- 100 * mean(v)
    if (abs(o - PUB[[nm]]) > 0.7) ok2 <- FALSE
    cat(sprintf("%-46s %10.1f %10.1f %7.2f\n", substr(nm, 1, 46), PUB[[nm]], o, o - PUB[[nm]]))
}
# the one cross-group figure the paper prints
oth <- subset(d, cov_provider_group == "Other_Provider" & item == "Anxiety")
cat(sprintf("%-46s %10.1f %10.1f %7.2f\n", "Anxiety (other providers)", 43.2,
            100 * mean(oth$resp), 100 * mean(oth$resp) - 43.2))
if (abs(100 * mean(oth$resp) - 43.2) > 0.7) ok2 <- FALSE
cat(sprintf("\nCHECK 2 paper<->live: %s (n obstetrician per item = %d)\n",
            ifelse(ok2, "all 9 named symptoms + the Anxiety cross-group figure reproduce", "FAILED"),
            sum(ob$item == "Anxiety")))

## ---- CHECK 3 --------------------------------------------------------------
toks <- function(x) {
    x <- tolower(gsub("[^a-z0-9]+", " ", tolower(x)))
    setdiff(strsplit(trimws(x), " +")[[1]],
            c("a", "the", "of", "to", "in", "with", "or", "that", "is", "and", "no"))
}
code_t <- lapply(shipped$item, toks); text_t <- lapply(shipped$item_text, toks)
n <- nrow(shipped); J <- matrix(0, n, n)
for (i in seq_len(n)) for (j in seq_len(n)) {
    a <- text_t[[i]]; b <- code_t[[j]]
    J[i, j] <- length(intersect(a, b)) / length(union(a, b))
}
best <- apply(J, 1, which.max); self <- diag(J)
runner <- sapply(seq_len(n), function(i) max(J[i, -i]))
cat(sprintf("\n%-52s %6s %6s %s\n", "shipped item_text", "self J", "next J", "best match is own code"))
for (i in seq_len(n))
    cat(sprintf("%-52s %6.2f %6.2f %s\n", substr(shipped$item_text[i], 1, 52),
                self[i], runner[i], ifelse(best[i] == i, "yes", "NO")))
ok3 <- all(best == seq_len(n))
cat(sprintf("\nCHECK 3 column<->wording: %d/%d item_texts match their own code best (min self-J %.2f, max rival J %.2f)\n",
            sum(best == seq_len(n)), n, min(self), max(runner)))

cat(if (ok1 && ok2 && ok3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

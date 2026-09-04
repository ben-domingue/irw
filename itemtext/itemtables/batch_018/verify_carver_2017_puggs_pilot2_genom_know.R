# verify_carver_2017_puggs_pilot2_genom_know.R
#
# WHAT IS BEING VERIFIED (the mapping, not the plumbing):
#   (a) that live item code `Qk` is the pilot-2 raw file's column `Qk` -- i.e.
#       that the shipped item_text, taken from S1 Table's printed item number k,
#       belongs to that code; and
#   (b) that the shipped answer key (S2 Text Code Book, Section 4:
#       1 = correct answer is True, 2 = correct answer is False) is the key that
#       actually produced the live 0/1 `resp`.
#
# ROUTE: full source re-run. The live table's resp is a correctness score, so
# per-item (n, k=#correct) is a joint fingerprint of BOTH the column identity and
# the key direction: flipping any single item's key sends k -> n-k, and n != 2k
# for all 16 items, so a flip on any item is detectable. Recomputing (n, k) from
# S6 Table (the pilot-2 raw xlsx) under the Code Book key and matching all 32
# numbers exactly pins every item individually.
#
# Live side uses a server-side GROUP BY (no irw_fetch export).

suppressMessages(library(redivis))
suppressMessages(library(readxl))

TBL  <- "datapages.item_response_warehouse_3:5xaj:v4_0.carver_2017_puggs_pilot2_genom_know:8kfe"
XLSX <- ".cache/carver_2017_puggs_pilot2_genom_know/s006.xlsx"
URL  <- paste0("https://journals.plos.org/plosone/article/file",
               "?type=supplementary&id=10.1371/journal.pone.0169808.s006")

if (!file.exists(XLSX)) {
    dir.create(dirname(XLSX), recursive = TRUE, showWarnings = FALSE)
    download.file(URL, XLSX, mode = "wb", quiet = TRUE)
}

# S2 Text (Code Book, second pilot), Section 4. 1 = "True" is correct, 2 = "False".
KEY <- c(Q10=2,Q11=1,Q12=1,Q13=2,Q14=1,Q15=1,Q16=1,Q17=1,Q18=2,Q19=2,
         Q20=2,Q21=1,Q22=2,Q23=1,Q24=2,Q25=1)

live <- redivis$query(sprintf(
    "SELECT item, COUNT(*) AS n, SUM(resp) AS k FROM `%s` GROUP BY item ORDER BY item", TBL))$to_data_frame()
live <- as.data.frame(live)

raw <- as.data.frame(readxl::read_excel(XLSX, sheet = "Sheet1"))
src <- do.call(rbind, lapply(names(KEY), function(it) {
    v <- suppressWarnings(as.numeric(raw[[it]]))
    v <- v[!is.na(v) & v %in% c(1, 2)]          # 3 = don't know, 99 = missing: dropped
    data.frame(item = it, n_src = length(v), k_src = sum(v == KEY[[it]]))
}))

cmp <- merge(live, src, by = "item")
cmp <- cmp[order(match(cmp$item, names(KEY))), ]
cmp$n_ok <- cmp$n == cmp$n_src
cmp$k_ok <- cmp$k == cmp$k_src
# a key flip on this item would produce this k instead:
cmp$k_if_flipped <- cmp$n_src - cmp$k_src
print(cmp, row.names = FALSE)

cat("\nitems compared:", nrow(cmp), "of", length(KEY), "\n")
cat("n matches: ", sum(cmp$n_ok), "/", nrow(cmp), "\n", sep = "")
cat("k matches: ", sum(cmp$k_ok), "/", nrow(cmp), "\n", sep = "")
cat("items where a key flip would be undetectable (k == n-k): ",
    sum(cmp$k_src == cmp$k_if_flipped), "\n", sep = "")

# Corroboration (route 8): the five statements whose text mentions "epigenetic"
# should be the five with the most don't-know/missing, i.e. the lowest n --
# the paper reports epigenetics items drew by far the most "Don't know".
EPI <- c("Q15","Q17","Q18","Q19","Q22")
lowest5 <- cmp$item[order(cmp$n)][1:5]
cat("five lowest-n items: ", paste(sort(lowest5), collapse = ","),
    " | five 'epigenetic' stems: ", paste(sort(EPI), collapse = ","), "\n", sep = "")
epi_ok <- setequal(lowest5, EPI)

ok <- all(cmp$n_ok) && all(cmp$k_ok) &&
      nrow(cmp) == length(KEY) && all(cmp$k_src != cmp$k_if_flipped) && epi_ok
cat(if (ok) "VERDICT: PASS" else "VERDICT: FAIL", "\n", sep = "")

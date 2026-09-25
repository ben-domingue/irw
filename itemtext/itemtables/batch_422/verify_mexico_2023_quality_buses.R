# verify_mexico_2023_quality_buses.R -- batch_422, route 9 (response-frequency matching).
#
# Claim: IRW item p5_9_k is INEGI microdata column P5_9_K, which the ENCIG 2023 questionnaire
# prints as question 5.9 option K (bus/van/combi/microbus characteristics), and p5_9a is P5_9A
# (question 5.9a, satisfaction). Resp coding per data/mexico_2023_quality.do: P5_9_1..8 recoded
# 1 (Si) -> 0 and 2 (No) -> 1, code 9 -> missing; P5_9A kept 1..6, 9 -> missing.
#
# The do-file appends the ENCIG 2021 file by variable name, with no wave column; ids 1..38966
# are 2023 and 38967..78896 are 2021. So the prediction is: live count(item, resp) =
# 2023 count + 2021 count of the same-named source column, cell for cell. The script also
# shows the count vectors differ between every pair of items, so a permutation of codes
# cannot pass -- and it prints the 2021 filter counts that show 2021's P5_9 is a DIFFERENT
# service (articulated BRT, 2021 question 5.9), which is the table's disclosed data defect.
#
# Fetches: INEGI microdata zips (CSV) for 2023 and 2021; live counts via a server-side
# aggregate query (no table export).

suppressMessages({ library(irw); library(data.table) })
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE <- "mexico_2023_quality_buses"
C <- ".cache/mexico_2023_quality_buses"
f23 <- cached_zip_members(
  file.path(C, c("encig2023_01_sec1_A_3_4_5_8_9_10.csv", "encig2023_02_residentes_sec_2.csv")),
  c("encig2023_01_sec1_A_3_4_5_8_9_10.csv", "encig2023_02_residentes_sec_2.csv"),
  "https://www.inegi.org.mx/contenidos/programas/encig/2023/microdatos/encig23_base_datos_csv.zip")
f21 <- cached_zip_members(
  file.path(C, c("encig2021_01_sec1_A_3_4_5_8_9_10.csv", "encig2021_02_residentes_sec_2.csv")),
  c("encig2021_01_sec1_A_3_4_5_8_9_10.csv", "encig2021_02_residentes_sec_2.csv"),
  "https://www.inegi.org.mx/contenidos/programas/encig/2021/microdatos/encig21_base_datos_csv.zip")

cols <- c(paste0("P5_9_", 1:8), "P5_9A")
load_wave <- function(f) {
  a <- fread(f[1], colClasses = "character"); setnames(a, toupper(names(a)))
  r <- fread(f[2], colClasses = "character"); setnames(r, toupper(names(r)))
  merge(r[, .(ID_PER)], a, by = "ID_PER")
}
w23 <- load_wave(f23); w21 <- load_wave(f21)
cat(sprintf("merged persons: 2023 = %d, 2021 = %d, total = %d\n", nrow(w23), nrow(w21), nrow(w23) + nrow(w21)))

src_counts <- function(m) {
  out <- list()
  for (v in cols) {
    x <- suppressWarnings(as.numeric(m[[v]]))
    x[x == 9] <- NA
    if (v != "P5_9A") x <- x - 1          # 1 -> 0 (Si), 2 -> 1 (No)
    tb <- table(x)
    out[[v]] <- data.frame(item = tolower(v), resp = as.numeric(names(tb)), n = as.integer(tb))
  }
  do.call(rbind, out)
}
s <- merge(src_counts(w23), src_counts(w21), by = c("item", "resp"), all = TRUE, suffixes = c("_23", "_21"))
s[is.na(s)] <- 0L
s$n_src <- s$n_23 + s$n_21

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
q <- function(x) as.data.frame(irw:::.irw_query_tibble(sprintf(x, ref)))
live <- q("SELECT CAST(item AS STRING) item, SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) resp, COUNT(*) n_live FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','') GROUP BY 1,2")
ids <- q("SELECT MIN(id) mn, MAX(id) mx, COUNT(DISTINCT id) n FROM `%s`")
cat(sprintf("live ids: %d..%d, %d distinct\n\n", ids$mn, ids$mx, ids$n))

cmp <- merge(s, live, by = c("item", "resp"), all = TRUE)
cmp[is.na(cmp)] <- 0L
cmp <- cmp[order(cmp$item, cmp$resp), ]
print(cmp, row.names = FALSE)
cells_ok <- all(cmp$n_src == cmp$n_live)
cat(sprintf("\ncells compared: %d, exact matches: %d\n", nrow(cmp), sum(cmp$n_src == cmp$n_live)))

# Does the route distinguish every item from every other? Match each live item's count
# vector against every source column's; a correct and unique tie = exactly one match, the namesake.
key <- function(d, col) sapply(split(d, d$item), function(z) paste(z$resp, z[[col]], collapse = ";"))
ks <- key(cmp, "n_src"); kl <- key(cmp, "n_live")
hits <- sapply(names(kl), function(i) paste(names(ks)[ks == kl[[i]]], collapse = ","))
print(data.frame(live_item = names(kl), matching_source_column = hits), row.names = FALSE)
unique_ok <- all(hits == names(kl)) && length(unique(ks)) == length(ks)

# The disclosed defect: 2021 P5_9 is articulated BRT. Its respondents are the 2021 filter
# P5_1_8 users (2021 question 5.1 item 08), not the 2021 bus users (P5_1_7 -> P5_8_*).
f8 <- sum(w21$P5_1_8 == "1", na.rm = TRUE); f7 <- sum(w21$P5_1_7 == "1", na.rm = TRUE)
n21_p591 <- sum(!is.na(w21$P5_9_1) & w21$P5_9_1 != "")
n21_p581 <- sum(!is.na(w21$P5_8_1) & w21$P5_8_1 != "")
cat(sprintf("\n2021: P5_9_1 answered by %d persons = P5_1_8 (articulated BRT) users %d; 2021 bus users P5_1_7 = %d answered P5_8_1 (%d), which the IRW table does not include.\n",
            n21_p591, f8, f7, n21_p581))
cat("Not established by this route: the tie of column P5_9_K to questionnaire option K is the\n",
    "questionnaire's own printed numbering (INEGI naming convention), not a statistical inference.\n", sep = "")

cat(if (cells_ok && unique_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

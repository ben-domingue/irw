# verify_mexico_2023_quality_trains.R -- batch_428, route 9 (response-frequency matching), per wave.
#
# Claim: IRW item p5_12_k is INEGI ENCIG 2023 microdata column P5_12_K, printed in the 2023
# questionnaire (p.11) as question 5.12 option K (metro or light rail, "el metro o tren ligero"),
# and p5_12a is P5_12A (question 5.12a, satisfaction). Since the #2415 rebuild
# (data/mexico_2023_quality.py) the 2021 rows (cov_year = 2021) come from ENCIG 2021 column
# P5_10_K / P5_10A -- 2021 question 5.10 (p.9), the same metro/light-rail question under INEGI's
# earlier numbering (2023 inserted 5.7 IMSS-Bienestar and 5.11 Cablebus) -- renamed onto the 2023
# name (RENAME_2021) before stacking. 2021 has no 5.12/5.13.
#
# Resp coding per data/mexico_2023_quality.py: yes/no items 1 (Si) -> 0, 2 (No) -> 1;
# codes 9/98/99 -> missing; P5_12A kept 1..6.
#
# Prediction: for each wave separately, live count(item, resp | cov_year) equals the count of
# the mapped source column, cell for cell; and each live item's count vector matches exactly
# one column among ALL section-V columns of that wave (P5_*), namely its mapped one, so a
# permutation of the five yes/no codes, a flipped Si/No direction, or a mis-mapped 2021 rename
# (e.g. onto 2021 5.11 toll highways, or 2023's same-named-but-different 2021 column) fails.
# Corroboration: every 5.12 (2023) / 5.10 (2021) answerer reported metro/light-rail use in 5.1
# (2023 option 11 P5_1_11, 2021 option 09 P5_1_9).
#
# Fetches: INEGI microdata zips (CSV) for 2023 and 2021; live counts via a server-side
# aggregate query (no table export).

suppressMessages({ library(irw); library(data.table) })
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE <- "mexico_2023_quality_trains"
C <- ".cache/mexico_2023_quality_trains"
f23 <- cached_zip_members(
  file.path(C, c("encig2023_01_sec1_A_3_4_5_8_9_10.csv", "encig2023_02_residentes_sec_2.csv")),
  c("encig2023_01_sec1_A_3_4_5_8_9_10.csv", "encig2023_02_residentes_sec_2.csv"),
  "https://www.inegi.org.mx/contenidos/programas/encig/2023/microdatos/encig23_base_datos_csv.zip")
f21 <- cached_zip_members(
  file.path(C, c("encig2021_01_sec1_A_3_4_5_8_9_10.csv", "encig2021_02_residentes_sec_2.csv")),
  c("encig2021_01_sec1_A_3_4_5_8_9_10.csv", "encig2021_02_residentes_sec_2.csv"),
  "https://www.inegi.org.mx/contenidos/programas/encig/2021/microdatos/encig21_base_datos_csv.zip")

load_wave <- function(f) {
  a <- fread(f[1], colClasses = "character"); setnames(a, toupper(names(a)))
  r <- fread(f[2], colClasses = "character"); setnames(r, toupper(names(r)))
  merge(r[, .(ID_PER)], a, by = "ID_PER")
}
w23 <- load_wave(f23); w21 <- load_wave(f21)
cat(sprintf("merged persons: 2023 = %d, 2021 = %d\n", nrow(w23), nrow(w21)))

items <- c(paste0("p5_12_", 1:5), "p5_12a")
recode <- function(m, v) {
  x <- suppressWarnings(as.numeric(m[[v]]))
  x[x %in% c(9, 98, 99)] <- NA
  if (!grepl("[AB]$", v)) x <- x - 1          # yes/no: 1 -> 0 (Si), 2 -> 1 (No)
  x
}
counts <- function(m, srccols, year) {
  do.call(rbind, lapply(srccols, function(v) {
    tb <- table(recode(m, v))
    if (!length(tb)) return(NULL)
    data.frame(src = v, year = year, resp = as.numeric(names(tb)), n = as.integer(tb), row.names = NULL)
  }))
}
map23 <- setNames(c(paste0("P5_12_", 1:5), "P5_12A"), items)
map21 <- setNames(c(paste0("P5_10_", 1:5), "P5_10A"), items)     # #2415 harmonised mapping
# candidate pool: every section-V column of the wave (excluding the 0-10 grade columns *B)
pool <- function(m) grep("^P5_[0-9]+(_[0-9]+|A)$", names(m), value = TRUE)
s23 <- counts(w23, pool(w23), 2023); s21 <- counts(w21, pool(w21), 2021)
cat(sprintf("candidate source columns: 2023 = %d, 2021 = %d\n", length(unique(s23$src)), length(unique(s21$src))))

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
q <- function(x) as.data.frame(irw:::.irw_query_tibble(sprintf(x, ref)))
live <- q("SELECT CAST(item AS STRING) item, CAST(cov_year AS INT64) year, SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) resp, COUNT(*) n_live FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','') GROUP BY 1,2,3")
ids <- q("SELECT CAST(cov_year AS INT64) year, MIN(id) mn, MAX(id) mx, COUNT(DISTINCT id) n, COUNT(*) nrow FROM `%s` GROUP BY 1 ORDER BY 1")
print(ids, row.names = FALSE)

key <- function(d, col, by) sapply(split(d, d[[by]]), function(z) { z <- z[order(z$resp), ]; paste(z$resp, z[[col]], sep = ":", collapse = ";") })
ok_all <- nrow(ids) == 2 && setequal(ids$year, c(2021, 2023))
for (yr in c(2023, 2021)) {
  src <- if (yr == 2023) s23 else s21
  mp <- if (yr == 2023) map23 else map21
  lv <- live[live$year == yr, ]
  ks <- key(src, "n", "src"); kl <- key(lv, "n_live", "item")
  cat(sprintf("\n== cov_year %d ==\n", yr))
  cat(sprintf("%-8s %-8s %-40s %-40s %s\n", "item", "source", "source resp:n", "live resp:n", "pool columns matching live vector"))
  for (it in items) {
    hits <- names(ks)[ks == kl[[it]]]
    good <- identical(hits, mp[[it]])
    ok_all <- ok_all && good
    cat(sprintf("%-8s %-8s %-40s %-40s %s%s\n", it, mp[[it]], ks[[mp[[it]]]], kl[[it]],
                paste(hits, collapse = ","), if (good) "" else "  <-- MISMATCH"))
  }
  if (length(unique(ks[mp])) != length(mp)) { ok_all <- FALSE; cat("mapped source vectors not all distinct\n") }
}

# Block corroboration: the 5.1 filter question (metro / light-rail user)
f23u <- w23[!is.na(recode(w23, "P5_12_1")) | !is.na(recode(w23, "P5_12A"))]
f21u <- w21[!is.na(recode(w21, "P5_10_1")) | !is.na(recode(w21, "P5_10A"))]
cat(sprintf("\n2023 5.12 answerers: %d; of these P5_1_11 == 1: %d\n", nrow(f23u), sum(f23u$P5_1_11 == "1")))
cat(sprintf("2021 5.10 answerers: %d; of these P5_1_9 == 1: %d\n", nrow(f21u), sum(f21u$P5_1_9 == "1")))
ok_all <- ok_all && all(f23u$P5_1_11 == "1") && all(f21u$P5_1_9 == "1")

cat("Not established by this route: that column P5_12_K (2023) / P5_10_K (2021) is questionnaire option K --\n",
    "that is the questionnaires' own printed numbering (INEGI's naming convention), not a statistical inference.\n", sep = "")
cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

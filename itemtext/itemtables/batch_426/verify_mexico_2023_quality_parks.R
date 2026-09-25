# verify_mexico_2023_quality_parks.R -- batch_426, route 9 (response-frequency matching), per wave.
#
# Claim: IRW item p4_4_k is INEGI ENCIG microdata column P4_4_K, printed in both the 2023 and the
# 2021 questionnaire (Seccion IV, p.5 of each PDF) as question 4.4 option K (parks and gardens,
# "los parques y jardines de esta ciudad"), and p4_4a is P4_4A (question 4.4a, satisfaction).
# Section IV was NOT renumbered between waves: RENAME_2021 in data/mexico_2023_quality.py has no
# p4_* entry and ASKED_2021 lists p4_4_1..4, p4_4a, so 2021 rows (cov_year = 2021) come from the
# same-named 2021 columns.
#
# Resp coding per data/mexico_2023_quality.py: yes/no items 1 (Si) -> 0, 2 (No) -> 1;
# codes 9/98/99 -> missing; P4_4A kept 1..6.
#
# Prediction: for each wave separately, live count(item, resp | cov_year) equals the count of the
# mapped source column, cell for cell; and each live item's count vector matches exactly one
# column among ALL section-IV rating columns of that wave (P4_*), namely its mapped one, so a
# permutation of the four yes/no codes, a flipped Si/No direction, or a mix-up with a
# neighbouring service block (4.3 street lighting, 4.5 trash, ...) fails.
#
# Fetches: INEGI microdata zips (CSV) for 2023 and 2021; live counts via a server-side
# aggregate query (no table export).

suppressMessages({ library(irw); library(data.table) })
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE <- "mexico_2023_quality_parks"
C <- ".cache/mexico_2023_quality_parks"
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

items <- c(paste0("p4_4_", 1:4), "p4_4a")
recode <- function(m, v) {
  x <- suppressWarnings(as.numeric(m[[v]]))
  if (!grepl("[AB]$", v)) x[x %in% c(1, 2)] <- x[x %in% c(1, 2)] - 1   # yes/no: 1 -> 0 (Si), 2 -> 1 (No)
  x[x %in% c(9, 98, 99)] <- NA
  x
}
counts <- function(m, srccols, year) {
  do.call(rbind, lapply(srccols, function(v) {
    tb <- table(recode(m, v))
    if (!length(tb)) return(NULL)
    data.frame(src = v, year = year, resp = as.numeric(names(tb)), n = as.integer(tb), row.names = NULL)
  }))
}
map23 <- setNames(c(paste0("P4_4_", 1:4), "P4_4A"), items)
map21 <- map23                                                     # section IV not renumbered
pool <- function(m) grep("^P4_[0-9]+(_[0-9]+|A)$", names(m), value = TRUE)   # excludes 0-10 grades *B
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
  cat(sprintf("%-8s %-8s %-44s %-44s %s\n", "item", "source", "source resp:n", "live resp:n", "pool columns matching live vector"))
  for (it in items) {
    hits <- names(ks)[ks == kl[[it]]]
    good <- identical(hits, mp[[it]])
    ok_all <- ok_all && good
    cat(sprintf("%-8s %-8s %-44s %-44s %s%s\n", it, mp[[it]], ks[[mp[[it]]]], kl[[it]],
                paste(hits, collapse = ","), if (good) "" else "  <-- MISMATCH"))
  }
  if (length(unique(ks[mp])) != length(mp)) { ok_all <- FALSE; cat("mapped source vectors not all distinct\n") }
}

cat("\nNot established by this route: that column P4_4_K is questionnaire option K of question 4.4 --\n",
    "that is the questionnaires' own printed numbering (INEGI's naming convention), not a statistical inference.\n", sep = "")
cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

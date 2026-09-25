# verify_mexico_2023_quality_electricgovernment.R -- batch_424, route 9 (response-frequency matching), per wave.
#
# Claim: IRW item p10_1_k is INEGI ENCIG microdata column P10_1_K, printed in the questionnaire as
# question 10.1 option K (Seccion X, Gobierno electronico). data/mexico_2023_quality.py melts these
# unrenamed (lowercased) in both waves: P10_1_1..6 are in ASKED_2021 and absent from RENAME_2021, and
# section X is numbered identically in the 2023 and 2021 cuestionarios.
#
# Resp coding per the .py: 1 (Si) -> 0, 2 (No) -> 1; codes 9/98/99 -> missing.
#
# Prediction: for each wave (cov_year) separately, live count(item, resp) equals the count of the
# namesake source column, cell for cell; and each live item's count vector matches exactly one source
# column (its namesake), with all six source vectors distinct, so any permutation of codes fails.
#
# Fetches: INEGI microdata zips (CSV) for 2023 and 2021; live counts via a server-side aggregate
# query (no table export).

suppressMessages({ library(irw); library(data.table) })
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE <- "mexico_2023_quality_electricgovernment"
C <- ".cache/mexico_2023_quality_electricgovernment"
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
  merge(r[, .(ID_PER)], a, by = "ID_PER")       # the .py's residentes x sec1 inner join
}
w23 <- load_wave(f23); w21 <- load_wave(f21)
cat(sprintf("merged persons: 2023 = %d, 2021 = %d\n", nrow(w23), nrow(w21)))

items <- paste0("p10_1_", 1:6)
srcmap <- setNames(paste0("P10_1_", 1:6), items)
counts <- function(m) {
  do.call(rbind, lapply(srcmap, function(v) {
    x <- suppressWarnings(as.numeric(m[[v]]))
    x[x %in% c(9, 98, 99)] <- NA
    x <- x - 1                                  # 1 -> 0 (Si), 2 -> 1 (No)
    tb <- table(x)
    data.frame(src = v, resp = as.numeric(names(tb)), n = as.integer(tb), row.names = NULL)
  }))
}
src <- list(`2023` = counts(w23), `2021` = counts(w21))

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
q <- function(x) as.data.frame(irw:::.irw_query_tibble(sprintf(x, ref)))
live <- q("SELECT CAST(item AS STRING) item, CAST(cov_year AS INT64) year, SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) resp, COUNT(*) n_live FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','') GROUP BY 1,2,3")
ids <- q("SELECT CAST(cov_year AS INT64) year, MIN(id) mn, MAX(id) mx, COUNT(DISTINCT id) n FROM `%s` GROUP BY 1 ORDER BY 1")
print(ids, row.names = FALSE)

key <- function(d, col, by) sapply(split(d, d[[by]]), function(z) { z <- z[order(z$resp), ]; paste(z$resp, z[[col]], sep = ":", collapse = ";") })
ok_all <- TRUE
for (yr in c("2023", "2021")) {
  ks <- key(src[[yr]], "n", "src"); kl <- key(live[live$year == as.integer(yr), ], "n_live", "item")
  cat(sprintf("\n== cov_year %s ==\n", yr))
  cat(sprintf("%-8s %-8s %-22s %-22s %s\n", "item", "source", "source resp:n", "live resp:n", "live vector matches"))
  for (it in items) {
    hits <- names(ks)[ks == kl[[it]]]
    good <- identical(hits, srcmap[[it]])
    ok_all <- ok_all && good
    cat(sprintf("%-8s %-8s %-22s %-22s %s%s\n", it, srcmap[[it]], ks[[srcmap[[it]]]], kl[[it]],
                paste(hits, collapse = ","), if (good) "" else "  <-- MISMATCH"))
  }
  if (length(unique(ks)) != length(ks)) { ok_all <- FALSE; cat("source vectors not all distinct\n") }
  sh <- sapply(items, function(it) { z <- src[[yr]][src[[yr]]$src == srcmap[[it]], ]; z$n[z$resp == 0] / sum(z$n) })
  cat("Si share by item: ", paste(sprintf("%s=%.3f", items, sh), collapse = " "), "\n")
}
cat("Not established by this route: that column P10_1_K is questionnaire option K of 10.1 --\n",
    "that is the cuestionario's own printed numbering (INEGI's naming convention), not a statistical inference.\n", sep = "")
cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

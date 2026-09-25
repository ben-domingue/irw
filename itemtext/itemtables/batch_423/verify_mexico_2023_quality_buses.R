# verify_mexico_2023_quality_buses.R -- batch_423, route 9 (response-frequency matching), per wave.
#
# Claim: IRW item p5_9_k is INEGI ENCIG 2023 microdata column P5_9_K, printed in the 2023
# questionnaire as question 5.9 option K (urban bus/van/combi/microbus), and p5_9a is P5_9A
# (question 5.9a, satisfaction). Since the #2415 rebuild (data/mexico_2023_quality.py) the
# 2021 rows (cov_year = 2021) come from ENCIG 2021 column P5_8_K / P5_8A -- 2021 question 5.8,
# the same bus question under INEGI's earlier numbering -- renamed onto the 2023 name
# (RENAME_2021 in the .py) before stacking.
#
# Resp coding per data/mexico_2023_quality.py: yes/no items 1 (Si) -> 0, 2 (No) -> 1;
# codes 9/98/99 -> missing; P5_9A kept 1..6.
#
# Prediction: for each wave separately, live count(item, resp | cov_year) equals the
# count of the mapped source column, cell for cell; and each live item's count vector
# matches exactly one source column (its mapped one), so a permutation of codes fails.
# The script also shows the pre-#2415 pooling (2021 P5_9_*, articulated BRT) does NOT
# reproduce the live 2021 rows, i.e. the batch_422 defect is gone.
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

load_wave <- function(f) {
  a <- fread(f[1], colClasses = "character"); setnames(a, toupper(names(a)))
  r <- fread(f[2], colClasses = "character"); setnames(r, toupper(names(r)))
  merge(r[, .(ID_PER)], a, by = "ID_PER")
}
w23 <- load_wave(f23); w21 <- load_wave(f21)
cat(sprintf("merged persons: 2023 = %d, 2021 = %d\n", nrow(w23), nrow(w21)))

items <- c(paste0("p5_9_", 1:8), "p5_9a")
counts <- function(m, srccols, year) {
  out <- list()
  for (j in seq_along(srccols)) {
    v <- srccols[j]
    x <- suppressWarnings(as.numeric(m[[v]]))
    x[x %in% c(9, 98, 99)] <- NA
    if (!grepl("A$", v)) x <- x - 1          # 1 -> 0 (Si), 2 -> 1 (No)
    tb <- table(x)
    out[[v]] <- data.frame(src = v, year = year, resp = as.numeric(names(tb)), n = as.integer(tb), row.names = NULL)
  }
  do.call(rbind, out)
}
map23 <- setNames(c(paste0("P5_9_", 1:8), "P5_9A"), items)
map21 <- setNames(c(paste0("P5_8_", 1:8), "P5_8A"), items)     # #2415 harmonised mapping
old21 <- setNames(c(paste0("P5_9_", 1:8), "P5_9A"), items)     # pre-#2415 by-name append (BRT)
s23 <- counts(w23, map23, 2023); s21 <- counts(w21, map21, 2021); o21 <- counts(w21, old21, 2021)

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
q <- function(x) as.data.frame(irw:::.irw_query_tibble(sprintf(x, ref)))
live <- q("SELECT CAST(item AS STRING) item, CAST(cov_year AS INT64) year, SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) resp, COUNT(*) n_live FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','') GROUP BY 1,2,3")
ids <- q("SELECT CAST(cov_year AS INT64) year, MIN(id) mn, MAX(id) mx, COUNT(DISTINCT id) n FROM `%s` GROUP BY 1 ORDER BY 1")
print(ids, row.names = FALSE)

# key: "resp:n;..." per (year, item/src)
key <- function(d, col, by) sapply(split(d, d[[by]]), function(z) { z <- z[order(z$resp), ]; paste(z$resp, z[[col]], sep = ":", collapse = ";") })
ok_all <- TRUE
for (yr in c(2023, 2021)) {
  src <- if (yr == 2023) s23 else s21
  mp <- if (yr == 2023) map23 else map21
  lv <- live[live$year == yr, ]
  ks <- key(src, "n", "src"); kl <- key(lv, "n_live", "item")
  cat(sprintf("\n== cov_year %d ==\n", yr))
  cat(sprintf("%-7s %-7s %-45s %-45s %s\n", "item", "source", "source resp:n", "live resp:n", "live vector matches"))
  for (it in items) {
    hits <- names(ks)[ks == kl[[it]]]
    good <- identical(hits, mp[[it]])
    ok_all <- ok_all && good
    cat(sprintf("%-7s %-7s %-45s %-45s %s%s\n", it, mp[[it]], ks[[mp[[it]]]], kl[[it]],
                paste(hits, collapse = ","), if (good) "" else "  <-- MISMATCH"))
  }
  if (length(unique(ks)) != length(ks)) { ok_all <- FALSE; cat("source vectors not all distinct\n") }
}

# The pre-#2415 defect: 2021 P5_9_* (articulated BRT) would have been pooled under these codes.
ko <- key(o21, "n", "src"); kl21 <- key(live[live$year == 2021, ], "n_live", "item")
old_hits <- sum(sapply(items, function(it) ko[[old21[[it]]]] == kl21[[it]]))
cat(sprintf("\npre-#2415 mapping (2021 P5_9_*, articulated BRT): %d of 9 live 2021 items match it (expect 0).\n", old_hits))
cat(sprintf("e.g. 2021 P5_9_1 (BRT) %s vs live 2021 p5_9_1 %s\n", ko[["P5_9_1"]], kl21[["p5_9_1"]]))
ok_all <- ok_all && old_hits == 0

cat("Not established by this route: that column P5_9_K (2023) / P5_8_K (2021) is questionnaire option K --\n",
    "that is the questionnaires' own printed numbering (INEGI's naming convention), not a statistical inference.\n", sep = "")
cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

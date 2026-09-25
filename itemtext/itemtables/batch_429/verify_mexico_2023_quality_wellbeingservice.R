# verify_mexico_2023_quality_wellbeingservice.R -- batch_429, route 9 (response-frequency matching).
#
# Claim: IRW item p5_7_KK is INEGI ENCIG 2023 microdata column P5_7_KK, printed in the 2023
# questionnaire (p.9) as question 5.7 option KK (health service of IMSS-Bienestar, antes
# IMSS-Prospera), and p5_7a is P5_7A (question 5.7a, satisfaction). The question exists only in
# ENCIG 2023 (2021's 5.7 is home electricity, routed to p5_8_* by RENAME_2021), so the table
# must carry NO cov_year = 2021 rows.
#
# Resp coding per data/mexico_2023_quality.py: yes/no items 1 (Si) -> 0, 2 (No) -> 1;
# codes 9/98/99 -> missing; P5_7A kept 1..6.
#
# Prediction: (a) live rows are all cov_year 2023, ids within the 2023 block (1..38966);
# (b) live count(item, resp) equals the count of the mapped 2023 source column, cell for cell;
# (c) each live item's count vector matches exactly one column among ALL section-V rating
# columns of 2023 (P5_2..P5_13, incl. the word-identical 5.4 IMSS / 5.5 ISSSTE / 5.6 State-INSABI
# health blocks), namely its mapped one -- so a permutation of options or the wrong provider block
# fails. Corroboration: every 5.7 answerer reported IMSS-Bienestar use in 5.1 option 06
# (P5_1_06 = 1), the printed filter "APLICA 5.7 Y 5.7a".
#
# Fetches: INEGI 2023 microdata zip (CSV); live counts via a server-side aggregate query (no export).

suppressMessages({ library(irw); library(data.table) })
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE <- "mexico_2023_quality_wellbeingservice"
C <- ".cache/mexico_2023_quality_health"   # shared ENCIG microdata cache (batch_424)
f23 <- cached_zip_members(
  file.path(C, c("encig2023_01_sec1_A_3_4_5_8_9_10.csv", "encig2023_02_residentes_sec_2.csv")),
  c("encig2023_01_sec1_A_3_4_5_8_9_10.csv", "encig2023_02_residentes_sec_2.csv"),
  "https://www.inegi.org.mx/contenidos/programas/encig/2023/microdatos/encig23_base_datos_csv.zip")

a <- fread(f23[1], colClasses = "character"); setnames(a, toupper(names(a)))
r <- fread(f23[2], colClasses = "character"); setnames(r, toupper(names(r)))
w23 <- merge(r[, .(ID_PER)], a, by = "ID_PER")
cat(sprintf("merged persons 2023 = %d\n", nrow(w23)))

items <- c(sprintf("p5_7_%02d", 1:11), "p5_7a")
map23 <- setNames(c(sprintf("P5_7_%02d", 1:11), "P5_7A"), items)
pool <- grep("^P5_([2-9]|1[0-3])(_[0-9]+|A)$", names(w23), value = TRUE)
cat(sprintf("candidate pool: %d section-V rating columns (5.2..5.13)\n", length(pool)))
src <- do.call(rbind, lapply(pool, function(v) {
  x <- suppressWarnings(as.numeric(w23[[v]]))
  x[x %in% c(9, 98, 99)] <- NA
  if (!grepl("A$", v)) x <- x - 1
  tb <- table(x)
  data.frame(src = v, resp = as.numeric(names(tb)), n = as.integer(tb))
}))

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
q <- function(x) as.data.frame(irw:::.irw_query_tibble(sprintf(x, ref)))
yrs <- q("SELECT CAST(cov_year AS INT64) year, MIN(id) mn, MAX(id) mx, COUNT(DISTINCT id) n_id, COUNT(*) n_rows FROM `%s` GROUP BY 1 ORDER BY 1")
cat("\nlive rows by cov_year:\n"); print(yrs, row.names = FALSE)
ok_all <- nrow(yrs) == 1 && isTRUE(yrs$year == 2023) && yrs$mx <= 38966
cat(sprintf("2023-only (no cov_year 2021 rows, ids <= 38966): %s\n", ok_all))

live <- q("SELECT CAST(item AS STRING) item, SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) resp, COUNT(*) n_live FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','') GROUP BY 1,2")

key <- function(d, col, by) sapply(split(d, d[[by]]), function(z) { z <- z[order(z$resp), ]; paste(z$resp, z[[col]], sep = ":", collapse = ";") })
ks <- key(src, "n", "src"); kl <- key(live, "n_live", "item")
cat(sprintf("\n%-8s %-8s %-36s %-36s %s\n", "item", "source", "source resp:n", "live resp:n", "pool columns matching live vector"))
for (it in items) {
  lk <- if (it %in% names(kl)) kl[[it]] else "<absent>"
  hits <- names(ks)[ks == lk]
  good <- identical(hits, map23[[it]])
  ok_all <- ok_all && good
  cat(sprintf("%-8s %-8s %-36s %-36s %s%s\n", it, map23[[it]], ks[[map23[[it]]]], lk,
              paste(hits, collapse = ","), if (good) "" else "  <-- MISMATCH"))
}
if (length(unique(ks[map23])) != length(map23)) { ok_all <- FALSE; cat("mapped source vectors not all distinct\n") }

# Block corroboration: 5.7 is asked only of IMSS-Bienestar users (5.1 option 06).
ans <- rowSums(sapply(grep("^P5_7_", names(w23), value = TRUE), function(v) w23[[v]] %in% c("1", "2", "9"))) > 0
fl <- w23[["P5_1_06"]] == "1"
cat(sprintf("\n5.7 answerers %d; with 5.1 option 06 (IMSS-Bienestar) = 1: %d; option-06 users %d\n",
            sum(ans), sum(ans & fl), sum(fl)))
ok_all <- ok_all && sum(ans) == sum(ans & fl)

cat("Not established by this route: that column P5_7_KK is questionnaire option KK of 5.7 --\n",
    "that is the questionnaire's own printed numbering (01..11), not a statistical inference.\n", sep = "")
cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

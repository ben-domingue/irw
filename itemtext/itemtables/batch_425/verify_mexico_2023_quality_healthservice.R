# verify_mexico_2023_quality_healthservice.R -- batch_425, route 9 (response-frequency matching), per wave.
#
# Claim: IRW item p5_6_KK is INEGI ENCIG 2023 microdata column P5_6_KK, printed in the 2023
# questionnaire (p.9) as question 5.6 option KK (health service of the State government or
# INSABI, antes seguro popular), and p5_6a is P5_6A (question 5.6a, satisfaction). The 2021 rows
# (cov_year = 2021) come from ENCIG 2021 column P5_6_K (unpadded, K = 1..9; renamed onto P5_6_0K
# by RENAME_2021 in data/mexico_2023_quality.py) and P5_6_10, P5_6_11, P5_6A (same name, listed
# in ASKED_2021) -- 2021 question 5.6 (p.8), the same question under the same number.
#
# Resp coding per data/mexico_2023_quality.py: yes/no items 1 (Si) -> 0, 2 (No) -> 1;
# codes 9/98/99 -> missing; P5_6A kept 1..6.
#
# Prediction: for each wave separately, live count(item, resp | cov_year) equals the count of
# the mapped source column, cell for cell; and each live item's count vector matches exactly one
# column in the candidate pool of ALL section-V health questions (5.4 IMSS, 5.5 ISSSTE, 5.6
# State/INSABI, and 2023's 5.7 IMSS-Bienestar), namely its mapped one -- so a permutation of
# options, a shifted 2021 rename, or the wrong provider block (5.4/5.5/5.7 share 5.6's wording)
# fails. Corroboration: every 5.6 answerer reported State/INSABI use in 5.1 option 05
# (2023 P5_1_05 / 2021 P5_1_5 = 1), the printed filter "APLICA 5.6 Y 5.6a".
#
# Fetches: INEGI microdata zips (CSV) for 2023 and 2021; live counts via a server-side
# aggregate query (no table export).

suppressMessages({ library(irw); library(data.table) })
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE <- "mexico_2023_quality_healthservice"
C <- ".cache/mexico_2023_quality_health"   # shared ENCIG microdata cache (batch_424)
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

items <- c(sprintf("p5_6_%02d", 1:11), "p5_6a")
counts <- function(m, srccols, year) {
  out <- list()
  for (v in srccols) {
    x <- suppressWarnings(as.numeric(m[[v]]))
    x[x %in% c(9, 98, 99)] <- NA
    if (!grepl("A$", v)) x <- x - 1          # 1 -> 0 (Si), 2 -> 1 (No)
    tb <- table(x)
    out[[v]] <- data.frame(src = v, year = year, resp = as.numeric(names(tb)), n = as.integer(tb), row.names = NULL)
  }
  do.call(rbind, out)
}
map23 <- setNames(c(sprintf("P5_6_%02d", 1:11), "P5_6A"), items)
map21 <- setNames(c(paste0("P5_6_", 1:11), "P5_6A"), items)     # RENAME_2021 (1..9) + same-name (10, 11, A)
pool <- function(m) grep("^P5_[4-7](_[0-9]+|A)$", names(m), value = TRUE)   # every health-block column
s23 <- counts(w23, pool(w23), 2023); s21 <- counts(w21, pool(w21), 2021)
cat(sprintf("candidate pool: 2023 %d columns, 2021 %d columns\n", length(pool(w23)), length(pool(w21))))

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
q <- function(x) as.data.frame(irw:::.irw_query_tibble(sprintf(x, ref)))
live <- q("SELECT CAST(item AS STRING) item, CAST(cov_year AS INT64) year, SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) resp, COUNT(*) n_live FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','') GROUP BY 1,2,3")
ids <- q("SELECT CAST(cov_year AS INT64) year, MIN(id) mn, MAX(id) mx, COUNT(DISTINCT id) n FROM `%s` GROUP BY 1 ORDER BY 1")
print(ids, row.names = FALSE)

key <- function(d, col, by) sapply(split(d, d[[by]]), function(z) { z <- z[order(z$resp), ]; paste(z$resp, z[[col]], sep = ":", collapse = ";") })
ok_all <- TRUE
for (yr in c(2023, 2021)) {
  src <- if (yr == 2023) s23 else s21
  mp <- if (yr == 2023) map23 else map21
  lv <- live[live$year == yr, ]
  ks <- key(src, "n", "src"); kl <- key(lv, "n_live", "item")
  cat(sprintf("\n== cov_year %d ==\n", yr))
  cat(sprintf("%-8s %-8s %-42s %-42s %s\n", "item", "source", "source resp:n", "live resp:n", "pool columns matching live vector"))
  for (it in items) {
    lk <- if (it %in% names(kl)) kl[[it]] else "<absent>"
    hits <- names(ks)[ks == lk]
    good <- identical(hits, mp[[it]])
    ok_all <- ok_all && good
    cat(sprintf("%-8s %-8s %-42s %-42s %s%s\n", it, mp[[it]], ks[[mp[[it]]]], lk,
                paste(hits, collapse = ","), if (good) "" else "  <-- MISMATCH"))
  }
  if (length(unique(ks[mp])) != length(mp)) { ok_all <- FALSE; cat("mapped source vectors not all distinct\n") }
}

# Block corroboration: 5.6 is asked only of State/INSABI health users (5.1 option 05).
filt <- function(m, flag) {
  ans <- rowSums(sapply(grep("^P5_6_", names(m), value = TRUE), function(v) m[[v]] %in% c("1", "2", "9"))) > 0
  c(answerers = sum(ans), with_flag = sum(ans & m[[flag]] == "1"), flag_users = sum(m[[flag]] == "1"))
}
f23c <- filt(w23, "P5_1_05"); f21c <- filt(w21, "P5_1_5")
cat(sprintf("\n5.6 answerers with 5.1 option 05 (State/INSABI) = 1: 2023 %d/%d (flag users %d), 2021 %d/%d (flag users %d)\n",
            f23c[2], f23c[1], f23c[3], f21c[2], f21c[1], f21c[3]))
ok_all <- ok_all && f23c[1] == f23c[2] && f21c[1] == f21c[2]

cat("Not established by this route: that column P5_6_KK is questionnaire option KK of 5.6 --\n",
    "that is the questionnaires' own printed numbering (01..11 in both waves), not a statistical inference.\n", sep = "")
cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

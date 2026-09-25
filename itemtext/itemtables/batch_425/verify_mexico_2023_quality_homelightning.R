# verify_mexico_2023_quality_homelightning.R -- batch_425, route 9 (response-frequency matching), per wave.
#
# Claim: IRW item p5_8_K (K = 1..3) is INEGI ENCIG 2023 microdata column P5_8_K, printed in the 2023
# questionnaire as question 5.8 option K (the electricity service -- "servicio de luz" -- received in the
# dwelling), and p5_8a is P5_8A (question 5.8a, satisfaction). The 2021 rows (cov_year = 2021) come from
# ENCIG 2021 columns P5_7_1..3 and P5_7A, which RENAME_2021 in data/mexico_2023_quality.py maps onto
# p5_8_* -- 2021 printed the same electricity question as 5.7/5.7a (2021 has no IMSS-Bienestar block,
# so every later 5.x question sits one number lower). 2021's own P5_8_* is the bus question and is
# renamed away to p5_9_*.
#
# Resp coding per data/mexico_2023_quality.py: yes/no items 1 (Si) -> 0, 2 (No) -> 1;
# codes 9/98/99 -> missing; P5_8A kept 1..6.
#
# Prediction: for each wave separately, live count(item, resp | cov_year) equals the count of the
# mapped source column, cell for cell; and each live item's count vector matches exactly one column
# among ALL section-V P5_* columns of that wave (its mapped one) -- so a permutation of the three
# yes/no codes, a missing 2021 rename (P5_8_* = buses), or a flipped Si/No direction fails.
# Corroboration: every 5.8 (2021: 5.7) answerer reported electricity-service use in 5.1
# (2023 option 07 = P5_1_07; 2021 option 06 = P5_1_6), the printed filter "APLICA 5.8 Y 5.8a".
#
# Fetches: INEGI microdata zips (CSV) for 2023 and 2021; live counts via a server-side
# aggregate query (no table export).

suppressMessages({ library(irw); library(data.table) })
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE <- "mexico_2023_quality_homelightning"
C <- ".cache/mexico_2023_quality_homelightning"
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

items <- c("p5_8_1", "p5_8_2", "p5_8_3", "p5_8a")
map23 <- setNames(c("P5_8_1", "P5_8_2", "P5_8_3", "P5_8A"), items)
map21 <- setNames(c("P5_7_1", "P5_7_2", "P5_7_3", "P5_7A"), items)     # RENAME_2021

# recode every section-V rating column the way the .py does, so a live vector can be tested
# against all of them (not just the mapped one)
vec <- function(m, v) {
  x <- suppressWarnings(as.numeric(m[[v]]))
  x[x %in% c(9, 98, 99)] <- NA
  if (!grepl("A$", v)) x <- x - 1          # yes/no: 1 -> 0 (Si), 2 -> 1 (No)
  tb <- table(x)
  if (!length(tb)) return(NA_character_)
  paste(names(tb), as.integer(tb), sep = ":", collapse = ";")
}
cands <- function(m) { cc <- grep("^P5_([2-9]|1[0-3])_[0-9]+$|^P5_([2-9]|1[0-3])A$", names(m), value = TRUE)
                        setNames(sapply(cc, function(v) vec(m, v)), cc) }
k23 <- cands(w23); k21 <- cands(w21)
cat(sprintf("candidate section-V columns: 2023 = %d, 2021 = %d\n", length(k23), length(k21)))

tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
q <- function(x) as.data.frame(irw:::.irw_query_tibble(sprintf(x, ref)))
live <- q("SELECT CAST(item AS STRING) item, CAST(cov_year AS INT64) year, SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) resp, COUNT(*) n_live FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','') GROUP BY 1,2,3")
ids <- q("SELECT CAST(cov_year AS INT64) year, MIN(id) mn, MAX(id) mx, COUNT(DISTINCT id) n FROM `%s` GROUP BY 1 ORDER BY 1")
print(ids, row.names = FALSE)

key_live <- function(lv) sapply(split(lv, lv$item), function(z) { z <- z[order(z$resp), ]
  paste(z$resp, z$n_live, sep = ":", collapse = ";") })

ok_all <- TRUE
for (yr in c(2023, 2021)) {
  ks <- if (yr == 2023) k23 else k21
  mp <- if (yr == 2023) map23 else map21
  kl <- key_live(live[live$year == yr, ])
  cat(sprintf("\n== cov_year %d ==\n", yr))
  cat(sprintf("%-7s %-7s %-45s %-45s %s\n", "item", "source", "source resp:n", "live resp:n", "columns matching live vector"))
  for (it in items) {
    lk <- if (it %in% names(kl)) kl[[it]] else "<absent>"
    hits <- names(ks)[!is.na(ks) & ks == lk]
    good <- identical(hits, mp[[it]])
    ok_all <- ok_all && good
    cat(sprintf("%-7s %-7s %-45s %-45s %s%s\n", it, mp[[it]], ks[[mp[[it]]]], lk,
                paste(hits, collapse = ","), if (good) "" else "  <-- MISMATCH"))
  }
  if (length(unique(ks[mp])) != length(mp)) { ok_all <- FALSE; cat("mapped source vectors not all distinct\n") }
}

# Negative control: 2021's own P5_8_* is the bus question; it must NOT reproduce live 2021 p5_8_*.
kl21 <- key_live(live[live$year == 2021, ])
neg <- sapply(1:3, function(k) identical(k21[[paste0("P5_8_", k)]], kl21[[paste0("p5_8_", k)]]))
cat(sprintf("\nnegative control (2021 P5_8_K = buses reproduces live 2021 p5_8_K): %s\n", paste(neg, collapse = ",")))
ok_all <- ok_all && !any(neg)

# Block corroboration: 5.8 (2021: 5.7) is asked only of electricity-service users (5.1 option 07 / 06).
filt <- function(m, cols, flag) {
  ans <- rowSums(sapply(cols, function(v) m[[v]] %in% c("1", "2", "9"))) > 0
  c(answerers = sum(ans), with_flag = sum(ans & m[[flag]] == "1"))
}
f23c <- filt(w23, map23[1:3], "P5_1_07"); f21c <- filt(w21, map21[1:3], "P5_1_6")
cat(sprintf("5.8/5.7 answerers with 5.1 electricity = 1: 2023 %d/%d, 2021 %d/%d\n",
            f23c[2], f23c[1], f21c[2], f21c[1]))
ok_all <- ok_all && f23c[1] == f23c[2] && f21c[1] == f21c[2]

cat("Not established by this route: that column P5_8_K (2021 P5_7_K) is questionnaire option K --\n",
    "that is the questionnaires' own printed numbering (1..3 under 5.8 in 2023, under 5.7 in 2021), not a statistical inference.\n", sep = "")
cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

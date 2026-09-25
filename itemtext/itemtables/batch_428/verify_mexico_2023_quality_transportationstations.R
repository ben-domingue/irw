# verify_mexico_2023_quality_transportationstations.R -- batch_428, route 9 (response-frequency
# matching), per wave, plus a routing check.
#
# Claim: IRW item p5_10_k is INEGI ENCIG 2023 microdata column P5_10_K, printed in the 2023
# questionnaire (Seccion V) as question 5.10 option K (articulated public transport with stations and
# an exclusive lane, "(TRANSPORTE)" -- BRT/Metrobus-type), and p5_10a is P5_10A (question 5.10a,
# satisfaction). Section V was renumbered in 2023 from 5.7 on (IMSS-Bienestar inserted as 5.7), so
# the same question is 5.9/5.9a in ENCIG 2021: RENAME_2021 in data/mexico_2023_quality.py maps
# 2021 p5_9_k -> p5_10_k and p5_9a -> p5_10a (and 2021 p5_10_* -> p5_12_*, metro), so the 2021
# rows (cov_year = 2021) must come from 2021 columns P5_9_K / P5_9A -- NOT the same-named 2021
# P5_10_* (metro / light rail).
#
# Resp coding per data/mexico_2023_quality.py: yes/no items 1 (Si) -> 0, 2 (No) -> 1;
# codes 9/98/99 -> missing; P5_10A kept 1..6.
#
# Predictions:
#  (a) for each wave separately, live count(item, resp | cov_year) equals the count of the mapped
#      source column, cell for cell; and each live item's count vector matches exactly one column
#      among ALL section-V rating columns of that wave (P5_*, excl. the 0-10 grades *B), namely its
#      mapped one -- so a permutation of the eight yes/no codes, a flipped Si/No direction, or a
#      mix-up with a neighbouring block (5.9 buses, which prints the SAME eight item wordings; 5.11
#      cablecar; 5.12 metro; or the un-renamed 2021 P5_10_* metro block) fails.
#  (b) routing: screener 5.1 option "fue usuario(a) de transporte publico que cuenta con estaciones
#      fijas y un carril exclusivo para su uso como (TRANSPORTE)?" (2023 option 09 -> P5_1_09;
#      2021 option 08 -> P5_1_8) routes Si to this question. So persons answering any of the
#      mapped block must be exactly that option's Si set, and no other 5.1 option's Si set.
#
# Fetches: INEGI microdata zips (CSV) for 2023 and 2021; live counts via a server-side
# aggregate query (no table export).

suppressMessages({ library(irw); library(data.table) })
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE <- "mexico_2023_quality_transportationstations"
C <- ".cache/mexico_2023_quality_transportationstations"
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

items <- c(paste0("p5_10_", 1:8), "p5_10a")
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
map23 <- setNames(c(paste0("P5_10_", 1:8), "P5_10A"), items)
map21 <- setNames(c(paste0("P5_9_", 1:8), "P5_9A"), items)       # 2021 question 5.9 (RENAME_2021)
pool <- function(m) grep("^P5_[0-9]+(_[0-9]+|A)$", names(m), value = TRUE)   # excludes 0-10 grades *B
s23 <- counts(w23, pool(w23), 2023); s21 <- counts(w21, pool(w21), 2021)
cat(sprintf("candidate source columns (all section V): 2023 = %d, 2021 = %d\n",
            length(unique(s23$src)), length(unique(s21$src))))

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

# The renumbering trap: same-named 2021 P5_10_* (metro / light rail) must NOT reproduce live 2021.
ks21 <- key(s21, "n", "src"); kl21 <- key(live[live$year == 2021, ], "n_live", "item")
same <- intersect(c(paste0("P5_10_", 1:8), "P5_10A"), names(ks21))
bad_hits <- sum(sapply(same, function(v) { it <- tolower(v); it %in% names(kl21) && ks21[[v]] == kl21[[it]] }))
cat(sprintf("\nsame-named 2021 columns (P5_10_*, metro): %d present, %d reproduce the live 2021 item of that name (expect 0)\n",
            length(same), bad_hits))
cat(sprintf("e.g. 2021 P5_10_1 (metro) %s vs live 2021 p5_10_1 %s\n", ks21[["P5_10_1"]], kl21[["p5_10_1"]]))
ok_all <- ok_all && bad_hits == 0

# (b) routing check
cat("\n== routing: 5.1 BRT-option Si set vs answerer set of the mapped block ==\n")
for (yr in c(2023, 2021)) {
  m <- if (yr == 2023) w23 else w21
  scr <- if (yr == 2023) "P5_1_09" else "P5_1_8"
  blk <- if (yr == 2023) paste0("P5_10_", 1:8) else paste0("P5_9_", 1:8)
  filled <- function(v) !is.na(m[[v]]) & trimws(m[[v]]) != ""
  si <- m$ID_PER[filled(scr) & trimws(m[[scr]]) == "1"]
  ans <- m$ID_PER[Reduce(`|`, lapply(blk, filled))]
  scrs <- grep("^P5_1_[0-9]+$", names(m), value = TRUE)
  eq <- scrs[sapply(scrs, function(s) setequal(m$ID_PER[filled(s) & trimws(m[[s]]) == "1"], ans))]
  good <- setequal(si, ans) && identical(eq, scr)
  ok_all <- ok_all && good
  cat(sprintf("%d: %s Si = %d; %s..8 answerers = %d; intersection = %d; screener options whose Si set equals it: %s%s\n",
              yr, scr, length(si), blk[1], length(ans), length(intersect(si, ans)), paste(eq, collapse = ","),
              if (good) "" else "  <-- MISMATCH"))
}

cat("\nNot established by this route: that column P5_10_K (2023) / P5_9_K (2021) is printed option K of\n",
    "question 5.10 (2023) / 5.9 (2021) -- that is the questionnaires' own printed numbering (INEGI's naming\n",
    "convention), not a statistical inference.\n", sep = "")
cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

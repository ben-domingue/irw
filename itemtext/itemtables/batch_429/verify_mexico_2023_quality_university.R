# verify_mexico_2023_quality_university.R -- batch_429, route 9 (response-frequency matching), per wave,
# plus a routing check.
#
# Claim: IRW item p5_3_k is INEGI ENCIG microdata column P5_3_K, printed in both the 2023 and the
# 2021 questionnaire (Seccion V; p.8 of the 2023 PDF, p.7 of the 2021 PDF) as question 5.3 option K
# (public education in universities or technological universities), and p5_3a is P5_3A (question
# 5.3a, satisfaction). Question 5.3 was NOT renumbered between waves (the 2023 renumbering inserted
# 5.7 and 5.11, after it): RENAME_2021 in data/mexico_2023_quality.py has no p5_3* entry and
# ASKED_2021 lists p5_3_1..8, p5_3a, so 2021 rows (cov_year = 2021) come from the same-named 2021
# columns.
#
# Resp coding per data/mexico_2023_quality.py: yes/no items 1 (Si) -> 0, 2 (No) -> 1;
# codes 9/98/99 -> missing; P5_3A kept 1..6.
#
# Predictions:
#  (a) for each wave separately, live count(item, resp | cov_year) equals the count of the mapped
#      source column, cell for cell; and each live item's count vector matches exactly one column
#      among ALL section-V rating columns of that wave (P5_*, excl. the 0-10 grades *B), namely its
#      mapped one -- so a permutation of the eight yes/no codes, a flipped Si/No direction, or a
#      mix-up with a neighbouring block (5.2 schooling, whose options 2-9 share wording with 5.3's
#      1-8; 5.4 IMSS, ...) fails.
#  (b) routing: 5.1 option 02 (P5_1_02 in 2023, P5_1_2 in 2021; "fue usuario(a) de educacion publica
#      en universidades o universidades tecnologicas?") routes Si to "APLICA 5.3 Y 5.3a". So the
#      persons with any answer on P5_3_1..8 must be exactly the 5.1-option-02 Si set, and no other
#      screener option's Si set -- which ties the P5_3 block to the university screener option.
#
# Fetches: INEGI microdata zips (CSV) for 2023 and 2021; live counts via a server-side
# aggregate query (no table export).

suppressMessages({ library(irw); library(data.table) })
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE <- "mexico_2023_quality_university"
C <- ".cache/mexico_2023_quality_university"
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

items <- c(paste0("p5_3_", 1:8), "p5_3a")
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
map23 <- setNames(c(paste0("P5_3_", 1:8), "P5_3A"), items)
map21 <- map23                                                     # 5.3 not renumbered
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

# (b) routing check: answerers of the 5.3 block == Si set of 5.1 option 02
cat("\n== routing: 5.1 option 02 Si set vs 5.3 answerer set ==\n")
for (yr in c(2023, 2021)) {
  m <- if (yr == 2023) w23 else w21
  scr <- if (yr == 2023) "P5_1_02" else "P5_1_2"
  filled <- function(v) !is.na(m[[v]]) & trimws(m[[v]]) != ""        # fread reads blank cells as NA
  si <- m$ID_PER[filled(scr) & trimws(m[[scr]]) == "1"]
  blk <- paste0("P5_3_", 1:8)
  ans <- m$ID_PER[Reduce(`|`, lapply(blk, filled))]
  # which 5.1 screener option's Si set equals the 5.3 answerer set?
  scrs <- grep("^P5_1_[0-9]+$", names(m), value = TRUE)
  eq <- scrs[sapply(scrs, function(s) setequal(m$ID_PER[filled(s) & trimws(m[[s]]) == "1"], ans))]
  good <- setequal(si, ans) && identical(eq, scr)
  ok_all <- ok_all && good
  cat(sprintf("%d: %s Si = %d; 5.3 answerers = %d; intersection = %d; screener options whose Si set equals it: %s%s\n",
              yr, scr, length(si), length(ans), length(intersect(si, ans)), paste(eq, collapse = ","),
              if (good) "" else "  <-- MISMATCH"))
}

cat("\nNot established by this route: that column P5_3_K is questionnaire option K of question 5.3 --\n",
    "that is the questionnaires' own printed numbering (INEGI's naming convention), not a statistical inference.\n", sep = "")
cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

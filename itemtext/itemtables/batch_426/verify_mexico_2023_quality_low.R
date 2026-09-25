# verify_mexico_2023_quality_low.R -- batch_426, route 9 (response-frequency matching, per wave)
# + a per-person routing check that ties each 5.1 column to the follow-up question it opens.
#
# Claim: IRW item p5_1_KK (KK = 01..12) is INEGI ENCIG 2023 microdata column P5_1_KK, printed in the
# 2023 questionnaire as question 5.1 option KK ("Digame si durante 2023 en (ESTADO), ¿usted... fue
# usuario(a) de <servicio>?"), the Seccion V "servicios publicos bajo demanda" use screener. ENCIG 2021
# asked the same screener with 10 options (no IMSS-Bienestar, no Cablebus/Mexicable), and RENAME_2021
# in data/mexico_2023_quality.py maps 2021 P5_1_1..5 -> p5_1_01..05, P5_1_6 -> p5_1_07,
# P5_1_7 -> p5_1_08, P5_1_8 -> p5_1_09, P5_1_9 -> p5_1_11, P5_1_10 -> p5_1_12. p5_1_06 and p5_1_10
# carry 2023 rows only.
#
# Resp coding per data/mexico_2023_quality.py: 1 (Si) -> 0, 2 (No) -> 1; 9/98/99 -> missing.
#
# Predictions:
#  (a) for each wave, live count(item, resp | cov_year) equals the count of the mapped source column,
#      cell for cell, and each live vector matches exactly one of ALL P5_1_* columns of that wave;
#  (b) per person, P5_1_KK = 1 (Si) iff the person answered the follow-up block the questionnaire routes
#      that option to ("CON CODIGO 1: APLICA 5.x Y 5.xa"). This ties each column to a question of known
#      content (5.2 basic education ... 5.13 toll highways), independently of the printed option number,
#      and must hold for the mapped block and for no other block.
#
# Fetches: INEGI microdata zips (CSV) for 2023 and 2021; live counts via a server-side aggregate query
# (no table export).

suppressMessages({ library(irw); library(data.table) })
source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")

TABLE <- "mexico_2023_quality_low"
C <- ".cache/mexico_2023_quality_low"
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

items <- sprintf("p5_1_%02d", 1:12)
map23 <- setNames(sprintf("P5_1_%02d", 1:12), items)
map21 <- c(p5_1_01 = "P5_1_1", p5_1_02 = "P5_1_2", p5_1_03 = "P5_1_3", p5_1_04 = "P5_1_4",
           p5_1_05 = "P5_1_5", p5_1_07 = "P5_1_6", p5_1_08 = "P5_1_7", p5_1_09 = "P5_1_8",
           p5_1_11 = "P5_1_9", p5_1_12 = "P5_1_10")                       # RENAME_2021
# follow-up question each option routes to (printed "CON CODIGO 1: APLICA 5.x Y 5.xa")
route23 <- setNames(2:13, items)                                          # 2023: option KK -> 5.(KK+1)
route21 <- setNames(2:11, names(map21))                                   # 2021: option k  -> 5.(k+1)
content <- c(p5_1_01 = "basic education", p5_1_02 = "university", p5_1_03 = "IMSS", p5_1_04 = "ISSSTE",
             p5_1_05 = "state/INSABI health", p5_1_06 = "IMSS-Bienestar", p5_1_07 = "electricity",
             p5_1_08 = "bus/van/combi", p5_1_09 = "BRT (fixed stations, own lane)", p5_1_10 = "Cablebus/Mexicable",
             p5_1_11 = "metro/light rail", p5_1_12 = "toll highways")

vec <- function(m, v) {
  x <- suppressWarnings(as.numeric(m[[v]]))
  x[x %in% c(9, 98, 99)] <- NA
  x <- x - 1                                  # 1 -> 0 (Si), 2 -> 1 (No)
  tb <- table(x)
  if (!length(tb)) return(NA_character_)
  paste(names(tb), as.integer(tb), sep = ":", collapse = ";")
}
cands <- function(m) { cc <- grep("^P5_1_[0-9]+$", names(m), value = TRUE)
                        setNames(sapply(cc, function(v) vec(m, v)), cc) }
k23 <- cands(w23); k21 <- cands(w21)
cat(sprintf("candidate 5.1 columns: 2023 = %d, 2021 = %d\n", length(k23), length(k21)))

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
  cat(sprintf("\n== (a) route 9, cov_year %d ==\n", yr))
  cat(sprintf("%-8s %-8s %-22s %-22s %s\n", "item", "source", "source resp:n", "live resp:n", "columns matching live vector"))
  for (it in items) {
    lk <- if (it %in% names(kl)) kl[[it]] else "<absent>"
    if (!it %in% names(mp)) {                    # 2023-only item: must have no live 2021 rows
      good <- lk == "<absent>"
      cat(sprintf("%-8s %-8s %-22s %-22s %s\n", it, "-", "(not asked)", lk, if (good) "ok, 2023-only" else "<-- UNEXPECTED 2021 ROWS"))
      ok_all <- ok_all && good; next
    }
    hits <- names(ks)[!is.na(ks) & ks == lk]
    good <- identical(hits, mp[[it]])
    ok_all <- ok_all && good
    cat(sprintf("%-8s %-8s %-22s %-22s %s%s\n", it, mp[[it]], ks[[mp[[it]]]], lk,
                paste(hits, collapse = ","), if (good) "" else "  <-- MISMATCH"))
  }
  if (length(unique(ks[mp])) != length(mp)) { ok_all <- FALSE; cat("mapped source vectors not all distinct\n") }
}

# (b) routing: Si on option KK <=> answered follow-up block 5.(route). Build answerer sets per block.
answerers <- function(m, qn) {
  cc <- grep(sprintf("^P5_%d_[0-9]+$|^P5_%dA$", qn, qn), names(m), value = TRUE)
  rowSums(sapply(cc, function(v) { x <- m[[v]]; !is.na(x) & nzchar(trimws(x)) & x != "NA" })) > 0
}
for (yr in c(2023, 2021)) {
  m  <- if (yr == 2023) w23 else w21
  mp <- if (yr == 2023) map23 else map21
  rt <- if (yr == 2023) route23 else route21
  blocks <- sort(unique(rt))
  A <- sapply(blocks, function(b) answerers(m, b)); colnames(A) <- paste0("5.", blocks)
  cat(sprintf("\n== (b) routing, %d: n(Si), n(answered mapped block), n(Si & answered), blocks whose answerer set == Si set ==\n", yr))
  for (it in names(mp)) {
    si <- m[[mp[[it]]]] %in% "1"
    eq <- colnames(A)[apply(A, 2, function(a) identical(a, si))]
    tgt <- paste0("5.", rt[[it]])
    good <- identical(eq, tgt)
    ok_all <- ok_all && good
    cat(sprintf("%-8s %-8s %-30s Si=%6d  %-5s answered=%6d  both=%6d  equal-set blocks: %s%s\n", it, mp[[it]],
                content[[it]], sum(si), tgt, sum(A[, tgt]), sum(si & A[, tgt]), paste(eq, collapse = ","),
                if (good) "" else "  <-- MISMATCH"))
  }
}

cat("\nNot established by these routes: the exact 5.1 wording itself -- that rests on INEGI's printed\n",
    "questionnaire (option KK under 5.1); the routing check ties each column to the CONTENT of the follow-up\n",
    "question it opens, which is what distinguishes every item from every other.\n", sep = "")
cat(if (ok_all) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

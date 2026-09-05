# verify_dejesus_2017_sf36.R  -- Step 5b mapping verification
#
# mapping_basis = paper_explicit. The study's own supplements reproduce the whole
# questionnaire with the SAME numbering the data columns use: S2 File "Projeto de
# pesquisa" Anexo 5 (Portuguese, as administered) and S3 File "Research project"
# Attachment 5 (the authors' own English rendering), both of PLOS ONE
# 10.1371/journal.pone.0179185 (CC BY 4.0). The IRW item code IS the S4 File
# column name ("SF-36 3.1"), and data/dejesus_2017_ozone_knee.py melts those
# columns by name, so the only inference is that "SF-36 3.1" means Anexo 5
# question 3's FIRST sub-item, question 4/5's printed 1=Sim/2=Nao maps onto the
# 0/1 the file actually stores, and so on.
#
# Three falsifiable predictions are checked, all from the questionnaire text:
#
#  A. RESPONSE-RANGE FINGERPRINT (route 2). Anexo 5 gives Q1 five options, Q2
#     five, each of Q3's ten sub-items three, Q4's four and Q5's three a yes/no
#     pair, Q6 five, Q7 six, Q8 five. That mixed pattern must appear in the live
#     table, item for item.
#  B. KEYING DIRECTION (route 6). Q3 is scored 1 = "dificulta muito" .. 3 = "nao
#     dificulta"; every other shipped item is scored so that a HIGHER number is
#     worse health. So the Q3 block mean must correlate NEGATIVELY with Q1, Q2,
#     Q6, Q7, Q8 and with the Q4/Q5 yes-no items, and that fixes 1 = "Sim" /
#     0 = "Nao" for Q4-Q5 -- which the printed questionnaire does NOT tell you,
#     because it prints 1=Sim/2=Nao while the deposited file stores 0/1.
#  C. DIFFICULTY ORDERING inside Q3 (route 8). The ten activities are a near-
#     Guttman ladder, so their means must order accordingly: vigorous activities
#     hardest, bathing/dressing easiest, and each nested pair in the right order
#     (walking a mile < several blocks < one block; several flights of stairs <
#     one flight).
#
# What this does NOT establish: nothing here separates SF-36 4.2 / 4.3 / 4.4 from
# each other (means 0.368 / 0.383 / 0.365, identical 0/1 range) or 5.2 from 5.3.
# Those four rest on the questionnaire's own sub-item order alone. Status is
# therefore PARTIAL, not VERIFIED.
#
# Data: the live per-item aggregates come from irw_table_sets() (server-side, no
# export); the item-level statistics come from the CC BY S4 File itself, which is
# legitimate here only because the live table is a straight melt of it -- step A
# is what proves that (n and range match column for column).

suppressMessages({library(irw); library(readxl)})

TABLE <- "dejesus_2017_sf36"
S4 <- paste0("https://journals.plos.org/plosone/article/file",
             "?type=supplementary&id=10.1371/journal.pone.0179185.s004")

ITEMS <- c("SF-36 1", "SF-36 2", paste0("SF-36 3.", 1:10),
           paste0("SF-36 4.", 1:4), paste0("SF-36 5.", 1:3),
           "SF-36 6", "SF-36 7", "SF-36 8")

# Predicted (min, max, n_levels) read off Anexo 5 of the S2 File.
PRED <- rbind(c(1,5,5), c(1,5,5),
              matrix(rep(c(1,3,3), 10), ncol = 3, byrow = TRUE),
              matrix(rep(c(0,1,2),  7), ncol = 3, byrow = TRUE),
              c(1,5,5), c(1,6,6), c(1,5,5))
rownames(PRED) <- ITEMS

tf <- tempfile(fileext = ".xls")   # S4 File is a legacy OLE2 .xls despite the (XLS) label
# PLOS 403s a bare libcurl UA; send the same one the processing script uses.
old_ua <- getOption("HTTPUserAgent")
options(HTTPUserAgent = "IRW-Finder/1.0 (ben.domingue@gmail.com)")
download.file(S4, tf, quiet = TRUE, mode = "wb", method = "libcurl")
options(HTTPUserAgent = old_ua)
raw <- as.data.frame(readxl::read_excel(tf))
x <- sapply(ITEMS, function(k) suppressWarnings(as.numeric(raw[[k]])))

s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
pi <- pi[match(ITEMS, pi$item), ]

cat("== A. response-range fingerprint: questionnaire vs live table vs S4 File ==\n")
cat(sprintf("%-11s %-14s %-22s %-18s\n", "item", "predicted", "live (n/min/max/lvls)", "S4 (n/min/max)"))
okA <- TRUE
for (i in seq_along(ITEMS)) {
    col <- x[, i]; col <- col[!is.na(col)]
    hitL <- pi$resp_min[i] == PRED[i,1] && pi$resp_max[i] == PRED[i,2] &&
            pi$n_resp_levels[i] == PRED[i,3]
    hitS <- length(col) == pi$n[i] && min(col) == pi$resp_min[i] && max(col) == pi$resp_max[i]
    okA <- okA && hitL && hitS
    cat(sprintf("%-11s %-14s %-22s %-18s %s\n", ITEMS[i],
                sprintf("%g-%g/%g", PRED[i,1], PRED[i,2], PRED[i,3]),
                sprintf("%d/%g/%g/%g", pi$n[i], pi$resp_min[i], pi$resp_max[i], pi$n_resp_levels[i]),
                sprintf("%d/%g/%g", length(col), min(col), max(col)),
                if (hitL && hitS) "ok" else "MISMATCH"))
}

pf <- rowMeans(x[, paste0("SF-36 3.", 1:10)], na.rm = TRUE)
others <- setdiff(ITEMS, paste0("SF-36 3.", 1:10))

cat("\n== B. keying direction: correlation of each item with the Q3 (function) block mean ==\n")
cat("   Q3 is coded 3 = 'nao dificulta de modo algum', so every worse-is-higher item\n")
cat("   must come out NEGATIVE; for Q4/Q5 that is what fixes 1 = 'Sim', 0 = 'Nao'.\n")
rs <- sapply(others, function(k) cor(x[, k], pf, use = "complete.obs"))
for (k in others) cat(sprintf("  %-11s r = %+.3f  %s\n", k, rs[k],
                              if (rs[k] < 0) "ok" else "WRONG SIGN"))
okB <- all(rs < 0)

yn <- paste0("SF-36 ", c("4.1","4.2","4.3","4.4","5.1","5.2","5.3"))
cat("\n   mean Q3-block function score by response, yes/no items:\n")
for (k in yn) cat(sprintf("  %-11s resp=0: %.2f   resp=1: %.2f   (resp=1 must be the WORSE group)\n",
                          k, mean(pf[x[, k] == 0], na.rm = TRUE), mean(pf[x[, k] == 1], na.rm = TRUE)))
okB <- okB && all(sapply(yn, function(k)
    mean(pf[x[, k] == 1], na.rm = TRUE) < mean(pf[x[, k] == 0], na.rm = TRUE)))

cat("\n== C. difficulty ordering inside Q3 (higher mean = less limited) ==\n")
m <- colMeans(x[, paste0("SF-36 3.", 1:10)], na.rm = TRUE)
lab <- c("vigorous activities", "moderate activities", "lifting/carrying groceries",
         "several flights of stairs", "one flight of stairs", "bending/kneeling",
         "walking >1 km", "walking several blocks", "walking one block",
         "bathing or dressing")
for (i in 1:10) cat(sprintf("  %-11s %.3f   %s\n", names(m)[i], m[i], lab[i]))
pred <- list(
  c("SF-36 3.1 (vigorous) is the most limited of the ten",
    all(m["SF-36 3.1"] < m[setdiff(names(m), "SF-36 3.1")])),
  c("SF-36 3.10 (bathing/dressing) is the least limited of the ten",
    all(m["SF-36 3.10"] > m[setdiff(names(m), "SF-36 3.10")])),
  c("walking ladder: >1 km < several blocks < one block",
    m["SF-36 3.7"] < m["SF-36 3.8"] && m["SF-36 3.8"] < m["SF-36 3.9"]),
  c("stairs ladder: several flights < one flight",
    m["SF-36 3.4"] < m["SF-36 3.5"]))
for (p in pred) cat(sprintf("  %-60s %s\n", p[1], if (as.logical(p[2])) "ok" else "FAILED"))
okC <- all(sapply(pred, function(p) as.logical(p[2])))

cat(sprintf("\nA range fingerprint: %s | B keying direction: %s | C difficulty ordering: %s\n",
            ifelse(okA, "ok", "FAIL"), ifelse(okB, "ok", "FAIL"), ifelse(okC, "ok", "FAIL")))
cat("Note: this pins the block boundaries, the five standalone items, the Q3 order and\n",
    "the 0/1 yes-no direction. It does NOT distinguish SF-36 4.2/4.3/4.4 from each other\n",
    "(0.368/0.383/0.365) or 5.2 from 5.3 -- those follow the questionnaire's own order.\n", sep = "")

cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

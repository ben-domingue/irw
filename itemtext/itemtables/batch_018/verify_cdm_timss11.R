# verify_cdm_timss11.R -- Step 5b, item_text <-> item mapping.
#
# THE CLAIM. Every shipped item_text was transcribed from the page of
# "TIMSS 2011 User Guide for the International Database: Released Items,
# Mathematics - Fourth Grade" (IEA / TIMSS & PIRLS International Study Center,
# 2013) whose header prints that item's own code, e.g. the page headed
# "ID: M031071" carries the half-turn rotation item shipped as M031071.
# cdm.R builds the IRW table with `x <- x[, as.character(Q$item)]`, so the IRW
# `item` IS the CDM column name, which is that same IEA item ID. The tie is
# therefore a LABEL match (Step 5b's "explicit code labels" exemption), not an
# order inference. This script corroborates it with numbers.
#
# THE FALSIFIABLE PREDICTION. The same IEA publication ships
# T11_UG_G4_M_Released_Items_Statistics.xlsx, one sheet per released item,
# headed with that item's ID and giving each country's percent correct.
# AUSTRIA is the country this table samples (data.timss11.G4.AUT, IDCNTRY=40).
# If a shipped wording sat on the wrong code, the IEA percent correct for that
# code would not track the response data for that column.
#
# Two checks:
#   (1) live per-item n (irw::irw_table_sets, server-side aggregate -- no
#       export) == per-item non-missing n in the CDM source object, all 174
#       items. This pins the live table to this exact source object.
#   (2) IEA-published Austria percent correct vs observed percent correct, all
#       73 released items.
#
# WHAT THIS DOES NOT ESTABLISH: the other 101 items are TIMSS secure items and
# ship no item_text at all, so there is no mapping claim about them to check.

suppressMessages(library(irw))
suppressMessages(library(CDM))

TABLE <- "cdm_timss11"
TOL   <- 3.0   # percentage points; published values are survey-weighted, observed are not

# IEA published percent correct, Austria, from
# T11_UG_G4_M_Released_Items_Statistics.xlsx (one sheet per item).
PUBLISHED <- c(
  M031004=36, M031009=35, M031016=27, M031043=52,
  M031071=40, M031079B=81, M031079C=41, M031083=75,
  M031088=76, M031093=49, M031109=61, M031128=77,
  M031133=80, M031155=52, M031159=71, M031183=23,
  M031185=57, M031187=82, M031210=35, M031218=64,
  M031251=43, M031252=66, M031294=68, M031297=30,
  M031313=79, M031316=94, M031317=18, M031325=12,
  M031346A=74, M031346B=30, M031346C=22, M031379=18,
  M031380=19, M041003=56, M041010=87, M041011=75,
  M041041=55, M041064=58, M041098=37, M041104=37,
  M041107=90, M041115A=63, M041115B=51, M041122=12,
  M041143=40, M041148=67, M041155=56, M041158=74,
  M041160A=89, M041160B=89, M041175=87, M041184=79,
  M041199=76, M041265=47, M041284=15, M041299=28,
  M041320=38, M041327=39, M041328=72, M041329=75,
  M041335=93, M051001=17, M051007=32, M051015=26,
  M051064A=48, M051064B=67, M051091=43, M051109=63,
  M051117=57, M051123=37, M051203=58, M051305=72,
  M051601=61)

# ---- source object: exactly what data/cdm.R reads -------------------------
data(data.timss11.G4.AUT)
Q   <- data.timss11.G4.AUT$q.matrix1
src <- data.timss11.G4.AUT$data[, as.character(Q$item)]

# ---- check 1: live per-item n == source per-item n ------------------------
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
live_n <- setNames(as.numeric(pi$n), as.character(pi$item))
src_n  <- sapply(src, function(v) sum(!is.na(v)))

common <- intersect(names(live_n), names(src_n))
cat(sprintf("check 1: %d items compared (live set %d, source set %d)\n",
            length(common), length(live_n), length(src_n)))
nbad <- sum(live_n[common] != src_n[common])
cat(sprintf("check 1: per-item n mismatches: %d\n", nbad))
if (nbad > 0) print(data.frame(item = common, live = live_n[common],
                               src = src_n[common])[live_n[common] != src_n[common], ])
ok1 <- (nbad == 0) && setequal(names(live_n), names(src_n))
cat(sprintf("check 1: %s\n\n", if (ok1) "PASS -- live table is this source object, column for column" else "FAIL"))

# ---- check 2: IEA Austria percent correct vs observed ---------------------
ids <- names(PUBLISHED)
obs <- 100 * sapply(src[ids], mean, na.rm = TRUE)
d   <- obs - PUBLISHED

cat(sprintf("%-10s %10s %10s %8s\n", "item", "IEA pub", "observed", "diff"))
o <- order(-abs(d))
for (i in o) cat(sprintf("%-10s %10d %10.1f %8.1f\n", ids[i], PUBLISHED[i], obs[i], d[i]))

cat(sprintf("\ncheck 2: n = %d released items; Pearson r = %.4f; max |diff| = %.1f pp; mean |diff| = %.2f pp (tolerance %.1f)\n",
            length(ids), cor(PUBLISHED, obs), max(abs(d)), mean(abs(d)), TOL))
ok2 <- max(abs(d)) <= TOL

# How much of the pinning is the statistics doing on their own? Report how many
# items have a RIVAL published value within tolerance of their observed value --
# for those, the numbers alone would not separate them and the code label on the
# released-item page is what does.
rivals <- sapply(seq_along(ids), function(i) sum(abs(PUBLISHED - obs[i]) <= TOL) - 1L)
cat(sprintf("check 2: items whose observed value is within tolerance of some OTHER item's published value: %d of %d\n",
            sum(rivals > 0), length(ids)))
cat("         -> the statistics corroborate the assignment but do not by themselves\n")
cat("            separate every item from every other; the printed item ID does.\n")
cat("check 2: nothing here speaks to the 101 secure items, which ship no item_text.\n\n")

cat(if (ok1 && ok2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_SABFI2_Gallardo_Pujol_2018_Micro.R -- Step 5b re-runnable check (batch_166)
#
# CLAIM. Micro1..Micro6 are the six contexts of the micro-macro life-space item
# (Salgado, Gonzalez-Suhr & Oceja, 2013, "EV-macro") in the order the International
# Situations Project's Spanish survey screen shows them (item 14):
#   Micro1 En familia | Micro2 Con amigos | Micro3 En la ciudad donde vivo |
#   Micro4 En la sociedad | Micro5 En el mundo | Micro6 En el trabajo
# so the MACRO block (city, society, world; Salgado 2013) is {Micro3, Micro4, Micro5}
# and the MICRO/MESO block (family, friends, work) is {Micro1, Micro2, Micro6}; resp
# 1 = Nada ... 4 = Totalmente, stored unrecoded.
#
# The live table is NOT a racial-microaggression scale (the dictionary Description
# says so); see provenance.
#
# DATA. The study's own Study 3 file on OSF kp572 (CC BY 4.0), which
# data/SABFI2_Gallardo_Pujol_2018.R melts without renaming or recoding
# (select(starts_with("Micro")) + pivot_longer). Used instead of irw_fetch() to keep
# this check off the Redivis export cap; step (0) ties it to the live table by per-item
# n, mean and floor/ceiling %, hard-coded from item_stats.R run 2026-09-10.
#
# PUBLISHED. Salgado, Gonzalez-Suhr & Oceja (2013), Anales de Psicologia 29(2), 583-589,
# doi 10.6018/analesps.29.2.136351, Study 1 (N=149 UAM psychology students, 1-10 scale,
# instrument order family, friends, work, city, society, world):
#   EFA factor 1 (macro): city .37, society .63, world .55
#   EFA factor 2 (micro/meso): family .33, friends .32, work .57
#   means: friends 7.84, family 7.14, work 6.42 | society 6.28, city 6.09, world 5.58
#
# Competing hypothesis tested throughout: the columns follow the ORIGINAL instrument
# order (family, friends, work, city, society, world -- also the row order of the ISP's
# Spanish translation .docx), which would make the macro block {Micro4, Micro5, Micro6}.

csv <- file.path(tempdir(), "sabfi2_study3.csv")
if (!file.exists(csv)) download.file("https://osf.io/download/r2zhc/", csv, quiet = TRUE, mode = "wb")
d <- read.csv(csv)
M <- d[, paste0("Micro", 1:6)]
ok <- TRUE

# (0) the OSF file is the live table
LIVE_N    <- rep(419, 6)
LIVE_MEAN <- c(3.09, 3.25, 2.84, 2.70, 2.48, 2.43)
LIVE_FLOOR <- c(2.6, 1.2, 4.3, 2.9, 8.6, 16.0)
LIVE_CEIL  <- c(33.9, 36.3, 16.9, 14.6, 12.9, 6.7)
obs_n <- colSums(!is.na(M)); obs_m <- colMeans(M, na.rm = TRUE)
obs_f <- 100 * colMeans(M == 1, na.rm = TRUE); obs_c <- 100 * colMeans(M == 4, na.rm = TRUE)
cat("(0) OSF Study 3 file vs live item_stats.R\n")
for (i in 1:6) cat(sprintf("  %-7s n live %d / osf %d | mean live %.2f / osf %.4f | floor%% %.1f / %.1f | ceil%% %.1f / %.1f\n",
                           names(M)[i], LIVE_N[i], obs_n[i], LIVE_MEAN[i], obs_m[i], LIVE_FLOOR[i], obs_f[i], LIVE_CEIL[i], obs_c[i]))
if (any(obs_n != LIVE_N) || any(abs(obs_m - LIVE_MEAN) > 0.006) ||
    any(abs(obs_f - LIVE_FLOOR) > 0.06) || any(abs(obs_c - LIVE_CEIL) > 0.06)) {
  cat("  -> OSF file does NOT reproduce live table\n"); ok <- FALSE
}

# (1) route 5: which of the 10 three-vs-three splits gives the clearest block structure?
C <- cor(M)
res <- NULL
cmb <- combn(6, 3)
for (k in seq_len(ncol(cmb))) {
  a <- cmb[, k]; if (!(1 %in% a)) next; b <- setdiff(1:6, a)
  w <- c(C[a, a][upper.tri(diag(3))], C[b, b][upper.tri(diag(3))]); x <- as.vector(C[a, b])
  res <- rbind(res, data.frame(block_with_Micro1 = paste(a, collapse = ","), other_block = paste(b, collapse = ","),
                               mean_within = mean(w), mean_cross = mean(x), within_minus_cross = mean(w) - mean(x)))
}
res <- res[order(-res$within_minus_cross), ]
cat("\n(1) block structure, all 10 splits (Micro numbers), ranked by mean within-block r minus mean cross-block r\n")
print(res, digits = 3, row.names = FALSE)
cat(sprintf("  claimed split {1,2,6}|{3,4,5}: %.3f   original-instrument-order split {1,2,3}|{4,5,6}: %.3f\n",
            res$within_minus_cross[res$block_with_Micro1 == "1,2,6"], res$within_minus_cross[res$block_with_Micro1 == "1,2,3"]))
cat(sprintf("  within macro {3,4,5}: r34 %.2f r35 %.2f r45 %.2f | largest cross-block r %.2f\n",
            C[3, 4], C[3, 5], C[4, 5], max(C[c(1, 2, 6), c(3, 4, 5)])))
if (res$block_with_Micro1[1] != "1,2,6") { cat("  -> claimed split is not the best-fitting one\n"); ok <- FALSE }

# (2) Salgado's macro loadings order city (.37) < world (.55) < society (.63)
fa <- factanal(M, 2, rotation = "promax")
L <- unclass(fa$loadings)
macro_f <- which.max(colSums(abs(L[c("Micro4", "Micro5"), , drop = FALSE])))
lm <- L[, macro_f]
cat("\n(2) 2-factor promax EFA, loadings on the macro factor (published city .37 < world .55 < society .63)\n")
cat(sprintf("  %-7s %.3f\n", names(lm), lm), sep = "")
cat(sprintf("  claimed: city=Micro3 %.3f < world=Micro5 %.3f < society=Micro4 %.3f\n", lm["Micro3"], lm["Micro5"], lm["Micro4"]))
if (!(lm["Micro3"] < lm["Micro5"] && lm["Micro5"] < lm["Micro4"])) { cat("  -> macro loading order does not match\n"); ok <- FALSE }
cat(sprintf("  under the original-order reading, 'world' would be Micro6, whose macro loading is %.3f\n", lm["Micro6"]))

# (3) direction: micro/meso contexts endorsed more than macro (published 7.13 vs 5.98 on 1-10)
mic <- mean(obs_m[c(1, 2, 6)]); mac <- mean(obs_m[3:5])
cat(sprintf("\n(3) direction: mean of micro/meso items %.3f vs macro items %.3f (published 7.13 vs 5.98)\n", mic, mac))
cat(sprintf("  friends Micro2 %.2f > family Micro1 %.2f (published 7.84 > 7.14)\n", obs_m[2], obs_m[1]))
if (!(mic > mac)) { cat("  -> micro not above macro; direction in doubt\n"); ok <- FALSE }

cat("\nNOT ESTABLISHED: (a) order WITHIN the micro/meso block -- nothing here separates family/friends/work\n",
    "beyond the weak friends>family mean ordering, and 'work' behaves UNLIKE Salgado's sample (lowest mean\n",
    "here, 2.43 with 16% 'Nada', vs third-highest there; loads .30 on the micro factor vs published .57);\n",
    "(b) society vs world rests on a .80 vs .75 loading gap. Tie of codes to screen positions rests on the\n",
    "deposit exporting in on-screen order. Hence PARTIAL.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

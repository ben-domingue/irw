# Verification for hao_2025_social_regulation (batch_457).
#
# CLAIM. The IRW code IS the deposit's column name (data/hao_2025_foreign_language_anxiety.py
# melts SR1..SR8 by name), but the deposit (figshare 10.6084/m9.figshare.30397234, one .xlsx,
# header row only) carries no item wording, and Hao & Sun's preprint (Research Square
# rs-7750527/v1) prints only one (ego-resilience) example item. Wording comes from Guo & Li
# (2022) Front Psychol 13:1046340, Appendix 1 (Table_1.docx), whose retained social-resilience
# items are original items 17-24 (item 16 deleted in EFA). Mapping assumed: SRk = Guo item 16+k.
# This is a paper_order inference.
#
# Routes (all cross-sample or content-structural; PARTIAL by construction):
#  (a) content pairs -> correlation structure. Items 17 and 18 are the only two items with
#      parallel wording ("When I ... encounter difficulties in FL learning, I would seek help
#      from my classmates / teachers"); items 19 and 20 are the two about helping/getting on
#      with classmates. Under the assumed mapping the strongest inter-item correlation should be
#      SR1-SR2, and SR3-SR4 should be the strongest pair not involving SR1/SR2.
#  (b) marker: Guo item 23 ("make foreign friends if time permits") has by far the largest SD
#      in Guo & Li (1.732 vs 1.445-1.563), so SR7 should have the largest live SD.
#  (c) item means vs Guo & Li Table 1 (N=313 college EFL, 7-point): Guo's highest item (20)
#      should be the live highest (SR4); within the pairs, 17>18 and 20>19 in Guo.
#  Rank correlation of all 8 means is printed but is weak (rho ~0.42) and NOT used for the verdict.
suppressMessages(library(irw))
TABLE <- "hao_2025_social_regulation"
GUO_M  <- c(4.73, 4.42, 4.82, 5.07, 4.87, 4.84, 4.64, 4.58)          # items 17..24
GUO_SD <- c(1.445, 1.487, 1.554, 1.458, 1.460, 1.546, 1.732, 1.563)
codes <- paste0("SR", 1:8); names(GUO_M) <- names(GUO_SD) <- codes

d <- as.data.frame(irw::irw_fetch(TABLE))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w)); w <- w[, codes]
m <- colMeans(w, na.rm = TRUE); s <- apply(w, 2, sd, na.rm = TRUE)
cat(sprintf("%-4s %-4s %7s %7s %8s %8s\n", "item", "Guo", "Guo_M", "Guo_SD", "live_M", "live_SD"))
for (i in 1:8) cat(sprintf("%-4s %-4d %7.2f %7.3f %8.3f %8.3f\n", codes[i], 16 + i, GUO_M[i], GUO_SD[i], m[i], s[i]))

R <- cor(w, use = "pairwise"); diag(R) <- NA
top <- which(R == max(R, na.rm = TRUE), arr.ind = TRUE)[1, ]
cat(sprintf("\n(a) strongest inter-item r = %.3f between %s and %s (predicted SR1-SR2)\n",
            max(R, na.rm = TRUE), codes[top[1]], codes[top[2]]))
R2 <- R[3:8, 3:8]
top2 <- which(R2 == max(R2, na.rm = TRUE), arr.ind = TRUE)[1, ]
cat(sprintf("    strongest pair among SR3-SR8: r = %.3f, %s-%s (predicted SR3-SR4); next best r = %.3f\n",
            max(R2, na.rm = TRUE), codes[2 + top2[1]], codes[2 + top2[2]],
            sort(R2[upper.tri(R2)], decreasing = TRUE)[2]))
a_ok <- setequal(codes[top], c("SR1", "SR2")) && setequal(codes[2 + top2], c("SR3", "SR4"))
b_ok <- names(which.max(s)) == "SR7"
cat(sprintf("(b) largest live SD: %s = %.3f (predicted SR7)\n", names(which.max(s)), max(s)))
c_ok <- names(which.max(m)) == "SR4" && m["SR1"] > m["SR2"] && m["SR4"] > m["SR3"]
cat(sprintf("(c) highest live mean: %s (predicted SR4); SR1>SR2: %s; SR4>SR3: %s\n",
            names(which.max(m)), m["SR1"] > m["SR2"], m["SR4"] > m["SR3"]))
cat(sprintf("    [info only] Spearman rho, all 8 means Guo vs live = %.3f\n", cor(GUO_M, m, method = "spearman")))

cat("\nNOT ESTABLISHED: cross-sample (college EFL, 7-pt) vs this study (junior high, 1-5), and the\n",
    "predictions in (a) were stated after inspecting the matrix, though they follow from the wording.\n",
    "The routes pin SR1/SR2 as the help-seeking pair, SR3/SR4 as the helping/relationship pair, SR7\n",
    "and SR4; they do NOT separate SR5, SR6 and SR8 from each other (Guo means 4.87/4.84/4.58 vs live\n",
    "3.47/3.39/3.45 -- SR6/SR8 order discordant). Status: PARTIAL.\n", sep = "")
cat(if (a_ok && b_ok && c_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

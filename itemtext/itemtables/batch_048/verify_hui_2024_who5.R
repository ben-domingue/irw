# verify_hui_2024_who5.R -- Step 5b evidence, re-runnable.
#
# CLAIM: IRW item code WHO<n> carries the wording printed as item <n> of the
# official WHO-Five Well-Being Index, and resp is coded 0 = "At no time" ...
# 5 = "All of the time" (higher = better well-being), as shipped in
# itemtables/batch_048/hui_2024_who5__items.csv.
#
# The item codes WHO1..WHO5 ARE the column names of the study's own data file
# (data/hui_2024_gbfs_battery.py melts value_vars=["WHO1".."WHO5"] by name), and
# that file carries no variable or value labels, so the only tie between code and
# wording is the trailing digit against the instrument's fixed canonical
# numbering. Two independent predictions are tested.
#
# (A) DIRECTION / BLOCK IDENTITY -- decisive, and it is what pins option_text to
#     resp. Hui et al. (2024) PLOS ONE 19(5):e0300064 report, on this very
#     sample, Cronbach's alpha = 0.913 for the WHO-5 and a concurrent-validity
#     correlation of r = +0.354 between the GBFS total and the WHO-5 total. The
#     sign is the falsifiable part: if the shipped anchors were reversed (0 =
#     "All of the time"), the same computation returns -0.354.
#
# (B) MAPPING -- per-item profile against an independent published WHO-5 sample.
#     Iversen HH, Kjollesdal MKR, Ellingsen-Dalskau LH, Haugum M, Bjertnaes O (2025),
#     Qual Life Res 35, doi:10.1007/s11136-025-04104-9 (PMC12748132, CC BY), Table 2, print per-item mean
#     (0-100 scale) and per-item "At no time" (floor) percentage for all five
#     numbered WHO-5 items in a nationwide sample of N ~ 2296 inpatients. Item 4
#     ("I woke up feeling fresh and rested") is the marker: lowest mean and by far
#     the highest floor in that sample, and it is a distribution no other WHO-5
#     item produces.
#
# What this does NOT establish: it does not separate every item from every other.
# Items 3 and 5 are ~0.2 points apart here (published order actually puts 5 above
# 3), and items 1 and 2 are close, so a 3<->5 or a 1<->2 swap would not be caught.
# The verification row is PARTIAL for exactly that reason.

suppressMessages(library(irw))

TABLE <- "hui_2024_who5"

# --- published values, hard-coded ---
ALPHA_PUB <- 0.913                      # Hui et al. 2024, Methods (this sample)
R_PUB     <- 0.354                      # Hui et al. 2024, Abstract/Results (this sample)
# Ness et al. 2025 (PMC12748132) Table 2: item mean on the 0-100 scale, floor %.
PUB_MEAN  <- c(WHO1 = 36.23, WHO2 = 36.11, WHO3 = 30.86, WHO4 = 28.98, WHO5 = 34.95)
PUB_FLOOR <- c(WHO1 = 14.2,  WHO2 = 17.7,  WHO3 = 28.2,  WHO4 = 35.0,  WHO5 = 18.9)

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
its <- paste0("WHO", 1:5)

wide <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
                direction = "wide")
names(wide) <- sub("^resp\\.", "", names(wide))
wide <- wide[stats::complete.cases(wide[, its]), ]

# ---- (A) direction / block identity ----
X <- as.matrix(wide[, its])
k <- ncol(X)
alpha <- k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))

g <- as.data.frame(irw::irw_fetch("hui_2024_gbfs"))
g$resp <- as.numeric(g$resp)
gw <- reshape(g[, c("id", "item", "resp")], idvar = "id", timevar = "item",
              direction = "wide")
names(gw) <- sub("^resp\\.", "", names(gw))
gits <- paste0("b", 1:28)
gw <- gw[stats::complete.cases(gw[, gits]), ]
gw$gbfs_total <- rowSums(gw[, gits])
wide$who_total <- rowSums(X)
m <- merge(wide[, c("id", "who_total")], gw[, c("id", "gbfs_total")], by = "id")
r_asis <- cor(m$gbfs_total, m$who_total)
r_rev  <- cor(m$gbfs_total, 25 - m$who_total)

cat("(A) DIRECTION / BLOCK IDENTITY, against Hui et al. (2024) on this sample\n")
cat(sprintf("    n complete WHO-5 = %d ; n paired with GBFS = %d\n", nrow(wide), nrow(m)))
cat(sprintf("    Cronbach alpha        observed %.4f   published %.3f\n", alpha, ALPHA_PUB))
cat(sprintf("    r(GBFS, WHO-5) as shipped %+.4f   published %+.3f\n", r_asis, R_PUB))
cat(sprintf("    r(GBFS, WHO-5) if anchors reversed %+.4f  <- what a flipped scale would give\n", r_rev))
okA <- abs(alpha - ALPHA_PUB) <= 0.005 && abs(r_asis - R_PUB) <= 0.005 && r_asis > 0

# ---- (B) per-item profile ----
obs_mean  <- sapply(its, function(i) mean(d$resp[d$item == i]) * 20)   # to 0-100
obs_floor <- sapply(its, function(i) 100 * mean(d$resp[d$item == i] == 0))

cat("\n(B) PER-ITEM PROFILE, against Iversen et al. (2025) Qual Life Res, PMC12748132, Table 2 (N~2296)\n")
cat(sprintf("    %-5s %10s %10s | %9s %9s\n", "item", "mean.pub", "mean.obs", "floor.pub", "floor.obs"))
for (i in its)
    cat(sprintf("    %-5s %10.2f %10.2f | %8.1f%% %8.2f%%\n",
                i, PUB_MEAN[i], obs_mean[i], PUB_FLOOR[i], obs_floor[i]))
rho <- cor(PUB_MEAN[its], obs_mean[its], method = "spearman")
cat(sprintf("    Spearman rank correlation of item means: %.2f\n", rho))
cat(sprintf("    lowest observed mean  : %s (published lowest: WHO4)\n", its[which.min(obs_mean)]))
cat(sprintf("    highest observed floor: %s (published highest: WHO4)\n", its[which.max(obs_floor)]))
cat(sprintf("    highest observed mean : %s (published highest: WHO1)\n", its[which.max(obs_mean)]))
okB <- its[which.min(obs_mean)] == "WHO4" && its[which.max(obs_floor)] == "WHO4" &&
       its[which.max(obs_mean)] == "WHO1" && rho >= 0.7

cat("\nNOT ESTABLISHED: WHO3 vs WHO5 (observed means differ by only",
    sprintf("%.2f", abs(obs_mean["WHO3"] - obs_mean["WHO5"])),
    "points on the 0-100 scale, and the published sample orders them the other way),\n",
    "and WHO1 vs WHO2 are separated by only",
    sprintf("%.2f", abs(obs_mean["WHO1"] - obs_mean["WHO2"])),
    "points. A 3<->5 or 1<->2 swap would survive this test; hence PARTIAL.\n")

cat(if (okA && okB) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

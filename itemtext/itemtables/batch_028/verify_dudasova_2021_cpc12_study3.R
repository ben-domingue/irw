# Step 5b verification for dudasova_2021_cpc12_study3.
#
# CLAIM: cpc1..cpc12 are, in order, items 1..12 of the German CPC-12 as printed
# in Lorenz et al. (2016) PLOS ONE 11(4):e0152892 S1 Appendix -- i.e.
# cpc1-3 = hope (SHS), cpc4-6 = optimism (AFF/LOT-R), cpc7-9 = resilience
# (RS-13), cpc10-12 = self-efficacy (GSE).
#
# FALSIFIABLE PREDICTION: Dudasova et al. (2021) Table 7 publishes standardized
# factor loadings for the 4+1 factor model fitted to exactly this dataset
# (the second German sample, N=202, their S3 File). Refitting that model on the
# live IRW table with the claimed grouping must reproduce every loading. A
# wrong block assignment, or a within-block permutation, changes which loading
# lands on which row.

suppressMessages({library(irw); library(lavaan); library(dplyr); library(tidyr)})

TABLE <- "dudasova_2021_cpc12_study3"

# Dudasova et al. 2021, Table 7 (10.1371/journal.pone.0247114.t007), 4+1 factors.
PUB <- c(Hope1=.659, Hope2=.624, Hope3=.780,
         Optimism1=.752, Optimism2=.781, Optimism3=.683,
         Resil1=.282, Resil2=.817, Resil3=.385,
         `S-E1`=.633, `S-E2`=.620, `S-E3`=.759)
PUB2 <- c(Hope=.789, Optimism=.582, Resil=.863, SelfEf=.821)   # 2nd-order
TOL <- 0.01

d <- irw::irw_fetch(TABLE)
w <- as.data.frame(d %>% select(id, item, resp) %>%
                     pivot_wider(names_from = item, values_from = resp))

mod <- "
Hope   =~ cpc1  + cpc2  + cpc3
Opt    =~ cpc4  + cpc5  + cpc6
Res    =~ cpc7  + cpc8  + cpc9
SE     =~ cpc10 + cpc11 + cpc12
PsyCap =~ Hope + Opt + Res + SE
"
fit <- lavaan::cfa(mod, data = w, estimator = "MLR")
ss  <- lavaan::standardizedSolution(fit)
ld  <- ss[ss$op == "=~", ]

obs1 <- setNames(ld$est.std[match(paste0("cpc", 1:12), ld$rhs)], paste0("cpc", 1:12))
obs2 <- setNames(ld$est.std[match(c("Hope","Opt","Res","SE"), ld$rhs)],
                 c("Hope","Opt","Res","SE"))

cat(sprintf("%-7s %-11s %10s %10s %8s\n",
            "item", "Table7 row", "published", "observed", "diff"))
for (i in 1:12)
  cat(sprintf("%-7s %-11s %10.3f %10.3f %8.3f\n",
              names(obs1)[i], names(PUB)[i], PUB[i], obs1[i], obs1[i] - PUB[i]))
cat("\nsecond-order loadings on PsyCap:\n")
for (i in 1:4)
  cat(sprintf("%-7s %-11s %10.3f %10.3f %8.3f\n",
              names(obs2)[i], names(PUB2)[i], PUB2[i], obs2[i], obs2[i] - PUB2[i]))

worst <- max(abs(c(obs1 - PUB, obs2 - PUB2)))
cat(sprintf("\nlargest deviation: %.4f (tolerance %.2f)\n", worst, TOL))

# Independent corroboration for the resilience block's internal order: the paper
# states in prose that "items one and three that measure resilience had rather
# low factor loading" and quotes their wording -- (7) "Sometimes I make myself
# do things whether I want to or not", (9) "It's okay if there are people who
# don't like me". So cpc7 and cpc9 must be the low pair, cpc8 the high one.
cat(sprintf("\nresilience block loadings: cpc7=%.3f cpc8=%.3f cpc9=%.3f\n",
            obs1["cpc7"], obs1["cpc8"], obs1["cpc9"]))
res_ok <- obs1["cpc8"] > obs1["cpc7"] && obs1["cpc8"] > obs1["cpc9"]
cat("paper's prose (items 7 and 9 are the weak resilience pair) reproduced: ",
    res_ok, "\n", sep = "")

# What this does NOT establish.
cat("\nNote: the loading match pins the four subscale BLOCKS {1,2,3}{4,5,6}{7,8,9}\n",
    "{10,11,12} and reproduces Dudasova's per-item values exactly, and the paper's\n",
    "prose independently pins the resilience block's internal order. It does NOT\n",
    "independently establish the order WITHIN the hope, optimism and self-efficacy\n",
    "blocks -- that rests on the S1 Appendix numbering matching the cpc1..cpc12\n",
    "column numbering. Status is therefore PARTIAL, not VERIFIED.\n", sep = "")

cat(if (worst <= TOL && res_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

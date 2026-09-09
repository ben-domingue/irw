# verify_meloni_2015_child_disab_knowledge.R
#
# mapping_basis = paper_order. The S2 File codebook (PLOS ONE 10.1371/journal.pone.0128876.s002,
# "Child's disability knowledge") prints 16 statements as two unnumbered lists -- 8 stereotypes
# (false) and 8 knowledge (true) -- and ties them to no code. The live item codes carry a
# content block and a keying letter (HK1-7_BELIEF_F, HK8-13_KNOW_T, HK14_SOCPART_F,
# HK15-16_SOCPART_T). The shipped mapping assigns the codebook's three social-participation
# statements to the three SOCPART codes and preserves the codebook's relative order inside
# each block.
#
# That is an ORDER inference, so it is checked here against the response data by the
# content predictions the mapping makes. Route 8 (semantic coherence of the response
# distribution) plus route 6 (keying polarity).

suppressMessages(library(irw))
TABLE <- "meloni_2015_child_disab_knowledge"

d <- irw::irw_fetch(TABLE)
m  <- tapply(d$resp, d$item, mean)
fl <- tapply(d$resp, d$item, function(x) 100 * mean(x == 1))

F_items <- c("HK1_BELIEF_F","HK2_BELIEF_F","HK3_BELIEF_F","HK4_BELIEF_F","HK5_BELIEF_F",
             "HK6_BELIEF_F","HK7_BELIEF_F","HK14_SOCPART_F")
T_items <- c("HK8_KNOW_T","HK9_KNOW_T","HK10_KNOW_T","HK11_KNOW_T","HK12_KNOW_T",
             "HK13_KNOW_T","HK15_SOCPART_T","HK16_SOCPART_T")

cat("per-item mean agreement (1 = disagree a lot ... 4 = agree a lot)\n")
ord <- order(m)
for (i in ord) cat(sprintf("  %-15s mean %.3f  floor%% %5.1f\n", names(m)[i], m[i], fl[names(m)[i]]))

ok <- logical(0); say <- function(lbl, pass, txt) { cat(sprintf("\n[%s] %s\n      %s\n", if (pass) "PASS" else "FAIL", lbl, txt)); ok <<- c(ok, pass) }

# P1 -- keying polarity (route 6). 8 false statements should attract less agreement than
# the 8 true ones, which is only true if the F/T split of the codebook lists matches the
# F/T split of the codes.
mF <- mean(m[F_items]); mT <- mean(m[T_items])
say("P1 keying polarity", mT > mF + 0.5,
    sprintf("false-keyed block mean %.3f vs true-keyed block mean %.3f (gap %.3f)", mF, mT, mT - mF))

# P2 -- HK3. Of the 8 false statements exactly one is COMPLIMENTARY ("all disabled persons
# are extraordinary people"); the other seven are derogatory or restrictive. It should be
# the most-endorsed false item by a clear margin.
others <- setdiff(F_items, "HK3_BELIEF_F")
say("P2 HK3_BELIEF_F = 'all disabled persons are extraordinary people'",
    m["HK3_BELIEF_F"] > max(m[others]) + 0.3,
    sprintf("HK3 mean %.3f vs next-highest false item %s %.3f (margin %.3f)",
            m["HK3_BELIEF_F"], names(which.max(m[others])), max(m[others]),
            m["HK3_BELIEF_F"] - max(m[others])))

# P3 -- HK2. The moral-blame statement ("if a person becomes disabled it is because she was
# bad") should be the most rejected of all 16 items, on both mean and floor%.
say("P3 HK2_BELIEF_F = 'if a person becomes disabled it is because she was bad'",
    names(which.min(m)) == "HK2_BELIEF_F" && names(which.max(fl)) == "HK2_BELIEF_F",
    sprintf("lowest mean is %s (%.3f, next %.3f); highest floor%% is %s (%.1f%%)",
            names(which.min(m)), min(m), sort(m)[2], names(which.max(fl)), max(fl)))

# P4 -- the two SOCPART_T codes. HK16 is the familiar accessibility fact (acoustic traffic
# signal for blind pedestrians); HK15 is the exclusionary claim (only disabled athletes
# attend the Paralympics). Agreement should be higher for HK16.
say("P4 HK16 (acoustic traffic signal) > HK15 (Paralympics only for disabled athletes)",
    m["HK16_SOCPART_T"] > m["HK15_SOCPART_T"] + 0.2,
    sprintf("HK16 %.3f vs HK15 %.3f (gap %.3f)", m["HK16_SOCPART_T"], m["HK15_SOCPART_T"],
            m["HK16_SOCPART_T"] - m["HK15_SOCPART_T"]))

cat("\nWhat this does NOT establish: the order WITHIN the runs of statistically\n",
    "indistinguishable items. HK4/HK6/HK7 sit at 1.780/1.676/1.757 and HK9/HK13 at\n",
    "2.555/2.539 -- gaps of 0.02-0.10, far inside sampling error at n=73-76 -- so a swap\n",
    "inside either run would not be detected here. The mapping is PARTIAL, not VERIFIED.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

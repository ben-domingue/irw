# verify_komura_2026_gqs_anthropomorphism.R
#
# CLAIM UNDER TEST. The item text shipped for this table comes from S2 File of
# Komura & Yamada (2026), PLOS ONE 10.1371/journal.pone.0340449, which prints the
# questionnaire screens with the five GQS subscales, each item numbered inside its
# subscale block:
#
#   Anthropomorphism:  1. Machine-like <-> Human-like
#                      2. Artificial   <-> Natural
#                      3. Unconscious  <-> Conscious
#                      4. Still        <-> Lively
#                      5. Mechanical   <-> Organic
#
# The mapping asserted is that S2's "Anthropomorphism: n" is S3 File's column
# gqs_anthropomorphism_n, which data/komura_2026_godspeed.py melts verbatim into
# the live `item`. This script tests three consequences of that claim.
#
# WHAT IT DOES NOT ESTABLISH is stated in the output and repeated here: nothing
# below separates items 1, 2, 3 and 5 from one another. Status is PARTIAL.

suppressMessages({library(irw); library(readxl)})

TABLE <- "komura_2026_gqs_anthropomorphism"
URL <- paste0("https://journals.plos.org/plosone/article/file",
              "?type=supplementary&id=10.1371/journal.pone.0340449.s003")

tmp <- tempfile(fileext = ".xlsx")
utils::download.file(URL, tmp, quiet = TRUE, mode = "wb",
                     headers = c("User-Agent" = "IRW-itemtext/1.0"))
q <- as.data.frame(readxl::read_excel(tmp, sheet = "questionnaires"))

live <- irw::irw_fetch(TABLE)

## ---- Bridge: the S3 column really is the live item (not itself the evidence) ----
cat("== Bridge: live item vs S3 File column, response-frequency match ==\n")
bridge_ok <- TRUE
for (i in 1:5) {
    it <- paste0("gqs_anthropomorphism_", i)
    lv <- table(factor(live$resp[live$item == it], levels = 1:5))
    sv <- table(factor(q[[it]], levels = 1:5))
    same <- identical(as.vector(lv), as.vector(sv))
    bridge_ok <- bridge_ok && same
    cat(sprintf("  %-24s live %-18s src %-18s %s\n", it,
                paste(as.vector(lv), collapse = "/"),
                paste(as.vector(sv), collapse = "/"),
                if (same) "match" else "MISMATCH"))
}

## ---- Test 1: block sizes. S2's five blocks are 5/5/5/5/3 items ----
cat("\n== Test 1: S2 subscale block sizes vs S3 column blocks ==\n")
S2_SIZES <- c(anthropomorphism = 5, animacy = 5, likeability = 5,
              perceived_intelligence = 5, perceived_safety = 3)
obs_sizes <- sapply(names(S2_SIZES), function(p)
    sum(grepl(paste0("^gqs_", p, "_\\d+$"), names(q))))
for (p in names(S2_SIZES))
    cat(sprintf("  %-24s S2 %d  S3 %d  %s\n", p, S2_SIZES[[p]], obs_sizes[[p]],
                if (S2_SIZES[[p]] == obs_sizes[[p]]) "match" else "MISMATCH"))
t1 <- all(as.integer(S2_SIZES) == as.integer(obs_sizes))
cat("  -> pins the anthropomorphism BLOCK (incl. the non-standard 3-item safety\n",
    "     block, which a mis-aligned block reading would break). Says nothing\n",
    "     about order WITHIN the block.\n", sep = "")

## ---- Test 2: scale direction, resp 1 = left anchor ----
# S2 marks perceived_safety items 2 and 3 "(reversed item)": Calm<->Agitated and
# Peaceful<->Surprised put the unfavourable pole on the RIGHT, while item 1
# (Anxious<->Calm) puts it on the left. If resp 1 = left anchor / 5 = right
# anchor, items 2 and 3 must sit well BELOW item 1. If the coding ran the other
# way the pattern inverts. This is the shipped option_text mapping (anchor at 1
# and 5) for the whole GQS block, anthropomorphism included.
cat("\n== Test 2: response direction, from S2's reversed-item flags ==\n")
ps <- sapply(1:3, function(i) mean(q[[paste0("gqs_perceived_safety_", i)]], na.rm = TRUE))
cat(sprintf("  perceived_safety_1 (Anxious<->Calm, not reversed) mean %.2f\n", ps[1]))
cat(sprintf("  perceived_safety_2 (Calm<->Agitated, REVERSED)    mean %.2f\n", ps[2]))
cat(sprintf("  perceived_safety_3 (Peaceful<->Surprised, REVERSED) mean %.2f\n", ps[3]))
t2 <- ps[1] > ps[2] && ps[1] > ps[3]
cat(sprintf("  -> item 1 above both reversed items by %.2f / %.2f: consistent with\n",
            ps[1] - ps[2], ps[1] - ps[3]))
cat("     resp 1 = left anchor, resp 5 = right anchor. Fixes the DIRECTION of\n",
    "     option_text for every GQS item; does not identify any item.\n", sep = "")

## ---- Test 3: item 4 is the liveliness item ("Still <-> Lively") ----
# Of the five anthropomorphism anchors, only #4 is about being animate/active.
# The animacy block's activity items (Stagnant<->Lively, Inactive<->Active,
# Unresponsive<->Responsive, Sleepy<->Awake) are the same content. So after
# partialling out the anthropomorphism block itself, item 4 should retain the
# strongest residual association with the animacy activity mean.
cat("\n== Test 3: which anthropomorphism item carries liveliness content ==\n")
act <- rowMeans(q[, paste0("gqs_animacy_", 2:5)], na.rm = TRUE)
pr <- numeric(5)
for (i in 1:5) {
    y  <- q[[paste0("gqs_anthropomorphism_", i)]]
    oth <- rowMeans(q[, paste0("gqs_anthropomorphism_", setdiff(1:5, i))], na.rm = TRUE)
    ry <- residuals(lm(y ~ oth)); ra <- residuals(lm(act ~ oth))
    pr[i] <- cor(ry, ra)
    cat(sprintf("  gqs_anthropomorphism_%d  partial r with animacy activity mean = %+.3f\n", i, pr[i]))
}
t3 <- which.max(pr) == 4 && (sort(pr, decreasing = TRUE)[1] - sort(pr, decreasing = TRUE)[2]) > 0.10
cat(sprintf("  -> max at item %d (%.3f), next %.3f. Item 4 is the shipped\n",
            which.max(pr), max(pr), sort(pr, decreasing = TRUE)[2]))
cat("     'Still <-> Lively'. Pins item 4 only.\n")

cat("\nNOT ESTABLISHED: items 1, 2, 3 and 5 are not separated from one another by\n",
    "any test here. Their order rests on S2 File's explicit numbering alone, which\n",
    "is why this table is recorded PARTIAL rather than VERIFIED.\n", sep = "")

cat(if (bridge_ok && t1 && t2 && t3) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

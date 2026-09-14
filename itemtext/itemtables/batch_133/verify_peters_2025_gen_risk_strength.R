# Step 5b verification for peters_2025_gen_risk_strength.
#
# CLAIM UNDER TEST: the three item codes die / hospital / symptoms carry the
# Generic Belief expectancy stems taken from the study's own operationalization
# sheet (v1/operationalizations/sheets/DMQs.xlsx, sheet `en`), i.e.
#   die      -> "If I get infected with the coronavirus, I will ..."
#               1 = "certainly not die"                 .. 5 = "certainly die"
#   hospital -> "If I get infected with the coronavirus, I will ..."
#               1 = "certainly not end up in a hospital".. 5 = "certainly end up in a hospital"
#   symptoms -> "If I get infected with the coronavirus, I will get ..."
#               1 = "no symptoms"                       .. 5 = "severe symptoms"
#
# Route 8 (semantic coherence of the response distribution). The three anchors
# name three nested COVID-19 outcomes of strictly decreasing severity/base rate:
# dying implies hospitalisation implies symptoms. Any respondent sample must
# therefore endorse them in the order symptoms > hospital > die, both in mean
# and (inversely) in the % sitting on the "nothing happens to me" floor. With
# only three items a strict ordering on BOTH statistics pins each item to a
# distinct position -- there is no permutation of the three texts other than the
# shipped one that satisfies it. This also checks the option->resp direction:
# if 1 and 5 were swapped the ordering would invert.

suppressMessages(library(irw))

TABLE <- "peters_2025_gen_risk_strength"
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

items <- c("die", "hospital", "symptoms")
m  <- tapply(d$resp, d$item, mean)[items]
fl <- tapply(d$resp, d$item, function(v) 100 * mean(v == min(d$resp)))[items]
n  <- tapply(d$resp, d$item, length)[items]

cat(sprintf("%-9s %6s %8s %10s\n", "item", "n", "mean", "floor%(resp=1)"))
for (i in items) cat(sprintf("%-9s %6d %8.2f %10.1f\n", i, n[i], m[i], fl[i]))

ord_mean  <- m[["symptoms"]] > m[["hospital"]] && m[["hospital"]] > m[["die"]]
ord_floor <- fl[["symptoms"]] < fl[["hospital"]] && fl[["hospital"]] < fl[["die"]]

cat(sprintf("\nmean ordering  symptoms > hospital > die : %.2f > %.2f > %.2f  -> %s\n",
            m[["symptoms"]], m[["hospital"]], m[["die"]], ord_mean))
cat(sprintf("floor ordering symptoms < hospital < die : %.1f < %.1f < %.1f  -> %s\n",
            fl[["symptoms"]], fl[["hospital"]], fl[["die"]], ord_floor))

cat("\nWhat this does NOT establish: it is a severity-ordering argument, not a\n",
    "per-item textual match. It does not confirm the exact English wording of the\n",
    "stems or anchors (that comes from DMQs.xlsx `en` and the LimeSurvey .lss, and\n",
    "is not testable from the response data), and it does not pin the unlabelled\n",
    "midpoints 2-4, which are shipped blank because the instrument labels only the\n",
    "endpoints.\n", sep = "")

cat(if (ord_mean && ord_floor) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

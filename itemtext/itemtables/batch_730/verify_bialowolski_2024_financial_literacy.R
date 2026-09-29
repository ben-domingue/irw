# verify_bialowolski_2024_financial_literacy.R -- Step 5b, batch_730.
#
# Claim: FL_n <-> appendix Qn for n = 1..17, and FL_19 <-> Q18 (FL_18 absent
# from the deposit). The item codes ARE the Stata column names (pattern 1), but
# the Stata labels only say "Poprawnosc odpowiedzi : FL_n" -- they carry no
# wording, and the appendix numbers Q1..Q18, so the FL->Q tie is an inference.
# The paper (Cwynar et al. 2025, IJCS 10.1111/ijcs.70083) is closed and gave
# 403 to every route tried, so there are no published per-item statistics.
# Routes used: 8 (semantic coherence of difficulty) and content-pair structure
# in the inter-item correlation matrix. resp is 0/1 correctness.
#
# What this does NOT establish: the order among items that share no pairing
# and no distinctive difficulty (e.g. FL_3/FL_4/FL_9/FL_11 are not
# individually pinned), and it cannot exclude that FL_19 is a question absent
# from the appendix rather than Q18 -- it only shows FL_19 behaves like a
# risk/return item. Hence PARTIAL, not VERIFIED.
suppressMessages(library(irw))
TABLE <- "bialowolski_2024_financial_literacy"
d <- irw::irw_fetch(TABLE)
w <- reshape(as.data.frame(d[, c("id", "item", "resp")]), idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
items <- c(paste0("FL_", 1:17), "FL_19")
w <- w[, items]
m <- colMeans(w, na.rm = TRUE)
cat("Per-item proportion correct:\n"); print(round(m, 3))
R <- cor(w, use = "pairwise.complete.obs"); diag(R) <- NA
top <- function(i, k = 3) names(sort(R[i, ], decreasing = TRUE))[1:k]
ok <- logical(0)

# 1. Q16 "inflation means cost of living rises" -> easiest item
cat("\n1. easiest item:", names(which.max(m)), sprintf("(%.3f)", max(m)), "expect FL_16\n")
ok["Q16"] <- names(which.max(m)) == "FL_16"
# 2. Q2 (bond prices) and Q10 (PLN 30 minimum payment = interest, never paid off) -> two hardest
h2 <- names(sort(m))[1:2]
cat("2. two hardest:", h2, sprintf("(%.3f, %.3f)", m[h2[1]], m[h2[2]]), "expect FL_2, FL_10\n")
ok["Q2Q10"] <- setequal(h2, c("FL_2", "FL_10"))
# 3. Q1 and Q12 are both inflation-vs-purchasing-power ('less than today') -> strongest pair
idx <- which(R == max(R, na.rm = TRUE), arr.ind = TRUE)[1, ]
pr <- sort(c(rownames(R)[idx[1]], colnames(R)[idx[2]]))
cat("3. strongest pair:", pr, sprintf("r=%.3f", max(R, na.rm = TRUE)), "expect FL_1, FL_12\n")
ok["Q1Q12"] <- setequal(pr, c("FL_1", "FL_12"))
# 4. Q13/Q14 open-ended simple-interest numeracy; Q15 continues Q14's PLN 100 scenario
cat("4. top partners FL_13:", top("FL_13"), "| FL_15:", top("FL_15"),
    sprintf("| r(13,14)=%.3f r(14,15)=%.3f\n", R["FL_13", "FL_14"], R["FL_14", "FL_15"]))
ok["Q13Q14"] <- top("FL_13", 1) == "FL_14"
ok["Q14Q15"] <- top("FL_15", 1) == "FL_14"
# 5. Q5 and Q17 are the two diversification items
cat("5. top partners FL_5:", top("FL_5"), "| FL_17:", top("FL_17"),
    sprintf("| r(5,17)=%.3f\n", R["FL_5", "FL_17"]))
ok["Q5Q17"] <- top("FL_5", 1) == "FL_17" && "FL_5" %in% top("FL_17", 2)
# 6. Q18 (risk-return) should align with the risk/investment block, not the arithmetic block
risk <- c("FL_3", "FL_4", "FL_5", "FL_6", "FL_11", "FL_17")
cat("6. top partners FL_19:", top("FL_19"), "; expect >= 2 of top-3 in", risk, "\n")
ok["Q18"] <- sum(top("FL_19") %in% risk) >= 2
# 7. Q7 (total interest, 30y) and Q8 (monthly instalment, 15y): mutual partners in the arithmetic block
cat(sprintf("7. r(7,8)=%.3f; FL_7 top: %s\n", R["FL_7", "FL_8"], paste(top("FL_7"), collapse = " ")))
cat("\nchecks:\n"); print(ok)
cat("NOT established: order among unpaired mid-difficulty items (FL_3, FL_4, FL_6, FL_7, FL_8, FL_9, FL_11);",
    "that FL_19 is Q18 rather than an unlisted question.\n")
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

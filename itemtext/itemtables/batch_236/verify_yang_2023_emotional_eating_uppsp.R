# verify_yang_2023_emotional_eating_uppsp.R
#
# CLAIM UNDER TEST. data/yang_2023_emotional_eating.py assigns this table's item
# codes POSITIONALLY: upps_cols = [c for c in cols if c.startswith("@12")] and
# then UPPSP_<i> = the i-th of those 20 columns of the PLOS S1 Data workbook
# (journal.pone.0280701.s001). The shipped item_text for UPPSP_2..UPPSP_20 is
# that column's own header with its "@12,<i>. " export prefix stripped, so the
# mapping is only right if the positional reconstruction reproduces the live
# table column for column.
#
# ROUTE A (primary, Step 5b route 9 applied to the item axis): per-item
# response-frequency matching. 20 items x 4 levels = 80 cells compared between
# the live IRW table and the reconstructed source columns. All 20 source
# count-vectors are distinct, so a full match separates EVERY item from every
# other item -- swapping any two items' text would break four cells.
#
# ROUTE B (corroboration, Step 5b route 3): the raw column sum of exactly these
# 20 columns must reproduce the workbook's own pre-computed "SUPPSP" total, and
# its Cronbach's alpha and its correlations with the workbook's EESR / CESD /
# DERS totals must reproduce the four statistics the paper publishes
# (alpha .834; r = .382 with emotional eating, .422 with depressive symptoms,
# .473 with difficulties in emotion regulation).
#
# ROUTE C (option axis + one item's identity, printed, part of the verdict):
#   C1. The paper's Measures section states "Responses to questions ranged from
#       1 (strongly agree) to 4 (strongly disagree)". The shipped option_text
#       assigns those two endpoint labels the OTHER way round (1 = strongly
#       disagree, 4 = strongly agree), on the evidence that the four canonical
#       negative-urgency items {6,8,13,15} correlate POSITIVELY with the
#       workbook's depression total. Under the paper's parenthetical the same
#       number would mean "strongly disagrees that he acts without thinking when
#       upset", which cannot be the pole that tracks depression. The same
#       sentence's own interpretive clause ("higher scores indicating stronger
#       negative urgency") agrees with the data, not with its parenthetical.
#   C2. UPPSP_1's source header is the block instruction with the item's own
#       label truncated to "I", so its wording is assigned by elimination:
#       headers 2..20 are the canonical SUPPS-P items 2..20 and cover
#       {2,5,12,19} premeditation, {6,8,13,15} negative urgency, {9,14,16,18}
#       sensation seeking, {3,10,17,20} positive urgency and only THREE of the
#       four perseverance items {4,7,11}. The missing one is canonical item 1,
#       "I generally like to see things through to the end." The data agree:
#       UPPSP_1's single largest correlate is UPPSP_11 ("I will finish it well
#       as soon as I start").
#
# WHAT THIS DOES NOT ESTABLISH: routes A and B pin the item CODE to its source
# COLUMN for all 20 items, and 19 of those columns carry their own wording. They
# say nothing about UPPSP_1's words (route C2 is an elimination argument, not a
# source) and nothing about the two middle response levels, which ship blank.

suppressMessages({library(irw); library(readxl)})

TABLE  <- "yang_2023_emotional_eating_uppsp"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file?",
                 "type=supplementary&id=10.1371/journal.pone.0280701.s001")

xlsx   <- ".cache/yang_2023_emotional_eating_uppsp/s001.xlsx"
if (!file.exists(xlsx)) {
    xlsx <- file.path(tempdir(), "yang2023_s1.xlsx")
    download.file(SI_URL, xlsx, mode = "wb", quiet = TRUE)
}

raw   <- suppressMessages(readxl::read_excel(xlsx))
hdr   <- names(raw)
block <- grep("^@12", hdr, value = TRUE)
stopifnot(length(block) == 20)

# header-embedded numbering == position, for the 19 numbered headers
nums <- as.integer(sub("^@12[.,]\\s*(\\d+).*$", "\\1", block[-1]))
cat("header numbering: @12,<n> equals its position for", sum(nums == 2:20),
    "of 19 numbered headers (item 1's header is the block instruction with the",
    "item label truncated to \"I\", so its position is fixed by elimination)\n\n")

src <- as.data.frame(raw[, block]); names(src) <- paste0("UPPSP_", 1:20)
X   <- sapply(src, function(x) suppressWarnings(as.numeric(x)))

d  <- irw::irw_fetch(TABLE)
lv <- paste0("UPPSP_", 1:20)
live_tab <- table(factor(d$item, levels = lv), factor(d$resp, levels = 1:4))
src_tab  <- t(sapply(1:20, function(j) sapply(1:4, function(k) sum(X[, j] == k, na.rm = TRUE))))

cat("-- ROUTE A: per-item response counts, live vs positional reconstruction --\n")
cat(sprintf("%-9s %-18s %-18s %s\n", "item", "live 1,2,3,4", "source 1,2,3,4", "ok"))
ok <- logical(20)
for (i in 1:20) {
    l <- as.integer(live_tab[i, ]); s <- as.integer(src_tab[i, ])
    ok[i] <- identical(l, s)
    cat(sprintf("%-9s %-18s %-18s %s\n", lv[i], paste(l, collapse = ","),
                paste(s, collapse = ","), if (ok[i]) "MATCH" else "MISMATCH"))
}
uniq <- length(unique(apply(src_tab, 1, paste, collapse = ",")))
cat(sprintf("\ncells matched: %d of 80; items matched: %d of 20\n",
            sum(live_tab == src_tab), sum(ok)))
cat(sprintf("distinct count-vectors among the 20 source columns: %d of 20 -- %s\n\n",
            uniq, if (uniq == 20)
              "no two items share a response distribution, so this route separates every item"
            else "some items are indistinguishable by this route"))

cat("-- ROUTE B: the block's raw sum against the workbook total and the paper --\n")
tot   <- suppressWarnings(as.numeric(raw[["SUPPSP"]]))
s_raw <- rowSums(X)
n_tot <- sum(tot == s_raw, na.rm = TRUE)
cat(sprintf("raw sum of the 20 columns == workbook 'SUPPSP' column for %d of %d respondents\n",
            n_tot, sum(!is.na(tot))))
alpha <- 20/19 * (1 - sum(apply(X, 2, var)) / var(s_raw))
rr <- c(EESR = cor(s_raw, suppressWarnings(as.numeric(raw[["EESR"]]))),
        CESD = cor(s_raw, suppressWarnings(as.numeric(raw[["CESD"]]))),
        DERS = cor(s_raw, suppressWarnings(as.numeric(raw[["DERS"]]))))
PUB <- c(EESR = 0.382, CESD = 0.422, DERS = 0.473)
cat(sprintf("Cronbach's alpha  observed %.3f   published %.3f\n", alpha, 0.834))
for (g in names(rr))
    cat(sprintf("r(UPPS-P, %-4s)  observed %+0.3f  published %+0.3f\n", g, rr[g], PUB[g]))
b_ok <- n_tot == sum(!is.na(tot)) && abs(alpha - 0.834) < 0.01 && max(abs(rr - PUB)) < 0.005
cat("\n")

cat("-- ROUTE C1: which numeric code is 'strongly agree' --\n")
cesd <- suppressWarnings(as.numeric(raw[["CESD"]]))
grp  <- list(NegUrgency = c(6, 8, 13, 15), Perseverance = c(1, 4, 7, 11),
             Premeditation = c(2, 5, 12, 19), SensationSeeking = c(9, 14, 16, 18),
             PositiveUrgency = c(3, 10, 17, 20))
for (g in names(grp)) {
    s <- rowSums(X[, grp[[g]]])
    cat(sprintf("%-17s items %-12s mean/item %.2f   r(depression) = %+0.3f\n",
                g, paste(grp[[g]], collapse = ","), mean(s) / 4, cor(s, cesd)))
}
nu <- cor(rowSums(X[, grp$NegUrgency]), cesd)
cat(sprintf("\nnegative urgency r(depression) = %+0.3f: the HIGH codes are the agreeing pole,\n", nu))
cat("so 4 = strongly agree and 1 = strongly disagree, the reverse of the paper's parenthetical.\n\n")

cat("-- ROUTE C2: UPPSP_1's identity by elimination --\n")
cm <- cor(X, use = "pairwise")
cat("UPPSP_1's correlations, largest first:\n")
print(round(sort(cm[1, -1], decreasing = TRUE), 3))
cat(sprintf("\nmean r with the three canonical perseverance mates {4,7,11}: %+0.3f\n",
            mean(cm[1, c(4, 7, 11)])))
cat(sprintf("mean r with the other 16 items:                              %+0.3f\n",
            mean(cm[1, setdiff(2:20, c(4, 7, 11))])))
c2_ok <- names(which.max(cm[1, -1])) == "UPPSP_11" &&
         mean(cm[1, c(4, 7, 11)]) > mean(cm[1, setdiff(2:20, c(4, 7, 11))])

cat("\n")
pass <- all(ok) && uniq == 20 && b_ok && nu > 0.3 && c2_ok
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

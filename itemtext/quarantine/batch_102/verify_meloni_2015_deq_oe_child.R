# verify_meloni_2015_deq_oe_child.R -- Step 5b, re-runnable evidence.
#
# CLAIM UNDER TEST. Each of the 36 items is a CODED CATEGORY COUNT, not a
# question: the child gave one free-text answer per stimulus and two blind
# coders scored how many expressions in it fell into each of nine
# disability-model categories. The IRW code splits as
# DEQ_OE_<stimulus>_<model>, and this script tests the two halves of that
# reading against the live data:
#
#   stimulus: MD = Giovanni in a wheelchair (motor), SD = Maria blind
#             (sensory), CD = Paolo autistic (cognitive), ND = Elena, an
#             able-bodied person (no disability)
#   model:    Eth ethical, Est aesthetic, Rel religious, Med medical,
#             Env environmental, SRel socio-relational, Bio biopsychosocial,
#             Oth other, Idont "I don't know"
#             (S2 File codebook, criteria list 1..9, in that order)
#
# What would break if the mapping were wrong: the content predictions P1-P5
# below, and -- decisively for the macro-model grouping -- P6, which rebuilds
# the codebook's own 0-3 presence score and must reproduce the article's
# published claim about the children.

suppressMessages(library(irw))
TABLE <- "meloni_2015_deq_oe_child"

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)
STIM  <- c("MD", "SD", "CD", "ND")
MODEL <- c("Eth", "Est", "Rel", "Med", "Env", "SRel", "Bio", "Oth", "Idont")
code  <- function(s, m) paste0("DEQ_OE_", s, "_", m)
mu    <- tapply(d$resp, d$item, mean)
tot   <- tapply(d$resp, d$item, sum)
M     <- outer(STIM, MODEL, Vectorize(function(s, m) mu[[code(s, m)]]))
dimnames(M) <- list(STIM, MODEL)

cat("=== per-item mean coded-mention count (rows = stimulus, cols = model) ===\n")
print(round(M, 3))
cat("\n")

ok <- logical(0); say <- function(lbl, pass, txt) {
    cat(sprintf("%-4s %-6s %s\n", lbl, if (pass) "PASS" else "FAIL", txt))
    ok[[length(ok) + 1L]] <<- pass
}

# P1 -- the medical model is the modal category for every stimulus.
top <- MODEL[apply(M, 1, which.max)]
say("P1", all(top == "Med"),
    sprintf("Med is the top category in %d/4 sections (tops: %s)",
            sum(top == "Med"), paste(STIM, top, sep = "=", collapse = " ")))

# P2 -- and it collapses for the ONE stimulus with no disability.
say("P2", M["ND", "Med"] < 0.5 * min(M[c("MD","SD","CD"), "Med"]),
    sprintf("Med: MD %.3f, SD %.3f, CD %.3f vs able-bodied ND %.3f",
            M["MD","Med"], M["SD","Med"], M["CD","Med"], M["ND","Med"]))

# P3 -- "why does a normal person have difficulties?" is the question that
#       draws unclassifiable answers and outright ignorance.
say("P3", which.max(M[, "Oth"]) == 4 && which.max(M[, "Idont"]) == 4,
    sprintf("Oth peaks at ND (%.3f vs %.3f/%.3f/%.3f); Idont peaks at ND (%.3f vs %.3f/%.3f/%.3f)",
            M["ND","Oth"], M["MD","Oth"], M["SD","Oth"], M["CD","Oth"],
            M["ND","Idont"], M["MD","Idont"], M["SD","Idont"], M["CD","Idont"]))

# P4 -- Paolo is described as failing to understand what others say, so the
#       socio-relational reading should lead among the three disabilities.
say("P4", M["CD","SRel"] > M["MD","SRel"] && M["CD","SRel"] > M["SD","SRel"],
    sprintf("SRel among the disability stimuli: CD %.3f > MD %.3f, SD %.3f",
            M["CD","SRel"], M["MD","SRel"], M["SD","SRel"]))

# P5 -- the three blame/appearance/fate categories are all but unused, which
#       is the article's own headline about children.
blame <- sum(tot[code(rep(STIM, each = 3), rep(c("Eth","Est","Rel"), 4))])
med   <- sum(tot[code(STIM, "Med")])
say("P5", blame < 0.05 * med,
    sprintf("Eth+Est+Rel total %d coded mentions across all 4 stimuli vs Med %d",
            blame, med))

# P6 -- DECISIVE for the macro-model grouping. The S2 codebook scores the
# individual model as PRESENCE of any of {Eth, Est, Rel, Med} and the social
# model as presence of any of {Env, SRel}, each counted over the three
# DISABILITY stimuli only, giving 0-3; a respondent "prefers" a model at > 1.5.
# The article reports: "Almost all of the children preferred the individual
# model" (and the OE typology puts essentially none in social-only).
ids <- sort(unique(d$id))
W <- matrix(0, nrow = length(ids), ncol = length(unique(d$item)),
            dimnames = list(as.character(ids), sort(unique(d$item))))
W[cbind(as.character(d$id), as.character(d$item))] <- d$resp
w <- W
g  <- function(s, m) W[, code(s, m)]
pres <- function(ms) rowSums(sapply(c("MD","SD","CD"),
            function(s) as.integer(rowSums(sapply(ms, function(m) g(s, m))) > 0)))
IND <- pres(c("Eth","Est","Rel","Med")); SOC <- pres(c("Env","SRel"))
p_ind  <- mean(IND > 1.5 & SOC <= 1.5)
p_soc  <- mean(SOC > 1.5 & IND <= 1.5)
p_both <- mean(IND > 1.5 & SOC > 1.5)
cat(sprintf("\nP6 typology (n = %d children): individual-only %.1f%%, social-only %.1f%%, both %.1f%%, neither %.1f%%\n",
            nrow(W), 100*p_ind, 100*p_soc, 100*p_both,
            100*mean(IND <= 1.5 & SOC <= 1.5)))
say("P6", p_ind > 0.85 && p_soc < 0.02,
    sprintf("individual-only %.1f%% (article: \"almost all of the children preferred the individual model\"), social-only %.1f%%",
            100*p_ind, 100*p_soc))

# P7 -- falsification. Swap the two macro-model memberships and the same
# computation must NOT reproduce the article.
IND2 <- pres(c("Env","SRel")); SOC2 <- pres(c("Eth","Est","Rel","Med"))
p_ind2 <- mean(IND2 > 1.5 & SOC2 <= 1.5)
say("P7", p_ind2 < 0.05,
    sprintf("with Env/SRel read as the individual model instead, individual-only falls to %.1f%% -- the grouping is not interchangeable",
            100*p_ind2))

cat("\nWhat this does NOT establish: the data cannot separate Eth from Est.\n",
    "Across all 4 stimuli x 76 children there are ", sum(tot[code(STIM,"Eth")]),
    " ethical and ", sum(tot[code(STIM,"Est")]), " aesthetic coded mentions, so no\n",
    "distributional route could tell those two suffixes apart. They are separated\n",
    "instead by the suffix names themselves and by the S1 workbook's column order\n",
    "(Eth, Est, Rel, Med, Env, SRel, Bio, Oth, Idont), which reproduces the S2\n",
    "codebook's numbered criteria list 1..9 exactly.\n", sep = "")

cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

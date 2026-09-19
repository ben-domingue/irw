# verify_meloni_2015_deq_oe_child.R -- Step 5b, re-runnable evidence. batch_103.
#
# WHAT IS BEING VERIFIED. Each of the 36 items is a CODED-MENTION COUNT, not a
# question the child answered. A child gave one free-text answer per stimulus;
# two blind coders scored how many expressions in that answer fell into each of
# nine disability-model categories. The IRW code reads DEQ_OE_<stimulus>_<model>
# and the shipped mapping claims:
#
#   stimulus  MD = Giovanni, in a wheelchair (motor)      SD = Maria, blind (sensory)
#             CD = Paolo, autistic (cognitive)            ND = Elena, a normal person
#   model     Eth ethical, Est aesthetic, Rel religious, Med medical, Env
#             environmental, SRel socio-relational, Bio biopsychosocial, Oth other,
#             Idont "I don't know"   (S2 File codebook criteria list 1..9, in order)
#
# ROUTE 3 (published subscale means) is the decisive half and is what makes this
# more than a plausibility argument. Fig 1 of the article (journal.pone.0128876.g001,
# "Mean frequency preference for the three disability models by age group") prints
# six numbers for the children. The codebook defines those composites in terms of
# the very suffixes under test: individual = presence of ANY of {Eth, Est, Rel,
# Med}, social = presence of ANY of {Env, SRel}, each counted over the THREE
# disability stimuli only (0-3); biopsychosocial is Bio the same way. So the six
# published numbers are a falsifiable prediction about which suffix belongs to
# which macro-model and about which stimulus is the able-bodied one.
#
# ROUTE 8 (semantic coherence) then separates categories inside those groups.

suppressMessages(library(irw))
TABLE <- "meloni_2015_deq_oe_child"

# Article Fig 1, read from the published PNG. Rows = macro-model, cols = age group.
PUBLISHED <- rbind(Individual      = c(`6-8` = 2.92, `9-11` = 2.86),
                   Social          = c(0.07, 0.60),
                   Biopsychosocial = c(0.10, 0.18))
TOL <- 0.05

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
STIM  <- c("MD", "SD", "CD", "ND")
MODEL <- c("Eth", "Est", "Rel", "Med", "Env", "SRel", "Bio", "Oth", "Idont")
cd    <- function(s, m) paste0("DEQ_OE_", s, "_", m)

ids <- sort(unique(d$id)); its <- sort(unique(d$item))
W <- matrix(0, length(ids), length(its), dimnames = list(as.character(ids), its))
W[cbind(as.character(d$id), d$item)] <- d$resp
age <- tapply(d$cov_age, d$id, function(x) x[1])[as.character(ids)]
grp <- ifelse(age <= 8, "6-8", "9-11")

mu  <- tapply(d$resp, d$item, mean)
tot <- tapply(d$resp, d$item, sum)
M   <- outer(STIM, MODEL, Vectorize(function(s, m) mu[[cd(s, m)]]))
dimnames(M) <- list(STIM, MODEL)

cat("=== per-item mean coded-mention count (rows = stimulus, cols = model) ===\n")
print(round(M, 3)); cat("\n")

ok <- logical(0)
say <- function(lbl, pass, txt) {
    cat(sprintf("%-4s %-4s %s\n", lbl, if (pass) "PASS" else "FAIL", txt))
    ok[[length(ok) + 1L]] <<- pass
}

## ---- ROUTE 3 -------------------------------------------------------------
# Codebook: "When the presence of at least one of the ethical, aesthetic,
# religious, or medical models was detected, then the presence of the individual
# model had to be checked. When the presence of at least one of the socio-
# environmental or socio-relational models was detected, then the presence of the
# social model had to be checked." Scored 0-3 over the disability conditions.
DIS <- c("MD", "SD", "CD")
pres <- function(ms) rowSums(sapply(DIS, function(s)
            as.integer(rowSums(W[, cd(s, ms), drop = FALSE]) > 0)))
OBS <- rbind(Individual      = tapply(pres(c("Eth", "Est", "Rel", "Med")), grp, mean),
             Social          = tapply(pres(c("Env", "SRel")),               grp, mean),
             Biopsychosocial = tapply(pres("Bio"),                          grp, mean))
OBS <- OBS[, c("6-8", "9-11")]

cat("=== ROUTE 3: article Fig 1 vs recomputed composites (n = ",
    sum(grp == "6-8"), " aged 6-8, ", sum(grp == "9-11"), " aged 9-11) ===\n", sep = "")
cat(sprintf("%-16s %18s %18s\n", "", "6-8 pub/obs", "9-11 pub/obs"))
for (i in 1:3)
    cat(sprintf("%-16s %8.2f %8.3f  %8.2f %8.3f\n", rownames(OBS)[i],
                PUBLISHED[i, 1], OBS[i, 1], PUBLISHED[i, 2], OBS[i, 2]))
worst <- max(abs(OBS - PUBLISHED))
say("R3", worst <= TOL,
    sprintf("all 6 published Fig 1 values reproduced, largest deviation %.3f (tol %.2f)",
            worst, TOL))

# Falsification: the grouping must not be interchangeable. Swap the individual and
# social memberships and the same computation must miss Fig 1 badly.
SW <- rbind(Individual      = tapply(pres(c("Env", "SRel")),               grp, mean),
            Social          = tapply(pres(c("Eth", "Est", "Rel", "Med")),  grp, mean),
            Biopsychosocial = tapply(pres("Bio"),                          grp, mean))[, c("6-8", "9-11")]
say("R3x", max(abs(SW - PUBLISHED)) > 1,
    sprintf("with Env/SRel read as the individual model instead, largest deviation is %.2f -- not interchangeable",
            max(abs(SW - PUBLISHED))))

# And ND must be the able-bodied stimulus the composite EXCLUDES: including it
# (0-4 scale) would overshoot the published 0-3 individual figure.
pres4 <- function(ms) rowSums(sapply(STIM, function(s)
             as.integer(rowSums(W[, cd(s, ms), drop = FALSE]) > 0)))
inc <- tapply(pres4(c("Eth", "Est", "Rel", "Med")), grp, mean)[c("6-8", "9-11")]
say("R3y", all(abs(inc - PUBLISHED[1, ]) > 0.3),
    sprintf("counting ND too gives %.2f / %.2f against published %.2f / %.2f -- ND is the excluded able-bodied stimulus",
            inc[1], inc[2], PUBLISHED[1, 1], PUBLISHED[1, 2]))

## ---- ROUTE 8 -------------------------------------------------------------
cat("\n=== ROUTE 8: semantic coherence ===\n")

# P1: Med is the modal category for every stimulus -- "For all the children,
#     people with disability are disabled because they are sick" (Discussion).
top <- MODEL[apply(M, 1, which.max)]
say("P1", all(top == "Med"),
    sprintf("Med is the top category in %d/4 sections (%s)", sum(top == "Med"),
            paste(STIM, top, sep = "=", collapse = " ")))

# P2: and it collapses for the one stimulus with no disability.
say("P2", M["ND", "Med"] < 0.5 * min(M[DIS, "Med"]),
    sprintf("Med: MD %.2f, SD %.2f, CD %.2f vs able-bodied ND %.2f",
            M["MD","Med"], M["SD","Med"], M["CD","Med"], M["ND","Med"]))

# P3: "Other" = "any complete expression not attributable to one of the previous
#     models", and the codebook says denial of disability falls there. Asking why
#     a NORMAL person has difficulties is the item that draws denials, so Oth must
#     spike at ND; Idont ("clearly expressed ignorance") must not spike the same way.
say("P3", M["ND","Oth"] > 4 * max(M[DIS,"Oth"]) && M["ND","Idont"] < 1.5 * max(M[DIS,"Idont"]),
    sprintf("Oth: ND %.3f vs %.3f/%.3f/%.3f (%.1fx the largest disability value); Idont ND %.3f vs CD %.3f (%.2fx) -- flat",
            M["ND","Oth"], M["MD","Oth"], M["SD","Oth"], M["CD","Oth"],
            M["ND","Oth"] / max(M[DIS,"Oth"]),
            M["ND","Idont"], M["CD","Idont"], M["ND","Idont"] / max(M[DIS,"Idont"])))

# P4/P5: Env is "architectural and cultural environments (barriers, rules,
#     regulations)"; SRel "made explicit reference to the attitudes and prejudices
#     that characterize human social relationships". Paolo is described as not
#     understanding what others say -- a relational, not an architectural, barrier;
#     Giovanni's wheelchair and Maria's blindness are the architectural ones.
say("P4", M["CD","SRel"] > M["MD","SRel"] && M["CD","SRel"] > M["SD","SRel"],
    sprintf("SRel is highest at CD among the disability stimuli: %.3f vs MD %.3f, SD %.3f",
            M["CD","SRel"], M["MD","SRel"], M["SD","SRel"]))
say("P5", M["CD","Env"] == 0 && M["MD","Env"] > 0 && M["SD","Env"] > 0,
    sprintf("Env is exactly 0 at CD (%d coded mentions) while MD %d and SD %d -- the reverse of SRel, so Env and SRel are not interchangeable",
            tot[[cd("CD","Env")]], tot[[cd("MD","Env")]], tot[[cd("SD","Env")]]))

# P6: the blame/appearance/fate categories are all but unused, which is the
#     article's own headline about children.
blame <- sum(tot[cd(rep(STIM, each = 3), rep(c("Eth","Est","Rel"), 4))])
med   <- sum(tot[cd(STIM, "Med")])
say("P6", blame < 0.05 * med,
    sprintf("Eth+Est+Rel total %d coded mentions across all 4 stimuli against Med %d",
            blame, med))

cat("\nWHAT THIS DOES NOT ESTABLISH.\n")
cat(sprintf(" - Eth vs Est vs Rel: %d, %d and %d coded mentions in the whole table. No\n",
            sum(tot[cd(STIM,"Eth")]), sum(tot[cd(STIM,"Est")]), sum(tot[cd(STIM,"Rel")])))
cat("   distributional route can separate three near-empty categories; they rest on the\n")
cat("   suffix names and on the S1 header order reproducing the codebook's criteria 1..9.\n")
cat(sprintf(" - MD vs SD: the two are close on every category (Med %.2f/%.2f, Env %.3f/%.3f,\n",
            M["MD","Med"], M["SD","Med"], M["MD","Env"], M["SD","Env"]))
cat(sprintf("   SRel %.3f/%.3f) and nothing here distinguishes a wheelchair stimulus from a blind\n",
            M["MD","SRel"], M["SD","SRel"]))
cat("   one, so a swap of those two section_prompts would be undetected. That pair rests on\n")
cat("   MD = motor / SD = sensory disability plus the S1 column order matching the\n")
cat("   codebook's question order (i) wheelchair, (ii) blind, (iii) autistic, (iv) normal.\n")
cat(" - Route 3 pins macro-model MEMBERSHIP, not the order within {Eth,Est,Rel,Med} or\n")
cat("   within {Env,SRel}; P1/P2 pin Med and P4/P5 pin Env vs SRel, the rest do not follow.\n")

cat(if (all(ok)) "\nVERDICT: PASS\n" else "\nVERDICT: FAIL\n")

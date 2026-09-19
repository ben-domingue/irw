# verify_verbagg.R -- Step 5b evidence for `verbagg`, re-runnable.
#
# CLAIM UNDER TEST (the mapping, not the plumbing):
#   (a) item axis   -- S1=bus, S2=train, S3=store, S4=operator; the Want/Do token
#                      in the code is the behaviour mode; Curse/Scold/Shout is the
#                      behaviour. i.e. S2WantShout means "I miss a train because a
#                      clerk gave me faulty information. I would want to shout".
#   (b) resp axis   -- resp 1 == "perhaps" OR "yes"; resp 0 == "no". (lme4 builds
#                      r2 as levels(no,perhaps,yes) -> (N,Y,Y), and
#                      data/verbagg.R sets resp = 1 iff r2 == "Y".)
#
# ROUTE: response-frequency matching (Step 5b route 9 / route 1) against an
# independently distributed copy of the SAME 316-person x 24-item study,
# edstan::aggression, whose items carry named scenarios (bus/train/store/operator)
# and facet indicators instead of lme4's S1..S4 codes. Hard-coded below from
# edstan 1.0.6 data/aggression.rda: per item, the number of respondents with
# dich == 1 ("perhaps" or "yes"), and, as a contrast, with poly == 2 ("yes" only).
#
# CAUTION recorded deliberately: edstan's `description` STRINGS carry a want/do
# inversion relative to edstan's own `do` indicator column (its "want bus shout"
# row has do == 1). The mode below is taken from the `do` indicator, not from the
# string. The scenario token in those same strings is therefore corroborative,
# not authoritative -- see the closing note.

suppressMessages(library(irw))
TABLE <- "verbagg"

# scenario, behaviour, mode(from edstan `do` indicator), sum(dich==1), sum(poly==2)
E <- read.csv(text = "scen,beh,mode,dich,yesonly
bus,curse,Want,225,130
bus,scold,Want,190,104
bus,shout,Want,162,63
bus,curse,Do,225,117
bus,scold,Do,180,83
bus,shout,Do,108,40
train,curse,Want,249,137
train,scold,Want,198,105
train,shout,Want,158,74
train,curse,Do,207,110
train,scold,Do,154,62
train,shout,Do,78,25
store,curse,Want,188,68
store,scold,Want,118,28
store,shout,Want,76,13
store,curse,Do,145,37
store,scold,Do,77,16
store,shout,Do,29,4
operator,curse,Want,218,91
operator,scold,Want,137,49
operator,shout,Want,99,35
operator,curse,Do,198,81
operator,scold,Do,135,44
operator,shout,Do,57,14
", stringsAsFactors = FALSE)

# The shipped mapping, expressed as a prediction about item codes.
SIT <- c(bus = "S1", train = "S2", store = "S3", operator = "S4")
BEH <- c(curse = "Curse", scold = "Scold", shout = "Shout")
E$code <- paste0(SIT[E$scen], E$mode, BEH[E$beh])
E$code[E$code == "S4WantCurse"] <- "S4wantCurse"   # live data spells this one lowercase

d <- irw::irw_fetch(TABLE)
live_sum <- tapply(d$resp, d$item, sum)
live_n   <- tapply(d$resp, d$item, length)

stopifnot(all(E$code %in% names(live_sum)), length(live_sum) == 24)

cat(sprintf("%-12s %-9s %-6s %-5s %9s %9s %6s %9s\n",
            "item", "scenario", "behav", "mode", "edstan", "live", "diff", "yes-only"))
for (i in order(E$code)) {
  cat(sprintf("%-12s %-9s %-6s %-5s %9d %9d %6d %9d\n",
              E$code[i], E$scen[i], E$beh[i], E$mode[i],
              E$dich[i], live_sum[[E$code[i]]],
              live_sum[[E$code[i]]] - E$dich[i], E$yesonly[i]))
}

diffs <- sapply(seq_len(nrow(E)), function(i) live_sum[[E$code[i]]] - E$dich[i])
cat(sprintf("\nitems matching exactly: %d/24   n per item (live): %s\n",
            sum(diffs == 0), paste(unique(live_n), collapse = ",")))
cat(sprintf("resp axis: live endorsed total %d vs edstan perhaps-or-yes %d vs yes-only %d\n",
            sum(d$resp), sum(E$dich), sum(E$yesonly)))

cat("\nWhat this does NOT establish: the counts tie each live code to one edstan row,\n",
    "but S1DoCurse and S1WantCurse both total 225, so the count alone cannot separate\n",
    "that pair -- the Want/Do token in the code (and lme4's own `mode` column) does.\n",
    "Bus-vs-train and store-vs-operator identity rests on edstan's scenario labels plus\n",
    "the difR and psychotools documentation, not on anything internal to the IRW table;\n",
    "lme4's `situ` column only confirms the blocks (S1,S2 = other-to-blame; S3,S4 = self).\n",
    "Hence PARTIAL, not VERIFIED.\n", sep = "")

ok <- all(diffs == 0) && sum(d$resp) == sum(E$dich) && sum(d$resp) != sum(E$yesonly)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

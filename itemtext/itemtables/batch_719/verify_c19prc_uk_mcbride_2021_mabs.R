# verify_c19prc_uk_mcbride_2021_mabs.R -- Step 5b, batch_719.
#
# Claim: the crosswalk's content-keyed per-wave rename (data/c19prc_uk_mcbride_2021_crosswalk.py)
# ties each MABS_* code to the right source column. W4 inserted a NEW item at position 1
# ("God is aware of everything we do.") and moved "The soul is immortal" from W1 position 1
# to W4 position 9, so a bare-name pooling would conflate questions. The rename is NOT
# number-preserving, hence this check.
#
# SOURCE below = per-column counts of resp 1..5 read from the OSF v2zur .sav files
# (C19PRC_UKW1W2_archive_final.sav W1_ReligiousBeliefN; C19PRC_UK_W4_archive_final.sav
# W4_ReligiousBeliefN), each column identified by its own .sav variable label (quoted).
# Every one of the 17 source distributions is distinct, so a swap of any two codes within
# a wave breaks the cell match.
suppressMessages(library(irw))
TABLE <- "c19prc_uk_mcbride_2021_mabs"
SOURCE <- list(
  # wave 1
  list(1, "MABS_soul_immortal",   "W1_ReligiousBelief1 'The soul is immortal.'",            c(224,327,895,286,289)),
  list(1, "MABS_misery",          "W1_ReligiousBelief2 'Belief in God ... misery'",         c(349,534,655,311,170)),
  list(1, "MABS_holy_books",      "W1_ReligiousBelief3 'God has revealed ... holy books'",  c(109,229,726,383,569)),
  list(1, "MABS_moral_judgment",  "W1_ReligiousBelief4 'Moral judgments ...'",              c(729,585,544,100,65)),
  list(1, "MABS_praying",         "W1_ReligiousBelief5 '... by praying'",                   c(188,282,670,316,557)),
  list(1, "MABS_scientific_laws", "W1_ReligiousBelief6 '... scientific laws'",              c(273,513,749,346,141)),
  list(1, "MABS_afterlife",       "W1_ReligiousBelief7 'Our fate in the afterlife ...'",    c(110,261,794,338,518)),
  list(1, "MABS_indoctrinate",    "W1_ReligiousBelief8 'It is wrong to indoctrinate ...'",  c(544,513,690,192,77)),
  # wave 4
  list(4, "MABS_god_aware",       "W4_ReligiousBelief1 'God is aware of everything we do.'",c(433,593,1204,351,1286)),
  list(4, "MABS_misery",          "W4_ReligiousBelief2",                                    c(591,740,1290,519,727)),
  list(4, "MABS_holy_books",      "W4_ReligiousBelief3",                                    c(269,470,1360,442,1326)),
  list(4, "MABS_moral_judgment",  "W4_ReligiousBelief4",                                    c(1275,1050,1054,212,276)),
  list(4, "MABS_praying",         "W4_ReligiousBelief5",                                    c(413,618,1218,350,1268)),
  list(4, "MABS_scientific_laws", "W4_ReligiousBelief6",                                    c(617,932,1410,552,356)),
  list(4, "MABS_afterlife",       "W4_ReligiousBelief7",                                    c(212,559,1444,459,1193)),
  list(4, "MABS_indoctrinate",    "W4_ReligiousBelief8",                                    c(956,882,1396,353,280)),
  list(4, "MABS_soul_immortal",   "W4_ReligiousBelief9 'The soul is immortal'",             c(409,599,1687,346,826)))

d <- irw::irw_fetch(TABLE)
ok <- 0; tot <- 0
for (s in SOURCE) {
  lv <- d$resp[d$wave == s[[1]] & d$item == s[[2]]]
  obs <- sapply(1:5, function(r) sum(lv == r))
  m <- sum(obs == s[[4]]); ok <- ok + m; tot <- tot + 5
  cat(sprintf("W%d %-21s src %-26s live %-26s %s  [%s]\n", s[[1]], s[[2]],
      paste(s[[4]], collapse="/"), paste(obs, collapse="/"), if (m == 5) "OK" else "MISMATCH", s[[3]]))
}
cat(sprintf("\n%d / %d wave x item x resp cells match\n", ok, tot))
# Direction (1 = Strongly agree) is from the .sav value labels; corroborated offline by
# self-identified atheists (W1_Religion==7) averaging 4.29 on 'praying' vs Christians 2.86
# and 1.91 vs 2.70 on 'indoctrinate'. Not re-computed here (needs the .sav).
cat("Does NOT establish: wording beyond the .sav labels (the W1 questionnaire PDF is image-only).\n")
cat(if (ok == tot) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

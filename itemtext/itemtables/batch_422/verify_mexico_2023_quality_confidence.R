# verify_mexico_2023_quality_confidence.R -- batch_422
#
# Claim: live item p11_1_NN is INEGI ENCIG variable P11_1_NN (2023 file, zero-padded)
# stacked with P11_1_N (2021 file, unpadded), and P11_1_NN is row NN of question 11.1
# ("En su opinion, cuanta confianza le generan...") in the ENCIG 2023/2021 cuestionario.
#
# Route 9 (response-frequency matching): per item x resp-level counts tabulated from
# INEGI's own public microdata (encig23_base_datos_csv.zip -> encig2023_01_sec_11.csv,
# sha256 af733d86...; encig21_base_datos_csv.zip -> encig2021_01_sec_11.csv,
# sha256 4463e585...) are hard-coded below. The processing script stacks 2023 on 2021
# with `append, force`; 2021's columns are unpadded (P11_1_1..P11_1_9), so for items
# 01-09 the 2021 answers never reach the table -- the prediction is therefore
# 2023 + (item >= 10 ? 2021 : 0). A swap of any two items' text/codes breaks this,
# since every item's 5-cell count vector is distinct.
# Marker (route 7): item 07 "Companeros(as) del trabajo" must carry by far the largest
# "No aplica" (resp 5) share -- respondents without a job.
# NOT established by the numbers: the code -> questionnaire-row tie itself, which rests on
# the cuestionario printing rows 01..25 under 11.1 (explicit code labels); the numbers
# prove live code = INEGI column, the marker corroborates row 07.
suppressMessages(library(irw))
TABLE <- "mexico_2023_quality_confidence"
R23 <- rbind(
   c(9283,20380,4015,920,699),
  c(1798,13517,12053,11180,35),
  c(5720,21284,8018,2915,111),
  c(6422,16634,8940,5782,39),
  c(1831,16983,11750,4426,216),
  c(2728,16403,11543,6818,43),
  c(5972,13574,3739,989,12711),
  c(2561,17540,11540,5872,68),
  c(16484,16995,3808,1112,104),
  c(1400,13482,11626,6080,1089),
  c(6509,21271,7471,2471,99),
  c(1171,12711,13365,8407,157),
  c(2292,17318,12541,5492,30),
  c(3500,17822,11192,4923,26),
  c(3821,19379,9055,3510,91),
  c(7273,22508,5080,1312,590),
  c(1830,14224,12496,7007,107),
  c(6039,18038,8925,4288,142),
  c(942,10742,13909,12030,50),
  c(6058,19262,8041,3944,33),
  c(8139,19509,6647,3194,29),
  c(1837,14004,13022,7999,62),
  c(1907,18383,12531,5024,20),
  c(3077,20651,8724,2507,162),
  c(3800,22361,7797,2066,71) )
R21 <- rbind(
   c(10311,20173,3705,917,354),
  c(1679,12374,12186,13107,45),
  c(5837,21605,8174,2842,92),
  c(5874,16637,9674,6225,49),
  c(1998,16633,11900,4857,168),
  c(2838,15873,11932,7378,60),
  c(6557,14369,3854,1070,11276),
  c(2646,16753,12054,6650,67),
  c(17101,17232,3614,1148,99),
  c(1453,13296,11860,6648,735),
  c(6606,21675,7356,2598,100),
  c(1211,12648,13495,8938,117),
  c(2419,18370,12330,4901,35),
  c(3490,17629,11252,5485,32),
  c(4093,19541,8804,3380,96),
  c(7803,22879,4835,1252,331),
  c(1881,14281,12753,6995,80),
  c(6307,18712,8616,4237,115),
  c(959,10352,13968,12976,49),
  c(6286,19627,7803,3647,53),
  c(8702,19598,6469,2929,44),
  c(1776,13415,12773,9342,58),
  c(1842,17898,13009,5513,25),
  c(3116,20388,8747,2611,117),
  c(4327,22398,7741,2116,54) )
d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]
fail <- FALSE
cat(sprintf("%-9s %-32s %-32s %s\n", "item", "predicted (1/2/3/4/5)", "live (1/2/3/4/5)", "abs diff"))
for (i in 1:25) {
  code <- sprintf("p11_1_%02d", i)
  pred <- R23[i, ] + if (i >= 10) R21[i, ] else 0
  live <- as.integer(table(factor(d$resp[d$item == code], levels = 1:5)))
  dd <- sum(abs(pred - live))
  if (dd != 0) fail <- TRUE
  cat(sprintf("%-9s %-32s %-32s %d\n", code, paste(pred, collapse = "/"), paste(live, collapse = "/"), dd))
}
# distinctness: no two items share a predicted vector (so the match pins every item)
P <- t(sapply(1:25, function(i) R23[i, ] + if (i >= 10) R21[i, ] else 0))
ndist <- nrow(unique(P)); cat(sprintf("\ndistinct predicted count vectors: %d of 25\n", ndist))
if (ndist != 25) fail <- TRUE
na5 <- tapply(d$resp == 5, d$item, mean)
cat(sprintf("marker: 'No aplica' share p11_1_07 = %.3f; max of other 24 items = %.3f (%s)\n",
            na5["p11_1_07"], max(na5[names(na5) != "p11_1_07"]), names(which.max(na5[names(na5) != "p11_1_07"]))))
if (na5["p11_1_07"] <= max(na5[names(na5) != "p11_1_07"])) fail <- TRUE
cat("Not established: the questionnaire-row -> variable-name tie (explicit row numbers 01..25 in the cuestionario).\n")
cat(if (!fail) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

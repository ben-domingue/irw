# verify_depression_anxiety_stress.R
#
# CLAIM UNDER TEST
#   data/depression_anxiety_stress.R assigns `item` as a script-generated integer
#   (row_number() over unique(df$item) after the pivot) over the openpsychometrics
#   DASS raw file, having lowercased the header, dropped the *I (question-position)
#   and *E (latency) columns and the demographic block. Re-running that derivation
#   gives item 1-42 = Q1A-Q42A, 43-52 = TIPI1-TIPI10, 53-68 = VCL1-VCL16 -- which is
#   exactly the order in which depression_anxiety_stress__items.csv assigns text.
#
# WHAT WOULD BREAK IT
#   Any permutation of that assignment, and any permutation of the response anchors.
#   SRC below holds the per-item x per-response-level cell counts computed directly
#   from the raw source (openpsychometrics DASS_data_21.02.19/data.csv, 39,775
#   respondents), applying the script's own 0 -> NA rule to the DASS and TIPI blocks
#   and leaving the VCL 0/1 checklist alone. A correct mapping reproduces all
#   68 x 9 = 612 cells exactly. Swap any two items, or flip any block's anchor
#   order, and cells move immediately.
#
#   The comparison is run as a server-side GROUP BY rather than irw::irw_fetch(),
#   because this table is 2,704,700 rows and the full download times out
#   intermittently; the aggregate is the same numbers either way.

suppressMessages(library(redivis))

TABLE <- "depression_anxiety_stress"

# rows = items 1..68; cols = resp 0,1,2,3,4,5,6,7,NA
SRC <- matrix(c(
       0,   6104,  13320,   9958,  10393,      0,      0,      0,      0,   # item 1   = Q1A
       0,  14385,  11504,   6535,   7351,      0,      0,      0,      0,   # item 2   = Q2A
       0,  11563,  14062,   7744,   6406,      0,      0,      0,      0,   # item 3   = Q3A
       0,  17757,  11128,   6005,   4885,      0,      0,      0,      0,   # item 4   = Q4A
       0,   8014,  12794,   9179,   9788,      0,      0,      0,      0,   # item 5   = Q5A
       0,   7323,  13291,   9512,   9649,      0,      0,      0,      0,   # item 6   = Q6A
       0,  18092,  11333,   5594,   4756,      0,      0,      0,      0,   # item 7   = Q7A
       0,   8086,  13471,   9241,   8977,      0,      0,      0,      0,   # item 8   = Q8A
       0,   6544,  11788,   9709,  11734,      0,      0,      0,      0,   # item 9   = Q9A
       0,  10625,  11007,   7869,  10274,      0,      0,      0,      0,   # item 10  = Q10A
       0,   5143,  11136,   9898,  13598,      0,      0,      0,      0,   # item 11  = Q11A
       0,   9326,  12601,   9439,   8409,      0,      0,      0,      0,   # item 12  = Q12A
       0,   5646,  11200,   9007,  13922,      0,      0,      0,      0,   # item 13  = Q13A
       0,   7501,  12535,   8897,  10842,      0,      0,      0,      0,   # item 14  = Q14A
       0,  19587,  11262,   5150,   3776,      0,      0,      0,      0,   # item 15  = Q15A
       0,   8996,  11696,   8504,  10579,      0,      0,      0,      0,   # item 16  = Q16A
       0,   8644,   9800,   7822,  13509,      0,      0,      0,      0,   # item 17  = Q17A
       0,   8567,  12789,   9277,   9142,      0,      0,      0,      0,   # item 18  = Q18A
       0,  18506,  10370,   5428,   5471,      0,      0,      0,      0,   # item 19  = Q19A
       0,  11946,  11489,   7885,   8455,      0,      0,      0,      0,   # item 20  = Q20A
       0,  12694,  10308,   6947,   9826,      0,      0,      0,      0,   # item 21  = Q21A
       0,   9448,  14327,   8850,   7150,      0,      0,      0,      0,   # item 22  = Q22A
       0,  25111,   9139,   3349,   2176,      0,      0,      0,      0,   # item 23  = Q23A
       0,   8555,  13790,   8919,   8511,      0,      0,      0,      0,   # item 24  = Q24A
       0,  13569,  11924,   7664,   6618,      0,      0,      0,      0,   # item 25  = Q25A
       0,   6587,  11979,   9636,  11573,      0,      0,      0,      0,   # item 26  = Q26A
       0,   6582,  12889,   9670,  10634,      0,      0,      0,      0,   # item 27  = Q27A
       0,  12734,  12495,   7716,   6830,      0,      0,      0,      0,   # item 28  = Q28A
       0,   6424,  12280,   9733,  11338,      0,      0,      0,      0,   # item 29  = Q29A
       0,  10000,  12535,   8875,   8365,      0,      0,      0,      0,   # item 30  = Q30A
       0,   9254,  14022,   8756,   7743,      0,      0,      0,      0,   # item 31  = Q31A
       0,   7762,  14441,   9653,   7919,      0,      0,      0,      0,   # item 32  = Q32A
       0,   9095,  13146,   9498,   8036,      0,      0,      0,      0,   # item 33  = Q33A
       0,   8677,  10268,   7766,  13064,      0,      0,      0,      0,   # item 34  = Q34A
       0,   9317,  15373,   8810,   6275,      0,      0,      0,      0,   # item 35  = Q35A
       0,  12517,  12042,   7242,   7974,      0,      0,      0,      0,   # item 36  = Q36A
       0,  11580,  11362,   7228,   9605,      0,      0,      0,      0,   # item 37  = Q37A
       0,  12551,   9797,   6681,  10746,      0,      0,      0,      0,   # item 38  = Q38A
       0,   7673,  14405,   9657,   8040,      0,      0,      0,      0,   # item 39  = Q39A
       0,   7659,  10788,   9109,  12219,      0,      0,      0,      0,   # item 40  = Q40A
       0,  17323,  11617,   5693,   5142,      0,      0,      0,      0,   # item 41  = Q41A
       0,   5571,  12886,  10014,  11304,      0,      0,      0,      0,   # item 42  = Q42A
       0,   6229,   5603,   4633,   5877,   8420,   6046,   2482,    485,   # item 43  = TIPI1
       0,   3985,   4040,   4326,   6171,  10373,   6990,   3320,    570,   # item 44  = TIPI2
       0,   2252,   2843,   3981,   4516,   9121,  10230,   6242,    590,   # item 45  = TIPI3
       0,   2042,   2444,   2434,   2720,   8751,   9561,  11360,    463,   # item 46  = TIPI4
       0,   1647,   2226,   3341,   5140,   9525,   9697,   7682,    517,   # item 47  = TIPI5
       0,   2666,   2748,   3475,   4943,   7733,   8094,   9626,    490,   # item 48  = TIPI6
       0,   1015,   1367,   2270,   4421,   9097,  10997,  10007,    601,   # item 49  = TIPI7
       0,   4138,   4445,   4446,   4577,   9300,   6369,   5841,    659,   # item 50  = TIPI8
       0,   5507,   6401,   6819,   6837,   6250,   4943,   2591,    427,   # item 51  = TIPI9
       0,   5404,   5714,   6184,   7665,   6653,   4106,   3494,    555,   # item 52  = TIPI10
    7463,  32312,      0,      0,      0,      0,      0,      0,      0,   # item 53  = VCL1
   16711,  23064,      0,      0,      0,      0,      0,      0,      0,   # item 54  = VCL2
   33715,   6060,      0,      0,      0,      0,      0,      0,      0,   # item 55  = VCL3
    5296,  34479,      0,      0,      0,      0,      0,      0,      0,   # item 56  = VCL4
   12536,  27239,      0,      0,      0,      0,      0,      0,      0,   # item 57  = VCL5
   38177,   1598,      0,      0,      0,      0,      0,      0,      0,   # item 58  = VCL6
   36450,   3325,      0,      0,      0,      0,      0,      0,      0,   # item 59  = VCL7
   33041,   6734,      0,      0,      0,      0,      0,      0,      0,   # item 60  = VCL8
   38059,   1716,      0,      0,      0,      0,      0,      0,      0,   # item 61  = VCL9
    5147,  34628,      0,      0,      0,      0,      0,      0,      0,   # item 62  = VCL10
   36844,   2931,      0,      0,      0,      0,      0,      0,      0,   # item 63  = VCL11
   36423,   3352,      0,      0,      0,      0,      0,      0,      0,   # item 64  = VCL12
   28182,  11593,      0,      0,      0,      0,      0,      0,      0,   # item 65  = VCL13
   17274,  22501,      0,      0,      0,      0,      0,      0,      0,   # item 66  = VCL14
    6087,  33688,      0,      0,      0,      0,      0,      0,      0,   # item 67  = VCL15
    2749,  37026,      0,      0,      0,      0,      0,      0,      0   # item 68  = VCL16
), nrow = 68, ncol = 9, byrow = TRUE)

q <- redivis::query(paste(
  "SELECT item, resp, COUNT(*) AS n",
  "FROM `datapages.item_response_warehouse.depression_anxiety_stress`",
  "GROUP BY item, resp"))
live_df <- suppressWarnings(q$to_data_frame())

LIVE <- matrix(0L, nrow = 68, ncol = 9)
for (k in seq_len(nrow(live_df))) {
    i <- as.integer(as.character(live_df$item[k]))
    r <- suppressWarnings(as.integer(as.character(live_df$resp[k])))
    j <- if (is.na(r)) 9L else r + 1L        # col 9 is the NA level
    LIVE[i, j] <- LIVE[i, j] + as.integer(live_df$n[k])
}

lbl <- c(paste0("Q", 1:42, "A"), paste0("TIPI", 1:10), paste0("VCL", 1:16))
hdr <- c("r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "rNA")
cat(sprintf("%-5s %-8s %-5s", "item", "source", ""),
    sprintf("%7s", hdr), "\n")
show <- c(1, 17, 26, 42, 43, 52, 53, 58, 68)   # incl. the near-tied 17/26 pair
for (i in show) {
    cat(sprintf("%-5d %-8s %-5s", i, lbl[i], "raw "), sprintf("%7d", SRC[i, ]), "\n")
    cat(sprintf("%-5s %-8s %-5s", "", "", "live"), sprintf("%7d", LIVE[i, ]), "\n")
}

bad <- which(LIVE != SRC, arr.ind = TRUE)
cat(sprintf("\ncells compared: %d; mismatching cells: %d\n", length(LIVE), nrow(bad)))
if (nrow(bad) > 0) { cat("mismatches (row=item, col=resp+1, col 9 = NA):\n"); print(utils::head(bad, 20)) }

# What this does NOT establish: the WORDING of any item. That rests on
# codebook.txt's own Qn / TIPIn / VCLn keys, which tie each source column to its
# verbatim text. Everything about WHICH item each integer is, and which anchor each
# resp value is, is pinned here -- including items 17 and 26, whose means differ by
# only 2.5e-5 but which differ by 244 respondents at resp = 4.

cat(if (nrow(bad) == 0) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

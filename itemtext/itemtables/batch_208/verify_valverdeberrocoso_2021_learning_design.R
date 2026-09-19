# Step 5b mapping verification for valverdeberrocoso_2021_learning_design.
#
# CLAIM: each item code SPAnn / RESnn / PRAnn carries the nth item of the
# corresponding block of the study's questionnaire (S2 File, PLOS ONE
# 10.1371/journal.pone.0256283) -- "Espacios que utilizo para la
# ensenanza-aprendizaje con TIC" (8), "Resultados de aprendizaje que espero
# obtener con el uso de las TIC" (8), "Tipo de practica docente que realizo
# con TIC" (6). The questionnaire prints the items UNNUMBERED, so the tie is
# by presentation order (mapping_basis = paper_order).
#
# FALSIFIABLE PREDICTION: the paper's Table 1 publishes M and SD for all 22
# items in that same block order. If any two item_texts were swapped, the
# per-item mean/SD of the live table would no longer line up item-for-item.
#
# Every published mean is distinct WITHIN its block, so mean alone pins every
# item against every other item of its block; SD is printed as a second,
# independent check.

suppressMessages(library(irw))

TABLE <- "valverdeberrocoso_2021_learning_design"

# Paper Table 1 (10.1371/journal.pone.0256283.t001), in printed order.
PUB <- data.frame(
  item = c(paste0("SPA", sprintf("%02d", 1:8)),
           paste0("RES", sprintf("%02d", 1:8)),
           paste0("PRA", sprintf("%02d", 1:6))),
  text = c("Generic classroom", "Technology classroom", "Laboratory classroom",
           "Physical Education classroom", "Library", "Student's personal space",
           "Flipped Classroom", "Virtual classroom",
           "Knowledge", "Understanding", "Application", "Analysis",
           "Synthesis", "Evaluation", "Attitudinal", "Psychomotor",
           "Read/View/Listen", "Collaborate", "Debate-Reflect",
           "Investigate", "Practice", "Produce"),
  M  = c(5.04, 2.71, 1.78, 1.38, 2.57, 3.49, 2.33, 3.03,
         4.32, 4.51, 4.49, 4.45, 4.30, 4.19, 4.33, 3.25,
         4.78, 4.37, 4.13, 4.75, 4.65, 4.30),
  SD = c(1.139, 1.675, 1.331, 0.958, 1.546, 1.381, 1.509, 1.760,
         1.187, 1.154, 1.118, 1.160, 1.215, 1.279, 1.267, 1.486,
         1.105, 1.256, 1.333, 1.181, 1.182, 1.360),
  stringsAsFactors = FALSE)

TOL_M  <- 0.01
TOL_SD <- 0.002

d <- irw::irw_fetch(TABLE)
obs_m  <- tapply(d$resp, d$item, mean)[PUB$item]
obs_sd <- tapply(d$resp, d$item, sd)[PUB$item]

cat(sprintf("%-7s %-30s %8s %8s %8s | %8s %8s %8s\n",
            "item", "paper Table 1 label", "pub M", "obs M", "dM",
            "pub SD", "obs SD", "dSD"))
for (i in seq_len(nrow(PUB)))
  cat(sprintf("%-7s %-30s %8.2f %8.2f %8.3f | %8.3f %8.3f %8.3f\n",
              PUB$item[i], PUB$text[i], PUB$M[i], obs_m[i], obs_m[i] - PUB$M[i],
              PUB$SD[i], obs_sd[i], obs_sd[i] - PUB$SD[i]))

worst_m  <- max(abs(obs_m  - PUB$M))
worst_sd <- max(abs(obs_sd - PUB$SD))
cat(sprintf("\nlargest |dM| = %.4f (tol %.2f); largest |dSD| = %.4f (tol %.3f)\n",
            worst_m, TOL_M, worst_sd, TOL_SD))

# Would a swap be detectable? Show the smallest within-block mean gap.
for (blk in c("SPA", "RES", "PRA")) {
  m <- sort(PUB$M[substr(PUB$item, 1, 3) == blk])
  cat(sprintf("%s: %d items, smallest gap between published means = %.2f\n",
              blk, length(m), min(diff(m))))
}

cat("Note: this route pins each item against every other item. The two tightest\n",
    "pairs are settled by SD rather than by mean: RES01 4.32 vs RES07 4.33 (SD 1.187\n",
    "vs 1.267) within the RES block, and RES05 vs PRA06, both 4.30, which sit ACROSS\n",
    "blocks where the source column prefix already separates them (SD 1.215 vs 1.360).\n",
    "It does NOT independently verify the option_text<->resp\n",
    "mapping, which comes from the questionnaire's own printed anchor legend\n",
    "(1 = Nunca ... 6 = Siempre) and the paper's Methods restatement of it.\n", sep = "")

cat(if (worst_m <= TOL_M && worst_sd <= TOL_SD) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

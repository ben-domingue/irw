# verify_alqerem_2024_diabetic_health_literacy.R  (batch_331)
#
# mapping_basis is data_labels (the item codes are the .sav column names,
# upper-cased by data/alqerem_2024_diabetic_health_literacy.py, and each column
# carries its own variable label), so no script is owed. This one exists because
# the paper's Table 2 publishes per-item response frequencies that corroborate
# the item mapping independently AND expose a response-coding defect in the
# deposit, and both should be re-runnable.
#
# Al-Qerem et al. (2024), Healthcare 12(7):801, doi:10.3390/healthcare12070801,
# Table 2 (counts at levels 1..4 of the paper's 1-4 scale) and Table 3 (means).
suppressMessages(library(irw))
TABLE <- "alqerem_2024_diabetic_health_literacy"

paper <- list(                         # paper level 1, 2, 3, 4
  N1 = c(44,  93, 198,  65),           # Read and understand educational materials
  N2 = c(41,  97, 188,  74),           # Understand the written information
  N3 = c(42, 119, 174,  65),           # Understand the information on diabetes management
  N5 = c(43, 108, 175,  74),           # Understand the information I search for
  C2 = c(63, 155, 133,  49),           # Explain why my diabetic diet is important
  C3 = c(15,  80, 174, 131),           # Explain my diabetes condition
  C1 = c(15,  66, 183, 136))           # Ask health professionals a question
paper_mean <- c(N1 = 2.71, N2 = 2.74, N3 = 2.66, N5 = 2.70)

d <- irw::irw_fetch(TABLE)
tab <- table(factor(d$item), factor(d$resp, levels = 1:5))
print(tab)

ok <- TRUE
cat("\nInformative items: live code 1 -> paper 1, live 2 -> paper 3, live 3 -> paper 4,",
    "live 4+5 -> paper 2\n")
for (i in c("N1", "N2", "N3", "N5")) {
  live <- tab[i, ]
  pred <- c(live[1], live[4] + live[5], live[2], live[3])
  m <- c(1, 3, 4, 2, 2)[d$resp[d$item == i]]
  hit <- all(pred == paper[[i]]) && abs(mean(m) - paper_mean[i]) < 0.006
  cat(sprintf("  %s  collapsed live %s | paper %s | remapped mean %.3f vs %.2f  %s\n", i,
      paste(pred, collapse = "/"), paste(paper[[i]], collapse = "/"), mean(m),
      paper_mean[i], if (hit) "MATCH" else "MISMATCH"))
  ok <- ok && hit
}
# every informative item's paper vector is distinct, and each live item matches
# only its own label's row:
for (i in c("N1", "N2", "N3", "N5")) {
  live <- tab[i, ]; pred <- c(live[1], live[4] + live[5], live[2], live[3])
  others <- setdiff(c("N1", "N2", "N3", "N5"), i)
  if (any(sapply(others, function(o) all(pred == paper[[o]])))) ok <- FALSE
}

cat("\nCommunicative items (no exact collapse exists; anchor cells):\n")
comm <- c(C2 = tab["C2", 1] == 63,                      # only item at 63
          C1 = tab["C1", 1] == 15 && tab["C1", 3] == 183, # 'Ask' level 3 = 183
          C3 = tab["C3", 1] == 15 && tab["C3", 4] == 131) # 'Explain condition' level 4 = 131
for (i in names(comm)) cat(sprintf("  %s live %s | paper %s  %s\n", i,
    paste(tab[i, ], collapse = "/"), paste(paper[[i]], collapse = "/"),
    if (comm[i]) "anchor cells match" else "MISMATCH"))
ok <- ok && all(comm)

cat("\nDoes NOT establish: what any live resp code means. The live 1-5 codes are not the",
    "paper's 1-4 scale -- for N-items live 2 is the paper's 3rd level and live 4 and 5",
    "both fold into its 2nd -- and the C-items fit no clean collapse (C2 live",
    "63/153/124/13/47 vs paper 63/155/133/49). That is why option_text ships blank.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_argentina_2013_reproductive_transmission.R
# Claim: its03..its06 = ENSSyR 2013 ITS questions 3-6 (mosquitos, saliva, mate, sanitario),
# harmonised from mits03..06 (women) / vits03..06 (men) by data/argentina_2013_reproductive.do,
# and resp is reversed from the source coding (1 Si, 2 No) to 1 = No, 2 = Si.
# Prediction: the INDEC user-base documentation (ENSSyR_doc_utilizacion_bases_usuario.pdf,
# record layout pp. 40-41 women, pp. 73-74 men) prints SAMPLE frequencies for each variable.
# Live item x cov_sex x resp must reproduce them cell for cell. A swap of any two items, or a
# flipped resp direction, breaks it (all four items' Si counts differ in both sexes).
suppressMessages(library(irw))
TABLE <- "argentina_2013_reproductive_transmission"
# published counts: rows = item, c(No, Si)
PUB <- list(
  Mujer = rbind(its03 = c(2840, 1466), its04 = c(3627, 1108), its05 = c(4130, 657), its06 = c(3545, 944)),
  "Varón" = rbind(its03 = c(2578, 1619), its04 = c(3371, 1180), its05 = c(3854, 685), its06 = c(3484, 888)))
d <- irw::irw_fetch(TABLE)
sexlab <- if (is.numeric(d$cov_sex)) c(`2` = "Mujer", `1` = "Varón")[as.character(d$cov_sex)] else as.character(d$cov_sex)
ok <- TRUE
cat(sprintf("%-6s %-6s %8s %8s %8s %8s\n", "sex", "item", "pub_No", "live_1", "pub_Si", "live_2"))
for (s in names(PUB)) for (it in rownames(PUB[[s]])) {
  sub <- d[sexlab == s & d$item == it, ]
  l1 <- sum(sub$resp == 1); l2 <- sum(sub$resp == 2)
  p <- PUB[[s]][it, ]
  cat(sprintf("%-6s %-6s %8d %8d %8d %8d\n", s, it, p[1], l1, p[2], l2))
  if (l1 != p[1] || l2 != p[2]) ok <- FALSE
}
cat("Every item's (No, Si) pair is distinct within each sex, so the 16-cell match distinguishes all four items and fixes resp direction.\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

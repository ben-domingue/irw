# Step 5b for spain_2012_gender_custody (CIS Estudio 2968, P.27).
# Claim: IRW p2702 (DA2968 col 143) holds questionnaire row 1 "Si hay sentencia condenatoria
# firme, se deberia quitar la custodia ... al maltratador" (anti-abuser), and IRW p2701
# (col 144) holds row 2 "Que un hombre maltrate a su pareja no tiene por que implicar que sea
# un mal padre" (pro-father) -- i.e. the questionnaire's printed column markers (143)/(144),
# NOT the ES2968 SPSS labels, which attach these two texts the other way round.
# p2703 ("Los padres deben tener derecho, por encima de todo, a la custodia") and p2704
# ("Despues de cumplida la sentencia, deberia serle devuelta la custodia al padre") are both
# pro-father; labels and column markers agree on them.
# Prediction (raw codes, 1 = Muy de acuerdo .. 4 = Nada de acuerdo): the anti-abuser item
# correlates NEGATIVELY with p2703/p2704 and is heavily agreed with; the "not a bad father"
# item correlates POSITIVELY with p2703/p2704. Swapping the two texts reverses both signs.
suppressMessages(library(irw))
d <- as.data.frame(irw::irw_fetch("spain_2012_gender_custody"))
w <- reshape(d[, c("id","item","resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
r <- round(cor(w[, c("p2701","p2702","p2703","p2704")], use = "pairwise"), 3)
print(r)
m <- round(tapply(d$resp, d$item, mean), 3); print(m)
agree <- round(100 * tapply(d$resp <= 2, d$item, mean), 1)
cat("% Muy/Bastante de acuerdo among answering:\n"); print(agree)
sexgap <- round(tapply(d$resp[d$cov_sex=="Mujer"], d$item[d$cov_sex=="Mujer"], mean) -
                tapply(d$resp[d$cov_sex=="Hombre"], d$item[d$cov_sex=="Hombre"], mean), 3)
cat("mean(Mujer) - mean(Hombre):\n"); print(sexgap)
ok <- c(
  p2702_neg_with_pro_father = r["p2702","p2703"] < -0.15 && r["p2702","p2704"] < -0.15,
  p2701_pos_with_pro_father = r["p2701","p2703"] >  0.30 && r["p2701","p2704"] >  0.30,
  p2701_vs_p2702_negative   = r["p2701","p2702"] < -0.15,
  p2702_mostly_agreed       = agree["p2702"] > 80,
  p2701_mostly_disagreed    = agree["p2701"] < 40,
  p2701_sex_gap_like_pro_father = sign(sexgap["p2701"]) == sign(sexgap["p2703"]) && sign(sexgap["p2701"]) == sign(sexgap["p2704"]))
print(ok)
cat("Does NOT establish: which of p2703/p2704 is which -- both are pro-father (means",
    m["p2703"], "/", m["p2704"], ", r =", r["p2703","p2704"], "); that pair rests on the\n",
    "ES2968 labels agreeing with the questionnaire column markers (145)/(146).\n")
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

# verify_doustmohammadian_2017_fnlit.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: each of the 58 IRW item codes (the .sav column names, melted
# unrenamed by data/doustmohammadian_2017_fnlit.py) carries the FNLIT statement
# this extraction assigned to it.
#
# ROUTE 1/3 (per-item published statistics). Doustmohammadian et al. (2017),
# PLOS ONE 12(6):e0179196, S1 Table (cognitive domain) and S2 Table (skills
# domain) print, for every one of the 58 pilot items, the paper's own item code
# (Q2..Q67) and its Cronbach's alpha-if-item-deleted within its subscale. Alpha-
# if-deleted is a per-ITEM number: swapping any two items inside a subscale
# swaps their predicted values, so reproducing the whole published vector from
# the live IRW data is a falsifiable test of the code->text assignment.
#
# It also fixes the STORED SCALE DIRECTION: the published vector for the
# Interactive and Critical subscales only reproduces if Eatingbehav_StreetVender
# (Q36) and Critical_Management1 (Q56) are reversed first, i.e. the deposited
# file stores those two in raw questionnaire direction while every other item is
# stored in the authors' scored direction. That is what licenses shipping
# Interactive_familyDebate's (Q45) anchors inverted relative to the printed form
# and Critical_Management1's the same way round as printed.
#
# NOTE: this script calls irw_fetch(), which exports the table (21,634 rows).

suppressMessages(library(irw))
TABLE <- "doustmohammadian_2017_fnlit"

# item code -> paper Q code, as shipped in this extraction
MAP <- c(
 Foodknowledge_wholeNeeds="Q2", Foodknowledge_EatingBreakfast="Q3",
 Lifestyle_PA="Q4", Lifestyle_suger="Q5", Lifestyle_susagefat="Q6",
 Lifestyle_tanagholatshoor="Q7", Lifestyle_cancer="Q8",
 Foodsafty_expiratindate="Q9", Foodsafty_Ministry="Q10",
 Foodsafty_standardsign="Q11_3", Foodsafty_expiredate="Q11_2", Foodsafty_ingrediants="Q11_1",
 Understanding_newspapper="Q12", Understanding_foodlabling="Q13", Understanding_nutritionist="Q14",
 Understanding_withHelp="Q15", Understanding_TV="Q16", Understanding_Internet="Q17",
 Foodscience_boiling="Q18_1", Foodscience_taft="Q18_2", Foodscience_frying="Q18_3",
 Foodscience_growingVeg="Q20", Avaiability_HowtoFind="Q23",
 Foodchoice_Khoshkbar="Q24_1", Foodchoice_Shelvs="Q24_2", Foodchoice_Packing="Q24_3",
 Foodchoice_expiredate="Q24_4", Foodchoice_Standardsign="Q24_5", Foodchoice_Ministryliscence="Q24_6",
 Eatingbehav_wholefoodgroup="Q27", Eatingbehav_fruits="Q28", Eatingbehav_vegetables="Q29",
 Eatingbehav_breakfast="Q30", Eatingbehav_healthySnack="Q31", Eatingbehav_salt="Q32",
 Eatingbehav_PA="Q33", Eatingbehav_MyselfeSnack="Q34", Eatingbehav_MyselfeVeg="Q35",
 Eatingbehav_StreetVender="Q36", Interactive_Freinds="Q37", Interactive_Teachers="Q38",
 Interactive_others="Q39", Interactive_foodAlergy="Q40", Interactive_SchoolDebate="Q43",
 Interactive_ParentsDebate="Q44", Interactive_familyDebate="Q45",
 Interactive_WhimsyEmotional="Q48", Interactive_NoSkillEmotional="Q49",
 Interactive_PeersEmotional="Q50", Critical_DontcorrectMedia="Q53",
 Critical_MediaLiteracy="Q54", Critical_TrustMedia="Q55",
 Critical_Management1="Q56", Critical_Management2="Q57", Critical_Management3="Q58",
 Critical_Management4="Q59", Critical_Management5="Q60", Critical_Management6="Q67")
INV <- setNames(names(MAP), MAP)

# published alpha-if-item-deleted, S1/S2 Tables; and each subscale's published alpha
PUB <- list(
 Understanding = c(Q11_1=.674,Q13=.674,Q11_2=.676,Q11_3=.687,Q14=.668,Q12=.675,
                   Q18_1=.686,Q16=.674,Q18_2=.713,Q4=.692,Q20=.703,Q10=.694),
 Knowledge     = c(Q7=.547,Q5=.577,Q6=.555,Q8=.588,Q18_3=.683,Q9=.622,Q3=.628),
 Functional    = c(Q39=.775,Q37=.765,Q29=.781,Q34=.783,Q38=.774,Q35=.793,Q31=.784,
                   Q33=.783,Q28=.793,Q30=.792,Q40=.800,Q67=.791),
 Interactive   = c(Q48=.629,Q50=.627,Q49=.642,Q44=.674,Q43=.639,Q45=.658,Q36=.797,Q24_1=.671),
 FoodChoice    = c(Q24_6=.664,Q24_4=.689,Q24_5=.683,Q24_3=.691,Q24_2=.689,Q27=.718),
 Critical      = c(Q60=.401,Q58=.428,Q57=.320,Q56=.489))
PUB_ALPHA <- c(Understanding=.70,Knowledge=.63,Functional=.79,Interactive=.70,FoodChoice=.72,Critical=.48)
FLIP <- c("Q36","Q56")   # stored raw; authors' analysis used them reversed
TOL <- 0.0015

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)
w <- reshape(d[, c("id","item","resp")], idvar="id", timevar="item", direction="wide")
colnames(w) <- sub("^resp\\.", "", colnames(w))

alpha <- function(X) { X <- as.matrix(X); k <- ncol(X)
  k/(k-1)*(1 - sum(apply(X,2,var))/var(rowSums(X))) }

worst <- 0
for (nm in names(PUB)) {
  pub <- PUB[[nm]]; cols <- INV[names(pub)]
  X <- w[, cols, drop=FALSE]; X <- X[complete.cases(X), , drop=FALSE]
  for (q in intersect(FLIP, names(pub))) X[[INV[q]]] <- 4 - X[[INV[q]]]
  cat(sprintf("\n== %s subscale: alpha %.3f (published %.2f)%s\n", nm, alpha(X), PUB_ALPHA[nm],
              if (any(names(pub) %in% FLIP)) "  [reverse-scored: stored raw]" else ""))
  cat(sprintf("%-8s %-30s %10s %10s %8s\n","Q","IRW item","published","observed","diff"))
  for (i in seq_along(pub)) {
    a <- alpha(X[, -i, drop=FALSE]); dd <- a - pub[i]; worst <- max(worst, abs(dd))
    cat(sprintf("%-8s %-30s %10.3f %10.3f %+8.4f\n", names(pub)[i], cols[i], pub[i], a, dd))
  }
}
cat(sprintf("\nlargest deviation across all 49 published per-item values: %.4f (tolerance %.4f)\n", worst, TOL))

# The 9 items the paper gives no alpha-if-deleted for (dropped before the
# subscale analyses). Not testable by this route; they are pinned by their
# self-describing codes, and Critical_Management4 by elimination -- see below.
cat("\nWHAT THIS DOES NOT ESTABLISH BY NUMBERS: 9 of 58 items carry '-' in the published\n",
    "tables (Q2 wholeNeeds, Q15 withHelp, Q17 Internet, Q23 HowtoFind, Q32 salt,\n",
    "Q53 DontcorrectMedia, Q54 MediaLiteracy, Q55 TrustMedia, Q59 Management4). Eight are\n",
    "tied by self-describing codes; Critical_Management4=Q59 is the residual of a closed\n",
    "1-to-1 bijection (Management1,2,3,5,6 = Q56,Q57,Q58,Q60,Q67 are verified above and\n",
    "ascend in the paper's numbering, so the remaining slot between Q58 and Q60 is Q59).\n",
    "Within-subscale ties in the published values (Q11_1/Q13/Q16 all .674, Q34/Q33 .783,\n",
    "Q35/Q28 .793, Q24_4/Q24_2 .689) are separated by their self-describing codes, not by\n",
    "this route.\n", sep="")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

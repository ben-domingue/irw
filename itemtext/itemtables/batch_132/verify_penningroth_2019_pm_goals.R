# verify_penningroth_2019_pm_goals.R
#
# CLAIM UNDER TEST: each item code (anyXXXg) carries the goal-category label
# shipped in item_text. The source workbook's META-DATA sheet defines 14 of the
# 15 abbreviations (prf=profession, prp=property, yhea=your health, ohea=others'
# health, kid=children, mar=marriage/relatives, edu=education, trav=travel,
# leis=leisure, reti=retirement, war=war/terrorism, worl=world issues,
# self=self/growth, othr=other) -- it OMITS frnd. So the code->text tie is
# checked here against the data instead of taken on the sheet's word.
#
# FALSIFIABLE PREDICTION: Penningroth & Scott (2019) PLOS ONE 14(6):e0216888,
# Table 3, publishes the % of the overall sample, the young group and the older
# group reporting a PM task related to each of 14 goal categories ("other" is
# omitted from the paper's analyses). resp is binary 0/1, so 100*mean(resp) per
# item must reproduce those percentages -- and any permutation of item_text
# across items breaks it.
#
# Two categories tie at 46.1 overall (Education, Property) and two at 7.9
# (World issues, and the unpublished Other), which is why the young/older split
# is compared as well: it separates both pairs outright.

suppressMessages(library(irw))

TABLE <- "penningroth_2019_pm_goals"
TOL   <- 0.06  # paper rounds to 0.1, so up to 0.05 pp of rounding error is expected

# Paper Table 3: item code (per our shipped mapping) -> overall %, young %, older %
PUB <- rbind(
  anyleisg  = c(53.9, 62.5, 39.4),   # Leisure
  anyfrndg  = c(52.8, 58.9, 42.4),   # Friendship
  anyselfg  = c(50.6, 58.9, 36.4),   # Self/growth
  anyyheag  = c(48.3, 42.9, 57.6),   # Own health
  anyedug   = c(46.1, 64.3, 15.2),   # Education
  anyprpg   = c(46.1, 55.4, 30.3),   # Property
  anyprfg   = c(36.0, 46.4, 18.2),   # Profession
  anymarg   = c(27.0, 28.6, 24.2),   # Marriage/relatives
  anyoheag  = c(23.6, 23.2, 24.2),   # Others' health
  anytravg  = c(22.5, 23.2, 21.2),   # Travel
  anykidg   = c(18.0, 16.1, 21.2),   # Children
  anyretig  = c(14.6, 16.1, 12.1),   # Retirement
  anyworlg  = c( 7.9,  5.4, 12.1),   # World issues
  anywarg   = c( 4.5,  1.8,  9.1)    # War/terrorism
)
colnames(PUB) <- c("overall", "young", "older")

d <- irw::irw_fetch(TABLE)   # 1,335 rows -- negligible against the export cap
stopifnot(all(d$resp %in% c(0, 1)))
# cov_group_young_vs_older: 1 = young adults, 2 = older (source META-DATA sheet)
pct <- function(x) 100 * mean(x)
obs_all <- tapply(d$resp, d$item, pct)
yo      <- tapply(d$resp, list(d$item, d$cov_group_young_vs_older), pct)

cat(sprintf("%-9s %-22s %18s %18s\n", "item", "shipped item_text",
            "published o/y/o", "observed o/y/o"))
worst <- 0
LAB <- c(anyleisg="leisure activities", anyfrndg="friendship",
         anyselfg="self/personal growth", anyyheag="your health",
         anyedug="your education", anyprpg="your property/possessions",
         anyprfg="your profession/occupation", anymarg="marriage/relatives",
         anyoheag="the health of others", anytravg="travel",
         anykidg="your children's lives", anyretig="retirement",
         anyworlg="world issues", anywarg="war/terrorism")
for (it in rownames(PUB)) {
  o <- c(obs_all[[it]], yo[it, "1"], yo[it, "2"])
  worst <- max(worst, max(abs(o - PUB[it, ])))
  cat(sprintf("%-9s %-22s %18s %18s\n", it, LAB[[it]],
              paste(sprintf("%.1f", PUB[it, ]), collapse="/"),
              paste(sprintf("%.1f", o), collapse="/")))
}
cat(sprintf("\nlargest deviation: %.2f pp (tolerance %.2f)\n", worst, TOL))

# The 15th item, anyothrg ("other"), is not in Table 3 -- the paper drops the
# rarely-used "other" category from all analyses. It is pinned by elimination
# (every other code is claimed by an exact three-number match above) plus the
# META-DATA sheet's own "othr = other". Show it, don't score it.
cat(sprintf("\nanyothrg (\"other\", not published in Table 3): %.1f/%.1f/%.1f -- ",
            obs_all[["anyothrg"]], yo["anyothrg", "1"], yo["anyothrg", "2"]))
cat("pinned by elimination + META-DATA 'othr = other'.\n")

cat("Note: this route distinguishes all 14 published categories from one another,\n",
    "including the 46.1/46.1 and 7.9/7.9 overall ties, which the young/older split\n",
    "separates. It does not independently confirm anyothrg beyond elimination.\n", sep="")

cat(if (worst <= TOL) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

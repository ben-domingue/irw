# verify_sinche_2017_skill_development.R -- Step 5b mapping check (batch_176)
#
# mapping_basis = data_labels: item_text is the S1 .sav variable label of
# Doc_Skill_k. The processing script (data/sinche_2017_transferable_skills.py)
# builds its column list BY NAME (Doc_Skill_1..15) and then assigns
# skill_dev_{i+1} with enumerate(), so skill_dev_k should be Doc_Skill_k.
# Because enumerate() is on the positional list in SKILL.md, this checks it
# against the data rather than asserting the exemption.
#
# Two checks, both of which break if any two item texts were swapped:
#  A. Live item x resp counts (server-side aggregate query, NO table export)
#     vs Doc_Skill_k x value counts in the source .sav: 15 x 5 = 75 cells must
#     match exactly, and every item's 5-cell count vector must be unique so the
#     match distinguishes every item from every other.
#  B. The .sav label -> published per-skill means in PLOS ONE Table 3
#     (Doc Skill Mean, 2dp, image table t003), matched by skill LABEL, not order
#     (the paper sorts by mean).
# Not established: nothing about the wording beyond what the .sav labels say.

suppressMessages({ library(irw); library(haven) })

TABLE <- "sinche_2017_skill_development"
URL <- "https://doi.org/10.1371/journal.pone.0185023.s001"

tmp <- tempfile(fileext = ".sav")
download.file(URL, tmp, mode = "wb", quiet = TRUE,
              headers = c("User-Agent" = "IRW-itemtext-verify/1.0"))
sav <- haven::read_sav(tmp)

# --- A. live item x resp counts, server-side ---------------------------------
tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
ref <- tbl$qualified_reference
live <- as.data.frame(irw:::.irw_query_tibble(sprintf(
  "SELECT CAST(item AS STRING) AS item, SAFE_CAST(TRIM(CAST(resp AS STRING)) AS FLOAT64) AS resp, COUNT(*) AS n
   FROM `%s` WHERE resp IS NOT NULL AND TRIM(CAST(resp AS STRING)) NOT IN ('NA','') GROUP BY item, resp", ref)))

mism <- 0
vecs <- character(0)
cat("item          live counts (1..5)              .sav Doc_Skill_k counts (1..5)\n")
for (k in 1:15) {
  lv <- sapply(1:5, function(r) { x <- live$n[live$item == paste0("skill_dev_", k) & live$resp == r]; if (length(x)) x else 0 })
  sv <- sapply(1:5, function(r) sum(as.numeric(sav[[paste0("Doc_Skill_", k)]]) == r, na.rm = TRUE))
  ok <- all(lv == sv)
  if (!ok) mism <- mism + 1
  vecs <- c(vecs, paste(sv, collapse = "/"))
  cat(sprintf("skill_dev_%-3d %-30s %-30s %s\n", k, paste(lv, collapse = "/"),
              paste(sv, collapse = "/"), if (ok) "ok" else "MISMATCH"))
}
extra <- setdiff(unique(live$resp), 1:5)
uniq <- length(unique(vecs)) == 15
cat(sprintf("\nA: %d/15 items match cell-for-cell; live resp outside 1..5: %s; count vectors unique across items: %s\n",
            15 - mism, if (length(extra)) paste(extra, collapse = ",") else "none", uniq))

# --- B. .sav labels -> published Table 3 Doc Skill Means ---------------------
PUB <- c("Discipline-specific knowledge" = 4.73,
         "Ability to gather and interpret information" = 4.69,
         "Ability to analyze data" = 4.66,
         "Oral communication skills" = 4.38,
         "Ability to make decisions and solve problems" = 4.37,
         "Written communication skills" = 4.36,
         "Ability to learn quickly" = 4.18,
         "Ability to manage a project" = 4.18,
         "Creativity/innovative thinking" = 4.12,
         "Ability to set a vision and goals" = 3.99,
         "Time management" = 3.87,
         "Ability to work on a team" = 3.66,
         "Ability to work with people outside the organization" = 3.46,
         "Ability to manage others" = 3.26,
         "Career planning and awareness skills" = 3.05)
worst <- 0; unmatched <- 0
cat("\nB: label (from .sav)                                   published  .sav mean  diff\n")
for (k in 1:15) {
  v <- sav[[paste0("Doc_Skill_", k)]]
  lab <- trimws(sub("\\s*\\(\\d+\\)$", "", attr(v, "label")))
  if (!lab %in% names(PUB)) { unmatched <- unmatched + 1; cat("  UNMATCHED label:", lab, "\n"); next }
  mu <- mean(as.numeric(v), na.rm = TRUE)
  d <- mu - PUB[[lab]]; worst <- max(worst, abs(d))
  cat(sprintf("  %-52s %6.2f %10.3f %6.3f\n", lab, PUB[[lab]], mu, d))
}
cat(sprintf("B: largest |diff| = %.4f (tolerance 0.006 for 2dp rounding); unmatched labels: %d\n", worst, unmatched))
cat("Note: Table 3 ties 'learn quickly' and 'manage a project' at 4.18, so B alone does not separate\n",
    "those two; A does (7201 vs 7241 responses, distinct count vectors).\n", sep = "")

pass <- mism == 0 && !length(extra) && uniq && unmatched == 0 && worst <= 0.006
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

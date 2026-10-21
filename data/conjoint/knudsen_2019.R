##Trust in news sources, paired conjoint in the Norwegian Citizen Panel, from
##Knudsen, E., & Johannesson, M. P. (2019). Beyond the limits of survey experiments: How conjoint
##designs advance causal inference in political communication research. Political Communication,
##36(2), 259-271. https://doi.org/10.1080/10584609.2018.1493009
##Replication data: Harvard Dataverse doi:10.7910/DVN/KVHEKR, CC0 1.0. File read: data-trust.csv
##(3,910 rows = 1,955 respondents x 1 task x 2 sources). Also read as text: polcom-conjoint-figures.R
##(the authors' attribute headers and the figure's x-axis label).
##Usage: Rscript knudsen_2019.R <raw dir> <output dir>
##
##LICENCE NOTE. The deposit's README states that the raw Norwegian Citizen Panel (NCP) file cannot be
##shared openly under data-protection law, so the authors deposited PREPARED analysis files instead.
##The CC0 1.0 licence and this table cover those prepared files; the raw panel file is not in the
##deposit and is not used here. Researchers obtain the raw NCP from Sikt (formerly NSD).
##
##Design: a paired forced-choice conjoint on news sources ("Trust Study" in the paper), fielded in the
##NCP. One task per respondent, two hypothetical sources per task, eight attributes, every level
##present on every profile (no hidden attributes). Attribute names here follow the authors' own figure
##headers in polcom-conjoint-figures.R:
##  attr_advertisement   = "Advertisement"
##  attr_party_support   = "Editor/owner openly supports party" (10 levels incl. "No party")
##  attr_ethics          = "Violations of press ethics last year"
##  attr_comments_field  = "Comments field"
##  attr_readership      = "Readership"
##  attr_publication_form= "Current publication form"
##  attr_entertainment   = "Entertainment news"
##  attr_founded         = "When founded"
##Levels are the deposit's own strings, VERBATIM, including two the authors' plotting code rewrites for
##display only: "Online newpaper" (sic, published as-is here) and the "Have ..." phrasings that the
##figure script converts to "Has ...". Nothing is silently corrected.
##Language: the NCP is fielded in Norwegian, and the deposit ships only the authors' ENGLISH level
##labels, so display_language = no while label_language = en. The Norwegian strings respondents saw
##are not in the deposit.
##Outcome: choice = source_choice, 0/1, the source the respondent picked (exactly one of the two per
##respondent: checked). The question STEM IS NOT RECOVERABLE from the deposit, which ships no codebook
##or instrument, and the NCP wave 8/9 codebook is not public; the paper is paywalled and its
##repository copy is not retrievable. The deposit's own figure labels the quantity "Marginal effect,
##choosing source (%)", so the outcome is recorded as a forced choice of one source, wording unknown.
##The paper frames the study as being about trust, which is where this table's name comes from; the
##deposit does not let us assert the stem said "trust", so design_outcomes.csv records it as unknown.
##resp_choice is dropped as derived: it is the chosen source's number and equals source_choice
##(checked, 0 mismatches in 3,910 rows).
##task / profile: one task per respondent (task = 1, recorded by design); profile = source_id (1/2),
##recorded in the deposit.
##Respondent id: resp_id is 1..1955 sequential, i.e. the AUTHORS' re-keying, NOT the NCP responseid.
##It therefore does NOT link to arnesen_2019_* (whose ids are real NCP ids). The selective-exposure
##file in the same deposit is re-keyed 1..2071 independently, so its overlapping integers are NOT the
##same people.
##Covariates: the trust file ships none (no resp_* columns beyond the id).
##NOT built (held): data-selective.csv in the same deposit. Respondents pick exactly TWO of four
##headlines (2,008 of 2,071 picked two; 63 picked none), which the layout's one-chosen-per-task rule
##has no form for; and the four headlines are drawn from a pool of 755 REAL Norwegian news headlines
##whose source, party, valence and direction are coded features of real articles rather than
##randomised levels, so it also fails the scope test on randomised attributes. Held pending a ruling.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "data-trust.csv"), encoding = "UTF-8", na.strings = c("NA", ""))
stopifnot(nrow(d) == 3910, uniqueN(d$resp_id) == 1955, all(d[, .N, resp_id]$N == 2))
##resp_choice is the chosen source's number: confirm it carries nothing source_choice does not.
stopifnot(all((d$resp_choice == d$source_id) == (d$source_choice == 1)))
t <- d[, .(id = as.integer(resp_id), task = 1L, profile = as.integer(source_id),
           choice = as.integer(source_choice),
           attr_advertisement = source_adds, attr_party_support = source_party,
           attr_ethics = source_ethics, attr_comments_field = source_comments,
           attr_readership = source_readership, attr_publication_form = source_status,
           attr_entertainment = source_soft, attr_founded = source_established)]
ac <- grep("^attr_", names(t), value = TRUE)
stopifnot(!anyNA(t[, ..ac]), !anyNA(t$choice), all(t[, .(s = sum(choice)), .(id, task)]$s == 1))
setorder(t, id, task, profile)
fwrite(t, file.path(out, "knudsen_2019_news_trust.csv"))

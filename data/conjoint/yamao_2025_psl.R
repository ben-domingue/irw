##Iraq Personal Status Law amendment: single-profile rating experiment from
##Yamao, D. (2025). How do religious values affect marriage? Insights from a survey experiment on
##Iraq's Personal Status Law amendment [Data set]. Harvard Dataverse. No article DOI in the deposit.
##Replication data: doi:10.7910/DVN/RIVOJZ, CC0 1.0. Files read: cj_data.csv (the authors' analysis file,
##1,052 respondents x 5 tasks), PSL_Iraq2025.tab (raw Qualtrics export, read ONLY for the displayed Arabic
##text of the attribute levels), cjoint_analysis.Rmd (read as text: variable recodes, outcome name).
##Usage: Rscript yamao_2025_psl.R <dir with f14244277 (cj_data.csv) and f11809547 (PSL_Iraq2025.tab)> <output dir>
##
##Design: each respondent rated five single hypothetical amendments to Iraq's Personal Status Law (task 1-5,
##one profile each) described by four attributes: General_description (2 levels), Religious_customary (2),
##Support_criticism (4), Internal_external (3). Single-profile rating, rating = the authors' `selected`,
##integer 1-5 stored raw (the deposit has no questionnaire: question wording, anchors and direction are not
##documented). Cross-checked: the raw export's Q9-Q13 equal `selected` for tasks 1-5.
##Attribute level text: the displayed Arabic text from the raw export (F-t-k columns pair the authors' English
##tag with the Arabic text shown; the 11 tags map one-to-one to 11 Arabic strings). attr_ columns therefore
##hold Arabic text (label_language ar); the authors' English tags are in the table notes, not the data.
##English glosses (ours): General_description: "de facto legalizes child marriage under 18" / "allows choosing Sunni or
##Shia religious law"; Religious_customary: "recognized under some religious laws" / "practiced as a tribal custom,
##especially in rural areas"; Support_criticism: violation of children's/women's rights / preserves traditional
##tribal social order / protects poor women by placing them with trusted families / deepens sectarian conflict by
##splitting the legal system; Internal_external: evaluated by local groups as a traditional way to help poor
##families / criticized by international or by local human-rights groups as child-marriage legislation.
##Attribute names: attr_general_description, attr_religious_customary, attr_support_criticism, attr_internal_external.
##Attribute order within the raw columns is constant (F-t-1..3 then 4); no display-order record, so no attrpos_.
##Respondents: the raw export has 1,195 rows; cj_data keeps 1,052 (authors' exclusions, filter not documented;
##Finished/attention-check do not reproduce it exactly). We keep the authors' 1,052. id = respondent.
##Covariates (codes mapped from the authors' Rmd recodes): cov_gender (Gender 1 Male, 2 Female), cov_age
##(Age, years), cov_sect (D6: 1 Sunni, 2 Shia, 3 Christian, 4 Kurd, 5 others), cov_urban_rural (D8: 1 Urban,
##2 Rural). Region/education/other attitude codes (D3, D7, Q*) are not mapped by any codebook and are dropped.
##Rows with missing rating (82 of 5,260) are dropped.
##Dropped: IPAddress, lat/long, ResponseId, cintID (panel ID), RecipientEmail/Names (PII in the raw export; the
##raw export is used only for attribute text), dates, derived dummies.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
d <- fread(file.path(raw, "f14244277"), encoding = "UTF-8")
r <- fread(file.path(raw, "f11809547"), skip = 2, header = FALSE, encoding = "UTF-8")
setnames(r, names(fread(file.path(raw, "f11809547"), nrow = 0)))
m <- unique(rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:4, function(k)
  data.table(nm = r[[sprintf("F-%d-%d", t, k)]], tx = r[[sprintf("F-%d-1-%d", t, k)]]))))))[nm != ""]
stopifnot(nrow(m) == 11)
gd <- grep("يشرع", m$tx, value=TRUE); ch <- grep("يسمح باختيار", m$tx, value=TRUE)
rel <- grep("القوانين الدينية", m$tx, value=TRUE); tri <- grep("عرف قبلي", m$tx, value=TRUE)
mp <- c("De fact legalization"=gd, "Right to choose"=ch, "Religious laws"=rel, "Tribal customs"=tri,
 "Violation to women's right"=grep("انتهاك حقوق", m$tx, value=TRUE), "Social order"=grep("النظام التقليدي", m$tx, value=TRUE),
 "Protect poor women"=grep("حماية نساء", m$tx, value=TRUE), "Legal fragmentaion"=grep("تعميق الصراع", m$tx, value=TRUE),
 "Evaluation"=grep("تم تقييم", m$tx, value=TRUE), "International criticism"=grep("الدولية", m$tx, value=TRUE),
 "Domestic criticism"=grep("الإنسان المحلية", m$tx, value=TRUE))
stopifnot(all(sapply(mp, length) == 1))
tr <- trimws(unlist(mp)); names(tr) <- names(mp)
o <- data.table(id = as.integer(d$respondent), task = as.integer(d$task), profile = 1L, rating = as.integer(d$selected))
for (v in c("General_description", "Religious_customary", "Support_criticism", "Internal_external")) {
  x <- tr[trimws(d[[v]])]; stopifnot(!anyNA(x)); o[[paste0("attr_", tolower(v))]] <- unname(x) }
o[, `:=`(cov_gender = c("male","female")[d$Gender], cov_age = as.integer(d$Age),
         cov_sect = c("Sunni","Shia","Christian","Kurd","others")[d$D6], cov_urban_rural = c("Urban","Rural")[d$D8])]
o <- o[!is.na(rating)]
setorder(o, id, task, profile)
fwrite(o, file.path(out, "yamao_2025_iraq_psl_amendment.csv"))

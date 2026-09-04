# verify_chinvararak_2021_phq15.R
#
# What is being verified. The shipped item_text is the PHQ-15's canonical English
# wording (RDC/TMD consortium reprint 12May2013, "no permission required to
# reproduce, translate, display, or distribute"). The study administered a THAI
# PHQ-15 and neither the PLOS deposit nor the supplements carry the Thai stems, so
# the English ships as a translated_substitute. The mapping claim is therefore:
#   phqN in the live IRW table  ==  the N-th canonical PHQ-15 item.
#
# It rests on the deposit's own SPSS VARIABLE LABELS, which give a terse Thai
# symptom keyword per column (mapping_basis = data_labels), plus the fact that
# data/chinvararak_2021_attachment_depression.py melts PHQ_COLS = phq1..phq15 with
# NO renaming, so the IRW code IS the source column name.
#
# Three falsifiable checks below:
#   (A) label route -- all 15 Thai labels printed beside the shipped English; a
#       permuted assignment would show a symptom against the wrong stem.
#   (B) marker route (Step 5b route 7) -- canonical item 4 is "Menstrual cramps ...
#       [women only]" and must be the ONLY item with fewer respondents. Live phq4
#       must have n < 180 while all 14 others sit at 180.
#   (C) option axis -- the .sav VALUE labels tie the three Thai anchors to 0/1/2
#       directly; the shipped option_text/resp pairs must reproduce that map.
#
# What this does NOT establish: it does not independently re-derive the Thai
# keyword -> canonical-item correspondence from the response data. Fourteen of the
# fifteen items are separated by the variable labels alone (a label match, not a
# statistical inference); only phq4 is pinned by the data.

suppressMessages({library(irw); library(haven)})

TABLE  <- "chinvararak_2021_phq15"
SI_URL <- paste0("https://journals.plos.org/plosone/article/file",
                 "?type=supplementary&id=10.1371/journal.pone.0255995.s001")

# Shipped English wording, canonical PHQ-15 order (hard-coded: it came from a form,
# it will not change).
SHIPPED <- c(
 "Stomach pain", "Back pain",
 "Pain in your arms, legs, or joints (knees, hips, etc)",
 "Menstrual cramps or other problems with your periods [women only]",
 "Headaches", "Chest pain", "Dizziness", "Fainting spells",
 "Feeling your heart pound or race", "Shortness of breath",
 "Pain or problems during sexual intercourse",
 "Constipation, loose bowels, or diarrhea", "Nausea, gas, or indigestion",
 "Feeling tired or having low energy", "Trouble sleeping")

# Shipped option_text -> resp (Thai anchors as they appear in the CSV).
SHIPPED_OPT <- c("ไม่รบกวน",
                 "รบกวนเล็กน้อย",
                 "รบกวนมาก")
names(SHIPPED_OPT) <- c("0", "1", "2")

tmp <- tempfile(fileext = ".sav")
utils::download.file(SI_URL, tmp, mode = "wb", quiet = TRUE)
sav <- haven::read_sav(tmp)
cols <- paste0("phq", 1:15)

## (A) variable labels beside the shipped English -------------------------------
cat("== (A) SPSS variable label (deposit) vs shipped item_text ==\n")
labs <- vapply(cols, function(c) {
  l <- attr(sav[[c]], "label"); if (is.null(l)) "" else sub("^phq ", "", l)
}, character(1))
for (i in seq_along(cols))
  cat(sprintf("%-6s %-28s | %s\n", cols[i], labs[i], SHIPPED[i]))
okA <- all(nzchar(labs))
cat(sprintf("all 15 columns carry a distinct Thai symptom label: %s (distinct = %d)\n\n",
            okA && length(unique(labs)) == 15, length(unique(labs))))
okA <- okA && length(unique(labs)) == 15

## (B) marker item -- canonical #4 is women-only --------------------------------
cat("== (B) marker route: canonical item 4 is 'women only' ==\n")
s <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- s$per_item; pi$item <- as.character(pi$item)
live_n <- setNames(as.numeric(pi$n), pi$item)[cols]
sav_n  <- vapply(cols, function(c) sum(!is.na(sav[[c]])), numeric(1))
sexn   <- sum(!is.na(sav$sex) & sav$sex == 2)
for (i in seq_along(cols))
  cat(sprintf("%-6s live n = %4.0f   .sav non-missing = %4.0f   diff = %.0f\n",
              cols[i], live_n[i], sav_n[i], live_n[i] - sav_n[i]))
cat(sprintf("females in deposit (sex==2): %d\n", sexn))
short <- cols[live_n < max(live_n)]
cat(sprintf("items below the modal n: %s (n = %.0f); expected exactly phq4\n",
            paste(short, collapse = ","), min(live_n)))
okB <- identical(short, "phq4") && all(live_n == sav_n)
cat(sprintf("phq4 is the sole reduced-n item AND live n reproduces the .sav exactly: %s\n\n", okB))

## (C) option axis ---------------------------------------------------------------
cat("== (C) option_text <-> resp, from the .sav VALUE labels ==\n")
vl <- attr(sav$phq1, "labels")
for (i in seq_along(vl))
  cat(sprintf("  .sav: %s = %s\n", format(vl[i]), names(vl)[i]))
okC <- all(vapply(names(SHIPPED_OPT), function(k)
             identical(names(vl)[match(as.numeric(k), as.numeric(vl))], SHIPPED_OPT[[k]]),
           logical(1)))
cat(sprintf("shipped option_text/resp pairs reproduce the .sav value labels: %s\n", okC))
cat(sprintf("live resp set {%s} == .sav codes {%s}: %s\n\n",
            paste(sort(s$resp), collapse = ","), paste(sort(as.numeric(vl)), collapse = ","),
            identical(sort(as.numeric(s$resp)), sort(as.numeric(vl)))))

cat("Note: (A) is a label match, not an inference, and it is what separates 14 of the\n",
    "15 items; only phq4 is independently pinned by the data in (B). The shipped\n",
    "English is a substitute for unrecovered Thai stems, so (A) also asserts a\n",
    "keyword->canonical-item correspondence that no statistic here tests.\n", sep = "")

cat(if (okA && okB && okC) "VERDICT: PASS\n" else "VERDICT: FAIL\n")

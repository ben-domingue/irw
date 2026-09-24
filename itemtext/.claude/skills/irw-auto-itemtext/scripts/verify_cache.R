# Cold-cache fallback for verify_<table>.R scripts (irw#2228).
#
# WHY. A verify script's whole point is that a second reader can re-run the
# round's mapping evidence instead of trusting its report. That failed in
# practice: the scripts read their deposit files out of itemtext/.cache/,
# .cache/ is gitignored, and so 24 of the 48 scripts in batches 300-304 died
# on `missing cached deposit file` for everyone except the machine that wrote
# them. Step 1 of the triage protocol was, in effect, unavailable.
#
# So a cache miss is no longer fatal: it is a download. The cache stays the
# fast path -- a reader who has already fetched a deposit does not fetch it
# again -- and a cold cache costs time rather than the whole check.
#
# WHAT THIS IS NOT. It does not make a script's evidence weaker or stronger.
# The comparison is unchanged; only where the left-hand side comes from moves.
# And it is not a general downloader: every URL here is one a human recorded
# with the extraction, so a fetch either returns that file or fails loudly.
#
# Usage, from a verify script (cwd is itemtext/):
#
#   source(".claude/skills/irw-auto-itemtext/scripts/verify_cache.R")
#   sav <- cached_source(".cache/batch_303/EHAS_CFA.sav",
#                        "https://osf.io/download/dysv5/")
#
# `url` may be a vector; they are tried in order, which is what CRAN needs
# (a version lives under src/contrib until it is superseded, then moves to
# src/contrib/Archive/<pkg>/).

.VERIFY_UA <- "IRW-itemtext-verify/1.0 (+https://github.com/ben-domingue/irw)"

# One download, reported rather than swallowed. `download.file()` turns a
# server error into a WARNING about a length mismatch, which says nothing
# useful; curl reports the status code. Both follow redirects, which the
# default method does not reliably do -- Dataverse and OSF both redirect.
.verify_download <- function(u, path, mode = "wb", min_bytes = 1L, tries = 3L) {
    for (attempt in seq_len(tries)) {
        why <- NULL
        if (requireNamespace("curl", quietly = TRUE)) {
            h <- curl::new_handle()
            curl::handle_setopt(h, useragent = .VERIFY_UA, followlocation = TRUE,
                                connecttimeout = 30L, timeout = 1800L)
            why <- tryCatch({ curl::curl_download(u, path, quiet = TRUE, handle = h); NULL },
                            error = function(e) conditionMessage(e))
        } else {
            why <- tryCatch({
                utils::download.file(u, path, mode = mode, quiet = TRUE,
                                     method = "libcurl",
                                     headers = c("User-Agent" = .VERIFY_UA))
                NULL
            }, error = function(e) conditionMessage(e),
               warning = function(w) conditionMessage(w))
        }
        if (is.null(why) && file.exists(path) && file.info(path)$size >= min_bytes) {
            return(list(ok = TRUE, why = ""))
        }
        if (is.null(why)) why <- sprintf("empty or short file (< %d bytes)", min_bytes)
        unlink(path)
        # 5xx and 429 are the deposit having a bad minute, not the URL being
        # wrong; a short wait costs less than a failed check.
        if (attempt < tries && grepl("50[0-9]|429|timed? ?out|Recv failure", why)) {
            Sys.sleep(5 * attempt)
            next
        }
        return(list(ok = FALSE, why = why))
    }
    list(ok = FALSE, why = "exhausted retries")
}

cached_source <- function(path, url = NULL, mode = "wb", min_bytes = 1L) {
    if (file.exists(path) && file.info(path)$size >= min_bytes) return(path)
    if (is.null(url) || !length(url)) {
        stop("missing cached deposit file and no source URL is recorded for it: ",
             path, "\n  Fetch it by hand from the source named in this batch's ",
             "provenance.csv, or add the URL to this script's cached_source() call.")
    }
    dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
    why <- character(0)
    for (u in url) {
        message("  cache miss, fetching: ", path, "\n    <- ", u)
        res <- .verify_download(u, path, mode, min_bytes)
        if (isTRUE(res$ok)) return(path)
        why <- c(why, sprintf("%s -- %s", u, res$why))
        unlink(path)
    }
    stop("could not fetch the deposit file and the cache is cold: ", path,
         "\n  tried:\n    ", paste(why, collapse = "\n    "),
         "\n  The check is not run rather than run against nothing. A source ",
         "that is temporarily down is the common case -- retry before ",
         "concluding the evidence is unreachable.")
}

# Some deposits publish no per-file endpoint -- ResearchBox serves the whole
# box as one zip -- so the members are extracted from a single download. The
# zip itself is NOT kept: it is the members that are the evidence, and a
# 140 MB archive is not worth caching for three small files.
cached_zip_members <- function(paths, members, zip_url, min_bytes = 1L) {
    stopifnot(length(paths) == length(members))
    if (all(file.exists(paths) & file.info(paths)$size >= min_bytes)) return(paths)
    tmp <- tempfile(fileext = ".zip")
    on.exit(unlink(tmp), add = TRUE)
    message("  cache miss, fetching the deposit archive for ", length(paths),
            " file(s)\n    <- ", zip_url)
    ok <- tryCatch({
        utils::download.file(zip_url, tmp, mode = "wb", quiet = TRUE,
                             headers = c("User-Agent" = .VERIFY_UA))
        file.exists(tmp) && file.info(tmp)$size > 0
    }, error = function(e) FALSE, warning = function(w) FALSE)
    if (!isTRUE(ok)) {
        stop("could not fetch the deposit archive and the cache is cold.\n  tried: ",
             zip_url)
    }
    inside <- utils::unzip(tmp, list = TRUE)$Name
    for (i in seq_along(paths)) {
        hit <- inside[endsWith(inside, members[i])]
        if (!length(hit)) stop("not in the deposit archive: ", members[i])
        dir.create(dirname(paths[i]), recursive = TRUE, showWarnings = FALSE)
        con <- utils::unzip(tmp, files = hit[1], exdir = tempdir(), junkpaths = TRUE)
        file.copy(con, paths[i], overwrite = TRUE)
        unlink(con)
    }
    paths
}


# The OTHER cold-start problem, and the larger one. A verify script compares
# the live response table against the __items.csv the round shipped -- but
# clear_uploaded_itemtables.py deletes that CSV once the upload is confirmed,
# by design, so every verify script for an uploaded table loses its left-hand
# side. Across the corpus 76 scripts read a local __items.csv and in batches
# 300-304 only the four HELD tables still have one.
#
# The right left-hand side after upload is what actually shipped, so this
# falls back to the live item-text shard. NOTE THAT THIS DOES NOT WORK YET
# FOR EVERY TABLE: irw::irw_itemtext() reads irw_text and not irw_text_2, and
# all of batches 300-304 went to irw_text_2, so for those it returns nothing.
# That is an Rpkg gap, not something a verify script can route around -- the
# same one that makes irw_list_itemtext_tables() report 695 of ~1,250. Until
# it is closed the message below says so, which is worth more than
# "cannot open the connection".
shipped_items <- function(table, path = NULL) {
    if (!is.null(path) && file.exists(path)) {
        return(utils::read.csv(path, stringsAsFactors = FALSE,
                               na.strings = "NA", encoding = "UTF-8"))
    }
    x <- tryCatch(as.data.frame(irw::irw_itemtext(table)),
                  error = function(e) NULL)
    if (is.null(x) || !nrow(x)) {
        stop("no shipped item text to compare against.\n",
             "  The local CSV is gone (cleared after upload, which is intended),",
             "\n  and irw::irw_itemtext(\"", table, "\") returned nothing.",
             "\n  If this table is in irw_text_2, that is the known shard gap ",
             "rather than a missing upload:\n  irw_itemtext() reads irw_text ",
             "only. Check itemtext/live_tables.csv for the shard.")
    }
    x
}

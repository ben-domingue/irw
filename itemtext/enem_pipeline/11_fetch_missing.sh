#!/bin/bash
# Fetch the booklet PDFs INEP does not ship inside the 2024/2025 microdata zips,
# and any other missing source. INEP rate-limits: it reset every connection
# after ~6 requests, including ones that had just succeeded. So: one file at a
# time, 90s apart, with retries, and it is safe to re-run -- existing files of
# non-zero size are skipped.
#
# download.inep.gov.br sends only its leaf certificate and omits the
# intermediate, so every client fails verification by default. We complete the
# chain from the certificate's own AIA extension (RNP ICPEdu -> GlobalSign Root
# R46, which is in the system store), so this is verified, not --insecure.
set -u
E=$HOME/enem
W=$HOME/enem/itemtext_run/allyears
BUNDLE=$W/inep_chain.pem

if [ ! -s "$BUNDLE" ]; then
  echo "building the certificate chain"
  openssl s_client -connect download.inep.gov.br:443 -servername download.inep.gov.br \
    </dev/null 2>/dev/null | openssl x509 -out "$W/leaf.pem"
  url=$(openssl x509 -in "$W/leaf.pem" -noout -text | sed -n 's|.*CA Issuers - URI:\(http[^ ]*\).*|\1|p' | head -1)
  curl -sS --max-time 60 -o "$W/inter.crt" "$url"
  openssl x509 -inform DER -in "$W/inter.crt" -out "$W/inter.pem" 2>/dev/null \
    || openssl x509 -in "$W/inter.crt" -out "$W/inter.pem"
  cat /etc/ssl/certs/ca-certificates.crt "$W/inter.pem" > "$BUNDLE"
fi

B=https://download.inep.gov.br/enem/provas_e_gabaritos
fetch() {  # year filename
  local y=$1 f=$2
  local d="$E/extracted_$y/microdados_enem_$y/PROVAS E GABARITOS"
  [ -d "$d" ] || d="$E/extracted_$y/PROVAS E GABARITOS"
  mkdir -p "$d"
  if [ -s "$d/$f" ]; then echo "  have  $f"; return 0; fi
  local code
  code=$(curl -sS -L --max-time 300 --retry 3 --retry-delay 30 --retry-all-errors \
           --cacert "$BUNDLE" -o "$d/$f" -w '%{http_code}' "$B/$f" 2>/dev/null)
  if [ "$code" = "200" ] && [ -s "$d/$f" ]; then
    echo "  ok    $f  $(stat -c%s "$d/$f") bytes"
  else
    rm -f "$d/$f"; echo "  FAIL  $f  (HTTP $code)"
  fi
  sleep 90
}

# 2024/2025: the zips ship no provas at all, though their LEIA-ME lists them.
# Needed for the items the accessibility booklet swaps away (2024: 4, 2025: 3).
fetch 2024 2024_PV_impresso_D1_CD1.pdf
fetch 2024 2024_PV_impresso_D2_CD5.pdf
fetch 2025 2025_PV_impresso_D1_CD1.pdf
fetch 2025 2025_PV_impresso_D2_CD5.pdf
echo "FETCH_DONE"

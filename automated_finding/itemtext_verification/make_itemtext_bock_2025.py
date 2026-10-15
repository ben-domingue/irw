#!/usr/bin/env python3
"""Item text for bock_2025_epistemic_beliefs and bock_2025_responsibility (Zenodo
10.5281/zenodo.14803512). Survey-Questionnaire.pdf prints every item with its code (Q1_1 .. Q5_B2),
which are the data columns, so the tie is explicit. Parsed with pdftotext. English administration.
"""
import re
import subprocess

from _itemtext_writer_c import load_script, row, write

mod = load_script("bock_2025_energy_modelling")
PDF = mod.RAW_DIR / "Survey-Questionnaire.pdf"
LIK = {1: "Strongly disagree", 2: "Somewhat disagree", 3: "Neither agree nor disagree", 4: "Somewhat agree", 5: "Strongly agree"}
EB_PROMPT = ("Consider the field of mathematical modelling and scenario development to guide long-term energy "
             "planning and climate policy decisions. Please rate your agreement with the following statements.")
RESP_PROMPT = {
    "Q3_A": "A decision-maker commissions a modeller to develop a model and generate model-based scenarios; they can exchange information throughout. How is the responsibility for the aspects below divided between the modeller and the decision-maker? (0 = modeller .. 10 = decision-maker)",
    "Q3_B": "In this case, how balanced is the distribution of information between the modeller and the decision-maker on the aspects below? (0 = modeller has more .. 10 = decision-maker has more)",
    "Q4_A": "As before, but the modeller does not come from the same country and cultural background as the decision-maker. How is the responsibility for the aspects below divided between the modeller and the decision-maker? (0 = modeller .. 10 = decision-maker)",
    "Q4_B": "In this case, how balanced is the distribution of information between the modeller and the decision-maker on the aspects below? (0 = modeller has more .. 10 = decision-maker has more)",
    "Q5_A": "A scenario-user consults published model-based scenarios they were not involved in producing. How is the responsibility for the use of the scenario results divided between the modeller and the scenario-user? (0 = modeller .. 10 = scenario-user)",
    "Q5_B": "In this case, how balanced is the distribution of information between the modeller and the scenario-user on the aspects below? (0 = modeller has more .. 10 = scenario-user has more)",
}


def items():
    txt = subprocess.run(["pdftotext", "-raw", str(PDF), "-"], capture_output=True, text=True, check=True).stdout
    txt = re.sub(r"November 2023.*?Page \d+ of 10\s*Questionnaire: Narratives in Model-Based Scenarios", " ", txt, flags=re.S)
    out = {}
    for m in re.finditer(r"(Q[1-5]_[AB]?\d+)\.\s+(.*?)\s*\[(?:L|S\d)\.[AB]?\d+\]", txt, flags=re.S):
        out[m[1]] = " ".join(m[2].replace("o o o o o", " ").split())
    return out


def main():
    it = items()
    assert len(it) == 37, (len(it), sorted(it))
    eb, rs = [], []
    for code, stem in it.items():
        if code.startswith(("Q1_", "Q2_")):
            for r, lab in LIK.items():
                eb.append(row("bock_2025_epistemic_beliefs", "bock_2025_epistemic_beliefs_1", code,
                              "Epistemic beliefs about energy modelling and scenarios, 18 agreement items", "en", r, stem,
                              option_text=lab, section_prompt=EB_PROMPT))
        else:
            sec = code[:4]
            for r in range(0, 11):
                rs.append(row("bock_2025_responsibility", f"bock_2025_responsibility_{sec}", code,
                              "Perceived responsibility and information asymmetry between modeller and decision-maker / scenario-user, 19 sliders 0-10",
                              "en", r, stem, section_prompt=RESP_PROMPT[sec]))
    write("bock_2025_epistemic_beliefs", eb)
    write("bock_2025_responsibility", rs)


if __name__ == "__main__":
    main()

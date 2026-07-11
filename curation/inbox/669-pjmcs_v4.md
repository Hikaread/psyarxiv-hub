---
osf_id: pjmcs_v4
title: Automating Abstract Screening in Research Synthesis using Large Language Models: A Tutorial and Proof-of-Concept Study
authors: Mirka Henninger, Jan Radek, Jean-Paul Snijder-Steinhilber, Martin Pauly
date_posted: 2026-07-11
source_date: 2026-06-18
link: https://osf.io/preprints/psyarxiv/pjmcs_v4/
categories: Other Clinical
number: 669
---

## Summary
This paper provides a **comprehensive tutorial and proof-of-concept study** for using **Large Language Models (LLMs)** to automate **abstract screening** in systematic reviews and meta-analyses. The authors propose a structured workflow: (1) divide the corpus into **training**, **test**, and **screening sets**; (2) manually rate training and test abstracts; (3) iteratively engineer and evaluate **prompts** on training data, then test on held-out data; (4) screen remaining abstracts automatically. A key innovation is the **uncertainty quantification** approach: running the model **10 times per abstract** and flagging inconsistent classifications for manual review. The proof-of-concept used **1,992 abstracts** from a recent meta-analysis, comparing **closed-source models** (GPT-4, Claude) and **open-weight models** (LLaMA, Gemma). LLM-assisted screening achieved accuracy **comparable to human raters** while substantially reducing time and cost. The authors provide **R scripts and implementation guidance** on GitLab and emphasize that this represents an **initial step** requiring continued validation as LLM technology evolves.

## Clinical Insight
For clinicians and researchers who conduct **systematic reviews** — increasingly a core skill in **evidence-based practice** — this tutorial offers a practical pathway to dramatically reduce the **most time-consuming step** of the review process. Abstract screening typically requires hundreds of hours of expert time and is prone to **fatigue-related errors**. The proposed workflow is particularly valuable for **clinical psychology reviews** where the literature is vast and inclusion criteria often involve nuanced clinical judgment (e.g., distinguishing "clinical sample" from "community sample with elevated scores"). The **uncertainty quantification** approach (running the model multiple times) is a clever solution that preserves human oversight for ambiguous cases — exactly the cases where clinical expertise matters most. The demonstration that **open-weight models** run locally can achieve reasonable performance is important for reviews involving **sensitive clinical data** that cannot be sent to commercial APIs. For clinical training programs, teaching LLM-assisted screening could be integrated into **research methods curricula**, preparing the next generation of evidence-based practitioners to work efficiently with AI tools. The authors appropriately caution that LLM screening should **complement, not replace**, human judgment.

## Methodology Note
This is an other-type paper (tutorial/methodology with proof-of-concept).

__Measurement Validity__: The proof-of-concept uses human-rated abstracts as the gold standard for comparison.
Sensitivity, specificity, and F1 scores are reported across models and prompt configurations.
The comparison between closed-source and open-weight models provides practical guidance on model selection.

__Open Science__: R scripts and prompt templates are provided on GitLab.
The paper itself is openly accessible on PsyArXiv.
This is an excellent example of open methodology for a methods paper.
The training/test/split approach supports reproducibility of the screening workflow.

__Participant Transparency__: The proof-of-concept used 1,992 abstracts from a meta-analysis in psychology.
The specific meta-analysis topic and inclusion criteria are described in the full text.
The human raters' characteristics and inter-rater reliability are important details for evaluating the gold standard.

## Relevant For
- Systematic review and meta-analysis authors
- Evidence-based practice researchers
- Clinical psychologists conducting literature reviews
- Research methods instructors
- Health technology assessment professionals

## Notes
Highly practical tutorial with working code. The uncertainty quantification approach is innovative and pragmatic. Essential reading for anyone planning a systematic review in psychology.
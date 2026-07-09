---
number: 623
osf_id: qdmrf_v2
title: Old Test, New Tricks: Using Large Language Models to Generate New Divergent Thinking Test Items
authors: Averie Linnell, Simone Luchini, Austin Swanson, Roni Reiter-Palmon, Roger Beaty, Antonio Laverghetta Jr.
date_posted: 2026-07-06
source_date: 2026-07-06
categories: Psychopathology & Assessment
link: https://osf.io/preprints/psyarxiv/qdmrf_v2
---

## Summary

This study evaluated whether **large language models (LLMs)** can generate psychometrically valid items for the **Consequences task** of **diverggent thinking** assessment, comparing LLM-generated items to traditional human-written items from **Guilford's** original set. A sample of **192 undergraduates** from two universities completed six Consequences tasks — two human-written, two standard LLM-generated ("Guilford style"), and two **genre-inspired** (sci-fi and fantasy themes) — along with validation measures including the **Alternative Uses Task (AUT)**, **Raven's Progressive Matrices**, **Openness to Experience** (DeYoung's scale, alpha = .76-.77), **Need for Cognition** (NCS-6, alpha = .79), **Creative Self-Efficacy** (alpha = .68), and the **Biographical Inventory of Creative Behaviors (BICB)**.

LLM-generated items elicited **significantly higher fluency** (d = 0.29), **flexibility** (d = 0.40), and **originality** (d = 0.14) compared to human-written items. Repeated-measures ANOVAs showed significant differences across tasks for all three metrics (fluency: F(5, 948) = 24.03, p < .001, partial eta-squared = .11; flexibility: F(5, 948) = 17.64, p < .001, partial eta-squared = .09; originality: F(5, 948) = 7.49, p < .001, partial eta-squared = .04). **Genre-inspired items** produced the highest enjoyment (M = 3.53 for fantasy) and inspiration ratings (M = 3.78 for fantasy), with significantly higher positive emotional valence.

Convergent validity was strong: **AUT fluency** correlated with Consequences fluency at r = .51 (human) and r = .62 (LLM), while **Openness to Experience** correlated with LLM-item originality at r = .30 (p < .001). Importantly, **genre familiarity did not moderate** performance on genre-style items (interaction b = 0.02-0.06, all p > .18), demonstrating **measurement invariance** — participants unfamiliar with sci-fi or fantasy were not disadvantaged. Items were generated using **GPT-3.5-turbo** and **Llama-3-70b-instruct**, with content review by three graduate raters assessing scope, magnitude, accessibility, and controversy.

## Methodology Note

__Paper Type__: quantitative_experimental

__Statistical Power__: Adequate. A sensitivity analysis indicated 80% power to detect d = 0.20 at alpha = .05 with N = 192, which is sufficient for the reported effects. However, the small number of items per condition (2 human, 4 LLM) limits precision of item-level comparisons.

__Preregistration__: Not mentioned. The study does not appear to be preregistered, which is a limitation given the multiple comparisons across item types and validity measures.

__Effect Sizes__: Well reported. Effect sizes include partial eta-squared values for ANOVAs (.04-.11), Cohen's d for planned contrasts, and Pearson's r for validity correlations. This is a strength of the paper.

__Statistical Rigor__: Adequate with caveats. Repeated-measures ANOVA is appropriate for within-person comparisons. The planned contrasts comparing item types are methodologically sound. However, only one of 135 generated LLM items came from Llama-3-70b, so the study effectively compares items from a single model (GPT-3.5-turbo) against human items. The brief 12-item **Raven's Progressive Matrices** administered under a 3-minute time limit may not have reliably captured fluid intelligence.

__Measurement Validity__: Mixed strength. The AUT, BICB, and personality measures are well-established. Inter-rater reliability for originality scoring was acceptable (ICC = .71-.77 for Consequences, .83-.84 for CPS). However, the genre familiarity measure was developed ad hoc for this study (single item per genre), and the creative self-efficacy scale had relatively low reliability (alpha = .68). The generalizability of findings is limited by a predominantly white female undergraduate sample.

__Open Science__: Adequate. Data and analysis code are available on OSF. The authors also disclosed their use of Claude AI for writing assistance and code drafting.

__Participant Transparency__: Partially adequate. Sample size, age (M = 20.08, SD = 4.78), and recruitment method (SONA, two universities) are reported. However, detailed demographic breakdowns beyond noting the sample was majority white women would improve transparency.

## Clinical Insight

While this study focuses on cognitive assessment rather than clinical populations, it has meaningful implications for **clinical assessment practice**. Divergent thinking tests are used in **neuropsychological assessment**, **occupational therapy**, and increasingly in research on **psychopathology and creativity** (e.g., in bipolar disorder, schizophrenia-spectrum conditions). The limited item pool for Consequences tasks has been a persistent problem — repeated use of the same prompts introduces **practice effects** and **item exposure** risks that compromise validity in clinical and high-stakes settings.

The finding that LLMs can generate valid items with comparable or superior psychometric properties addresses a practical bottleneck. For clinicians and researchers who use creativity assessments, this means **larger, more diverse item banks** can be developed efficiently, enabling **parallel forms** for repeated testing and reducing the risk that patients remember prior items. The genre-inspired items' success — with high engagement and no unfair advantage for genre-familiar participants — is particularly promising, suggesting that item content can be expanded beyond the narrow traditional scope. Clinicians should be aware that **automated item generation** is rapidly advancing and may soon change how cognitive and creativity assessments are constructed and deployed.

## Relevant For
- Clinical psychologists using cognitive or creativity assessments
- Neuropsychologists interested in divergent thinking measures
- Assessment developers and psychometricians
- Researchers studying creativity and psychopathology
- Those interested in AI applications to psychological assessment

## Notes
Summary based on full PDF extraction (53 pages).
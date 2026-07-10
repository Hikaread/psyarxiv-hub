---
number: 647
osf_id: qwuvj_v2
title: Non-Ergodicity Sets a Structural Floor on Replicability
authors: Steven C. Hayes; Joseph Ciarrochi; Cristobal Eduardo Hernandez Contreras; Stefan G. Hofmann; Clarissa W. Ong; Baljinder K. Sahdra
date_posted: 2026-07-09
source_date: 2026-07-09
link: https://osf.io/preprints/psyarxiv/qwuvj_v2
categories: Other Clinical
---

## Summary
This theoretical paper by **Steven C. Hayes, Joseph Ciarrochi, and colleagues** argues that the **replication crisis** in the behavioral sciences is partly **structural and irreducible**: when psychological processes are **non-ergodic** (differing across individuals and over time), standard **convenience sampling** produces **estimand drift**, creating a mathematically guaranteed floor on replicability.
The authors derive a **closed-form expression** for this replication-failure floor using a simple two-class model: a fraction of people have a positive within-person effect, while the remainder have a negative effect.
Under **convenience sampling**, the composition of these subgroups varies randomly across studies, meaning each study estimates a **different population quantity** — increasing sample size only pins down the wrong target more precisely.
For plausible parameters (minority-sign mass near **0.42**, moderate convenience sampling), the model predicts a **~32% failure rate** for perfectly designed, perfectly powered studies, rising to **~52%** when finite-sample noise and significance selection are added — closely matching the observed **~51% failure rate** reported by Tyner et al. (2026) in *Nature*.
The authors propose that the solution is an **idionomic approach**: measuring processes **longitudinally within individuals** first, modeling at that level, and then generalizing across people — rather than assuming a single group-level effect applies to everyone.
A comprehensive **table of idionomic methods** is provided, ranging from **i-ARIMAX** (idiographic bivariate time-series modeling) and **personalized network modeling** (graphicalVAR) to **GSOM** (growing self-organizing maps for clustering person-level features) and **GIMME** (group iterative multiple model estimation).
The open-source **idionomics R package** (Hernandez et al., 2026) is introduced as a practical tool for estimating within-person effects and detecting **sign-divergent cases** (individuals whose effects run counter to the group average).

## Clinical Insight
This paper has **profound implications for evidence-based clinical practice**.
If a substantial portion of replication failure is **structural rather than methodological**, then even the most rigorously conducted **RCTs and meta-analyses** may produce findings that **do not apply to the individual client** sitting in front of the therapist.
The authors' argument directly supports the growing **process-based therapy (PBT)** movement: if group-level effect sizes describe almost no individual, then **treatment manuals based on averaged outcomes** may be inherently limited, and clinicians should instead focus on **identifying the specific processes** that drive change for each particular client.
The **idionomic toolkit** (i-ARIMAX, tsBoruta, graphicalVAR, GSOM, GIMME) provides a concrete methodological pathway for **personalized treatment planning**: clinicians and researchers can use intensive longitudinal data (e.g., EMA, daily diaries) to model **within-person process dynamics** and tailor interventions accordingly.
The paper's key message — "one size fits none" — is both a **critique of the dominant nomothetic paradigm** and a **call to action** for the clinical psychology community to invest in idiographic methods that can bridge the gap between population-level evidence and individual-level care.

## Methodology Note
This is an other-type paper (theoretical/methodological).

__Statistical Rigor__: The **mathematical derivation** of the replication-failure floor is rigorous and clearly presented, using a Beta-distribution model of convenience sampling to derive a closed-form expression for the probability of sign-reversal across studies.
**Monte Carlo simulations** (15,000 simulated studies per condition) validated the analytic predictions and demonstrated how the structural ceiling manifests at finite sample sizes.
The model was compared against the **empirical replication rates** from Tyner et al. (2026), showing close correspondence for plausible parameter values.
A limitation is that the two-class model is intentionally simplified; real idionomic distributions are likely **continuous and multimodal**, which the authors acknowledge but do not fully model.

__Measurement Validity__: Not applicable to this theoretical paper.
However, the paper provides a comprehensive **review of idionomic measurement tools** (Table 1), each with published validation evidence.
The **idionomics R package** includes a sign divergence test (**SDEN**) that quantifies the proportion of significant minority-sign effects, directly operationalizing the paper's theoretical construct.

__Open Science__: The paper is available as a **PsyArXiv preprint**.
**Simulation code** is deposited at OSF with a view-only link, supporting reproducibility of the Monte Carlo results.
The **idionomics R package** is open-source and available on **CRAN**.
The authors transparently disclose that a **large language model (Claude, Anthropic)** was used as an analytic and drafting aid, with full human oversight and independent verification of all mathematics and references.

__Participant Transparency__: Not applicable to this theoretical paper.
The empirical grounding draws on published datasets from prior idionomic studies (Sahdra et al., 2024; Ciarrochi et al., 2024), which are cited but not re-analyzed here.

## Relevant For
- Clinicians interested in personalized and process-based approaches to therapy
- Researchers concerned with the replicability and generalizability of clinical trial findings
- Methodologists working on idiographic and intensive longitudinal methods
- Practitioners questioning the applicability of group-level evidence to individual clients

## Notes
Full PDF was available and read. This is a high-impact theoretical paper by leading figures in clinical psychology (Hayes, Hofmann, Ciarrochi) that challenges fundamental assumptions about how clinical research evidence is generated and applied. The idionomic methods table is a particularly useful reference for practitioners looking to adopt personalized approaches.
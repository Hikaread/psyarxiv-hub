---
osf_id: drchp_v1
number: 609
date_posted: 2026-06-09
source_date: June 2026
title: Representational Idiosyncrasy of Psychopathology Across Text Embedding Models: Implications and Practical Suggestions for Clinical Psychological Science
authors: Jared T. Gabrielli, Whitney Ringwald, Camilo J. Ruggero, Leonard J. Simms, Roman Kotov, Nicholas R. Eaton
categories: Psychopathology & Assessment
---

## Summary
This study systematically examined how **21 text embedding models** represent **405 items** from the **HiTOP-SR** (Hierarchical Taxonomy of Psychopathology -- Self-Report), a non-public measure absent from model training data. Using **exploratory factor analysis** of item-level embedding representations at both global and domain-specific levels, the study revealed substantial **structural inconsistency** across models. Globally, structural congruence (using **Tucker's congruence coefficient**) frequently fell below the meaningful threshold of **CC < .85**, although broad two-factor solutions showed strong cross-model convergence. Domain-specific congruence varied considerably: **Anankastia** showed strong convergence across models, while **Antagonism** showed weak convergence. The findings demonstrate that text embedding models lack a **shared representational framework** for psychopathology, producing structures that are **idiosyncratic** and sensitive to model-specific features and methodological choices.

## Clinical Insight
As **large language models** are increasingly integrated into clinical tools -- from chatbot-based interventions to automated symptom screening -- this study delivers a critical caution: different AI models fundamentally **disagree** on how psychological constructs are organized. A clinical tool built on one embedding model may categorize a patient's symptoms differently than one built on another, with no obvious way to detect the discrepancy. The variable performance across HiTOP domains is particularly concerning: an LLM-based assessment tool might reliably capture **anankastic traits** but poorly distinguish **antagonistic** features, potentially leading to mischaracterization of personality pathology. For clinicians evaluating or adopting AI-based tools, the study underscores the need for **rigorous model-specific validation** before clinical deployment. The authors advocate for using embedding-based approaches (which are more stable than generative text outputs) and for conducting **cross-model consistency checks** as a standard quality assurance step. This work is essential reading for anyone involved in developing or procuring AI-driven clinical assessment tools.

## Relevant For
- Developers of AI-based clinical assessment tools
- Clinicians evaluating LLM-based mental health applications
- Psychopathology researchers using computational methods
- Clinical informaticists concerned with AI model reliability

## Notes
Full 57-page PDF was available. The study provides a systematic framework for evaluating LLM representational consistency.
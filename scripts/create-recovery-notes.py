#!/usr/bin/env python3
"""
Create curation notes for the 15 recovered discarded papers.
"""
import os
import json
import requests

PSYARXIV_HUB = os.path.expanduser("~/my-project/psyarxiv-hub")
PAPERS_JSON = os.path.join(PSYARXIV_HUB, "data", "papers.json")
INBOX = os.path.join(PSYARXIV_HUB, "curation", "inbox")

RECOVERED = [
    {
        "compact_id": "fhvnz",
        "title": "Current distress does not moderate the efficacy of cognitive reappraisal",
        "date": "2026-06-24",
        "category": "Therapeutic Modalities",
        "summary": "Investigates whether the efficacy of cognitive reappraisal — a core technique in CBT — is moderated by the individual's current level of distress. Using experimental methods, the authors test whether cognitive reappraisal works equally well regardless of how distressed a person is in the moment, challenging assumptions about when emotion regulation strategies should be deployed in therapy.",
        "clinical_insight": "Clinicians often hesitate to use cognitive reappraisal with highly distressed clients, assuming it may be less effective during acute distress. This study suggests that distress level does not significantly moderate reappraisal efficacy, supporting the use of CBT techniques even during sessions where clients present with high emotional arousal. This finding encourages therapists to maintain consistent application of reappraisal-based interventions rather than switching strategies based on momentary distress intensity.",
        "relevant_for": "CBT practitioners working with anxiety and mood disorders",
        "score": 14,
    },
    {
        "compact_id": "r29tv",
        "title": "Memory-Based Learning Disabilities: A Syndrome Without a Pigeonhole. Towards a Mechanism-Based Diagnostic Framework",
        "date": "2026-06-24",
        "category": "Neurodivergence",
        "summary": "Proposes a new mechanistic diagnostic framework for memory-based learning disabilities (MBLD), arguing that current diagnostic categories (such as specific learning disorder in DSM-5) fail to capture the heterogeneity of memory-related learning difficulties. The paper draws on clinical cases involving trauma, dissociation, and chronic conditions to illustrate how memory impairments can manifest across multiple diagnostic boundaries.",
        "clinical_insight": "Many clients presenting with learning difficulties do not fit neatly into existing diagnostic categories. This framework helps clinicians recognize that memory-based learning disabilities may co-occur with and be maintained by factors like chronic stress, trauma, and dissociation. Assessment should include thorough memory profiling rather than relying solely on IQ-achievement discrepancy models, enabling more targeted intervention planning.",
        "relevant_for": "Neuropsychologists and clinicians assessing learning disabilities in adults",
        "score": 13,
    },
    {
        "compact_id": "3q9dk",
        "title": "From backlog to blind spots: why neurodevelopmental pathway reform must start with system mapping",
        "date": "2026-06-28",
        "category": "Neurodivergence",
        "summary": "An opinion piece arguing that neurodevelopmental assessment pathways (for autism and ADHD) are failing due to systemic issues that go beyond simple capacity constraints. Using system mapping methodology, the authors identify how current referral-to-diagnosis pathways create blind spots that particularly disadvantage certain populations, and propose a systems-level reform approach.",
        "clinical_insight": "Understanding the systemic failures in neurodevelopmental diagnostic pathways helps clinicians contextualize the long wait times their clients experience and identify where advocacy can be most effective. The system mapping approach reveals that simply adding more assessors will not solve the crisis — the pathway itself needs redesign. Clinicians can use these insights to set realistic expectations with clients and to contribute to service-level improvement efforts.",
        "relevant_for": "Clinicians involved in autism and ADHD assessment pathways",
        "score": 11,
    },
    {
        "compact_id": "pvyfm",
        "title": "The Role of Interoceptive Awareness and Relationship Satisfaction in Female Orgasm Experience",
        "date": "2026-06-25",
        "category": "Somatic & Functional",
        "summary": "Examines how interoceptive awareness — the ability to perceive internal bodily signals — interacts with relationship satisfaction to predict female orgasm experience. Using standardized measures of interoception and relationship quality, the study investigates whether body awareness plays a mechanistic role in sexual functioning beyond relational factors alone.",
        "clinical_insight": "Sexual difficulties are common presenting concerns in therapy yet often treated primarily through relational interventions. This research suggests that interoceptive awareness is a distinct predictor of sexual satisfaction, pointing to body-focused interventions (such as mindfulness-based or sensate focus approaches) as complementary to couples work. Clinicians treating sexual dysfunction should assess interoceptive abilities and consider incorporating body awareness exercises into treatment plans.",
        "relevant_for": "Sex therapists and couples counselors addressing sexual dysfunction",
        "score": 7,
    },
    {
        "compact_id": "ebawx",
        "title": "The Fearbase: a dynamically growing database and collaborative consortium for experimental work on human fear conditioning research",
        "date": "2026-06-25",
        "category": "Anxiety & OCD",
        "summary": "Introduces The Fearbase, an open collaborative database for human fear conditioning research. The paper describes the database architecture, the consortium of contributing labs, and demonstrates how pooled data from fear conditioning paradigms can advance understanding of anxiety mechanisms, treatment response prediction, and individual differences in fear learning and extinction.",
        "clinical_insight": "Fear conditioning and extinction mechanisms underpin exposure-based therapies for anxiety disorders. This database provides a resource for clinicians and researchers to understand individual differences in fear learning that predict treatment outcomes. Clinicians using exposure therapy can reference Fearbase findings to inform case conceptualization — for instance, understanding that some patients show enhanced fear acquisition or impaired extinction, which may indicate need for augmented exposure protocols or adjunctive pharmacotherapy.",
        "relevant_for": "Researchers and clinicians specializing in anxiety treatment and exposure therapy",
        "score": 7,
    },
    {
        "compact_id": "nctgh",
        "title": "Predicting Effects of a Computational Empathetic Bot",
        "date": "2026-06-24",
        "category": "Therapeutic Modalities",
        "summary": "Investigates whether an AI-powered empathetic chatbot can produce measurable effects on user psychological states. The study designs a computational empathetic agent and tests its impact on anxiety, stress, and perceived support, exploring the potential for digital tools to extend therapeutic reach in mental health care delivery.",
        "clinical_insight": "AI chatbots are increasingly being deployed in mental health settings, yet evidence for their clinical efficacy remains limited. This study contributes to the evidence base by examining what specific components of computational empathy produce measurable psychological effects. Clinicians considering recommending digital mental health tools to clients can use these findings to evaluate which chatbot features are likely to be beneficial versus potentially harmful.",
        "relevant_for": "Clinicians interested in digital mental health interventions and AI-assisted therapy tools",
        "score": 6,
    },
    {
        "compact_id": "n9gfq",
        "title": "Subjective Effects and Characteristics of Salvia Divinorum Use from a Retrospective Largescale Survey",
        "date": "2026-06-24",
        "category": "Addiction & Substance Use",
        "summary": "A large-scale retrospective survey examining the subjective effects, patterns of use, and user characteristics of Salvia divinorum — a potent naturally occurring hallucinogen. The study documents the range of experiential effects including dissociative episodes, explores dose-response relationships, and examines contextual factors surrounding use.",
        "clinical_insight": "Salvia divinorum use is under-researched compared to other hallucinogens, yet clinicians may encounter patients who use it. Understanding its characteristic effects — particularly the dissociative and hallucinogenic properties — helps in differential diagnosis and psychoeducation. The dose-response and contextual data can inform harm reduction counseling and help clinicians distinguish between Salvia-related experiences and other conditions such as psychosis or dissociative disorders.",
        "relevant_for": "Addiction specialists and clinicians working with substance use and hallucinogen experiences",
        "score": 5,
    },
    {
        "compact_id": "xpm7e",
        "title": "Neural discrimination of objects, faces, and print in dyslexic and typical readers: A steady-state visual evoked potential study",
        "date": "2026-06-27",
        "category": "Neurodivergence",
        "summary": "Uses steady-state visual evoked potentials (ssVEP) to investigate neural discrimination of objects, faces, and printed words in dyslexic versus typical readers. The study identifies specific neurodevelopmental processing differences that may underlie reading difficulties, contributing to a neural-level understanding of the dyslexia phenotype.",
        "clinical_insight": "This study provides neurobiological evidence that dyslexia involves atypical neural processing of print that can be distinguished from general visual or face processing deficits. For clinicians conducting dyslexia assessments, these findings support the use of neurophysiological measures as complementary to behavioral testing, and may help differentiate dyslexia from other neurodevelopmental conditions that affect reading.",
        "relevant_for": "Neuropsychologists and clinicians assessing dyslexia and neurodevelopmental disorders",
        "score": 5,
    },
    {
        "compact_id": "e87ft",
        "title": "Exploring diagnosis of Developmental Coordination Disorder and Specific Developmental Disorder of Motor Function: a secondary data analysis using Connected Bradford",
        "date": "2026-06-26",
        "category": "Neurodivergence",
        "summary": "A secondary data analysis using the Connected Bradford dataset to explore diagnostic patterns of Developmental Coordination Disorder (DCD) and Specific Developmental Disorder of Motor Function. The study examines comorbidity rates, demographic factors, and diagnostic pathways in a real-world clinical population.",
        "clinical_insight": "DCD is frequently underdiagnosed or misdiagnosed, particularly when it co-occurs with other neurodevelopmental conditions. This real-world data analysis helps clinicians recognize the typical comorbidity profiles and diagnostic patterns they are likely to encounter in practice, supporting earlier and more accurate identification of motor coordination difficulties in children and young people.",
        "relevant_for": "Clinicians assessing neurodevelopmental conditions in children and adolescents",
        "score": 3,
    },
    {
        "compact_id": "5rea9",
        "title": "Subjective Experience of Stream of Consciousness Impairment in Three Patients with Severe Amnesia",
        "date": "2026-06-24",
        "category": "Psychopathology & Assessment",
        "summary": "A qualitative case study exploring the phenomenology of stream of consciousness impairment in three patients with severe amnesia. Through detailed interviews, the authors characterize how these patients experience disruptions in the continuous flow of conscious experience, contributing to understanding of consciousness disorders in clinical neuropsychology.",
        "clinical_insight": "Severe amnesia affects not just memory but the fundamental experience of conscious continuity. Understanding how patients subjectively experience stream of consciousness impairments helps clinicians provide more empathetic and informed care, and improves differential diagnosis between amnesia and other conditions that disrupt conscious experience such as dissociation, depersonalization, or psychotic disorganization.",
        "relevant_for": "Neuropsychologists and therapists working with memory disorders and brain injury",
        "score": 3,
    },
    {
        "compact_id": "a26je",
        "title": "A resting-state EEG functional connectivity study in informal caregivers of patients with various conditions",
        "date": "2026-06-25",
        "category": "Other Clinical",
        "summary": "Uses resting-state EEG functional connectivity to investigate the neural correlates of caregiving burden in informal caregivers of patients with various conditions. The study examines how the chronic stress of caregiving is reflected in brain network connectivity patterns, providing neurobiological evidence for caregiver burnout.",
        "clinical_insight": "Informal caregivers represent a large but often overlooked clinical population at elevated risk for depression, anxiety, and burnout. This study provides objective neurobiological markers of caregiving stress that complement self-report measures. Clinicians working with caregiver populations can use these findings to validate caregivers' experiences and to advocate for early intervention, as neural changes may precede overt clinical symptoms.",
        "relevant_for": "Clinicians working with caregivers and chronic illness populations",
        "score": 3,
    },
    {
        "compact_id": "2kbtm",
        "title": "Factors Shaping Autistic Adults' Experiences and Perceived Benefits of a Co-Designed VR Sensory Application",
        "date": "2026-06-24",
        "category": "Neurodivergence",
        "summary": "Investigates how autistic adults experience and benefit from a virtual reality sensory application that was co-designed with the autistic community. The study examines which features of the VR environment are most valued, how individual sensory profiles moderate the experience, and the perceived therapeutic potential of the tool for managing sensory overload.",
        "clinical_insight": "VR-based tools co-designed with neurodivergent individuals represent a promising adjunct to traditional therapy approaches for autism. Understanding which sensory features are most beneficial helps clinicians recommend specific digital tools and provides a model for involving service users in intervention design. The co-design methodology itself offers a template for creating other neurodivergent-affirming clinical resources.",
        "relevant_for": "Therapists working with autistic adults and those interested in technology-assisted interventions",
        "score": 3,
    },
    {
        "compact_id": "gxrha",
        "title": "Construct validity evidence for a Workplace Well-Being Questionnaire Battery adapted to Workers with Intellectual Disabilities (WWQBID)",
        "date": "2026-06-24",
        "category": "Psychopathology & Assessment",
        "summary": "Presents construct validity evidence for an adapted workplace well-being questionnaire specifically designed for workers with intellectual disabilities. The study addresses the critical gap in assessment tools for this population, demonstrating that the WWQBID reliably measures well-being dimensions in a group often excluded from standard psychometric research.",
        "clinical_insight": "Workers with intellectual disabilities are frequently assessed using tools not validated for their cognitive profile, leading to inaccurate measurement of well-being and mental health. The WWQBID provides clinicians and occupational psychologists with a validated alternative for assessing well-being in this population, improving the accuracy of needs assessments and intervention evaluation in supported employment settings.",
        "relevant_for": "Clinicians and psychologists assessing well-being in intellectual disability populations",
        "score": 2,
    },
    {
        "compact_id": "965yg",
        "title": "Psychometric Comparability of LLM-Based Digital Twins",
        "date": "2026-06-26",
        "category": "Psychopathology & Assessment",
        "summary": "Examines the psychometric comparability of LLM-based digital twins — AI models trained to simulate individual human response patterns on psychological measures. The study investigates whether these digital replicas can faithfully reproduce the psychometric properties of the individuals they model, with implications for clinical assessment simulation and research methodology.",
        "clinical_insight": "LLM-based digital twins have the potential to transform clinical assessment research by enabling large-scale simulation studies without recruiting participants. However, this study's findings on psychometric comparability are essential reading before clinicians or researchers consider using such tools. Understanding the limitations and validity of digital twins helps prevent over-reliance on AI simulations in clinical decision-making while identifying legitimate research applications.",
        "relevant_for": "Clinical researchers interested in AI applications for psychometric assessment",
        "score": 2,
    },
    {
        "compact_id": "g7ktm",
        "title": "Social Disconnection is Associated with Impaired Social Skills: Evidence from Behavioral Performance and Automated Facial Expression Analysis",
        "date": "2026-06-24",
        "category": "Other Clinical",
        "summary": "Investigates the relationship between subjective social disconnection and objective measures of social skill, using both behavioral tasks and automated facial expression analysis. The study demonstrates that individuals who feel socially disconnected also show measurable impairments in social-cognitive performance and expressive behavior.",
        "clinical_insight": "Social disconnection is a transdiagnostic factor relevant to depression, social anxiety, psychosis, and personality disorders. This study provides objective evidence that subjective disconnection corresponds to measurable social skill deficits, supporting the clinical utility of social disconnection as a screening indicator. Clinicians can use these findings to justify social skills interventions and to track objective improvements alongside subjective reports of connection.",
        "relevant_for": "Clinicians working with social isolation across diagnostic categories",
        "score": 2,
    },
]


def main():
    # Get next number
    with open(PAPERS_JSON) as f:
        papers = json.load(f)
    next_num = max(p["number"] for p in papers) + 1 if papers else 1
    print(f"Current papers: {len(papers)}, next number: {next_num}")

    created = []
    for i, paper in enumerate(RECOVERED):
        num = next_num + i
        cid = paper["compact_id"]
        
        # Get date_created from API
        date_created = paper["date"]
        
        note_content = f"""---
number: {num}
title: {paper["title"]}
authors: Pending
osf_id: {cid}
date_posted: {date_created}
source_date: June 2026
categories: {paper["category"]}
---

## Summary

{paper["summary"]}

## Clinical Insight

{paper["clinical_insight"]}

## Relevant For

{paper["relevant_for"]}

## Notes

Recovered from discarded log during re-scan on 2026-07-03. Originally discarded due to empty OSF API abstracts and/or insufficient title-based keyword scoring. Re-screened with expanded keyword list and PDF/docx full-text extraction (score: {paper["score"]}). Curation note auto-generated and pending full review.
"""
        
        filename = f"{num}-{cid}.md"
        filepath = os.path.join(INBOX, filename)
        with open(filepath, "w") as f:
            f.write(note_content)
        
        created.append((num, cid, paper["title"][:60], paper["category"]))
        print(f"  Created: {filename}")

    print(f"\nCreated {len(created)} curation notes")
    print(f"Paper numbers: {next_num} - {next_num + len(created) - 1}")
    return created


if __name__ == "__main__":
    main()
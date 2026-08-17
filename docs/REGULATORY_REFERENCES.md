# Regulatory References — Computer System Validation & Evidence

> **Portfolio boundary:** Synthetic data only. This is **not** a validated GxP system. References below orient the prototype’s design (traceability, test execution phases, audit-oriented records) to real regulatory language used in industry.

---

## Why CSV / CSA exists

Regulated organizations must have **confidence** that computerized systems used for GxP decisions work as intended and that the **records** those systems produce remain trustworthy over time. That confidence is built through a combination of:

- **Predicate rules** (CGMP, device QMS, clinical, lab, etc.)
- **Electronic records rules** (e.g., 21 CFR Part 11)
- **Guidance** on data integrity and software assurance
- **Industry frameworks** (e.g., ISPE GAMP 5) for scaling effort to risk

This prototype demonstrates **evidence patterns** (requirements → tests → executions → deviations → reviewable trail), not formal validation packages.

---

## 1. FDA — Electronic records & data integrity

### 21 CFR Part 11

- **Official text:** [eCFR Title 21 Part 11](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11/)
- **Purpose:** Criteria for electronic records and electronic signatures to be considered trustworthy and equivalent to paper
- **Closed systems (§ 11.10)** include: system validation; accurate/complete copies; limited access; **secure computer-generated time-stamped audit trails**; authority checks; training; documentation controls
- **Guidance:** [Part 11 Scope and Application](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/part-11-electronic-records-electronic-signatures-scope-and-application)

### Data integrity (drug CGMP)

- FDA guidance: *Data Integrity and Compliance With Drug CGMP — Questions and Answers* (2018)
- Data integrity = completeness, consistency, accuracy
- **ALCOA:** Attributable, Legible, Contemporaneous, Original (or true copy), Accurate
- Applies across the **data lifecycle** (create → process → archive → dispose)

### Computer Software Assurance (devices / QMS software)

- FDA guidance: *Computer Software Assurance for Production and Quality Management System Software*
- Risk-based assurance for software used in **production or quality management systems**
- Official listing: [FDA CSA guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/computer-software-assurance-production-and-quality-management-system-software)
- Complements *General Principles of Software Validation*

### Predicate examples

| CFR | Relevance to systems & records |
|-----|--------------------------------|
| **Part 211** | CGMP drugs — production/lab records, equipment, data backup (§ 211.68), retention |
| **Part 820 / QMSR** | Device quality system — software in production/QMS, design controls, document control |
| **Part 58** | GLP — nonclinical study records |
| **Clinical regs** | Electronic records supporting IND/IDE/NDA/BLA decisions |

---

## 2. IQ / OQ / PQ in context

Industry validation of computerized systems often structures testing as:

| Phase | Typical intent |
|-------|----------------|
| **IQ — Installation Qualification** | System installed as specified (environment, configuration, dependencies) |
| **OQ — Operational Qualification** | Functions operate as specified across operating ranges |
| **PQ — Performance Qualification** | Performs as intended in the business process / with representative data |

These terms are **industry practice** (strongly associated with GAMP-style programs and CSV). Formal acceptance still depends on approved protocols, deviations handling, and quality unit oversight — none of which this portfolio demo replaces.

**In this repo:** phases, test cases, and executions model the *shape* of evidence collection and status tracking.

---

## 3. Traceability (RTM)

A **Requirements Traceability Matrix** links:

User / functional requirements → design or configuration → test cases → test results → residual risk / deviations

Inspectors and auditors often ask: *“Show me how this requirement was tested and what happened when it failed.”*  
That is the problem space this tracker illustrates.

---

## 4. International alignment

| Body / document | Focus |
|-----------------|--------|
| **MHRA GxP Data Integrity Guidance (2018)** | ALCOA + Complete, Consistent, Enduring, Available |
| **PIC/S PI 041-1** | Data management & integrity in GMP/GDP environments |
| **EU GMP Annex 11** | Computerised systems |
| **EU GMP Chapter 4** | Documentation |
| **WHO** data integrity technical reports | Global medicines regulation |
| **ISPE GAMP 5** | Industry risk-based framework for GxP systems (not law) |

---

## 5. Regulated industries that care about these systems

- Pharmaceutical & biologics manufacturing  
- Medical devices (production + QMS software)  
- Clinical research organizations and sponsors  
- QC / analytical laboratories  
- GDP / wholesale distribution  
- Pharmacovigilance  
- Blood, tissue, cell & gene therapy operations  
- Any process where **electronic records** drive release, safety, or submission decisions  

---

## 6. Mapping prototype features → regulatory themes (educational)

| Theme | Regulatory signal | Prototype illustration |
|-------|-------------------|------------------------|
| Traceability | Defensible testing of requirements | RTM views |
| Structured test evidence | IQ/OQ/PQ-style execution records | Phases, test cases, executions |
| Deviation linkage | Failures must be visible and dispositioned | Deviations module |
| Audit-oriented history | Part 11 / Annex 11 audit trail concepts | Audit log & middleware patterns |
| Data boundary | Integrity starts with knowing what data is in scope | Portfolio safety docs + synthetic seed data |

**Non-claims:** no approved validation plan, no electronic signatures, no Part 11 certification, no production deployment.

---

## 7. Primary sources to bookmark

1. [21 CFR Part 11 (eCFR)](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11/)  
2. FDA Part 11 Scope and Application guidance  
3. FDA Data Integrity and Compliance With Drug CGMP (Q&A)  
4. FDA Computer Software Assurance guidance  
5. FDA General Principles of Software Validation  
6. MHRA GxP Data Integrity Guidance  
7. PIC/S PI 041-1  
8. EU GMP Annex 11 & Chapter 4  
9. ISPE GAMP 5 (industry)

Prefer regulator-hosted PDFs and eCFR text when writing SOPs or validation strategies.

---

*Last updated: 2026-08-17*

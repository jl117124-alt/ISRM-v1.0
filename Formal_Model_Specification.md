\# ISRM v1.0 – Formal Model Specification

\#\# Purpose

ISRM v1.0 is a structural regime classification model designed to quantify interaction between systemic scale intensity and internal restraint capacity.

It is diagnostic, not predictive.

\---

\#\# Definitions

SP (Structural Pressure):

SP \= (D × (1 \+ P)) / C

D \= S × TL × N    
C \= IRD × M  

\---

\#\# Components

\#\#\# S – Scale Composite  
Normalized average of:  
\- log(population)  
\- population density  
\- percent urban  
\- percent metro \>1M

\#\#\# IRD – Internal Restraint Density  
Normalized average of:  
\- volunteerism rate  
\- two-parent household rate  
\- voter turnout rate

\#\#\# M – Marriage Multiplier  
Marriage rate (and/or inverse divorce rate)

\#\#\# P – Fragmentation Amplifier  
Optional scaling term

\---

\#\# Normalization

Min-max normalization applied per defined domain.

Anchored normalization used for cross-temporal comparison.

\---

\#\# Enforcement Outcome (Validation Only)

Normalized composite:  
\- Police officers per 100k  
\- Incarceration rate per 100k

Enforcement is not part of SP.  
It is used only for validation tests.

\---

\#\# Domain

Validated in federated subnational systems with:  
\- Reliable demographic data  
\- Family structure proxies  
\- Civic participation proxies  
\- Enforcement statistics

Not validated for municipal or micro-regions lacking these.

\---

\#\# Falsifier Thresholds

See Falsifier\_Checklist.md
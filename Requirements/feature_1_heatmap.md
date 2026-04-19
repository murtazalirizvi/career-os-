# Feature 1: The "Hiring Manager's Lens" (Visual Heatmap)

## Epic 1.1: Visual Hierarchy & Eye-Tracking Simulation
- **Story 1: F-Pattern Identification.** Detect if content follows top-left heavy sweeps.
- **Story 2: Visual Weight Analysis.** Calculate if bolding/font-size creates the right focus.
- **Story 3: 6-Second Blur Test.** Simulates peripheral vision via Gaussian blur.
- **Story 4: Coordinate-Based Hot Zones.** Map X-Y coordinates to historical attention data.
- **Story 5: White Space Ratio.** Ensure 30-40% "breathing room" to reduce cognitive load.

## Epic 1.2: ATS Parsing & Structural Integrity
- **Story 1: Bot-View Reconstruction.** Shows user the raw text the machine sees.
- **Story 2: Unparseable Font Detection.** Flags Type 3 or non-standard Unicode fonts.
- **Story 3: Contact Field Mapping.** Verifies if Email/Phone are in standard locations.
- **Story 4: Header Hierarchy.** Validates logical nesting of sections (H1, H2).
- **Story 5: Hidden Text Scanner.** Detects "white-on-white" keywords to prevent blacklisting.

## Epic 1.3: Semantic Matching & Keyword Density
- **Story 1: Keyword Cloud Differential.** Compare JD frequency vs Resume frequency.
- **Story 2: Synonym Optimization.** Suggesting 'SPA' for 'Single Page Application'.
- **Story 3: Skill Frequency Map.** Prevents both under-selling and keyword stuffing.
- **Story 4: Buzzword Detection.** Replaces 'Hardworking' with action verbs like 'Engineered'.
- **Story 5: Missing Skill Prioritization.** Weighting missing skills based on JD importance.

## Epic 1.4: Competitive Benchmarking
- **Story 1: Industry Template Comparison.** Siamese Network check against Gold Standard resumes.
- **Story 2: Market Percentile Ranking.** Ranks user against other platform applicants.
- **Story 3: Baseline Metric Validation.** Length and bullet point quantity checks.
- **Story 4: USP Discovery.** Identifying rare skills (e.g., WebRTC) in user profile.
- **Story 5: Seniority Alignment.** Ensuring 'Years of Exp' matches JD requirements.

## Epic 1.5: Heatmap Export & Iteration Tracking
- **Story 1: Diagnostic Report.** PDF export of the audit.
- **Story 2: Version Control.** Save versions to see heatmap improvement over time.
- **Story 3: Before & After View.** Side-by-side visual validation.
- **Story 4: Job Category Tagging.** Organize resumes by target (Frontend vs Backend).
- **Story 5: Final Certification.** Unlocks 'Ready to Apply' badge at 90%+ score.

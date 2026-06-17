# ClipAgent MVP - Video Processing Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CLIPPING TOOL MVP PROCESSING PIPELINE                     │
└─────────────────────────────────────────────────────────────────────────────────┘

INPUT STAGE
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Video     │    │   SRT       │    │   Text      │
│   File      │    │  Subtitles  │    │   File      │
│  (.mp4)     │    │   (.srt)    │    │  (.txt)     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    Project Creation
                           │
                    ┌─────────────┐
                    │  Project    │
                    │  Manager    │
                    │ (UUID ID)   │
                    └─────────────┘
                           │
                    ┌─────────────┐
                    │  Text       │
                    │ Chunking    │
                    │ (5000 chars)│
                    └─────────────┘

STEP 1: OUTLINE EXTRACTION
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Input: Text Chunks → LLM Analysis → Topic Extraction                           │
│                                                                                 │
│  Process:                                                                       │
│  • Analyze transcript segments                                                  │
│  • Extract 2-5 core topics per chunk                                           │
│  • Ensure 95%+ content coverage                                                │
│  • Target 3-12 minute segments                                                  │
│                                                                                 │
│  Output: Structured topic outlines with summaries                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
STEP 2: TIMELINE EXTRACTION
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Input: Topic Outlines + SRT Subtitles → Time Mapping                          │
│                                                                                 │
│  Process:                                                                       │
│  • Match topics to SRT segments                                                │
│  • Ensure minimum 90-second duration                                           │
│  • Target 3-6 minute optimal length                                            │
│  • Merge adjacent short topics                                                 │
│                                                                                 │
│  Output: Precise start/end timestamps for each topic                           │
└─────────────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
STEP 3: CONTENT SCORING
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Input: Timeline Data → Multi-dimensional Scoring                              │
│                                                                                 │
│  Scoring Criteria:                                                              │
│  • Information Value (0.0-1.0)                                                 │
│  • Emotional Resonance (0.0-1.0)                                              │
│  • Viral Potential (0.0-1.0)                                                   │
│  • Structural Integrity (0.0-1.0)                                             │
│                                                                                 │
│  Process:                                                                       │
│  • LLM evaluates each clip                                                     │
│  • Apply minimum threshold (default: 0.7)                                      │
│  • Generate recommendation reasons                                             │
│                                                                                 │
│  Output: Scored clips with viral potential assessment                          │
└─────────────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
STEP 4: TITLE GENERATION
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Input: High-scoring Clips → Viral Title Creation                              │
│                                                                                 │
│  Principles:                                                                    │
│  • Stay true to original content                                                │
│  • Avoid clickbait language                                                     │
│  • Highlight core value propositions                                           │
│  • Keep titles concise and impactful                                           │
│                                                                                 │
│  Process:                                                                       │
│  • LLM generates compelling titles                                              │
│  • Optimize for click-through rates                                            │
│  • Ensure brand safety                                                         │
│                                                                                 │
│  Output: Viral-optimized titles for each clip                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
STEP 5: THEMATIC CLUSTERING
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Input: Titled Clips → Theme-based Grouping                                     │
│                                                                                 │
│  Categories:                                                                    │
│  • Investment & Finance                                                         │
│  • Career & Growth                                                             │
│  • Social Observations                                                          │
│  • Cultural Differences                                                         │
│  • Live Streaming & Interaction                                                │
│  • Relationships & Psychology                                                  │
│  • Health & Lifestyle                                                          │
│  • Content Creation & Platforms                                                │
│                                                                                 │
│  Rules: 2-5 clips per collection, max 5 collections                            │
│                                                                                 │
│  Output: Themed collections with summaries                                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
STEP 6: VIDEO GENERATION
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Input: Collection Data → FFmpeg Video Processing                              │
│                                                                                 │
│  Process:                                                                       │
│  • Extract individual clips using FFmpeg                                       │
│  • Generate collection compilation videos                                      │
│  • Handle file naming and organization                                         │
│  • Apply video optimization                                                    │
│                                                                                 │
│  Output: Final video files ready for distribution                             │
└─────────────────────────────────────────────────────────────────────────────────┘

OUTPUT STAGE
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Individual  │    │ Collection  │    │ Metadata    │
│   Clips     │    │   Videos    │    │   Files     │
│  (.mp4)     │    │   (.mp4)    │    │  (.json)    │
└─────────────┘    └─────────────┘    └─────────────┘

TECHNICAL STACK
┌─────────────────────────────────────────────────────────────────────────────────┐
│  LLM Providers: DashScope (Alibaba) + SiliconFlow                              │
│  Models: Qwen/Qwen3-8B, qwen-plus                                             │
│  Video Processing: FFmpeg                                                      │
│  API Framework: FastAPI                                                       │
│  Configuration: JSON-based settings                                           │
│  Caching: LLM response caching for efficiency                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

QUALITY FILTERING LOGIC
┌─────────────────────────────────────────────────────────────────────────────────┐
│  "Worth Watching" Criteria:                                                    │
│                                                                                 │
│  1. Information Density: High-value insights per minute                      │
│  2. Emotional Impact: Strong emotional resonance                               │
│  3. Discussion Potential: Content that sparks engagement                      │
│  4. Structural Quality: Complete, well-formed arguments                       │
│                                                                                 │
│  Threshold: Minimum score 0.7 (70%) - configurable per project               │
│  Priority: Quality over quantity                                              │
└─────────────────────────────────────────────────────────────────────────────────┘

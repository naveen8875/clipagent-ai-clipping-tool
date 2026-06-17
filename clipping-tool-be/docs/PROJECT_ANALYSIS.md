# ClipAgent MVP - Backend Analysis & Architecture

## Project Overview

**ClipAgent MVP** is an intelligent video clipping system that automatically identifies and extracts the most engaging segments from long-form videos. The system uses AI/LLM technology to analyze video transcripts and create short, viral-worthy clips with compelling titles and thematic collections.

## Core Architecture

### 1. **Main Entry Points**
- `app/main.py` - FastAPI application entrypoint
- `app/api/` - REST API route modules
- `app/pipeline/` - Core 6-step clipping pipeline
- `app/config.py` - Runtime configuration and prompt resolution

### 2. **Processing Pipeline (6-Step Workflow)**

The system follows a sophisticated 6-step pipeline to transform raw video content into curated clips:

#### **Step 1: Outline Extraction** (`step1_outline.py`)
- **Purpose**: Extract structured topics from video transcripts
- **Input**: Raw transcript text chunks (5000 characters each)
- **Process**: 
  - Uses LLM to analyze transcript segments
  - Extracts 2-5 core topics per 30-minute chunk
  - Ensures 95%+ content coverage
  - Targets 3-12 minute segments per topic
- **Output**: Structured topic outlines with content summaries

#### **Step 2: Timeline Extraction** (`step2_timeline.py`)
- **Purpose**: Map topics to precise video timestamps using SRT subtitles
- **Input**: Topic outlines + SRT subtitle files
- **Process**:
  - Matches topics to specific SRT subtitle segments
  - Ensures minimum 90-second duration per clip
  - Targets 3-6 minute optimal viewing length
  - Merges adjacent short topics when necessary
- **Output**: Precise start/end timestamps for each topic

#### **Step 3: Content Scoring** (`step3_scoring.py`)
- **Purpose**: Evaluate clips for viral potential using multi-dimensional scoring
- **Scoring Criteria**:
  - **Information Value**: Unique insights, knowledge density
  - **Emotional Resonance**: Ability to evoke strong emotions
  - **Viral Potential**: Shareable quotes, discussion triggers
  - **Structural Integrity**: Logical flow and completeness
- **Process**: LLM evaluates each clip on 0.0-1.0 scale
- **Output**: Scored clips with recommendation reasons

#### **Step 4: Title Generation** (`step4_title.py`)
- **Purpose**: Create compelling, click-worthy titles for high-scoring clips
- **Principles**:
  - Stay true to original content (no exaggeration)
  - Avoid clickbait language
  - Highlight core value propositions
  - Keep titles concise and impactful
- **Output**: Viral-optimized titles for each clip

#### **Step 5: Thematic Clustering** (`step5_clustering.py`)
- **Purpose**: Group related clips into thematic collections
- **Clustering Categories**:
  - Investment & Finance
  - Career & Growth
  - Social Observations
  - Cultural Differences
  - Live Streaming & Interaction
  - Relationships & Psychology
  - Health & Lifestyle
  - Content Creation & Platforms
- **Rules**: 2-5 clips per collection, maximum 5 collections
- **Output**: Themed collections with summaries

#### **Step 6: Video Generation** (`step6_video.py`)
- **Purpose**: Extract actual video clips and create collection videos
- **Process**:
  - Uses FFmpeg for precise video cutting
  - Generates individual clips with titles
  - Creates collection compilation videos
  - Handles file naming and organization
- **Output**: Final video files ready for distribution

## Key Technologies & Components

### **LLM Integration**
- **Providers**: DashScope (Alibaba) and SiliconFlow APIs
- **Models**: Qwen/Qwen3-8B, qwen-plus
- **Factory Pattern**: `LLMFactory` manages different providers
- **Caching**: Raw LLM responses cached to avoid re-processing

### **Video Processing**
- **Tool**: FFmpeg for video manipulation
- **Features**:
  - Precise timestamp-based cutting
  - SRT to FFmpeg time format conversion
  - Batch processing capabilities
  - File sanitization and organization

### **Project Management**
- **Multi-project Support**: Each project gets isolated directories
- **Metadata Tracking**: Project status, progress, file info
- **UUID-based IDs**: Unique project identification
- **State Management**: Tracks processing steps and errors

### **Configuration System**
- **Video Categories**: 8 different content types with specialized prompts
- **API Management**: Secure key storage and provider switching
- **Thresholds**: Configurable scoring thresholds (default: 0.7)
- **Chunk Sizes**: Configurable text processing chunks (default: 5000 chars)

## Prompt Engineering Strategy

The system uses sophisticated prompt engineering with category-specific templates:

### **Outline Extraction Prompts**
- Focus on complete coverage (95%+ content)
- Prioritize information density
- Ensure natural topic boundaries
- Balance duration vs. completeness

### **Timeline Extraction Prompts**
- Emphasize precision and completeness
- Enforce minimum duration requirements
- Prioritize natural speech boundaries
- Handle edge cases and transitions

### **Scoring Prompts**
- Multi-dimensional evaluation framework
- Clear scoring criteria (0.0-1.0 scale)
- Emphasis on viral potential factors
- Structured output format

### **Title Generation Prompts**
- Anti-clickbait principles
- Content authenticity requirements
- Viral optimization techniques
- Brand-safe language guidelines

### **Clustering Prompts**
- Thematic keyword matching
- Quality-based prioritization
- Collection size constraints
- Cross-topic relationship analysis

## Data Flow Architecture

```
Input Video + SRT → Text Chunking → LLM Analysis → Topic Extraction
                                                      ↓
Timeline Mapping ← SRT Matching ← Topic Outlines ← Content Analysis
       ↓
Score Evaluation → Quality Filtering → Title Generation
       ↓
Thematic Clustering → Collection Formation → Video Generation
       ↓
Final Clips + Collections → Distribution Ready Content
```

## Key Innovation Points

### **1. Content Coverage Strategy**
- Ensures no valuable content is lost
- Balances completeness with quality
- Handles edge cases and transitions

### **2. Duration Optimization**
- Enforces minimum viable clip length (90 seconds)
- Targets optimal viewing duration (3-6 minutes)
- Prevents overly short or long segments

### **3. Quality Scoring System**
- Multi-dimensional evaluation beyond simple metrics
- Considers viral potential and engagement factors
- Balances information value with entertainment value

### **4. Thematic Organization**
- Intelligent clustering based on content analysis
- Category-specific optimization
- Collection-based content delivery

### **5. Scalable Architecture**
- Multi-project isolation
- Caching and optimization
- Provider-agnostic LLM integration

## Technical Implementation Details

### **File Structure**
```
app/
├── pipeline/         # 6-step processing pipeline
├── utils/            # Core utilities (LLM, video, text processing)
├── api/              # FastAPI route handlers
├── config.py         # Configuration management
└── main.py           # FastAPI application entrypoint

prompts/en/           # English prompt templates, including category overrides
data/                 # Project metadata and settings
```

### **Error Handling**
- Comprehensive error management system
- Graceful degradation and recovery
- Detailed logging and debugging
- User-friendly error messages

### **Performance Optimizations**
- Batch processing for efficiency
- LLM response caching
- Parallel processing where possible
- Memory-efficient text chunking

## Business Logic for "Worth Watching" Clips

The system identifies clips worth watching through a sophisticated scoring algorithm:

### **Primary Factors**
1. **Information Density**: High-value insights per minute
2. **Emotional Impact**: Strong emotional resonance
3. **Discussion Potential**: Content that sparks engagement
4. **Structural Quality**: Complete, well-formed arguments

### **Secondary Factors**
1. **Timing Relevance**: Current trends and topics
2. **Audience Alignment**: Target demographic preferences
3. **Platform Optimization**: Format-specific considerations
4. **Brand Safety**: Appropriate content standards

### **Threshold Management**
- Default minimum score: 0.7 (70%)
- Configurable per project/category
- Dynamic adjustment based on content volume
- Quality-over-quantity prioritization

## Conclusion

ClipAgent MVP represents a sophisticated approach to automated video content curation, combining advanced AI/LLM capabilities with practical video processing techniques. The system's strength lies in its multi-step pipeline that ensures both content completeness and quality optimization, making it an effective tool for transforming long-form content into engaging short-form clips.

The architecture is designed for scalability, maintainability, and extensibility, with clear separation of concerns and robust error handling. The prompt engineering strategy ensures consistent, high-quality output while the scoring system provides intelligent filtering for viral potential.

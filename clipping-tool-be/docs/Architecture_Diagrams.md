# ClipAgent MVP - Architecture Diagrams

This document provides comprehensive visual diagrams of the ClipAgent MVP system architecture, data flow, and component interactions.

---

## Table of Contents

- [System Architecture Overview](#system-architecture-overview)
- [Component Architecture](#component-architecture)
- [Data Flow Architecture](#data-flow-architecture)
- [Processing Pipeline Architecture](#processing-pipeline-architecture)
- [LLM Integration Architecture](#llm-integration-architecture)
- [Storage Architecture](#storage-architecture)
- [Deployment Architecture](#deployment-architecture)

---

## System Architecture Overview

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[CLI Tool]
    end
    
    subgraph "Presentation Layer"
        C[React Frontend<br/>TypeScript + Ant Design]
    end
    
    subgraph "API Layer"
        D[FastAPI Backend<br/>RESTful API]
        E[WebSocket<br/>Real-time Updates]
    end
    
    subgraph "Business Logic Layer"
        F[Project Manager]
        G[ClipAgentsProcessor<br/>Pipeline Orchestrator]
        H[Upload Manager]
        I[Bilibili Downloader]
    end
    
    subgraph "Processing Layer"
        J1[Step 1: Outline]
        J2[Step 2: Timeline]
        J3[Step 3: Scoring]
        J4[Step 4: Titles]
        J5[Step 5: Clustering]
        J6[Step 6: Video Gen]
    end
    
    subgraph "Integration Layer"
        K[LLM Factory]
        L[Video Processor<br/>FFmpeg Wrapper]
        M[Text Processor<br/>SRT Parser]
    end
    
    subgraph "External Services"
        N1[DashScope API<br/>Alibaba Cloud]
        N2[SiliconFlow API]
        N3[Bilibili Platform]
    end
    
    subgraph "Data Layer"
        O1[File Storage<br/>Videos + Metadata]
        O2[JSON Database<br/>Projects + Settings]
        O3[Cache Storage<br/>LLM Responses]
    end
    
    A --> C
    B --> D
    C --> D
    C --> E
    D --> F
    D --> G
    D --> H
    D --> I
    
    F --> O2
    G --> J1
    J1 --> J2
    J2 --> J3
    J3 --> J4
    J4 --> J5
    J5 --> J6
    
    J1 --> K
    J2 --> K
    J3 --> K
    J4 --> K
    J5 --> K
    J6 --> L
    
    K --> N1
    K --> N2
    I --> N3
    
    J1 --> M
    J2 --> M
    
    G --> O1
    G --> O3
    H --> O1
    I --> O1
    
    style C fill:#61dafb
    style D fill:#009688
    style G fill:#ff9800
    style K fill:#ffc107
    style L fill:#9c27b0
```

---

## Component Architecture

### Backend Component Diagram

```mermaid
graph LR
    subgraph "app/main.py"
        A[FastAPI App]
        B[API Layer]
        C[Route Handlers]
        D[Application Startup]
    end
    
    subgraph "app/api/"
        E[Upload and Processing Routes]
        F[Request Validation]
    end
    
    subgraph "app/pipeline/"
        G1[OutlineExtractor]
        G2[TimelineExtractor]
        G3[ContentScorer]
        G4[TitleGenerator]
        G5[ClusteringEngine]
        G6[VideoGenerator]
    end
    
    subgraph "app/utils/"
        H1[LLMFactory]
        H2[DashScope Client]
        H3[SiliconFlowClient]
        H4[VideoProcessor]
        H5[TextProcessor]
        H6[APIKeyManager]
        H7[ErrorHandler]
    end
    
    subgraph "app/config.py"
        I[ConfigManager]
        J[Settings Model]
    end
    
    A --> B
    A --> C
    A --> D
    C --> E
    E --> F
    F --> G1
    F --> G2
    F --> G3
    F --> G4
    F --> G5
    F --> G6
    
    G1 --> H1
    G2 --> H1
    G3 --> H1
    G4 --> H1
    G5 --> H1
    G6 --> H4
    
    H1 --> H2
    H1 --> H3
    
    G1 --> H5
    G2 --> H5
    
    B --> H6
    
    E --> I
    H1 --> I
    I --> J
    
    style A fill:#4caf50
    style E fill:#ff9800
    style H1 fill:#2196f3
    style I fill:#9c27b0
```

### Frontend Component Diagram

```mermaid
graph TB
    subgraph "Pages"
        A[HomePage]
        B[ProjectDetailPage]
        C[SettingsPage]
    end
    
    subgraph "Components"
        D[ProjectCard]
        E[ClipCard]
        F[CollectionCard]
        G[UploadModal]
        H[BilibiliDownloadModal]
        I[ProcessingStatus]
    end
    
    subgraph "Services"
        J[API Service]
        K[WebSocket Service]
    end
    
    subgraph "Store/State"
        L[Projects State]
        M[Settings State]
        N[Processing State]
    end
    
    A --> D
    A --> G
    A --> H
    B --> E
    B --> F
    B --> I
    
    D --> J
    E --> J
    F --> J
    G --> J
    H --> J
    I --> K
    
    J --> L
    J --> M
    K --> N
    
    style A fill:#61dafb
    style J fill:#ff9800
    style L fill:#4caf50
```

---

## Data Flow Architecture

### Complete Data Flow Diagram

```mermaid
flowchart TD
    Start([User Uploads Video + SRT]) --> A[FastAPI Receives Upload]
    A --> B{Validate Files}
    B -->|Invalid| Error1[Return Error]
    B -->|Valid| C[Create Project ID]
    
    C --> D[Save to uploads/project_id/input/]
    D --> E[Initialize Project Metadata]
    E --> F[Start Processing Pipeline]
    
    F --> G[Parse SRT File]
    G --> H[Chunk Text 30min/5000chars]
    H --> I1[Step 1: Outline Extraction]
    
    I1 --> I1A[Load Outline Prompt]
    I1A --> I1B[For Each Chunk]
    I1B --> I1C{LLM Call}
    I1C -->|Success| I1D[Parse Topics]
    I1C -->|Failure| I1E[Retry 3x]
    I1E -->|Still Fails| Error2[Log Error]
    I1D --> I1F[Merge & Dedupe]
    I1F --> I1G[Save step1_outline.json]
    
    I1G --> I2[Step 2: Timeline Mapping]
    I2 --> I2A[Load Timeline Prompt]
    I2A --> I2B[Match Topics to SRT]
    I2B --> I2C{LLM Call}
    I2C --> I2D[Validate Timestamps]
    I2D --> I2E[Convert SRT → FFmpeg Time]
    I2E --> I2F[Save step2_timeline.json]
    
    I2F --> I3[Step 3: Content Scoring]
    I3 --> I3A[Load Scoring Prompt]
    I3A --> I3B[For Each Clip]
    I3B --> I3C{LLM Score 4 Dimensions}
    I3C --> I3D[Calculate Final Score]
    I3D --> I3E{Score >= 0.7?}
    I3E -->|No| I3F[Filter Out]
    I3E -->|Yes| I3G[Keep Clip]
    I3G --> I3H[Save step3_scoring.json]
    
    I3H --> I4[Step 4: Title Generation]
    I4 --> I4A[Load Title Prompt]
    I4A --> I4B[For Each High-Score Clip]
    I4B --> I4C{LLM Generate Title}
    I4C --> I4D[Validate Title Quality]
    I4D --> I4E[Save step4_titles.json]
    
    I4E --> I5[Step 5: Thematic Clustering]
    I5 --> I5A[Load Clustering Prompt]
    I5A --> I5B[Send All Clips to LLM]
    I5B --> I5C{LLM Group by Theme}
    I5C --> I5D[Create Collections 2-5 clips]
    I5D --> I5E[Generate Collection Metadata]
    I5E --> I5F[Save step5_clustering.json]
    
    I5F --> I6[Step 6: Video Generation]
    I6 --> I6A[For Each Clip]
    I6A --> I6B{FFmpeg Extract}
    I6B -->|Success| I6C[Save to clips/]
    I6B -->|Failure| I6D[Retry with Fallback]
    I6C --> I6E[For Each Collection]
    I6E --> I6F{FFmpeg Concatenate}
    I6F --> I6G[Save to collections/]
    I6G --> I6H[Save Final Metadata]
    
    I6H --> End([Processing Complete])
    
    style Start fill:#4caf50
    style End fill:#4caf50
    style I1 fill:#e3f2fd
    style I2 fill:#e3f2fd
    style I3 fill:#e3f2fd
    style I4 fill:#e3f2fd
    style I5 fill:#e3f2fd
    style I6 fill:#e3f2fd
    style Error1 fill:#ffcdd2
    style Error2 fill:#ffcdd2
```

### Request-Response Flow

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Frontend
    participant FastAPI
    participant ProjectMgr
    participant Pipeline
    participant LLM
    participant FFmpeg
    participant Storage
    
    User->>Frontend: Upload video + SRT
    Frontend->>FastAPI: POST /api/projects/upload
    FastAPI->>ProjectMgr: create_project()
    ProjectMgr->>Storage: Save files
    ProjectMgr-->>FastAPI: project_id
    FastAPI-->>Frontend: {project_id, status}
    
    Frontend->>FastAPI: POST /api/projects/{id}/process
    FastAPI->>Pipeline: run_full_pipeline()
    
    loop For each step (1-6)
        Pipeline->>Storage: Load input data
        Pipeline->>LLM: Send prompt + data
        LLM-->>Pipeline: AI response
        Pipeline->>Storage: Save step results
        Pipeline->>FastAPI: Update progress
        FastAPI->>Frontend: WebSocket update
        Frontend->>User: Show progress
    end
    
    Pipeline->>FFmpeg: Extract clips
    FFmpeg->>Storage: Save videos
    Pipeline->>Storage: Save metadata
    Pipeline-->>FastAPI: Complete
    FastAPI-->>Frontend: {status: "completed"}
    Frontend-->>User: Show results
```

---

## Processing Pipeline Architecture

### 6-Step Pipeline Flow

```mermaid
graph TD
    subgraph "Input"
        A[Video File]
        B[SRT Subtitles]
    end
    
    subgraph "Step 1: Outline Extraction"
        C1[Parse SRT]
        C2[Chunk Text 30min]
        C3[LLM: Extract Topics]
        C4[Merge & Dedupe]
        C5[Output: Outlines JSON]
    end
    
    subgraph "Step 2: Timeline Mapping"
        D1[Load Outlines]
        D2[Load SRT Chunks]
        D3[LLM: Match to Timestamps]
        D4[Validate Time Format]
        D5[Output: Timeline JSON]
    end
    
    subgraph "Step 3: Content Scoring"
        E1[Load Timeline]
        E2[LLM: Score 4 Dimensions]
        E3[Calculate Final Score]
        E4[Filter by Threshold]
        E5[Output: Scored Clips JSON]
    end
    
    subgraph "Step 4: Title Generation"
        F1[Load Scored Clips]
        F2[LLM: Generate Titles]
        F3[Validate Quality]
        F4[Output: Titled Clips JSON]
    end
    
    subgraph "Step 5: Thematic Clustering"
        G1[Load Titled Clips]
        G2[LLM: Group by Theme]
        G3[Create Collections]
        G4[Output: Collections JSON]
    end
    
    subgraph "Step 6: Video Generation"
        H1[Load Clips + Collections]
        H2[FFmpeg: Extract Clips]
        H3[FFmpeg: Concat Collections]
        H4[Output: Video Files]
    end
    
    A --> C1
    B --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5
    
    C5 --> D1
    B --> D2
    D1 --> D3
    D2 --> D3
    D3 --> D4
    D4 --> D5
    
    D5 --> E1
    E1 --> E2
    E2 --> E3
    E3 --> E4
    E4 --> E5
    
    E5 --> F1
    F1 --> F2
    F2 --> F3
    F3 --> F4
    
    F4 --> G1
    G1 --> G2
    G2 --> G3
    G3 --> G4
    
    G4 --> H1
    A --> H2
    H1 --> H2
    H2 --> H3
    H3 --> H4
    
    style C5 fill:#e8f5e9
    style D5 fill:#e8f5e9
    style E5 fill:#e8f5e9
    style F4 fill:#e8f5e9
    style G4 fill:#e8f5e9
    style H4 fill:#e8f5e9
```

### Pipeline State Machine

```mermaid
stateDiagram-v2
    [*] --> Initialized: Create Project
    Initialized --> Step1_Running: Start Processing
    
    Step1_Running --> Step1_Complete: Outlines Extracted
    Step1_Running --> Step1_Failed: LLM Error
    Step1_Failed --> Step1_Running: Retry
    Step1_Failed --> Failed: Max Retries
    
    Step1_Complete --> Step2_Running: Start Timeline
    Step2_Running --> Step2_Complete: Timestamps Mapped
    Step2_Running --> Step2_Failed: LLM Error
    Step2_Failed --> Step2_Running: Retry
    Step2_Failed --> Failed: Max Retries
    
    Step2_Complete --> Step3_Running: Start Scoring
    Step3_Running --> Step3_Complete: Clips Scored
    Step3_Running --> Step3_Failed: LLM Error
    Step3_Failed --> Step3_Running: Retry
    Step3_Failed --> Failed: Max Retries
    
    Step3_Complete --> Step4_Running: Start Titles
    Step4_Running --> Step4_Complete: Titles Generated
    Step4_Running --> Step4_Failed: LLM Error
    Step4_Failed --> Step4_Running: Retry
    Step4_Failed --> Failed: Max Retries
    
    Step4_Complete --> Step5_Running: Start Clustering
    Step5_Running --> Step5_Complete: Collections Created
    Step5_Running --> Step5_Failed: LLM Error
    Step5_Failed --> Step5_Running: Retry
    Step5_Failed --> Failed: Max Retries
    
    Step5_Complete --> Step6_Running: Start Video Gen
    Step6_Running --> Step6_Complete: Videos Created
    Step6_Running --> Step6_Failed: FFmpeg Error
    Step6_Failed --> Step6_Running: Retry
    Step6_Failed --> Failed: Max Retries
    
    Step6_Complete --> Completed: All Done
    Completed --> [*]
    Failed --> [*]
```

---

## LLM Integration Architecture

### LLM Factory Pattern

```mermaid
classDiagram
    class LLMFactory {
        +create_client(provider, api_key, model)
        +get_default_client()
        +test_connection(provider, api_key, model)
    }
    
    class LLMClient {
        -api_key: str
        -model: str
        +call(prompt, input_data)
        +call_with_retry(prompt, input_data, max_retries)
    }
    
    class SiliconFlowClient {
        -api_key: str
        -model: str
        +call(prompt, input_data)
        +call_with_retry(prompt, input_data, max_retries)
    }
    
    class ConfigManager {
        -settings: Settings
        +get_api_config()
        +update_api_key()
    }
    
    class OutlineExtractor {
        -llm_client
        +extract_outline(srt_path)
    }
    
    class TimelineExtractor {
        -llm_client
        +extract_timeline(outlines)
    }
    
    class ContentScorer {
        -llm_client
        +score_clips(timeline)
    }
    
    LLMFactory --> LLMClient: creates
    LLMFactory --> SiliconFlowClient: creates
    LLMFactory --> ConfigManager: uses
    
    OutlineExtractor --> LLMFactory: uses
    TimelineExtractor --> LLMFactory: uses
    ContentScorer --> LLMFactory: uses
    
    LLMClient ..|> ILLMClient: implements
    SiliconFlowClient ..|> ILLMClient: implements
    
    class ILLMClient {
        <<interface>>
        +call(prompt, input_data)
        +call_with_retry(prompt, input_data, max_retries)
    }
```

### LLM Request Flow

```mermaid
sequenceDiagram
    participant Pipeline
    participant LLMFactory
    participant ConfigMgr
    participant LLMClient
    participant ProviderAPI
    participant Cache
    
    Pipeline->>LLMFactory: get_default_client()
    LLMFactory->>ConfigMgr: get_api_config()
    ConfigMgr-->>LLMFactory: {provider, api_key, model}
    
    alt provider == "openrouter"
        LLMFactory->>LLMClient: new OpenRouterClient(api_key, model)
        LLMFactory-->>Pipeline: LLMClient instance
    else provider == "grok"
        LLMFactory->>LLMClient: new GrokClient(api_key, model)
        LLMFactory-->>Pipeline: GrokClient instance
    end
    
    Pipeline->>LLMClient: call_with_retry(prompt, data)
    
    loop Retry up to 3 times
        LLMClient->>Cache: check_cache(prompt, data)
        
        alt Cache Hit
            Cache-->>LLMClient: cached_response
        else Cache Miss
            LLMClient->>DashScope: API request
            DashScope-->>LLMClient: response
            LLMClient->>Cache: save(prompt, data, response)
        end
        
        alt Success
            LLMClient-->>Pipeline: response
        else Failure
            LLMClient->>LLMClient: wait (exponential backoff)
        end
    end
```

---

## Storage Architecture

### File System Structure

```mermaid
graph TD
    subgraph "Project Root"
        A[clipagent_mvp/]
    end
    
    subgraph "Data Directory"
        B[data/]
        B1[projects.json]
        B2[settings.json]
    end
    
    subgraph "Uploads Directory"
        C[uploads/]
        C1[tmp/]
        C2[project_id_1/]
        C3[project_id_2/]
    end
    
    subgraph "Project Structure"
        D[input/]
        D1[video.mp4]
        D2[subtitles.srt]
        
        E[output/]
        E1[clips/]
        E2[collections/]
        E3[metadata/]
        
        F[logs/]
        F1[processing.log]
    end
    
    subgraph "Metadata Files"
        G1[step1_outline.json]
        G2[step2_timeline.json]
        G3[step3_scoring.json]
        G4[step4_titles.json]
        G5[step5_clustering.json]
        G6[clips_metadata.json]
        G7[collections_metadata.json]
    end
    
    subgraph "Prompt Templates"
        H[prompt_en/]
        H1[outline.txt]
        H2[timeline.txt]
        H3[recommendation.txt]
        H4[title_generation.txt]
        H5[clustering.txt]
        H6[business/]
        H7[knowledge/]
    end
    
    A --> B
    A --> C
    A --> H
    
    B --> B1
    B --> B2
    
    C --> C1
    C --> C2
    C --> C3
    
    C2 --> D
    C2 --> E
    C2 --> F
    
    D --> D1
    D --> D2
    
    E --> E1
    E --> E2
    E --> E3
    
    E3 --> G1
    E3 --> G2
    E3 --> G3
    E3 --> G4
    E3 --> G5
    E3 --> G6
    E3 --> G7
    
    F --> F1
    
    H --> H1
    H --> H2
    H --> H3
    H --> H4
    H --> H5
    H --> H6
    H --> H7
    
    style A fill:#4caf50
    style B fill:#2196f3
    style C fill:#ff9800
    style E3 fill:#9c27b0
    style H fill:#00bcd4
```

### Data Model Relationships

```mermaid
erDiagram
    PROJECT ||--o{ CLIP : contains
    PROJECT ||--o{ COLLECTION : contains
    PROJECT ||--|| VIDEO : has
    PROJECT ||--|| SRT : has
    COLLECTION ||--o{ CLIP : includes
    
    PROJECT {
        string id PK
        string name
        string video_path
        string status
        string video_category
        datetime created_at
        datetime updated_at
        int current_step
        string error_message
    }
    
    CLIP {
        string id PK
        string project_id FK
        string title
        string generated_title
        string start_time
        string end_time
        float final_score
        string recommend_reason
        string outline
        array content
        int chunk_index
    }
    
    COLLECTION {
        string id PK
        string project_id FK
        string collection_title
        string collection_summary
        array clip_ids
        string collection_type
        datetime created_at
    }
    
    VIDEO {
        string path
        string format
        int duration
        int width
        int height
    }
    
    SRT {
        string path
        int entry_count
        string language
    }
```

---

## Deployment Architecture

### Docker Deployment

```mermaid
graph TB
    subgraph "Docker Host"
        subgraph "Docker Network: clipagent-network"
            A[clipagent-app Container]
            B[Volume: uploads]
            C[Volume: data]
            D[Volume: output]
        end
    end
    
    subgraph "Container: clipagent-app"
        E[Nginx<br/>Static Files]
        F[FastAPI Backend<br/>Port 8000]
        G[React Frontend<br/>Built Static]
    end
    
    subgraph "External Services"
        H[DashScope API]
        I[SiliconFlow API]
        J[Bilibili Platform]
    end
    
    K[User Browser] --> E
    E --> G
    E --> F
    
    F --> B
    F --> C
    F --> D
    F --> H
    F --> I
    F --> J
    
    style A fill:#2196f3
    style B fill:#4caf50
    style C fill:#4caf50
    style D fill:#4caf50
```

### Production Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        A[Nginx / Traefik]
    end
    
    subgraph "Application Tier"
        B1[App Instance 1]
        B2[App Instance 2]
        B3[App Instance N]
    end
    
    subgraph "Storage Tier"
        C1[Shared File Storage<br/>NFS / S3]
        C2[Database<br/>PostgreSQL]
        C3[Cache<br/>Redis]
    end
    
    subgraph "External Services"
        D1[DashScope API]
        D2[SiliconFlow API]
        D3[CDN<br/>CloudFlare]
    end
    
    E[Users] --> A
    A --> B1
    A --> B2
    A --> B3
    
    B1 --> C1
    B2 --> C1
    B3 --> C1
    
    B1 --> C2
    B2 --> C2
    B3 --> C2
    
    B1 --> C3
    B2 --> C3
    B3 --> C3
    
    B1 --> D1
    B2 --> D1
    B3 --> D1
    
    B1 --> D2
    B2 --> D2
    B3 --> D2
    
    C1 --> D3
    
    style A fill:#ff9800
    style C1 fill:#4caf50
    style C2 fill:#2196f3
    style C3 fill:#f44336
```

---

## Conclusion

These architecture diagrams provide a comprehensive visual understanding of the ClipAgent MVP system:

1. **System Architecture**: Shows the overall layered architecture from client to data storage
2. **Component Architecture**: Details the internal structure of backend and frontend components
3. **Data Flow**: Illustrates how data moves through the system from upload to final output
4. **Processing Pipeline**: Visualizes the 6-step video processing workflow
5. **LLM Integration**: Explains the factory pattern and provider abstraction
6. **Storage Architecture**: Maps out the file system and data model relationships
7. **Deployment Architecture**: Shows Docker and production deployment configurations

These diagrams serve as a reference for understanding, maintaining, and extending the ClipAgent MVP system.

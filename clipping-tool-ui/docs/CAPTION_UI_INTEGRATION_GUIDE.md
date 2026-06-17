# Caption System UI Integration Guide

This document explains how to integrate the caption system with the existing video upload UI and provides complete API examples.

## Table of Contents

1. [Video Upload API Changes](#video-upload-api-changes)
2. [Caption UI Components](#caption-ui-components)
3. [Integration Flow](#integration-flow)
4. [API Examples](#api-examples)
5. [UI State Management](#ui-state-management)
6. [Error Handling](#error-handling)

## Video Upload API Changes

### Updated Video Upload Endpoint

The video upload API now accepts an optional `caption_specification` field along with the HeyGen data:

```bash
POST /api/v1/videos/upload
Content-Type: application/json
```

**Request Body:**

```json
{
  "data": {
    "video_input_type": "url",
    "video_key": "https://www.youtube.com/watch?v=uaUowO1YuoM",
    "name": "My Video Title",
    "input_language": "",
    "output_settings": {
      "prompt": "Create compelling clips",
      "duration_types": ["60"],
      "aspect_ratio": "landscape",
      "is_captions_enabled": true
    },
    "source_type": "video_repurpose"
  },
  "title": "My Awesome Video",
  "description": "Video description",
  "caption_specification": {
    "animation": {
      "type": "karaoke_highlight"
    },
    "typography": {
      "font_family": "Arial",
      "font_size": 24,
      "font_weight": "bold",
      "font_style": "normal"
    },
    "colors": {
      "primary_text": "#FFFFFF",
      "secondary_text": "#808080",
      "outline_color": "#000000",
      "shadow_color": "#000000"
    },
    "effects": {
      "outline_width": 2,
      "shadow_distance": 2,
      "shadow_blur": 1
    },
    "positioning": {
      "alignment": "center",
      "vertical_position": "bottom",
      "margin_bottom": 50,
      "margin_sides": 20
    },
    "advanced": {
      "word_spacing": 1.0,
      "line_spacing": 1.2,
      "max_words_per_line": 6
    }
  }
}
```

### Video Upload cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/videos/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "video_input_type": "url",
      "video_key": "https://www.youtube.com/watch?v=uaUowO1YuoM",
      "name": "My Captioned Video",
      "input_language": "",
      "output_settings": {
        "prompt": "Create compelling clips with captions",
        "duration_types": ["60"],
        "aspect_ratio": "landscape",
        "is_captions_enabled": true
      },
      "source_type": "video_repurpose"
    },
    "title": "My Captioned Video",
    "description": "This video will have custom captions",
    "caption_specification": {
      "animation": {"type": "karaoke_highlight"},
      "typography": {"font_family": "Arial", "font_size": 24, "font_weight": "bold"},
      "colors": {"primary_text": "#FFFFFF", "outline_color": "#000000"},
      "effects": {"outline_width": 2},
      "positioning": {"alignment": "center", "vertical_position": "bottom"}
    }
  }'
```

## Caption UI Components

### 1. Caption Toggle Component

```jsx
const CaptionToggle = ({ enabled, onChange }) => (
  <div className="caption-toggle">
    <label className="flex items-center space-x-2">
      <input
        type="checkbox"
        checked={enabled}
        onChange={(e) => onChange(e.target.checked)}
        className="rounded border-gray-300"
      />
      <span className="text-sm font-medium">Add Captions</span>
    </label>
  </div>
);
```

### 2. Caption Style Selector

```jsx
const CaptionStyleSelector = ({ selectedStyle, onStyleChange }) => {
  const captionStyles = [
    {
      id: "karaoke_highlight",
      name: "Karaoke Highlight",
      description: "Word-by-word green highlighting",
      preview: "🎵 Hello World",
    },
    {
      id: "karaoke_rainbow",
      name: "Karaoke Rainbow",
      description: "Colorful rainbow highlighting",
      preview: "🌈 Hello World",
    },
    {
      id: "static",
      name: "Static Subtitles",
      description: "Simple fade-in/fade-out",
      preview: "Hello World",
    },
    {
      id: "minimal",
      name: "Minimal Style",
      description: "Clean, minimal subtitles",
      preview: "Hello World",
    },
  ];

  return (
    <div className="caption-style-selector">
      <h3 className="text-lg font-semibold mb-4">Caption Style</h3>
      <div className="grid grid-cols-2 gap-4">
        {captionStyles.map((style) => (
          <div
            key={style.id}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              selectedStyle === style.id
                ? "border-blue-500 bg-blue-50"
                : "border-gray-200 hover:border-gray-300"
            }`}
            onClick={() => onStyleChange(style.id)}
          >
            <div className="text-sm font-medium">{style.name}</div>
            <div className="text-xs text-gray-600 mt-1">
              {style.description}
            </div>
            <div className="text-lg mt-2">{style.preview}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 3. Caption Customization Panel

```jsx
const CaptionCustomizationPanel = ({ captionSpec, onSpecChange }) => {
  const updateSpec = (section, field, value) => {
    onSpecChange({
      ...captionSpec,
      [section]: {
        ...captionSpec[section],
        [field]: value,
      },
    });
  };

  return (
    <div className="caption-customization-panel space-y-6">
      {/* Typography Settings */}
      <div className="typography-settings">
        <h4 className="text-md font-semibold mb-3">Typography</h4>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Font Family
            </label>
            <select
              value={captionSpec.typography.font_family}
              onChange={(e) =>
                updateSpec("typography", "font_family", e.target.value)
              }
              className="w-full p-2 border rounded"
            >
              <option value="Arial">Arial</option>
              <option value="Helvetica">Helvetica</option>
              <option value="Times New Roman">Times New Roman</option>
              <option value="Verdana">Verdana</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Font Size</label>
            <input
              type="range"
              min="12"
              max="48"
              value={captionSpec.typography.font_size}
              onChange={(e) =>
                updateSpec("typography", "font_size", parseInt(e.target.value))
              }
              className="w-full"
            />
            <div className="text-xs text-gray-600">
              {captionSpec.typography.font_size}px
            </div>
          </div>
        </div>
      </div>

      {/* Color Settings */}
      <div className="color-settings">
        <h4 className="text-md font-semibold mb-3">Colors</h4>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Primary Text
            </label>
            <input
              type="color"
              value={captionSpec.colors.primary_text}
              onChange={(e) =>
                updateSpec("colors", "primary_text", e.target.value)
              }
              className="w-full h-10 border rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              Outline Color
            </label>
            <input
              type="color"
              value={captionSpec.colors.outline_color}
              onChange={(e) =>
                updateSpec("colors", "outline_color", e.target.value)
              }
              className="w-full h-10 border rounded"
            />
          </div>
        </div>
      </div>

      {/* Positioning Settings */}
      <div className="positioning-settings">
        <h4 className="text-md font-semibold mb-3">Positioning</h4>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Alignment</label>
            <select
              value={captionSpec.positioning.alignment}
              onChange={(e) =>
                updateSpec("positioning", "alignment", e.target.value)
              }
              className="w-full p-2 border rounded"
            >
              <option value="left">Left</option>
              <option value="center">Center</option>
              <option value="right">Right</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              Vertical Position
            </label>
            <select
              value={captionSpec.positioning.vertical_position}
              onChange={(e) =>
                updateSpec("positioning", "vertical_position", e.target.value)
              }
              className="w-full p-2 border rounded"
            >
              <option value="top">Top</option>
              <option value="center">Center</option>
              <option value="bottom">Bottom</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
};
```

### 4. Caption Preview Component

```jsx
const CaptionPreview = ({
  captionSpec,
  sampleText = "Hello World! This is a sample caption.",
}) => {
  const getPreviewStyle = () => {
    return {
      fontFamily: captionSpec.typography.font_family,
      fontSize: `${captionSpec.typography.font_size}px`,
      fontWeight: captionSpec.typography.font_weight,
      color: captionSpec.colors.primary_text,
      textAlign: captionSpec.positioning.alignment,
      textShadow: `2px 2px 0 ${captionSpec.colors.outline_color}`,
      padding: "20px",
      backgroundColor: "rgba(0,0,0,0.7)",
      borderRadius: "8px",
      margin: "10px 0",
    };
  };

  return (
    <div className="caption-preview">
      <h4 className="text-md font-semibold mb-3">Preview</h4>
      <div className="bg-gray-900 p-4 rounded-lg">
        <div style={getPreviewStyle()}>{sampleText}</div>
      </div>
    </div>
  );
};
```

## Integration Flow

### 1. Multi-Step Video Upload Component

```jsx
const VideoUploadWithCaptions = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [heygenData, setHeygenData] = useState({
    video_input_type: "url",
    video_key: "",
    name: "",
    input_language: "",
    output_settings: {
      prompt: "Create compelling clips",
      duration_types: ["60"],
      aspect_ratio: "landscape",
      is_captions_enabled: true,
    },
    source_type: "video_repurpose",
  });
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [captionsEnabled, setCaptionsEnabled] = useState(false);
  const [captionSpec, setCaptionSpec] = useState(getDefaultCaptionSpec());
  const [uploading, setUploading] = useState(false);

  const steps = [
    {
      id: 1,
      title: "Video Configuration",
      description: "Set up your video source and settings",
    },
    {
      id: 2,
      title: "Caption Customization",
      description: "Customize captions and preview",
    },
    {
      id: 3,
      title: "Review & Submit",
      description: "Review settings and submit for processing",
    },
  ];

  const getDefaultCaptionSpec = () => ({
    animation: {
      type: "karaoke_highlight",
    },
    typography: {
      font_family: "Arial",
      font_size: 24,
      font_weight: "bold",
      font_style: "normal",
    },
    colors: {
      primary_text: "#FFFFFF",
      secondary_text: "#808080",
      outline_color: "#000000",
      shadow_color: "#000000",
    },
    effects: {
      outline_width: 2,
      shadow_distance: 2,
      shadow_blur: 1,
    },
    positioning: {
      alignment: "center",
      vertical_position: "bottom",
      margin_bottom: 50,
      margin_sides: 20,
    },
    advanced: {
      word_spacing: 1.0,
      line_spacing: 1.2,
      max_words_per_line: 6,
    },
  });

  const canProceedToNextStep = () => {
    switch (currentStep) {
      case 1:
        return heygenData.video_key && heygenData.name && title;
      case 2:
        return true; // Caption step is optional
      case 3:
        return true; // Review step
      default:
        return false;
    }
  };

  const nextStep = () => {
    if (canProceedToNextStep() && currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleUpload = async () => {
    if (!heygenData.video_key || !title) return;

    setUploading(true);

    const requestBody = {
      data: heygenData,
      title: title,
      description: description,
    };

    if (captionsEnabled) {
      requestBody.caption_specification = captionSpec;
    }

    try {
      const response = await fetch("/api/v1/videos/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${getAuthToken()}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const result = await response.json();

      if (response.ok) {
        // Success - redirect to video status page
        router.push(`/videos/${result.id}/status`);
      } else {
        throw new Error(result.detail || "Upload failed");
      }
    } catch (error) {
      console.error("Upload error:", error);
      // Handle error
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="video-upload-container max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Upload Video with Captions</h1>

      {/* HeyGen Data Section */}
      <div className="heygen-data-section mb-8">
        <h2 className="text-xl font-semibold mb-4">
          Video Source Configuration
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Video URL</label>
            <input
              type="url"
              value={heygenData.video_key}
              onChange={(e) =>
                setHeygenData({ ...heygenData, video_key: e.target.value })
              }
              className="w-full p-2 border rounded"
              placeholder="https://www.youtube.com/watch?v=..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Video Name</label>
            <input
              type="text"
              value={heygenData.name}
              onChange={(e) =>
                setHeygenData({ ...heygenData, name: e.target.value })
              }
              className="w-full p-2 border rounded"
              placeholder="Enter video name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Prompt</label>
            <input
              type="text"
              value={heygenData.output_settings.prompt}
              onChange={(e) =>
                setHeygenData({
                  ...heygenData,
                  output_settings: {
                    ...heygenData.output_settings,
                    prompt: e.target.value,
                  },
                })
              }
              className="w-full p-2 border rounded"
              placeholder="Create compelling clips"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              Aspect Ratio
            </label>
            <select
              value={heygenData.output_settings.aspect_ratio}
              onChange={(e) =>
                setHeygenData({
                  ...heygenData,
                  output_settings: {
                    ...heygenData.output_settings,
                    aspect_ratio: e.target.value,
                  },
                })
              }
              className="w-full p-2 border rounded"
            >
              <option value="landscape">Landscape</option>
              <option value="portrait">Portrait</option>
              <option value="square">Square</option>
            </select>
          </div>
        </div>
      </div>

      {/* Video Details */}
      <div className="video-details mb-8">
        <h2 className="text-xl font-semibold mb-4">Video Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="Enter video title"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              Description
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="Enter video description"
            />
          </div>
        </div>
      </div>

      {/* Caption Toggle */}
      <div className="caption-section mb-8">
        <CaptionToggle
          enabled={captionsEnabled}
          onChange={setCaptionsEnabled}
        />
      </div>

      {/* Caption Configuration */}
      {captionsEnabled && (
        <div className="caption-configuration space-y-6">
          <CaptionStyleSelector
            selectedStyle={captionSpec.animation.type}
            onStyleChange={(style) =>
              setCaptionSpec({
                ...captionSpec,
                animation: { ...captionSpec.animation, type: style },
              })
            }
          />

          <CaptionCustomizationPanel
            captionSpec={captionSpec}
            onSpecChange={setCaptionSpec}
          />

          <CaptionPreview captionSpec={captionSpec} />
        </div>
      )}

      {/* Upload Button */}
      <div className="upload-actions">
        <button
          onClick={handleUpload}
          disabled={!heygenData.video_key || !title || uploading}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {uploading
            ? "Submitting to HeyGen..."
            : "Submit Video for Processing"}
        </button>
      </div>
    </div>
  );
};
```

## API Examples

### 1. Get Available Caption Templates

```bash
curl -X GET "http://localhost:8000/api/v1/captions/templates" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**

```json
[
  {
    "id": "template-1",
    "name": "Karaoke Highlight",
    "description": "Word-by-word green highlighting with smooth transitions",
    "template_type": "karaoke",
    "template_config": {
      "animation": { "type": "karaoke_highlight" },
      "typography": { "font_family": "Arial", "font_size": 24 },
      "colors": { "primary_text": "#FFFFFF", "outline_color": "#000000" },
      "effects": { "outline_width": 2 },
      "positioning": { "alignment": "center", "vertical_position": "bottom" }
    },
    "is_default": true
  }
]
```

### 2. Update Caption Specification for Existing Video

```bash
curl -X POST "http://localhost:8000/api/v1/captions/video/{video_id}/specification" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "caption_specification": {
      "animation": {"type": "karaoke_rainbow"},
      "typography": {"font_family": "Arial", "font_size": 28},
      "colors": {"primary_text": "#FFFFFF", "outline_color": "#000000"},
      "effects": {"outline_width": 3},
      "positioning": {"alignment": "center", "vertical_position": "bottom"}
    }
  }'
```

### 3. Get Caption Processing Status

```bash
curl -X GET "http://localhost:8000/api/v1/captions/video/{video_id}/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**

```json
{
  "video_id": "video-123",
  "caption_specification": {
    "animation": { "type": "karaoke_highlight" },
    "typography": { "font_family": "Arial", "font_size": 24 }
  },
  "caption_processing_status": "completed",
  "caption_processed_at": "2024-01-15T10:30:00Z",
  "processed_video_urls": {
    "clip-1": "https://drive.google.com/file/d/.../view",
    "clip-2": "https://drive.google.com/file/d/.../view"
  },
  "errors": {}
}
```

### 4. Apply Caption Template to Video

```bash
curl -X POST "http://localhost:8000/api/v1/captions/video/{video_id}/apply-template/{template_id}" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## UI State Management

### React Hook for Caption Management

```jsx
const useCaptionManagement = (videoId) => {
  const [captionStatus, setCaptionStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateCaptionSpec = async (captionSpec) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/captions/video/${videoId}/specification`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${getAuthToken()}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ caption_specification: captionSpec }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update caption specification");
      }

      const result = await response.json();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getCaptionStatus = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/captions/video/${videoId}/status`, {
        headers: {
          Authorization: `Bearer ${getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to get caption status");
      }

      const status = await response.json();
      setCaptionStatus(status);
      return status;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const applyTemplate = async (templateId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/captions/video/${videoId}/apply-template/${templateId}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${getAuthToken()}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to apply template");
      }

      const result = await response.json();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    captionStatus,
    loading,
    error,
    updateCaptionSpec,
    getCaptionStatus,
    applyTemplate,
  };
};
```

## Error Handling

### Common Error Scenarios

1. **Invalid Caption Specification**

```json
{
  "detail": "Invalid caption specification: Font size must be between 12 and 72"
}
```

2. **Caption Processing Failed**

```json
{
  "video_id": "video-123",
  "caption_processing_status": "failed",
  "errors": {
    "clip-1": "Failed to download from HeyGen"
  }
}
```

3. **Video Not Found**

```json
{
  "detail": "Video video-123 not found"
}
```

### Error Handling Component

```jsx
const CaptionErrorHandler = ({ error, onRetry }) => {
  const getErrorMessage = (error) => {
    if (error.includes("Invalid caption specification")) {
      return "Please check your caption settings and try again.";
    }
    if (error.includes("Failed to download")) {
      return "Unable to process video. Please try again later.";
    }
    return "An unexpected error occurred. Please try again.";
  };

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-center">
        <div className="text-red-400 mr-3">⚠️</div>
        <div>
          <div className="text-red-800 font-medium">
            Caption Processing Error
          </div>
          <div className="text-red-600 text-sm mt-1">
            {getErrorMessage(error)}
          </div>
        </div>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-3 bg-red-600 text-white px-4 py-2 rounded text-sm hover:bg-red-700"
        >
          Retry
        </button>
      )}
    </div>
  );
};
```

## Best Practices

### 1. Progressive Enhancement

- Start with basic video upload
- Add caption toggle for advanced users
- Provide sensible defaults for caption specifications

### 2. User Experience

- Show real-time preview of caption styles
- Provide preset templates for quick setup
- Allow customization for power users
- Show processing status clearly

### 3. Performance

- Lazy load caption customization components
- Debounce caption specification updates
- Cache template data
- Optimize preview rendering

### 4. Accessibility

- Provide keyboard navigation for all controls
- Include proper ARIA labels
- Ensure color contrast meets WCAG guidelines
- Support screen readers

This integration guide provides everything needed to build a comprehensive caption system UI that works seamlessly with the existing video upload flow.

## Multi-Step UI Implementation

### Enhanced Multi-Step Component

For a better user experience, implement a multi-step wizard that separates video configuration from caption customization:

```jsx
const MultiStepVideoUpload = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [heygenData, setHeygenData] = useState({
    video_input_type: "url",
    video_key: "",
    name: "",
    input_language: "",
    output_settings: {
      prompt: "Create compelling clips",
      duration_types: ["60"],
      aspect_ratio: "landscape",
      is_captions_enabled: true,
    },
    source_type: "video_repurpose",
  });
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [captionsEnabled, setCaptionsEnabled] = useState(false);
  const [captionSpec, setCaptionSpec] = useState(getDefaultCaptionSpec());
  const [uploading, setUploading] = useState(false);

  const steps = [
    {
      id: 1,
      title: "Video Configuration",
      description: "Set up your video source and settings",
    },
    {
      id: 2,
      title: "Caption Customization",
      description: "Customize captions and preview",
    },
    {
      id: 3,
      title: "Review & Submit",
      description: "Review settings and submit for processing",
    },
  ];

  const canProceedToNextStep = () => {
    switch (currentStep) {
      case 1:
        return heygenData.video_key && heygenData.name && title;
      case 2:
        return true; // Caption step is optional
      case 3:
        return true; // Review step
      default:
        return false;
    }
  };

  const nextStep = () => {
    if (canProceedToNextStep() && currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-8">Create Video with Captions</h1>

      {/* Step Progress Indicator */}
      <div className="step-progress mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div
                className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  currentStep >= step.id
                    ? "bg-blue-600 border-blue-600 text-white"
                    : "border-gray-300 text-gray-500"
                }`}
              >
                {step.id}
              </div>
              <div className="ml-3">
                <div
                  className={`text-sm font-medium ${
                    currentStep >= step.id ? "text-blue-600" : "text-gray-500"
                  }`}
                >
                  {step.title}
                </div>
                <div className="text-xs text-gray-500">{step.description}</div>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-4 ${
                    currentStep > step.id ? "bg-blue-600" : "bg-gray-300"
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="step-content min-h-96">
        {currentStep === 1 && (
          <VideoConfigurationStep
            heygenData={heygenData}
            setHeygenData={setHeygenData}
            title={title}
            setTitle={setTitle}
            description={description}
            setDescription={setDescription}
          />
        )}

        {currentStep === 2 && (
          <CaptionCustomizationStep
            captionsEnabled={captionsEnabled}
            setCaptionsEnabled={setCaptionsEnabled}
            captionSpec={captionSpec}
            setCaptionSpec={setCaptionSpec}
          />
        )}

        {currentStep === 3 && (
          <ReviewAndSubmitStep
            heygenData={heygenData}
            title={title}
            description={description}
            captionsEnabled={captionsEnabled}
            captionSpec={captionSpec}
            uploading={uploading}
            onUpload={handleUpload}
          />
        )}
      </div>

      {/* Step Navigation */}
      <div className="step-navigation flex justify-between mt-8">
        <button
          onClick={prevStep}
          disabled={currentStep === 1}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
        >
          Previous
        </button>

        {currentStep < 3 ? (
          <button
            onClick={nextStep}
            disabled={!canProceedToNextStep()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-blue-700"
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleUpload}
            disabled={!canProceedToNextStep() || uploading}
            className="px-6 py-2 bg-green-600 text-white rounded-lg disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-green-700"
          >
            {uploading ? "Submitting..." : "Submit for Processing"}
          </button>
        )}
      </div>
    </div>
  );
};
```

### Step Components

#### Step 1: Video Configuration

```jsx
const VideoConfigurationStep = ({
  heygenData,
  setHeygenData,
  title,
  setTitle,
  description,
  setDescription,
}) => {
  return (
    <div className="space-y-6">
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium mb-4">Video Source</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Video URL</label>
            <input
              type="url"
              value={heygenData.video_key}
              onChange={(e) =>
                setHeygenData({ ...heygenData, video_key: e.target.value })
              }
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="https://www.youtube.com/watch?v=..."
            />
            <p className="text-xs text-gray-600 mt-1">
              YouTube, Google Drive, or other supported URLs
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Video Name</label>
            <input
              type="text"
              value={heygenData.name}
              onChange={(e) =>
                setHeygenData({ ...heygenData, name: e.target.value })
              }
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter video name"
            />
          </div>
        </div>
      </div>

      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium mb-4">Processing Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">AI Prompt</label>
            <textarea
              value={heygenData.output_settings.prompt}
              onChange={(e) =>
                setHeygenData({
                  ...heygenData,
                  output_settings: {
                    ...heygenData.output_settings,
                    prompt: e.target.value,
                  },
                })
              }
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Create compelling clips"
              rows="3"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              Aspect Ratio
            </label>
            <select
              value={heygenData.output_settings.aspect_ratio}
              onChange={(e) =>
                setHeygenData({
                  ...heygenData,
                  output_settings: {
                    ...heygenData.output_settings,
                    aspect_ratio: e.target.value,
                  },
                })
              }
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="landscape">Landscape (16:9)</option>
              <option value="portrait">Portrait (9:16)</option>
              <option value="square">Square (1:1)</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium mb-4">Video Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter video title"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              Description
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter video description"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
```

#### Step 2: Caption Customization

```jsx
const CaptionCustomizationStep = ({
  captionsEnabled,
  setCaptionsEnabled,
  captionSpec,
  setCaptionSpec,
}) => {
  return (
    <div className="space-y-6">
      <div className="bg-gray-50 p-6 rounded-lg">
        <CaptionToggle
          enabled={captionsEnabled}
          onChange={setCaptionsEnabled}
        />
      </div>

      {captionsEnabled && (
        <div className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <CaptionStyleSelector
              selectedStyle={captionSpec.animation.type}
              onStyleChange={(style) =>
                setCaptionSpec({
                  ...captionSpec,
                  animation: { ...captionSpec.animation, type: style },
                })
              }
            />
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <CaptionCustomizationPanel
              captionSpec={captionSpec}
              onSpecChange={setCaptionSpec}
            />
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <CaptionPreview captionSpec={captionSpec} />
          </div>
        </div>
      )}

      {!captionsEnabled && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <div className="text-blue-800 font-medium mb-2">
            No Captions Selected
          </div>
          <div className="text-blue-600 text-sm">
            Your video will be processed without custom captions. You can always
            add captions later.
          </div>
        </div>
      )}
    </div>
  );
};
```

#### Step 3: Review and Submit

```jsx
const ReviewAndSubmitStep = ({
  heygenData,
  title,
  description,
  captionsEnabled,
  captionSpec,
  uploading,
  onUpload,
}) => {
  return (
    <div className="space-y-6">
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium mb-4">Video Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Video URL:</span>
            <div className="text-gray-600 truncate">{heygenData.video_key}</div>
          </div>
          <div>
            <span className="font-medium text-gray-700">Title:</span>
            <div className="text-gray-600">{title}</div>
          </div>
          <div>
            <span className="font-medium text-gray-700">Aspect Ratio:</span>
            <div className="text-gray-600 capitalize">
              {heygenData.output_settings.aspect_ratio}
            </div>
          </div>
          <div>
            <span className="font-medium text-gray-700">Captions:</span>
            <div className="text-gray-600">
              {captionsEnabled ? "Enabled" : "Disabled"}
            </div>
          </div>
        </div>
      </div>

      {captionsEnabled && (
        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="text-lg font-medium mb-4">Caption Settings</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Style:</span>
              <div className="text-gray-600 capitalize">
                {captionSpec.animation.type.replace("_", " ")}
              </div>
            </div>
            <div>
              <span className="font-medium text-gray-700">Font:</span>
              <div className="text-gray-600">
                {captionSpec.typography.font_family}{" "}
                {captionSpec.typography.font_size}px
              </div>
            </div>
          </div>
        </div>
      )}

      {captionsEnabled && (
        <div className="bg-gray-900 p-6 rounded-lg">
          <h3 className="text-lg font-medium mb-4 text-white">
            Caption Preview
          </h3>
          <div className="flex justify-center">
            <div
              style={{
                fontFamily: captionSpec.typography.font_family,
                fontSize: `${Math.min(captionSpec.typography.font_size, 32)}px`,
                fontWeight: captionSpec.typography.font_weight,
                color: captionSpec.colors.primary_text,
                textAlign: captionSpec.positioning.alignment,
                textShadow: `2px 2px 0 ${captionSpec.colors.outline_color}`,
                padding: "20px",
                backgroundColor: "rgba(0,0,0,0.7)",
                borderRadius: "8px",
                maxWidth: "80%",
              }}
            >
              Hello World! This is how your captions will look.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

### Benefits of Multi-Step UI

1. **Better UX Flow**: Clear separation of concerns - video setup vs caption customization
2. **Progressive Disclosure**: Users can focus on one thing at a time
3. **Validation**: Each step validates before proceeding
4. **Real-time Preview**: Caption preview in dedicated step
5. **Review Step**: Final confirmation before submission
6. **Mobile Friendly**: Easier to navigate on smaller screens
7. **Error Prevention**: Step-by-step validation reduces errors

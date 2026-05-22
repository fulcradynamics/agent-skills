---
name: fulcra-create-annotations
description: "Define and create custom data types and schemas (Annotations) in Fulcra using CURL during user onboarding."
---

# Fulcra Create Annotations

This utility skill provides the exact CURL commands and JSON schemas needed to create custom data types (Annotations) in a user's Fulcra account. Use this primarily during onboarding to set up the data structures for a user's intent.

## Authentication

Always retrieve a fresh access token using the Fulcra CLI before making requests:
```bash
TOKEN=$(uv tool run fulcra-api auth print-access-token)
```

## Schema Discovery

Before creating an annotation, particularly one with specific measurements (like volume, mass, distance, or temperature), query the schema endpoints to understand the required JSON structure and valid units based on the user's intent.

**1. Annotation Schema:** Understand the root fields (`name`, `description`, `annotation_type`, etc.)
```bash
curl -s -H "Authorization: Bearer $TOKEN" https://api.fulcradynamics.com/user/v1alpha1/schema/annotation
```

**2. Measurement Schema:** Understand the exact structure for the `measurement_spec` based on the chosen type, including valid enumerations for `unit`.
```bash
curl -s -H "Authorization: Bearer $TOKEN" https://api.fulcradynamics.com/user/v1alpha1/schema/measurement
```
Use the output of these commands to ensure your JSON payload is perfectly formed.

## Creating an Annotation

Annotations are created by sending a `POST` request to the Fulcra API.

**CRITICAL RULE:** Execute the `curl` POST command exactly ONCE per desired annotation. The API does not upsert. Every POST request creates a new duplicate. Do not retry just to view headers.

```bash
curl -i -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... json payload ... }' \
  https://api.fulcradynamics.com/user/v1alpha1/annotation
```

### Handling the Response

The creation endpoint returns an HTTP `303 See Other` status. There is no JSON response body. 
To get the ID of the newly created annotation, look at the `location` header in the curl output:
`location: https://api.fulcradynamics.com/user/v1alpha1/annotation/<UUID>`

## JSON Payload Examples

### 1. Moment Annotation
Used for tracking occurrences of an event without a specific measurement.
```json
{
  "annotation_type": "moment",
  "name": "Target Name",
  "description": "Description of the moment",
  "tags": []
}
```

### 2. Numeric Annotation (Count)
Used for tracking a specific quantity or number.
```json
{
  "annotation_type": "numeric",
  "name": "Target Name",
  "description": "Description of the count",
  "measurement_spec": {
    "measurement_type": "count",
    "value_type": "real",
    "metric_kind": "discrete",
    "unit": null,
    "count": { "value": null }
  },
  "tags": []
}
```

### 3. Boolean Annotation
Used for tracking simple Yes/No or True/False states.
```json
{
  "annotation_type": "boolean",
  "name": "Target Name",
  "description": "Description of the boolean",
  "measurement_spec": {
    "measurement_type": "boolean",
    "value_type": "boolean",
    "metric_kind": "discrete",
    "unit": null,
    "boolean": { "value": null }
  },
  "tags": []
}
```

### 4. Scale Annotation
Used for 1-5 scales (e.g., mood, pain, intensity). This requires a `spec` block to map labels, colors, and emojis.
```json
{
  "annotation_type": "scale",
  "name": "Target Name",
  "description": "Description of the scale",
  "measurement_spec": {
    "measurement_type": "scale",
    "value_type": "integer",
    "metric_kind": "discrete",
    "unit": null,
    "scale": { "min_allowed": 1, "max_allowed": 5, "value": null }
  },
  "spec": {
    "default_note": null,
    "scale": {
      "label_mapping": {
        "mapping_type": "string",
        "string": { "mapping": { "1": "Very Low", "2": "Low", "3": "Medium", "4": "High", "5": "Very High" } }
      },
      "scale_mapping": {
        "mapping_type": "emoji",
        "color": { "mapping": { "1": "#ff3b30", "2": "#ff9e96", "3": "#8a8a8f", "4": "#99e3ab", "5": "#33c759" } },
        "string": { "mapping": { "1": "annotation-emoji-1", "2": "annotation-emoji-2", "3": "annotation-emoji-3", "4": "annotation-emoji-4", "5": "annotation-emoji-5" } }
      }
    }
  },
  "tags": []
}
```
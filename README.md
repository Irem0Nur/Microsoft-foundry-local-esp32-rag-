---
title: Soil Classifier
emoji: 🌱
colorFrom: green
colorTo: brown
sdk: docker
pinned: false
---

# Soil Classifier API

Toprak türü sınıflandırma API'si.

## Endpoint

`POST /predict`

```json
{
  "imageBase64": "base64_encoded_image"
}
```

## Yanıt

```json
{
  "soilType": "clay",
  "confidence": 85,
  "summary": "Estimated using fine-tuned ViT soil classifier."
}
```

# Business Requirements Document (BRD)

## 1) Project Overview
**Project Name:** Fashion AI Studio

Fashion AI Studio is a web application that generates high‑quality fashion product images using generative AI. Users upload garment images and optional accessories/patterns, select model and framing options, and receive AI‑generated images for e‑commerce use. The system tracks generation history and usage cost, with admin‑only access to aggregated reporting.

## 2) Objectives
- Enable fast, high‑quality AI fashion image generation for uploaded garments.
- Provide a simple, guided UI for configuration and uploads.
- Offer per‑user usage tracking (images and cost) and admin reporting.
- Support secure access with role‑based controls (standard user vs admin).

## 3) Stakeholders
- **Business Owner/Product Manager**: Defines feature scope and success metrics.
- **Admin Users**: Manage access, view usage history and totals.
- **End Users (Designers/Operators)**: Generate images from garment inputs.
- **Engineering**: Build and maintain Django backend and AI integration.

## 4) In Scope
- User authentication (login/logout) and admin‑only user creation.
- AI image generation pipeline with multiple views per garment.
- Upload flow for garment images, model images, optional pattern and brooch.
- Storage of generated images and per‑request history in database.
- Admin history page with total images and total cost.
- Download generated images as ZIP.

## 5) Out of Scope
- Public user registration or self‑service signup.
- Payments/billing integration.
- External asset management systems or CDN integration.
- Mobile app (browser‑only UI).

## 6) User Personas
- **Operator (Standard User):**
  - Needs quick generation of product images.
  - Access limited to generation features.

- **Admin User:**
  - Needs visibility into usage and costs.
  - Can create new user accounts.

## 7) Functional Requirements
### 7.1 Authentication & Access Control
- Users must log in to access the application.
- Admins can create new users; non‑admins cannot access the user creation page.
- Admins can access the history dashboard; non‑admins are redirected to the studio.

### 7.2 Image Generation
- The system must accept:
  - Garment images (one or more).
  - Model reference images.
  - Optional pattern image.
  - Optional accessory/brooch image and placement.
  - Gender and body type.
  - Number of images (single view or multi‑view set).
  - Optional special instructions.
- The system must generate outputs using the Gemini image model with strict color/texture preservation instructions.
- The system must support multiple views (front/back/left/closeup) when requested.

### 7.3 File Storage & Retrieval
- Generated images are saved under a date‑based folder structure.
- System must allow users to download a ZIP of generated images for a selected run.

### 7.4 Usage Tracking
- The system must track per‑user totals: number of images and total cost.
- Each generation request must create a history entry capturing inputs and outputs.
- Admin history view must show:
  - Total images generated across all users.
  - Total cost across all users.
  - Paginated list of generation history.

## 8) Data Requirements
### 8.1 Core Entities
- **ImageGenerationSummary**: total_images, total_cost, user, timestamps.
- **ImageGenerationHistory**: timestamp, gender, bodytype, uploaded_images, generated_images, generated_count, cost_per_image, totals, created_at.

### 8.2 File Storage
- Media storage for generated images by date and run.
- Optional JSON logs in media/json (legacy/supporting data).

## 9) Integrations
- **Google Gemini (genai) API** for image generation.
- Django REST Framework for API endpoints.

## 10) Non‑Functional Requirements
- **Performance:** Support parallel generation with controlled concurrency.
- **Security:**
  - Session‑based authentication.
  - Admin‑only endpoints for history.
- **Reliability:**
  - Retry logic on model generation failures.
  - Safe handling of invalid or corrupted images.
- **Usability:**
  - Clean, guided UI with upload previews.
  - Clear feedback on generation status and errors.

## 11) Assumptions
- Gemini API key is configured in environment variables.
- Server has sufficient CPU/RAM for concurrent image processing.
- Media storage path is writable.

## 12) Risks & Mitigations
- **API failures or latency:** Add retries and timeouts (already present).
- **Large file uploads:** Enforce size limits and provide user feedback.
- **Cost overrun:** Admin dashboard provides visibility into usage totals.

## 13) Success Metrics
- Time to generate images per request meets business SLA.
- High successful generation rate (low error/retry frequency).
- Admins can audit usage and costs with complete history coverage.

## 14) Future Enhancements (Optional)
- Public signup with email verification.
- Role‑based pricing or quotas.
- Download management and history export (CSV).
- Model selection with multiple AI backends.

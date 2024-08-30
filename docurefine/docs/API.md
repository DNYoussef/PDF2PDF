# DocuRefine API Documentation

This document describes the API endpoints for the DocuRefine web application.

## Endpoints

### 1. Process Document

**URL:** `/process`
**Method:** `POST`
**Content-Type:** `multipart/form-data`

#### Request Parameters

- `file`: The document file to be processed (PDF, PNG, JPG, JPEG, DOCX, or HTML)

#### Response

- **Success Response:**
  - **Code:** 202
  - **Content:** `{ "task_id": "<task_id>" }`

- **Error Response:**
  - **Code:** 400
  - **Content:** `{ "error": "<error_message>" }`

  OR

  - **Code:** 500
  - **Content:** `{ "error": "An error occurred while processing the file" }`

### 2. Check Task Status

**URL:** `/status/<task_id>`
**Method:** `GET`

#### Response

- **Success Response:**
  - **Code:** 200
  - **Content:** 
    ```json
    {
      "state": "<task_state>",
      "status": "<status_message>",
      "result": "<result_data>"  // Only present when task is completed
    }
    ```

- **Error Response:**
  - **Code:** 404
  - **Content:** `{ "error": "Task not found" }`

### 3. Download Processed Document

**URL:** `/download/<task_id>`
**Method:** `GET`

#### Response

- **Success Response:**
  - **Code:** 200
  - **Content:** The processed PDF file

- **Error Response:**
  - **Code:** 404
  - **Content:** `{ "error": "Output file not found" }`

  OR

  - **Code:** 400
  - **Content:** `{ "error": "Task not completed" }`

## Error Handling

The API uses the following error codes:

- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Error responses will include a JSON object with an "error" key containing a description of the error.
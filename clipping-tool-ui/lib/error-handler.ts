// Error handling utilities for consistent error responses

export interface ApiError {
  error: string;
  message: string;
  details?: any;
  code?: string;
}

export interface ValidationError {
  field: string;
  message: string;
}

export class AppError extends Error {
  public statusCode: number;
  public code?: string;
  public details?: any;

  constructor(
    message: string,
    statusCode: number = 500,
    code?: string,
    details?: any
  ) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
    this.name = "AppError";
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: any) {
    super(message, 400, "VALIDATION_ERROR", details);
    this.name = "ValidationError";
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string = "Authentication failed") {
    super(message, 401, "AUTH_ERROR");
    this.name = "AuthenticationError";
  }
}

export class AuthorizationError extends AppError {
  constructor(message: string = "Access denied") {
    super(message, 403, "AUTHZ_ERROR");
    this.name = "AuthorizationError";
  }
}

export class NotFoundError extends AppError {
  constructor(message: string = "Resource not found") {
    super(message, 404, "NOT_FOUND");
    this.name = "NotFoundError";
  }
}

export class ConflictError extends AppError {
  constructor(message: string = "Resource conflict") {
    super(message, 409, "CONFLICT");
    this.name = "ConflictError";
  }
}

export class ExternalServiceError extends AppError {
  constructor(service: string, message: string) {
    super(
      `External service error (${service}): ${message}`,
      502,
      "EXTERNAL_SERVICE_ERROR"
    );
    this.name = "ExternalServiceError";
  }
}

// Error handler for API routes
export function handleApiError(error: unknown): Response {
  console.error("API Error:", error);

  if (error instanceof AppError) {
    return new Response(
      JSON.stringify({
        error: error.message,
        code: error.code,
        details: error.details,
      }),
      {
        status: error.statusCode,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  if (error instanceof Error) {
    return new Response(
      JSON.stringify({
        error: "Internal server error",
        message: error.message,
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }

  return new Response(
    JSON.stringify({
      error: "Unknown error occurred",
    }),
    {
      status: 500,
      headers: { "Content-Type": "application/json" },
    }
  );
}

// Error handler for Next.js API routes
export function handleNextApiError(error: unknown) {
  console.error("Next.js API Error:", error);

  if (error instanceof AppError) {
    return {
      error: error.message,
      code: error.code,
      details: error.details,
      status: error.statusCode,
    };
  }

  if (error instanceof Error) {
    return {
      error: "Internal server error",
      message: error.message,
      status: 500,
    };
  }

  return {
    error: "Unknown error occurred",
    status: 500,
  };
}

// Utility to check if error is a known error type
export function isKnownError(error: unknown): error is AppError {
  return error instanceof AppError;
}

// Utility to extract error message safely
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === "string") {
    return error;
  }
  return "An unknown error occurred";
}

// Utility to extract error status code safely
export function getErrorStatus(error: unknown): number {
  if (error instanceof AppError) {
    return error.statusCode;
  }
  return 500;
}

/**
 * Step 6: Schema-First Response Validation (Frontend)
 * TypeScript service for validating streaming JSON responses using AJV.
 */

import Ajv from 'ajv';
import type { ValidateFunction, ErrorObject } from 'ajv';
import responseSchema from '../schemas/response.schema.json';

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

export interface FallbackResponse {
  main_advice: string;
  reasoning?: string;
  confidence_score?: number;
  alternatives?: string[] | null;
  model_identifier?: string;
}

class SchemaValidator {
  private ajv: Ajv;
  private validate: ValidateFunction;

  constructor() {
    this.ajv = new Ajv({ 
      allErrors: true,
      strict: false // Allow additional properties not in schema
    });
    this.validate = this.ajv.compile(responseSchema);
  }

  /**
   * Validate JSON data against the StructuredAdvice schema
   */
  validateJson(data: any): ValidationResult {
    try {
      const isValid = this.validate(data);
      
      if (!isValid) {
        const errorMessages = this.validate.errors?.map((err: ErrorObject) => 
          `${err.instancePath} ${err.message}`
        ).join(', ') || 'Unknown validation error';
        
        console.warn('Schema validation failed:', errorMessages);
        return {
          isValid: false,
          error: `Schema validation failed: ${errorMessages}`
        };
      }
      
      return { isValid: true };
    } catch (error) {
      console.error('Validation error:', error);
      return {
        isValid: false,
        error: `Validation error: ${error instanceof Error ? error.message : 'Unknown error'}`
      };
    }
  }

  /**
   * Validate streaming chunk - handles partial JSON during streaming
   */
  validateStreamingChunk(jsonString: string, isComplete: boolean = false): ValidationResult {
    if (!jsonString.trim()) {
      return { isValid: true }; // Empty chunks are OK during streaming
    }

    // For complete responses, do full validation
    if (isComplete) {
      try {
        const data = JSON.parse(jsonString);
        return this.validateJson(data);
      } catch (error) {
        return {
          isValid: false,
          error: `Invalid JSON format: ${error instanceof Error ? error.message : 'Parse error'}`
        };
      }
    }

    // For partial responses, check if it's potentially valid JSON
    try {
      const data = JSON.parse(jsonString);
      return this.validateJson(data);
    } catch {
      // Incomplete JSON is expected during streaming
      return { isValid: true };
    }
  }

  /**
   * Create a fallback response when validation fails
   */
  createFallbackResponse(originalText: string, errorMessage: string): FallbackResponse {
    return {
      main_advice: originalText.trim() || "Sorry, I encountered an error generating a response.",
      reasoning: `Response validation failed: ${errorMessage}`,
      confidence_score: 0.1,
      alternatives: null,
      model_identifier: "validation_fallback"
    };
  }

  /**
   * Get the JSON schema for external use
   */
  getSchema() {
    return responseSchema;
  }
}

// Export singleton instance
export const schemaValidator = new SchemaValidator(); 
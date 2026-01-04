import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, timeout } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private backendUrl = 'http://localhost:5000/'; // Define backend URL
  private timeoutDuration = 15000; // 15 seconds timeout

  constructor(private http: HttpClient) {}

  // Generic GET request with timeout
  get(endpoint: string, params?: any): Observable<any> {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.append(key, params[key]);
        }
      });
    }
    
    return this.http.get(`${this.backendUrl}${endpoint}`, { 
      params: httpParams,
      headers: {
        'Content-Type': 'application/json'
      }
    }).pipe(
      timeout(this.timeoutDuration),
      catchError(this.handleError)
    );
  }

  // Generic POST request with timeout and better error handling
  post(endpoint: string, data: any, options: any = {}): Observable<any> {
    // Don't set Content-Type for FormData - let browser set it automatically
    const isFormData = data instanceof FormData;
    const defaultOptions = {
      headers: isFormData ? {} : {
        'Content-Type': 'application/json'
      },
      ...options
    };

    return this.http.post(`${this.backendUrl}${endpoint}`, data, defaultOptions).pipe(
      timeout(this.timeoutDuration),
      catchError(this.handleError)
    );
  }

  // Generic PUT request with timeout
  put(endpoint: string, data: any): Observable<any> {
    return this.http.put(`${this.backendUrl}${endpoint}`, data, {
      headers: {
        'Content-Type': 'application/json'
      }
    }).pipe(
      timeout(this.timeoutDuration),
      catchError(this.handleError)
    );
  }

  // Generic DELETE request with timeout
  delete(endpoint: string): Observable<any> {
    return this.http.delete(`${this.backendUrl}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    }).pipe(
      timeout(this.timeoutDuration),
      catchError(this.handleError)
    );
  }

  // Error handling method
  private handleError(error: any): Observable<never> {
    let errorMessage = 'An unknown error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      if (error.status === 0) {
        errorMessage = 'Cannot connect to server. Please check if the backend is running.';
      } else if (error.status === 401) {
        errorMessage = 'Unauthorized. Please login again.';
      } else if (error.status === 403) {
        errorMessage = 'Forbidden. You do not have permission to access this resource.';
      } else if (error.status === 404) {
        errorMessage = 'Resource not found.';
      } else if (error.status >= 500) {
        errorMessage = 'Server error. Please try again later.';
      } else {
        errorMessage = `Server Error: ${error.status} - ${error.message}`;
      }
    }
    
    console.error('API Service Error:', errorMessage, error);
    return throwError(() => new Error(errorMessage));
  }
}
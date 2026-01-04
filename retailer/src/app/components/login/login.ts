import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router'; // Added RouterModule
import { ApiService } from '../../services/back-end-service';

@Component({
  standalone: true,
  selector: 'app-login',
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  showPassword: boolean = false;
  loginForm: FormGroup;
  errorMessage: string = '';
  loading: boolean = false;

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  get passwordControl() {
    return this.loginForm.get('password');
  }

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  onSubmit() {
    this.errorMessage = '';
    
    if (this.loginForm.valid) {
      this.loading = true;
      const loginData = {
        email: this.loginForm.value.email.toLowerCase().trim(),
        password: this.loginForm.value.password
      };
  
      // Updated to 'retailer/login' to match retailer routes in routes.py
      this.apiService.post('retailer/login', loginData).subscribe({
        next: (response) => {
          this.loading = false;
          Object.entries(response).forEach(([key, value]) => {
            localStorage.setItem(key, String(value));
          });
          this.router.navigate(['/dashboard']);
        },
        error: (error) => {
          this.loading = false;
          console.error('Login error:', error);
          this.handleLoginError(error);
        }
      });
    } else {
      this.errorMessage = 'Please fill out the form correctly.';
    }
  }

  private handleLoginError(error: any) {
    if (error.status === 404) {
      this.errorMessage = 'User not found';
    } else if (error.status === 401) {
      this.errorMessage = 'Invalid credentials';
    } else if (error.error?.error) {
      this.errorMessage = error.error.error;
    } else {
      this.errorMessage = 'Internal server error. Please try again later.';
    }
  }

  // FIXED: Now uses Router instead of EventEmitter
  onSignupClick() {
    console.log("Navigating to signup...");
    this.router.navigate(['/signup']);
  }

  onForgotPasswordClick() {
    console.log("Navigating to forgot-password...");
    this.router.navigate(['/forgot-password']);
  }
}
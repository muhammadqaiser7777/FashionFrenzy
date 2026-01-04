import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/back-end-service';

@Component({
  standalone: true,
  selector: 'app-login',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  showPassword: boolean = false;
  loginForm: FormGroup;
  errorMessage: string = '';
  loading: boolean = false;

  @Output() loginSuccess = new EventEmitter<void>();

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(6)]]
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
        username: this.loginForm.value.username.toLowerCase().trim(),
        password: this.loginForm.value.password
      };
  
      // Check hardcoded admin credentials first
      if (this.checkHardcodedCredentials(loginData.username, loginData.password)) {
        this.loading = false;
        // Simulate successful login with hardcoded data
        localStorage.setItem('auth_token', 'hardcoded_admin_token');
        localStorage.setItem('username', loginData.username);
        localStorage.setItem('status', 'Verified');
        localStorage.setItem('role', 'admin');
        this.router.navigate(['/dashboard']);
        return;
      }

      // If not hardcoded, try API call
      this.apiService.post('admin/login', loginData).subscribe({
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
    }
  }

  // Check hardcoded admin credentials
  private checkHardcodedCredentials(username: string, password: string): boolean {
    const hardcodedUsers: { [key: string]: string } = {
      'aqib': 'abcd1234',
      'adnan': 'abcd1234'
    };
    
    return hardcodedUsers[username.toLowerCase()] === password;
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

  onSignupClick() {
    // Admin accounts are created by system administrators
    alert('Admin accounts are created by system administrators. Please contact your administrator.');
  }

  onForgotPasswordClick() {
    // Admin password reset handled by system administrators
    alert('Password reset for admin accounts is handled by system administrators. Please contact your administrator.');
  }
}
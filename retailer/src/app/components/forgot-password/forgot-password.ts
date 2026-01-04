import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/back-end-service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.css'
})
export class ForgotPassword {
  email: string = '';
  errorMessage: string = '';
  successMessage: string = '';
  loading: boolean = false;

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  onSubmit() {
    this.errorMessage = '';
    this.successMessage = '';
    
    if (!this.email.trim()) {
      this.errorMessage = 'Email is required';
      return;
    }

    this.loading = true;

    this.apiService.post('retailer/password-forget', { email: this.email }).subscribe({
      next: (response) => {
        this.loading = false;
        this.successMessage = 'Password reset OTP sent to your email. Please check your inbox.';
        // In a real app, you might navigate to an OTP verification component
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 3000);
      },
      error: (error) => {
        this.loading = false;
        console.error('Forgot password error:', error);
        if (error.status === 404) {
          this.errorMessage = 'Email not found';
        } else if (error.error?.error) {
          this.errorMessage = error.error.error;
        } else {
          this.errorMessage = 'An error occurred. Please try again.';
        }
      }
    });
  }

  goBack() {
    this.router.navigate(['/login']);
  }
}
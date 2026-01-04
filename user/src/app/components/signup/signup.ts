import { Component, EventEmitter, Output, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/back-end-service';

@Component({
  standalone: true,
  selector: 'app-signup',
  imports: [CommonModule, FormsModule],
  templateUrl: './signup.html',
  styleUrl: './signup.css'
})
export class Signup implements OnDestroy {
  @Output() signupSuccess = new EventEmitter<void>();
  @Output() loginClicked = new EventEmitter<void>();

  fullName = '';
  email = '';
  gender: 'male' | 'female' | 'other' = 'male';
  password = '';
  confirmPassword = '';
  errorMessage = '';
  isLoading = false;

  showPassword = false;
  showConfirmPassword = false;

  // OTP
  showOtpPopup = false;
  otp = '';
  otpErrorMessage = '';
  isVerifyingOtp = false;
  otpTimer = 180;
  isOtpBlocked = true;
  private otpInterval: any = null;

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnDestroy() {
    if (this.otpInterval) clearInterval(this.otpInterval);
  }

  togglePassword(field: 'password' | 'confirmPassword') {
    field === 'password'
      ? (this.showPassword = !this.showPassword)
      : (this.showConfirmPassword = !this.showConfirmPassword);
  }

  get passwordsMatch(): boolean {
    return this.password === this.confirmPassword;
  }

  validateForm(): boolean {
    if (!this.fullName || !this.email || !this.password || !this.confirmPassword) {
      this.errorMessage = 'All fields are required';
      return false;
    }

    if (!this.passwordsMatch) {
      this.errorMessage = 'Passwords do not match';
      return false;
    }

    if (this.password.length < 8) {
      this.errorMessage = 'Password must be at least 8 characters';
      return false;
    }

    return true;
  }

  onSignup() {
    this.errorMessage = '';
    if (!this.validateForm()) return;

    this.isLoading = true;

    const payload = {
      full_name: this.fullName.trim(),
      email: this.email.trim().toLowerCase(),
      password: this.password,
      gender: this.gender
    };

    this.apiService.post('signup', payload).subscribe({
      next: (res: any) => {
        // Save session data
        localStorage.setItem('auth_token', res.auth_token);
        localStorage.setItem('email', res.email);
        localStorage.setItem('full_name', res.full_name);
        localStorage.setItem('profile_pic', res.profile_pic || '');
        localStorage.setItem('status', res.status);

        this.isLoading = false;
        this.showOtpPopup = true;
        this.startOtpTimer();
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err?.error?.error || 'Signup failed';
      }
    });
  }

  startOtpTimer() {
    this.isOtpBlocked = true;
    this.otpTimer = 180;

    if (this.otpInterval) clearInterval(this.otpInterval);

    this.otpInterval = setInterval(() => {
      this.otpTimer--;

      if (this.otpTimer <= 0) {
        this.isOtpBlocked = false;
        clearInterval(this.otpInterval);
      }
    }, 1000);
  }

  verifyOtp() {
    if (!this.otp || this.otp.length !== 6) {
      this.otpErrorMessage = 'Enter a valid 6-digit OTP';
      return;
    }

    this.isVerifyingOtp = true;
    this.otpErrorMessage = '';

    const payload = {
      email: localStorage.getItem('email'),
      auth_token: localStorage.getItem('auth_token'),
      otp: this.otp
    };

    this.apiService.post('verify', payload).subscribe({
      next: () => {
        localStorage.setItem('status', 'Verified');
        this.isVerifyingOtp = false;
        this.showOtpPopup = false;
        this.signupSuccess.emit();
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.isVerifyingOtp = false;
        this.otpErrorMessage = err?.error?.error || 'Invalid OTP';
      }
    });
  }

  regenerateOtp() {
    if (this.isOtpBlocked) return;

    this.apiService.post('otp-refresh', {
      email: localStorage.getItem('email')
    }).subscribe({
      next: () => {
        alert('New OTP sent to your email');
        this.startOtpTimer();
      },
      error: () => {
        alert('Failed to resend OTP');
      }
    });
  }

  validateOtpInput(event: KeyboardEvent) {
    if (!/[0-9]/.test(event.key) && event.key !== 'Backspace') {
      event.preventDefault();
    }
  }

  onLoginClick() {
    this.loginClicked.emit();
  }
}

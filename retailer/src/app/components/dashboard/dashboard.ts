import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/back-end-service';

interface DashboardStats {
  total_orders: number;
  pending_orders: number;
  confirmed_orders: number;
  rejected_orders: number;
  delivered_orders: number;
  total_revenue: number;
  total_products: number;
  low_stock_products: number;
  monthly_revenue: Array<{month: string, revenue: number}>;
  top_selling_products: Array<{
    id: number;
    title: string;
    category: string;
    quantity_sold: number;
    revenue: number;
    stock: number;
  }>;
  recent_orders: Array<{
    id: number;
    user_email: string;
    total_amount: number;
    delivery_status: string;
    created_at: string;
    items_count: number;
  }>;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {
  isLoading = true;
  stats: DashboardStats = {
    total_orders: 0,
    pending_orders: 0,
    confirmed_orders: 0,
    rejected_orders: 0,
    delivered_orders: 0,
    total_revenue: 0,
    total_products: 0,
    low_stock_products: 0,
    monthly_revenue: [],
    top_selling_products: [],
    recent_orders: []
  };

  activeTab = 'overview'; // overview, products, orders, analytics

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnInit() {
    this.checkAuth();
    this.loadDashboardStats();
  }

  checkAuth() {
    const authToken = localStorage.getItem('auth_token');
    const status = localStorage.getItem('status');
    
    if (!authToken || status !== 'Verified') {
      this.router.navigate(['/login']);
      return;
    }
  }

  loadDashboardStats() {
    const authToken = localStorage.getItem('auth_token');
    if (!authToken) return;

    this.apiService.post('retailer/dashboard/advanced-stats', { auth_token: authToken }).subscribe({
      next: (response) => {
        this.stats = response;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load dashboard stats:', err);
        this.isLoading = false;
      }
    });
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getStatusColor(status: string): string {
    const statusColors: { [key: string]: string } = {
      'pending': '#f59e0b',
      'confirmed': '#10b981',
      'delivered': '#3b82f6',
      'rejected': '#ef4444',
      'processing': '#8b5cf6'
    };
    return statusColors[status.toLowerCase()] || '#6b7280';
  }

  navigateToProducts() {
    this.router.navigate(['/products']);
  }

  navigateToOrders() {
    this.router.navigate(['/orders']);
  }

  refreshStats() {
    this.isLoading = true;
    this.loadDashboardStats();
  }

  getUserName(): string {
    return localStorage.getItem('full_name') || 'User';
  }

  getChartHeightPercentage(month: {month: string, revenue: number}): number {
    if (!this.stats.monthly_revenue || this.stats.monthly_revenue.length === 0) {
      return 0;
    }
    
    const maxRevenue = Math.max(...this.stats.monthly_revenue.map(m => m.revenue));
    if (maxRevenue === 0) {
      return 0;
    }
    
    return (month.revenue / maxRevenue) * 100;
  }

  logout() {
    const authToken = localStorage.getItem('auth_token');
    const email = localStorage.getItem('email');
    
    if (authToken && email) {
      this.apiService.post('retailer/logout', { 
        auth_token: authToken, 
        email: email 
      }).subscribe({
        next: () => {
          localStorage.clear();
          this.router.navigate(['/login']);
        },
        error: () => {
          localStorage.clear();
          this.router.navigate(['/login']);
        }
      });
    } else {
      localStorage.clear();
      this.router.navigate(['/login']);
    }
  }
}

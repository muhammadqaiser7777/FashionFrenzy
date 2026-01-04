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

interface Product {
  id?: number;
  category: string;
  title: string;
  description: string;
  price: number;
  discounted_price?: number;
  stock: number;
  images: Array<{image_url: string, is_primary: boolean}>;
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
  isLoadingProducts = false;
  products: Product[] = [];
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

  activeTab = 'overview'; // overview, products, orders

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
    
    // Load products when products tab is selected
    if (tab === 'products') {
      this.loadProducts();
    }
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount).replace('PKR', 'Rs');
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

  // Product Management
  private retryCount = 0;
  private maxRetries = 3;

  loadProducts() {
    const authToken = localStorage.getItem('auth_token');
    if (!authToken) {
      this.isLoadingProducts = false;
      return;
    }

    this.isLoadingProducts = true;
    
    // Add timeout and better error handling
    const timeoutId = setTimeout(() => {
      console.warn('Product loading timeout');
      this.isLoadingProducts = false;
      if (this.products.length === 0) {
        alert('Loading products is taking too long. Please try again.');
      }
    }, 10000); // 10 second timeout

    this.apiService.post('retailer/view-products', { auth_token: authToken }).subscribe({
      next: (response) => {
        clearTimeout(timeoutId);
        this.products = response.products || [];
        this.isLoadingProducts = false;
        this.retryCount = 0; // Reset retry count on success
        console.log('Products loaded successfully:', this.products.length);
      },
      error: (err) => {
        clearTimeout(timeoutId);
        console.error('Failed to load products:', err);
        this.isLoadingProducts = false;
        
        // Retry logic for network errors
        if ((err.status === 0 || err.status >= 500) && this.retryCount < this.maxRetries) {
          this.retryCount++;
          console.log(`Retrying... Attempt ${this.retryCount} of ${this.maxRetries}`);
          setTimeout(() => {
            this.loadProducts();
          }, 2000 * this.retryCount); // Exponential backoff
          return;
        }
        
        // Show user-friendly error message
        if (err.status === 0) {
          alert('Cannot connect to server. Please check if the backend is running.');
        } else if (err.status === 401) {
          alert('Session expired. Please login again.');
          this.router.navigate(['/login']);
        } else {
          alert('Failed to load products. Please try again.');
        }
      }
    });
  }

  getProductImageUrl(product: Product): string {
    if (!product.images || product.images.length === 0) {
      return '';
    }
    
    // Try to find primary image first
    const primaryImage = product.images.find((img: any) => img.is_primary);
    if (primaryImage && primaryImage.image_url) {
      // Fix image URL to include backend base URL
      const imageUrl = primaryImage.image_url;
      return imageUrl.startsWith('http') ? imageUrl : `http://localhost:5000${imageUrl}`;
    }
    
    // Fallback to first image
    const firstImage = product.images[0];
    if (firstImage && firstImage.image_url) {
      const imageUrl = firstImage.image_url;
      return imageUrl.startsWith('http') ? imageUrl : `http://localhost:5000${imageUrl}`;
    }
    
    return '';
  }

  getStockStatus(stock: number): string {
    if (stock === 0) return 'Out of Stock';
    if (stock < 10) return 'Low Stock';
    return 'In Stock';
  }

  getStockColor(stock: number): string {
    if (stock === 0) return '#ef4444';
    if (stock < 10) return '#f59e0b';
    return '#10b981';
  }

  handleImageError(event: Event) {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
    const parent = img.parentElement;
    if (parent) {
      const noImageDiv = parent.querySelector('.no-image') as HTMLElement;
      if (noImageDiv) {
        noImageDiv.style.display = 'flex';
      }
    }
  }

  openEditProduct(product: Product) {
    this.router.navigate(['/products'], { queryParams: { edit: product.id } });
  }

  async deleteProduct(product: Product) {
    if (!confirm(`Are you sure you want to delete "${product.title}"?`)) return;

    const authToken = localStorage.getItem('auth_token');
    if (!authToken || !product.id) return;

    this.apiService.post('retailer/delete-product', {
      auth_token: authToken,
      product_id: product.id
    }).subscribe({
      next: (response) => {
        alert('Product deleted successfully!');
        this.loadProducts(); // Refresh products list
      },
      error: (err) => {
        console.error('Delete failed:', err);
        alert('Failed to delete product. Please try again.');
      }
    });
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

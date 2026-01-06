import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/back-end-service';

interface Product {
  id?: number;
  category: string;
  title: string;
  description: string;
  price: number;
  discounted_price?: number;
  stock: number;
  images: Array<{image_url: string, is_primary: boolean}>;
  retailer_name?: string;
  status?: string;
  admin_comment?: string;
  actionLoading?: boolean;
}

interface AdminStats {
  pending_products: number;
  approved_products: number;
  rejected_products: number;
  total_retailers: number;
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
  activeTab = 'overview';
  
  pendingProducts: Product[] = [];
  approvedProducts: Product[] = [];
  rejectedProducts: Product[] = [];
  filteredProducts: Product[] = [];
  
  selectedCategory = '';
  
  // Categories for filtering
  categories = [
    "Men Clothing",
    "Women Clothing",
    "Men Wallet",
    "Women Purse",
    "Men Shoes",
    "Women Shoes"
  ];
  
  stats: AdminStats = {
    pending_products: 0,
    approved_products: 0,
    rejected_products: 0,
    total_retailers: 0
  };

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnInit() {
    this.checkAuth();
    this.loadDashboardData();
  }

  checkAuth() {
    const authToken = localStorage.getItem('auth_token');
    const status = localStorage.getItem('status');
    
    if (!authToken || status !== 'Verified') {
      this.router.navigate(['/login']);
      return;
    }
  }

  getUserName(): string {
    return localStorage.getItem('username') || 'Admin';
  }

  logout() {
    if (confirm('Are you sure you want to logout?')) {
      localStorage.clear();
      this.router.navigate(['/login']);
    }
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;
    this.loadTabData(tab);
  }

  loadDashboardData() {
    this.loadStats();
    this.loadPendingProducts();
  }

  loadTabData(tab: string) {
    switch (tab) {
      case 'pending':
        if (this.pendingProducts.length === 0) {
          this.loadPendingProducts();
        } else {
          this.filterProducts();
        }
        break;
      case 'approved':
        if (this.approvedProducts.length === 0) {
          this.loadApprovedProducts();
        }
        break;
      case 'rejected':
        if (this.rejectedProducts.length === 0) {
          this.loadRejectedProducts();
        }
        break;
      case 'overview':
        this.loadStats();
        break;
    }
  }

  loadStats() {
    this.stats.pending_products = this.pendingProducts.length;
    this.stats.approved_products = this.approvedProducts.length;
    this.stats.rejected_products = this.rejectedProducts.length;
    this.stats.total_retailers = 0; // Will be updated from API
  }

  async loadPendingProducts() {
    this.isLoading = true;
    
    try {
      const authToken = localStorage.getItem('auth_token');
      if (!authToken) {
        throw new Error('No auth token found');
      }

      const response = await this.apiService.post('admin/view-pending-products', {
        auth_token: authToken
      }).toPromise();
      
      console.log('Pending products response:', response);
      
      const products = response?.products || [];
      this.pendingProducts = products.map((p: any) => ({
        id: p.id,
        category: p.category,
        title: p.title,
        description: p.description,
        price: p.price,
        discounted_price: p.discounted_price,
        stock: p.stock,
        images: p.images || [],
        retailer_name: p.retailer?.full_name || p.retailer_name || 'Unknown',
        status: p.status
      }));
      
      this.filterProducts();
      this.stats.pending_products = this.pendingProducts.length;
    } catch (error: any) {
      console.error('Failed to load pending products:', error);
      
      if (error.status === 404) {
        this.pendingProducts = [];
        this.showInfoMessage('Product approval feature will be available once backend endpoints are implemented.');
      } else if (error.status === 0) {
        this.showInfoMessage('Cannot connect to server. Please check if the backend is running.');
      } else if (error.status === 401) {
        alert('Session expired. Please login again.');
        this.router.navigate(['/login']);
      } else if (error.status === 500) {
        console.error('Server error details:', error.error);
        this.showInfoMessage('Server error loading products. Please check backend logs.');
      } else {
        this.showInfoMessage(`Failed to load pending products: ${error.message || 'Please try again.'}`);
      }
      
      this.pendingProducts = [];
    } finally {
      this.isLoading = false;
    }
  }

  async loadApprovedProducts() {
    this.isLoading = true;
    
    try {
      const authToken = localStorage.getItem('auth_token');
      if (!authToken) {
        throw new Error('No auth token found');
      }

      const response = await this.apiService.post('admin/view-approved-products', {
        auth_token: authToken
      }).toPromise();
      
      console.log('Approved products response:', response);
      
      const products = response?.products || [];
      this.approvedProducts = products.map((p: any) => ({
        id: p.id,
        category: p.category,
        title: p.title,
        description: p.description,
        price: p.price,
        discounted_price: p.discounted_price,
        stock: p.stock,
        images: p.images || [],
        retailer_name: p.retailer?.full_name || p.retailer_name || 'Unknown',
        status: p.status
      }));
      
      this.stats.approved_products = this.approvedProducts.length;
    } catch (error: any) {
      console.error('Failed to load approved products:', error);
      this.approvedProducts = [];
    } finally {
      this.isLoading = false;
    }
  }

  async loadRejectedProducts() {
    this.isLoading = true;
    
    try {
      const authToken = localStorage.getItem('auth_token');
      if (!authToken) {
        throw new Error('No auth token found');
      }

      const response = await this.apiService.post('admin/view-rejected-products', {
        auth_token: authToken
      }).toPromise();
      
      console.log('Rejected products response:', response);
      
      const products = response?.products || [];
      this.rejectedProducts = products.map((p: any) => ({
        id: p.id,
        category: p.category,
        title: p.title,
        description: p.description,
        price: p.price,
        discounted_price: p.discounted_price,
        stock: p.stock,
        images: p.images || [],
        retailer_name: p.retailer?.full_name || p.retailer_name || 'Unknown',
        status: p.status,
        admin_comment: p.admin_comment
      }));
      
      this.stats.rejected_products = this.rejectedProducts.length;
    } catch (error: any) {
      console.error('Failed to load rejected products:', error);
      this.rejectedProducts = [];
    } finally {
      this.isLoading = false;
    }
  }

  filterProducts() {
    if (this.selectedCategory) {
      this.filteredProducts = this.pendingProducts.filter(p => p.category === this.selectedCategory);
    } else {
      this.filteredProducts = this.pendingProducts;
    }
  }

  private showInfoMessage(message: string) {
    const infoDiv = document.createElement('div');
    infoDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #3b82f6;
      color: white;
      padding: 1rem;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 1000;
      max-width: 400px;
      font-size: 0.875rem;
    `;
    infoDiv.textContent = message;
    
    document.body.appendChild(infoDiv);
    
    setTimeout(() => {
      if (document.body.contains(infoDiv)) {
        document.body.removeChild(infoDiv);
      }
    }, 5000);
  }

  async approveProduct(product: Product) {
    if (!confirm(`Are you sure you want to approve "${product.title}"?`)) return;

    product.actionLoading = true;
    
    try {
      const authToken = localStorage.getItem('auth_token');
      if (!authToken || !product.id) {
        throw new Error('Missing auth token or product ID');
      }

      const response = await this.apiService.post('admin/edit-product-status', {
        auth_token: authToken,
        product_id: product.id,
        status: 'approved',
        admin_comment: ''
      }).toPromise();
      
      console.log('Approve response:', response);
      
      if (response?.success) {
        // Remove from pending and add to approved
        this.pendingProducts = this.pendingProducts.filter(p => p.id !== product.id);
        this.approvedProducts.push({ ...product, status: 'approved' });
        this.filterProducts();
        this.stats.pending_products--;
        this.stats.approved_products++;
        
        alert(`Product "${product.title}" has been approved successfully!`);
      } else {
        throw new Error(response?.message || 'Approval failed');
      }
    } catch (error: any) {
      console.error('Failed to approve product:', error);
      
      if (error.status === 404) {
        this.showInfoMessage('Product approval feature will be available once the backend endpoint is implemented.');
      } else if (error.status === 0) {
        alert('Cannot connect to server. Please check if the backend is running.');
      } else if (error.status === 401) {
        alert('Session expired. Please login again.');
        this.router.navigate(['/login']);
      } else {
        alert(`Failed to approve product: ${error.message || 'Please try again.'}`);
      }
    } finally {
      product.actionLoading = false;
    }
  }

  async rejectProduct(product: Product) {
    const reason = prompt('Please provide a reason for rejection (optional):');
    
    if (!confirm(`Are you sure you want to reject "${product.title}"?`)) return;

    product.actionLoading = true;
    
    try {
      const authToken = localStorage.getItem('auth_token');
      if (!authToken || !product.id) {
        throw new Error('Missing auth token or product ID');
      }

      const response = await this.apiService.post('admin/edit-product-status', {
        auth_token: authToken,
        product_id: product.id,
        status: 'rejected',
        admin_comment: reason || ''
      }).toPromise();
      
      console.log('Reject response:', response);
      
      if (response?.success) {
        // Remove from pending and add to rejected
        this.pendingProducts = this.pendingProducts.filter(p => p.id !== product.id);
        this.rejectedProducts.push({ ...product, status: 'rejected', admin_comment: reason || '' });
        this.filterProducts();
        this.stats.pending_products--;
        this.stats.rejected_products++;
        
        alert(`Product "${product.title}" has been rejected.${reason ? ' Reason: ' + reason : ''}`);
      } else {
        throw new Error(response?.message || 'Rejection failed');
      }
    } catch (error: any) {
      console.error('Failed to reject product:', error);
      
      if (error.status === 404) {
        this.showInfoMessage('Product rejection feature will be available once the backend endpoint is implemented.');
      } else if (error.status === 0) {
        alert('Cannot connect to server. Please check if the backend is running.');
      } else if (error.status === 401) {
        alert('Session expired. Please login again.');
        this.router.navigate(['/login']);
      } else {
        alert(`Failed to reject product: ${error.message || 'Please try again.'}`);
      }
    } finally {
      product.actionLoading = false;
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

  getProductImageUrl(product: Product): string {
    if (!product.images || product.images.length === 0) {
      return '';
    }
    
    const primaryImage = product.images.find(img => img.is_primary);
    if (primaryImage && primaryImage.image_url) {
      const imageUrl = primaryImage.image_url;
      return imageUrl.startsWith('http') ? imageUrl : `http://localhost:5000${imageUrl}`;
    }
    
    const firstImage = product.images[0];
    if (firstImage && firstImage.image_url) {
      const imageUrl = firstImage.image_url;
      return imageUrl.startsWith('http') ? imageUrl : `http://localhost:5000${imageUrl}`;
    }
    
    return '';
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
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../services/back-end-service';

interface OrderItem {
  id: number;
  product_id: number;
  quantity: number;
  subtotal: number;
  product_title: string;
  product_image?: string;
}

interface Order {
  id: number;
  user_email: string;
  total_amount: number;
  delivery_status: string;
  created_at: string;
  items: OrderItem[];
  items_count?: number;
}

@Component({
  selector: 'app-orders',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './orders.html',
  styleUrl: './orders.css'
})
export class Orders implements OnInit {
  orders: Order[] = [];
  isLoading = true;
  selectedOrder: Order | null = null;
  showOrderModal = false;
  showRejectModal = false;
  rejectReason = '';
  
  // Filters
  statusFilter = '';
  dateFilter = '';
  searchTerm = '';
  sortBy = 'created_at';
  sortOrder = 'desc';
  
  // Status options
  statusOptions = [
    { value: '', label: 'All Orders' },
    { value: 'pending', label: 'Pending' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'processing', label: 'Processing' },
    { value: 'shipped', label: 'Shipped' },
    { value: 'delivered', label: 'Delivered' },
    { value: 'rejected', label: 'Rejected' },
    { value: 'returned', label: 'Returned' }
  ];

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnInit() {
    this.checkAuth();
    this.loadOrders();
  }

  checkAuth() {
    const authToken = localStorage.getItem('auth_token');
    const status = localStorage.getItem('status');
    
    if (!authToken || status !== 'Verified') {
      this.router.navigate(['/login']);
      return;
    }
  }

  loadOrders() {
    const authToken = localStorage.getItem('auth_token');
    if (!authToken) return;

    this.apiService.post('retailer/view-orders', { auth_token: authToken }).subscribe({
      next: (response) => {
        this.orders = response.orders || [];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load orders:', err);
        this.isLoading = false;
      }
    });
  }

  // Order Management
  async confirmOrder(order: Order) {
    if (!confirm(`Are you sure you want to confirm order #${order.id}?`)) return;

    const authToken = localStorage.getItem('auth_token');
    if (!authToken) return;

    this.apiService.post('retailer/confirm-order', {
      auth_token: authToken,
      order_id: order.id
    }).subscribe({
      next: (response) => {
        alert(`Order #${order.id} confirmed successfully!`);
        this.loadOrders();
      },
      error: (err) => {
        console.error('Confirm order failed:', err);
        alert('Failed to confirm order. Please try again.');
      }
    });
  }

  openRejectModal(order: Order) {
    this.selectedOrder = order;
    this.showRejectModal = true;
    this.rejectReason = '';
  }

  async rejectOrder() {
    if (!this.selectedOrder || !this.rejectReason.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }

    const authToken = localStorage.getItem('auth_token');
    if (!authToken) return;

    this.apiService.post('retailer/reject-order', {
      auth_token: authToken,
      order_id: this.selectedOrder.id,
      rejection_reason: this.rejectReason
    }).subscribe({
      next: (response) => {
        alert(`Order #${this.selectedOrder!.id} rejected successfully!`);
        this.closeRejectModal();
        this.loadOrders();
      },
      error: (err) => {
        console.error('Reject order failed:', err);
        alert('Failed to reject order. Please try again.');
      }
    });
  }

  closeRejectModal() {
    this.showRejectModal = false;
    this.selectedOrder = null;
    this.rejectReason = '';
  }

  // Order Details
  showOrderDetails(order: Order) {
    this.selectedOrder = order;
    this.showOrderModal = true;
  }

  closeOrderModal() {
    this.showOrderModal = false;
    this.selectedOrder = null;
  }

  // Filtering and Sorting
  get filteredOrders(): Order[] {
    let filtered = this.orders;

    // Search filter
    if (this.searchTerm) {
      const searchLower = this.searchTerm.toLowerCase();
      filtered = filtered.filter(order => 
        order.id.toString().includes(searchLower) ||
        order.user_email.toLowerCase().includes(searchLower) ||
        order.delivery_status.toLowerCase().includes(searchLower)
      );
    }

    // Status filter
    if (this.statusFilter) {
      filtered = filtered.filter(order => order.delivery_status === this.statusFilter);
    }

    // Date filter
    if (this.dateFilter) {
      const filterDate = new Date(this.dateFilter);
      filtered = filtered.filter(order => {
        const orderDate = new Date(order.created_at);
        return orderDate.toDateString() === filterDate.toDateString();
      });
    }

    // Sorting
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (this.sortBy) {
        case 'id':
          aValue = a.id;
          bValue = b.id;
          break;
        case 'user_email':
          aValue = a.user_email;
          bValue = b.user_email;
          break;
        case 'total_amount':
          aValue = a.total_amount;
          bValue = b.total_amount;
          break;
        case 'delivery_status':
          aValue = a.delivery_status;
          bValue = b.delivery_status;
          break;
        case 'created_at':
        default:
          aValue = new Date(a.created_at);
          bValue = new Date(b.created_at);
          break;
      }

      if (this.sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }

  // Utility Functions
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
      'processing': '#8b5cf6',
      'shipped': '#3b82f6',
      'delivered': '#059669',
      'rejected': '#ef4444',
      'returned': '#dc2626'
    };
    return statusColors[status.toLowerCase()] || '#6b7280';
  }

  getStatusBadgeClass(status: string): string {
    const statusClasses: { [key: string]: string } = {
      'pending': 'badge-pending',
      'confirmed': 'badge-confirmed',
      'processing': 'badge-processing',
      'shipped': 'badge-shipped',
      'delivered': 'badge-delivered',
      'rejected': 'badge-rejected',
      'returned': 'badge-returned'
    };
    return statusClasses[status.toLowerCase()] || 'badge-default';
  }

  canConfirmOrder(order: Order): boolean {
    return order.delivery_status.toLowerCase() === 'pending';
  }

  canRejectOrder(order: Order): boolean {
    return order.delivery_status.toLowerCase() === 'pending';
  }

  navigateBack() {
    this.router.navigate(['/dashboard']);
  }
}
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
}

interface ProductImage {
  file?: File;
  preview?: string;
  url?: string;
  is_primary: boolean;
}

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './products.html',
  styleUrl: './products.css'
})
export class Products implements OnInit {
  products: Product[] = [];
  isLoading = true;
  showAddForm = false;
  showEditForm = false;
  editingProduct: Product | null = null;
  
  // Form data
  formData: Product = {
    category: '',
    title: '',
    description: '',
    price: 0,
    discounted_price: undefined,
    stock: 0,
    images: []
  };
  
  // Image upload
  selectedImages: ProductImage[] = [];
  imageUploadInProgress = false;
  
  // Filters
  searchTerm = '';
  selectedCategory = '';
  sortBy = 'created_at';
  sortOrder = 'desc';
  
  // Categories
  categories = [
    'Clothing',
    'Electronics', 
    'Home & Garden',
    'Sports & Outdoors',
    'Beauty & Health',
    'Books & Media',
    'Toys & Games',
    'Automotive',
    'Other'
  ];

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnInit() {
    this.checkAuth();
    this.loadProducts();
  }

  checkAuth() {
    const authToken = localStorage.getItem('auth_token');
    const status = localStorage.getItem('status');
    
    if (!authToken || status !== 'Verified') {
      this.router.navigate(['/login']);
      return;
    }
  }

  loadProducts() {
    const authToken = localStorage.getItem('auth_token');
    if (!authToken) return;

    this.apiService.post('retailer/view-products', { auth_token: authToken }).subscribe({
      next: (response) => {
        this.products = response.products || [];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load products:', err);
        this.isLoading = false;
      }
    });
  }

  // Product Management
  openAddForm() {
    this.showAddForm = true;
    this.resetForm();
  }

  openEditForm(product: Product) {
    this.showEditForm = true;
    this.editingProduct = product;
    this.formData = { ...product };
    this.selectedImages = product.images.map(img => ({
      url: img.image_url,
      is_primary: img.is_primary
    }));
  }

  closeForms() {
    this.showAddForm = false;
    this.showEditForm = false;
    this.editingProduct = null;
    this.resetForm();
    this.selectedImages = [];
  }

  resetForm() {
    this.formData = {
      category: '',
      title: '',
      description: '',
      price: 0,
      discounted_price: undefined,
      stock: 0,
      images: []
    };
  }

  // Image Management
  onImageSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    Array.from(input.files).forEach(file => {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        alert('File size must be less than 5MB');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        this.selectedImages.push({
          file: file,
          preview: e.target?.result as string,
          is_primary: this.selectedImages.length === 0
        });
      };
      reader.readAsDataURL(file);
    });
  }

  removeImage(index: number) {
    this.selectedImages.splice(index, 1);
    if (this.selectedImages.length > 0 && !this.selectedImages.some(img => img.is_primary)) {
      this.selectedImages[0].is_primary = true;
    }
  }

  setPrimaryImage(index: number) {
    this.selectedImages.forEach((img, i) => {
      img.is_primary = i === index;
    });
  }

  async uploadImages(): Promise<string[]> {
    const authToken = localStorage.getItem('auth_token');
    if (!authToken || this.selectedImages.length === 0) return [];

    const uploadedUrls: string[] = [];
    
    for (const imageData of this.selectedImages) {
      if (imageData.url) {
        // Image already has URL (from edit)
        uploadedUrls.push(imageData.url);
        continue;
      }

      if (!imageData.file) continue;

      this.imageUploadInProgress = true;
      
      try {
        const formData = new FormData();
        formData.append('image', imageData.file);
        formData.append('auth_token', authToken);

        const response = await this.apiService.post('retailer/upload-image', formData).toPromise();
        if (response && response.image_url) {
          uploadedUrls.push(response.image_url);
        }
      } catch (error) {
        console.error('Image upload failed:', error);
        alert('Failed to upload image. Please try again.');
      }
    }

    this.imageUploadInProgress = false;
    return uploadedUrls;
  }

  // Form Submission
  async submitForm() {
    if (!this.validateForm()) return;

    const authToken = localStorage.getItem('auth_token');
    if (!authToken) return;

    try {
      // Upload images first
      const imageUrls = await this.uploadImages();
      
      // Prepare product data
      const productData = {
        ...this.formData,
        images: imageUrls.map((url, index) => ({
          image_url: url,
          is_primary: this.selectedImages[index]?.is_primary || false
        }))
      };

      let response;
      if (this.editingProduct) {
        // Update existing product
        response = await this.apiService.post('retailer/edit-product', {
          auth_token: authToken,
          product_id: this.editingProduct.id,
          ...productData
        }).toPromise();
      } else {
        // Add new product
        response = await this.apiService.post('retailer/add-product', {
          auth_token: authToken,
          ...productData
        }).toPromise();
      }

      if (response) {
        alert(this.editingProduct ? 'Product updated successfully!' : 'Product added successfully!');
        this.closeForms();
        this.loadProducts();
      }
    } catch (error) {
      console.error('Form submission failed:', error);
      alert('Failed to save product. Please try again.');
    }
  }

  validateForm(): boolean {
    if (!this.formData.category || !this.formData.title || !this.formData.price || this.formData.stock < 0) {
      alert('Please fill in all required fields');
      return false;
    }

    if (this.formData.price <= 0) {
      alert('Price must be greater than 0');
      return false;
    }

    if (this.selectedImages.length === 0) {
      alert('Please add at least one product image');
      return false;
    }

    return true;
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
        this.loadProducts();
      },
      error: (err) => {
        console.error('Delete failed:', err);
        alert('Failed to delete product. Please try again.');
      }
    });
  }

  // Filtering and Sorting
  get filteredProducts(): Product[] {
    let filtered = this.products;

    // Search filter
    if (this.searchTerm) {
      const searchLower = this.searchTerm.toLowerCase();
      filtered = filtered.filter(product => 
        product.title.toLowerCase().includes(searchLower) ||
        product.description.toLowerCase().includes(searchLower) ||
        product.category.toLowerCase().includes(searchLower)
      );
    }

    // Category filter
    if (this.selectedCategory) {
      filtered = filtered.filter(product => product.category === this.selectedCategory);
    }

    // Sorting
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (this.sortBy) {
        case 'title':
          aValue = a.title;
          bValue = b.title;
          break;
        case 'price':
          aValue = a.price;
          bValue = b.price;
          break;
        case 'stock':
          aValue = a.stock;
          bValue = b.stock;
          break;
        case 'created_at':
        default:
          aValue = a.id || 0;
          bValue = b.id || 0;
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

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
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

  getProductImageUrl(product: Product): string {
    if (!product.images || product.images.length === 0) {
      return '';
    }
    
    // Try to find primary image first
    const primaryImage = product.images.find(img => img.is_primary);
    if (primaryImage && primaryImage.image_url) {
      return primaryImage.image_url;
    }
    
    // Fallback to first image
    const firstImage = product.images[0];
    return firstImage ? firstImage.image_url : '';
  }

  navigateBack() {
    this.router.navigate(['/dashboard']);
  }
}
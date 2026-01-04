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
    'Men\'s Clothing',
    'Women\'s Clothing',
    'Men\'s Wallets',
    'Women\'s Purses',
    'Men\'s Shoes',
    'Women\'s Shoes'
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
    if (!authToken) {
      this.isLoading = false;
      return;
    }

    this.isLoading = true;
    
    // Add timeout and better error handling
    const timeoutId = setTimeout(() => {
      console.warn('Product loading timeout');
      this.isLoading = false;
      if (this.products.length === 0) {
        alert('Loading products is taking too long. Please try again.');
      }
    }, 10000); // 10 second timeout

    this.apiService.post('retailer/view-products', { auth_token: authToken }).subscribe({
      next: (response) => {
        clearTimeout(timeoutId);
        this.products = response.products || [];
        this.isLoading = false;
        console.log('Products loaded successfully:', this.products.length);
      },
      error: (err) => {
        clearTimeout(timeoutId);
        console.error('Failed to load products:', err);
        this.isLoading = false;
        
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

      // Check file type - allow JPG, JPEG, PNG
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
      if (!validTypes.includes(file.type)) {
        alert('Only JPG, JPEG, and PNG files are allowed');
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
      reader.onerror = () => {
        alert('Failed to read file. Please try a different image.');
      };
      reader.readAsDataURL(file);
    });
  }

  // Check backend connectivity
  async checkBackendConnection(): Promise<boolean> {
    try {
      const authToken = localStorage.getItem('auth_token');
      if (!authToken) return false;
      
      // Simple test endpoint
      const response = await this.apiService.post('retailer/dashboard/advanced-stats', { auth_token: authToken }).toPromise();
      return !!response;
    } catch (error) {
      console.error('Backend connectivity check failed:', error);
      return false;
    }
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
    
    for (let i = 0; i < this.selectedImages.length; i++) {
      const imageData = this.selectedImages[i];
      
      if (imageData.url) {
        // Image already has URL (from edit)
        uploadedUrls.push(imageData.url);
        continue;
      }

      if (!imageData.file) continue;

      this.imageUploadInProgress = true;
      
      try {
        console.log(`Uploading image ${i + 1}/${this.selectedImages.length}:`, imageData.file.name);
        
        const formData = new FormData();
        formData.append('image', imageData.file);
        formData.append('auth_token', authToken);

        console.log('Making upload request to: retailer/upload-image');
        const response: any = await this.apiService.post('retailer/upload-image', formData).toPromise();
        
        console.log('Upload response:', response);
        
        if (response && response.image_url) {
          uploadedUrls.push(response.image_url);
          console.log(`Image ${i + 1} uploaded successfully:`, response.image_url);
        } else {
          console.error(`Upload response missing image_url:`, response);
          throw new Error('Upload response missing image URL');
        }
      } catch (error: any) {
        console.error(`Image upload failed for image ${i + 1}:`, error);
        
        // More specific error messages
        if (error.status === 0) {
          alert(`Cannot connect to server for image upload. Please check if the backend is running.`);
        } else if (error.status === 401) {
          alert(`Authentication failed. Please login again.`);
        } else if (error.status === 413) {
          alert(`Image file is too large. Please choose a smaller file (max 5MB).`);
        } else if (error.status === 415) {
          alert(`Unsupported file format. Please use JPG, JPEG, or PNG files.`);
        } else {
          alert(`Failed to upload image "${imageData.file.name}". Please try again. Error: ${error.message || 'Unknown error'}`);
        }
        
        // Continue with next image instead of stopping completely
        continue;
      }
    }

    this.imageUploadInProgress = false;
    console.log('Upload completed. Uploaded URLs:', uploadedUrls);
    return uploadedUrls;
  }

  // Form Submission
  async submitForm() {
    if (!this.validateForm()) return;

    const authToken = localStorage.getItem('auth_token');
    if (!authToken) return;

    // Show loading state
    const submitButton = document.querySelector('.submit-btn') as HTMLButtonElement;
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = 'Saving...';
    }

    try {
      // Check backend connectivity first
      console.log('Checking backend connectivity...');
      const isConnected = await this.checkBackendConnection();
      
      if (!isConnected) {
        alert('Cannot connect to the backend server. Please ensure the server is running on localhost:5000');
        return;
      }

      // Upload images first
      console.log('Starting image upload...');
      const imageUrls = await this.uploadImages();
      
      if (imageUrls.length === 0 && this.selectedImages.length > 0) {
        alert('Failed to upload images. Please check the console for details and try again.');
        return;
      }
      
      // Prepare product data
      const productData = {
        ...this.formData,
        images: imageUrls.map((url, index) => ({
          image_url: url,
          is_primary: this.selectedImages[index]?.is_primary || false
        }))
      };

      console.log('Submitting product data:', productData);

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

      console.log('Product submission response:', response);

      if (response) {
        // Show success message
        alert(this.editingProduct ? 'Product updated successfully!' : 'Product added successfully!');
        
        // Close form and reload products
        this.closeForms();
        this.loadProducts();
      }
    } catch (error: any) {
      console.error('Form submission failed:', error);
      
      if (error.status === 0) {
        alert('Cannot connect to server. Please check if the backend is running on localhost:5000');
      } else if (error.status === 401) {
        alert('Session expired. Please login again.');
        this.router.navigate(['/login']);
      } else {
        alert(`Failed to save product: ${error.message || 'Unknown error'}. Please check the console for details.`);
      }
    } finally {
      // Reset button state
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = this.editingProduct ? 'Update Product' : 'Add Product';
      }
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
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount).replace('PKR', 'Rs');
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

  navigateBack() {
    this.router.navigate(['/dashboard']);
  }
}
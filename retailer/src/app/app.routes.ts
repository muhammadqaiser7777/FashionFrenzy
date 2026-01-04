// app-routing.module.ts
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Login } from './components/login/login';
import { Signup } from './components/signup/signup';
import { ChangePassword } from './components/change-password/change-password';
import { ForgotPassword } from './components/forgot-password/forgot-password';
import { Dashboard } from './components/dashboard/dashboard';
import { Products } from './components/products/products';
import { Orders } from './components/orders/orders';

export const routes: Routes = [
  { path: '', component: Login },
  { path: 'login', component: Login },
  { path: 'signup', component: Signup },
  { path: 'forgot-password', component: ForgotPassword },
  { path: 'change-password', component: ChangePassword },
  { path: 'dashboard', component: Dashboard },
  { path: 'products', component: Products },
  { path: 'orders', component: Orders },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, {
      scrollPositionRestoration: 'enabled', // 👈 scrolls to top automatically
      anchorScrolling: 'enabled'           // optional: allows #anchor navigation
    })
  ],
  exports: [RouterModule] // 👈 needed so routing works
})
export class AppRoutingModule {}
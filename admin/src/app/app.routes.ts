// app-routing.module.ts
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Login } from './components/login/login';
import { Dashboard } from './components/dashboard/dashboard';

export const routes: Routes = [
  { path: '', component: Login },
  { path: 'login', component: Login },
  { path: 'dashboard', component: Dashboard },
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
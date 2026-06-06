import { Routes } from '@angular/router';
import { RegistrazioneComponent } from './registrazione/registrazione.component';
import { LoginComponent } from './login/login.component';
import { FirstpageComponent } from './firstpage/firstpage.component';
import { HomeComponent } from './home/home.component';

export const routes: Routes = [
    { path: '',loadComponent: () => import('./firstpage/firstpage.component').then(m => m.FirstpageComponent),pathMatch:'full'},
    { path: 'registrazione',loadComponent: () => import('./registrazione/registrazione.component').then(m => m.RegistrazioneComponent)},
    {path:'login',loadComponent: () => import('./login/login.component').then(m => m.LoginComponent)},
    {path:'home',loadComponent: () => import('./home/home.component').then(m => m.HomeComponent)}
];

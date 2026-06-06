import { Routes } from '@angular/router';
import { RegistrazioneComponent } from './registrazione/registrazione.component';
import { LoginComponent } from './login/login.component';
import { FirstpageComponent } from './firstpage/firstpage.component';
import { HomesComponent } from './homes/homes.component';
import { HomedComponent } from './homed/homed.component';

export const routes: Routes = [
    { path: '',loadComponent: () => import('./firstpage/firstpage.component').then(m => m.FirstpageComponent),pathMatch:'full'},
    { path: 'registrazione',loadComponent: () => import('./registrazione/registrazione.component').then(m => m.RegistrazioneComponent)},
    {path:'login',loadComponent: () => import('./login/login.component').then(m => m.LoginComponent)},
    {path:'homes',loadComponent: () => import('./homes/homes.component').then(m => m.HomesComponent)},
    {path:'homed',loadComponent: () => import('./homed/homed.component').then(m => m.HomedComponent)}
];

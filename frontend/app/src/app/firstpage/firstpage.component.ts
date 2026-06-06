import { Component } from '@angular/core';
import { Router } from '@angular/router';
@Component({
  selector: 'app-firstpage',
  imports: [],
  templateUrl: './firstpage.component.html',
  styleUrl: './firstpage.component.css'
})
export class FirstpageComponent {

  constructor(public Route: Router){}
   // Metodo invocato al click sul pulsante di login
  Login() {
    this.Route.navigate(['/login']); // Naviga alla pagina di login
  }

  // Metodo invocato al click sul pulsante di registrazione
  Regis() {
    this.Route.navigate(['/registrazione']); // Naviga alla pagina di registrazione

  }




ngAfterViewInit() {
    // Aggiunge un listener per pulire il token JWT quando si chiude o aggiorna la pagina
    window.addEventListener('beforeunload', () => {
      localStorage.removeItem('jwt'); // Rimuove il token prima di abbandonare la pagina
    });
  }
}
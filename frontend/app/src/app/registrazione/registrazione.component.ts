import { Component } from '@angular/core';
import { CommonModule, NgIf } from '@angular/common';
import { FormsModule,NgForm, NgModel } from '@angular/forms';
import { UserService } from '../user.service';
import { Router } from '@angular/router';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-registrazione',
  imports: [NgIf,FormsModule,RouterLink,CommonModule],
  templateUrl: './registrazione.component.html',
  styleUrl: './registrazione.component.css'
})
export class RegistrazioneComponent {
// Dati del form
  email: string = '';
  nome: string = '';
  cognome: string = '';
  password: string = '';
  confermaPassword: string = '';
  ruolo: string = ' ';
  data_nascita: Date = new Date();

  // Stato
  errore: string = '';
  successo: string = '';
  caricamento: boolean = false;

  constructor(private userService: UserService, private router: Router) {}

  regi() {
    // Validazione base
    if (!this.email || !this.nome || !this.cognome || !this.password) {
      this.errore = 'Compila tutti i campi obbligatori.';
      return;
    }

    if (this.password !== this.confermaPassword) {
      this.errore = 'Le password non coincidono.';
      return;
    }

    this.errore = '';
    this.caricamento = true;
    console.log(this.ruolo)

    this.userService.REGIST(
      this.email,
      this.nome,
      this.cognome,
      this.password,
      this.ruolo,
      this.data_nascita
    ).subscribe({
      next: (res) => {
        this.caricamento = false;
        this.successo = res.message || 'Registrazione avvenuta con successo!';
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (err) => {
        this.caricamento = false;
        this.errore = err.error?.message || 'Errore durante la registrazione.';
      }
    });
  }
}
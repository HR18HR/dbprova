import { Component,AfterViewChecked,DoCheck} from '@angular/core';
import { Data, Router, RouterLink, RouterOutlet} from '@angular/router';
import {FormsModule} from '@angular/forms'
import { UserService,Token} from '../user.service';
import { NgIf } from '@angular/common';
import { jwtDecode } from 'jwt-decode';

//Interface Token--> email,username,role
@Component({
  selector: 'app-login',
  imports: [FormsModule,NgIf],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  
  guard: boolean = false; // Variabile booleana non usata in questo codice, probabilmente serviva per controllare l’accesso
  username: string = '';  // Campo per lo username dell’utente, legato a un input nel template
  password: string = '';  // Campo per la password dell’utente
  Errore: { message: string, tentativi: number } = { message: '', tentativi: 0 }; // Oggetto per gestire i messaggi di errore e tentativi falliti
  benvenuto: string = ''; // Messaggio di benvenuto visualizzato all’utente dopo il login




  // Costruttore: inietto Userservice (il servizio che gestisce la logica HTTP) e Router (per cambiare pagina)
  constructor(public SerH: UserService, public Rotta: Router) {}




  // Funzione che viene chiamata quando l’utente clicca su "Accedi"
  Log_In(): void {
    this.SerH.Log_In(this.username, this.password).subscribe({
      next: data => {
        // Parsing brutale della risposta per ottenere il messaggio e il token (da sistemare meglio!)
        this.benvenuto = data.message = 'Benvenuto';
        localStorage.setItem("jwt", data.token); // Attenzione: "token" sembra un errore di battitura per "token"

        // Se il token è stato salvato correttamente
        if (localStorage.getItem("jwt") != null) {
          setTimeout(()=>{
              this.Rotta.navigate(["/home"])
          },2000)
          
    
         
        }
      },
      error: err => {
        // nel caso le credenziali fossero sbagliate, catturo errore mandato dalla funzione che gestisce Login nel Backend
        if(err.status==401)this.Errore.message="Credenziali non Valide" 
       else this.Errore.message = err.error.errore;
          
          this.Errore.tentativi = 1;
          setTimeout(() => { this.Errore.tentativi = 0 }, 3000);
  
      }
    })
  }

/************************************************************************************************************/

  // Funzione collegata al pulsante "Registrati", cambia pagina e porta l’utente alla pagina di registrazione
  INDI() {
    this.Rotta.navigate(["/registrazione"]);
  }


  

}
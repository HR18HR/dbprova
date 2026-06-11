import { Injectable } from '@angular/core';
import { HttpClient,HttpHeaders,provideHttpClient} from '@angular/common/http';
import { Observable } from 'rxjs';
import { Buffer } from 'buffer';

//Interface User-->emial,username,password,ruolo//
export interface UserM{
  email:string;
  password?:string,
  ruolo?:string,
  
}
export interface Token{
  id:number,
  nome:string,
  cognome:string,
  email:string,
  ruolo:string,
  password:string,
  data_nascita :Date | null
  
}

@Injectable({
  providedIn: 'root'
})

export class UserService { 
  
 




  
  constructor(public Http: HttpClient) {} // Inietto l'HttpClient per poter fare chiamate HTTP (es: POST, GET, DELETE ecc.)






  // Funzione di login: prende username e password, li concatena con ":" e li codifica in base64 per l'autenticazione Basic
  Log_In(email: string, password: string): Observable<{token:string,message:string}> {
    const header = new HttpHeaders({
      'Authorization': 'Basic ' + Buffer.from(email.concat(':').concat(password)).toString("base64")
    })
    return this.Http.post<{token:string,message:string}>('http://localhost:5000/login', {}, { headers: header }) // Fa la POST al backend con l'header Authorization
  }







  // Funzione per la registrazione utente normale: invia email, username e password tramite POST
  REGIST(email: string, nome:string,cognome:string,password: string, ruolo: string,data_nascita:Date): Observable<{message:string}> {
    return this.Http.post<{message:string}>("http://localhost:5000/registrazione", { 
      email: email, nome: nome, cognome:cognome,
      password: password ,ruolo:ruolo,data_nascita:data_nascita

    }, {})
  }





// Aggiorna i dati dell'utente (email, username, password) inviando una richiesta PUT con autenticazione
  Update(email: string, password: string,data_nascita:Date,nome:string,cognome:string,token:string): Observable<{token:string,message:string}> {
    const header = new HttpHeaders({
      'Authorization': 'Bearer ' + token
    });
    return this.Http.post<{token:string,message:string}>("http://localhost:5000/aggiorna", 
      { email: email,password: password,
        data_nascita:data_nascita,nome:nome,cognome:cognome
       }, { headers: header })
  }



}
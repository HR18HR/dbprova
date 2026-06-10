import { NgFor, NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule, NgModel } from '@angular/forms';
import { Token, UserService } from '../user.service';
import { jwtDecode } from 'jwt-decode';


@Component({
  selector: 'app-home',
  imports: [NgIf,NgFor,FormsModule],
  templateUrl: './homes.component.html',
  styleUrl: './homes.component.css'
})
export class HomesComponent {

to:Token={id:0,nome:"",cognome:"",email:"",ruolo:"",data_nascita:null,password:" "}
risposta:string=''; //mostar i messaggi ricevuti dal backend
res:{Pos:number,Neg:number}={Pos:0,Neg:0} //oggetto che mostra il div della risposta backend
message:string=" "
mostraModifica: boolean = false;


constructor( public user:UserService) {}


 ngAfterViewInit() {
    const token = localStorage.getItem('jwt');

    if (token != null) {
      this.to= jwtDecode<Token>(token);

    }
  }

  
  VisualizzaModifica() {
    !this.mostraModifica ;
  }


  aggiornaUtente() {

  const token = localStorage.getItem('jwt');

  if (!token) {
    return;
  }

  this.user.Update(
    this.to.email,
    this.to.password,
    this.to.data_nascita!,
    this.to.nome,
    this.to.cognome,
    token
  ).subscribe({
  next: (r) => {
    this.res.Pos = 1;
    this.res.Neg = 0;
    this.message = r.message;
    localStorage.setItem("jwt",r.token)
    this.to=this.to= jwtDecode<Token>(r.token)
    setTimeout(()=>{
        this.res.Pos=0
    }
  ,2000)
  },
  error: (err) => {
    this.res.Pos = 0;
    this.res.Neg = 1;
    this.message = "Errore Dati Non Aggiornati";
     setTimeout(()=>{
        this.res.Neg=0
    }
  ,2000)
  }
});

}



}

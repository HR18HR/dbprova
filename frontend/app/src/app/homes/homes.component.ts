import { NgFor, NgIf } from '@angular/common';
import { Component,OnInit,AfterViewInit } from '@angular/core';
import { FormsModule, NgModel } from '@angular/forms';
import { Token, UserService } from '../user.service';
import { jwtDecode } from 'jwt-decode';
import { Esami, EsamiPratica, Istituti, PraticheService ,Pratica} from '../pratiche.service';

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

 istituti:Istituti[]=[]
 esami :Esami[]=[]

 pratica = {
  studente_email: '',
  docente_email: null as string | null,
  data_inizio: '',
  data_fine: null as string | null,
  nome_istituto: ''
};
mostraPratica: boolean = false;
mostraEsami: boolean = false;

esamiPratica: EsamiPratica[] = [];

idPratica: string = '';
emailStudente: string = '';
emailDocente: string = '';
 filePratica: File | null = null;

dataPartenza: string = '';

dataRientro: string = '';

semestre: string = '';

nomeIstituto: string = '';

pratiche_1: Pratica[] = [];


constructor( public user:UserService,public pratiche:PraticheService) {}


 ngOnInit() {
    const token = localStorage.getItem('jwt');

    if (token != null) {
      this.to= jwtDecode<Token>(token);
      this.pratica.studente_email=this.to.email
      this.pratiche.GetIstituti(token).subscribe({
        next:(r)=>{
          this.istituti=r
          alert(this.istituti[0].nome)

        },
        error:(err)=>{
        
        }
      })


      this.pratiche.GetEsami(token).subscribe({
        next:(r)=>{
          this.esami=r
          alert(this.esami[0].nome)

        },
        error:(err)=>{
        
        }
      })
    
    this.pratiche.GetPraticheUtente(token)

    .subscribe({

      next: (response) => {

        this.pratiche_1 = response;
        console.log(this.pratiche_1[0])


      },

      error: (err) => {


      }

    });



    
  }



  }


   VisualizzaModifica() {

    this.mostraModifica = !this.mostraModifica;
  }

  VisualizzaEsami() {
  this.mostraEsami = !this.mostraEsami;
}


VisualizzaPratica() {
  if (!this.mostraPratica) {
    this.mostraPratica = true;

    this.idPratica = this.generaIdPratica();
    this.emailStudente = this.to.email;

    this.emailDocente = '';
    this.nomeIstituto = '';
    this.dataPartenza = '';
    this.dataRientro = ' ';
    this.semestre = '';

    this.esamiPratica = [];
    this.filePratica = null;
  } else {
    this.chiudiPratica();
  }
}

chiudiPratica() {
  this.mostraPratica = false;

  this.idPratica = '';
  this.emailStudente = '';
  this.emailDocente = '';
  this.esamiPratica = [];
  this.filePratica = null;
  this.dataPartenza=' ';
  this.semestre=' ';
  this.dataRientro='';
  this.nomeIstituto='';
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





generaIdPratica(lunghezza: number = 12): string {
  const caratteri = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let risultato = '';

  for (let i = 0; i < lunghezza; i++) {
    risultato += caratteri.charAt(Math.floor(Math.random() * caratteri.length));
  }

  return risultato;
}

aggiungiRigaEsame() {

  this.esamiPratica.push({
    id: this.esamiPratica.length + 1,
    pratica_id: this.idPratica,
    esame_locale_nome: '',
    esame_estero_nome: ''
  });

}

rimuoviEsamePratica(index: number) {

  this.esamiPratica.splice(index, 1);

}

selezionaFile(event: Event) {

  const input = event.target as HTMLInputElement;

  if (input.files && input.files.length > 0) {
    this.filePratica = input.files[0];
  }

}




creaPratica() {
  const token = localStorage.getItem("jwt");

  if (!token) {
    this.message = "Token mancante";
    return;
  }

  this.pratiche.CreaPratica(
    token,
    this.idPratica,
    this.emailStudente,
    this.emailDocente,
    this.nomeIstituto,
    this.dataPartenza,
    this.dataRientro,
    this.semestre,
    this.esamiPratica,
    this.filePratica
  ).subscribe({
    next: (r) => {
      this.message = r.message;
      this.res.Pos = 1;
      this.res.Neg = 0;

      this.chiudiPratica();
    },
    error: (err) => {
      this.message = err.error?.errore ?? "Errore creazione pratica";
      this.res.Pos = 0;
      this.res.Neg = 1;
    }
  });

  setTimeout(()=>{
    this.pratiche.GetPraticheUtente(token)

    .subscribe({

      next: (response) => {

        this.pratiche_1 = response;


      },

      error: (err) => {


      }

    });

  

},2000)



}




}

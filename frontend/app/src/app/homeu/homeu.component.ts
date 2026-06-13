import { NgFor, NgIf } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PraticheService, Pratica } from '../pratiche.service';

@Component({
  selector: 'app-homeu',
  standalone: true,
  imports: [NgIf, NgFor, FormsModule],
  templateUrl: './homeu.component.html',
  styleUrl: './homeu.component.css'
})
export class HomeuComponent implements OnInit {

  pratiche: Pratica[] = [];
  praticaSelezionata: Pratica | null = null;

  messaggio = '';
  errore = '';

  constructor(private praticheService: PraticheService) {}

  ngOnInit(): void {

    setInterval(()=>this.caricaPratiche(),2000);
  }

  caricaPratiche(): void {
    let token=localStorage.getItem("jwt_2")
    if(token){
    this.praticheService.getPraticheUfficio(token).subscribe({
      next: data => {
        this.pratiche = data;
      },
      error: err => {
        this.errore = err.error?.errore || 'Errore nel caricamento pratiche';
      }
    });
  }
  }

  apriPratica(p: Pratica): void {
    this.praticaSelezionata = p;
    this.messaggio = '';
    this.errore = '';
  }

  chiudiPratica(): void {
    this.praticaSelezionata = null;
  }

  accettaPratica(): void {
  if (!this.praticaSelezionata) return;
  let token=localStorage.getItem("jwt_2")
    if(token){
  this.praticheService.accettaPraticaUfficio(this.praticaSelezionata.id,token).subscribe({
    next: res => {
      this.messaggio = res.message || 'Pratica accettata correttamente';

      this.praticaSelezionata!.stato = res.pratica.stato;

      this.caricaPratiche();
    },
    error: err => {
      this.errore = err.error?.errore || 'Errore durante approvazione';
    }
  });
}
  }

  rifiutaPratica(): void {
  if (!this.praticaSelezionata) return;
    let token=localStorage.getItem("jwt_2")
    if(token){
  this.praticheService.rifiutaPraticaUfficio(this.praticaSelezionata.id,token).subscribe({
    next: res => {
      this.messaggio = res.message || 'Pratica rifiutata correttamente';

      this.praticaSelezionata!.stato = res.pratica.stato;

      this.caricaPratiche();
    },
    error: err => {
      this.errore = err.error?.errore || 'Errore durante rifiuto';
    }
  });
}
}

  scaricaAgreement(id: string): void {
    let token=localStorage.getItem("jwt_2")
    if(token){
    this.praticheService.scaricaAgreementUfficio(id,token).subscribe({
      next: blob => {
        const fileURL = URL.createObjectURL(blob);
        window.open(fileURL, '_blank');
      },
      error: err => {
        this.errore = 'Errore apertura learning agreement';
      }
    });
  }
}
}
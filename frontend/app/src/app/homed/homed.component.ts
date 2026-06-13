import { Component,OnInit,AfterViewInit} from '@angular/core';
import { Pratica, PraticheService} from '../pratiche.service';
import { NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-homed',
  imports: [NgIf,FormsModule,NgFor],
  templateUrl: './homed.component.html',
  styleUrl: './homed.component.css'
})
export class HomedComponent implements AfterViewInit{


praticheDocente: Pratica[] = [];
praticaSelezionata: Pratica | null = null;

motivazioneRifiuto: string = '';

message: string = '';
res = {
  Pos: 0,
  Neg: 0
};

constructor(public pratiche_1 :PraticheService){}


ngAfterViewInit(): void {

    const token = localStorage.getItem("jwt_1");



    if (token!=undefined) {

      setInterval(()=>this.caricaPraticheDocente(token),2000)

    }
  }



  caricaPraticheDocente(token: string): void {

    this.pratiche_1.getPraticheDocente(token).subscribe({

      next: (r) => {

        this.praticheDocente = r;

      },

      error: (err) => {

        this.message = err.error?.errore ?? 'Errore caricamento pratiche docente';

        this.res.Pos = 0;

        this.res.Neg = 1;

      }

    });

  }

mostraDettaglioPratica(p: Pratica) {
  this.praticaSelezionata = p;
  this.motivazioneRifiuto = p.motivazione ?? '';
}

chiudiDettaglio() {
  this.praticaSelezionata = null;
  this.motivazioneRifiuto = '';
}

accettaPratica() {
  const token = localStorage.getItem('jwt_1');

  if (!token || !this.praticaSelezionata) {
    return;
  }

  this.pratiche_1.accettaPraticaDocente(
    token,
    this.praticaSelezionata.id
  ).subscribe({
    next: (r) => {
      this.message = r.message;
      this.res.Pos = 1;
      this.res.Neg = 0;

      const i = this.praticheDocente.findIndex(p => p.id === r.pratica.id);

      if (i !== -1) {
        this.praticheDocente[i] = r.pratica;
      }

      this.praticaSelezionata = r.pratica;
    },
    error: (err) => {
      this.message = err.error?.errore ?? 'Errore approvazione pratica';
      this.res.Pos = 0;
      this.res.Neg = 1;
    }
  });
}


rifiutaPratica() {
  const token = localStorage.getItem('jwt_1');

  if (!token || !this.praticaSelezionata) {
    return;
  }

  if (!this.motivazioneRifiuto || this.motivazioneRifiuto.trim() === '') {
    this.message = 'La motivazione è obbligatoria per rifiutare la pratica';
    this.res.Pos = 0;
    this.res.Neg = 1;
    return;
  }

  this.pratiche_1.rifiutaPraticaDocente(
    token,
    this.praticaSelezionata.id,
    this.motivazioneRifiuto
  ).subscribe({
    next: (r) => {
      this.message = r.message;
      this.res.Pos = 1;
      this.res.Neg = 0;

      const i = this.praticheDocente.findIndex(p => p.id === r.pratica.id);

      if (i !== -1) {
        this.praticheDocente[i] = r.pratica;
      }

      this.praticaSelezionata = r.pratica;
    },
    error: (err) => {
      this.message = err.error?.errore ?? 'Errore rifiuto pratica';
      this.res.Pos = 0;
      this.res.Neg = 1;
    }
  });
}


mostraLearningAgreement() {
  const token = localStorage.getItem('jwt_1');

  if (!token || !this.praticaSelezionata) {
    return;
  }

  this.pratiche_1.scaricaLearningAgreement(
    token,
    this.praticaSelezionata.id
  ).subscribe({
    next: (file) => {
      const url = window.URL.createObjectURL(file);
      window.open(url, '_blank');
    },
    error: (err) => {
      this.message = err.error?.errore ?? 'Errore apertura Learning Agreement';
      this.res.Pos = 0;
      this.res.Neg = 1;
    }
  });

}

puoDecidereDocente(): boolean {
  return this.praticaSelezionata?.stato === 'ATT_APPROVAZIONE'
}


motivazioneReadOnly(): boolean {
  if (!this.praticaSelezionata) {
    return true;
  }

  return ![
    'ATT_APPROVAZIONE',
    'MOBILITA'
  ].includes(this.praticaSelezionata.stato);
}




}

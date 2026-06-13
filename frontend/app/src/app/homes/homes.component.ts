import { NgFor, NgIf } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Token, UserService } from '../user.service';
import { jwtDecode } from 'jwt-decode';
import { Esami, EsamiPratica, Istituti, PraticheService, Pratica } from '../pratiche.service';
import { error } from 'node:console';

@Component({
  selector: 'app-home',
  imports: [NgIf, NgFor, FormsModule],
  templateUrl: './homes.component.html',
  styleUrl: './homes.component.css'
})
export class HomesComponent implements OnInit {

  to: Token = {
    id: 0,
    nome: '',
    cognome: '',
    email: '',
    ruolo: '',
    data_nascita: null,
    password: ' '
  };

  risposta: string = '';
  res: { Pos: number, Neg: number } = { Pos: 0, Neg: 0 };
  message: string = ' ';

  mostraModifica: boolean = false;
  mostraPratica: boolean = false;
  mostraEsami: boolean = false;

  istituti: Istituti[] = [];
  esami: Esami[] = [];

  pratica = {
    studente_email: '',
    docente_email: null as string | null,
    data_inizio: '',
    data_fine: null as string | null,
    nome_istituto: ''
  };

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

  praticaSelezionata: Pratica | null = null;
  modificaPraticaAttiva: boolean = false;

  motivazioneModifica: string = '';
  dataRientroModifica: string = '';
  esamiPraticaModifica: EsamiPratica[] = [];
  eliminata:boolean=false;

  constructor(
    public user: UserService,
    public pratiche: PraticheService
  ) {}

  ngOnInit() {
    const token = localStorage.getItem('jwt');

    if (token != null) {
      this.to = jwtDecode<Token>(token);
      this.pratica.studente_email = this.to.email;

      this.caricaIstituti(token);
      this.caricaEsami(token);
      this.caricaPraticheUtente(token);
    }
  }

  caricaIstituti(token: string) {
    this.pratiche.GetIstituti(token).subscribe({
      next: (r) => {
        this.istituti = r;
      },
      error: () => {}
    });
  }

  caricaEsami(token: string) {
    this.pratiche.GetEsami(token).subscribe({
      next: (r) => {
        this.esami = r;
      },
      error: () => {}
    });
  }

  caricaPraticheUtente(token: string) {
    this.pratiche.GetPraticheUtente(token).subscribe({
      next: (response) => {
        this.pratiche_1 = response;
      },
      error: () => {}
    });
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
      this.dataRientro = '';
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
    this.dataPartenza = '';
    this.semestre = '';
    this.dataRientro = '';
    this.nomeIstituto = '';
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

        localStorage.setItem('jwt', r.token);
        this.to = jwtDecode<Token>(r.token);

        setTimeout(() => {
          this.res.Pos = 0;
        }, 2000);
      },
      error: () => {
        this.res.Pos = 0;
        this.res.Neg = 1;
        this.message = 'Errore Dati Non Aggiornati';

        setTimeout(() => {
          this.res.Neg = 0;
        }, 2000);
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
      esame_estero_id: ''
    } as any);
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
    const token = localStorage.getItem('jwt');

    if (!token) {
      this.message = 'Token mancante';
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
        this.caricaPraticheUtente(token);
      },
      error: (err) => {
        this.message = err.error?.errore ?? 'Errore creazione pratica';
        this.res.Pos = 0;
        this.res.Neg = 1;
      }
    });
  }

  selezionaPratica(p: Pratica) {
    this.semestre = (p as any).semestre ?? '';
    this.praticaSelezionata = p;
    this.modificaPraticaAttiva = false;

    this.emailDocente = p.docente_email ?? '';
    this.nomeIstituto = p.nome_istituto ?? '';
    this.dataPartenza = (p as any).data_inizio ?? '';
    this.dataRientroModifica = (p as any).data_fine ?? '';
    this.motivazioneModifica = (p as any).motivazione ?? '';

    this.esamiPraticaModifica = ((p as any).esami ?? []).map((e: any, index: number) => ({
      id: e.id ?? index + 1,
      pratica_id: p.id,
      esame_locale_nome: e.esame_locale_nome ?? '',
      esame_estero_id: e.esame_estero_id ?? e.esame_estero_nome ?? ''
    } as any));
  }

  puoVedereTastoModifica(p: Pratica): boolean {
    return p.stato === 'ATT_APPROVAZIONE' || p.stato === 'MOBILITA_IN_CORSO';
  }

  puoModificareCampoNormale(p: Pratica): boolean {
    return p.stato === 'ATT_APPROVAZIONE';
  }

  puoModificareDataRientro(p: Pratica): boolean {
    return p.stato === 'ATT_APPROVAZIONE' || p.stato === 'MOBILITA_IN_CORSO';
  }

  puoModificareEsami(p: Pratica): boolean {
    return p.stato === 'ATT_APPROVAZIONE' || p.stato === 'MOBILITA_IN_CORSO';
  }

  puoModificareMotivazione(p: Pratica): boolean {
    return false;
  }

  isReadOnlyTotale(p: Pratica): boolean {
    return p.stato !== 'ATT_APPROVAZIONE' && p.stato !== 'MOBILITA_IN_CORSO';
  }

  attivaModificaPratica() {
    this.modificaPraticaAttiva = true;
  }

  annullaModificaPratica() {
    this.modificaPraticaAttiva = false;

    if (this.praticaSelezionata) {
      this.selezionaPratica(this.praticaSelezionata);
    }
  }

  aggiungiEsameModifica() {
    if (!this.praticaSelezionata) return;

    this.esamiPraticaModifica.push({
      id: this.esamiPraticaModifica.length + 1,
      pratica_id: this.praticaSelezionata.id,
      esame_locale_nome: '',
      esame_estero_id: ''
    } as any);
  }

  rimuoviEsameModifica(index: number) {
    this.esamiPraticaModifica.splice(index, 1);
  }

  salvaModificaPratica() {
    const token = localStorage.getItem('jwt');

    if (!token || !this.praticaSelezionata) {
      return;
    }

    /*
    Qui poi devi creare/chiamare il metodo nel service:

    this.pratiche.ModificaPratica(
      token,
      this.praticaSelezionata.id,
      this.emailDocente,
      this.nomeIstituto,
      this.dataPartenza,
      this.dataRientroModifica,
      this.esamiPraticaModifica
    ).subscribe({
      next: (r) => {
        this.message = r.message;
        this.res.Pos = 1;
        this.res.Neg = 0;
        this.modificaPraticaAttiva = false;
        this.praticaSelezionata = null;
        this.caricaPraticheUtente(token);
      },
      error: (err) => {
        this.message = err.error?.errore ?? 'Errore modifica pratica';
        this.res.Pos = 0;
        this.res.Neg = 1;
      }
    });
    */
  }


  eliminaPratica(id:string){
    let token =localStorage.getItem("jwt")
    this.eliminata=true
    if(token!=undefined){
    this.pratiche.eliminaPratica(id,token).subscribe({
      next:(r)=>{
        this.message = r.message;
        this.res.Pos = 1;
        this.res.Neg = 0;
        this.pratiche_1=this.pratiche_1.filter((
          p => p.id !== id
        ))
      this.praticaSelezionata = null;
      this.modificaPraticaAttiva = false;

      },

      error:(err)=>{
        this.message = err.error?.errore ?? 'Errore creazione pratica';
        this.res.Pos = 0;
        this.res.Neg = 1;

      }


    })
  }
}


  puoEliminarePratica(pratica: Pratica): boolean {
  return pratica.stato === 'CREATA' || pratica.stato === 'ATT_APPROVAZIONE';
}

}
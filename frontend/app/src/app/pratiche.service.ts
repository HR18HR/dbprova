import { Injectable } from '@angular/core';
import { HttpClient,HttpHeaders,provideHttpClient} from '@angular/common/http';
import { Observable } from 'rxjs';
import { Buffer } from 'buffer';

export interface Istituti{
  nome:string,
  paese:string,
  citta:string,
  indirizzo:string
}

export interface Utenti {
  id: number;
  nome: string;
  cognome: string;
  email: string;
  password_hash: string;
  salt: string;
  ruolo: 'S' | 'D' | 'U';
  data_nascita: string; 
}

export interface Istituti {
  nome: string;
  indirizzo: string;
  citta: string ;
  paese: string;
}

export interface Pratica {
  id: string; // TEXT, non number
  studente_email: string;
  docente_email: string | null;
  nome_istituto: string | null;
  stato:
    | 'CREATA'
    | 'ATT_APPROVAZIONE'
    | 'APPROVATA_DOCENTE'
    | 'APPROVATA_UFFICIO'
    | 'MOBILITA_IN_CORSO'
    | 'APPROVATO_TRANSCRIPT'
    | 'CHIUSA';
  data_creazione: string;
  semestre:'PRIMO' | 'SECONDO' | 'ANNO' // TIMESTAMP → string
  motivazione: string | null;
  data_inizio: string;   // DATE → string
  data_fine: string | null;
  esami:EsamiPratica[]
}

export interface EsamiEsteri {
  id: string;
  nome: string;
  crediti: number;
}

export interface Esami {
  nome: string;
  crediti: number;
  nome_esame_estero: string | null;
}

export interface EsamiPratica {
  id: number;
  pratica_id: string;
  esame_locale_nome: string;
  esame_estero_nome: string;
  crediti?: number;
}



@Injectable({
  providedIn: 'root'
})
export class PraticheService {

  constructor(public Http: HttpClient) { }








GetIstituti(token: string): Observable<Istituti[]> {
  const headers = new HttpHeaders({
    'Authorization': 'Bearer ' + token
  });
  
  return this.Http.get<Istituti[]>('http://localhost:5000/istituti', { headers });
}

GetEsami(token: string): Observable<Esami[]> {
  const headers = new HttpHeaders({
    'Authorization': 'Bearer ' + token
  });
  
  return this.Http.get<Esami[]>('http://localhost:5000/esami', { headers });
}





CreaPratica(
  token: string,
  idPratica: string,
  emailStudente: string,
  emailDocente: string,
  nomeIstituto: string,
  dataPartenza: string,
  dataRientro: string | null,
  semestre: string,
  esami: EsamiPratica[],
  file: File | null
):Observable<{message:string}> {
  const formData = new FormData();

  formData.append("id_pratica", idPratica);
  formData.append("email_studente", emailStudente);
  formData.append("email_docente", emailDocente);
  formData.append("nome_istituto", nomeIstituto);
  formData.append("data_partenza", dataPartenza);
  formData.append("data_rientro", dataRientro ?? "");
  formData.append("semestre", semestre);
  formData.append("esami", JSON.stringify(esami));

  if (file) {
    formData.append("agreement", file);
  }

  return this.Http.post<{message:string}>(
    'http://localhost:5000/pratica',
    formData,
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
}




GetPraticheUtente(
  token: string
): Observable<Pratica[]> {

  return this.Http.get<Pratica[]>(
    'http://localhost:5000/pratiche',
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
}


eliminaPratica(id: string,token:string): Observable<{ message: string }> {


  return this.Http.delete<{ message: string }>(
    `http://localhost:5000/eliminapratiche/${id}`,
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
}



ModificaPratica(
  token: string,
  id_pratica: string,
  email_docente: string,
  nome_istituto: string,
  data_partenza: string,
  data_rientro: string | null,
  semestre: string,
  esami: EsamiPratica[],
  learningAgreementModifica: File | null,
  transcript: File | null
): Observable<{ message: string, pratica: Pratica }> {

  const headers = new HttpHeaders({
    Authorization: `Bearer ${token}`
  });

  const formData = new FormData();

  formData.append('email_docente', email_docente);
  formData.append('nome_istituto', nome_istituto);
  formData.append('data_partenza', data_partenza);

  if (data_rientro) {
    formData.append('data_rientro', data_rientro);
  }

  formData.append('semestre', semestre);
  formData.append('esami', JSON.stringify(esami));

  if (learningAgreementModifica) {
    formData.append('agreement', learningAgreementModifica);
  }
  if (transcript) {
    formData.append('transcript', transcript);
  }

  return this.Http.put<{ message: string, pratica: Pratica }>(
    `http://localhost:5000/modifica_pratica/${id_pratica}`,
    formData,
    { headers }
  );
}

getPraticheDocente(token: string): Observable<Pratica[]> {
  const headers = new HttpHeaders({
    Authorization: `Bearer ${token}`
  });

  return this.Http.get<Pratica[]>(
    'http://localhost:5000/pratiche_docente',
    { headers }
  );
}


accettaPraticaDocente(
  token: string,
  id_pratica: string
): Observable<{message:string, pratica:Pratica}> {
  const headers = new HttpHeaders({
    Authorization: `Bearer ${token}`
  });

  return this.Http.put<{message:string, pratica:Pratica}>(
    `http://localhost:5000/pratiche_docente/${id_pratica}/accetta`,
    {},
    { headers }
  );
}



rifiutaPraticaDocente(
  token: string,
  id_pratica: string,
  motivazione: string
): Observable<{message:string, pratica:Pratica}> {
  const headers = new HttpHeaders({
    Authorization: `Bearer ${token}`
  });

  return this.Http.put<{message:string, pratica:Pratica}>(
    `http://localhost:5000/pratiche_docente/${id_pratica}/rifiuta`,
    { motivazione },
    { headers }
  );
}



scaricaLearningAgreement(token: string, id_pratica: string): Observable<Blob> {
  const headers = new HttpHeaders({
    Authorization: `Bearer ${token}`
  });

  return this.Http.get(
    `http://localhost:5000/pratiche_docente/${id_pratica}/learning_agreement`,
    {
      headers,
      responseType: 'blob'
    }
  );
}




getPraticheUfficio(token: string) {
  return this.Http.get<Pratica[]>(
    "http://localhost:5000/pratiche_ufficio",
    {
      headers: new HttpHeaders({
        Authorization: `Bearer ${token}`
      })
    }
  );
}

accettaPraticaUfficio(id: string, token: string) {
  return this.Http.put<any>(
    `http://localhost:5000/pratiche_ufficio/${id}/accetta`,
    {},
    {
      headers: new HttpHeaders({
        Authorization: `Bearer ${token}`
      })
    }
  );
}

rifiutaPraticaUfficio(id: string, token: string) {
  return this.Http.put<any>(
    `http://localhost:5000/pratiche_ufficio/${id}/rifiuta`,
    {},
    {
      headers: new HttpHeaders({
        Authorization: `Bearer ${token}`
      })
    }
  );
}

scaricaAgreementUfficio(id: string, token: string) {
  return this.Http.get(
    `http://localhost:5000/pratiche_ufficio/${id}/learning_agreement`,
    {
      headers: new HttpHeaders({
        Authorization: `Bearer ${token}`
      }),
      responseType: 'blob'
    }
  );
}

scaricaTranscript(token: string, id_pratica: string): Observable<Blob> {
  const headers = new HttpHeaders({
    Authorization: `Bearer ${token}`
  });

  return this.Http.get(
    `http://localhost:5000/pratiche_docente/${id_pratica}/transcript`,
    {
      headers,
      responseType: 'blob'
    }
  );
}




}


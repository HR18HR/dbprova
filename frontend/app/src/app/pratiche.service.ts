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
  data_nascita: string; // DATE → string (ISO format)
}

export interface Istituti {
  nome: string;
  indirizzo: string;
  citta: string ;
  paese: string;
}

<<<<<<< Updated upstream
<<<<<<< Updated upstream
export interface Pratica {
=======
export interface Pratiche {
>>>>>>> Stashed changes
=======
export interface Pratiche {
>>>>>>> Stashed changes
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
  data_creazione: string; // TIMESTAMP → string
  motivazione: string | null;
  data_inizio: string;   // DATE → string
  data_fine: string | null;
<<<<<<< Updated upstream
<<<<<<< Updated upstream
  esami:EsamiPratica[]
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
  esame_estero_nome: string;
=======
  esame_estero_id: string;
>>>>>>> Stashed changes
=======
  esame_estero_id: string;
>>>>>>> Stashed changes
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




<<<<<<< Updated upstream
<<<<<<< Updated upstream
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


=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes


}

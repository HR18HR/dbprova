import { NgFor, NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule, NgModel } from '@angular/forms';

@Component({
  selector: 'app-home',
  imports: [NgIf,NgFor,FormsModule],
  templateUrl: './homes.component.html',
  styleUrl: './homes.component.css'
})
export class HomesComponent {
  ruolo: string = localStorage.getItem("ruolo") || "";

pratiche: any[] = [];

creaPratica() {}
modificaPratica(id: number) {}
eliminaPratica(id: number) {}

approvaPratica(id: number) {}
rifiutaPratica(id: number, motivazione: string) {}

confermaPrePartenza(id: number) {}
chiudiPratica(id: number) {}

}

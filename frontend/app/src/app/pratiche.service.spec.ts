import { TestBed } from '@angular/core/testing';

import { PraticheService } from './pratiche.service';

describe('PraticheService', () => {
  let service: PraticheService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PraticheService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

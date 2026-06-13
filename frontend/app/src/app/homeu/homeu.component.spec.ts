import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HomeuComponent } from './homeu.component';

describe('HomeuComponent', () => {
  let component: HomeuComponent;
  let fixture: ComponentFixture<HomeuComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomeuComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HomeuComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

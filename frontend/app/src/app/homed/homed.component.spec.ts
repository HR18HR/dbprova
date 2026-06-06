import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HomedComponent } from './homed.component';

describe('HomedComponent', () => {
  let component: HomedComponent;
  let fixture: ComponentFixture<HomedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomedComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HomedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

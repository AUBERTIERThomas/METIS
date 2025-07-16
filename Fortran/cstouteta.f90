!   Last change:  T     3 Jan 2003   11:07 am
!   rajout du PERP fa�on dual EM 27 mai 2015 ok avec un signe moins (qui est normal vu la g�om�trie mod�lis�e)
!   le programme fonctionne le 19/05/2020
!   à faire : rajouter le GEM2 et envisager un passage sous python pour appel dans les procédure de traitement 
!   rajout en cours 21/07/2023
!   version avec alimentaiton par fichier on utilise get_command_argument (fortran 2003)
!   on passe chaque calcul pour les géométries dans des subroutines
!   On peut choisir d'initialiser avec un nom de fichier ou sinon, le programme se lance à la main
!   fonctionnel le 05/06/2025 pour les fonction dédiée au géométrie prp prp2 (dualEM) VCP et HCP
!   fonction bucking ok implémentaiotn en test le 12/06/2025 :
! - valeurs très proches de 0 donc la façon de calculer n'est pas bonne. à reprendre

!   fonction cus OK le 10/06/2025 attention, différence à la 6 décimale pour prp,prp2,HCP (passage en double précision ?)
!   à implémenter dans le programme principal
    
program cs150
implicit none
interface
  FUNCTION FC1(Xx,Rr)
    implicit none
    real::fc1
    REAL,INTENT(IN)::xx,rr
  END function fc1
  
  FUNCTION FC2(Xx,Zz,Rr)
    implicit none
    REAL::fc2
    REAL, INTENT(IN)::xx,rr,zz
  END function fc2
  
  subroutine rep_perp(X,Y,Z,tl,rep)
    implicit none
    real, intent(in)::x,y,Z
    real, dimension(:), intent(in) :: tl
    real, dimension(:),allocatable,intent(out) :: rep
  end subroutine rep_perp
  
  subroutine rep_perp2(X,Y,Z,tl,rep)
    implicit none
    real, intent(in)::x,y,Z
    real, dimension(:), intent(in) :: tl
    real, dimension(:),allocatable,intent(out) :: rep
  end subroutine rep_perp2
  
  subroutine rep_hcp(X,Y,Z,tl,rep)
    implicit none
    real, intent(in)::x,y,Z
    real, dimension(:), intent(in) :: tl
    real, dimension(:),allocatable,intent(out) :: rep
  end subroutine rep_hcp
  
  subroutine rep_vcp(X,Y,Z,tl,rep)
    implicit none
    real, intent(in)::x,y,Z
    real, dimension(:), intent(in) :: tl
    real, dimension(:),allocatable,intent(out) :: rep
  end subroutine rep_vcp

  subroutine rep_cus(X,Y,Z,tl,a,b,rep)
    implicit none
    real, intent(in)::x,y,Z
    real, dimension(:), intent(in) :: tl
    real, dimension(:),intent(in):: a,b
    real, dimension(:),allocatable,intent(out) :: rep

  end subroutine rep_cus

  subroutine rep_bucking(num_bc,rep,rep_bc)
    implicit none
    real,dimension(:),intent(in) :: rep
    real,dimension(:),allocatable,intent(out) :: rep_bc
    integer,intent(in)::num_bc
  end subroutine rep_bucking


END interface

integer ::i,nb_ec,ib,ic,ioerr,ioerrf,num_buck,nb_cfg,nb_col
REAL:: x,y,z,n,a,co,ymax
real,dimension(:),allocatable :: tl,Y1,resultat,r1,rephcp, repvcp,repprp,repprp2,repCUS
character(10),parameter :: st2i='0123456789'
character(4),dimension(4):: lab_cfg=(/' PRP','PRP2',' HCP',' VCP'/)
character(20) :: nomfich,nomfich_ini
character(250)::form_col,tit_col

write(*,*) " Programme d'etalonnage à la boule des dispositif slingram frequentiel"
write(*,*) "le calcul est base sur keller et friknesht"
write(*,*) "le champ est considere uniforme sur le volume de la boule"
!la boule est sur l'axe T-R si x=0 le changer est utile pour faire une carte de sensibilité

call get_command_argument(1,nomfich_ini,status=ioerr)
if (ioerr==0) then
  write(*,*) "initialisation à partir du fichier ",nomfich_ini
  open(15,file=nomfich_ini,status='old',iostat=ioerrf)
  if (ioerrf/=0) stop "absence du fichier d''initialisation"
  read(15,*) nb_ec
  read(15,* )num_buck
else
  write(*,*) 'Combien d''ecartment voulez vous (en considerant la bucking coil comme une receptrice) ?'
  read(*,*) nb_ec
  write (*,*) 'position bucking coil ? (aucune=0)'
  read (*,*) num_buck
  write(*,*) "dispositif calcules : Perp (CS), Perp (DualEM) HCP, VCP"
endif

allocate(tl(nb_ec),y1(nb_ec),R1(nb_ec),resultat(nb_ec))



! si il y a bucking coil alors le résultat sera la différence des autres réceptrices avec ell
if (num_buck/=0) then
  nb_col=size(resultat)-1
else
  nb_col=size(resultat)
endif
allocate(repPRP(nb_col),repPRP2(nb_col),repHCP(nb_col),repVCP(nb_col),repCUS(nb_col))

tit_col="position(cm) "
form_col="(F7.2,2X"
nb_cfg=size(lab_cfg)
do ib=1,nb_cfg
  if (nb_col>1) then
    do ic=1,nb_col
      tit_col=trim(tit_col)//' '//lab_cfg(ib)//'v'//st2i(ic+1:ic+1)
    enddo
    form_col=trim(form_col)//','//st2i(nb_col+1:nb_col+1)//'(2X,F10.3)'
  else
    tit_col=trim(tit_col)//' '//lab_cfg(ib)
    form_col=trim(form_col)//',2x,F10.3'
  endif
enddo
form_col=trim(form_col)//")"


if (ioerr==0) then
  read(15,*) nomfich
  OPEN(7,FILE=nomfich)

  do ib=1,nb_ec
    read(15,*) tl(ib)
  enddo
  write(7,*) tl  
  READ(15,*)X,Y,Z
  read(15,*) n,ymax
  read(15,*) a
  CO=-A*A*A/2.

  write(7,*) tit_col
  ! boucle sur les positions de la boule
    do
      ! calcul PERP 
      call rep_perp(x,y,z,tl,resultat)
      if (num_buck/=0) then
        call rep_bucking(num_buck,resultat,repPRP)
        repPRP=-CO*repPRP*TL*TL*TL*1000000.
      else
        repPRP=-CO*resultat*TL*TL*TL*1000000.
      endif

      ! calcul HCP 
      call rep_hcp(x,y,z,tl,resultat)
      if (num_buck/=0) then
        call rep_bucking(num_buck,resultat,repHCP)
        repHCP=-CO*repHCP*TL*TL*TL*1000000.
      else
        repHCP=-CO*resultat*TL*TL*TL*1000000.
      endif
      ! calcul PERP (style Dual EM)
      call rep_perp2(x,y,z,tl,resultat)
      if (num_buck/=0) then
        call rep_bucking(num_buck,resultat,repprp2)
        repPRP2=-CO*repPRP2*TL*TL*TL*1000000.
      else
        repPRP2=-CO*resultat*TL*TL*TL*1000000.
      endif
    
      ! calcul VCP
      call rep_vcp(x,y,z,tl,resultat)
      if (num_buck/=0) then
        call rep_bucking(num_buck,resultat,repprp2)
        repVCP=-CO*repVCP*TL*TL*TL*1000000.
      else
        repVCP=-CO*resultat*TL*TL*TL*1000000.
      endif
                
!      WRITE(*,form_col)y,REPprp,repprp2,rephcp,repvcp
      write(7,form_col) y,REPprp,repprp2,rephcp,repvcp
      if (y>=ymax) exit
      y=y+n 
    END do
else
  do
    write(*,*) 'rentrez le nom du fichier'
    read(*,*) nomfich
    OPEN(7,FILE=nomfich)
    do ib=1,nb_ec
      write(*,*) '�cartement des bobines (cm) (',ib,')'
      read(*,*) tl(ib)
    enddo
    write(7,*) tl  
    WRITE(*,*)'POSITION initiale DE LA BOULE EN X, Y ET  Z PAR RAPPORT'
    WRITE(*,*)' A L EMETTRICE ?(calcul en uemcgs si au dessus Z positif)'
    write(*,*)'attention le deplacement est selon y, l''axe du dispositif'
    READ(*,*)X,Y,Z
    write(*,*)'pas en Y et position finale'
    read(*,*) n,ymax
    write(*,*)'rayon de la boule (cm)'
    read(*,*) a
    CO=-A*A*A/2.
    write(7,*) tit_col

  ! boucle sur les positions de la boule
    do
    
        ! calcul PERP 
      call rep_perp(x,y,z,tl,resultat)
      if (num_buck/=0) then
        call rep_bucking(num_buck,resultat,repPRP)
        repPRP=-CO*repPRP*TL*TL*TL*1000000.
      else
        repPRP=-CO*resultat*TL*TL*TL*1000000.
      endif

      ! calcul HCP 
      call rep_hcp(x,y,z,tl,resultat)
      if (num_buck/=0) then
        call rep_bucking(num_buck,resultat,repHCP)
        repHCP=-CO*repHCP*TL*TL*TL*1000000.
      else
        repHCP=-CO*resultat*TL*TL*TL*1000000.
      endif
      ! calcul PERP (style Dual EM)
      call rep_perp2(x,y,z,tl,resultat)
      if (num_buck/=0) then
        call rep_bucking(num_buck,resultat,repprp2)
        repPRP2=-CO*repPRP2*TL*TL*TL*1000000.
      else
        repPRP2=-CO*resultat*TL*TL*TL*1000000.
      endif
    
      ! calcul VCP
      call rep_vcp(x,y,z,tl,resultat)
      if (num_buck/=0) then
        call rep_bucking(num_buck,resultat,repprp2)
        repVCP=-CO*repVCP*TL*TL*TL*1000000.
      else
        repVCP=-CO*resultat*TL*TL*TL*1000000.
      endif
      
    !WRITE(*,form_col)y,REPprp,repprp2,rephcp,repvcp
      write(7,form_col) y,REPprp,repprp2,rephcp,repvcp
        if (y>=ymax) exit
        y=y+n 
      END do
      WRITE(*,*) 'on continue avec une autre geometrie initiale? (oui:1)'
      READ(*,*) i
      IF(i/=1) then
        exit
      else
        write(*,*) 'Combien d''ecartment voulez vous (en considerant la bucking coil comme une receptrice) ?'
        read(*,*) nb_ec
        write (*,*) 'position bucking coil ? (aucune=0)'
        read (*,*) num_buck
        write(*,*) "dispositif calcules : Perp (CS), Perp (DualEM) HCP, VCP"
        deallocate(tl,y1,r1,resultat,repPRP,repPRP2,repHCP,repVCP)
        allocate(tl(nb_ec),y1(nb_ec),R1(nb_ec),resultat(nb_ec),repPRP(nb_ec),repPRP2(nb_ec),repHCP(nb_ec),repVCP(nb_ec))


        ! si il y a bucking coil alors le résultat sera la différence des autres réceptrices avec la bucking
        if (num_buck/=0) then
          nb_col=size(resultat)-1
        else
          nb_col=size(resultat)
        endif
      endif

      close(7)
  end do
endif
stop
end program cs150

 FUNCTION FC1(Xx,Rr)
  implicit none
  real::fc1
  REAL,INTENT(IN)::xx,rr

      FC1=(3.*Xx*Xx/Rr/Rr-1.)/rR/rR/rR
 RETURN
 END function fc1

 FUNCTION FC2(Xx,Zz,Rr)
  implicit none
  real::fc2,r5
  REAL, INTENT(IN)::xx,rr,zz
    R5=Rr**5
    FC2=3.*Xx*Zz/R5
  RETURN
 END function fc2

 ! calcul PERP T DHy R DV
 subroutine rep_perp(X,Y,Z,tl,rep)
  implicit none

  interface
  FUNCTION FC1(Xx,Rr)
    implicit none
    real::fc1
    REAL,INTENT(IN)::xx,rr
  END function fc1
  
  FUNCTION FC2(Xx,Zz,Rr)
    implicit none
    REAL::fc2
    REAL, INTENT(IN)::xx,rr,zz
  END function FC2
  end interface

  real, intent(in)::x,y,Z
  real, dimension(:), intent(in) :: tl
  real, dimension(:),allocatable,intent(out) :: rep
  real,dimension(:),allocatable::Y1,R1
  real :: X1,Z1,R,HX,HY,HZ
  integer :: i,n_tl

  n_tl=size(tl)
  allocate(Y1(n_tl),R1(n_tl),rep(n_tl))
  Y1=TL-Y
  X1=-X
  Z1=-Z
  r=SQRT(x*x+y*y+z*z)
  R1=SQRT(X1*X1+Y1*Y1+Z1*Z1)
  !calcul du champ au niveau de la sphère (pour avoir la direction du dipôle induit) 
  HX=FC2(X,Y,R)
  HY=FC1(Y,R)
  HZ=FC2(Y,Z,R)
  do i=1,n_tl
    rep(i)=HZ*FC1(Z1,R1(i))+HY*FC2(Y1(i),Z1,R1(i))+HX*FC2(X1,Z1,R1(i))
  enddo
 end subroutine rep_perp
 
 ! calcul PERP dual EM T DV R DHy
 subroutine rep_perp2(X,Y,Z,tl,rep)
  implicit none
  interface
  FUNCTION FC1(Xx,Rr)
    implicit none
    real::fc1
    REAL,INTENT(IN)::xx,rr
  END function fc1
  
  FUNCTION FC2(Xx,Zz,Rr)
    implicit none
    REAL::fc2
    REAL, INTENT(IN)::xx,rr,zz
  END function FC2
  end interface

  real, intent(in)::x,y,Z
  real, dimension(:), intent(in) :: tl
  real, dimension(:),allocatable,intent(out) :: rep
  real,dimension(:),allocatable::Y1,R1
  real :: X1,Z1,R,HX,HY,HZ
  integer :: i,n_tl

  n_tl=size(tl)
  allocate(Y1(n_tl),R1(n_tl),rep(n_tl))
  Y1=TL-Y
  X1=-X
  Z1=-Z
  r=SQRT(x*x+y*y+z*z)
  R1=SQRT(X1*X1+Y1*Y1+Z1*Z1)
!calcul du champ au niveau de la sphère (pour avoir la direction du dipôle induit) 
  HX=FC2(X,Z,R)
  HY=FC2(Y,Z,R)
  HZ=FC1(Z,R)
  do i=1,n_tl
    REP=HZ*FC2(Y1(i),Z1,R1(i))+HY*FC1(Y1(i),R1(i))+HX*FC2(X1,Y1(i),R1(i))
  enddo
  return
 end subroutine rep_perp2

 ! calcul HCP T DV R DV
 subroutine rep_hcp(X,Y,Z,tl,rep)
  implicit none
  interface
  FUNCTION FC1(Xx,Rr)
    implicit none
    real::fc1
    REAL,INTENT(IN)::xx,rr
  END function fc1
  
  FUNCTION FC2(Xx,Zz,Rr)
    implicit none
    REAL::fc2
    REAL, INTENT(IN)::xx,rr,zz
  END function FC2
  end interface

  real, intent(in)::x,y,Z
  real, dimension(:), intent(in) :: tl
  real, dimension(:),allocatable,intent(out) :: rep
  real,dimension(:),allocatable::Y1,R1
  real :: X1,Z1,R,HX,HY,HZ
  integer :: i,n_tl

  n_tl=size(tl)
  allocate(Y1(n_tl),R1(n_tl),rep(n_tl))
  Y1=TL-Y
  X1=-X
  Z1=-Z
  R1=SQRT(X1*X1+Y1*Y1+Z1*Z1)
  r=SQRT(x*x+y*y+z*z)
  !calcul du champ au niveau de la sphère (pour avoir la direction du dipôle induit)  
  HX=FC2(X,Z,R)
  HY=FC2(Y,Z,R)
  HZ=FC1(Z,R)
  do i=1,n_tl
    REP(i)=HZ*FC1(Z1,R1(i))+HY*FC2(Y1(i),Z1,R1(i))+HX*FC2(X1,Z1,R1(i))
  enddo
  return
 end subroutine rep_hcp

! calcul VCP T DHx R DHx
subroutine rep_vcp(X,Y,Z,tl,rep)
  implicit none
  
  interface
  FUNCTION FC1(Xx,Rr)
    implicit none
    real::fc1
    REAL,INTENT(IN)::xx,rr
  END function fc1
  
  FUNCTION FC2(Xx,Zz,Rr)
    implicit none
    REAL::fc2
    REAL, INTENT(IN)::xx,rr,zz
  END function FC2
  end interface

 
  real, intent(in)::x,y,Z
  real, dimension(:), intent(in) :: tl
  real, dimension(:),allocatable,intent(out) :: rep
  real,dimension(:),allocatable::Y1,R1
  real :: X1,Z1,R,HX,HY,HZ
  integer :: i,n_tl

  n_tl=size(tl)
  allocate(Y1(n_tl),R1(n_tl),rep(n_tl))

  Y1=TL-Y
  X1=-X
  Z1=-Z
  R1=SQRT(X1*X1+Y1*Y1+Z1*Z1)
  r=SQRT(x*x+y*y+z*z)
  !calcul du champ au niveau de la sphère (pour avoir la direction du dipôle induit) 
  HX=FC1(X,R)
  HY=FC2(Y,X,R)
  HZ=FC2(X,Z,R)
  do i=1,n_tl
    REP(i)=HZ*FC2(X1,Z1,R1(i))+HY*FC2(Y1(i),X1,R1(i))+HX*FC1(X1,R1(i))
  end do

  return
end subroutine rep_vcp

!calcul de la réponse pour un couple de dipole T R quelconque
subroutine rep_cus(X,Y,Z,tl,a,b,rep)
  implicit none
  interface
  FUNCTION FC1(Xx,Rr)
    implicit none
    real::fc1
    REAL,INTENT(IN)::xx,rr
  END function fc1
  
  FUNCTION FC2(Xx,Zz,Rr)
    implicit none
    REAL::fc2
    REAL, INTENT(IN)::xx,rr,zz
  END function FC2
  end interface

  real, intent(in)::x,y,Z
  real, dimension(:), intent(in) :: tl
  real, dimension(:),intent(in):: a,b
  real, dimension(:),allocatable,intent(out) :: rep
  real,dimension(:),allocatable::Y1,R1
  real :: coefTx,coefTy,coefTz,coefRx,coefRy,coefRz,pi
  real :: X1,Z1,R,HX,HY,HZ
  integer :: i,n_tl
  pi=4.*atan2(1.,1.)

  coefTx=cos(a(2)*pi/180.)*sin(a(1)*pi/180.)
  coefTy=cos(a(2)*pi/180.)*cos(a(1)*pi/180.)
  coefTz=sin(a(2)*pi/180.)
  coefRx=cos(b(2)*pi/180.)*sin(b(1)*pi/180.)
  coefRy=cos(b(2)*pi/180.)*cos(b(1)*pi/180.)
  coefRz=sin(b(2)*pi/180.)

  n_tl=size(tl)
  allocate(Y1(n_tl),R1(n_tl),rep(n_tl))

  Y1=TL-Y
  X1=-X
  Z1=-Z
  R1=SQRT(X1*X1+Y1*Y1+Z1*Z1)
  r=SQRT(x*x+y*y+z*z)
  !calcul du champ au niveau de la sphère (pour avoir la direction du dipôle induit) 
  HX=coefTx*FC1(X,R)+coefTy*FC2(Y,X,R)+coefTz*FC2(Z,X,R)
  HY=coefTx*FC2(X,Y,R)+coefTy*fc1(y,r)+coefTz*fc2(Z,Y,r)
  HZ=coefTx*FC2(X,Z,R)+coefTy*fc2(y,z,r)+coefTz*fc1(z,r)

  do i=1,n_tl
    REP(i)=coefRx*(HZ*FC2(X1,Z1,R1(i))+HY*FC2(Y1(i),X1,R1(i))+HX*FC1(X1,R1(i)))+&
    &coefRy*(HZ*FC2(y1(i),Z1,R1(i))+HY*FC1(Y1(i),R1(i))+HX*FC2(X1,y1(i),R1(i)))+&
    &coefRz*(HZ*FC1(Z1,R1(i))+HY*FC2(Y1(i),z1,R1(i))+HX*FC2(X1,Z1,R1(i)))
  end do
 return

end subroutine rep_cus

subroutine rep_bucking(num_bc,rep,rep_bc)
  implicit none
  real,dimension(:),intent(in) :: rep
  real,dimension(:),allocatable,intent(out) :: rep_bc
  integer,intent(in)::num_bc
  integer::t_rep,i,ib

  t_rep=size(rep)
  allocate(rep_bc(t_rep-1))
  ib=1
  do i=1,t_rep
    if (i/=num_bc) then
      rep_bc(ib)=rep(i)-rep(num_bc)
      ib=ib+1
    endif
  enddo
  return
end subroutine rep_bucking 

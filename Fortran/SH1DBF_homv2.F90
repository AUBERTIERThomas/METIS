! SH1DBF_hom.F90
! REPONSE POUR UN SLINGRAM BF
! version expurgée pour appel python dans le cadre du traitement EMBF (<500kHz)
! les appareils sont libres (multi fréquence multi disposition)
! le calcul peut être old style (rep1D() sans permittivité)
! ou pas (rep1Dv2()) mais on utilisera la v2
!--------------------------------------------------------------------------------------------------
! le 21/05/2020 le résultat de la réécriture fonctionne en comparant avec le 1D AT
! le 22/05/2020 refonte de l'organisation avec mise dans les modules correspondants des initialisations de 
! terrain et géométrie (préparation pour le changement total)
! prochaines étapes
! rajouter les dernières configurations en les extrayant des programmes plus récents OK le 25/05/2020
! reproposer toutes les fonctionnalités
! variation fréquentielle OK
! enfoncement d'une couche OK
! élévation au dessus d'un sol homogène OK
! épaississement d'une première couche OK
! variation de propriété d'un sol homogène pour calcul des courbes d'étalonnage
! utiliser la source Hanksgcmodv2.f90 pour la transformée de hankel
! adapter pour que les fréquence intermédiaire soit faite également et prise en compte de la permittivité
! les fonctions prenant en compte la permittivité sont OK le 13/08/2020 (avec un bémol de Nan pas expliqué.)
! 
! reste le coeefficient de normalisation par le champ primaire à vérifier
! (mettre HCP ou deuxième position de Gauss pour tous (à vérifier pour la boule du coup))
! implémenter les valeur fixes et ensuie travailler sur la valeur générale : à faire 
! les hanksgc montent jusqu'à 500 000 Hz (à vérifier)
! rajouter le dual EM et le GEM2 (au moins en potentiel)
! rajouter le calcul d'abaque pour les valeurs de propiétés apparentes
! réflexion sur le rajout d'appariel avec bucking : introduciton d'un tableau buck qui contient le rapport de 
! distance entre la réceptrice principale et la bucking si ce rapport est inférieur à 1 alors il y a bucking
! pour l'utilisation avec fichier d'entrée dans la ligne de commande, il faut reboucler toute l'initialisation
! par fichier OK le 02/07/2025
!



!--------------------------------------------------------------------------------------------------
! le module E_S gère les formats et la cuisine d'initialisation par fichier.
! les sauvegardes sont gérées par les procédures unset des modules appareils et propriete_1D
! En théorie, les affichages des différents menus devraient aussi se retrouver dans ce module
! ainsi que la mémoire des différents choix fait par l'utilisateur.
! 
! à faire : dans l'idéal, il faudrait créer un module pour chaque langue avec les phrases
! ayant le même nom de variable mais un appel à un module différent (comme french_talk).
! Ce boulot est monstrueux...
! mais une fois fait, pour un module, copier coller et traduction sont rapides (et faisable par n'importe qui)
! 
! à faire : checker que tous les formats sont bien dans le module E_S
!--------------------------------------------------------------------------------------------------

module E_S
    use french_talk

    implicit none
    character(len=*) , parameter :: fmt0="(a4,', "//EEai//"CARTEMENT '"//",F5.2,4X,' HAUTEUR ',F4.2,2X,&
    &'fr"//e_ai//"quence (Hz) : ',F10.2)"
    character(len=*) , parameter :: fmt1="(a4,', hauteur Tx ',F4.2,4X,' HAUTEUR Rx',F5.2,2X,'fr"//e_ai//"quence (Hz) : ',F10.2)"
    character(len=*) , parameter :: fmt2="('fr"//e_ai//"quence',F10.2,' Hz',3X,'valeur du champ secondaire : ',E15.8,3X,E15.8)"
    character(len=*) , parameter :: fmt2b="(F10.2,3X,E15.8,3X,E15.8)"
    
    character(len=*) , parameter :: fmt3="('Rau : ',F7.2,'ohm.m - Epsilon r :',F9.2,'/Kph(1000Hz) : ',E12.5,&
    &' uSI - Kqu : ',E12.5,' uSI/Valeur du champ secondaire : ',E15.8,3X,E15.8)"
    character(len=*) , parameter :: fmt3b="(2X,F7.2,3X,F9.2,3X,E12.5,3X,E12.5,3X,E15.8,3X,E15.8)"
    character(len=*) , parameter :: fmt3c="(2X,F7.2,3X,F9.2,3X,E12.5,3X,E12.5)"
    character(len=*), parameter :: fmt3d="(2X,F7.2,3X,F9.2,3X,E12.5,3X,E12.5,3X,E15.8,3X,E15.8,3X,F7.2)"
    character(len=*) , parameter :: fmt4="('"//e_ai//"paisseur (m) :',F5.2,2X,'valeur du champ secondaire : ',&
    &E15.8,3X,E15.8)"
    character(len=*) , parameter :: fmt4b="(2X,F5.2,3X,E15.8,3X,E15.8)"
    character(len=*) , parameter :: fmt5="(2X,F5.2,3X,E15.8,3X,E15.8)"
    
    character(1) :: i_choix
    logical :: f_init
    character(len=25),dimension(:),allocatable :: n_fich_init

    real*8,dimension(:),allocatable :: tab_h,tab_rau,tab_kp,tab_kq,tab_e,tab_eps
    logical :: premier_f,premier_c,premier_ab

    contains
!--------------------------------------------------------------------------------------------------
! Init_fichier permet d'initialiser pour un seul terrain 1D les calculs pour plusieurs
! géométrie et pour plusieurs fréquences.
! à l'aide d'un fichier. variation de hauteur, variation d'écartement,variation de fréquences
! reste à trouver la façon d'initialiser les multi terrains
! (variation d'épaisseur, variation de profondeur et variation de propriété)
!--------------------------------------------------------------------------------------------------

    subroutine init_fichier(nomfich)
        implicit none
        integer :: tai,i_fch,slg
        integer,parameter :: numfich=3
        character :: ifich
        character(len=*), intent(in), optional :: nomfich
        character(256) :: lig_fic
        character(3) :: ext
        character(4)::extrait
        character(4),dimension(numfich), parameter :: tab_ext=(/'.geo','.frq','.T1D'/)
        character(21):: corp
        ifich=''
        f_init=.FALSE.
        if (present(nomfich)) then
            tai=len_trim(nomfich)
            ext=nomfich(tai-2:tai)
            corp=nomfich(1:tai-4)
!            write(*,*) 'Vous initialiser le programme '//a_gr//' partir du fichier :'
!            write(*,*) nomfich
!            write(*,*) 'Voulez vous continuer ? (oui:1)'
!            read(*,*) ifich
            ifich='1'
        endif
        allocate(n_fich_init(numfich))
        if (ifich/='1') then
            write(*,*) 'initialisation manuelle'
        else
            f_init=.TRUE.
            open(unit=10,file=nomfich)
            do i_fch=1,numfich
                n_fich_init(i_fch)=trim(corp)//tab_ext(i_fch)
                open(unit=10+i_fch,file=n_fich_init(i_fch))
            ENDDO
            i_fch=0
            do
                read(10,'(A256)',end=125) lig_fic
                select case(lig_fic(1:2))
                case(' #')
                    slg=len(trim(lig_fic))
                    extrait=lig_fic(slg-3:slg+1)
                    if (extrait=='CSTM') then
                        write(10+i_fch,*) trim(lig_fic)
                        cycle
                    endif
                    write(*,*) trim(lig_fic)//' OK' 
                    i_fch=i_fch+1
                case default
                    write(10+i_fch,*) trim(lig_fic(2:))
                end select
            enddo
125         write(*,*) 'les fichiers suivants ont '//e_ai//'t'//e_ai//' cr'//e_ai//e_ai//'s :'
            write(*,*) n_fich_init
            do i_fch=0,numfich
                close(10+i_fch)
            enddo
        endif
        return
    end subroutine init_fichier

!--------------------------------------------------------------------------------------------------
! la fonction I2char() fait la comversion d'un entier inférieur à 1000 en chaine de caractère
! utile pour l'écriture des fichiers avec des tableaux à nombre de colonne variable.
!--------------------------------------------------------------------------------------------------
    function I2Char(i)
        implicit none
        character(10), parameter :: entier='0123456789'
        character(3) :: I2char
        integer:: c,d,u
        integer, intent(in):: i
        if (i>999) then
            write(*,*) "l'entier est trop grand, renvoie 1"
            I2char='1'
            return
        endif
        u=mod(i,10)+1
        c=i/100
        d=i/10-c*10+1
        c=c+1
        I2char=entier(c:c)//entier(d:d)//entier(u:u)
        return
    end function I2char
!--------------------------------------------------------------------------------------------------
end module E_S

module appareil
    use E_S
    implicit none

    character(4), dimension(10), parameter :: label=(/'perp','SH3 ','HCP ','coax','VCP ','VCX ','VVCP','PRP2','GEM2','CSTM'/)
    
    ! les tableaux permettent de faire des boucles sur plusieurs appariels (ou configuration pour les multiprofondeurs)
    real*8,dimension(:), allocatable :: tl,he,hr,f,H_bobe,V_bobe,H_bobr,V_bobr,dxr,dyr,buck
    integer,dimension(:), allocatable :: ibob
	
    ! les paramètres **_c permettent d'actualiser l'appel aux différentes initialisations 
    real*8 :: tl_c,he_c,hr_c,f_c,H_bobe_c,V_bobe_c,H_bobr_c,V_bobr_c,dxr_c,dyr_c,buck_c
    
    integer :: ibob_c
    
    integer :: nconf,nfreq


    contains

    
!--------------------------------------------------------------------------------------------------
! procédure unset_geom() de suppression des tableaux contenant les dispositifs
! la sauvegarde est possible si il y a un nom de fichier
! à noter, la sauvegarde avec un .geo ne sauvegarde que les informations sur le dispositif
! toute autre extension considère un fichier contenant toutes les informations (à sécuriser)
!--------------------------------------------------------------------------------------------------
    subroutine unset_geom(nomfich)
        implicit none
        character(len=*),optional, intent(in) :: nomfich
        character(len=25):: frm_tl,frm_h,frm_ib
        integer::tai
        character(3)::ext

        frm_tl="("//I2char(nconf)//"f5.2)"
        frm_h="("//I2char(nconf)//"f5.2)"
        frm_ib="("//I2char(nconf)//"I2)"
        if (present(nomfich)) then
            tai=len(nomfich)
            ext=nomfich(tai-3:tai)
            select case(ext)
            case('geo')
                open(unit=45,file=nomfich)
            case default
                open(unit=45,file=nomfich,position='append')
                write(45,*) '# Geometrie(s) d''appareil'
            end select
            write(45,'(I2)') nconf
            write(45,frm_ib) ibob
            write(45,frm_tl) tl
            write(45,frm_tl) buck
            write(45,frm_h) he
            write(45,frm_h) hr
            write(45,*) '# parametres utiles pour CSTM'
            write(45,frm_tl) H_bobe
            write(45,frm_tl) V_bobe
            write(45,frm_tl) H_bobr
            write(45,frm_tl) V_bobr
            write(45,frm_tl) dxr
            write(45,frm_tl) dyr
            close(unit=45)
        endif
        
        deallocate(tl,he,hr,ibob,dxr,dyr,h_bobe,v_bobe,h_bobr,v_bobr)
    end subroutine unset_geom
!--------------------------------------------------------------------------------------------------
! procédure set_geom qui permet d'initaliser les différents dispositifs
! les paramètres sont dépendant de la géométrie de bobine rentrée
! l'initalisation peut se faire manuellement ou par un fichier
! pour les appareils multibobines, il faut rentrer les différentes paire émission réception
! à faire : orientation quelconque des bobines avec rajout des angles teta_H et teta_V défini
! par rapport à l'axe
!--------------------------------------------------------------------------------------------------
    subroutine set_geom(nomfich)
        implicit none
        character(len=*),optional, intent(in) :: nomfich
        character(len=25):: frm_tl,frm_h,frm_ib
        real*8 :: tl_b
        integer :: i,n_app,ibob_cour
        
        if (present(nomfich)) then
            open(unit=46,file=nomfich)
            read(46,'(I2)') nconf
            allocate(tl(nconf),he(nconf),hr(nconf),ibob(nconf),h_bobe(nconf),v_bobe(nconf))
            allocate(dxr(nconf),dyr(nconf),h_bobr(nconf),v_bobr(nconf),buck(nconf))
            frm_tl="("//I2char(nconf)//"f5.2)"
            frm_h="("//I2char(nconf)//"f5.2)"
            frm_ib="("//I2char(nconf)//"I2)"
            read(46,frm_ib) ibob
            read(46,frm_tl) tl
            read(46,frm_tl) buck
            read(46,frm_h) he
            read(46,frm_tl) hr
            read(46,*)
            read(46,frm_tl) h_bobe
            read(46,frm_tl) v_bobe
            read(46,frm_tl) h_bobr
            read(46,frm_tl) V_bobr
            read(46,frm_tl) dxr
            read(46,frm_tl) dyr
        else
            do
                write(*,*) 'combien d''appareils voulez vous d'//e_ai//'finir'
                read(*,*) n_app
                if(n_app>0) exit
            enddo
            nconf=n_app
            allocate(tl(nconf),he(nconf),hr(nconf),ibob(nconf),h_bobe(nconf),v_bobe(nconf))
            allocate(h_bobr(nconf),v_bobr(nconf),dxr(nconf),dyr(nconf),buck(nconf))
            do i=1,n_app
                do
                    WRITE(*,*)' CONFIGURATION DES BOBINES ?'
                    WRITE(*,*)'1=PERPENDICULAIRES, 2= TYPE SH3 '
                    WRITE(*,*)'3=HORIZONTALES COPLANAIRES, 4= COAXIALES'
                    WRITE(*,*)'5=VERTICALES COPLANAIRES, 6=coaxiales (appareil vertical)'
                    write(*,*)'7=verticales coplanaires (appareil vertical)'
                    write(*,*)'8=perpendiculaires (type Dual EM)'
                    write(*,*)'9=bucking coil (type GEM2)'
                    write(*,*)'0=personnalis'//e_ai//'e (rentr'//e_ai//'e manuelle)'
                    READ(*,*) IBOB_cour
                    IF(IBOB_cour >=0 .AND. IBOB_cour<=9) exit
                end do
                ibob(i)=ibob_cour
                select case(ibob_cour)
                case(1:5,8,9)
                    WRITE(*,*)' ECART ENTRE LES BOBINES ET HAUTEUR DE L APPAREIL ?'
                    READ(*,*) TL(i),He(i)
                    if (ibob_cour/=9) then
                        buck(i)=1.
                    else
                        write(*,*) 'donnez la distance entre la bucking coil et l'''//e_ai//'m'//e_ai//'trice'
                        read(*,*) tl_b
                        buck(i)=tl_b/tl(i)
                    endif
                    Hr(i)=he(i)
                    dxr(i)=tl(i)
                    dyr(i)=0
                    WRITE(*,fmt0) label(ibob(i)),TL(i),He(i)
                    select case (ibob_cour)
                    case(1)
                    ! Tx horizontale suivant x
                        h_bobe(i)=0.
                        v_bobe(i)=0.
                    ! Rx verticale
                        h_bobr(i)=0.
                        v_bobr(i)=90.
                    case(2)
                    ! tx inclinée de 35° dans le plan vertical
                        h_bobe(i)=0.
                        v_bobe(i)=35.
                    ! Rx inclinée de 35° dans le plan vertical
                        h_bobr(i)=0.
                        v_bobr(i)=35.
                    case(3)
                    ! Tx verticale
                        h_bobe(i)=0.
                        v_bobe(i)=90.
                    ! Rx verticale
                        h_bobr(i)=0.
                        v_bobr(i)=90.
                    case(4)
                    ! Tx horizontale suivant X
                        h_bobe(i)=0.
                        v_bobe(i)=0.
                    ! Rx horizontale suivant X
                        h_bobr(i)=0.
                        v_bobr(i)=0.
                    case(5)
                    ! Tx horizontale suivant Y
                        h_bobe(i)=90.
                        v_bobe(i)=0.
                    ! Rx horizontale suivant Y
                        h_bobr(i)=90.
                        v_bobr(i)=0.
                    case(8)
                    ! Tx verticale
                        h_bobe(i)=0.
                        v_bobe(i)=90.
                    ! Rx horizontale suivant X
                        h_bobr(i)=0.
                        v_bobr(i)=0.
                    case(9)
                    ! Tx horizontale suivant Y
                        h_bobe(i)=90.
                        v_bobe(i)=0.
                    ! Rx horizontale suivant Y
                        h_bobr(i)=90.
                        v_bobr(i)=0.
                    end select
                case(6,7)
                    WRITE(*,*)"hauteur de l'"//e_ai//'mettrice et de la r'//e_ai//'ceptrice ?'
                    READ(*,*) he(i),hr(i)
                    tl(i)=abs(hr(i)-he(i))
                    dxr(i)=0
                    dyr(i)=0
                    WRITE(*,fmt1)label(ibob(i)),He(i),Hr(i)
                case(0)
                    write(*,*) 'pas encore impl'//e_ai//'ment'//e_ai
                end select
            end do
        endif
        write(*,*) 'g'//e_ai//'om'//e_ai//'trie d''appareil initialis'//e_ai//'es'
    return
    end subroutine set_geom

!--------------------------------------------------------------------------------------------------
! procédure unset_freq() de suppression des tableaux de fréquences
! le fichier d'entrée est optionnel et conditionne la sauvegarde ou non des valeurs
! à noter, la sauvegarde avec un .frq ne sauvegarde que les informations sur les fréquences dans un fichier dédié
! toute autre extension considère un fichier contenant toutes les informations (à sécuriser)
!--------------------------------------------------------------------------------------------------
    subroutine unset_freq(nomfich)
        implicit none
        character(len=*), optional, intent(in) :: nomfich
        character(len=25) :: fmt_f
        integer :: tai
        character(3)::ext
        if (present(nomfich)) then
            tai=len(nomfich)
            ext=nomfich(tai-3:tai)
            fmt_f="("//i2char(nfreq)//"F10.2)"
            select case (ext)
            case('frq')
                open(unit=47,file=nomfich)
            case default
                open(unit=47,file=nomfich,position='append')
                write(47,*) '# Tableau de frequence(s)'
            end select
            write(47,'(I2)') nfreq
            write(47,fmt_f) f
            close(47)
        endif
        deallocate(f)
    end subroutine unset_freq

!--------------------------------------------------------------------------------------------------
! procédure set_freq() d'intialisation des fréquences
! le tableau peut être défini de plusieurs manières :
! par un fichier d'entrée
! par un choix du nombre de fréquence et une rentrée manuelle de toute les fréquences
! par un choix du nombre de fréquence, du min, du max avec une progression linéaire
! par un choix du nombre de fréquence, du min, du max avec une progression géométrique
!--------------------------------------------------------------------------------------------------
    subroutine set_freq(nomfich)
        implicit none
        character(len=*), optional, intent(in) :: nomfich
        integer :: i,ic,icour
        character(len=15)::phr
        character(len=25) :: fmt_f
        real*8::fmin,fmax,pas_freq

        if (present(nomfich)) then
            open(unit=48,file=nomfich)
            read(48,'(I2)') nfreq
            allocate(f(nfreq))
            fmt_f="("//i2char(nfreq)//"F10.2)"
            read(48,fmt_f) f
        else
            phr="l'appareil"
            if (nconf/=1) phr='les appareils'
            do
                write(*,*)'combien de fr'//e_ai//'quence(s) pour '//phr
                read(*,*) nfreq
                if (nfreq>0) exit
            enddo
            allocate(f(nfreq))
            fmt_f="("//i2char(nfreq)//"F10.2)"
            if (nfreq/=1) then
                do
                    write(*,*) 'mode de rentr'//e_ai//'e :'
                    write(*,*) 'min max (lin) : 1'
                    write(*,*) 'min max (g'//e_ai//'o) : 2'
                    write(*,*) 'manuelle : 3'
                    read(*,*) ic
                    if (ic>0 .or. ic<4) exit
                enddo
                select case(ic)
                case(1)
                    write(*,*)'rentrez la fr'//e_ai//'quence minimale puis la fr'//e_ai//'quence maximale'
                    read(*,*) fmin,fmax
                    pas_freq=(fmax-fmin)/(nfreq-1)
                    do icour=1,nfreq
                        f(icour)=fmin+(icour-1)*pas_freq
                    enddo
                case(2)
                    write(*,*)'rentrez la fr'//e_ai//'quence minimale puis la fr'//e_ai//'quence maximale'
                    read(*,*) fmin,fmax
                    pas_freq=(log(fmax)-log(fmin))/(nfreq-1)
                    do icour=1,nfreq
                        f(icour)=nint(exp(log(fmin)+(icour-1)*pas_freq))
                    enddo
                case(3)
                    do i =1,nfreq
                        write(*,*) 'fr'//e_ai//'quence n'//deg ,i
                        read(*,*) f(i)
                    end do
                end select
            else
                write(*,*) 'valeur de la fr'//e_ai//'quence ?'
                read(*,*) f
            endif
        endif
        write(*,*) 'fr'//e_ai//'quence(s) initialis'//e_ai//'e(s)'
        write(*,fmt_f) f
        
        return
    end subroutine set_freq
end module appareil

!--------------------------------------------------------------------------------------------------
! Le module propriete_1D gére le terrain 1D.
! a_cour,b_cour et p_cour sont les paramètres qui permmettent de gérer les boucles pour les 
! différentes options du menu principal
!--------------------------------------------------------------------------------------------------
module propriete_1D
    use appareil
    implicit none
        double complex, allocatable, dimension(:) :: SUS,gam2,csig
        real*8, allocatable, dimension(:) :: rau,chip,chiq,e,eps
        
! pour gérer les terrain homogène en entrée sortie (un peu cracra je sais)        
        real*8,allocatable, dimension (:,:) :: pcour
        integer, dimension(:) , allocatable :: col_p

        integer :: NCOU
        integer, parameter :: nmax=10
        real*8, parameter :: f_ref=1000
        real*8::a_cour,b_cour,p_cour,rau_c,e_c,chip_c,chiq_c,gam0_2

        !real*8, allocatable, dimension(:) :: a,b,p
        real*8,parameter :: pi=3.141592653589793,mu0=4.*pi*1e-7,eps0=8.85418791762039e-12
    
    contains
        
        subroutine unset_prop_cou(nomfich)
            implicit none
            character(len=*), optional, intent(in) :: nomfich
            character(len=25) :: frm_r,frm_kp,frm_kq,frm_e,frm_eps,frm_cc
            integer,dimension(2)::np
            integer::tai,n
            character(3)::ext

            if (present(nomfich)) then
                tai=len(nomfich)
                ext=nomfich(tai-3:tai)
                frm_r="("//I2char(ncou)//"(2X,f7.2))"
                frm_eps="("//I2char(ncou)//"(2X,f7.2))"
                frm_kp="("//I2char(ncou)//"(2X,E12.5))"
                frm_kq="("//I2char(ncou)//"(2X,E12.5))"
                frm_e="("//I2char(ncou-1)//"(2X,f5.2))"
                select case(ext)
                case('T1D')
                    open(unit=49,file=nomfich)
                case default
                    open(unit=49,file=nomfich,position='append')
                    write(49,*)'# Terrain 1D'
                end select

                select case (i_choix)
                
                case('4')
                    n=size(col_p)
                    np=shape(pcour)
                    write(49,'(I2)') n
                    write(49,'(I5)') np(2)
                    frm_cc="("//I2char(n)//"(2X,i2))"
                    write(49,frm_cc) col_p
                    write(49,fmt3c) pcour(:,1)
                    write(49,fmt3c) pcour(:,np(2))
                    close(49)
                    

                case default
                    write(49,'(I2)') ncou
                    write(49,frm_r) rau
                    write(49,frm_eps) eps
                    write(49,frm_kp) chip
                    write(49,frm_kq) chiq
                    write(49,frm_e) e
                    close(49)
                end select
            endif
            deallocate(rau,chip,chiq,e,eps)
        end subroutine unset_prop_cou

!        subroutine unset_prop_coub(nomfich)

!--------------------------------------------------------------------------------------------------
! procédure set_prop_cou qui permet de rentrer les paramètres des modèles et qui s'adapte en
! fonction du choix fait dans le menu
!--------------------------------------------------------------------------------------------------
        subroutine set_prop_cou(nomfich)
            implicit none
            character(len=*),optional, intent(in) :: nomfich
            character(len=25) :: frm_r,frm_kp,frm_kq,frm_e,frm_eps,frm_cc
            integer :: i,n,np
            
            if (present(nomfich)) then
                open(unit=50,file=nomfich)
                select case (i_choix)

                case('4')
                    read(50,'(I2)') n
                    read(50,'(I5)') np
                    write(*,*) n,np
                    if (allocated(col_p)) deallocate(col_p)
                    if (allocated(pcour)) deallocate(pcour)
                    allocate(col_p(n),pcour(4,np))
                    frm_cc="("//I2char(n)//"(2X,i2))"
                    read(50,frm_cc) col_p
                    read(50,fmt3c) pcour(:,1)
                    read(50,fmt3c) pcour(:,np)
                    close(50)
                    !write(*,*) 'tableau Pcour :'
                    !write(*,fmt3c) pcour
                    ncou=1
                    allocate(rau(ncou),chip(ncou),chiq(ncou),eps(ncou),e(ncou-1))
                    write(*,*) "allocation propri"//e_ai//'t'//e_ai//'s OK'

                case default
                    read(50,'(I2)') ncou
                    frm_r="("//I2char(ncou)//"(2X,f7.2))"
                    frm_eps="("//I2char(ncou)//"(2X,f12.2))"
                    frm_kp="("//I2char(ncou)//"(2X,E12.5))"
                    frm_kq="("//I2char(ncou)//"(2X,E12.5))"
                    frm_e="("//I2char(ncou-1)//"(2X,f5.2))"
                    allocate(rau(ncou),chip(ncou),chiq(ncou),e(ncou-1),eps(ncou))
                    read(50,frm_r) rau
                    read(50,frm_eps) eps
                    read(50,frm_kp) chip
                    read(50,frm_kq) chiq
                    read(50,frm_e) e
                    close(50)
                end select
            else
                select case (i_choix)
                case('2')
                    ncou=3
                    allocate(rau(ncou),chip(ncou),chiq(ncou),e(ncou-1),eps(ncou))
                    e(2)=0.1
                    write(*,*) 'propri'//e_ai//'t'//e_ai//'s de l''encaissant RAU, eps_r, CHI (Ph et Qu(+))'
                    read(*,*) rau(1),eps(1),chip(1),chiq(1)
                    rau(3)=rau(1)
                    eps(3)=eps(1)
                    chip(3)=chip(1)
                    chiq(3)=chiq(1)
                    write(*,*) 'propri'//e_ai//'t'//e_ai//'s de la couche fine RAU, eps_r, CHI (Ph et Qu(+))'
                    read(*,*) rau(2),eps(2),chip(2),chiq(2)
                case('3')
                    ncou=2
                    allocate(rau(ncou),eps(ncou),chip(ncou),chiq(ncou),e(ncou-1))
                    write(*,*) 'propri'//e_ai//'t'//e_ai//'s de la premi'//e_gr//'re couche RAU,eps_r,CHI (Ph et Qu(+))'
                    read(*,*) rau(1),eps(1),chip(1),chiq(1)
                    write(*,*) 'propri'//e_ai//'t'//e_ai//'s de la seconde couche RAU,eps_r,CHI (Ph et Qu(+))'
                    read(*,*) rau(2),eps(2),chip(2),chiq(2)
                case('4')
                    ncou=1
                    allocate(rau(ncou),eps(ncou),chip(ncou),chiq(ncou),e(ncou-1))
                    write(*,*) "allocation propri"//e_ai//'t'//e_ai//'s OK'
                case default
                    do
                        WRITE(*,*)' Nombre de couches ?'
                        READ(*,*)NCOU
                        IF(NCOU<=Nmax) exit
                    end do
                    allocate(rau(ncou),eps(ncou),chip(ncou),chiq(ncou),e(ncou-1))
                    IF(NCOU.GT.1) THEN
                        DO I=1,NCOU-1
                            WRITE(*,*)'Couche',I,' RAU, eps_r, CHI (Ph et Qu(+),E ?'
                            READ(*,*)RAU(I),eps(i),CHIP(I),CHIQ(I),E(I)
                        ENDDO
                    ENDIF
                    WRITE(*,*)'Couche',NCOU,' RAU, eps_r CHI (Ph et Qu(+)) ?'
                    READ(*,*)RAU(NCOU),eps(ncou),CHIP(NCOU),CHIQ(NCOU)
                end select
            endif
            return
        end subroutine set_prop_cou
!--------------------------------------------------------------------------------------------------
        subroutine unset_gam_sus_sig()
            implicit none
            deallocate(sus,gam2,csig)
        end subroutine unset_gam_sus_sig
!---------------------------------------------------------------------------------------------------
! la procédure set_gam_sus_sig() permet de calculer pour chaque frequence et chaque géométrie les
! caractéristiques du terrain
! a faire : intégrer les effets de epsilon ici et aussi voir pour des lois
! de comportement fréquentiel
! à vérifier, pour usage de k
!--------------------------------------------------------------------------------------------------
        Subroutine set_gam_sus_sig()
            implicit none
            real*8 :: chip_cour
            integer :: i_c
            if (.not.allocated(sus)) allocate(sus(ncou))
            if (.not.allocated(csig)) allocate(csig(ncou))
            if (.not. allocated(gam2)) allocate(gam2(ncou))
            DO I_c=1,NCOU
                csig(i_c)=dcmplx(1./rau(i_c),eps(i_c)*2*pi*f_c*eps0)
                chip_cour=chip(i_c)-2/pi*chiq(i_c)*log(f_c/f_ref)
                SUS(I_c)=CMPLX(1.+CHIP_cour,-CHIQ(I_c),kind=8)
                gam2(i_c)=cmplx(0.,2*pi*f_c,kind=8)*mu0*sus(i_c)*csig(i_c)
!                GAM2(I_c)=DCMPLX(0.,PI*PI*F_c*.8E-06/RAU(I_c))
               
            ENDDO
            return
        end subroutine set_gam_sus_sig
!--------------------------------------------------------------------------------------------------
! la procédure unset_ABP() remet à zéro a_cour,b_cour et p_cour
!--------------------------------------------------------------------------------------------------
        subroutine unset_ABP()
            implicit none
            a_cour=0
            b_cour=0
            p_cour=0
        end subroutine unset_ABP
!--------------------------------------------------------------------------------------------------
! la procédure set_ABP() calcule à la volée les paramètre A,B et p nécessaire pour le calcul 1D
! Pour fonctionner, il faut que He_c,F_c,Tl_c et hr_c soient initialisés
! elle initialise  p_cour,a_cour et b_cour
! plusieurs questions sur la valeur de p avec l'introduction de epsilon (au 1 juillet 2020)
!--------------------------------------------------------------------------------------------------
        subroutine set_ABP()
            implicit none
            
            P_cour=SQRT(RAU(1)/F_c/PI/PI/.4E-06)
            select case(ibob_c)
                case(1:5)
                    A_cour=2.*He_c/p_cour
                    B_cour=TL_c/P_cour
                case(6,7)
                    A_cour=(He_c+hr_c)/P_cour
                    B_cour=tl_c**3/P_cour**3
            end select
            return
        end subroutine set_ABP
!--------------------------------------------------------------------------------------------------
! La procédure affich_mod_1D() affiche sous format texte le modèle de terrain 1D courant
!--------------------------------------------------------------------------------------------------
        subroutine affich_mod_1D()
            implicit none
            integer::i
            character(len=*), parameter::fmta="('couche n"//deg//"',I2,' rau :',F7.2,' eps_r : ',F7.2,' Kph :',E12.5,' Kqu :',&
            &E12.5,' e ',F5.2)"
            character(len=*), parameter::fmtb="('couche n"//deg//"',I2,' rau :',F7.2,' eps_r : ',F7.2,&
            &' Kph :',E12.5,' Kqu :',E12.5)"
            do i=1, (ncou-1)
                write(*,*) '___________________________________________________________'
                write(*,fmta) i,rau(i),eps(i),chip(i),chiq(i),e(i)
            ENDDO
            write(*,*) '___________________________________________________________'
            write(*,fmtb) ncou,rau(ncou),eps(ncou),chip(ncou),chiq(ncou)
            write(*,*)''
            return
        end subroutine affich_mod_1D

    end module propriete_1D


!--------------------------------------------------------------------------------------------------
! module fonction1D contenant les fonctions permettant la réponse 1D BF d'un terrain à n couches
!--------------------------------------------------------------------------------------------------
module fonction1D
use E_S
use appareil
use propriete_1D
use hanksgcmod
implicit none
contains

!--------------------------------------------------------------------------------------------------
! fonction de calcul de la cotangente en complexe
!--------------------------------------------------------------------------------------------------
    FUNCTION CTH(Z_cth)
    implicit none

        double COMPLex :: CTH
        double complex,intent(in) :: Z_cth
        real*8 :: x_cth,y_cth,a_cth,b_cth,c_cth
        
        X_cth=realpart(Z_cth)
        Y_cth=imagpart(z_cth)
        A_cth=COS(Y_cth)
        B_cth=SIN(Y_cth)
        C_cth=TANH(X_cth)
        CTH=dCMPLX(A_cth*C_cth,B_cth)/dCMPLX(A_cth,C_cth*B_cth)
        RETURN
    END function cth
!--------------------------------------------------------------------------------------------------
!fonction commune de calcul de la réponse d'un terrain tabulaire utilisée dans Fun0 et Fun2
!--------------------------------------------------------------------------------------------------
    FUNCTION FUN(gg)

    implicit none

        double COMPLEX :: Y,RK,CK
        double complex :: al,u
        double complex :: fun
        real*8, intent(in) :: gg
        real*8 :: g
        integer :: k

        FUN=(0.,0.)
        g=gg
        IF(gg.LT.0.1E-20) G=0.
        IF( gg*a_cour .GT. 30.) RETURN
        AL=DCMPLX(G/p_cour,0.)
        U=SQRT(GAM2(NCOU)+AL*AL)
!        write(*,*) u,sus
        RK=-U/SUS(NCOU)
        IF (NCOU /=1) then
            DO K=NCOU-1,1,-1
                U=SQRT(GAM2(K)+AL*AL)
                Y=U/SUS(K)
                CK=CTH(U*DCMPLX(E(K),0.))
                RK=Y*(RK-Y*CK)/(Y-RK*CK)
            ENDDO
        endif
       ! write(*,*) 'Rk : ',rk
        FUN=(AL+RK)/(AL-RK)/DCMPLX(EXP(G*a_cour),0.)

    RETURN
    END function fun

    
!--------------------------------------------------------------------------------------------------
! fonction de calcul de la réponse tabulaire Fun0
!--------------------------------------------------------------------------------------------------
    FUNCTION FUN0(G)
    implicit none
        
        double COMPLEX :: FUN0
        real*8, intent(in) :: g
        
        FUN0=FUN(G)*DCMPLX(G*G,0.)
        RETURN
    END function fun0
!--------------------------------------------------------------------------------------------------
! fonction de calcul de la réponse tabulaire FUN2
!--------------------------------------------------------------------------------------------------
    FUNCTION FUN2(G)
    implicit none
    double COMPLEX FUN2
    real*8, intent(in) :: g
    
        FUN2=FUN(G)*DCMPLX(G,0.)
    
        RETURN
    END function Fun2
!--------------------------------------------------------------------------------------------------
! fonction de calcul de la réponse 1D CIB0 pour les slingram verticaux
! Elle est spécifique car on se trouve sur l'axe (les transformées de hankel sont donc simplifiée) 
!--------------------------------------------------------------------------------------------------
    FUNCTION CIB0(Aa,FUNC)
        interface
            double complex function func(gg)
                real*8, intent(in) :: gg
            end function func
        end interface 
        real*8, intent(in) ::aa
        double COMPLEX CIB0,C3,F(4),DS,CD
        real*8 :: g,dg
        integer :: i,nt
        !DG=0.3/Aa ! la version ci-dessous est celle issue de programme plus récent
        dg=0.02/aa
        C3=(3.,0.)
        CD=DCMPLX(3.*DG/8.,0.)
        CIB0=(0.,0.)
        G=0.
        NT=0
        F(1)=FUNC(G)
        do
            DO I=2,4
                NT=NT+1
                G=G+DG
                F(I)=FUNC(G)
            enddo
            DS=CD*(F(1)+C3*F(2)+C3*F(3)+F(4))
            CIB0=CIB0+DS
            F(1)=F(4)
            IF(NT.GT.1000.OR.G.GT.2000.) THEN
                IF(ABS(DS)*10.GT.ABS(CIB0)) CIB0=dcmplx(0.,0.)
                exit
            ENDIF
            IF(ABS(DS).LE.0.000001*ABS(CIB0)) exit
        enddo
        RETURN
    END function CIB0
!--------------------------------------------------------------------------------------------------
! Introduction des fonction de calcul des réponses 1D conformément à l'article de 2014
! funZx indique la composante horizontale en ligne du champ pour un dipôle vertical
! On a donc les fonctions FunZx, FunZy, FunZz et FunXx1, funXx2,funXx3, FunXy1, FunXy2 et FunXz
!--------------------------------------------------------------------------------------------------

!--------------------------------------------------------------------------------------------------
! fonction funZx dont on prends la transformée de hankel pour obtenir la composante horizontale
! d'un champ crée par un dipôle vertical
!--------------------------------------------------------------------------------------------------
function funZx(gg)
    implicit none
    double complex :: funZx
    real*8, intent(in) :: gg
    real*8:: g
    double complex :: u0
    funZx=(0.,0.)
    g=gg
    if (gg<1e-20) g=0
    IF (gg .GT. 30.) RETURN
    u0=sqrt(cmplx(g*g+gam0_2,0.,kind=8))
    funZx=u0*g*Rv(g)/exp(u0*(hr_c+he_c))
    return
end function funZx

function funZy(gg)
    implicit none
    double complex :: funZy
    real*8, intent(in) :: gg
    real*8:: g
    g=gg
    funZy=funZx(g)
    return
end function funZy

function funZz(gg)
    implicit none
    double complex :: funZz
    real*8, intent(in) :: gg
    double complex :: u0
    real*8:: g
    g=gg
    u0=sqrt(cmplx(g*g+gam0_2,0.,kind=8))
    funZz=g*funZx(g)/u0
    return
end function funZz

function funXx1(gg)
    implicit none
    double complex :: funXx1
    real*8, intent(in) :: gg
    real*8:: g
    double complex :: u0
    funXx1=(0.,0.)
    g=gg
    u0=sqrt(cmplx(g*g+gam0_2,0.,kind=8))
    funXx1=Rh(g)**exp(u0*(-1*hr_c-he_c))
    return
end function funXx1

function funXx2(gg)
    implicit none
    double complex :: funXx2
    real*8, intent(in) :: gg
    real*8 :: g
    funXx2=(0.,0.)
    g=gg
    funXx2=funXx3(g)/g
    return
end function funXx2

function funXx3(gg)
    implicit none
    double complex :: funXx3
    real*8, intent(in) :: gg
    real*8:: g
    double complex :: u0
    funXx3=(0.,0.)
    g=gg
    if (gg<1e-20) g=0
    if (gg>30) return
    u0=sqrt(cmplx(g*g+gam0_2,0.,kind=8))
    funXx3=R1(g)*exp(u0*(-1*hr_c-he_c))
    return
end function funXx3

function funXy1(gg)
    implicit none
    double complex :: funXy1
    real*8, intent(in) :: gg
    real*8:: g
    funXy1=(0.,0.)
    g=gg
    funXy1=funXx2(g)
    return
end function funXy1

function funXy2(gg)
    implicit none
    double complex :: funXy2
    real*8, intent(in) :: gg
    real*8:: g
    funXy2=(0.,0.)
    g=gg
    funXy2=funXx3(g)
    return
end function funXy2

function funXz(gg)
    implicit none
    double complex :: funXz
    real*8, intent(in) :: gg
    real*8:: g
    FunXz=(0.,0.)
    g=gg
    funXz=funZx(g)
    return
end function funXz
!--------------------------------------------------------------------------------------------------
! Les 3 fonctions Rv(gg), Rh(gg) et R1(gg) sont les fonctions noyaux qui permettent d'exprimer
! toutes les fonctions FunZx, FunZy, FunZz,FunXx, FunXy, FunXz qui servent le calcul des 

function Rv(gg)
    implicit none
    double complex :: Rv
    real*8, intent(in) :: gg
    real*8 :: g
    double complex :: u0,u0mu0,Y1
    g=gg
    if (gg<1e-20) g=0
    u0=sqrt(cmplx(g*g+gam0_2,0.,kind=8))
    u0mu0=u0/mu0
    Y1=Y1D(g)
!write(*,*) 'Y1 : ',Y1
    Rv=g/u0*(u0mu0+Y1)/(u0mu0-Y1)
   !write(*,*) 'g : ',g,' Rv',Rv
    return
end function Rv

function Rh(gg)
    implicit none
    double complex :: Rh
    real*8, intent(in) :: gg
    real*8 :: g
    double complex :: u0,u0sig0,Z1
    g=gg
    if (gg<1e-20) g=0
    u0=sqrt(cmplx(g*g+gam0_2,0.,kind=8))
    u0sig0=u0/cmplx(0,2*pi*f_c*eps0,kind=8)
    Z1=Z1D(g)
    Rh=g/u0*(u0sig0+Z1)/(u0sig0-Z1)
    !write(*,*) Z1,u0,u0sig0
    !write(*,*) 'g :',g ,' Rh :' ,Rh
    return
end function Rh

function R1(gg)
    implicit none
    double complex :: R1
    real*8,intent(in) :: gg
    real*8 :: g
    double complex :: u0
    g=gg
    if (gg<1e-20) g=0
    u0=sqrt(cmplx(g*g+gam0_2,0.,kind=8))
    R1=gam0_2*Rh(g)+u0*u0*Rv(g)
    return
end function R1


!--------------------------------------------------------------------------------------------------
! fonction Y1D(gg) de calcul de l'impédance pour un dipôle vertical sur un terrain 1D tabulaire
!--------------------------------------------------------------------------------------------------

function Y1D(gg)
    implicit none
    double complex :: Y1D
    real*8, intent(in) :: gg
    real*8 :: g
    double complex :: Uc,Umuc,Yc,tgh
    integer :: i
    g=gg
    if (gg<1e-20) g=0

    do i=ncou,1,-1
        Uc=sqrt(g*g+gam2(i))
        Umuc=-1*Uc/sus(i)/mu0
        if (i==ncou) then 
            Yc=Umuc
        else
            tgh=cth(Uc*e(i))
            Yc=Umuc*(Yc-Umuc*tgh)/(Umuc-Yc*tgh)
        endif
    enddo
    Y1D=Yc
    return
end function Y1D

!--------------------------------------------------------------------------------------------------
! fonction Z1D (gg) de calcul de l'impédance pour un dipôle horizontal sur un terrain 1D tabulaire
!--------------------------------------------------------------------------------------------------

function Z1D(gg)
    implicit none
    double complex :: Z1D
    real*8, intent(in) :: gg
    real*8 :: g
    double complex :: Uc,Usigc,Zc,tgh
    integer :: i

    g=gg
    if (gg<1e-20) g=0
    do i=ncou,1,-1
        Uc=sqrt(g*g+gam2(i))
        Usigc=-1*Uc/csig(i)
        if (i==ncou) then 
            Zc=Usigc
        else
            tgh=cth(Uc*e(i))
            Zc=Usigc*(Zc-Usigc*tgh)/(Usigc-Zc*tgh)
        endif
    enddo
    Z1D=Zc
    return
end function Z1D

!--------------------------------------------------------------------------------------------------
! fonction qui calcul la réponse 1D du terrain en fonction des différents paramètres courant
! la gestion du format d'affichage ne devrait pas se faire ici mais dans chaque appel
! (sans le ichoix)
! T0,T1 et T2 sont les 3 intégrales de Wait qui permettent de calculer tous les dispositifs
! en négligeant les effets de permittivitté, elles sont conservées pour mémoire et comparaison
!--------------------------------------------------------------------------------------------------

    subroutine rep1D(qt)
        implicit none
        double complex, intent(out) :: QT


        double complex :: T0,T1,T2
!        real*8,dimension(:),allocatable :: param
!        character(len=256) :: fmt_c



        select case(ibob_c)
            !Perp type CS OK
            case(1)
                T1=HANKSGC(1,b_cour,FUN0,1)
                QT=-DCMPLX(b_cour*b_cour*b_cour,0.)*T1
                if (premier_c) write(*,fmt0) label(ibob_c),TL_c,He_c,F_c
            !Type SH3
            case(2)
                T0=HANKSGC(0,b_cour,FUN0,1)
                T2=HANKSGC(1,b_cour,FUN2,1)
                QT=DCMPLX(b_cour*b_cour/3.,0.)*(T0*dcmplx(3.*b_cour,0.)-T2)
                if (premier_c) write(*,fmt0)label(ibob_c),TL_c,He_c,f_c
            !HCP OK
            case(3)
                T0=HANKSGC(0,b_cour,FUN0,1)
                QT=DCMPLX(b_cour*b_cour*b_cour,0.)*T0
                if (premier_c) write(*,fmt0)label(ibob_c),TL_c,He_c,f_c
            !Coax
            case(4)
                T0=HANKSGC(0,b_cour,FUN0,1)
                T2=HANKSGC(1,b_cour,FUN2,1)
                QT=DCMPLX(b_cour*b_cour,0.)*(T0*dcmplx(b_cour,0.)-T2)
                if (premier_c) write(*,fmt0)label(ibob_c),TL_c,He_c,f_c
            !VCP
            case(5)
                T2=HANKSGC(1,b_cour,FUN2,1)
                QT=DCMPLX(b_cour*b_cour,0.)*T2
                if (premier_c) write(*,fmt0)label(ibob_c),TL_c,He_c,f_c
            !VCX
            case(6)
                T0=CIB0(a_cour,FUN0)
                QT=-T0*b_cour
                if (premier_c) write(*,fmt1)label(ibob_c),He_c,Hr_c,f_c
            !VVCP
            case(7)
                T0=CIB0(a_cour,FUN0)
                QT= T0*b_cour*DCMPLX(.5,0.)
                if (premier_c) write(*,fmt1)label(ibob_c),He_c,Hr_c,f_c
            !Perp Dual EM type Cs multiplié par -1
            case(8)
                
            ! orientation quelconque
            case(0)
                write(*,*) 'pas encore impl'//e_ai//'ment'//e_ai
        end select
        !write(*,trim(fmt_c)) param, QT
        
        return
    end subroutine rep1d

!--------------------------------------------------------------------------------------------------
! rep1Dv2 permet de faire le calcul avec la prise en compte de la permittivité et une orientation
! quelqconque de bobine.
! le calcul reprends les notations de Thiesson et al. 2014
! le calcul est fait en modifiant les coefficients en fonction des orientations
! le cas custom fera le calcul complet avec les orientaiton des bobines en H et V
! peut être qu'il sera intéressant de "shunté" le calcul complet des champs, pour optimiser le 
! temps de calcul
!--------------------------------------------------------------------------------------------------

    subroutine rep1Dv2(qt)
        implicit none

        double complex, intent(out) :: qt 
        double complex :: H_zx,H_zy,H_zz,H_xx,H_xy,H_xz,H_yx,H_yy,H_yz,C1
        double complex :: H_x,H_y,H_z
        real*8 :: r2,r,r3,D2R,CTx,CTy,CTz,CRx,CRy,CRz,rnorm,rnorm2,rnorm3,cnorm,Cn_aux!,cnorm2,CTaux
        C1=1.!/4./pi
        D2R=pi/180.
        gam0_2=-1*eps0*mu0*(2*pi*f_c)**2
       
! ici on défini un rayon horizontal il faudrait vérifier que c'est bien le cas dans le calcul général 
        r2=dxr_c*dxr_c+dyr_c*dyr_c
        r=sqrt(r2)
        r3=r2*r
!        write(*,*) gam0_2
! les 3 composantes du champ d'un dipôle vertical
        H_zx=-1*c1*dxr_c/r*hanksgc(1,r,funZx,1)
        H_zy=-1*c1*dyr_c/r*hanksgc(1,r,funZy,1)
        H_zz=c1*hanksgc(0,r,funZz,1)

!        write(*,*) 'Hzx : ',H_zx
!        write(*,*) 'Hzy : ',H_zy
!        write(*,*) 'Hzz : ',H_zz
! les 3 composantes du champ d'un dipôle horizontal suivant X
        H_xx=-1*C1*(gam0_2*hanksgc(0,r,FunXx1,1)+(dxr_c*dxr_c-dyr_c*dyr_c)/r3*hanksgc(1,r,funXx2,1))
        H_xx=H_xx+C1*dxr_c*dxr_c/r2*hanksgc(0,r,funXx3,1)
        H_xy=C1*dxr_c*dyr_c/r2*(2/r*hanksgc(1,r,FunXy1,1)-hanksgc(0,r,funXy2,1))
        H_xz=-1*C1*dxr_c/r*hanksgc(1,r,FunXz,1)
! les 3 composantes du champ d'un dipôle horizontal suivant Y 
        H_yx=H_xy
        H_yy=-1*C1*(gam0_2*hanksgc(0,r,FunXx1,1)+(dyr_c*dyr_c-dxr_c*dxr_c)/r3*hanksgc(1,r,funXx2,1))
        H_yy=H_yy+C1*dyr_c*dyr_c/r2*hanksgc(0,r,funXx3,1)
        H_yz=-1*C1*dyr_c/r*hanksgc(1,r,FunXz,1)
        

! on calcule la distance entre Tx et Rx
        rnorm2=r2+(hr_c-he_c)*(hr_c-he_c)
        rnorm=sqrt(rnorm2)
        rnorm3=rnorm*rnorm2
! On attribue les coeffcients en fonction des dispositifs
! (à faire implicitement pour les dispositifs classiques)
        CTx=0.
        CTy=0.
        CTz=0.
        CRx=0.
        CRy=0.
        CRz=0.
        select case (ibob_c)
        ! Perp CS OK (en fait cnorm devrait être égal à 2.)
        case(1)
            CTx=1.
            CRz=1.
            cnorm=1
        ! SH3 à remplacer par les coefficient cos <> sqrt(2)/sqrt(3) sin <>1/sqrt(3)
        case(2)
            CTx=-1*sin(54.736*D2R)
            CTz=cos(54.736*D2R)
            CRx=-1*sin(54.736*D2R)
            CRz=cos(54.736*D2R)
        ! vu avec Alain, la valeur est en fait une valeur de normalisaiton prise 
        ! comme la valeur du champ primaire en HCP donc cnorm vaux 1 partout
            cnorm=1
        ! HCP et VCX OK HCP pas VCX
        case(3,6)
            CTz=1.
            CRz=1.
            cnorm=1.
!            if (ibob_c/=3) cnorm=2.
        ! Coax et VVCP en ligne OK coax
        case(4,7)
            CTx=1.
            CRx=1.
            cnorm=1.
!            if (ibob_c/=4) cnorm=1.
        ! VCP (ici dans le cadre 3D, on pourra mettre le VVCP en travers 
        ! même si la réponse 1D est la même)
        case(5)
            CTy=1.
            CRy=1.
            cnorm=1.
        ! Perp Dual
        case(8)
            CTz=1.
            CRx=1.
            cnorm=1.
        ! cas général
        !ici il faut implémenter la formule de cnorm générique liée à la position de la réceptrice
        !en fait on peut prendr ecomme principe que c'est le champ primaire HCP qui fait foi
        !donc on utilise de nouveau 1
        case(0)
            CTx=cos(h_bobe_c*D2R)*cos(v_bobe_c*D2R)
            CTy=sin(h_bobe_c*D2R)*cos(v_bobe_c*D2R)
            CTz=sin(v_bobe_c*D2R)
            CRx=cos(h_bobr_c*D2R)*cos(v_bobr_c*D2R)
            CRy=sin(h_bobr_c*D2R)*cos(v_bobr_c*D2R)
            CRz=sin(v_bobr_c*D2R)
            Cn_aux=CTx*Dxr_c+CTy*Dyr_c+CTz*(hr_c-he_c)
            Cn_aux=Cn_aux/rnorm
!            cnorm=sqrt(1+3*Cn_aux*Cn_aux)
            cnorm=1
        end select

! on applique les coefficients à l'émission
        H_x=CTx*H_xx+CTy*H_yx+CTz*H_zx
        H_y=CTx*H_yx+CTy*H_yy+CTz*H_zy
        H_z=CTx*H_zx+CTy*H_zy+CTz*H_zz


! ainsi que le coeficient de norma du champ primaire qui dépend de l'orientaiotn du dipole émetteur
! et de la position du dipôle récepteur

       ! cnorm2=CTx*dxr_c+CTy*dyr_c+CTz*(hr_c-he_c)
       ! cnorm2=cnorm2*cnorm2*3
       ! CTaux=(CTx+CTy+CTz)*(CTx+CTy+CTz)
       ! cnorm=sqrt(cnorm2+CTaux*rnorm2)/rnorm

! on projette sur la direction de la réception
        Qt=CRx*H_x+CRy*H_y+CRz*H_z
        Qt=Qt*rnorm3/cnorm
        return
    end subroutine rep1Dv2
end module fonction1D

!--------------------------------------------------------------------------------------------------
module menu_general
    use E_S
    use french_talk
    use propriete_1D
    use appareil
    use fonction1D
    
    implicit none

       
    contains
    
    subroutine init_menu()
        implicit none
        
        do
            write(*,*) '----------------------------------------------------------'
            write(*,*) '-----interface non graphique avec le monde de l''EMBF------'
            write(*,*) '-----------------------Menu principal---------------------'
            write(*,*) '----------------------------------------------------------'
            write(*,*)
            write(*,*) 'Faites votre choix :'
            write(*,*)'1) calcul de la profondeur d''investigation avec variation de hauteur'
            write(*,*)'2) calcul de la profondeur d''investigation avec enfoncement d''une couche fine'
            write(*,*)'3) calcul de la profondeur d''investigation par changement d'''//e_ai//'paisseur &
            &de la premi'//e_gr//'re couche'
            write(*,*)'4) calcul d''abaque en faisant varier une ou plusieurs propri'//e_ai//'t'//e_ai//'s'
            write(*,*)'5) calcul d''abaque en fonction de la fr'//e_ai//'quence'
            write(*,*)'6) calcul d''abaque avec l'''//e_ai//'cartement'
            write(*,*)'8) test du programme et rentr'//e_ai//'e manuelle des diff'//e_ai//'rents '//e_ai//'l'//e_ai//'ments'
            write(*,*)'9) '//e_ai//'criture des fichiers pour initialisation par fichier'
            write(*,*)'T) test des fonctions noyaux'
            write(*,*)'Q) quitter le programme'
            read(*,*) i_choix
            select case (i_choix)
            case('1')
                call abaque_elevation()
            case('2')
                call abaque_couche_fine()
            case('3')
                call abaque_epaisseur()
            case('4')
                call abaque_propriete()
            case('5')
                call abaque_freq()
            case('8')
                call exec_test()
                exit
            case('9')

                exit
            case('t','T')
                call test_noy()
            case('Q','q')
                exit
            case default
                write(*,*) 'd',e_ai,'sol',e_ai,' je ne comprends pas ', i_choix
            end select
        end do
        return
    end subroutine init_menu
!--------------------------------------------------------------------------------------------------
! la procédure abaque_elevation() permet de calculer les valeurs de champ pour différentes hauteurs
!--------------------------------------------------------------------------------------------------

    subroutine abaque_elevation()
        implicit none
        real*8 :: hmin,hmax,hpas
        integer :: i_c,i_f
        double complex :: res,res2

        call set_geom()
        call set_freq()
        call set_prop_cou()

        write(*,*) 'Rentrez la hauteur min et la hauteur max de l''appareil (en m)'
        write(*,*) 'attention pour les appareils verticaux, ce sera la hauteur de l'''//e_ai//'mettrice'
        read(*,*) hmin,hmax
        write(*,*) 'Rentrez le pas entre les palliers (en m)'
        read(*,*) hpas
        do i_c=1,nconf
            ibob_c=ibob(i_c)
            premier_f=.TRUE.
            do i_f=1,nfreq
                f_c=f(i_f)
                select case (ibob_c)
                case(1:5,8)
                    he_c=hmin-hpas
                    hr_c=he_c
                    tl_c=tl(i_c)
                    dxr_c=dxr(i_c)
                    dyr_c=dyr(i_c)
                    h_bobe_c=h_bobe(i_c)
                    v_bobe_c=v_bobe(i_c)
                    h_bobr_c=h_bobr(i_c)
                    v_bobr_c=v_bobr(i_c)
                case(6:7)
                    he_c=hmin-hpas
                    hr_c=he_c+TL(i_c)
                    tl_c=tl(i_c)
                    dxr_c=dxr(i_c)
                    dyr_c=dyr(i_c)
                    h_bobe_c=h_bobe(i_c)
                    v_bobe_c=v_bobe(i_c)
                    h_bobr_c=h_bobr(i_c)
                    v_bobr_c=v_bobr(i_c)
                case(0)
                    he_c=hmin-hpas
                    hr_c=he_c+TL(i_c)
                    tl_c=tl(i_c)
                    dxr_c=dxr(i_c)
                    dyr_c=dyr(i_c)
                    h_bobe_c=h_bobe(i_c)
                    v_bobe_c=v_bobe(i_c)
                    h_bobr_c=h_bobr(i_c)
                    v_bobr_c=v_bobr(i_c)
                end select
                premier_ab=.TRUE.
                do while (he_c<=hmax)
                    he_c=he_c+hpas
                    hr_c=hr_c+hpas
                    call set_gam_sus_sig()
                    call set_ABP()
                    call rep1D(res)
                    call rep1Dv2(res2)
                    if (premier_ab) write(*,*) 'hauteur de T en m     Champ secondaire'
                    write(*,'(a)',advance='no') 'calcul ancien'
                    write(*,fmt5) he_c,res
                    write(*,'(a)',advance='no') 'calcul nouveau'
                    write(*,fmt5) he_c,res2
                    premier_ab=.FAlSE.
                enddo
                premier_f =.FALSE.
            enddo
            premier_c=.FALSE.
        enddo
        call unset_geom()
        call unset_freq()
        call unset_prop_cou()
        return
    end subroutine abaque_elevation

!--------------------------------------------------------------------------------------------------
! la procédure abaque_couche_fine() permet de calculer les valeurs de champ pour un enfoncement
! d'une couche fine
!--------------------------------------------------------------------------------------------------

    subroutine abaque_couche_fine()
        implicit none
        real*8 :: emin,emax,epas,ecour
        integer :: i_f,i_c,i_pas
        double complex :: res

        call set_geom()
        call set_freq()
        call set_prop_cou()

        write(*,*) 'Rentrez l'''//e_ai//'paisseur min et l'''//e_ai//'paiseur max de la premi'//e_gr//'re couche(en m)'
        read(*,*) emin,emax
        write(*,*) 'Rentrez le pas entre les palliers (en m)'
        read(*,*) epas
        i_pas=0
        ecour=emin+i_pas*epas
        premier_ab=.TRUE.
        do while (ecour<=emax)
            e(1)=ecour
            premier_c=.TRUE.
            do i_c=1,nconf
                he_c=he(i_c)
                hr_c=hr(i_c)
                tl_c=tl(i_c)
                dxr_c=dxr(i_c)
                dyr_c=dyr(i_c)
                ibob_c=ibob(i_c)
                h_bobe_c=h_bobe(i_c)
                v_bobe_c=v_bobe(i_c)
                h_bobr_c=h_bobr(i_c)
                v_bobr_c=v_bobr(i_c)
                premier_f=.TRUE.
                do i_f=1,nfreq
                    f_c=f(i_f)
                    call set_gam_sus_sig()
                    call set_abp()
                    call rep1D(res)
                    if (premier_ab) then 
                        write(*,fmt4) ecour,res
                    else
                        write(*,fmt4b) ecour,res
                    endif
                    premier_f=.FALSE.
                ENDDO
                call unset_abp()
                premier_c=.FALSE.
            enddo
            i_pas=i_pas+1
            ecour=emin+i_pas*epas
            premier_ab=.FALSE.
        enddo
        
        call unset_geom()
        call unset_freq()
        call unset_prop_cou()
        return
    end subroutine abaque_couche_fine
!--------------------------------------------------------------------------------------------------
! la procédure abaque_freq() permet de calculer la variation fréquentielle du signal sur un
! modèle de terrain 1D fixé
!--------------------------------------------------------------------------------------------------

    subroutine abaque_freq(nomfich)
        implicit none
        character(len=*), optional, intent(in) :: nomfich
        integer :: i_c,i_f
        character :: choix
        double complex :: res

        if (present(nomfich)) then
            write(*,*) 'pas encore impl'//e_ai//'ment'//e_ai
        else
            call set_geom()
            call set_freq()
            do
                call set_prop_cou()
                call affich_mod_1D()
                premier_c=.TRUE.
                do i_c=1,nconf
                    he_c=he(i_c)
                    hr_c=hr(i_c)
                    tl_c=tl(i_c)
                    dxr_c=dxr(i_c)
                    dyr_c=dyr(i_c)
                    ibob_c=ibob(i_c)
                    h_bobe_c=h_bobe(i_c)
                    v_bobe_c=v_bobe(i_c)
                    h_bobr_c=h_bobr(i_c)
                    v_bobr_c=v_bobr(i_c)
                    premier_f=.TRUE.
                    do i_f=1,nfreq
                        f_c=f(i_f)
                        call set_gam_sus_sig()
                        call set_abp()
                        call rep1D(res)
                        write(*,fmt2) f_c,res
                        premier_f=.FALSE.
                    enddo
                    premier_c=.FALSE.
                ENDDO
                write(*,*) 'voulez vous changez de mod'//e_gr//'le 1D ? (oui :1)'
                read(*,*) choix
                if (choix/='1') exit
            
                call unset_prop_cou()
                call unset_gam_sus_sig()
                call unset_ABP()
            enddo
       
        call unset_prop_cou()
        call unset_gam_sus_sig()
        call unset_ABP()
        call unset_freq()
        call unset_geom()
        endif
        return
    end subroutine abaque_freq

!--------------------------------------------------------------------------------------------------
! procédure abaque_epaisseur() permet de calculer la profondeur d'investiation avec
! l'épaississement d'une première couche
!--------------------------------------------------------------------------------------------------
    subroutine abaque_epaisseur(nomfich)
        implicit none
        character(len=*), optional, intent(in) :: nomfich
        real*8 :: emin,emax,epas,ecour
        integer :: i_f,i_c,i_pas
        double complex :: res

        if (present(nomfich)) then
            write(*,*) 'pas encore impl'//e_ai//'ment'//e_ai
        else
            call set_geom()
            call set_freq()
            call set_prop_cou()

            write(*,*) 'Rentrez l'''//e_ai//'paisseur min et l'''//e_ai//'paiseur max de la premi'//e_gr//'re couche(en m)'
            read(*,*) emin,emax
            write(*,*) 'Rentrez le pas entre les palliers (en m)'
            read(*,*) epas
            premier_f=.TRUE.
            do i_f =1,nfreq
                premier_c=.TRUE.
                f_c=f(i_f)
                do i_c=1,nconf
                    he_c=he(i_c)
                    hr_c=hr(i_c)
                    tl_c=tl(i_c)
                    dxr_c=dxr(i_c)
                    dyr_c=dyr(i_c)
                    ibob_c=ibob(i_c)
                    h_bobe_c=h_bobe(i_c)
                    v_bobe_c=v_bobe(i_c)
                    h_bobr_c=h_bobr(i_c)
                    v_bobr_c=v_bobr(i_c)
                    i_pas=0
                    ecour=emin+i_pas*epas
                    premier_ab=.TRUE.
                    do  while (ecour<=emax)
                        e(1)=ecour
                        call set_gam_sus_sig()
                        call set_abp()
                        call rep1Dv2(res)
                        if (premier_ab) then
                            write(*,fmt4) ecour,res
                        else
                            write(*,fmt4b) ecour,res
                        endif
                        premier_ab=.FALSE.
                        i_pas=i_pas+1
                        ecour=emin+i_pas*epas
                    ENDDO
                    call unset_gam_sus_sig()
                    call unset_ABP()
                    premier_c=.FALSE.
                enddo
                premier_f=.FALSE.
            enddo
            call unset_freq()
            call unset_geom()
            call unset_prop_cou()
        endif
        return
    end subroutine abaque_epaisseur

!-----------------------------------------------------------------------------------------------
! sous programme qui effectue les abaques pour terrain homogène
!    intialisation par un fichier en cours 18/06/2025

    subroutine abaque_propriete(nomfich)
        implicit none
        character(len=*), optional, intent(in) :: nomfich
        real*8 :: pcmin,pcmax,pcpas
        real*8,dimension(:,:),allocatable :: pcour2
        integer :: i_c,i_pas,n_p,nb_p,i_l1,i_l2,i_l3, ind_d,ind_f,i_f,i_t,tai,avancement
        integer,dimension(2)::nb_paux
        integer,parameter :: maxiter=250000
        
        character(3), dimension(4):: nom_param=(/'rau','eps','Kph','Kqu'/)
        character(1) :: i_sav
        character(20)::corp
        character(24)::nomfich_f,nomfich_g,nomfich_t,nomfich_s
        double complex :: res


        if (present(nomfich)) then
            call init_fichier(nomfich)
            tai=len_trim(nomfich)
            corp=nomfich(1:tai-4)
            nomfich_f=trim(corp)//'.frq'
            nomfich_g=trim(corp)//'.geo'
            nomfich_t=trim(corp)//'.T1D'
            nomfich_s=trim(corp)//'.dat'
            open(unit=30,file=nomfich_s)
            call set_geom(nomfich_g)
            call set_freq(nomfich_f)
            call set_prop_cou(nomfich_t)
            n_p=size(col_p)
            nb_paux=shape(pcour)
            nb_p=nb_paux(2)
        else
            call set_geom()
            call set_freq()
            call set_prop_cou()
            write(*,*) 'combien de param'//e_gr//'tres voulez vous faire varier (min : 1, max : 4)'
            read(*,*) n_p
            write(*,*) 'combien de valeurs de param'//e_gr//'tres voulez vous explorer (max=',maxiter,'it'//e_ai//'ration)'
            write(*,*) 'Soit ',floor(maxiter**(1/4.)),' pour 4 param'//e_gr//'tres, ',floor(maxiter**(1/3.)),' pour 3 param'&
            &//e_gr//'tres'
            write(*,*) 'et ',floor(sqrt(real(maxiter))),' pour 2 param'//e_gr//'tres'
            read(*,*) nb_p
            allocate(col_p(n_p))
            ! on limite le nombre d'itérations
            if (nb_p**n_p>maxiter) then
                select case (n_p)
                case(1)
                    nb_p=maxiter
                case(2)
                    nb_p=floor(sqrt(real(maxiter)))
                case(3)
                    nb_p=floor(maxiter**(1/3.))
                case(4)
                    nb_p=floor(maxiter**(1/4.))
                end select
            endif
            allocate(pcour(4,nb_p))
            write(*,*) 'rentrez les valeurs initiales de propri'//e_ai//'t'//e_ai
            write(*,*) 'Rau, Eps_r, Kph, Kqu'
            read(*,*) pcour(:,1)
            
        !   la colonne 1 de pcour correspond à rau, la colonne 2 correspond à eps, la colonne 3 correspond à Kph 
        !   la colonne 4 correspond à Kqu
            if (n_p/=4) then
                write(*,*) 'Rentrer les indices des colonnes des ',n_p,' param'//e_gr//'tres'
                write(*,*) '1 <-> rau, 2 <-> eps_r, 3 <-> kph, 4 <-> Kqu (',n_p,' valeurs attendues)'
                read(*,*) col_p
            else
                col_p=(/1,2,3,4/)
            endif
            pcour(:,nb_p)=pcour(:,1)
            do i_c=1,n_p
                write(*,*) 'rentrer le maximum de ',nom_param(col_p(i_c))
                read(*,*) pcour(col_p(i_c),nb_p)
            enddo
        endif

        do i_c=1,4 
            pcmin=pcour(i_c,1)
            pcmax=pcour(i_c,nb_p)
            pcpas=(pcmax-pcmin)/(nb_p-1)
        !   pcpas= (pcmax/pcmin)**(1./(nb_p-1))
            do i_pas=2,nb_p-1
                pcour(i_c,i_pas)=pcour(i_c,i_pas-1)+pcpas
            enddo
        enddo
        write(*,*) 'initialisation pcour OK'
        write(*,*) 'nombre de param'//e_gr//'tres qui varient : ',n_p
        write(*,*) 'nombre de variations par param'//e_gr//'tres : ',nb_p
        write(*,*) 'nombre de lignes du tableau Pcour2 : ',nb_p**n_p

        allocate(pcour2(4,nb_p**n_p))
        do i_c=1,4
            pcour2(i_c,:)=pcour(i_c,1)
        enddo
     

        select case(n_p)
        case(1)
            pcour2=pcour
        case(2)
            do i_l1=1,nb_p
                ind_d=(i_l1-1)*nb_p+1
                ind_f=(i_l1-1)*nb_p+nb_p
                pcour2(col_p(1),ind_d:ind_f)=pcour(col_p(1),i_l1)
                pcour2(col_p(2),ind_d:ind_f)=pcour(col_p(2),:)
            enddo
        case(3)
            do i_l1=1,nb_p
                do i_l2=1,nb_p
                    ind_d=(i_l1-1)*nb_p*nb_p+(i_l2-1)*nb_p+1
                    ind_f=(i_l1-1)*nb_p*nb_p+(i_l2-1)*nb_p+nb_p
                    pcour2(col_p(1),ind_d:ind_f)=pcour(col_p(1),i_l1)
                    pcour2(col_p(2),ind_d:ind_f)=pcour(col_p(2),i_l2)
                    pcour2(col_p(3),ind_d:ind_f)=pcour(col_p(3),:)
                enddo
            enddo
        case(4)
            do i_l1=1,nb_p
                do i_l2=1,nb_p
                    do i_l3=1,nb_p
                        ind_d=(i_l1-1)*nb_p*nb_p*nb_p+(i_l2-1)*nb_p*nb_p+(i_l3-1)*nb_p+1
                        ind_f=(i_l1-1)*nb_p*nb_p*nb_p+(i_l2-1)*nb_p*nb_p+(i_l3-1)*nb_p+nb_p
                        pcour2(col_p(1),ind_d:ind_f)=pcour(col_p(1),i_l1)
                        pcour2(col_p(2),ind_d:ind_f)=pcour(col_p(2),i_l2)
                        pcour2(col_p(3),ind_d:ind_f)=pcour(col_p(3),i_l3)
                        pcour2(col_p(4),ind_d:ind_f)=pcour(col_p(4),:)
                    enddo
                enddo
            enddo
        end select
        write(*,*) 'initialisation Pcour2 OK'
        premier_ab=.TRUE.
        do i_t=1,nb_p**n_p
            avancement=floor(float(i_t)/float(nb_p**n_p)*100.)
            rau(1)=pcour2(1,i_t)
            eps(1)=pcour2(2,i_t)
            chip(1)=pcour2(3,i_t)
            chiq(1)=pcour2(4,i_t)
            premier_f=.TRUE.
            do i_f =1,nfreq
                f_c=f(i_f)
                premier_c=.TRUE.
                do i_c=1,nconf
                    he_c=he(i_c)
                    hr_c=hr(i_c)
                    dxr_c=dxr(i_c)
                    dyr_c=dyr(i_c)
                    h_bobe_c=h_bobe(i_c)
                    v_bobe_c=v_bobe(i_c)
                    h_bobr_c=h_bobr(i_c)
                    v_bobr_c=v_bobr(i_c)
                    tl_c=tl(i_c)
                    ibob_c=ibob(i_c)
                    call set_gam_sus_sig()
                    call set_abp()
                    call rep1Dv2(res)
                    if (present(nomfich)) then
                        write(30,fmt3b) pcour2(:,i_t),res
                    else
                        if (premier_ab .and. premier_c) then
                            write(*,*) "sauvegarde dans un fichier ? (oui :1)"
                            read(*,*) i_sav
                            if (i_sav=='1') then
                                write(*,'(A)',advance='no' ) "Nom du fichier : "
                                read(*,*) nomfich_s
                                open(unit=30,file=nomfich_s)
                            endif
                         end if
                        if (i_sav=='1') then
                            if (nconf/=1) then
                                write(30,fmt3d) pcour2(:,i_t),res,tl_c
                            else
                                write(30,fmt3b) pcour2(:,i_t),res
                            endif
                        else
                            if (nconf/=1) then
                                write(*,fmt3d) pcour2(:,i_t),res,tl_c
                            else
                                write(30,fmt3b) pcour2(:,i_t),res
                            endif
                        endif
                    endif
                    premier_c=.FALSE.
                enddo
                premier_f=.FALSE.
                call unset_gam_sus_sig()
                call unset_ABP()
            enddo
            premier_ab=.FALSE.
        enddo
       
        !write (*,'(F9.3,2X,F9.3,2X,E10.5,2X,E10.5)') pcour2
       
        call unset_geom()
        call unset_freq()
        call unset_prop_cou()
        close(30)
        deallocate(pcour2)
        return
    end subroutine abaque_propriete

!--------------------------------------------------------------------------------------------------
! execution manuelle avec rentrée des choses à la main pour s'assurer que le bouzin fonctionne
! On a quand même une boucle sur la fréquence et sur le nombre de dispositifs
! Pas de sauvegarde dans un fichier pour le moment
!
    subroutine exec_test()
        implicit none
        logical :: dispositif,terrain,sortie
        integer :: i_c,i_f,choix
        double complex :: res,res2
        dispositif=.TRUE.
        terrain=.TRUE.
        sortie=.FALSE.
        do
            if (dispositif) then
                call set_geom()
                call set_freq()
                dispositif=.FALSE.
            endif
            if (terrain) then
                call set_prop_cou()
                terrain=.FALSE.
            endif
            call affich_mod_1D()
            do i_c=1,nconf
                dxr_c=dxr(i_c)
                dyr_c=dyr(i_c)
                h_bobe_c=h_bobe(i_c)
                v_bobe_c=v_bobe(i_c)
                h_bobr_c=h_bobr(i_c)
                v_bobr_c=v_bobr(i_c)
                he_c=he(i_c)
                hr_c=hr(i_c)
                tl_c=tl(i_c)
                do i_f=1,nfreq
                    f_c=f(i_f)
                    ibob_c=ibob(i_c)
                    call set_gam_sus_sig()
                    call set_ABP()
                    call rep1D(res)
                    write(*,*) 'calcul 1 : ',res
                    !write(*,*) 'csig : ',csig
                    !write(*,*) 'sus : ' ,sus
                    !write(*,*) 'gam2 :',gam2
                    
                    call rep1Dv2(res2)
                    write(*,*) 'calcul 2 : ',res2
                    !write(*,*) 'csig : ', csig
                    !write(*,*) 'sus : ' ,sus
                    !write(*,*) 'gam2 :',gam2
                ENDDO
            enddo
            WRITE(*,*)'On recommence avec : '
            write(*,*) 'UN AUTRE TERRAIN : 1'
            write(*,*) 'un autre dispositif : 2'
            write(*,*) 'les deux : 3'
        !    write(*,*) 'test ASCII : 4'
            write(*,*) 'sortie : 0'
            READ(*,*)choix
            select case (choix)
                case(0)
                    sortie=.TRUE.
                case(1)
                    terrain=.TRUE.
                case(2)
                    dispositif=.TRUE.
                case(3)
                    terrain=.TRUE.
                    dispositif=.TRUE.
        !       case(4)
        !            call tab_ascii()
        !            sortie= .TRUE.
                case default
                    sortie=.TRUE.
            end select
            if (sortie) then
                call unset_gam_sus_sig()
                call unset_ABP()
                call unset_geom()
                call unset_freq()
                call unset_prop_cou()
                exit
            endif
            if (terrain) then 
                call unset_prop_cou()
                call unset_ABP()
                call unset_gam_sus_sig()
            end if
            if (dispositif) then
                call unset_freq()
                call unset_geom()
            end if
        enddo
        return
    end subroutine exec_test

! subroutine de test des fonctions noyaux

    subroutine test_noy()
        implicit none
        logical :: dispositif,terrain,sortie
        integer :: i_c,i_f,choix,n_g,i_g
        real*8 :: psdgmin,psdgcour,pas_psdg
        !double complex :: u0!,aux1,aux2,aux3

        n_g=8
        psdgmin=1e-8
        pas_psdg=1.e1
        
        dispositif=.TRUE.
        terrain=.TRUE.
        sortie=.FALSE.
        !aux1=(1.,1.)
        do
            if (dispositif) then
                call set_geom()
                call set_freq()
                    dispositif=.FALSE.
            endif
            if (terrain) then
                call set_prop_cou()
                terrain=.FALSE.
            endif
            call affich_mod_1D()
            do i_c=1,nconf
                dxr_c=dxr(i_c)
                dyr_c=dyr(i_c)
                h_bobe_c=h_bobe(i_c)
                v_bobe_c=v_bobe(i_c)
                h_bobr_c=h_bobr(i_c)
                v_bobr_c=v_bobr(i_c)
                he_c=he(i_c)
                hr_c=hr(i_c)
                tl_c=tl(i_c)
                do i_f=1,nfreq
                    f_c=f(i_f)
                    ibob_c=ibob(i_c)
                    call set_gam_sus_sig()
                    call set_ABP()
                    write(*,*) 'csig : ',csig
                    write(*,*) 'sus : ' ,sus
                    write(*,*) 'gam2 :',gam2
                    gam0_2=-1*eps0*mu0*(2*pi*f_c)**2
                    do i_g=1,n_g
                        
                        psdgcour=psdgmin*pas_psdg**(i_g-1)
                        write(*,*) psdgcour                      
                        !write(*,*) 'Xx1 : ',FunXx1(psdgcour),'Xx2 : ', Funxx2(psdgcour),' Xx3 : ',FunXx3(psdgcour)
                       ! write(*,*) 'Xy1 : ',funXy1(psdgcour), 'Xy2 : ',funXy2(psdgcour)
                       ! write(*,*) 'Xz : ',funXz(psdgcour)
                        write(*,*) 'Zx : ',FunZx(psdgcour)
                        !write(*,*) 'Zy : ',FunZy(psdgcour)
                        !write(*,*) 'Zz : ',FunZz(psdgcour)
                        !write(*,*) 'fun :',fun(psdgcour)
                        write(*,*) 'fun0 :',Fun0(psdgcour)
                        !write(*,*) 'fun2 :',fun2(psdgcour)
                        !write(*,*) 'Uo : ',sqrt(cmplx(psdgcour*psdgcour+gam0_2,0.,kind=8)), 'gam0 : ',gam0_2
                        !write(*,*) 'R1 : ',R1(psdgcour),'RH : ',rh(psdgcour),' Rv : ',Rv(psdgcour)
                        !write(*,*) 'Y1 : ',Y1D(psdgcour),'Z1 : ',Z1D(psdgcour)
                        !u0=sqrt(cmplx(psdgcour*psdgcour+gam0_2,0.,kind=8))
                        !aux1=u0/csig(1)
                        !aux2=realpart(u0)/csig(1)
                        !aux3=cmplx(0.,realpart(u0),kind=8)/csig(1)
                        !write(*,*) 'Uo : ', u0, 'Aux1 : ',exp(u0)
                        !write(*,*) 'Aux2 : ', aux2, 'Aux3 : ',aux3

                    end do
                ENDDO
            enddo
            WRITE(*,*)'On recommence avec : '
            write(*,*) 'UN AUTRE TERRAIN : 1'
            write(*,*) 'un autre dispositif : 2'
            write(*,*) 'les deux : 3'
        !    write(*,*) 'test ASCII : 4'
            write(*,*) 'sortie : 0'
            READ(*,*)choix
            select case (choix)
                case(0)
                    sortie=.TRUE.
                case(1)
                    terrain=.TRUE.
                case(2)
                    dispositif=.TRUE.
                case(3)
                    terrain=.TRUE.
                    dispositif=.TRUE.
        !       case(4)
        !            call tab_ascii()
        !            sortie= .TRUE.
                case default
                    sortie=.TRUE.
            end select
            if (sortie) then
                call unset_gam_sus_sig()
                call unset_ABP()
                call unset_geom()
                call unset_freq()
                call unset_prop_cou()
                exit
            endif
            if (terrain) then 
                call unset_prop_cou()
                call unset_ABP()
                call unset_gam_sus_sig()
            end if
            if (dispositif) then
                call unset_freq()
                call unset_geom()
            end if
        enddo
        return
        end subroutine test_noy

!--------------------------------------------------------------------------------------------------
    subroutine sav_res(nomfich)
        implicit none
        character(len=*),optional, intent(in)::nomfich
        character(len=25) :: nomfich2
        if (.not.( present(nomfich))) then
            write(*,*) 'rentrez un nom de fichier de sortie'
            read(*,*) nomfich2
        else
            nomfich2=nomfich
        endif
        open(unit=25,file=nomfich2)
        close(25)
        return
    end subroutine sav_res

end module menu_general


!--------------------------------------------------------------------------------------------------
program SH1DBF_hom
use E_S
use menu_general
use propriete_1D
use appareil
use fonction1D
use hanksgcmod

implicit none

character(20):: nfich
character(1):: i_choix2
integer :: ioerr,ioerrf

!---------------------------------------
call get_command_argument(1,nfich,status=ioerr)
if (ioerr==0) then
  write(*,*) "initialisation à partir du fichier ",nfich
  write(*,*) " voulez vous continuez (oui : 1)"
  i_choix2='1'
  if (i_choix2=='1') then
    open(15,file=nfich,status='old',iostat=ioerrf)
    close(15)
    if (ioerrf/=0) stop "absence du fichier d''initialisation"
    i_choix='4'
 !   call exec_test()
    call abaque_propriete(nfich)
  else
    i_choix='4'
!    call exec_test()
    call abaque_propriete()
  endif
else
    i_choix="4"
!    call exec_test()
    call abaque_propriete()
endif
!if (i_choix=='Q'.or.i_choix=='q') stop
!call init_fichier('test.dat')
STOP
END program SH1DBF_hom

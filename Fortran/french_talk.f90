!module qui permet d'avoir les caractère é,è,ç,à,ù et \'E
!ensuite, ce serait intéressant de le développer en remplaçant les phrases en français dans les différentes
!sortie écran par des valeur de chaine de caractère qui ensuite serait différentes en fonction du module
! utilisé fr,en,es par exemple

module french_talk
    implicit none
    character (1), parameter :: e_ai=achar(130),e_gr=achar(138)
    character (1), parameter :: ccec=achar(135),a_gr=achar(133)
    character (1), parameter :: EEai=achar(144),u_ai=achar(151)
    character (1), parameter :: deg=achar(248)


    contains

    subroutine tab_ascii ()
        implicit none
        integer :: i
        do i=1,256
            write(*,*) i , char(i), achar(i)
        end do
        return
    end subroutine tab_ascii
end module french_talk
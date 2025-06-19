function sum2(a) result(b) bind(c, name='sum2')
    use iso_c_binding
    implicit none
    
    real(c_double), intent(in)  :: a
    real(c_double)              :: b
    
    b = a + 2.d0
    
end function sum2

from rockstar import RockStar

fortran_code = """program hello
    write(*,*) 'Hello, world!'
end program hello"""

rock_it_bro = RockStar(days=400, file_name='helloworld.f90', code=fortran_code)
rock_it_bro.make_me_a_rockstar()

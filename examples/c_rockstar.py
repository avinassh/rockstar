from rockstar import RockStar

c_code = "printf('Hello world')"
rock_it_bro = RockStar(days=400, file_name='helloWorld.c', code=c_code)
rock_it_bro.make_me_a_rockstar()

from rockstar import RockStar

lua_code = "print 'hello world!'"
rock_it_bro = RockStar(days=400, file_name='helloworld.lua', code=lua_code)
rock_it_bro.make_me_a_rockstar()

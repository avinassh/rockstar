from rockstar import RockStar

make_file = """all:
    echo 'Hello world!'"""
rock_it_bro = RockStar(days=400, file_name='Makefile', code=make_file)
rock_it_bro.make_me_a_rockstar()

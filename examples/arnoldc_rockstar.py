from rockstar import RockStar

arnoldc_code = """IT'S SHOWTIME
TALK TO THE HAND "Hello World"
YOU HAVE BEEN TERMINATED"""

rock_it_bro = RockStar(days=400, file_name='hello.arnoldc', code=arnoldc_code)
rock_it_bro.make_me_a_rockstar()

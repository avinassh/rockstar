from RockStar import RockStar

hack_code = """<?hh
echo 'Hello World';
"""

rock_it_bro = RockStar(days=400, file_name='helloworld.hack', code=hack_code)
rock_it_bro.make_me_a_rockstar()

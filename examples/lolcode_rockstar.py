from rockstar import RockStar

lolcode_code = """HAI
CAN HAS STDIO?
VISIBLE "HAI WORLD!"
KTHXBYE"""

rock_it_bro = RockStar(days=400, file_name='helloworld.lol', code=lolcode_code)
rock_it_bro.make_me_a_rockstar()

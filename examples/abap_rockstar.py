from rockstar import RockStar

abap_code = """***************************************
** Program: HELLOWORLD                 **
***************************************

REPORT HELLOWORLD
WRITE 'Hello, world!'.
"""

rock_it_bro = RockStar(days=400, file_name='helloworld.abap', code=abap_code)
rock_it_bro.make_me_a_rockstar()

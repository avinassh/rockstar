from rockstar import RockStar

cobol_code = """IDENTIFICATION DIVISION.
PROGRAM-ID. HELLO-WORLD.
* Rock Star hello world program
PROCEDURE DIVISION.
    DISPLAY 'Hello world!'.
    STOP RUN."""

rock_it_bro = RockStar(days=400, file_name='helloworld.cobol', code=cobol_code)
rock_it_bro.make_me_a_rockstar()

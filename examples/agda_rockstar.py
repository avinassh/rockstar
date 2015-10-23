from rockstar import RockStar

agda_code = """module hello where
  open import IO
  main = run (putStrLn "Hello, World!")"""

rock_it_bro = RockStar(days=400, file_name='helloworld.agda', code=agda_code)
rock_it_bro.make_me_a_rockstar()
